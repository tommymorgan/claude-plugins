Feature: Browser Testing CLI Tools

  @user
  Scenario: Browser testing agents use CLI tools instead of MCP for browser automation
    Given a browser testing agent is launched to test a web application
    When the agent performs browser automation (navigation, clicking, typing, screenshots)
    Then all browser interactions happen through CLI commands
    And no MCP tool schemas are loaded into the agent's context
    And the agent's token usage for browser operations is reduced

  <!-- DONE -->

  @user
  Scenario: Agent reports clear error when a required CLI tool is not installed
    Given a browser testing agent is launched
    And a required CLI tool is not installed on the system
    When the agent attempts to start browser testing
    Then it reports which tool is missing
    And it references the README for installation instructions
    And it does not attempt to fall back to MCP tools

  <!-- DONE -->

  @user
  Scenario: Agent records video demos when requested
    Given a browser testing agent is testing a web application
    When the user requests a demo recording of the test session
    Then the agent records a video of the browser interactions
    And the video file is saved to the current working directory
    And the test report references the video file

  <!-- DONE -->

  @user
  Scenario: Agent refuses demo recording when playwright-cli is unavailable
    Given a browser testing agent is testing a web application
    And playwright-cli is not installed
    When the user requests a demo recording
    Then the agent tells the user it cannot record demos without playwright-cli
    And it references the README for installation instructions
    And it does not silently substitute traces or screenshots

  <!-- DONE -->

  @user
  Scenario: Agent performs deep performance profiling when scenarios require it
    Given a browser testing agent encounters a scenario mentioning performance analysis
    When the agent needs Lighthouse audits, memory snapshots, or performance tracing
    Then it loads performance profiling tools on demand
    And it provides actionable performance insights
    And the profiling tools are not loaded for non-performance scenarios

  <!-- DONE -->

  @user
  Scenario: Agent falls back to basic performance measurement when deep profiling is unavailable
    Given a browser testing agent encounters a performance scenario
    And chrome-devtools-mcp is not configured
    When the agent performs performance analysis
    Then it uses JavaScript-based Core Web Vitals measurement as fallback
    And it notes in the report that deep profiling was unavailable
    And the test still produces useful performance data

  <!-- DONE -->

  @user
  Scenario: Agent cleans up browser sessions after testing completes
    Given a browser testing agent has completed its test run
    When the agent finishes reporting results
    Then it closes all browser sessions it opened
    And the agent-browser daemon is stopped if no other sessions are active
    And no orphaned browser processes remain
    And cleanup happens even if tests encountered errors

  <!-- DONE -->

  @user
  Scenario: Existing test command continues working without changes
    Given a user runs the /tommymorgan:test command
    When the command dispatches browser testing agents
    Then the agents use CLI tools for browser automation
    And the command interface and output format remain unchanged
    And no user workflow changes are required

  <!-- DONE -->

  @technical
  Scenario: Exploratory tester agent frontmatter lists only Bash, Read, Glob, Grep as tools
    Given the exploratory-tester.md agent definition
    When the frontmatter tools list is read
    Then it contains Bash, Read, Glob, and Grep
    And it does not contain any mcp__playwright__ prefixed tools
    And it does not contain any mcp__plugin_compound-engineering_pw__ prefixed tools

  <!-- DONE -->

  @technical
  Scenario: Browser explorer agent frontmatter lists only Bash, Read, Glob, Grep as tools
    Given the browser-explorer.md agent definition
    When the frontmatter tools list is read
    Then it contains Bash, Read, Glob, and Grep
    And it does not contain any MCP tool references

  <!-- DONE -->

  @technical
  Scenario: Agent instructions use agent-browser CLI commands for primary browser automation
    Given any browser testing agent definition
    When the agent instructions reference browser interactions
    Then navigation uses "agent-browser open" or "agent-browser goto"
    And element discovery uses "agent-browser snapshot -i"
    And clicking uses "agent-browser click @ref"
    And typing uses "agent-browser fill @ref" or "agent-browser type"
    And screenshots use "agent-browser screenshot"
    And console checking uses "agent-browser console"
    And JavaScript evaluation uses "agent-browser eval"
    And agents use named sessions ("agent-browser -s=<agent-name>") to prevent conflicts

  <!-- DONE -->

  @technical
  Scenario: Agent instructions use playwright-cli for video recording
    Given a browser testing agent definition with demo recording capability
    When the instructions describe video recording
    Then video start uses "playwright-cli video-start"
    And video stop uses "playwright-cli video-stop"
    And video recording is only invoked when explicitly requested

  <!-- DONE -->

  @technical
  Scenario: Agent instructions use ToolSearch for conditional chrome-devtools-mcp loading
    Given a browser testing agent encounters performance profiling keywords
    When the agent needs deep performance analysis
    Then it calls ToolSearch to discover chrome-devtools-mcp tools
    And it uses performance_start_trace and performance_stop_trace for tracing
    And it uses lighthouse_audit for Lighthouse analysis
    And it uses take_memory_snapshot for memory profiling
    And chrome-devtools-mcp tools are never loaded for non-performance scenarios

  <!-- DONE -->

  @technical
  Scenario: Agent instructions emphasize shell argument safety
    Given any browser testing agent definition that runs CLI commands via Bash
    When the instructions describe command construction
    Then all user-controlled values (URLs, form text, selectors) are properly quoted
    And the browser-testing-patterns skill includes a Shell Safety section
    And the Shell Safety section shows correct quoting patterns for agent-browser commands

  <!-- DONE -->

  @technical
  Scenario: Browser testing patterns skill references CLI commands instead of MCP tools
    Given the browser-testing-patterns SKILL.md
    When the skill describes browser interaction patterns
    Then all examples use agent-browser CLI commands
    And no MCP tool names appear in the skill
    And the ref system (@e1, @e2) is explained for element interaction
    And re-snapshotting after DOM changes is emphasized

  <!-- DONE -->

  @technical
  Scenario: Playwright MCP tools reference is replaced with agent-browser CLI reference
    Given the references/ directory in browser-testing-patterns
    When the reference files are examined
    Then playwright-mcp-tools.md no longer exists
    And agent-browser-cli.md exists with CLI command documentation
    And the reference covers navigation, interaction, inspection, and session management

  <!-- DONE -->

  @technical
  Scenario: Performance metrics reference documents two-tier profiling approach
    Given the references/performance-metrics.md file
    When the performance analysis section is read
    Then it describes basic profiling via agent-browser eval for Core Web Vitals
    And it describes deep profiling via chrome-devtools-mcp for Lighthouse and memory
    And it explains when to use each tier
    And it documents the ToolSearch pattern for conditional loading

  <!-- DONE -->

  @technical
  Scenario: Pre-flight check validates CLI tool availability
    Given a browser testing agent starts a test session
    When the agent performs pre-flight checks
    Then it runs "which agent-browser" to verify installation
    And it runs "which playwright-cli" only when video recording is requested
    And missing tools produce clear error messages referencing the README

  <!-- DONE -->

  @technical
  Scenario: README documents tooling choices, installation, and project links
    Given the testing/ directory in the plugin
    When a developer reads the README.md
    Then it explains why agent-browser was chosen for primary automation
    And it explains why playwright-cli is used for video recording
    And it explains why chrome-devtools-mcp is used for performance profiling
    And it provides installation commands for each tool
    And it links to each project's GitHub repository

  <!-- DONE -->

  @technical
  Scenario: No MCP tool references remain in any testing file
    Given the testing/ directory in the plugin
    When all files are searched for MCP tool patterns
    Then no file contains "mcp__playwright__" references
    And no file contains "mcp__plugin_compound-engineering_pw__" references
    And the only MCP reference is the conditional chrome-devtools-mcp pattern via ToolSearch

  <!-- DONE -->
