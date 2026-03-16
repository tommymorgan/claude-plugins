import { describe, it, expect } from "vitest";
import {
  DemoScriptSchema,
} from "../src/script-schema.js";

describe("Demo script follows versioned JSON schema", () => {
  it("should validate a complete demo script with all required fields", () => {
    const script: DemoScript = {
      version: 1,
      name: "product-tour",
      strategy: "scene-based",
      resolution: { width: 1920, height: 1080 },
      voice: { name: "en-US-GuyNeural", rate: "+0%", pitch: "+0Hz" },
      scenes: [
        {
          id: "welcome",
          narration: "Welcome to our product tour.",
          actions: [
            { type: "navigate", url: "https://example.com" },
            { type: "wait", duration: 2000 },
          ],
          transition: "crossfade",
        },
      ],
    };

    const result = DemoScriptSchema.safeParse(script);

    expect(result.success).toBe(true);
  });

  it("should require version field", () => {
    const script = {
      name: "test",
      strategy: "scene-based",
      resolution: { width: 1920, height: 1080 },
      voice: { name: "en-US-GuyNeural" },
      scenes: [],
    };

    const result = DemoScriptSchema.safeParse(script);

    expect(result.success).toBe(false);
  });

  it("should require each scene to have id, narration, actions, and transition", () => {
    const scene = {
      id: "test",
      narration: "Hello",
      actions: [],
      transition: "crossfade",
    };

    const script = {
      version: 1,
      name: "test",
      strategy: "scene-based",
      resolution: { width: 1920, height: 1080 },
      voice: { name: "en-US-GuyNeural" },
      scenes: [scene],
    };

    const result = DemoScriptSchema.safeParse(script);

    expect(result.success).toBe(true);
  });

  it("should reject scenes missing required fields", () => {
    const script = {
      version: 1,
      name: "test",
      strategy: "scene-based",
      resolution: { width: 1920, height: 1080 },
      voice: { name: "en-US-GuyNeural" },
      scenes: [{ id: "test" }],
    };

    const result = DemoScriptSchema.safeParse(script);

    expect(result.success).toBe(false);
  });

  it("should accept all three recording strategies", () => {
    for (const strategy of ["scene-based", "continuous", "screenshot"]) {
      const script = {
        version: 1,
        name: "test",
        strategy,
        resolution: { width: 1920, height: 1080 },
        voice: { name: "en-US-GuyNeural" },
        scenes: [],
      };

      const result = DemoScriptSchema.safeParse(script);

      expect(result.success).toBe(true);
    }
  });

  it("should support all action types", () => {
    const actions = [
      { type: "navigate" as const, url: "https://example.com" },
      { type: "click" as const, selector: "button" },
      { type: "fill" as const, selector: "#input", value: "hello" },
      { type: "wait" as const, duration: 1000 },
      { type: "scroll" as const, direction: "down" as const, amount: 500 },
      { type: "hover" as const, selector: ".menu" },
      { type: "screenshot" as const },
      { type: "highlight" as const, selector: ".important" },
    ];

    const script = {
      version: 1,
      name: "test",
      strategy: "scene-based",
      resolution: { width: 1920, height: 1080 },
      voice: { name: "en-US-GuyNeural" },
      scenes: [
        {
          id: "all-actions",
          narration: "Showing all actions",
          actions,
          transition: "crossfade",
        },
      ],
    };

    const result = DemoScriptSchema.safeParse(script);

    expect(result.success).toBe(true);
  });

  it("should allow scene-level voice overrides", () => {
    const script = {
      version: 1,
      name: "test",
      strategy: "scene-based",
      resolution: { width: 1920, height: 1080 },
      voice: { name: "en-US-GuyNeural", rate: "+0%", pitch: "+0Hz" },
      scenes: [
        {
          id: "slow",
          narration: "This is slower",
          actions: [],
          transition: "crossfade",
          voiceOverrides: { rate: "-10%" },
        },
      ],
    };

    const result = DemoScriptSchema.safeParse(script);

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.scenes[0].voiceOverrides?.rate).toBe("-10%");
    }
  });
});
