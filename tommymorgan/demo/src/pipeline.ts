import { mkdir } from "node:fs/promises";
import { appendFile } from "node:fs/promises";
import { join } from "node:path";
import type { DemoScript } from "./script-schema.js";
import { recordScene, type RecordingResult } from "./recorder.js";
import { generateNarration, type NarrationResult } from "./tts.js";
import { composeVideo, type SceneInput } from "./composer.js";

export interface SceneResult {
  sceneId: string;
  success: boolean;
  error?: string;
  recording?: RecordingResult;
  narration?: NarrationResult;
}

export interface PipelineResult {
  success: boolean;
  videoPath?: string;
  subtitlePath?: string;
  sceneResults: SceneResult[];
}

export async function runPipeline(
  script: DemoScript,
  outputDir: string
): Promise<PipelineResult> {
  const scenesDir = join(outputDir, "scenes");
  await mkdir(scenesDir, { recursive: true });

  const errorsLogPath = join(outputDir, "errors.log");
  const sceneResults: SceneResult[] = [];
  const successfulScenes: SceneInput[] = [];

  // Process each scene independently
  for (const scene of script.scenes) {
    const result = await processScene(
      scene,
      script,
      scenesDir,
      errorsLogPath
    );
    sceneResults.push(result);

    if (result.success && result.recording && result.narration) {
      successfulScenes.push({
        id: scene.id,
        type: result.recording.type,
        mediaPath: result.recording.path,
        audioPath: result.narration.audioPath,
        durationMs: result.narration.durationMs,
        subtitlePath: result.narration.subtitlePath,
      });
    }
  }

  const hasFailures = sceneResults.some((r) => !r.success);

  // Compose only if we have at least one successful scene
  if (successfulScenes.length > 0) {
    try {
      const composed = await composeVideo({
        scenes: successfulScenes,
        outputDir,
        resolution: script.resolution,
        transition: script.scenes[0]?.transition ?? "crossfade",
      });

      return {
        success: !hasFailures,
        videoPath: composed.videoPath,
        subtitlePath: composed.subtitlePath,
        sceneResults,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      await safeAppendError(errorsLogPath, `Composition failed: ${errorMessage}`);

      return { success: false, sceneResults };
    }
  }

  return {
    success: false,
    sceneResults,
  };
}

export async function rerecordScene(
  script: DemoScript,
  sceneId: string,
  outputDir: string
): Promise<SceneResult> {
  const scene = script.scenes.find((s) => s.id === sceneId);
  if (!scene) {
    return { sceneId, success: false, error: `Scene "${sceneId}" not found` };
  }

  const scenesDir = join(outputDir, "scenes");
  await mkdir(scenesDir, { recursive: true });

  const errorsLogPath = join(outputDir, "errors.log");
  return processScene(scene, script, scenesDir, errorsLogPath);
}

async function processScene(
  scene: DemoScript["scenes"][number],
  script: DemoScript,
  scenesDir: string,
  errorsLogPath: string
): Promise<SceneResult> {
  try {
    // Step 1: Record
    const recording = await recordScene({
      scene,
      strategy: script.strategy,
      outputDir: scenesDir,
      resolution: script.resolution,
    });

    // Step 2: Generate narration
    const narration = await generateNarration({
      sceneId: scene.id,
      text: scene.narration,
      voice: script.voice,
      outputDir: scenesDir,
      voiceOverrides: scene.voiceOverrides,
    });

    return {
      sceneId: scene.id,
      success: true,
      recording,
      narration,
    };
  } catch (err) {
    const errorMessage =
      err instanceof Error ? err.message : String(err);

    await safeAppendError(errorsLogPath, `Scene "${scene.id}" failed: ${errorMessage}`);

    return {
      sceneId: scene.id,
      success: false,
      error: errorMessage,
    };
  }
}

async function safeAppendError(logPath: string, message: string): Promise<void> {
  try {
    await appendFile(logPath, `[${new Date().toISOString()}] ${message}\n`, "utf-8");
  } catch {
    console.error(`Failed to write to error log: ${message}`);
  }
}
