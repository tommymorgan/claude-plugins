import { afterEach, describe, expect, it, vi } from "vitest";
import { calculateWorkItemAge } from "../src/work-item-age.js";

describe("Work Item Age calculation", () => {
	afterEach(() => {
		vi.useRealTimers();
	});

	it("should return 1 when item started today", () => {
		vi.useFakeTimers();
		vi.setSystemTime(new Date("2026-01-05T15:00:00Z"));

		const age = calculateWorkItemAge(new Date("2026-01-05T08:00:00Z"));
		expect(age).toBe(1);
	});

	it("should count calendar days inclusive of start day", () => {
		vi.useFakeTimers();
		vi.setSystemTime(new Date("2026-01-10T15:00:00Z"));

		// Started Jan 5, today is Jan 10 = 6 days
		const age = calculateWorkItemAge(new Date("2026-01-05T08:00:00Z"));
		expect(age).toBe(6);
	});

	it("should use UTC for date calculations", () => {
		vi.useFakeTimers();
		vi.setSystemTime(new Date("2026-01-06T01:00:00Z"));

		// Started late Jan 5 UTC, now early Jan 6 UTC = 2 days
		const age = calculateWorkItemAge(new Date("2026-01-05T23:00:00Z"));
		expect(age).toBe(2);
	});
});
