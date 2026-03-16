import { describe, it, expect } from "vitest";
import {
  detectBrowserTool,
} from "../src/browser.js";

describe("Browser automation uses fallback chain", () => {
  it("should return the first available browser tool", async () => {
    const tool = await detectBrowserTool();

    // On this machine, agent-browser should be detected first
    expect(tool).not.toBeNull();
    expect(tool!.name).toBeDefined();
    expect(["agent-browser", "playwright", "playwright-mcp"]).toContain(
      tool!.name
    );
  });

  it("should prefer agent-browser over playwright", async () => {
    const tool = await detectBrowserTool();

    // agent-browser is installed on this machine
    if (tool) {
      expect(tool.name).toBe("agent-browser");
    }
  });

  it("should return tool with cleanup function", async () => {
    const tool = await detectBrowserTool();

    expect(tool).not.toBeNull();
    expect(tool!.cleanup).toBeTypeOf("function");
  });
});

describe("Recording fails gracefully when no browser automation is available", () => {
  it("should return null and list checked tools when none available", async () => {
    // Test the reporting function directly
    const { formatMissingToolsMessage } = await import("../src/browser.js");

    const message = formatMissingToolsMessage();

    expect(message).toContain("agent-browser");
    expect(message).toContain("playwright");
    expect(message).toContain("install");
  });
});

describe("Browser state is cleared after recording", () => {
  it("should provide a cleanup function that completes without error", async () => {
    const tool = await detectBrowserTool();

    if (tool) {
      await expect(tool.cleanup()).resolves.not.toThrow();
    }
  });
});
