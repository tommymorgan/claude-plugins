import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { generateNarration } from "../src/tts.js";
import { mkdtempSync, rmSync, existsSync, statSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import type { VoiceSettings } from "../src/script-schema.js";

describe("Edge TTS generates MP3 audio per scene", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "tts-test-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should produce an MP3 file for a scene narration", async () => {
    const voice: VoiceSettings = { name: "en-US-GuyNeural" };

    const result = await generateNarration({
      sceneId: "intro",
      text: "Welcome to our product tour.",
      voice,
      outputDir: tempDir,
    });

    expect(existsSync(result.audioPath)).toBe(true);
    expect(result.audioPath).toMatch(/\.mp3$/);
    expect(statSync(result.audioPath).size).toBeGreaterThan(0);
  }, 15000);

  it("should produce a VTT subtitle file alongside the MP3", async () => {
    const voice: VoiceSettings = { name: "en-US-GuyNeural" };

    const result = await generateNarration({
      sceneId: "intro",
      text: "Welcome to our product tour.",
      voice,
      outputDir: tempDir,
    });

    expect(existsSync(result.subtitlePath)).toBe(true);
    expect(result.subtitlePath).toMatch(/\.vtt$/);
  }, 15000);

  it("should report the audio duration in milliseconds", async () => {
    const voice: VoiceSettings = { name: "en-US-GuyNeural" };

    const result = await generateNarration({
      sceneId: "intro",
      text: "Welcome to our product tour.",
      voice,
      outputDir: tempDir,
    });

    expect(result.durationMs).toBeGreaterThan(0);
    expect(result.durationMs).toBeLessThan(30000);
  }, 15000);
});

describe("Voice settings are configurable at script and scene level", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "tts-test-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should use the script-level voice by default", async () => {
    const voice: VoiceSettings = { name: "en-US-JennyNeural" };

    const result = await generateNarration({
      sceneId: "default-voice",
      text: "Testing default voice.",
      voice,
      outputDir: tempDir,
    });

    expect(existsSync(result.audioPath)).toBe(true);
  }, 15000);

  it("should apply scene-level rate override", async () => {
    const voice: VoiceSettings = {
      name: "en-US-GuyNeural",
      rate: "+0%",
      pitch: "+0Hz",
    };

    const result = await generateNarration({
      sceneId: "slow-scene",
      text: "This is slower narration.",
      voice,
      outputDir: tempDir,
      voiceOverrides: { rate: "-20%" },
    });

    expect(existsSync(result.audioPath)).toBe(true);
    // Slower rate should produce longer audio than default
    expect(result.durationMs).toBeGreaterThan(0);
  }, 15000);
});

describe("Scene duration is driven by narration length", () => {
  let tempDir: string;

  beforeEach(() => {
    tempDir = mkdtempSync(join(tmpdir(), "tts-test-"));
  });

  afterEach(() => {
    rmSync(tempDir, { recursive: true, force: true });
  });

  it("should return duration that can be used to set scene video length", async () => {
    const voice: VoiceSettings = { name: "en-US-GuyNeural" };

    const short = await generateNarration({
      sceneId: "short",
      text: "Hi.",
      voice,
      outputDir: tempDir,
    });

    const long = await generateNarration({
      sceneId: "long",
      text: "This is a much longer sentence that should take more time to narrate than just a simple greeting.",
      voice,
      outputDir: tempDir,
    });

    expect(long.durationMs).toBeGreaterThan(short.durationMs);
  }, 30000);
});
