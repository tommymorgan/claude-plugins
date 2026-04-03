import { calculateCycleTime } from "../cycle-time.js";
import type { WorkItem } from "../types.js";

export interface GitHubPR {
	number: number;
	title: string;
	merged_at: string;
	created_at: string;
	user: { login: string };
	labels: { name: string }[];
}

export interface GitHubCommit {
	commit: { author: { date: string } };
}

export interface FetchOptions {
	page?: number;
	since?: string;
}

export interface GitHubClient {
	fetchMergedPRsPage(repo: string, options: FetchOptions): Promise<GitHubPR[]>;
	fetchPRCommits(repo: string, prNumber: number): Promise<GitHubCommit[]>;
}

/**
 * Fetch all merged PRs from a GitHub repo and convert to WorkItems.
 *
 * Handles pagination transparently. Supports incremental fetching
 * via the `since` option (only PRs merged after this date).
 *
 * Start time: earliest commit authored date on the PR branch.
 * Falls back to PR created_at when commit data is unavailable.
 */
export async function fetchMergedPRs(
	client: GitHubClient,
	repo: string,
	options: { since?: string } = {},
): Promise<WorkItem[]> {
	const allPRs: GitHubPR[] = [];
	let page = 1;

	while (true) {
		const prs = await client.fetchMergedPRsPage(repo, {
			page,
			since: options.since,
		});
		if (prs.length === 0) break;
		allPRs.push(...prs);
		page++;
	}

	const items: WorkItem[] = [];

	for (const pr of allPRs) {
		const commits = await client.fetchPRCommits(repo, pr.number);
		const startedAt = getEarliestCommitDate(commits) ?? pr.created_at;

		const cycleTimeDays = calculateCycleTime(
			new Date(startedAt),
			new Date(pr.merged_at),
		);

		items.push({
			id: pr.number,
			title: pr.title,
			author: pr.user.login,
			startedAt,
			finishedAt: pr.merged_at,
			cycleTimeDays,
			repo,
			labels: pr.labels.map((l) => l.name),
		});
	}

	return items;
}

function getEarliestCommitDate(commits: GitHubCommit[]): string | undefined {
	if (commits.length === 0) return undefined;

	let earliest = commits[0].commit.author.date;
	for (const c of commits) {
		if (c.commit.author.date < earliest) {
			earliest = c.commit.author.date;
		}
	}
	return earliest;
}
