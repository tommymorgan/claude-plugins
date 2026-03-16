import { describe, it, expect } from "vitest";
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

const projectRoot = resolve(import.meta.dirname, "..");

describe("Demo orchestrator is a TypeScript Node.js project", () => {
  it("should compile TypeScript with no type errors", () => {
    const result = execFileSync("npx", ["tsc", "--noEmit"], {
      cwd: projectRoot,
      encoding: "utf-8",
    });

    expect(result.trim()).toBe("");
  });

  it("should produce dist output when built", () => {
    execFileSync("npx", ["tsc"], {
      cwd: projectRoot,
      encoding: "utf-8",
    });

    expect(existsSync(resolve(projectRoot, "dist", "index.js"))).toBe(true);
  });

  it("should export the orchestrator entry point", async () => {
    const mod = await import("../src/index.js");

    expect(mod.createDemo).toBeTypeOf("function");
  });
});
