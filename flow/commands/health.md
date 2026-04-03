---
description: "Show current flow health including WIP, aging items, and throughput trends"
---

# Flow Health

Display current flow health for daily standup and process monitoring.

## Steps

1. **Resolve project config** by matching git remote URL against `~/.tommymorgan/flows/`

2. **Read flow data** from `~/.tommymorgan/flows/<slug>-data.json`

3. **Fetch live WIP** from the configured source:
   - GitHub: `gh api "repos/{owner}/{repo}/pulls?state=open&per_page=100"`
   - For each open item, calculate Work Item Age
   - Note the current timestamp

4. **Calculate the 85th percentile** of historical Cycle Time (intervention threshold)

5. **Calculate Throughput** for the last 4 weeks

6. **Display**, oldest aging item first:
   ```
   Flow Health (as of {timestamp})

   ## Current WIP: {count} open items

   | Item | Author | Age (days) | Status |
   |------|--------|-----------|--------|
   | #{id} {title} | {author} | {age} | ⚠️ AGING (exceeds {p85}d SLE) |
   | #{id} {title} | {author} | {age} | |

   ## Throughput (last 4 weeks)

   | Week of | Items completed |
   |---------|----------------|
   | {date}  | {count}        |

   ## Intervention Candidates
   {count} items exceed the 85th percentile age ({p85} days).
   ```

## Arguments

- `--author <name>` — Filter to a specific author
- `--repo <owner/repo>` — Filter to a specific repo
