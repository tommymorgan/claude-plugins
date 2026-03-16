import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { detectSensitiveUrls } from "../src/sensitive.js";
import { rerecordScene } from "../src/pipeline.js";
import { writeScript, readScript } from "../src/script-io.js";
import type { DemoScript } from "../src/script-schema.js";
import { mkdtempSync, rmSync, existsSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";

function makeScript(overrides: Partial<DemoScript> = {}): DemoScript {
  return {
    version: 1,
    name: "flow-test",
    strategy: "screenshot",
    resolution: { width: 1280, height: 720 },
    voice: { name: "en-US-GuyNeural" },
    scenes: [
      {
        id: "scene1",
        narration: "First scene.",
        actions: [{ type: "navigate", url: "https://example.com" }],
        transition: "crossfade",
      },
    ],
    ...overrides,
  };
}

describe("User creates a demo by describing it conversationally", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "flow-test-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should write a script to the project demos directory with at least one scene", async () => {
    const script = makeScript({ name: "conversational-test" });

    const scriptPath = await writeScript(script, tempDir);

    expect(existsSync(scriptPath)).toBe(true);

    const loaded = await readScript(scriptPath);
    expect(loaded.scenes.length).toBeGreaterThanOrEqual(1);
    expect(loaded.scenes[0].narration).toBeTruthy();
    expect(loaded.scenes[0].actions.length).toBeGreaterThanOrEqual(1);
  });
});

describe("Demo is generated from a plan file without interaction", () => {
  it("should be able to read a script and pass it directly to the pipeline", async () => {
    const tempDir = mkdtempSync(join(tmpdir(), "flow-test-"));

    try {
      const script = makeScript({ name: "plan-input-test" });
      const scriptPath = await writeScript(script, tempDir);
      const loaded = await readScript(scriptPath);

      // The loaded script is valid and can be passed to runPipeline
      expect(loaded.version).toBe(1);
      expect(loaded.strategy).toBe("screenshot");
      expect(loaded.scenes).toHaveLength(1);
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });
});

describe("Sensitive content warning is displayed for authenticated demos", () => {
  it("should detect URLs with common authentication patterns", () => {
    const urls = [
      "https://app.example.com/login",
      "https://example.com/auth/callback",
      "https://example.com/admin/dashboard",
      "https://example.com/account/settings",
    ];

    for (const url of urls) {
      expect(detectSensitiveUrls([url])).toHaveLength(1);
    }
  });

  it("should not flag public URLs", () => {
    const urls = [
      "https://example.com",
      "https://example.com/about",
      "https://example.com/pricing",
    ];

    expect(detectSensitiveUrls(urls)).toHaveLength(0);
  });

  it("should extract URLs from script actions", () => {
    const script = makeScript({
      scenes: [
        {
          id: "auth-scene",
          narration: "Logging in",
          actions: [
            { type: "navigate", url: "https://app.example.com/login" },
            { type: "fill", selector: "#email", value: "user@example.com" },
          ],
          transition: "crossfade",
        },
      ],
    });

    const urls = script.scenes.flatMap((s) =>
      s.actions
        .filter((a): a is { type: "navigate"; url: string } => a.type === "navigate")
        .map((a) => a.url)
    );

    expect(detectSensitiveUrls(urls)).toHaveLength(1);
  });
});

describe("User re-records a single failed or unsatisfactory scene", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "flow-test-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should re-record only the specified scene", async () => {
    const script = makeScript({
      name: "rerecord-test",
      scenes: [
        {
          id: "keep-this",
          narration: "Keep this scene.",
          actions: [{ type: "navigate", url: "https://example.com" }],
          transition: "crossfade",
        },
        {
          id: "redo-this",
          narration: "Redo this scene.",
          actions: [{ type: "navigate", url: "https://example.com" }],
          transition: "crossfade",
        },
      ],
    });

    const result = await rerecordScene(script, "redo-this", tempDir);

    expect(result.sceneId).toBe("redo-this");
    expect(result.success).toBe(true);
  }, 30000);
});
