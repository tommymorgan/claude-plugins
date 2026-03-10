# tommymorgan

**Version**: 0.7.0
**Category**: Development Workflow
**License**: MIT

Comprehensive development workflow plugin enforcing disciplined planning, autonomous TDD execution, expert code review, complete task completion, and automatic image preprocessing.

## Philosophy

**Bulldog Persistence + Border Collie Intelligence**

This plugin enforces discipline without being obstructive. It won't let you take shortcuts that create technical debt, but it applies excellent autonomous judgment to get work done right.

## Installation

```bash
claude plugin install tommymorgan@tommymorgan
```

## Commands

### Planning

#### `/tommymorgan:plan`
Create structured Gherkin-based feature plans.

**Output**: `plans/YYYY-MM-DD-<feature-name>.md`

Plans contain:
- User Requirements (Gherkin scenarios from user perspective)
- Technical Specifications (implementation scenarios)
- Scenarios marked with `<!-- TODO -->` or `<!-- DONE -->`

#### `/tommymorgan:work <plan-file>`
Execute plan autonomously using TDD until 100% complete.

**Workflow**:
1. Verify local dev environment works
2. For each TODO scenario:
   - Write failing test (RED)
   - Implement until test passes (GREEN)
   - Refactor if needed
   - Run code review gate (must approve before continuing)
   - Commit incrementally
3. Run exploratory testing gate
4. Squash commits into single clean commit
5. Mark all scenarios as DONE

**Quality Gates** (mandatory):
- Code review: Every scenario reviewed before next one starts
- Exploratory testing: Full validation before completion
- All tests must pass
- No stopping until 100% complete

#### `/tommymorgan:status [plan-file]`
Check scenario completion progress.

**Output**:
```
Progress: 8/12 scenarios complete (67% done)

User Requirements:
✅ User can register with email
✅ User can login with credentials
⏳ User can refresh JWT token

Technical Specifications:
✅ Database stores user records
⏳ API validates JWT signatures
...

Next scenario: User can refresh JWT token
```

#### `/tommymorgan:review-features <path>`
Review Gherkin scenarios with a panel of domain experts.

**Accepts**:
- `.feature` files
- Plan files (`.md`)
- Directories (all `.feature` files)
- Glob patterns (`features/*.feature`)

#### `/tommymorgan:review-plan <plan-file>`
Review a plan file with the expert panel (wrapper around `/review-features`).

**Expert Panel** (13 composite domain experts):
1. **Product Strategy Expert** — User outcomes vs implementation details
2. **Continuous Delivery Expert** — Testability, automation, deployability
3. **Security Expert** — Threat modeling, authentication, data protection
4. **UX Expert** — User experience, clarity, error messaging
5. **Data Systems Expert** — Storage, queries, migrations, performance
6. **Domain Design Expert** — Domain modeling, ubiquitous language
7. **SRE Expert** — Operations, observability, reliability (context-aware)
8. **Testing Expert** — Test strategy, coverage, maintainability
9. **Cloud Expert** — Infrastructure, scaling, deployment topology
10. **Accessibility Expert** — Inclusive design, WCAG compliance
11. **Engineering Effectiveness Expert** — Developer experience, feedback loops
12. **Software Architecture Expert** — Modularity, composition, boundaries
13. **Privacy Expert** — Data collection, consent, retention

**Context-Aware Filtering**: Experts adjust recommendations based on plan type:
- Hook vs API vs UI vs Database
- CLI tool vs production service
- Simple tool vs data-intensive system

**Output**:
- Critical/High/Medium priority recommendations
- Expert debates and consensus for conflicts
- Specific scenario references
- Concrete improvement suggestions

**Output format**: Structured review with prioritized recommendations

### Testing

#### `/tommymorgan:test`
Plan-aware exploratory testing.

Automatically selects testing strategy:
- **API testing**: REST/GraphQL endpoint validation
- **Browser testing**: Functional, visual, accessibility, performance
- **CLI testing**: Command validation, output correctness, exit codes

### Migration

#### `/tommymorgan:migrate-to-living-specs`
One-time migration to create living `.feature` files from historical plan files.

#### `/tommymorgan:generate-docs`
Generate user or developer documentation from living `.feature` files.

#### `/tommymorgan:coverage-analysis`
Analyze test coverage of living specification scenarios.

### Debugging

#### `/tommymorgan:root-cause`
Systematic root cause analysis using five whys methodology.

**Prevents**: Speculation-driven debugging, endless fix loops, harmful changes

**Process**:
1. Observe the problem
2. Gather evidence (logs, code, metrics)
3. Ask "why?" until root cause found (typically 5 levels deep)
4. Only then attempt fixes

## Hooks

### Stop Hook (Work Completion Enforcement)

**Purpose**: Enforces complete work sessions - no partial completion.

**Behavior**:
- Searches for plan files in current and parent directories (up to 3 levels)
- Calculates completion: `done_count / (todo_count + done_count)`
- **Blocks stopping** if completion < 100%
- **Allows stopping** if completion = 100% or no plan found

**Error Message**:
```
Work incomplete: 3/12 scenarios TODO (75%)
```

**No Override**: Strictly enforces completion. Emergency exits:
1. Complete the work (mark scenarios DONE)
2. Use Ctrl+C to force quit

**Performance**: Executes in <500ms

**Safety**:
- Path validation prevents traversal attacks
- Graceful failure on malformed plans
- Defensive defaults (allow stop on errors)

### Automatic Image Resizing

**Purpose**: Prevents Claude API errors by automatically resizing oversized images before submission.

**Behavior**:
- Intercepts UserPromptSubmit events
- Detects images exceeding 2000px in any dimension
- Resizes to 2000px max dimension (maintains aspect ratio)
- Uses LANCZOS resampling for quality preservation
- Preserves transparency for PNG/GIF
- Converts RGBA→RGB for JPEG (white background)

**Feedback**:
```
Image resized to meet Claude Code 2000px limit: 3200x2400 to 2000x1500
```

**Configuration**:
Create `.claude/tommymorgan.local.md` to disable:
```yaml
---
auto_resize_images: false
---

# TommyMorgan Plugin Configuration

Set auto_resize_images to false to disable automatic resizing.
```

**Default**: Enabled (automatic resizing active)

**Conflict Detection**:
- Warns if old `auto-resize-images` plugin is installed
- Suggests uninstalling to avoid duplicate processing
- Both hooks will run during transition period

**Error Handling**:
- Unsupported formats (WEBP, etc): Blocks with helpful conversion instructions
- Corrupted images: Blocks with recovery suggestions
- Missing dependencies: Exits gracefully with error to stderr

**Performance**: Executes in <5 seconds per image

**Dependencies**: Python 3.8+ with Pillow (PIL) library

## Plan File Format

```markdown
# Feature: User Authentication API

**Created**: 2026-01-01
**Goal**: Add JWT-based authentication for API endpoints

## User Requirements

<!-- TODO -->
# Living: none (initial implementation)
# Action: creates
# Status: TODO
# Living updated: NO
Scenario: User registers with email
  Given I am a new user
  When I POST to /api/auth/register with email and password
  Then I receive a 201 response with user ID
  And I receive a JWT access token

<!-- DONE -->
# Living: apps/api/features/authentication.feature::user-logs-in
# Action: replaces
# Status: DONE
# Living updated: YES
Scenario: User logs in with credentials
  Given I am a registered user
  When I POST to /api/auth/login with valid credentials
  Then I receive a JWT access token

## Technical Specifications

<!-- TODO -->
# Living: none (initial implementation)
# Action: creates
# Status: TODO
# Living updated: NO
Scenario: JWT tokens expire after 7 days
  Given a user has a valid JWT token
  When 7 days have passed
  Then the token should be rejected as expired
  And API should return 401 Unauthorized

## Affected Documentation

- [ ] Update README.md — document authentication endpoints
- [ ] Update docs/api.md — add auth API reference

## Notes

**Design Decisions**:
- Using HS256 for JWT signing (symmetric, simpler for single server)
- 7-day token expiration (balance security vs UX)
- Refresh tokens stored in database, access tokens stateless
```

## Workflow Example

```bash
# 1. Create a plan
/tommymorgan:plan
You: "Add user authentication API with JWT tokens"
Claude: [Creates structured plan with User Requirements and Technical Specs]

# 2. Review the plan (optional)
/tommymorgan:review-plan plans/2026-01-01-auth-api.md
Claude:
## Critical Issues
[Cagan] Missing scenario: User sees helpful error for invalid credentials
[OWASP] Scenario needed: System prevents brute force login attempts
...

# 3. Execute the plan
/tommymorgan:work plans/2026-01-01-auth-api.md
Claude:
Implementing scenario: User registers with email
- Writing failing test... [RED]
- Implementing registration endpoint... [GREEN]
- Running code review gate... [APPROVED]
- Committed: feat(auth): add user registration endpoint

Implementing scenario: JWT tokens expire after 7 days
- Writing failing test... [RED]
...
All scenarios complete! Squashing commits...

# 4. Check progress anytime
/tommymorgan:status
Claude:
Progress: 12/12 scenarios complete (100% done)
All scenarios implemented and tested ✓

# Try to stop early (will be blocked)
<Ctrl+D>
Claude: Work incomplete: 4/12 scenarios TODO (67%)
[Stop blocked - complete the work or use Ctrl+C]
```

## Components

### Skills
- `brainstorming` - Collaborative idea exploration and design
- `plan-format` - Gherkin plan structure and formatting
- `tdd-execution` - Red-Green-Refactor workflow
- `verification-sweep` - Test execution and validation
- `api-testing-patterns` - REST/GraphQL testing patterns
- `browser-testing-patterns` - Web UI testing with agent-browser CLI
- `cli-testing-patterns` - CLI tool testing patterns
- `rest-api-guidelines` - REST API design patterns and conventions
- `five-whys-methodology` - Root cause analysis process

### Agents

**Code Review** (6 agents run in parallel during /work):
- `code-reviewer` - CLAUDE.md compliance, style, bugs, quality
- `comment-analyzer` - Comment accuracy, completeness, staleness
- `test-analyzer` - Coverage gaps, edge cases, test quality
- `silent-failure-hunter` - Empty catches, missing logging, swallowed errors
- `type-design-analyzer` - Encapsulation, invariants, enforcement
- `code-simplifier` - Unnecessary complexity, redundancy

**Exploratory Testing**:
- `exploratory-tester` - Autonomous exploratory testing against plan scenarios
- `api-explorer` - Autonomous API endpoint testing
- `browser-explorer` - Autonomous browser-based testing
- `cli-tester` - Autonomous CLI tool testing

**Debugging**:
- `root-cause-analyzer` - Autonomous five whys investigation

### Hooks
- **Stop Hook**: Enforces work completion before stopping
- **Automatic Image Resizing**: Prevents API errors by resizing oversized images
- **Pre-Push Squash**: Verifies commits are squashed before push
- **Post-Push Cleanup**: Cleanup after successful push

## Design Principles

1. **No Shortcuts**: Stop hook enforces completion - no override mechanism
2. **Quality Gates**: Code review and testing gates are mandatory, not optional
3. **Evidence-Based**: Root cause analysis before fixes (no speculation)
4. **Incremental**: TDD with small commits, then squash at end
5. **Autonomous**: Agents handle complex tasks independently
6. **Context-Aware**: Experts adjust to plan type (API vs hook vs CLI)
7. **Bulldog Persistence**: Don't give up or take shortcuts
8. **Border Collie Intelligence**: Excellent judgment and autonomy

## Testing

The plugin includes comprehensive test suites:
- `planning/commands/test_review_plan.py` - 15 tests for plan parsing and context detection
- `hooks/test_stop_if_incomplete.py` - 18 tests for stop hook enforcement
- `hooks/test_resize_images.py` - 18 tests for automatic image resizing
- `hooks/test_pre_push_squash.py` - Tests for pre-push verification

Run tests:
```bash
cd tools/claude-plugins/tommymorgan
python3 -m pytest
```

## Requirements

**Python 3.8+** for hooks

**Python Dependencies:**
- `Pillow (PIL)` - Required for automatic image resizing

**Optional CLI tools for browser testing:**
- `agent-browser` — Required for browser-based testing agents (install: `npm install -g @vercel-labs/agent-browser`)
- `playwright-cli` — Required only for video demo recording (install: `npm install -g @playwright/cli@latest`)
- `chrome-devtools-mcp` — Optional, for deep performance profiling (Lighthouse, memory snapshots)

See `testing/README.md` for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Contributing

This is part of the tommymorgan personal marketplace. Suggestions welcome via GitHub issues.

## License

MIT License - See LICENSE file for details

## Repository

- **GitHub**: https://github.com/tommymorgan/claude-plugins
- **Issues**: https://github.com/tommymorgan/claude-plugins/issues
- **Plugin Directory**: `tommymorgan/`
