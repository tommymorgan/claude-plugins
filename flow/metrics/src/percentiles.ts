/**
 * Calculate a single percentile value from an array of numbers using rank-based ordering.
 *
 * No assumptions about distribution shape. Works with skewed cycle time data.
 */
export function calculatePercentile(
	values: readonly number[],
	percentile: number,
): number {
	if (values.length === 0) return 0;

	const sorted = [...values].sort((a, b) => a - b);

	const rank = (percentile / 100) * sorted.length;
	const index = Math.min(Math.ceil(rank) - 1, sorted.length - 1);

	return sorted[Math.max(0, index)];
}

/**
 * Calculate multiple percentiles at once, returning a map of percentile → value.
 */
export function calculatePercentiles(
	values: readonly number[],
	percentileList: readonly number[],
): Record<number, number> {
	const result: Record<number, number> = {};
	for (const p of percentileList) {
		result[p] = calculatePercentile(values, p);
	}
	return result;
}
