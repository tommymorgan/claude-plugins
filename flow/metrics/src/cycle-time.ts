/**
 * Calculate Cycle Time in calendar days (inclusive of start and end day).
 *
 * Per Vacanti: Cycle Time = End Date - Start Date + 1 in calendar days.
 * No weekends or holidays are subtracted. Dates are normalized to UTC.
 */
export function calculateCycleTime(started: Date, finished: Date): number {
	const startUtcDay = Date.UTC(
		started.getUTCFullYear(),
		started.getUTCMonth(),
		started.getUTCDate(),
	);
	const endUtcDay = Date.UTC(
		finished.getUTCFullYear(),
		finished.getUTCMonth(),
		finished.getUTCDate(),
	);

	const msPerDay = 86_400_000;
	return Math.floor((endUtcDay - startUtcDay) / msPerDay) + 1;
}
