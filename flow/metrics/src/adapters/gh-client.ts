import { execFile as nodeExecFile } from "node:child_process";
import { promisify } from "node:util";
import type {
	FetchOptions,
	GitHubClient,
	GitHubCommit,
	GitHubPR,
} from "./github.js";

const execFileAsync = promisify(nodeExecFile);

async function gh(args: string[]): Promise<string> {
	// execFile is used instead of exec to prevent shell injection.
	// All arguments are passed as an array, never interpolated into a shell string.
	const { stdout } = await execFileAsync("gh", args);
	return stdout;
}

/**
 * Check if gh CLI is installed and authenticated.
 * Returns an error message if not, or null if ready.
 */
export async function checkGhAuth(): Promise<string | null> {
	try {
		await execFileAsync("gh", ["auth", "status"]);
		return null;
	} catch {
		return "gh CLI is not installed or not authenticated. Run `gh auth login` to authenticate.";
	}
}

/**
 * GitHubClient implementation using the gh CLI.
 */
export function createGhClient(): GitHubClient {
	return {
		async fetchMergedPRsPage(
			repo: string,
			options: FetchOptions,
		): Promise<GitHubPR[]> {
			const raw = await gh([
				"api",
				`repos/${repo}/pulls?state=closed&per_page=100&page=${options.page ?? 1}&sort=updated&direction=desc`,
			]);

			const prs: Array<GitHubPR & { merged_at: string | null }> =
				JSON.parse(raw);

			return prs.filter((pr): pr is GitHubPR => {
				if (!pr.merged_at) return false;
				if (options.since && pr.merged_at < options.since) return false;
				return true;
			});
		},

		async fetchPRCommits(
			repo: string,
			prNumber: number,
		): Promise<GitHubCommit[]> {
			try {
				const raw = await gh([
					"api",
					`repos/${repo}/pulls/${prNumber}/commits?per_page=100`,
				]);
				return JSON.parse(raw);
			} catch {
				return [];
			}
		},
	};
}
