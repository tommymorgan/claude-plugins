export { checkSystemDependencies } from "./check-deps.js";
export { DemoScriptSchema } from "./script-schema.js";
export type { DemoScript, Scene, Action, VoiceSettings } from "./script-schema.js";
export { writeScript, readScript } from "./script-io.js";
export { generateNarration } from "./tts.js";
export type { NarrationOptions, NarrationResult } from "./tts.js";
export { detectBrowserTool, formatMissingToolsMessage } from "./browser.js";
export type { BrowserTool } from "./browser.js";
export { recordScene } from "./recorder.js";
export type { RecordSceneOptions, RecordingResult } from "./recorder.js";
export { composeVideo } from "./composer.js";
export type { ComposeOptions, ComposeResult, SceneInput } from "./composer.js";
export { runPipeline, rerecordScene } from "./pipeline.js";
export type { PipelineResult, SceneResult } from "./pipeline.js";
export { validateOutput } from "./validator.js";
export type { ValidationResult } from "./validator.js";
export { detectSensitiveUrls } from "./sensitive.js";

export interface CreateDemoOptions {
  scriptPath?: string;
  outputDir?: string;
}

export async function createDemo(
  _options?: CreateDemoOptions
): Promise<void> {
  // Orchestrator entry point — implemented in later scenarios
}
