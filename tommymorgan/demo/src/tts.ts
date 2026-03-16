import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { join } from "node:path";
import { stat } from "node:fs/promises";
import type { VoiceSettings } from "./script-schema.js";

const execFileAsync = promisify(execFile);

export interface NarrationOptions {
  sceneId: string;
  text: string;
  voice: VoiceSettings;
  outputDir: string;
  voiceOverrides?: Partial<Omit<VoiceSettings, "name">>;
}

export interface NarrationResult {
  audioPath: string;
  subtitlePath: string;
  durationMs: number;
}

export async function generateNarration(
  options: NarrationOptions
): Promise<NarrationResult> {
  const audioPath = join(options.outputDir, `${options.sceneId}.mp3`);
  const subtitlePath = join(options.outputDir, `${options.sceneId}.vtt`);

  const effectiveRate = options.voiceOverrides?.rate ?? options.voice.rate;
  const effectivePitch = options.voiceOverrides?.pitch ?? options.voice.pitch;

  const args = [
    "--text",
    options.text,
    "--voice",
    options.voice.name,
    "--write-media",
    audioPath,
    "--write-subtitles",
    subtitlePath,
  ];

  if (effectiveRate) {
    args.push(`--rate=${effectiveRate}`);
  }

  if (effectivePitch) {
    args.push(`--pitch=${effectivePitch}`);
  }

  await execFileAsync("edge-tts", args, { timeout: 30000 });

  const durationMs = await getAudioDurationMs(audioPath);

  return { audioPath, subtitlePath, durationMs };
}

async function getAudioDurationMs(audioPath: string): Promise<number> {
  try {
    const { stdout } = await execFileAsync("ffprobe", [
      "-v",
      "quiet",
      "-show_entries",
      "format=duration",
      "-of",
      "csv=p=0",
      audioPath,
    ]);

    return Math.round(parseFloat(stdout.trim()) * 1000);
  } catch {
    // Fallback: estimate from file size (128kbps MP3 ≈ 16KB/s)
    const fileStat = await stat(audioPath);
    return Math.round((fileStat.size / 16000) * 1000);
  }
}
