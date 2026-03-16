Feature: Automated Demo Creator with TTS Narration
  As a user, I want to create polished product demo videos with natural voice
  narration so that I can showcase software products to both technical and
  non-technical audiences.

  @technical
  Scenario: Local development environment is configured
    Given the demo module exists at tommymorgan/demo/
    When a developer runs npm install and npm run build
    Then all TypeScript dependencies are installed and the project compiles
    And system dependency checks report whether ffmpeg and browser tools are available

  @technical
  Scenario: Demo orchestrator is a TypeScript Node.js project
    Given the demo module exists at tommymorgan/demo/
    When the project is built
    Then TypeScript compiles successfully with no type errors
    And the orchestrator can be invoked via node

  @technical
  Scenario: Demo script follows versioned JSON schema
    Given a demo script is generated
    When the script is written to disk
    Then it includes version field, resolution, voice settings, and scene array
    And each scene has id, narration, actions array, and transition type

  @technical
  Scenario: Script is written to project demos directory
    Given a demo script is generated for project "my-app"
    When the script is saved
    Then it is written to <project>/demos/<name>/script.json

  @technical
  Scenario: /tommymorgan:demo command is registered in plugin.json
    Given the demo command file exists at tommymorgan/demo/commands/demo.md
    When the plugin is loaded
    Then /tommymorgan:demo is available as a command

  @technical
  Scenario: Re-running a demo script overwrites previous output cleanly
    Given a demo has been previously generated at <project>/demos/<name>/
    When the same script is executed again
    Then previous output files are replaced and no duplicate artifacts remain

  @user
  Scenario: Narration audio is generated from scene text
    Given a demo script with narration text for each scene
    When the narration step executes
    Then natural-sounding audio is generated for each scene using Edge TTS

  @user
  Scenario: Scene duration is driven by narration length
    Given narration audio has been generated for a scene
    When the scene video is composed
    Then the video duration matches the narration duration plus configurable padding

  @technical
  Scenario: Edge TTS generates MP3 audio per scene
    Given a scene with narration text "Welcome to our product tour"
    When TTS generation runs
    Then an MP3 file and VTT subtitle file are produced for that scene

  @technical
  Scenario: Voice settings are configurable at script and scene level
    Given a demo script with voice "en-US-GuyNeural" at script level
    When a scene overrides rate to "-10%"
    Then that scene uses the overridden rate while other scenes use the default

  @technical
  Scenario: Browser automation uses fallback chain
    Given the demo is ready to record
    When the recording step starts
    Then it attempts agent-browser first, then playwright CLI, then playwright MCP
    And uses the first available option

  @technical
  Scenario: Recording fails gracefully when no browser automation is available
    Given no browser automation tool is installed
    When the recording step starts
    Then the user is informed which tools were checked and how to install them
    And no partial or corrupted output is produced

  @technical
  Scenario: Browser state is cleared after recording
    Given a demo has finished recording
    When the recording step completes
    Then all browser sessions, cookies, and auth tokens are cleared

  @user
  Scenario: User chooses scene-based recording strategy
    Given a demo script exists
    When the user selects the scene-based recording strategy
    Then each scene is recorded as an isolated video clip with browser automation

  @user
  Scenario: User chooses continuous recording strategy
    Given a demo script exists
    When the user selects the continuous recording strategy
    Then all scenes are captured in a single continuous browser recording

  @user
  Scenario: User chooses screenshot sequence strategy
    Given a demo script exists
    When the user selects the screenshot sequence strategy
    Then screenshots are taken after each scene's actions and animated with pan/zoom effects

  @user
  Scenario: Scenes are composed into a final MP4 video
    Given all scenes have been recorded and narration audio generated
    When composition executes
    Then a single MP4 file is produced with all scenes, transitions, and narration

  @user
  Scenario: Subtitles are generated as a sidecar file
    Given narration audio and timing data exist for all scenes
    When composition executes
    Then a .vtt subtitle file is generated alongside the MP4

  @technical
  Scenario: Screenshot strategy applies Ken Burns effect
    Given a scene using screenshot strategy with a PNG image
    When ffmpeg processes the scene
    Then zoompan filter animates the screenshot for the duration of the narration

  @technical
  Scenario: Scene-based clips are concatenated with crossfade transitions
    Given multiple scene video clips and audio files
    When ffmpeg composition runs
    Then clips are joined with crossfade transitions and narration audio is mixed in

  @technical
  Scenario: Final output is H.264 MP4 with AAC audio
    Given all scenes are composed
    When the final encoding step runs
    Then the output is an MP4 file with H.264 video codec and AAC audio codec

  @technical
  Scenario: Demo output directory contains all artifacts
    Given a completed demo named "product-tour"
    When the output is written
    Then the directory contains script.json, scenes/ with per-scene files, output.mp4, and output.vtt

  @technical
  Scenario: Failed scene does not block other scenes
    Given a scene fails during recording due to a selector not found
    When other scenes are still pending
    Then remaining scenes continue recording and a failure report is generated

  @technical
  Scenario: Errors are logged for automation pipelines
    Given a demo runs in automation mode
    When any step fails
    Then errors are written to errors.log in the demo output directory
    And the process exit code reflects overall success or failure

  @technical
  Scenario: Output video passes basic quality validation
    Given a demo video has been composed
    When validation runs on the output
    Then the video has non-zero audio levels, no black frames exceeding 3 seconds, and duration matches expected scene total

  @user
  Scenario: User creates a demo by describing it conversationally
    Given the user invokes /tommymorgan:demo
    When they describe a product demo in natural language
    Then a demo script is written to the project's demos directory
    And the script contains at least one scene with narration text and browser actions

  @user
  Scenario: User previews and edits the generated script
    Given Claude has generated a demo script
    When the script is presented scene-by-scene
    Then the user can edit narration text, reorder scenes, or add/remove scenes

  @user
  Scenario: Demo is generated from a plan file without interaction
    Given a plan file with a "Demo Scenarios" section exists
    When /tommymorgan:demo is invoked with the plan file path
    Then the demo script is generated automatically without user interaction

  @user
  Scenario: User re-records a single failed or unsatisfactory scene
    Given a completed demo with one scene the user wants to redo
    When the user requests re-recording of that specific scene
    Then only that scene is re-recorded and the final video is recomposed

  @user
  Scenario: Sensitive content warning is displayed for authenticated demos
    Given a demo script targets URLs requiring authentication
    When the script is generated
    Then a warning about sensitive data in recordings is included
