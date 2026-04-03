import { calculatePercentiles } from "./percentiles.js";

export interface MonteCarloConfig {
	throughputHistory: readonly number[];
	remainingItems: number;
	trials?: number;
	seed?: number;
	startDate?: Date;
}

export interface MonteCarloResult {
	percentiles: Record<number, number>; // percentile → weeks
	dates?: Record<number, Date>; // percentile → projected date (if startDate provided)
	totalTrials: number;
}

/**
 * Simple seeded PRNG (mulberry32).
 * Produces deterministic sequences for reproducible test results.
 */
function createRng(seed: number): () => number {
	let state = seed;
	return () => {
		state |= 0;
		state = (state + 0x6d2b79f5) | 0;
		let t = Math.imul(state ^ (state >>> 15), 1 | state);
		t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
}

/**
 * Run a Monte Carlo simulation to forecast when N remaining items will be complete.
 *
 * Each trial randomly samples from historical weekly throughput data,
 * accumulating until the remaining item count is reached. The number of
 * weeks elapsed per trial is recorded. Results are aggregated into a
 * probability distribution.
 *
 * Per Vacanti (WWIBD Ch. 5): Monte Carlo simulation is the appropriate
 * technique for multi-item forecasting because the problem is too complex
 * for enumeration or analytical probability.
 */
export function runMonteCarloSimulation(
	config: MonteCarloConfig,
): MonteCarloResult {
	const {
		throughputHistory,
		remainingItems,
		trials = 10000,
		seed = Date.now(),
		startDate,
	} = config;

	if (remainingItems <= 0) {
		const zeros = { 50: 0, 70: 0, 85: 0, 95: 0 };
		return {
			percentiles: zeros,
			dates: startDate
				? { 50: startDate, 70: startDate, 85: startDate, 95: startDate }
				: undefined,
			totalTrials: trials,
		};
	}

	const rng = createRng(seed);
	const weekResults: number[] = [];

	for (let trial = 0; trial < trials; trial++) {
		let completed = 0;
		let weeks = 0;

		while (completed < remainingItems) {
			const index = Math.floor(rng() * throughputHistory.length);
			completed += throughputHistory[index];
			weeks++;
		}

		weekResults.push(weeks);
	}

	const percentiles = calculatePercentiles(weekResults, [50, 70, 85, 95]);

	let dates: Record<number, Date> | undefined;
	if (startDate) {
		dates = {};
		for (const [p, weeks] of Object.entries(percentiles)) {
			const d = new Date(startDate);
			d.setUTCDate(d.getUTCDate() + weeks * 7);
			dates[Number(p)] = d;
		}
	}

	return { percentiles, dates, totalTrials: trials };
}
