# tommymorgan

Git-based plan tracking with autonomous TDD execution and verified task completion.

## Overview

This plugin makes the git repository the source of truth for project planning. Plans are markdown files with Gherkin requirements and verification commands that prove task completion. Claude can pick up any plan in a new session and accurately determine what's been done.

## Features

- **Gherkin Requirements**: Capture requirements as executable scenarios
- **Verification-Based Completion**: Each task has a command that proves it's done
- **Autonomous TDD**: Claude executes tasks using red-green-refactor cycle
- **Code Review Gates**: Every commit reviewed before merging
- **Worktree Integration**: Each feature gets an isolated git worktree
- **Session-Resilient**: Plans survive across Claude sessions

## Commands

### `/tommymorgan:plan "description"`

Create a new plan via brainstorming.

1. Asks questions one at a time to understand requirements
2. Generates Gherkin scenarios for all requirements
3. Creates tasks with verification commands
4. Writes plan to `<project>/plans/YYYY-MM-DD-<slug>.md`
5. Creates feature worktree and switches to it

### `/tommymorgan:status`

Verify task completion and show progress.

1. Runs all verification commands in the plan
2. Updates task statuses (pending → complete)
3. Reports: "X/Y tasks complete. Next: <task>"

### `/tommymorgan:work`

Execute plan autonomously until complete.

1. Runs verification sweep first
2. For each incomplete task:
   - Writes failing test (red)
   - Implements until test passes (green)
   - Requests code review (loop until approved)
   - Commits with conventional commit message
   - Updates plan status
3. Uses root-cause-analysis before marking anything blocked

## Plan File Format

```markdown
# Feature: User Authentication

**Created**: 2024-12-15
**Branch**: feat/user-auth
**Goal**: Users can register and log in

## Requirements

Feature: User Registration
  Scenario: Successful registration
    Given I am a new user
    When I register with valid email and password
    Then my account should be created

## Tasks

### 1. Create user model
**Verify**: `pnpm test src/models/user.test.ts`
**Status**: pending

### 2. Add registration endpoint
**Verify**: `pnpm test src/routes/register.test.ts`
**Status**: pending

## Notes
- Design decisions and context
```

## Prerequisites

This plugin requires:

```bash
# Required plugins
cc plugins add superpowers@superpowers-marketplace
cc plugins add pr-review-toolkit@claude-code-plugins
cc plugins add root-cause-analysis@tommymorgan
```

## Installation

```bash
# From tommymorgan marketplace
cc plugins add tommymorgan@tommymorgan
```

## License

MIT
