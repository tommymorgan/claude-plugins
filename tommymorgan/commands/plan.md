---
name: plan
description: Create a new feature plan via brainstorming with Gherkin requirements
argument-hint: "feature description"
allowed-tools:
  - Task
  - Skill
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# Create Feature Plan

Create a comprehensive feature plan through collaborative brainstorming, generating Gherkin requirements and verification-based tasks.

## Workflow

### Step 1: Invoke Brainstorming

Use the Skill tool to invoke the brainstorming skill:

```
Skill("superpowers:brainstorming")
```

Brainstorm the feature described by the user: $ARGUMENTS

Ask questions one at a time to understand:
- What problem does this solve?
- Who are the users?
- What are the success criteria?
- What are the constraints?

Explore 2-3 approaches and recommend one.

### Step 2: Determine Project Location

Infer the project location from context:
- Current working directory
- Recently accessed files
- Conversation context

Projects live in `apps/`, `libs/`, or `tools/` directories.

If ambiguous, use AskUserQuestion to ask:
"Which project does this feature belong to?"
Options: List detected projects from apps/, libs/, tools/

### Step 3: Generate Gherkin Requirements

Once the design is clear, write Gherkin scenarios for ALL requirements.

Format:
```gherkin
Feature: <feature name>
  Scenario: <happy path>
    Given <precondition>
    When <action>
    Then <outcome>

  Scenario: <edge case>
    Given <precondition>
    When <action>
    Then <outcome>
```

Cover:
- Happy paths
- Error cases
- Edge cases
- Security considerations

### Step 4: Generate Tasks with Verification Commands

Create tasks that map 1:1 with test files. Each task has exactly one verification command.

Format:
```markdown
### N. <task description>
**Verify**: `<command that exits 0 on success>`
**Status**: pending
```

The verification command should typically be running a specific test file:
- TypeScript/JavaScript: `pnpm test <path>` or `npm test -- <path>`
- Python: `pytest <path>`
- Go: `go test <path>`
- Rust: `cargo test <test_name>`

Always include a final task for test refactoring:
```markdown
### N. Refactor tests for maintainability
**Verify**: `<full test suite command>`
**Status**: pending
**Notes**: Reorganize from implementation-coupled to feature-focused tests
```

### Step 5: Write Plan File

Create the plan file at:
`<project>/plans/YYYY-MM-DD-<slug>.md`

Where:
- `<project>` is the inferred project path (e.g., `apps/web`, `libs/shared`)
- `YYYY-MM-DD` is today's date
- `<slug>` is a kebab-case version of the feature name

Plan file format:
```markdown
# Feature: <title>

**Created**: YYYY-MM-DD
**Branch**: feat/<slug>
**Goal**: <one-sentence user-facing outcome>

## Requirements

<Gherkin scenarios>

## Tasks

<numbered tasks with verify commands>

## Notes

<design decisions, constraints, context for future sessions>
```

Create the plans directory if it doesn't exist:
```bash
mkdir -p <project>/plans
```

### Step 6: Create Feature Worktree

Use the Skill tool to create a git worktree:

```
Skill("superpowers:using-git-worktrees")
```

Create a worktree for branch `feat/<slug>` based on the plan's branch field.

The worktree should be created from latest main so it contains the plan file.

### Step 7: Report Completion

After creating the plan and worktree, report:

```
Plan created: <path to plan file>
Worktree: <path to worktree>
Branch: feat/<slug>

Ready to work. Run /tommymorgan:work to begin.
```

## Important Notes

- Never skip brainstorming, even for "simple" features
- Gherkin scenarios must be complete before generating tasks
- Each task verification command must be runnable and deterministic
- The plan file is the source of truth for all future sessions
