import { describe, it, expect, beforeEach, afterEach } from "vitest";
import {
  recordScene,
  type RecordingResult,
} from "../src/recorder.js";
import type { Scene } from "../src/script-schema.js";
import { mkdtempSync, rmSync, existsSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

function makeScene(overrides: Partial<Scene> = {}): Scene {
  return {
    id: "test-scene",
    narration: "Test narration",
    actions: [
      { type: "navigate", url: "https://example.com" },
      { type: "wait", duration: 1000 },
    ],
    transition: "crossfade",
    ...overrides,
  };
}

describe("User chooses screenshot sequence strategy", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "recorder-test-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should capture a screenshot after executing scene actions", async () => {
    const scene = makeScene({ id: "screenshot-test" });

    const result = await recordScene({
      scene,
      strategy: "screenshot",
      outputDir: tempDir,
      resolution: { width: 1920, height: 1080 },
    });

    expect(result.type).toBe("screenshot");
    expect(existsSync(result.path)).toBe(true);
    expect(result.path).toMatch(/\.png$/);
  }, 30000);
});

describe("User chooses scene-based recording strategy", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "recorder-test-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should produce an isolated video clip for the scene", async () => {
    const scene = makeScene({ id: "scene-video-test" });

    const result = await recordScene({
      scene,
      strategy: "scene-based",
      outputDir: tempDir,
      resolution: { width: 1920, height: 1080 },
    });

    expect(result.type).toBe("video");
    expect(existsSync(result.path)).toBe(true);
    expect(result.path).toMatch(/\.(webm|mp4)$/);
  }, 30000);
});

describe("User chooses continuous recording strategy", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "recorder-test-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should produce a video clip as part of continuous recording", async () => {
    const scene = makeScene({ id: "continuous-test" });

    const result = await recordScene({
      scene,
      strategy: "continuous",
      outputDir: tempDir,
      resolution: { width: 1920, height: 1080 },
    });

    // Continuous recording still produces a video per scene
    // but does not close/reopen the browser between scenes
    expect(result.type).toBe("video");
    expect(existsSync(result.path)).toBe(true);
  }, 30000);
});
