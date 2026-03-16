import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

interface DependencyStatus {
  name: string;
  available: boolean;
  version?: string;
}

interface SystemDependencies {
  ffmpeg: DependencyStatus;
  agentBrowser: DependencyStatus;
  playwrightCli: DependencyStatus;
  playwrightMcp: DependencyStatus;
}

async function probeCommand(
  name: string,
  command: string,
  args: string[]
): Promise<DependencyStatus> {
  try {
    const { stdout } = await execFileAsync(command, args, { timeout: 5000 });
    const version = stdout.trim().split("\n")[0];
    return { name, available: true, version };
  } catch {
    return { name, available: false };
  }
}

export async function checkSystemDependencies(): Promise<SystemDependencies> {
  const [ffmpeg, agentBrowser, playwrightCli, playwrightMcp] =
    await Promise.all([
      probeCommand("ffmpeg", "ffmpeg", ["-version"]),
      probeCommand("agent-browser", "agent-browser", ["--version"]),
      probeCommand("playwright", "npx", ["playwright", "--version"]),
      probeCommand("playwright-mcp", "npx", [
        "@anthropic-ai/mcp-playwright",
        "--version",
      ]),
    ]);

  return { ffmpeg, agentBrowser, playwrightCli, playwrightMcp };
}
