# Browser Testing Tools

This plugin uses three CLI/MCP tools for browser-based testing, each chosen for a specific purpose.

## Tools

### agent-browser (Primary)

**Purpose**: All browser automation — navigation, clicking, typing, screenshots, console checking, JavaScript evaluation.

**Why this tool**: [agent-browser](https://github.com/vercel-labs/agent-browser) is purpose-built for AI coding agents. Its ref-based interaction model (`snapshot -i` → `click @e1`) is token-efficient and avoids loading large MCP tool schemas into the agent's context. It has the broadest capability set of the CLI tools, including built-in profiling, CDP access, diff commands, semantic locators, and network mocking.

**Install**:
```bash
npm install -g @vercel-labs/agent-browser
```

**Required**: Yes — all browser testing agents depend on this tool.

---

### playwright-cli (Video Recording)

**Purpose**: Recording video demos of test sessions.

**Why this tool**: [playwright-cli](https://github.com/microsoft/playwright-cli) provides video recording (`video-start`/`video-stop`), which agent-browser does not support. This is the only capability playwright-cli is used for — all other browser automation uses agent-browser.

**Install**:
```bash
npm install -g @playwright/cli@latest
```

**Required**: Only when video recording is requested. If not installed and a demo is requested, the agent will report that video recording requires playwright-cli.

---

### chrome-devtools-mcp (Deep Performance Profiling)

**Purpose**: Lighthouse audits, performance tracing, memory snapshots, and CrUX real-user data.

**Why this tool**: [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) provides deep performance analysis capabilities that neither CLI tool offers — full Lighthouse scores, Chrome DevTools performance traces, and heap memory snapshots. It's loaded conditionally via ToolSearch only when a scenario requires performance profiling, so it adds no overhead to non-performance test runs.

**Install**:

Configure as an MCP server in your Claude Code settings. The tool is loaded on-demand when needed:
```bash
npx -y chrome-devtools-mcp@latest
```

**Required**: Only for deep performance profiling (Lighthouse, memory snapshots, performance tracing). When unavailable, agents fall back to basic Core Web Vitals measurement via `agent-browser eval`.

## Architecture

```
Browser Testing
├── agent-browser (CLI)          ← Always used for browser automation
│   ├── Navigation, clicking, typing
│   ├── Snapshots with refs (@e1, @e2)
│   ├── Console, network, screenshots
│   ├── JavaScript evaluation
│   └── Basic profiling
├── playwright-cli (CLI)         ← Only for video recording
│   ├── video-start
│   └── video-stop
└── chrome-devtools-mcp (MCP)    ← Conditional, for deep profiling
    ├── Lighthouse audits
    ├── Performance tracing
    ├── Memory snapshots
    └── CrUX real-user data
```

## Token Efficiency

The previous approach used Playwright MCP tools (browser_navigate, browser_click, etc.), which loaded large tool schemas and verbose accessibility trees into the agent's context window. CLI commands are more token-efficient because they avoid this overhead — the agent simply runs shell commands and reads their output.

## Named Sessions

When multiple browser testing agents run concurrently, each uses a named session to prevent conflicts:

```bash
agent-browser -s=exploratory-tester open "https://example.com"
agent-browser -s=browser-explorer open "https://example.com"
```

## Shell Safety

Since CLI commands run through Bash, all user-controlled values (URLs, form text, selectors) must be properly quoted to prevent shell injection:

```bash
# Correct
agent-browser -s=test open "https://example.com/path?q=search term"
agent-browser -s=test fill @e3 "user's input"

# Incorrect — risk of shell injection
agent-browser open $url
agent-browser fill @ref $text
```
