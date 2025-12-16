# Feature: tommymorgan Plugin

**Created**: 2024-12-15
**Branch**: feat/tommymorgan-plugin
**Goal**: Git-based plan tracking with autonomous TDD execution and verified task completion

## Requirements

Feature: Plan Creation
  Scenario: Create plan via brainstorming
    Given I have a feature idea "User authentication"
    When I run /tommymorgan:plan "User authentication"
    Then Claude asks questions one at a time to refine requirements
    And generates Gherkin scenarios for all requirements
    And creates tasks with verification commands
    And writes plan to <project>/plans/YYYY-MM-DD-<slug>.md
    And creates a feature worktree from main
    And switches to the feature worktree

  Scenario: Infer project location from context
    Given I am working in apps/web/src/auth/
    When I run /tommymorgan:plan "Add login page"
    Then Claude infers project is apps/web
    And writes plan to apps/web/plans/YYYY-MM-DD-add-login-page.md

  Scenario: Ask when project location is ambiguous
    Given I am in the repository root
    When I run /tommymorgan:plan "Add shared utility"
    Then Claude asks which project this belongs to

Feature: Status Verification
  Scenario: Verify all tasks and update statuses
    Given a plan exists with 5 tasks
    And 2 tasks have passing verification commands
    When I run /tommymorgan:status
    Then Claude runs all 5 verification commands
    And updates statuses to complete for the 2 passing tasks
    And reports "2/5 tasks complete. Next: <first pending task>"

  Scenario: Detect completed work from previous session
    Given a plan was partially completed in a previous session
    When I start a new session and run /tommymorgan:status
    Then Claude accurately detects which tasks are complete
    And does not re-do completed work

Feature: Autonomous Work Execution
  Scenario: Execute full TDD cycle per task
    Given a plan with pending tasks
    When I run /tommymorgan:work
    Then for each task Claude writes a failing test first
    And implements until the test passes
    And requests code review from code-reviewer subagent
    And commits with conventional commit message
    And updates plan status to complete

  Scenario: Code review loop until approved
    Given Claude completed implementation for a task
    When code-reviewer finds issues
    Then Claude fixes the issues
    And requests another review
    And repeats until approved
    Then commits

  Scenario: Autonomous operation until complete
    Given a plan with 5 pending tasks
    When I run /tommymorgan:work
    Then Claude works through all 5 tasks without stopping
    And commits after each task
    And reports "Plan complete. All tasks verified."

  Scenario: Stop and investigate on failure
    Given Claude is working on a task
    When the test will not pass after reasonable attempts
    Then Claude invokes root-cause-analysis plugin
    And identifies the actual root cause
    And attempts fix based on root cause
    And if still failing marks task as blocked with root cause

Feature: Worktree Integration
  Scenario: Create worktree for new feature
    Given I run /tommymorgan:plan "New feature"
    When brainstorming completes and plan is written
    Then Claude creates a new git worktree for the feature branch
    And the worktree contains the plan file
    And Claude switches to the worktree

  Scenario: Work in existing worktree
    Given a feature worktree already exists
    When I run /tommymorgan:work
    Then Claude works in the current worktree
    And does not create a new one

## Tasks

### 1. Create plugin structure and manifest
**Verify**: `test -f tools/claude-plugins/tommymorgan/.claude-plugin/plugin.json && cat tools/claude-plugins/tommymorgan/.claude-plugin/plugin.json | jq -e '.name == "tommymorgan"'`
**Status**: complete

### 2. Implement /tommymorgan:plan command
**Verify**: `test -f tools/claude-plugins/tommymorgan/commands/plan.md`
**Status**: complete

### 3. Implement /tommymorgan:status command
**Verify**: `test -f tools/claude-plugins/tommymorgan/commands/status.md`
**Status**: complete

### 4. Implement /tommymorgan:work command
**Verify**: `test -f tools/claude-plugins/tommymorgan/commands/work.md`
**Status**: complete

### 5. Create plan-format skill with Gherkin template
**Verify**: `test -f tools/claude-plugins/tommymorgan/skills/plan-format/SKILL.md`
**Status**: complete

### 6. Create verification-sweep skill
**Verify**: `test -f tools/claude-plugins/tommymorgan/skills/verification-sweep/SKILL.md`
**Status**: complete

### 7. Create tdd-execution skill
**Verify**: `test -f tools/claude-plugins/tommymorgan/skills/tdd-execution/SKILL.md`
**Status**: complete

### 8. Remove or archive tommy-workflow plugin
**Verify**: `test ! -d tools/claude-plugins/tommy-workflow/.claude-plugin`
**Status**: complete

### 9. Rename marketplace to tommymorgan
**Verify**: `test -d /home/tommy/.claude/plugins/cache/tommymorgan && grep -q "tommymorgan@tommymorgan" /home/tommy/.claude/settings.json`
**Status**: complete

### 10. Test full workflow end-to-end
**Verify**: `echo "Manual verification: run /tommymorgan:plan, /tommymorgan:status, /tommymorgan:work on a test feature"`
**Status**: pending

## Notes

- Plugin replaces tommy-workflow with simpler, verification-based approach
- Plans live in project's plans/ directory, work happens in feature worktrees
- Plan file is source of truth - survives across sessions
- Gherkin scenarios make requirements unambiguous and testable
- 1:1 task-to-test-file mapping simplifies verification
- Final "refactor tests" task ensures test quality after implementation
- Uses root-cause-analysis before marking anything blocked
- Code review via code-reviewer subagent with fix-and-re-review loop
- Worktree created via superpowers:using-git-worktrees skill
