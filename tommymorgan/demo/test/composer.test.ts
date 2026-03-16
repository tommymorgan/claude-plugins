import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { composeVideo, type ComposeOptions } from "../src/composer.js";
import { generateNarration } from "../src/tts.js";
import {
  mkdtempSync,
  rmSync,
  existsSync,
  writeFileSync,
  mkdirSync,
} from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { execFileSync } from "node:child_process";

function createTestPng(path: string, width = 1920, height = 1080): void {
  // Generate a minimal valid PNG using ffmpeg
  execFileSync("ffmpeg", [
    "-y",
    "-f",
    "lavfi",
    "-i",
    `color=c=blue:s=${width}x${height}:d=1`,
    "-frames:v",
    "1",
    path,
  ]);
}

function createTestWebm(path: string, durationSecs = 2): void {
  execFileSync("ffmpeg", [
    "-y",
    "-f",
    "lavfi",
    "-i",
    `color=c=red:s=1920x1080:d=${durationSecs}`,
    "-c:v",
    "libvpx-vp9",
    path,
  ]);
}

describe("Screenshot strategy applies Ken Burns effect", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "composer-test-"));
    mkdirSync(join(tempDir, "scenes"), { recursive: true });
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should produce a video clip from a screenshot with pan/zoom animation", async () => {
    const pngPath = join(tempDir, "scenes", "intro.png");
    createTestPng(pngPath);

    const result = await composeVideo({
      scenes: [
        {
          id: "intro",
          type: "screenshot",
          mediaPath: pngPath,
          audioPath: null,
          durationMs: 3000,
        },
      ],
      outputDir: tempDir,
      resolution: { width: 1920, height: 1080 },
      transition: "crossfade",
    });

    expect(existsSync(result.videoPath)).toBe(true);
    expect(result.videoPath).toMatch(/\.mp4$/);
  }, 30000);
});

describe("Scene-based clips are concatenated with crossfade transitions", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "composer-test-"));
    mkdirSync(join(tempDir, "scenes"), { recursive: true });
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should concatenate multiple video clips into one output", async () => {
    const clip1 = join(tempDir, "scenes", "scene1.webm");
    const clip2 = join(tempDir, "scenes", "scene2.webm");
    createTestWebm(clip1, 2);
    createTestWebm(clip2, 2);

    const result = await composeVideo({
      scenes: [
        {
          id: "scene1",
          type: "video",
          mediaPath: clip1,
          audioPath: null,
          durationMs: 2000,
        },
        {
          id: "scene2",
          type: "video",
          mediaPath: clip2,
          audioPath: null,
          durationMs: 2000,
        },
      ],
      outputDir: tempDir,
      resolution: { width: 1920, height: 1080 },
      transition: "crossfade",
    });

    expect(existsSync(result.videoPath)).toBe(true);
  }, 30000);
});

describe("Final output is H.264 MP4 with AAC audio", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "composer-test-"));
    mkdirSync(join(tempDir, "scenes"), { recursive: true });
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should encode output as H.264 video with AAC audio", async () => {
    const pngPath = join(tempDir, "scenes", "test.png");
    createTestPng(pngPath);

    // Generate real audio
    const narration = await generateNarration({
      sceneId: "test",
      text: "This is a test.",
      voice: { name: "en-US-GuyNeural" },
      outputDir: join(tempDir, "scenes"),
    });

    const result = await composeVideo({
      scenes: [
        {
          id: "test",
          type: "screenshot",
          mediaPath: pngPath,
          audioPath: narration.audioPath,
          durationMs: narration.durationMs,
        },
      ],
      outputDir: tempDir,
      resolution: { width: 1920, height: 1080 },
      transition: "crossfade",
    });

    // Verify codec info with ffprobe
    const probeOutput = execFileSync("ffprobe", [
      "-v",
      "quiet",
      "-show_streams",
      "-of",
      "json",
      result.videoPath,
    ], { encoding: "utf-8" });

    const probe = JSON.parse(probeOutput);
    const videoStream = probe.streams.find(
      (s: { codec_type: string }) => s.codec_type === "video"
    );
    const audioStream = probe.streams.find(
      (s: { codec_type: string }) => s.codec_type === "audio"
    );

    expect(videoStream.codec_name).toBe("h264");
    expect(audioStream.codec_name).toBe("aac");
  }, 30000);
});

describe("Subtitles are generated as a sidecar file", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "composer-test-"));
    mkdirSync(join(tempDir, "scenes"), { recursive: true });
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should produce a .vtt subtitle file alongside the MP4", async () => {
    const pngPath = join(tempDir, "scenes", "sub-test.png");
    createTestPng(pngPath);

    const narration = await generateNarration({
      sceneId: "sub-test",
      text: "Subtitle test narration.",
      voice: { name: "en-US-GuyNeural" },
      outputDir: join(tempDir, "scenes"),
    });

    const result = await composeVideo({
      scenes: [
        {
          id: "sub-test",
          type: "screenshot",
          mediaPath: pngPath,
          audioPath: narration.audioPath,
          durationMs: narration.durationMs,
          subtitlePath: narration.subtitlePath,
        },
      ],
      outputDir: tempDir,
      resolution: { width: 1920, height: 1080 },
      transition: "crossfade",
    });

    expect(existsSync(result.subtitlePath)).toBe(true);
    expect(result.subtitlePath).toMatch(/\.vtt$/);
  }, 30000);
});

describe("Demo output directory contains all artifacts", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "composer-test-"));
    mkdirSync(join(tempDir, "scenes"), { recursive: true });
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should write output.mp4 and output.vtt to the output directory", async () => {
    const pngPath = join(tempDir, "scenes", "artifact-test.png");
    createTestPng(pngPath);

    const narration = await generateNarration({
      sceneId: "artifact-test",
      text: "Artifact test.",
      voice: { name: "en-US-GuyNeural" },
      outputDir: join(tempDir, "scenes"),
    });

    const result = await composeVideo({
      scenes: [
        {
          id: "artifact-test",
          type: "screenshot",
          mediaPath: pngPath,
          audioPath: narration.audioPath,
          durationMs: narration.durationMs,
          subtitlePath: narration.subtitlePath,
        },
      ],
      outputDir: tempDir,
      resolution: { width: 1920, height: 1080 },
      transition: "crossfade",
    });

    expect(result.videoPath).toBe(join(tempDir, "output.mp4"));
    expect(result.subtitlePath).toBe(join(tempDir, "output.vtt"));
    expect(existsSync(result.videoPath)).toBe(true);
    expect(existsSync(result.subtitlePath)).toBe(true);
  }, 30000);
});
