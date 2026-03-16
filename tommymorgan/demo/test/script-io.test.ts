import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { writeScript, readScript } from "../src/script-io.js";
import { mkdtempSync, rmSync, existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import type { DemoScript } from "../src/script-schema.js";

function makeScript(overrides: Partial<DemoScript> = {}): DemoScript {
  return {
    version: 1,
    name: "test-demo",
    strategy: "scene-based",
    resolution: { width: 1920, height: 1080 },
    voice: { name: "en-US-GuyNeural" },
    scenes: [
      {
        id: "intro",
        narration: "Welcome",
        actions: [{ type: "navigate", url: "https://example.com" }],
        transition: "crossfade",
      },
    ],
    ...overrides,
  };
}

describe("Script is written to project demos directory", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "demo-test-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should write script.json to <project>/demos/<name>/", async () => {
    const script = makeScript({ name: "product-tour" });

    await writeScript(script, tempDir);

    const expectedPath = join(tempDir, "demos", "product-tour", "script.json");
    expect(existsSync(expectedPath)).toBe(true);
  });

  it("should write valid JSON that matches the original script", async () => {
    const script = makeScript({ name: "product-tour" });

    await writeScript(script, tempDir);

    const content = readFileSync(
      join(tempDir, "demos", "product-tour", "script.json"),
      "utf-8"
    );
    const parsed = JSON.parse(content);

    expect(parsed.version).toBe(1);
    expect(parsed.name).toBe("product-tour");
    expect(parsed.scenes).toHaveLength(1);
  });

  it("should create the scenes/ subdirectory", async () => {
    const script = makeScript({ name: "product-tour" });

    await writeScript(script, tempDir);

    const scenesDir = join(tempDir, "demos", "product-tour", "scenes");
    expect(existsSync(scenesDir)).toBe(true);
  });

  it("should be readable back with readScript", async () => {
    const script = makeScript({ name: "round-trip" });

    await writeScript(script, tempDir);

    const loaded = await readScript(
      join(tempDir, "demos", "round-trip", "script.json")
    );

    expect(loaded.name).toBe("round-trip");
    expect(loaded.scenes).toHaveLength(1);
  });
});

describe("Re-running a demo script overwrites previous output cleanly", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "demo-test-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should replace previous script.json when re-run", async () => {
    const script1 = makeScript({
      name: "overwrite-test",
      scenes: [
        {
          id: "v1",
          narration: "Version 1",
          actions: [],
          transition: "crossfade",
        },
      ],
    });
    const script2 = makeScript({
      name: "overwrite-test",
      scenes: [
        {
          id: "v2",
          narration: "Version 2",
          actions: [],
          transition: "crossfade",
        },
      ],
    });

    await writeScript(script1, tempDir);
    await writeScript(script2, tempDir);

    const loaded = await readScript(
      join(tempDir, "demos", "overwrite-test", "script.json")
    );

    expect(loaded.scenes[0].id).toBe("v2");
  });

  it("should not leave duplicate artifacts after re-run", async () => {
    const script = makeScript({ name: "clean-rerun" });

    await writeScript(script, tempDir);
    await writeScript(script, tempDir);

    const content = readFileSync(
      join(tempDir, "demos", "clean-rerun", "script.json"),
      "utf-8"
    );
    const parsed = JSON.parse(content);

    expect(parsed.scenes).toHaveLength(1);
  });
});
