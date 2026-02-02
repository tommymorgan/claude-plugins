# Feature: Relentless Execution Until Complete

**Created**: 2026-01-02
**Goal**: Make tommymorgan:work execute plans with unwavering persistence, validating all application layers without premature stopping.

## User Requirements

<!-- DONE -->
Scenario: Command completes all scenarios without asking permission to continue
  Given I invoke /tommymorgan:work with a plan
  When the command encounters multiple scenarios to implement
  Then it implements all scenarios sequentially without asking "should I continue?"
  And it never mentions token usage as a reason to pause
  And it never asks "what should I do next?"

<!-- DONE -->
Scenario: Command validates entire application works, not individual layers
  Given I invoke /tommymorgan:work with a full-stack feature
  When the command finishes implementing scenarios
  Then it validates the database layer functions correctly
  And it validates the API layer functions correctly
  And it validates the UI layer functions correctly
  And it validates data flows correctly between all layers
  And it only reports completion when all layers work together

<!-- DONE -->
Scenario: Command fixes unexpected problems without asking
  Given I invoke /tommymorgan:work with a plan
  When the command encounters an error or broken functionality
  Then it fixes the problem immediately
  And it never asks "is this in scope?"
  And it never says "this is separate work"
  And it continues execution without user intervention

<!-- DONE -->
Scenario: Command only stops when explicit completion criteria met
  Given I invoke /tommymorgan:work with a plan
  When the command is executing
  Then it continues until all scenarios are marked DONE
  And all tests pass in local development
  And all application layers are functional
  And only then does it report completion

<!-- DONE -->
Scenario: Command detects application architecture automatically
  Given I invoke /tommymorgan:work on any project type
  When the command begins execution
  Then it identifies what layers exist in the application
  And it knows which layers to validate at completion
  And it adapts validation to the specific architecture

## Technical Specifications

<!-- DONE -->
Scenario: Workflow enforces completion check before any stopping point
  Given the work command is executing a plan
  When the workflow reaches any potential stopping point
  Then it must run a completion check function
  And the completion check must verify: all scenarios DONE AND all tests passing AND all layers functional
  And if the check returns false, execution continues
  And execution only stops if the check returns true

<!-- DONE -->
Scenario: Architecture detection examines project structure and dependencies
  Given the work command initializes for a project
  When it performs architecture detection
  Then it examines package.json, pyproject.toml, or equivalent for dependencies
  And it examines directory structure for layer identification
  And it examines the plan scenarios for mentioned layers
  And it stores the detected architecture (layers list) in working memory
  And detected layers include types like: database, api, ui, cli, library, build-output

<!-- DONE -->
Scenario: Layer validation executes appropriate checks per layer type
  Given the work command has detected application layers
  When it performs layer validation
  Then for database layers: it verifies migrations applied and queries execute
  And for API layers: it verifies endpoints respond with correct status and data
  And for UI layers: it verifies rendering and interactivity
  And for CLI layers: it verifies command execution and output
  And for library layers: it verifies exports and imports work
  And for build-output layers: it verifies build succeeds and artifacts are valid

<!-- DONE -->
Scenario: Integration validation checks data flow between layers
  Given the work command has detected multiple connected layers
  When it performs integration validation
  Then it identifies integration points between layers
  And it verifies data flows correctly from source to destination
  And it verifies control flow works between layers
  And it tests realistic user scenarios that span multiple layers

<!-- DONE -->
Scenario: Error handling never asks for permission to fix problems
  Given the work command encounters an error or failure
  When it determines the problem
  Then it immediately invokes root cause analysis
  And it applies the fix without asking user
  And it retries validation
  And it only escalates if blocked after exhausting options

<!-- DONE -->
Scenario: Workflow state machine prevents premature completion
  Given the work command is executing
  When it evaluates whether to continue or stop
  Then it checks: scenarios_all_done AND tests_all_passing AND layers_all_functional
  And if any condition is false, it identifies next action and continues
  And it never rationalizes "this is separate work" or "I've done my part"
  And completion is only reported when all three conditions are true

<!-- DONE -->
Scenario: Token usage concerns are ignored during execution
  Given the work command is executing a plan
  When token usage increases during long-running execution
  Then the command never mentions tokens as a stopping reason
  And it never asks "should we continue given token usage?"
  And it executes to completion regardless of tokens consumed

<!-- DONE -->
Scenario: Progress feedback provides visibility without interruption
  Given the work command is executing a long-running plan
  When significant actions occur (scenario started, tests running, layer validation, etc.)
  Then the command logs progress messages to output
  And progress messages are informational only (no user response needed)
  And messages indicate current activity and completion percentage
  And user can observe progress without the command stopping

<!-- DONE -->
Scenario: Local development environment is explicitly defined
  Given the work command needs to validate in local development
  When it determines where to run validation
  Then local development means: application running on developer machine (not production, not CI)
  And validation uses local database instances (containers or host processes)
  And validation uses locally running services (API servers, dev servers, etc.)
  And validation can access localhost ports and local filesystems
  And this excludes: remote servers, production environments, CI/CD pipelines

<!-- DONE -->
Scenario: Exhausting options is bounded and explicit
  Given the work command encounters an error during fixing
  When it applies fixes and retries
  Then exhausting options means: attempted root cause fix 3 times
  And each attempt must use root cause analysis (no speculation)
  And each attempt must try a different approach based on new evidence
  And after 3 failed attempts with root cause analysis, the command is considered blocked
  And blocked state requires user intervention

## Notes

### Design Decisions

**State Machine Approach**: The workflow operates as a strict state machine with explicit completion criteria. No conversational elements that allow premature stopping.

**Architecture Detection**: Rather than hardcoding layer types, the system intelligently detects what exists in each project. This allows validation to adapt to CLI tools, full-stack apps, libraries, etc.

**Completion Criteria Function**: A single source of truth function that checks all three criteria. Called before any potential stop point. Returns boolean - no ambiguity.

**No Escape Hatches**: The workflow explicitly forbids rationalizations like "separate work", "out of scope", "token usage", or "what should I do?". These are treated as bugs to be prevented.

### Implementation Strategy

1. Add `checkCompletionCriteria()` function that validates all three conditions
2. Add `detectArchitecture()` function that returns layers list
3. Add `validateLayer(layerType)` function with switch statement for layer-specific checks
4. Add `validateIntegration(layers)` function that tests cross-layer flows
5. Modify workflow to call `checkCompletionCriteria()` before any stop
6. Remove all "ask user to continue" logic
7. Add explicit "never stop for tokens" instruction

### Constraints

- Must remain compatible with existing plan file format (TODO/DONE comments)
- Must work with all project types (full-stack, CLI, library, static site, etc.)
- Must not break existing TDD, code review, and exploratory testing gates
- Should enhance, not replace, current workflow

### Expert Review Consensus

All 7 experts reviewed and reached consensus after debate:

**Key Additions from Review**:
1. **Progress Feedback** (Google SRE): Non-interactive logging provides observability without breaking autonomy
2. **Local Dev Definition** (Eric Evans): Explicit bounded context for validation environment
3. **Exhausting Options** (Dave Farley): 3 attempts with root cause analysis, then escalate

**User Veto**: Timeouts removed - true relentless execution means no time-based stopping.

**Unanimous Approval**: All experts approved the plan with these additions, confirming it solves the premature stopping problem while maintaining production quality.
