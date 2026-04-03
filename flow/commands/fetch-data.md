---
description: "Fetch work item data from the configured source and update local flow metrics"
---

# Flow Fetch Data

Collect flow data from the configured source for the current project.

## Steps

1. **Detect git remote** and resolve project config:
   ```bash
   git remote get-url origin
   ```
   Look up config in `~/.tommymorgan/flows/` by matching the remote URL.
   If no config found, report: "No flow configuration found for remote URL: <url>. Run /flow:setup to configure." and stop.
   If config file is invalid JSON, report: "Configuration file is invalid: <path>. Run /flow:setup to reconfigure." and stop.

2. **Check authentication** for the configured source:
   - GitHub: `gh auth status`
   - If not authenticated, report the error with remediation steps and stop.

3. **Read existing flow data** (if any) from `~/.tommymorgan/flows/<slug>-data.json`

4. **Determine the `since` date**:
   - If existing data exists, use the most recent `finishedAt` timestamp
   - If `--all` flag provided, ignore existing data and fetch everything
   - If no existing data, fetch all

5. **Fetch work items** using the configured adapter:
   - **GitHub**: For each configured repo, fetch merged PRs via `gh api`:
     - Get PR list with pagination
     - For each merged PR, fetch commits to get the earliest commit authored date
     - If configured start boundary data is unavailable, fall back to PR `created_at` and include a warning
     - Calculate Cycle Time: finished - started + 1 (calendar days, UTC)
   - **Linear / Git**: Not yet implemented — report "Adapter not yet available" and stop

6. **Merge new items** with existing data (deduplicate by id + source)

7. **Write updated data** to `~/.tommymorgan/flows/<slug>-data.json` atomically

8. **Report results**:
   ```
   Flow data updated.
   - Total items: {count}
   - New items fetched: {new_count}
   - Date range: {earliest_date} to {latest_date}
   - Source: {source} ({repos})
   {warnings if any fallbacks occurred}
   ```

## Arguments

- `--all` — Re-fetch all data (ignore incremental)
- `--repo owner/repo` — Override configured repo(s)
