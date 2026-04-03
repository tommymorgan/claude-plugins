import { describe, expect, it } from "vitest";
import { applyFilter, checkSampleSize } from "../src/filter.js";
import type { WorkItem } from "../src/types.js";

function makeItem(overrides: Partial<WorkItem> = {}): WorkItem {
	return {
		id: 1,
		title: "Test",
		author: "tommy",
		startedAt: "2026-01-01T10:00:00Z",
		finishedAt: "2026-01-03T15:00:00Z",
		cycleTimeDays: 3,
		repo: "infilla-app",
		labels: [],
		...overrides,
	};
}

describe("Filter", () => {
	const items: WorkItem[] = [
		makeItem({ id: 1, author: "tommy", repo: "infilla-app" }),
		makeItem({ id: 2, author: "alice", repo: "infilla-app" }),
		makeItem({ id: 3, author: "tommy", repo: "atlas" }),
		makeItem({ id: 4, author: "alice", repo: "atlas" }),
	];

	it("should return all items when no filter is applied", () => {
		expect(applyFilter(items, {})).toHaveLength(4);
	});

	it("should filter by author", () => {
		const result = applyFilter(items, { author: "tommy" });
		expect(result).toHaveLength(2);
		expect(result.every((i) => i.author === "tommy")).toBe(true);
	});

	it("should filter by repo", () => {
		const result = applyFilter(items, { repo: "atlas" });
		expect(result).toHaveLength(2);
		expect(result.every((i) => i.repo === "atlas")).toBe(true);
	});

	it("should combine author and repo filters", () => {
		const result = applyFilter(items, { author: "tommy", repo: "infilla-app" });
		expect(result).toHaveLength(1);
		expect(result[0].id).toBe(1);
	});

	it("should not modify the input array", () => {
		const original = [...items];
		applyFilter(items, { author: "tommy" });
		expect(items).toEqual(original);
	});
});

describe("Sample size check", () => {
	it("should return null when sample size is sufficient", () => {
		const items = Array.from({ length: 20 }, (_, i) => makeItem({ id: i }));
		expect(checkSampleSize(items)).toBeNull();
	});

	it("should return a warning when sample size is below 20", () => {
		const items = Array.from({ length: 15 }, (_, i) => makeItem({ id: i }));
		const warning = checkSampleSize(items);
		expect(warning).toContain("15");
		expect(warning).toContain("20");
	});

	it("should return a warning for empty arrays", () => {
		expect(checkSampleSize([])).toContain("0");
	});
});
