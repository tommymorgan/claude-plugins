---
name: status
description: Check scenario completion status in a plan and report progress
argument-hint: "[optional: path/to/plan.md]"
allowed-tools:
  - Read
  - Glob
  - Grep
---

# Check Plan Status

Parse plan file scenarios and report completion status. Shows TODO vs DONE scenarios and overall progress.

## Workflow

### Step 1: Find Plan File

If a path is provided as argument, use it:
```
$ARGUMENTS
```

If no path provided, find the plan file:

1. Check current directory for `plans/*.md` or `docs/plans/*.md`
2. Check parent directories
3. Look for most recent plan file by date in filename (YYYY-MM-DD pattern)

If multiple plans found and ambiguous, list them and ask user to specify.

### Step 2: Read and Parse Plan

Read the plan file and extract scenarios from both sections:

**User Requirements section:**
```gherkin
<!-- TODO -->
Scenario: <description>
  Given <context>
  When <action>
  Then <outcome>

<!-- DONE -->
Scenario: <description>
  Given <context>
  When <action>
  Then <outcome>
```

**Technical Specifications section:**
Same format as User Requirements.

### Step 3: Count Scenarios

Parse the plan and count:
- Total TODO scenarios (in both sections)
- Total DONE scenarios (in both sections)
- User Requirements TODO/DONE
- Technical Specifications TODO/DONE

Extract scenario titles (the "Scenario: <title>" line).

### Step 4: Report Status

Report current progress:

```
## Plan Status: <plan filename>

**Progress**: X/Y scenarios complete (Z% done)

### User Requirements
- ✅ <DONE scenario title>
- ✅ <DONE scenario title>
- ⏳ <TODO scenario title>

### Technical Specifications
- ✅ <DONE scenario title>
- ⏳ <TODO scenario title>
- ⏳ <TODO scenario title>

**Next scenario**: <first TODO scenario title>
```

If all scenarios DONE:
```
## Plan Complete! 🎉

All Y scenarios implemented and marked DONE.

User Requirements: X/X complete
Technical Specifications: Y/Y complete

Feature ready for deployment!
```

If no TODO scenarios remain but work seems incomplete:
```
## Status Check

All scenarios marked DONE.

Consider:
- Has exploratory testing been run?
- Have all quality gates passed?
- Is documentation up to date?
- Ready to squash commits and finalize?
```

### Step 5: Show Next Steps

Based on status, suggest next action:

**If TODO scenarios exist:**
```
**Next action**: Run /tommymorgan:work to implement next scenario
```

**If all DONE but not finalized:**
```
**Next action**: Ensure quality gates passed, then squash commits
```

**If complete:**
```
**Next action**: Feature ready! Consider running /tommymorgan:test for final validation
```

## Important Notes

- Scenarios ARE the plan - no separate verification commands
- TODO/DONE comments are the source of truth
- Status command is read-only - doesn't change plan file
- Work command updates TODO → DONE as scenarios are implemented
- Use this command frequently to check progress
- Parsing looks for exact comment format: `<!-- TODO -->` or `<!-- DONE -->`
