---
name: tommymorgan:code-review
description: "Diff-scoped code review with optional fix loop that re-reviews until clean"
argument-hint: "[aspects] [fix[:N]] [parallel] [auto]"
allowed-tools: ["Bash", "Glob", "Grep", "Read", "Task"]
---

# Code Review Orchestrator

Multi-agent code review with an optional fix loop that **re-reviews after every fix cycle until the review comes back clean** (not just until fixes are applied).

## Step 1: Parse Arguments

Parse `$ARGUMENTS` for four things:

### Review Aspects

Valid aspect keywords:
- `code` — general code review
- `tests` — test quality analysis
- `comments` — comment quality analysis
- `errors` — silent failure detection
- `types` — type design analysis
- `simplify` — code simplification
- `all` — run all auto-detected agents (default when no aspect specified)

### Fix Mode

- `fix` — enable fix loop with default max of 5 iterations
- `fix:N` (e.g., `fix:3`) — fix loop with N max iterations
- If absent: review-only mode

### Execution Mode

- `parallel` — run review agents simultaneously
- If absent: sequential (default)

### Auto Mode

- `auto` — after the review agents produce findings, automatically dispatch the expert panel to debate every finding, then accept their consensus without prompting the user. Implies `fix` (defaults to `fix:5` if no explicit `fix:N`).
- If absent: interactive mode (present findings to user, fix loop requires user to invoke)

When `auto` is enabled:
1. Review agents run and produce findings (Steps 2-5)
2. Expert panel reviews ALL findings (not just in fix mode) — debates and reaches consensus
3. Consensus is applied automatically: APPROVE → fix as suggested, MODIFY → fix with panel's revision, REJECT → skip
4. Fixer agent applies all approved/modified fixes
5. Full re-review cycle runs (Steps 2-5 again)
6. Loop continues until clean or max iterations

The user sees progress updates but is never prompted for decisions. This is the "hands-off" mode for when you trust the review pipeline.

## Step 2: Determine Diff

### 2a: Check for an open PR

```bash
gh pr view --json baseRefName -q .baseRefName 2>/dev/null
```

### 2b: Get the diff

- **If a PR exists**: `git diff $(git merge-base <base> HEAD)` — includes committed and uncommitted changes
- **If no PR**: `git diff $(git merge-base main HEAD)` — all branch changes. If empty, fall back to `git diff HEAD` for uncommitted-only.

### 2c: Get changed file list

```bash
git diff --name-only <same-scope-as-2b>
```

### 2d: Validate

If diff is empty, report "No changes to review" and stop.

## Step 3: Determine Applicable Agents

### Explicit aspect selection

| Aspect | Agent |
|--------|-------|
| `code` | `tommymorgan:code-reviewer` |
| `tests` | `tommymorgan:test-analyzer` |
| `comments` | `tommymorgan:comment-analyzer` |
| `errors` | `tommymorgan:silent-failure-hunter` |
| `types` | `tommymorgan:type-design-analyzer` |
| `simplify` | `tommymorgan:code-simplifier` |

### Auto-detection (when `all` or no aspect specified)

- **Always run**: `tommymorgan:code-reviewer`
- **If any changed file matches `*.test.*` or `*.spec.*`**: also run `tommymorgan:test-analyzer`
- **If diff contains `catch`, `try {`, `.catch(`, `throw `**: also run `tommymorgan:silent-failure-hunter`
- **If diff contains `type `, `interface `, `z.object`, `z.string`, `z.enum`**: also run `tommymorgan:type-design-analyzer`
- **If diff contains comment patterns** (`//`, `/*`, `**/`)**: also run `tommymorgan:comment-analyzer`
- **`tommymorgan:code-simplifier`** only runs when explicitly requested

## Step 4: Launch Review Agents

For each agent, dispatch a Task with:
- `subagent_type` set to the agent name
- Prompt containing the full diff, changed file list, and instruction to review

**Sequential** (default): one at a time, summarize each before the next.
**Parallel**: all agents simultaneously in a single message.

## Step 5: Aggregate Results

Present a unified summary:

```markdown
# Code Review Summary

## Critical Issues (must fix)
- [agent-name] Issue description — `file.ts`
  > quoted diff hunk

## Important Issues (should fix)
- [agent-name] Issue description — `file.ts`

## Suggestions (consider)
- [agent-name] Suggestion — `file.ts`

## Strengths
- What's well-done
```

Deduplicate findings flagged by multiple agents.

**If auto mode is enabled**, skip presenting findings to the user and proceed directly to Step 6.

## Step 6: Fix Loop (when fix or auto mode is enabled)

**If neither fix nor auto mode is enabled, stop after Step 5.**

### Critical Design Principle

**Applying fixes is not enough. The loop must re-review after fixing and only terminate when the review comes back clean.** The common failure mode is stopping after one fix cycle, assuming the fixes are correct. They often aren't — fixes can introduce new issues, miss the point of the finding, or break adjacent code.

### Initialize

```
cycle = 1
max_cycles = <parsed from fix:N, default 5>
previous_issue_count = infinity
```

### 6a: Check termination conditions

Before each cycle (including the first):

1. **Clean review**: If Step 5 found zero issues → "Code is clean." → stop.
2. **Max iterations**: If `cycle > max_cycles` → report remaining issues → stop.
3. **Stall detection**: If current issue count >= `previous_issue_count` AND `cycle > 1` → report stall → stop.

### 6b: Expert panel review

Dispatch a Task to the expert panel:
- `subagent_type`: `tommymorgan:expert-panel`
- Prompt: all findings with agent name, file path, diff hunk, issue, suggestion
- Instruction: "Review each finding. Auto-select relevant experts. Debate conflicts. Output consensus: APPROVE, MODIFY, or REJECT."

### 6c: Process panel consensus

Separate findings into Approved, Modified, Rejected.

If all findings rejected → report panel reasoning → stop.

### 6d: Apply fixes

Dispatch a Task to the fixer:
- `subagent_type`: `tommymorgan:fixer`
- Prompt: approved and modified fixes with file paths, context, consensus instructions

### 6e: Report cycle progress

```
Cycle {cycle}/{max_cycles}: {total_issues} issues → {approved} approved → {applied} fixed → re-reviewing...
```

### 6f: RE-REVIEW (the critical step)

```
previous_issue_count = total_issues
cycle = cycle + 1
```

**Go back to Step 2** — re-capture the diff (files changed), re-detect agents, re-run review (Steps 3-5). Then return to 6a to check termination.

**This is the whole point of the loop: fixes are not trusted until verified by a fresh review.**

### 6g: Final report

```markdown
# Fix Loop Complete

**Cycles**: {completed_cycles} of {max_cycles}
**Outcome**: {Clean | Stalled | Max iterations | All rejected}

## Fixes Applied
- Cycle 1: {N} fixes
- Cycle 2: {N} fixes

## Remaining Issues (if any)
- [agent-name] Issue — `file.ts`

## Expert Panel Rejections (if any)
- [finding]: Rejected because [reasoning]
```

## Usage Examples

```
/tommymorgan:code-review                    # Full auto-detected review
/tommymorgan:code-review tests errors       # Specific aspects
/tommymorgan:code-review all parallel       # All agents in parallel
/tommymorgan:code-review fix                # Review and fix (up to 5 cycles)
/tommymorgan:code-review fix:3              # Fix with max 3 cycles
/tommymorgan:code-review code tests fix     # Specific aspects with fix
/tommymorgan:code-review fix parallel       # Fix with parallel review
/tommymorgan:code-review auto               # Hands-off: review, panel debate, fix, re-review until clean
/tommymorgan:code-review auto parallel      # Same but with parallel review agents
/tommymorgan:code-review auto fix:10        # Auto with higher iteration limit
```
