import { describe, expect, it } from "vitest";
import { calculateThroughput } from "../src/throughput.js";

describe("Throughput calculation", () => {
	it("should count items completed per week", () => {
		const items = [
			{ finishedAt: new Date("2026-01-05T10:00:00Z") }, // Week of Jan 5
			{ finishedAt: new Date("2026-01-06T10:00:00Z") }, // Week of Jan 5
			{ finishedAt: new Date("2026-01-12T10:00:00Z") }, // Week of Jan 12
		];
		const result = calculateThroughput(items);

		expect(result.length).toBe(2);
		expect(result[0].count).toBe(2);
		expect(result[1].count).toBe(1);
	});

	it("should include periods with zero completions", () => {
		const items = [
			{ finishedAt: new Date("2026-01-05T10:00:00Z") }, // Week 1
			// Week 2 has no items
			{ finishedAt: new Date("2026-01-19T10:00:00Z") }, // Week 3
		];
		const result = calculateThroughput(items);

		expect(result.length).toBe(3);
		expect(result[0].count).toBe(1);
		expect(result[1].count).toBe(0);
		expect(result[2].count).toBe(1);
	});

	it("should return an empty array for no items", () => {
		expect(calculateThroughput([])).toEqual([]);
	});

	it("should not modify the input array", () => {
		const items = [
			{ finishedAt: new Date("2026-01-12T10:00:00Z") },
			{ finishedAt: new Date("2026-01-05T10:00:00Z") },
		];
		const original = items.map((i) => ({ finishedAt: new Date(i.finishedAt) }));
		calculateThroughput(items);
		expect(items.map((i) => i.finishedAt.toISOString())).toEqual(
			original.map((i) => i.finishedAt.toISOString()),
		);
	});

	it("should return period start dates aligned to Monday", () => {
		const items = [
			{ finishedAt: new Date("2026-01-07T10:00:00Z") }, // Wednesday
		];
		const result = calculateThroughput(items);

		// Week start should be Monday Jan 5
		expect(result[0].periodStart.getUTCDay()).toBe(1); // Monday
	});
});
