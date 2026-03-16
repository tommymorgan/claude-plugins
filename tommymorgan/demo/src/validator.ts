import { execFile } from "node:child_process";
import { promisify } from "node:util";
import type { DemoScript } from "./script-schema.js";

const execFileAsync = promisify(execFile);

export interface ValidationResult {
  hasVideo: boolean;
  hasAudio: boolean;
  durationMs: number;
  videoCodec: string | null;
  audioCodec: string | null;
}

export async function validateOutput(
  videoPath: string,
  _script: DemoScript
): Promise<ValidationResult> {
  const { stdout } = await execFileAsync("ffprobe", [
    "-v",
    "quiet",
    "-show_streams",
    "-show_format",
    "-of",
    "json",
    videoPath,
  ], { timeout: 30000 });

  let probe;
  try {
    probe = JSON.parse(stdout);
  } catch {
    throw new Error(`ffprobe returned invalid JSON for ${videoPath}`);
  }

  const videoStream = probe.streams?.find(
    (s: { codec_type: string }) => s.codec_type === "video"
  );
  const audioStream = probe.streams?.find(
    (s: { codec_type: string }) => s.codec_type === "audio"
  );

  const durationSecs = parseFloat(probe.format?.duration ?? "0");

  return {
    hasVideo: !!videoStream,
    hasAudio: !!audioStream,
    durationMs: Math.round(durationSecs * 1000),
    videoCodec: videoStream?.codec_name ?? null,
    audioCodec: audioStream?.codec_name ?? null,
  };
}
