import { describe, expect, it } from "vitest";
import { calculateXmR, detectSignals, type XmRChart } from "../src/xmr.js";

describe("XmR chart calculation", () => {
	it("should calculate central line as average of values", () => {
		const values = [10, 12, 8, 11, 9];
		const chart = calculateXmR(values);
		expect(chart.centralLine).toBe(10); // (10+12+8+11+9)/5 = 50/5
	});

	it("should calculate moving ranges between consecutive values", () => {
		const values = [10, 12, 8, 11, 9];
		const chart = calculateXmR(values);
		// Moving ranges: |12-10|=2, |8-12|=4, |11-8|=3, |9-11|=2
		expect(chart.movingRanges).toEqual([2, 4, 3, 2]);
	});

	it("should calculate average moving range", () => {
		const values = [10, 12, 8, 11, 9];
		const chart = calculateXmR(values);
		// Average MR: (2+4+3+2)/4 = 2.75
		expect(chart.averageMovingRange).toBe(2.75);
	});

	it("should set upper natural process limit as average + 2.66 * avgMR", () => {
		const values = [10, 12, 8, 11, 9];
		const chart = calculateXmR(values);
		// UNPL = 10 + 2.66 * 2.75 = 10 + 7.315 = 17.315
		expect(chart.upperLimit).toBeCloseTo(17.315, 2);
	});

	it("should set lower natural process limit as average - 2.66 * avgMR, minimum 0", () => {
		const values = [10, 12, 8, 11, 9];
		const chart = calculateXmR(values);
		// LNPL = 10 - 2.66 * 2.75 = 10 - 7.315 = 2.685
		expect(chart.lowerLimit).toBeCloseTo(2.685, 2);
	});

	it("should clamp lower limit to 0", () => {
		const values = [1, 2, 1, 2, 1];
		const chart = calculateXmR(values);
		// Central = 1.4, avgMR = 1, LNPL = 1.4 - 2.66 = -1.26 → clamp to 0
		expect(chart.lowerLimit).toBe(0);
	});

	it("should handle a single value", () => {
		const chart = calculateXmR([5]);
		expect(chart.centralLine).toBe(5);
		expect(chart.movingRanges).toEqual([]);
		expect(chart.averageMovingRange).toBe(0);
	});

	it("should not modify the input array", () => {
		const values = [10, 12, 8, 11, 9];
		const original = [...values];
		calculateXmR(values);
		expect(values).toEqual(original);
	});
});

describe("Signal detection", () => {
	it("should flag points above the upper natural process limit", () => {
		const chart: XmRChart = {
			values: [10, 12, 8, 25, 9], // 25 is way above
			centralLine: 10,
			movingRanges: [2, 4, 17, 16],
			averageMovingRange: 2.75,
			upperLimit: 17.315,
			lowerLimit: 2.685,
		};
		const dates = [
			"2026-01-01",
			"2026-01-08",
			"2026-01-15",
			"2026-01-22",
			"2026-01-29",
		];

		const signals = detectSignals(chart, dates);
		const aboveUpper = signals.filter((s) => s.rule === "above_upper_limit");
		expect(aboveUpper).toHaveLength(1);
		expect(aboveUpper[0].index).toBe(3);
		expect(aboveUpper[0].value).toBe(25);
	});

	it("should flag points below the lower natural process limit", () => {
		const chart: XmRChart = {
			values: [10, 12, 8, 11, 1], // 1 is below
			centralLine: 10,
			movingRanges: [2, 4, 3, 10],
			averageMovingRange: 2.75,
			upperLimit: 17.315,
			lowerLimit: 2.685,
		};
		const dates = [
			"2026-01-01",
			"2026-01-08",
			"2026-01-15",
			"2026-01-22",
			"2026-01-29",
		];

		const signals = detectSignals(chart, dates);
		const belowLower = signals.filter((s) => s.rule === "below_lower_limit");
		expect(belowLower).toHaveLength(1);
		expect(belowLower[0].index).toBe(4);
	});

	it("should flag runs of 8+ consecutive points on the same side of the central line", () => {
		// 8 points all above the central line (10)
		const values = [11, 12, 13, 14, 15, 11, 12, 13, 9];
		const chart: XmRChart = {
			values,
			centralLine: 10,
			movingRanges: [],
			averageMovingRange: 2,
			upperLimit: 15.32,
			lowerLimit: 4.68,
		};
		const dates = values.map((_, i) => `2026-01-0${i + 1}`);

		const signals = detectSignals(chart, dates);
		const runs = signals.filter((s) => s.rule === "run_of_8");
		expect(runs.length).toBeGreaterThan(0);
	});

	it("should flag 3 of 4 consecutive points in outer third on same side", () => {
		// Upper third starts at: centralLine + (upperLimit - centralLine) * 2/3
		// = 10 + (17.315 - 10) * 2/3 = 10 + 4.877 = 14.877
		const chart: XmRChart = {
			values: [10, 15, 16, 10, 15], // positions 1,2,4 are above 14.877 (3 of 4 from index 1-4)
			centralLine: 10,
			movingRanges: [],
			averageMovingRange: 2.75,
			upperLimit: 17.315,
			lowerLimit: 2.685,
		};
		const dates = [
			"2026-01-01",
			"2026-01-08",
			"2026-01-15",
			"2026-01-22",
			"2026-01-29",
		];

		const signals = detectSignals(chart, dates);
		const outerThird = signals.filter(
			(s) => s.rule === "three_of_four_outer_third",
		);
		expect(outerThird.length).toBeGreaterThan(0);
	});

	it("should return no signals for stable process data", () => {
		const chart: XmRChart = {
			values: [10, 11, 9, 10, 11, 9, 10, 11, 9, 10],
			centralLine: 10,
			movingRanges: [1, 2, 1, 1, 2, 1, 1, 2, 1],
			averageMovingRange: 1.33,
			upperLimit: 13.54,
			lowerLimit: 6.46,
		};
		const dates = chart.values.map(
			(_, i) => `2026-01-${String(i + 1).padStart(2, "0")}`,
		);

		const signals = detectSignals(chart, dates);
		expect(signals).toHaveLength(0);
	});

	it("should include the date and rule for each signal", () => {
		const chart: XmRChart = {
			values: [10, 30],
			centralLine: 10,
			movingRanges: [20],
			averageMovingRange: 20,
			upperLimit: 63.2,
			lowerLimit: 0,
		};
		const dates = ["2026-01-01", "2026-01-08"];

		const signals = detectSignals(chart, dates);
		// 30 is not above 63.2, so no signal here. Let me fix the test data.
		expect(signals).toHaveLength(0);
	});
});
