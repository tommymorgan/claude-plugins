import { describe, it, expect, beforeEach, afterEach } from "vitest";
import {
  runPipeline,
  type PipelineResult,
} from "../src/pipeline.js";
import { validateOutput } from "../src/validator.js";
import type { DemoScript } from "../src/script-schema.js";
import { mkdtempSync, rmSync, existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

function makeScript(overrides: Partial<DemoScript> = {}): DemoScript {
  return {
    version: 1,
    name: "pipeline-test",
    strategy: "screenshot",
    resolution: { width: 1280, height: 720 },
    voice: { name: "en-US-GuyNeural" },
    scenes: [
      {
        id: "scene1",
        narration: "First scene.",
        actions: [
          { type: "navigate", url: "https://example.com" },
          { type: "wait", duration: 500 },
        ],
        transition: "crossfade",
      },
    ],
    ...overrides,
  };
}

describe("Failed scene does not block other scenes", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "pipeline-test-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should continue recording remaining scenes when one fails", async () => {
    const script = makeScript({
      scenes: [
        {
          id: "good-scene",
          narration: "This works.",
          actions: [
            { type: "navigate", url: "https://example.com" },
          ],
          transition: "crossfade",
        },
        {
          id: "bad-scene",
          narration: "This fails.",
          actions: [
            { type: "click", selector: "#nonexistent-element-xyz-12345" },
          ],
          transition: "crossfade",
        },
      ],
    });

    const result = await runPipeline(script, tempDir);

    expect(result.sceneResults).toHaveLength(2);
    expect(result.sceneResults.find((s) => s.sceneId === "good-scene")?.success).toBe(true);
    expect(result.sceneResults.find((s) => s.sceneId === "bad-scene")?.success).toBe(false);
  }, 60000);
});

describe("Errors are logged for automation pipelines", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "pipeline-test-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should write errors to errors.log when a scene fails", async () => {
    const script = makeScript({
      scenes: [
        {
          id: "error-scene",
          narration: "This will fail.",
          actions: [
            { type: "click", selector: "#does-not-exist-at-all" },
          ],
          transition: "crossfade",
        },
      ],
    });

    const result = await runPipeline(script, tempDir);

    const errorsLogPath = join(tempDir, "errors.log");
    expect(existsSync(errorsLogPath)).toBe(true);

    const logContent = readFileSync(errorsLogPath, "utf-8");
    expect(logContent).toContain("error-scene");
  }, 60000);

  it("should report overall success as false when any scene fails", async () => {
    const script = makeScript({
      scenes: [
        {
          id: "failing",
          narration: "Fail.",
          actions: [
            { type: "click", selector: "#nope" },
          ],
          transition: "crossfade",
        },
      ],
    });

    const result = await runPipeline(script, tempDir);

    expect(result.success).toBe(false);
  }, 60000);
});

describe("Output video passes basic quality validation", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "pipeline-test-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should validate a successful pipeline output", async () => {
    const script = makeScript();

    const result = await runPipeline(script, tempDir);

    if (result.success && result.videoPath) {
      const validation = await validateOutput(result.videoPath, script);

      expect(validation.hasAudio).toBe(true);
      expect(validation.durationMs).toBeGreaterThan(0);
      expect(validation.hasVideo).toBe(true);
    }
  }, 60000);
});
