/**
 * Calculate Work Item Age: elapsed calendar days from start to now (inclusive).
 *
 * Per Vacanti: Age only applies to items that have started but not finished.
 * Once an item finishes, we calculate Cycle Time instead.
 */
export function calculateWorkItemAge(
	startedAt: Date,
	now: Date = new Date(),
): number {
	const startUtcDay = Date.UTC(
		startedAt.getUTCFullYear(),
		startedAt.getUTCMonth(),
		startedAt.getUTCDate(),
	);
	const nowUtcDay = Date.UTC(
		now.getUTCFullYear(),
		now.getUTCMonth(),
		now.getUTCDate(),
	);

	const msPerDay = 86_400_000;
	return Math.floor((nowUtcDay - startUtcDay) / msPerDay) + 1;
}
