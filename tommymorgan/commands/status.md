---
name: status
description: Verify all tasks in a plan and report completion status
argument-hint: "[optional: path/to/plan.md]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# Check Plan Status

Run all verification commands in a plan file and update task statuses. Report what's complete and what's next.

## Workflow

### Step 1: Find Plan File

If a path is provided as argument, use it:
```
$ARGUMENTS
```

If no path provided, find the plan file:

1. Check current directory for `plans/*.md`
2. Check parent directories for `plans/*.md`
3. Look for most recent plan file by date in filename

If multiple plans found and ambiguous, list them and ask user to specify.

### Step 2: Read and Parse Plan

Read the plan file and extract all tasks with their verification commands.

Tasks are formatted as:
```markdown
### N. <task description>
**Verify**: `<command>`
**Status**: pending|complete|blocked
```

Extract:
- Task number
- Task description
- Verification command (the content between backticks after **Verify**:)
- Current status

### Step 3: Run Verification Sweep

For each task, run its verification command:

```bash
<verification command>
```

Capture:
- Exit code (0 = success, non-zero = failure)
- Any output (for debugging if needed)

Determine new status:
- Exit code 0 → `complete`
- Exit code non-zero → keep current status (pending or blocked)

### Step 4: Update Plan File

For each task where status changed, update the plan file.

Change:
```markdown
**Status**: pending
```

To:
```markdown
**Status**: complete
```

Use the Edit tool to make precise updates. Only change the status line, preserve everything else.

### Step 5: Report Results

After verification sweep, report:

```
## Plan Status: <plan filename>

**Progress**: X/Y tasks complete

### Completed
- [x] Task 1: <description>
- [x] Task 2: <description>

### Pending
- [ ] Task 3: <description>
- [ ] Task 4: <description>

### Blocked
- [!] Task 5: <description>
  Root cause: <reason from plan>

**Next task**: <first pending task description>
```

If all tasks complete:
```
## Plan Complete!

All Y tasks verified and complete.
The feature is ready for final review.
```

## Important Notes

- Always run ALL verification commands, even for tasks marked complete (they might have regressed)
- Never mark a task complete without running its verification command
- If a verification command fails but was previously complete, keep it as complete and warn about regression
- Blocked tasks stay blocked until manually unblocked (verification commands don't clear blocked status)
- The plan file is updated in place - changes are visible immediately
