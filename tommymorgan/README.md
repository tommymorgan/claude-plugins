# tommymorgan

**Version**: 1.2.0
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

#### `/tommymorgan:review-plan <plan-file>`
Independent plan review with 7 domain experts providing context-aware, prioritized recommendations.

**Expert Panel**:
1. **Marty Cagan** (Product Strategy) - User outcomes vs implementation details
2. **Dave Farley** (Continuous Delivery) - Testability, automation, deployability
3. **OWASP Security Expert** - Security (context-aware filtering)
4. **Jakob Nielsen** (Usability) - User experience, clarity, error messaging
5. **Martin Kleppmann** (Distributed Systems) - Performance (context-aware)
6. **Eric Evans** (Domain-Driven Design) - Domain modeling, ubiquitous language
7. **Google SRE Expert** - Operations (context-aware filtering)

**Context-Aware Filtering**: Experts adjust recommendations based on plan type:
- Hook vs API vs UI vs Database
- CLI tool vs production service
- Simple tool vs data-intensive system

**Output**:
- Critical/High/Medium priority recommendations
- Expert debates and consensus for conflicts
- Specific scenario references
- Concrete improvement suggestions

**Performance**: Completes in <30 seconds

### Testing

#### `/tommymorgan:test`
Plan-aware exploratory testing.

Automatically selects testing strategy:
- **API testing**: REST/GraphQL endpoint validation
- **Browser testing**: Functional, visual, accessibility, performance
- **CLI testing**: Command validation, output correctness, exit codes

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
**Plugin**: tommymorgan
**Goal**: Add JWT-based authentication for API endpoints

## User Requirements

<!-- TODO -->
Scenario: User registers with email
  Given I am a new user
  When I POST to /api/auth/register with email and password
  Then I receive a 201 response with user ID
  And I receive a JWT access token

<!-- DONE -->
Scenario: User logs in with credentials
  Given I am a registered user
  When I POST to /api/auth/login with valid credentials
  Then I receive a JWT access token

## Technical Specifications

<!-- TODO -->
Scenario: JWT tokens expire after 7 days
  Given a user has a valid JWT token
  When 7 days have passed
  Then the token should be rejected as expired
  And API should return 401 Unauthorized

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
- `plan-format` - Gherkin plan structure and formatting
- `tdd-execution` - Red-Green-Refactor workflow
- `verification-sweep` - Test execution and validation
- `api-testing-patterns` - REST/GraphQL testing patterns
- `browser-testing-patterns` - Web UI testing with Playwright
- `cli-testing-patterns` - CLI tool testing patterns
- `five-whys-methodology` - Root cause analysis process

### Agents
- `api-explorer` - Autonomous API endpoint testing
- `browser-explorer` - Autonomous browser-based testing
- `cli-tester` - Autonomous CLI tool testing
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
- `planning/commands/test_review_plan.py` - 13 tests for plan parsing and context detection
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

**Recommended plugins** (not required):
- `pr-review-toolkit` - Additional code review agents
- `superpowers` - Enhanced skill system

## Changelog

### v1.2.0 (2026-01-01)
- **Added**: Built-in automatic image resizing (migrated from auto-resize-images)
- **Added**: Configuration support via `.claude/tommymorgan.local.md`
- Automatically resizes images >2000px before submission
- Conflict detection warns if old auto-resize-images plugin installed
- Configurable per-project (enabled by default)
- Transparent operation with clear feedback

### v1.1.1 (2026-01-01)
- **Removed**: Override mechanism for stop hook
- Stop hook now strictly enforces completion
- No `TOMMYMORGAN_ALLOW_INCOMPLETE_STOP` env var

### v1.1.0 (2026-01-01)
- **Added**: `/review-plan` command with 7 domain experts
- **Added**: Stop hook for work completion enforcement
- Expert review with context-aware filtering
- Expert debates for conflicting recommendations
- Prioritized recommendations (Critical/High/Medium)

### v1.0.2 (2025-12-31)
- **Added**: Pre-push squash verification hook
- **Added**: Post-push cleanup hook

## Contributing

This is part of the tommymorgan personal marketplace. Suggestions welcome via GitHub issues.

## License

MIT License - See LICENSE file for details

## Repository

- **GitHub**: https://github.com/tommymorgan/claude-plugins
- **Issues**: https://github.com/tommymorgan/claude-plugins/issues
- **Plugin Directory**: `tommymorgan/`
