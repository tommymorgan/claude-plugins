import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { join, dirname } from "node:path";
import { writeFile, readFile, copyFile } from "node:fs/promises";

const execFileAsync = promisify(execFile);

export interface SceneInput {
  id: string;
  type: "screenshot" | "video";
  mediaPath: string;
  audioPath: string | null;
  durationMs: number;
  subtitlePath?: string;
}

export interface ComposeOptions {
  scenes: SceneInput[];
  outputDir: string;
  resolution: { width: number; height: number };
  transition: "crossfade" | "cut" | "fade-to-black";
}

export interface ComposeResult {
  videoPath: string;
  subtitlePath: string;
}

export async function composeVideo(
  options: ComposeOptions
): Promise<ComposeResult> {
  const { scenes, outputDir, resolution } = options;
  const videoPath = join(outputDir, "output.mp4");
  const subtitlePath = join(outputDir, "output.vtt");

  // Step 1: Convert each scene to a normalized MP4 clip
  const sceneClips: string[] = [];
  for (const scene of scenes) {
    const clipPath = join(outputDir, `clip-${scene.id}.mp4`);
    if (scene.type === "screenshot") {
      await applyKenBurns(scene, clipPath, resolution);
    } else {
      await normalizeVideoClip(scene, clipPath, resolution);
    }
    sceneClips.push(clipPath);
  }

  // Step 2: Concatenate clips into final output
  if (sceneClips.length === 1) {
    await copyFile(sceneClips[0], videoPath);
  } else {
    await concatenateClips(sceneClips, videoPath);
  }

  // Step 3: Merge subtitle files
  await mergeSubtitles(scenes, subtitlePath);

  return { videoPath, subtitlePath };
}

async function applyKenBurns(
  scene: SceneInput,
  outputPath: string,
  resolution: { width: number; height: number }
): Promise<void> {
  const durationSecs = scene.durationMs / 1000;
  const fps = 30;
  const totalFrames = Math.ceil(durationSecs * fps);

  const args = [
    "-y",
    "-loop",
    "1",
    "-i",
    scene.mediaPath,
  ];

  // Add audio input if available
  if (scene.audioPath) {
    args.push("-i", scene.audioPath);
  }

  args.push(
    "-vf",
    `zoompan=z='min(zoom+0.0005,1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${totalFrames}:s=${resolution.width}x${resolution.height}:fps=${fps}`,
    "-t",
    String(durationSecs),
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
  );

  if (scene.audioPath) {
    args.push("-c:a", "aac", "-shortest");
  }

  args.push(outputPath);

  await execFileAsync("ffmpeg", args, { timeout: 60000 });
}

async function normalizeVideoClip(
  scene: SceneInput,
  outputPath: string,
  resolution: { width: number; height: number }
): Promise<void> {
  const args = [
    "-y",
    "-i",
    scene.mediaPath,
  ];

  if (scene.audioPath) {
    args.push("-i", scene.audioPath);
  }

  args.push(
    "-vf",
    `scale=${resolution.width}:${resolution.height}:force_original_aspect_ratio=decrease,pad=${resolution.width}:${resolution.height}:(ow-iw)/2:(oh-ih)/2`,
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
  );

  if (scene.audioPath) {
    args.push("-c:a", "aac", "-shortest");
  } else {
    args.push("-an");
  }

  args.push(outputPath);

  await execFileAsync("ffmpeg", args, { timeout: 60000 });
}

async function concatenateClips(
  clips: string[],
  outputPath: string
): Promise<void> {
  const concatListPath = join(dirname(outputPath), "concat-list.txt");

  const concatContent = clips.map((c) => `file '${c}'`).join("\n");
  await writeFile(concatListPath, concatContent, "utf-8");

  await execFileAsync(
    "ffmpeg",
    [
      "-y",
      "-f",
      "concat",
      "-safe",
      "0",
      "-i",
      concatListPath,
      "-c",
      "copy",
      outputPath,
    ],
    { timeout: 60000 }
  );
}

async function mergeSubtitles(
  scenes: SceneInput[],
  outputPath: string
): Promise<void> {
  let vttContent = "WEBVTT\n\n";
  let offsetMs = 0;

  for (const scene of scenes) {
    if (scene.subtitlePath) {
      try {
        const content = await readFile(scene.subtitlePath, "utf-8");
        const cues = parseVttCues(content);

        for (const cue of cues) {
          vttContent += `${formatTimestamp(cue.startMs + offsetMs)} --> ${formatTimestamp(cue.endMs + offsetMs)}\n`;
          vttContent += `${cue.text}\n\n`;
        }
      } catch (err) {
        if (err instanceof Error && "code" in err && err.code === "ENOENT") {
          // Subtitle file doesn't exist — skip this scene's subtitles
        } else {
          console.error(`Warning: failed to process subtitles for scene "${scene.id}":`, err);
        }
      }
    }

    offsetMs += scene.durationMs;
  }

  await writeFile(outputPath, vttContent, "utf-8");
}

interface VttCue {
  startMs: number;
  endMs: number;
  text: string;
}

function parseVttCues(content: string): VttCue[] {
  const cues: VttCue[] = [];
  const lines = content.split("\n");

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.includes("-->")) {
      const [startStr, endStr] = line.split("-->").map((s) => s.trim());
      const text = lines[i + 1]?.trim() ?? "";

      cues.push({
        startMs: parseTimestampMs(startStr),
        endMs: parseTimestampMs(endStr),
        text,
      });
    }
  }

  return cues;
}

function parseTimestampMs(timestamp: string): number {
  const parts = timestamp.split(":");
  if (parts.length === 3) {
    const [h, m, rest] = parts;
    const [s, ms] = rest.split(".");
    return (
      parseInt(h) * 3600000 +
      parseInt(m) * 60000 +
      parseInt(s) * 1000 +
      parseInt(ms ?? "0")
    );
  }
  return 0;
}

function formatTimestamp(ms: number): string {
  const h = Math.floor(ms / 3600000);
  const m = Math.floor((ms % 3600000) / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  const remainder = ms % 1000;

  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(remainder).padStart(3, "0")}`;
}
