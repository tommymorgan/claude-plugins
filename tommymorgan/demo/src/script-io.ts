import { mkdir, writeFile, readFile, rm } from "node:fs/promises";
import { join } from "node:path";
import { DemoScriptSchema, type DemoScript } from "./script-schema.js";

export async function writeScript(
  script: DemoScript,
  projectDir: string
): Promise<string> {
  const demoDir = join(projectDir, "demos", script.name);
  const scenesDir = join(demoDir, "scenes");

  // Clean previous output for idempotent re-runs
  await rm(demoDir, { recursive: true, force: true });

  await mkdir(scenesDir, { recursive: true });

  const scriptPath = join(demoDir, "script.json");
  await writeFile(scriptPath, JSON.stringify(script, null, 2), "utf-8");

  return scriptPath;
}

export async function readScript(scriptPath: string): Promise<DemoScript> {
  const content = await readFile(scriptPath, "utf-8");
  const parsed = JSON.parse(content);

  return DemoScriptSchema.parse(parsed);
}
