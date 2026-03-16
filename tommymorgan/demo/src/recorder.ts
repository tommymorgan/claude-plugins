import { chromium, type Browser, type Page } from "playwright";
import { join } from "node:path";
import { rename } from "node:fs/promises";
import type { Scene, Action } from "./script-schema.js";

export interface RecordSceneOptions {
  scene: Scene;
  strategy: "scene-based" | "continuous" | "screenshot";
  outputDir: string;
  resolution: { width: number; height: number };
  browser?: Browser;
}

export interface RecordingResult {
  type: "screenshot" | "video";
  path: string;
  sceneId: string;
}

async function executeAction(page: Page, action: Action): Promise<void> {
  switch (action.type) {
    case "navigate":
      await page.goto(action.url, { waitUntil: "networkidle" });
      break;
    case "click":
      await page.click(action.selector);
      break;
    case "fill":
      await page.fill(action.selector, action.value);
      break;
    case "wait":
      await page.waitForTimeout(action.duration);
      break;
    case "scroll":
      await page.evaluate(
        ({ direction, amount }) => {
          window.scrollBy(0, direction === "down" ? amount : -amount);
        },
        { direction: action.direction, amount: action.amount }
      );
      break;
    case "hover":
      await page.hover(action.selector);
      break;
    case "screenshot":
      // No-op here — screenshot is taken at the end for screenshot strategy
      break;
    case "highlight":
      await page.evaluate((selector: string) => {
        const el = document.querySelector(selector);
        if (el instanceof HTMLElement) {
          el.style.outline = "3px solid #ff0000";
          el.style.outlineOffset = "2px";
        }
      }, action.selector);
      break;
  }
}

async function executeActions(page: Page, actions: Action[]): Promise<void> {
  for (const action of actions) {
    try {
      await executeAction(page, action);
    } catch (err) {
      const detail = "selector" in action ? ` on "${action.selector}"` : "url" in action ? ` for "${action.url}"` : "";
      throw new Error(`Action "${action.type}"${detail} failed: ${err instanceof Error ? err.message : String(err)}`);
    }
  }
}

export async function recordScene(
  options: RecordSceneOptions
): Promise<RecordingResult> {
  const { scene, strategy, outputDir, resolution } = options;

  if (strategy === "screenshot") {
    return recordScreenshot(scene, outputDir, resolution);
  }

  return recordVideo(scene, outputDir, resolution, options.browser);
}

async function recordScreenshot(
  scene: Scene,
  outputDir: string,
  resolution: { width: number; height: number }
): Promise<RecordingResult> {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: resolution.width, height: resolution.height },
  });
  const page = await context.newPage();

  try {
    await executeActions(page, scene.actions);

    const screenshotPath = join(outputDir, `${scene.id}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: false });

    return { type: "screenshot", path: screenshotPath, sceneId: scene.id };
  } finally {
    await context.close();
    await browser.close();
  }
}

async function recordVideo(
  scene: Scene,
  outputDir: string,
  resolution: { width: number; height: number },
  existingBrowser?: Browser
): Promise<RecordingResult> {
  const browser = existingBrowser ?? (await chromium.launch({ headless: true }));
  const context = await browser.newContext({
    viewport: { width: resolution.width, height: resolution.height },
    recordVideo: {
      dir: outputDir,
      size: { width: resolution.width, height: resolution.height },
    },
  });
  const page = await context.newPage();
  let generatedVideoPath: string | undefined;

  try {
    await executeActions(page, scene.actions);

    // Small delay to capture the final state
    await page.waitForTimeout(500);

    // Capture the video path before closing — Playwright provides this API
    generatedVideoPath = await page.video()?.path() ?? undefined;
  } finally {
    await page.close();
    await context.close();

    if (!existingBrowser) {
      await browser.close();
    }
  }

  const videoPath = join(outputDir, `${scene.id}.webm`);

  if (generatedVideoPath) {
    await rename(generatedVideoPath, videoPath);
  } else {
    throw new Error(`Recording for scene "${scene.id}" produced no video file in ${outputDir}`);
  }

  return { type: "video", path: videoPath, sceneId: scene.id };
}
