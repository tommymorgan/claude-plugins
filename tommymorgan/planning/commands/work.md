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

## Completion Criteria

**The work command ONLY stops when ALL FOUR conditions are met:**

1. **All scenarios DONE**: Every scenario in plan marked `<!-- DONE -->`
2. **All tests passing**: Full test suite passes in local development
3. **All layers functional**: Every application layer validated and working
4. **All living specs written**: Every scenario has corresponding `.feature` file in `features/`

**Before ANY potential stopping point, check completion criteria:**
```
function checkCompletionCriteria():
  scenarios_done = all scenarios marked DONE in plan
  tests_passing = test suite exits 0 in local dev
  layers_functional = all detected layers validated successfully
  living_specs_written = features/*.feature contains all scenarios (verify with grep)

  return scenarios_done AND tests_passing AND layers_functional AND living_specs_written
```

**Verify living specs exist:**
```bash
# Count scenarios in plan
plan_scenarios=$(grep -c "^Scenario:" plan.md)

# Count scenarios in feature files
feature_scenarios=$(grep -c "^  Scenario:" features/*.feature 2>/dev/null || echo 0)

# Must match (or feature_scenarios >= plan_scenarios)
```

**If `checkCompletionCriteria()` returns false → continue execution**
**If `checkCompletionCriteria()` returns true → report completion and stop**

**NEVER:**
- Ask "should I continue?"
- Mention token usage as stopping reason
- Ask "what should I do next?"
- Say "this is separate work"
- Rationalize incomplete work as "done"

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

**Detect application architecture:**
```
function detectArchitecture():
  layers = []

  // Check project files
  if exists(package.json) → examine dependencies for: databases, APIs, UI frameworks, build tools
  if exists(pyproject.toml or requirements.txt) → examine for: databases, web frameworks, CLI tools

  // Check directory structure
  if exists(src/db or migrations or schema) → add 'database' layer
  if exists(src/api or routes or controllers) → add 'api' layer
  if exists(src/ui or components or views) → add 'ui' layer
  if exists(src/cli or __main__.py or bin/) → add 'cli' layer

  // Check plan scenarios for mentioned layers
  scan scenarios for keywords: "database", "API", "UI", "CLI", "build", "library"

  // Determine build vs library
  if has build process (vite, webpack, tsc, etc.) → add 'build-output' layer
  if exports modules (library) → add 'library' layer

  return layers
```

Store detected layers for validation later.

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

3. **Update living specification** (MANDATORY - not optional):

   **DEFAULT BEHAVIOR**: Every scenario MUST be written to a `.feature` file unless explicitly marked `# Living: none`.

   **Determine target file:**
   - If plan has `# Living: <path>` metadata → use that path
   - If NO metadata → derive from scenario: `features/<feature-area>.feature`
     - Example: "User logs in" → `features/authentication.feature`
     - Example: "API returns 404" → `features/api-errors.feature`

   **Write the scenario:**
   ```bash
   # Create features/ directory if needed
   mkdir -p features/

   # Write scenario to .feature file
   # Include @user or @technical tag based on section
   ```

   **Verify the write happened:**
   ```bash
   # MUST show the scenario in git diff
   git diff --name-only | grep -E "\.feature$"

   # MUST show scenario content
   grep -l "<scenario name>" features/*.feature
   ```

   **If verification fails → STOP and fix before continuing.**

   **Update plan metadata:**
   ```gherkin
   # Status: DONE
   # Living updated: YES
   ```

   **Commit living spec:**
   ```bash
   git add features/*.feature
   git commit -m "docs: add scenario to living specification"
   ```

   **GATE CHECK before next scenario:**
   - Run: `git log -1 --name-only | grep -E "\.feature$"`
   - If NO .feature file in last commit → HALT with error:
     ```
     ERROR: Living specification not updated!
     Scenario "<name>" must be written to features/<file>.feature
     This is MANDATORY, not optional.
     ```

4. **If blocked after reasonable attempts:**
   - **NEVER guess at fixes**
   - **ALWAYS invoke `/tommymorgan:root-cause`:**
     ```typescript
     Task({
       subagent_type: "tommymorgan:root-cause-analyzer",
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

Before marking scenario complete, run all 6 code review agents in parallel:

```typescript
// Run all 6 agents in parallel
const reviews = await Promise.all([
  Task({
    subagent_type: "tommymorgan:code-reviewer",
    description: "Review code quality",
    prompt: `Review implementation for: <Gherkin scenario text>
    Changed files: <list changed files>
    Check: CLAUDE.md compliance, style, bugs, quality`
  }),
  Task({
    subagent_type: "tommymorgan:comment-analyzer",
    description: "Review comments/docs",
    prompt: `Review documentation for: <Gherkin scenario text>
    Changed files: <list changed files>
    Check: Comment accuracy, completeness, staleness`
  }),
  Task({
    subagent_type: "tommymorgan:test-analyzer",
    description: "Review test coverage",
    prompt: `Review tests for: <Gherkin scenario text>
    Changed files: <list changed files>
    Check: Coverage gaps, edge cases, test quality`
  }),
  Task({
    subagent_type: "tommymorgan:silent-failure-hunter",
    description: "Hunt silent failures",
    prompt: `Review error handling for: <Gherkin scenario text>
    Changed files: <list changed files>
    Check: Empty catches, missing logging, swallowed errors`
  }),
  Task({
    subagent_type: "tommymorgan:type-design-analyzer",
    description: "Review type design",
    prompt: `Review types for: <Gherkin scenario text>
    Changed files: <list changed files>
    Check: Encapsulation, invariants, enforcement`
  }),
  Task({
    subagent_type: "tommymorgan:code-simplifier",
    description: "Find simplifications",
    prompt: `Review complexity for: <Gherkin scenario text>
    Changed files: <list changed files>
    Check: Unnecessary complexity, redundancy, clarity`
  })
]);
```

**Aggregate results:**
- APPROVED: All 6 agents approve (no issues with score >= 91)
- NEEDS_CHANGES: Any agent flags critical issues (score >= 91)

**Display all feedback:**
- Show issues from all agents grouped by severity
- Show verdicts from each agent

**If NEEDS_CHANGES:**
1. Invoke `/tommymorgan:root-cause` to analyze the feedback
2. Address issues based on root cause analysis
3. Re-run tests
4. Request another review (all 6 agents)
5. If still NEEDS_CHANGES, repeat steps 1-4
6. After 3 root-cause-driven iterations: Block and require user intervention

**Hooks will run automatically:**
- Linting
- Type checking
- Formatting

### Step 7: Check Progress

**After code review approves:**

Run `checkCompletionCriteria()`:
- All scenarios DONE?
- All tests passing?
- All layers functional?

**If ANY condition is false:**
- Identify what's incomplete
- **More scenarios TODO?** → Go to Step 4 (next scenario)
- **Tests not run/failing?** → Run tests, fix failures, retry
- **Layers not validated?** → Continue to Step 8

**If ALL conditions true:**
- Skip to Step 10 (already complete)

**DO NOT ask user - continue autonomously**

### Step 8: Layer Validation Gate

**Before exploratory testing**, validate all detected layers:

```
function validateLayers(detected_layers):
  for each layer in detected_layers:
    validateLayer(layer)

  validateIntegration(detected_layers)

function validateLayer(layer_type):
  switch layer_type:
    case 'database':
      - Verify migrations applied (check migration status)
      - Execute sample queries (SELECT, INSERT if appropriate)
      - Confirm schema matches expected structure

    case 'api':
      - Start API server in local dev
      - Test endpoints respond with correct status codes
      - Verify response data structure and content
      - Test error cases return appropriate errors

    case 'ui':
      - Start UI dev server
      - Verify pages/components render
      - Test interactivity (clicks, forms, navigation)
      - Verify data displays correctly

    case 'cli':
      - Execute command with valid inputs
      - Verify expected output
      - Test error cases
      - Confirm exit codes correct

    case 'library':
      - Verify exports are accessible
      - Test imports in sample code
      - Confirm types/interfaces work

    case 'build-output':
      - Run build process
      - Verify build succeeds (exit 0)
      - Confirm artifacts generated
      - Check artifacts are valid

function validateIntegration(layers):
  // Identify integration points and verify with concrete methods

  if 'database' in layers and 'api' in layers:
    - Start API server in local dev
    - Execute API endpoint that queries database
    - Verify API response contains expected database data
    - Check database query logs show correct SQL execution
    - Confirm data transformation from DB format to API format

  if 'api' in layers and 'ui' in layers:
    - Start both API and UI servers in local dev
    - Navigate UI to page that fetches from API
    - Verify network requests show API calls (browser DevTools or logs)
    - Verify UI displays correct API response data
    - Test error case: API returns error, UI shows error message

  if 'database' in layers and 'ui' in layers:
    - Execute end-to-end scenario: UI interaction → API call → DB operation → API response → UI update
    - Verify each layer processed the operation (check logs, network, DB)
    - Verify final UI state reflects the database change
    - Test reverse flow: DB change → UI reflects change (if applicable)

  // Test realistic user scenarios that span multiple layers
  - Extract key user flows from plan scenarios
  - For each flow: Execute as if user performed it
  - Verify data flows correctly through all layers
  - Verify outcome matches scenario expectation
  - Confirm no layer is bypassed or mocked
```

**If any layer validation fails:**
- **NEVER guess at fixes**
- **ALWAYS invoke `/tommymorgan:root-cause`:**
  ```typescript
  Task({
    subagent_type: "tommymorgan:root-cause-analyzer",
    description: "Analyze layer validation failure",
    prompt: `Root cause analysis:

    Layer: <layer type>
    Validation failure: <what failed>
    Evidence: <error messages, logs>

    Use five-whys methodology.
    Provide evidence-based analysis.`
  })
  ```
- Apply fix based on root cause
- Retry validation
- Apply retry logic (max 3 attempts with different root cause approaches)
- After 3 failed attempts: Block and require user intervention

**Only proceed when all layers validated.**

### Step 9: Exploratory Testing Gate

**After layer validation**, validate with exploratory testing:

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
- Check completion criteria
- If complete: Continue to Step 10
- If incomplete: Return to appropriate step

**If exploratory tests FAIL:**
- Go back to Step 4
- Fix failing scenarios
- Retry review, layer validation, and testing gates

### Step 10: Check Completion Criteria

**Before proceeding to final commit:**

Run `checkCompletionCriteria()`:
- All scenarios DONE?
- All tests passing?
- All layers functional?

**If ANY condition is false:**
- Identify what's incomplete
- Return to appropriate step to fix
- DO NOT ask user - continue autonomously

**If ALL conditions true:**
- Continue to Step 11

### Step 11: Squash & Final Commit

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

### Step 12: Update Plan & Report

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

## Progress Feedback

**Log progress messages at key milestones:**
- "Starting scenario X of Y: [title]"
- "Writing tests for scenario..."
- "Tests passing, implementing code..."
- "Running code review..."
- "Code review approved, continuing..."
- "Checking completion criteria..."
- "Completion check: X/3 criteria met (scenarios: X, tests: X, layers: X)"
- "Validating layers: [list]"
- "Validating [layer_type] layer..."
- "Layer [layer_type]: PASSED"
- "Testing integration between [layer1] and [layer2]..."
- "Integration validation complete"
- "Running exploratory tests..."
- "All tests passed, all layers functional"

**Messages are informational only - never wait for user response.**

## Error Handling

**When any validation or test fails:**
- Log: "Failure detected: [description]"
- Invoke `/tommymorgan:root-cause` (not speculation!)
- Apply evidence-based fix
- Retry validation
- Continue until fixed

**Retry logic - "exhausting options":**
- Attempt 1: Root cause analysis → fix → retry
- Attempt 2: Different root cause analysis → different fix → retry
- Attempt 3: Third root cause analysis → third fix → retry
- After 3 attempts: Block and require user intervention

**NEVER:**
- Ask "is this in scope?"
- Say "this is separate work"
- Ask "should I fix this?"
- Mention token usage
- Ask "what should I do?"

**ALWAYS:**
- Fix problems immediately
- Continue autonomously
- Apply bulldog persistence

## Important Notes

- **Scenarios ARE the plan** - no separate task lists
- **Commit incrementally** during TDD, squash at end
- **Documentation updates** are mandatory, not optional
- **Local dev verification** is mandatory before starting
- **Code review gate** is mandatory before continuing
- **Layer validation gate** is mandatory after all scenarios
- **Exploratory testing gate** is mandatory before completion
- **Completion criteria check** is mandatory before stopping
- **Root-cause analysis** instead of guessing
- **Bulldog persistence** - no shortcuts that create tech debt
- **Border Collie intelligence** - excellent autonomous judgment
- **Never stop for token usage** - execute to completion
- **Fix all problems** - never ask if in scope
- **LIVING SPECS ARE MANDATORY** - every scenario MUST be written to `features/*.feature`
  - This is NOT optional
  - Verify with `ls features/*.feature` and `grep "Scenario:" features/*.feature`
  - If features/ directory is empty or missing scenarios → work is NOT complete

## Local Development Definition

**Local development means:**
- Application running on developer machine (not production, not CI)
- Local database instances (containers or host processes)
- Locally running services (API servers, dev servers)
- Access to localhost ports and local filesystems

**Local development excludes:**
- Remote servers
- Production environments
- CI/CD pipelines
