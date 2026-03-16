---
name: tommymorgan:demo
description: Create polished product demo videos with natural TTS narration
user_invocable: true
---

# Create Demo Video

Create an automated product demo video with natural voice narration.

## Usage

- `/tommymorgan:demo` — Start a conversational demo creation session
- `/tommymorgan:demo <plan-file>` — Generate demo from a plan file's Demo Scenarios section

## Workflow

### Step 1: Determine Demo Parameters

**If a plan file path is provided:**
- Read the plan file
- Extract the "Demo Scenarios" section
- Generate the demo script automatically without user interaction

**If no plan file is provided:**
- Ask the user one question at a time:
  1. What product/feature are you demoing?
  2. What's the URL to start from?
  3. Who's the audience? (marketing / technical / both)
  4. Which recording strategy? (scene-based / continuous / screenshot)
  5. Target duration? (30s / 1min / 2min / custom)

### Step 2: Generate Demo Script

Generate a structured demo script with scenes based on the user's description.

Present the script scene-by-scene for approval:
```
Scene 1: "<title>"
  Narration: "<text>"
  Actions: <list>

Scene 2: "<title>"
  Narration: "<text>"
  Actions: <list>
```

The user can edit narration text, reorder scenes, or add/remove scenes.

**Sensitive content check:** If any scene navigates to a URL requiring authentication, warn:
```
⚠️ This demo targets authenticated URLs. The recording may capture sensitive
data (user info, tokens, private content). Review the final video before sharing.
```

### Step 3: Write Script to Disk

Write the finalized script using the demo orchestrator:

```bash
cd <project>/demos/<name>
node <plugin-root>/demo/dist/script-io.js write
```

The script is saved to `<project>/demos/<name>/script.json`.

### Step 4: Execute Recording Pipeline

Run the four-stage pipeline:

1. **Check dependencies** — Verify ffmpeg and browser tools are available
2. **Record scenes** — Using the selected strategy (scene-based / continuous / screenshot)
3. **Generate narration** — Edge TTS for each scene's narration text
4. **Compose video** — ffmpeg combines video + audio + transitions into MP4

Report progress at each stage.

### Step 5: Review and Iterate

After composition completes:
- Report the output file path: `<project>/demos/<name>/output.mp4`
- Report subtitle file: `<project>/demos/<name>/output.vtt`

If the user wants to re-record a specific scene:
- Re-run only that scene's recording and narration
- Recompose the full video

### Important Notes

- Browser automation priority: agent-browser → playwright CLI → playwright MCP
- Browser sessions are cleared after recording completes
- Re-running the same demo overwrites previous output cleanly
- All errors are logged to `<project>/demos/<name>/errors.log`
