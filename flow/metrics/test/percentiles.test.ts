import { describe, expect, it } from "vitest";
import {
	calculatePercentile,
	calculatePercentiles,
} from "../src/percentiles.js";

describe("Percentile calculation", () => {
	it("should return the value at the 50th percentile", () => {
		const values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
		expect(calculatePercentile(values, 50)).toBe(5);
	});

	it("should return the value at the 85th percentile", () => {
		const values = [
			1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
		];
		expect(calculatePercentile(values, 85)).toBe(17);
	});

	it("should return the value at the 95th percentile", () => {
		const values = [
			1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
		];
		expect(calculatePercentile(values, 95)).toBe(19);
	});

	it("should use rank-based ordering, not assume normal distribution", () => {
		// Heavily skewed data — typical of cycle time distributions
		const values = [1, 1, 2, 2, 3, 3, 4, 5, 10, 50];
		const p50 = calculatePercentile(values, 50);
		const p85 = calculatePercentile(values, 85);
		const p95 = calculatePercentile(values, 95);

		// Rank-based: 50th should be around 3, not the mean (8.1)
		expect(p50).toBeLessThanOrEqual(3);
		expect(p85).toBeGreaterThanOrEqual(5);
		expect(p95).toBeGreaterThanOrEqual(10);
	});

	it("should not modify the input array", () => {
		const values = [5, 3, 1, 4, 2];
		const original = [...values];
		calculatePercentile(values, 50);
		expect(values).toEqual(original);
	});

	it("should calculate multiple percentiles at once", () => {
		const values = [
			1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
		];
		const result = calculatePercentiles(values, [50, 70, 85, 95]);

		expect(result).toEqual({
			50: 10,
			70: 14,
			85: 17,
			95: 19,
		});
	});

	it("should handle a single-element array", () => {
		expect(calculatePercentile([42], 50)).toBe(42);
		expect(calculatePercentile([42], 85)).toBe(42);
	});

	it("should handle an empty array by returning 0", () => {
		expect(calculatePercentile([], 50)).toBe(0);
	});
});
