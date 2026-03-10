---
name: tommymorgan:review-plan
description: Review a plan file with the expert panel
argument-hint: "<path/to/plan.md>"
allowed-tools:
  - Skill
  - Read
  - Glob
---

# Review Plan

Review a plan file using the expert panel. This is a convenience wrapper around `/review-features`.

## Workflow

### Step 1: Find Plan File

If argument provided, use it:
```
$ARGUMENTS
```

If no argument, find the most recent plan file:
1. Search for `plans/*.md` in current project
2. Sort by date in filename (YYYY-MM-DD pattern)
3. Use most recent

### Step 2: Invoke Review Features

Pass the plan file to `/review-features`:

```
/tommymorgan:review-features <plan_file_path>
```

The expert panel will:
1. Extract Gherkin scenarios from the plan
2. Detect context from content
3. Run 13 domain experts
4. Provide prioritized recommendations

### Step 3: Display Results

The review output from `/review-features` is displayed directly.

## Notes

This command exists for backwards compatibility and discoverability.
All functionality is in `/review-features`, which also accepts:
- `.feature` files
- Directories of feature files
- Glob patterns
