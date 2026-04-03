export interface XmRChart {
	values: readonly number[];
	centralLine: number;
	movingRanges: number[];
	averageMovingRange: number;
	upperLimit: number;
	lowerLimit: number;
}

export type SignalRule =
	| "above_upper_limit"
	| "below_lower_limit"
	| "run_of_8"
	| "three_of_four_outer_third";

export interface Signal {
	index: number;
	value: number;
	date: string;
	rule: SignalRule;
}

/**
 * Calculate XmR (Individuals and Moving Range) chart values.
 *
 * Per Vacanti/Wheeler: control limits use 2.66 * average moving range,
 * NOT standard deviation. This works regardless of distribution shape.
 */
export function calculateXmR(values: readonly number[]): XmRChart {
	if (values.length === 0) {
		return {
			values,
			centralLine: 0,
			movingRanges: [],
			averageMovingRange: 0,
			upperLimit: 0,
			lowerLimit: 0,
		};
	}

	const centralLine = values.reduce((sum, v) => sum + v, 0) / values.length;

	const movingRanges: number[] = [];
	for (let i = 1; i < values.length; i++) {
		movingRanges.push(Math.abs(values[i] - values[i - 1]));
	}

	const averageMovingRange =
		movingRanges.length > 0
			? movingRanges.reduce((sum, v) => sum + v, 0) / movingRanges.length
			: 0;

	const upperLimit = centralLine + 2.66 * averageMovingRange;
	const lowerLimit = Math.max(0, centralLine - 2.66 * averageMovingRange);

	return {
		values,
		centralLine,
		movingRanges,
		averageMovingRange,
		upperLimit,
		lowerLimit,
	};
}

/**
 * Detect signals (exceptional variation) in XmR chart data.
 *
 * Rules implemented (standard Western Electric / Wheeler):
 * 1. Any point above the upper natural process limit
 * 2. Any point below the lower natural process limit
 * 3. Run of 8+ consecutive points on the same side of the central line
 * 4. 3 of 4 consecutive points in the outer third between central line and limit (same side)
 */
export function detectSignals(
	chart: XmRChart,
	dates: readonly string[],
): Signal[] {
	const signals: Signal[] = [];
	const { values, centralLine, upperLimit, lowerLimit } = chart;

	// Rule 1 & 2: Points outside limits
	for (let i = 0; i < values.length; i++) {
		if (values[i] > upperLimit) {
			signals.push({
				index: i,
				value: values[i],
				date: dates[i],
				rule: "above_upper_limit",
			});
		}
		if (values[i] < lowerLimit) {
			signals.push({
				index: i,
				value: values[i],
				date: dates[i],
				rule: "below_lower_limit",
			});
		}
	}

	// Rule 3: Run of 8+ on same side of central line
	let runStart = 0;
	let runSide: "above" | "below" | null = null;

	for (let i = 0; i < values.length; i++) {
		const side =
			values[i] > centralLine
				? "above"
				: values[i] < centralLine
					? "below"
					: null;

		if (side === null || side !== runSide) {
			runStart = i;
			runSide = side;
		}

		if (side !== null && i - runStart + 1 >= 8) {
			signals.push({
				index: i,
				value: values[i],
				date: dates[i],
				rule: "run_of_8",
			});
		}
	}

	// Rule 4: 3 of 4 consecutive points in outer third (same side)
	const upperThird = centralLine + ((upperLimit - centralLine) * 2) / 3;
	const lowerThird = centralLine - ((centralLine - lowerLimit) * 2) / 3;

	for (let i = 0; i <= values.length - 4; i++) {
		const window = values.slice(i, i + 4);

		// Check upper outer third
		const inUpperThird = window.filter((v) => v >= upperThird).length;
		if (inUpperThird >= 3) {
			signals.push({
				index: i + 3,
				value: values[i + 3],
				date: dates[i + 3],
				rule: "three_of_four_outer_third",
			});
		}

		// Check lower outer third
		const inLowerThird = window.filter((v) => v <= lowerThird).length;
		if (inLowerThird >= 3) {
			signals.push({
				index: i + 3,
				value: values[i + 3],
				date: dates[i + 3],
				rule: "three_of_four_outer_third",
			});
		}
	}

	return signals;
}
