export interface ThroughputPeriod {
	periodStart: Date;
	count: number;
}

function getMondayOfWeek(date: Date): Date {
	const d = new Date(
		Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()),
	);
	const day = d.getUTCDay();
	// Sunday = 0, Monday = 1, ..., Saturday = 6
	const diff = day === 0 ? 6 : day - 1;
	d.setUTCDate(d.getUTCDate() - diff);
	return d;
}

/**
 * Calculate Throughput: count of completed items per week.
 *
 * Weeks start on Monday. Periods with zero completions are included
 * to give an accurate picture of delivery pace.
 */
export function calculateThroughput(
	items: readonly { finishedAt: Date }[],
): ThroughputPeriod[] {
	if (items.length === 0) return [];

	const sorted = [...items].sort(
		(a, b) => a.finishedAt.getTime() - b.finishedAt.getTime(),
	);

	const firstMonday = getMondayOfWeek(sorted[0].finishedAt);
	const lastMonday = getMondayOfWeek(sorted[sorted.length - 1].finishedAt);

	const weekCounts = new Map<string, number>();

	// Initialize all weeks between first and last (inclusive) with 0
	const msPerWeek = 7 * 86_400_000;
	let current = new Date(firstMonday);
	while (current.getTime() <= lastMonday.getTime()) {
		weekCounts.set(current.toISOString(), 0);
		current = new Date(current.getTime() + msPerWeek);
	}

	// Count items per week
	for (const item of sorted) {
		const monday = getMondayOfWeek(item.finishedAt);
		const key = monday.toISOString();
		weekCounts.set(key, (weekCounts.get(key) ?? 0) + 1);
	}

	// Convert to sorted array
	return [...weekCounts.entries()]
		.sort(([a], [b]) => a.localeCompare(b))
		.map(([key, count]) => ({
			periodStart: new Date(key),
			count,
		}));
}
