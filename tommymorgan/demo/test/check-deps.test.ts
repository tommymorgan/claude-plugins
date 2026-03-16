import { describe, it, expect } from "vitest";
import { checkSystemDependencies } from "../src/check-deps.js";

describe("Local development environment is configured", () => {
  it("should report whether ffmpeg is available", async () => {
    const result = await checkSystemDependencies();

    expect(result.ffmpeg).toEqual(
      expect.objectContaining({
        name: "ffmpeg",
        available: expect.any(Boolean),
      })
    );
  });

  it("should report whether at least one browser automation tool is available", async () => {
    const result = await checkSystemDependencies();

    const browserTools = [
      result.agentBrowser,
      result.playwrightCli,
      result.playwrightMcp,
    ];

    for (const tool of browserTools) {
      expect(tool).toEqual(
        expect.objectContaining({
          name: expect.any(String),
          available: expect.any(Boolean),
        })
      );
    }
  });

  it("should report all dependencies in a single structured result", async () => {
    const result = await checkSystemDependencies();

    expect(result).toEqual(
      expect.objectContaining({
        ffmpeg: expect.objectContaining({ name: "ffmpeg" }),
        agentBrowser: expect.objectContaining({ name: "agent-browser" }),
        playwrightCli: expect.objectContaining({ name: "playwright" }),
        playwrightMcp: expect.objectContaining({ name: "playwright-mcp" }),
      })
    );
  });
});
