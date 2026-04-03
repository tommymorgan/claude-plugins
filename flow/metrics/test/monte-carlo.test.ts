import { describe, expect, it } from "vitest";
import { runMonteCarloSimulation } from "../src/monte-carlo.js";

describe("Monte Carlo simulation", () => {
	// Deterministic throughput: exactly 5 items/week
	const steadyThroughput = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5];

	it("should produce a probability distribution of completion weeks", () => {
		const result = runMonteCarloSimulation({
			throughputHistory: steadyThroughput,
			remainingItems: 15,
			trials: 1000,
			seed: 42,
		});

		expect(result.percentiles[50]).toBeGreaterThan(0);
		expect(result.percentiles[85]).toBeGreaterThanOrEqual(
			result.percentiles[50],
		);
		expect(result.percentiles[95]).toBeGreaterThanOrEqual(
			result.percentiles[85],
		);
	});

	it("should complete 15 items in exactly 3 weeks with steady throughput of 5/week", () => {
		const result = runMonteCarloSimulation({
			throughputHistory: steadyThroughput,
			remainingItems: 15,
			trials: 1000,
			seed: 42,
		});

		// With constant throughput of 5, 15 items always takes 3 weeks
		expect(result.percentiles[50]).toBe(3);
		expect(result.percentiles[85]).toBe(3);
		expect(result.percentiles[95]).toBe(3);
	});

	it("should produce wider distribution with variable throughput", () => {
		const variableThroughput = [2, 8, 3, 7, 1, 9, 4, 6, 2, 8];

		const result = runMonteCarloSimulation({
			throughputHistory: variableThroughput,
			remainingItems: 20,
			trials: 10000,
			seed: 42,
		});

		// With variable throughput, the spread should be wider
		expect(result.percentiles[95]).toBeGreaterThan(result.percentiles[50]);
	});

	it("should run 10000 trials by default", () => {
		const result = runMonteCarloSimulation({
			throughputHistory: steadyThroughput,
			remainingItems: 10,
			seed: 42,
		});

		expect(result.totalTrials).toBe(10000);
	});

	it("should produce deterministic results with the same seed", () => {
		const config = {
			throughputHistory: [2, 8, 3, 7, 1, 9, 4, 6, 2, 8],
			remainingItems: 20,
			trials: 1000,
			seed: 123,
		};

		const result1 = runMonteCarloSimulation(config);
		const result2 = runMonteCarloSimulation(config);

		expect(result1.percentiles).toEqual(result2.percentiles);
	});

	it("should return 0 weeks when no items remain", () => {
		const result = runMonteCarloSimulation({
			throughputHistory: steadyThroughput,
			remainingItems: 0,
			trials: 100,
			seed: 42,
		});

		expect(result.percentiles[50]).toBe(0);
		expect(result.percentiles[95]).toBe(0);
	});

	it("should handle throughput history with zero-completion weeks", () => {
		const withZeros = [0, 5, 0, 3, 0, 4, 0, 6, 0, 2];

		const result = runMonteCarloSimulation({
			throughputHistory: withZeros,
			remainingItems: 10,
			trials: 1000,
			seed: 42,
		});

		// Should still produce results — zero-throughput weeks just mean longer timelines
		expect(result.percentiles[50]).toBeGreaterThan(0);
		expect(result.percentiles[95]).toBeGreaterThan(result.percentiles[50]);
	});

	it("should convert weeks to projected completion dates when startDate provided", () => {
		const result = runMonteCarloSimulation({
			throughputHistory: steadyThroughput,
			remainingItems: 15,
			trials: 1000,
			seed: 42,
			startDate: new Date("2026-04-01T00:00:00Z"),
		});

		// 3 weeks from Apr 1 = Apr 22
		expect(result.dates).toBeDefined();
		expect(result.dates?.[50]).toEqual(new Date("2026-04-22T00:00:00Z"));
	});
});
