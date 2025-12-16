---
name: work
description: Execute plan autonomously using TDD until complete or blocked
argument-hint: "[optional: path/to/plan.md]"
allowed-tools:
  - Task
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - TodoWrite
---

# Execute Plan Autonomously

Work through all pending tasks in a plan using TDD, with code review before each commit. Continue autonomously until the plan is complete or a task is blocked.

## Workflow

### Step 1: Verification Sweep

First, verify current state by running all verification commands (like /tommymorgan:status).

This establishes ground truth:
- Which tasks are actually complete
- Which tasks are pending
- Which tasks are blocked

Update the plan file with accurate statuses before proceeding.

### Step 2: Check for Work

After verification sweep:

If all tasks complete:
```
Plan complete! All tasks verified.
```
Stop here.

If tasks are blocked with no pending tasks:
```
Plan blocked. No pending tasks available.
Blocked tasks:
- Task N: <description>
  Root cause: <reason>

Human intervention required.
```
Stop here.

If pending tasks exist, continue to Step 3.

### Step 3: Select Next Task

Pick the first pending task (by task number).

Read:
- Task description
- Verification command
- Related Gherkin scenarios from Requirements section

Use TodoWrite to track progress through the task.

### Step 4: TDD Cycle - Red Phase

Write a failing test based on:
- The task description
- Related Gherkin scenarios
- The verification command path (tells you where the test should go)

The test should:
- Describe behavior, not implementation
- Have a meaningful title
- Be runnable with the verification command

Run the verification command to confirm the test fails:
```bash
<verification command>
```

If it passes already (unexpected), investigate - the task might already be done.

### Step 5: TDD Cycle - Green Phase

Implement the minimum code to make the test pass.

Follow the Gherkin scenarios as specifications:
- Given → Set up preconditions
- When → Perform action
- Then → Verify outcomes

Run the verification command repeatedly until it passes:
```bash
<verification command>
```

If stuck after reasonable attempts (3-5 tries with different approaches):
- Do NOT guess at fixes
- Invoke root-cause-analysis (Step 7)

### Step 6: Code Review

Before committing, get code review from a subagent.

Use the Task tool to launch code-reviewer:

```typescript
Task({
  subagent_type: "pr-review-toolkit:code-reviewer",
  description: "Review implementation for task: <task description>",
  prompt: `Review the changes for this task:

Task: <task description>
Gherkin scenarios: <relevant scenarios>

Focus on:
- Does implementation satisfy the Gherkin scenarios?
- Code quality and best practices
- Security considerations
- Test quality

Changed files: <list changed files>

Provide specific feedback. Respond with APPROVED or NEEDS_CHANGES with details.`
})
```

**If NEEDS_CHANGES**:
1. Address the feedback
2. Run verification command to ensure tests still pass
3. Request another review
4. Loop until APPROVED (max 3 iterations)

**If still not approved after 3 iterations**:
- Investigate with root-cause-analysis
- If fundamental issue, mark task blocked

### Step 7: Handle Failures - Root Cause Analysis

When tests won't pass or code review loops:

**NEVER** guess at the cause or try random fixes.

**ALWAYS** invoke root-cause-analysis:

```typescript
Task({
  subagent_type: "root-cause-analysis:root-cause-analyzer",
  description: "Analyze failure for task: <task description>",
  prompt: `Systematic root cause analysis for:

Error/Issue: <what's failing>
Context: <task description and what was attempted>

Use five-whys methodology.
Identify actual root cause, not symptoms.
Provide evidence-based analysis.`
})
```

Based on root cause:
- If fixable: Apply fix, retry from Step 5
- If blocked (e.g., requires external change): Mark task blocked with root cause

### Step 8: Commit

After code review approves:

1. Stage changes:
```bash
git add -A
```

2. Create conventional commit:
```bash
git commit -m "<type>(<scope>): <description>

<body explaining what and why>

Task: <task number> - <task description>"
```

Commit type based on task:
- `feat` - New functionality
- `fix` - Bug fix
- `refactor` - Code improvement
- `test` - Test-only changes
- `docs` - Documentation

### Step 9: Update Plan Status

After successful commit, update the plan file:

Change task status from `pending` to `complete`:
```markdown
**Status**: complete
```

### Step 10: Continue to Next Task

Go back to Step 3 and pick the next pending task.

Continue until:
- All tasks complete → Report success
- Task blocked → Report blocked status with root cause
- No more pending tasks → Report completion

### Final Report

When finished (complete or blocked):

```
## Work Session Complete

**Plan**: <plan filename>
**Progress**: X/Y tasks complete
**Commits**: N commits made

### Completed This Session
- Task 1: <description> (commit abc123)
- Task 2: <description> (commit def456)

### Status
<"All tasks complete!" or "Blocked on task N: <root cause>">
```

## Important Notes

- Never skip the verification sweep at the start
- Never skip code review before commits
- Never guess at failures - always use root-cause-analysis
- Each task = one commit (atomic changes)
- The plan file is updated after each task completion
- If interrupted, the plan file reflects accurate state for next session
