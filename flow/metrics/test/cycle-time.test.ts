import { describe, expect, it } from "vitest";
import { calculateCycleTime } from "../src/cycle-time.js";

describe("Cycle Time calculation", () => {
	it("should count calendar days inclusive of start and end", () => {
		// Started Jan 1, finished Jan 3 = 3 days
		const result = calculateCycleTime(
			new Date("2026-01-01T10:00:00Z"),
			new Date("2026-01-03T15:00:00Z"),
		);
		expect(result).toBe(3);
	});

	it("should return 1 when started and finished on the same day", () => {
		const result = calculateCycleTime(
			new Date("2026-01-01T08:00:00Z"),
			new Date("2026-01-01T17:00:00Z"),
		);
		expect(result).toBe(1);
	});

	it("should not subtract weekends", () => {
		// Friday Jan 2 to Monday Jan 5 = 4 calendar days (includes Sat+Sun)
		const result = calculateCycleTime(
			new Date("2026-01-02T10:00:00Z"),
			new Date("2026-01-05T10:00:00Z"),
		);
		expect(result).toBe(4);
	});

	it("should normalize to UTC before calculating", () => {
		// These timestamps are the same UTC day despite different timezone offsets
		const result = calculateCycleTime(
			new Date("2026-01-01T23:00:00Z"), // Late Jan 1 UTC
			new Date("2026-01-03T01:00:00Z"), // Early Jan 3 UTC
		);
		expect(result).toBe(3);
	});

	it("should handle month boundaries", () => {
		// Jan 30 to Feb 2 = 4 days
		const result = calculateCycleTime(
			new Date("2026-01-30T10:00:00Z"),
			new Date("2026-02-02T10:00:00Z"),
		);
		expect(result).toBe(4);
	});

	it("should handle leap year boundaries", () => {
		// Feb 28 to Mar 1 in a non-leap year (2026) = 2 days
		const result = calculateCycleTime(
			new Date("2026-02-28T10:00:00Z"),
			new Date("2026-03-01T10:00:00Z"),
		);
		expect(result).toBe(2);
	});
});
