import type { FlowFilter, WorkItem } from "./types.js";

const MIN_SAMPLE_SIZE = 20;

export function applyFilter(
	items: readonly WorkItem[],
	filter: FlowFilter,
): WorkItem[] {
	return items.filter((item) => {
		if (filter.author && item.author !== filter.author) return false;
		if (filter.repo && item.repo !== filter.repo) return false;
		return true;
	});
}

/**
 * Check if the sample size is sufficient for meaningful analysis.
 * Returns a warning message if below threshold, null if sufficient.
 */
export function checkSampleSize(items: readonly unknown[]): string | null {
	if (items.length >= MIN_SAMPLE_SIZE) return null;
	return `Warning: Only ${items.length} data points available (minimum ${MIN_SAMPLE_SIZE} recommended for reliable percentiles).`;
}
