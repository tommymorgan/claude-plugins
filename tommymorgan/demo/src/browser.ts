import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

export interface BrowserTool {
  name: "agent-browser" | "playwright" | "playwright-mcp";
  command: string;
  args: string[];
  cleanup: () => Promise<void>;
}

interface ToolCandidate {
  name: BrowserTool["name"];
  command: string;
  checkArgs: string[];
}

const TOOL_CANDIDATES: ToolCandidate[] = [
  {
    name: "agent-browser",
    command: "agent-browser",
    checkArgs: ["--version"],
  },
  {
    name: "playwright",
    command: "npx",
    checkArgs: ["playwright", "--version"],
  },
  {
    name: "playwright-mcp",
    command: "npx",
    checkArgs: ["@anthropic-ai/mcp-playwright", "--version"],
  },
];

async function isAvailable(candidate: ToolCandidate): Promise<boolean> {
  try {
    await execFileAsync(candidate.command, candidate.checkArgs, {
      timeout: 10000,
    });
    return true;
  } catch {
    return false;
  }
}

export async function detectBrowserTool(): Promise<BrowserTool | null> {
  for (const candidate of TOOL_CANDIDATES) {
    if (await isAvailable(candidate)) {
      return {
        name: candidate.name,
        command: candidate.command,
        args: candidate.checkArgs.slice(0, -1),
        cleanup: createCleanupFn(candidate.name),
      };
    }
  }

  return null;
}

function createCleanupFn(
  toolName: BrowserTool["name"]
): () => Promise<void> {
  return async () => {
    switch (toolName) {
      case "agent-browser":
        try {
          await execFileAsync("agent-browser", ["close-all"], {
            timeout: 5000,
          });
        } catch {
          // Best effort — browser may already be closed
        }
        break;
      case "playwright":
      case "playwright-mcp":
        // Playwright cleans up automatically when the process exits
        break;
    }
  };
}

export function formatMissingToolsMessage(): string {
  const lines = [
    "No browser automation tool is available.",
    "",
    "The following tools were checked:",
    "",
    "  1. agent-browser — install with: npm install -g @anthropic-ai/agent-browser",
    "  2. playwright — install with: npx playwright install",
    "  3. playwright-mcp — install with: npm install -g @anthropic-ai/mcp-playwright",
    "",
    "Install at least one of these tools and try again.",
  ];

  return lines.join("\n");
}
