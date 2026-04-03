---
description: "Probabilistic delivery forecast — single items (percentiles) or multiple items (Monte Carlo simulation)"
---

# Flow Forecast

Answer "when will it be done?" probabilistically.

## Steps

1. **Resolve project config** and **read flow data**

2. **Apply filters** if provided

3. **Check sample size**: warn if fewer than 20 data points

4. **Determine forecast type** from arguments:

### Single Item Forecast (default)

- Calculate percentiles at 50th, 70th, 85th, 95th from historical Cycle Time
- Display:
  ```
  Single Item Forecast ({count} historical items)
  {filter_description if filtered}

  Based on historical data, the next work item has:
  - 50% chance of finishing within {n} days
  - 70% chance of finishing within {n} days
  - 85% chance of finishing within {n} days
  - 95% chance of finishing within {n} days

  Reforecast after significant process changes or every 2 weeks.
  ```

### Multiple Item Forecast (`--items N`)

- Calculate weekly Throughput from historical data
- Warn if fewer than 10 throughput periods available
- Run Monte Carlo simulation (10,000 trials)
- Convert weeks to projected dates from today
- Display:
  ```
  Multiple Item Forecast: {N} remaining items
  ({count} historical items, {weeks} weeks of throughput data)
  {filter_description if filtered}

  Probability of completing all {N} items:
  - 50% chance by {date} ({weeks} weeks)
  - 70% chance by {date} ({weeks} weeks)
  - 85% chance by {date} ({weeks} weeks)
  - 95% chance by {date} ({weeks} weeks)

  Reforecast when: items added/removed, throughput changes,
  or weekly as work progresses.
  ```

## Arguments

- `--items N` — Forecast for N remaining items (Monte Carlo)
- `--author <name>` — Use only this author's historical data
- `--repo <owner/repo>` — Use only this repo's historical data

## Important

- Forecasts include a RANGE and PROBABILITY — never a single date
- Each forecast states when it should be regenerated
- Never divide remaining items by average throughput (Flaw of Averages)
