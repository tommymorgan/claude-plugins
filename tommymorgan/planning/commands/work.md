---
name: tommymorgan:work
description: Execute plan autonomously with TDD, code review, and exploratory testing gates until complete
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
  - AskUserQuestion
---

# Execute Plan Autonomously with Quality Gates

Work through all scenarios in a plan using TDD with comprehensive quality gates. Continue autonomously until complete or blocked.

## Core Principles

- **Bulldog Persistence**: Don't give up or take shortcuts that create tech debt
- **Border Collie Intelligence**: Apply excellent judgment and autonomy
- **Root-Cause Driven**: Use `/tommymorgan:root-cause` instead of speculation
- **Quality Gates**: Code review and exploratory testing before completion
- **Documentation First-Class**: Update docs alongside code

## Workflow

### Step 1: Initialization

**Ask about workspace:**

Use AskUserQuestion to ask:
```
"Should I work in a worktree or directly on trunk?"
Options:
- "Create worktree at ~/src/worktrees/<repo>-<branch>" (Recommended for isolation)
- "Work directly on main/master/trunk" (Faster for small changes)
```

If worktree selected:
- Create at `~/src/worktrees/<repo-name>-<branch-name>/`
- Example: `~/src/worktrees/homelab-feat-plugin-consolidation/`
- Clean, short paths to avoid context window issues

**Read and understand plan:**
- Load plan file
- Parse User Requirements section
- Parse Technical Specifications section
- Understand all scenarios

### Step 2: Verify Local Development Environment

**CRITICAL**: All work must be done in local dev environment.

**Intelligently verify based on project type:**
- Container orchestration running (Podman, Docker)
- Databases accessible (PostgreSQL, Redis, etc.)
- Dev server can start
- Environment variables configured
- Dependencies installed

**If verification fails:**
```
STOP: Local dev environment not ready

Issues found:
- <specific problems>

See plan for local dev setup scenarios.
Run those first, then resume work.
```

**Only proceed if local dev works.**

### Step 3: Check Scenario Status

Read plan file and identify scenarios:
- Count TODO scenarios
- Count DONE scenarios
- Identify next TODO scenario

If all scenarios DONE:
```
Plan complete! All scenarios implemented and tested.
```
Stop here.

If scenarios remain, continue to Step 4.

### Step 4: Select Next Scenario

Pick the first TODO scenario (in order: User Requirements first, then Technical Specifications).

Use TodoWrite to track implementation of this scenario.

### Step 5: TDD Implementation

**Red-Green-Refactor for this scenario:**

1. **Write failing tests** that prove scenario is satisfied
   - Tests describe behavior from Gherkin Given/When/Then
   - Meaningful test titles
   - Run tests to confirm they fail

2. **Implement to make tests pass**
   - Write minimal code
   - Follow Gherkin as specification
   - **Update documentation** (user, developer, API docs as needed)
   - Commit incrementally (each green cycle)

3. **Update living specification** (automatic):
   - Parse scenario metadata from plan:
     ```gherkin
     # Living: <project>/specs/<file>.feature::<scenario-name>
     # Action: creates|replaces|extends|removes|deprecates
     # Status: TODO
     # Living updated: NO
     ```
   - If `Living:` is not "none":
     - Load the .feature file
     - Apply the action:
       - **creates**: Append new scenario to file (preserve @user/@technical tag)
       - **replaces**: Find and replace existing scenario completely
       - **extends**: Add new Given/When/Then steps to existing scenario
       - **removes**: Delete scenario from file
       - **deprecates**: Add @deprecated tag and comment
     - Update plan metadata:
       ```gherkin
       # Status: DONE
       # Living updated: YES
       ```
     - Commit living spec update
   - Enforce strict sequential:
     - Before starting next scenario, verify current has `Living updated: YES`
     - If NO, halt with error

4. **If blocked after reasonable attempts:**
   - **NEVER guess at fixes**
   - **ALWAYS invoke `/tommymorgan:root-cause`:**
     ```typescript
     Task({
       subagent_type: "root-cause-analysis:root-cause-analyzer",
       description: "Analyze failure: <scenario>",
       prompt: `Root cause analysis:

       Scenario: <Gherkin scenario>
       Error: <what's failing>
       Attempts: <what was tried>

       Use five-whys methodology.
       Provide evidence-based analysis.`
     })
     ```
   - Apply fix based on root cause
   - If unfixable, mark scenario blocked

5. **Refactor** if needed

### Step 6: Code Review Gate

Before marking scenario complete, get code review:

```typescript
Task({
  subagent_type: "pr-review-toolkit:code-reviewer",
  description: "Review scenario implementation",
  prompt: `Review implementation:

Scenario: <Gherkin scenario text>

Focus on:
- Does implementation satisfy the scenario?
- Code quality and best practices
- Security considerations
- Documentation accuracy and completeness
- Test quality

Changed files: <list changed files>

Respond: APPROVED or NEEDS_CHANGES with details.`
})
```

**If NEEDS_CHANGES:**
1. Address feedback (with bulldog persistence!)
2. Re-run tests
3. Request another review
4. Loop until APPROVED

**If still failing after 3 iterations:**
- Invoke `/tommymorgan:root-cause`
- Determine if blocked

**Hooks will run automatically:**
- Linting
- Type checking
- Formatting

### Step 7: Continue or Test

**After code review approves:**

Check if more TODO scenarios exist:
- **More scenarios?** → Go to Step 4 (next scenario)
- **All scenarios TODO → DONE?** → Continue to Step 8

### Step 8: Exploratory Testing Gate

**Before claiming completion**, validate with exploratory testing:

```typescript
Task({
  subagent_type: "tommymorgan:exploratory-tester",
  description: "Validate implementation against plan",
  prompt: `Run plan-aware exploratory testing.

Plan file: <plan path>

Validate all scenarios (User Requirements + Technical Specifications).
Report any failures.`
})
```

**If exploratory tests PASS:**
- Continue to Step 9

**If exploratory tests FAIL:**
- Go back to Step 4
- Fix failing scenarios
- Retry review and testing gates

### Step 9: Squash & Final Commit

**After all scenarios complete and tested:**

1. **Squash incremental commits** into single, clean commit:
   ```bash
   git rebase -i main  # or appropriate base branch
   ```

2. **Create final conventional commit:**
   ```bash
   git commit -m "<type>(<scope>): <description>

   <body describing what was delivered, not how>

   Implements: <list scenarios delivered>

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
   ```

### Step 10: Update Plan & Report

1. **Mark all scenarios as DONE** in plan file (change `<!-- TODO -->` to `<!-- DONE -->`)

2. **Report completion:**
   ```
   ## Work Session Complete

   **Plan**: <plan file>
   **Scenarios**: All X scenarios implemented
   **Quality Gates**: All passed (code review ✓, exploratory testing ✓)
   **Commits**: Squashed to 1 clean commit

   ### Completed Scenarios
   <list all DONE scenarios>

   ### Quality Summary
   - Code review: APPROVED
   - Exploratory testing: PASSED
   - Documentation: Updated
   - Local dev: Verified

   Ready for deployment!
   ```

## Error Handling

**When verification fails:**
- Invoke `/tommymorgan:root-cause` (not speculation!)
- Apply evidence-based fixes
- Retry with persistence

**When code review fails repeatedly:**
- Invoke `/tommymorgan:root-cause`
- Understand fundamental issue
- Fix properly, don't work around

**When exploratory tests fail:**
- Go back to implementation
- Fix the actual issues
- Don't proceed until passing

**Only ask user as absolute last resort** - apply excellent autonomous judgment first.

## Important Notes

- Scenarios ARE the plan - no separate task lists
- Commit incrementally during TDD, squash at end
- Documentation updates are mandatory, not optional
- Local dev verification is mandatory before starting
- Code review gate is mandatory before continuing
- Exploratory testing gate is mandatory before completion
- Root-cause analysis instead of guessing
- Bulldog persistence - no shortcuts that create tech debt
- Border Collie intelligence - excellent autonomous judgment
