---
description: "Display Service Level Expectations based on historical Cycle Time percentiles"
---

# Flow SLE (Service Level Expectations)

Show Cycle Time percentile lines from historical flow data.

## Steps

1. **Resolve project config** by matching git remote URL against `~/.tommymorgan/flows/`
   - If no config: "No flow configuration found for remote URL: <url>. Run /flow:setup to configure."
   - If invalid config: "Configuration file is invalid: <path>. Run /flow:setup to reconfigure."

2. **Read flow data** from `~/.tommymorgan/flows/<slug>-data.json`
   - If no data: "No flow data found. Run /flow:fetch-data first."

3. **Apply filters** if provided (--author, --repo)

4. **Check sample size**:
   - If fewer than 20 data points: "Warning: Only {count} data points available (minimum 20 recommended for reliable percentiles). Results may not be representative."
   - Display results regardless (don't block)

5. **Calculate percentiles** at 50th, 70th, 85th, and 95th using rank-based ordering

6. **Display**:
   ```
   Service Level Expectations ({count} items, {date_range})
   {filter_description if filtered}

   50th percentile:  {n} days — 50% of items finish in {n} days or less
   70th percentile:  {n} days — 70% of items finish in {n} days or less
   85th percentile:  {n} days — 85% of items finish in {n} days or less
   95th percentile:  {n} days — 95% of items finish in {n} days or less
   ```

## Arguments

- `--author <name>` — Filter to a specific author
- `--repo <owner/repo>` — Filter to a specific repo

## Important

- These are calendar days (no weekends subtracted)
- Percentiles are forecasts: "85th percentile = 12 days" means "there is an 85% chance the next item will finish in 12 days or less"
- Never communicate these as averages
