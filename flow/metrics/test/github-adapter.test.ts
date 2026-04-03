import { describe, expect, it, vi } from "vitest";
import {
	fetchMergedPRs,
	type GitHubClient,
	type GitHubCommit,
	type GitHubPR,
} from "../src/adapters/github.js";

function makePR(overrides: Partial<GitHubPR> = {}): GitHubPR {
	return {
		number: 1,
		title: "Test PR",
		merged_at: "2026-01-10T15:00:00Z",
		created_at: "2026-01-05T10:00:00Z",
		user: { login: "tommy" },
		labels: [{ name: "feature" }],
		...overrides,
	};
}

function makeCommit(date: string): GitHubCommit {
	return { commit: { author: { date } } };
}

function createMockClient(
	prs: GitHubPR[][],
	commits: Map<number, GitHubCommit[]> = new Map(),
): GitHubClient {
	let callCount = 0;
	return {
		fetchMergedPRsPage: vi.fn(async () => {
			const result = prs[callCount] ?? [];
			callCount++;
			return result;
		}),
		fetchPRCommits: vi.fn(async (_repo: string, prNumber: number) => {
			return commits.get(prNumber) ?? [];
		}),
	};
}

describe("GitHub data collection", () => {
	it("should fetch merged PRs and calculate cycle time", async () => {
		const commits = new Map([
			[
				1,
				[
					makeCommit("2026-01-05T08:00:00Z"),
					makeCommit("2026-01-07T10:00:00Z"),
				],
			],
		]);
		const client = createMockClient([[makePR()], []], commits);

		const items = await fetchMergedPRs(client, "org/infilla-app");

		expect(items).toHaveLength(1);
		expect(items[0].id).toBe(1);
		expect(items[0].author).toBe("tommy");
		expect(items[0].repo).toBe("org/infilla-app");
		expect(items[0].startedAt).toBe("2026-01-05T08:00:00Z");
		expect(items[0].finishedAt).toBe("2026-01-10T15:00:00Z");
		// Jan 5 to Jan 10 = 6 days inclusive
		expect(items[0].cycleTimeDays).toBe(6);
	});

	it("should fall back to PR created_at when commits are unavailable", async () => {
		const client = createMockClient([[makePR()], []], new Map([[1, []]]));

		const items = await fetchMergedPRs(client, "org/infilla-app");

		expect(items[0].startedAt).toBe("2026-01-05T10:00:00Z");
		// created_at Jan 5 to merged_at Jan 10 = 6 days
		expect(items[0].cycleTimeDays).toBe(6);
	});

	it("should use the earliest commit authored date as start time", async () => {
		const commits = new Map([
			[
				1,
				[
					makeCommit("2026-01-07T10:00:00Z"), // Later commit
					makeCommit("2026-01-03T08:00:00Z"), // Earliest commit
					makeCommit("2026-01-06T12:00:00Z"),
				],
			],
		]);
		const client = createMockClient([[makePR()], []], commits);

		const items = await fetchMergedPRs(client, "org/infilla-app");
		expect(items[0].startedAt).toBe("2026-01-03T08:00:00Z");
	});

	it("should handle pagination by fetching until empty page", async () => {
		const page1 = [makePR({ number: 1 }), makePR({ number: 2 })];
		const page2 = [makePR({ number: 3 })];
		const page3: GitHubPR[] = [];

		const commits = new Map([
			[1, [makeCommit("2026-01-05T08:00:00Z")]],
			[2, [makeCommit("2026-01-05T08:00:00Z")]],
			[3, [makeCommit("2026-01-05T08:00:00Z")]],
		]);
		const client = createMockClient([page1, page2, page3], commits);

		const items = await fetchMergedPRs(client, "org/infilla-app");

		expect(items).toHaveLength(3);
		expect(client.fetchMergedPRsPage).toHaveBeenCalledTimes(3);
	});

	it("should support incremental fetching with a since parameter", async () => {
		const client = createMockClient(
			[[makePR()], []],
			new Map([[1, [makeCommit("2026-01-05T08:00:00Z")]]]),
		);

		await fetchMergedPRs(client, "org/infilla-app", {
			since: "2026-01-09T00:00:00Z",
		});

		expect(client.fetchMergedPRsPage).toHaveBeenCalledWith(
			"org/infilla-app",
			expect.objectContaining({ since: "2026-01-09T00:00:00Z" }),
		);
	});

	it("should extract labels from PR", async () => {
		const pr = makePR({ labels: [{ name: "bug" }, { name: "urgent" }] });
		const client = createMockClient(
			[[pr], []],
			new Map([[1, [makeCommit("2026-01-05T08:00:00Z")]]]),
		);

		const items = await fetchMergedPRs(client, "org/infilla-app");
		expect(items[0].labels).toEqual(["bug", "urgent"]);
	});
});
