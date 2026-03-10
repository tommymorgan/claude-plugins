# Changelog

### v0.7.0 (2026-03-06)
- **Changed**: Expert panel expanded from 7 to 13 composite domain experts with named influences
- **Added**: Testing Expert, Cloud Expert, Accessibility Expert, Engineering Effectiveness Expert, Software Architecture Expert, and Privacy Expert
- **Changed**: Existing experts enriched with additional influences (e.g., Jez Humble added to Continuous Delivery, Don Norman added to UX)
- **Changed**: Brainstorming keyword routing table expanded from 5 rows to 11 for finer-grained expert matching
- **Changed**: Expert output uses domain labels instead of personal names
- **Added**: Context-aware self-filtering so experts acknowledge limited applicability rather than forcing irrelevant recommendations

### v0.6.0 (2026-02-28)
- **Changed**: Browser testing agents use agent-browser CLI instead of Playwright MCP tools for token-efficient browser automation
- **Added**: playwright-cli integration for video demo recording
- **Added**: Conditional chrome-devtools-mcp loading for deep performance profiling (Lighthouse, memory snapshots, performance tracing)
- **Added**: Shell safety guidelines for CLI command construction
- **Added**: Named session support for concurrent agent isolation
- **Added**: Pre-flight checks for CLI tool availability
- **Added**: `testing/README.md` documenting tooling choices and installation
- **Changed**: `references/playwright-mcp-tools.md` replaced with `references/agent-browser-cli.md`
- **Changed**: Performance metrics reference updated with two-tier profiling approach

### v0.5.0 (2026-02-06)
- **Added**: Technology Checkpoint step in plan command — scans project files and confirms undecided technology decisions
- **Added**: Section-level expert review during brainstorming Phase 3
- **Added**: Affected Documentation section in plan files
- **Added**: Incremental recommendation presentation in review-features (Critical one-at-a-time, High/Medium with review style choice)
- **Added**: REST API Guidelines skill
- **Added**: `claude_plugin` context detection category
- **Changed**: Plan format skill rewritten to match current scenario-based format
- **Changed**: Removed hardcoded expert count and aspirational performance timing from review-features

### v0.4.7 (2026-02-02)
- **Fixed**: Stop hook - `decision` field goes at top-level, not inside `hookSpecificOutput`

### v0.4.6 (2026-02-02)
- **Fixed**: Stop hook - omit `decision` field to allow stop (per official Claude Code docs); only `"block"` is valid

### v0.4.5 (2026-02-02)
- **Fixed**: Stop hook JSON schema - changed `stopDecision: "allow"` to `decision: "approve"` per Claude Code schema

### v0.4.4 (2026-02-02)
- **Fixed**: Updated all `specs/` references to `features/` (37 occurrences missed in v0.4.0)
- **Changed**: Living specification step is now MANDATORY by default, not conditional
- **Added**: Explicit verification commands for feature file creation
- **Added**: Living specs as 4th completion criteria (was 3, now 4)
- **Added**: Gate check that halts if .feature file not in commit

### v0.4.3 (2026-02-02)
- **Fixed**: hooks.json requires top-level `"hooks"` wrapper object (matches other plugins' format)

### v0.4.2 (2026-02-02)
- **Fixed**: hooks.json schema validation - Stop and UserPromptSubmit hooks now use correct nested structure

### v0.4.1 (2026-02-02)
- **Fixed**: Pre-push squash hook JSON output validation errors
  - `allow_command()` now exits cleanly without output (correct hook behavior)
  - `deny_command()` now includes required `hookEventName` field

### v0.4.0 (2026-02-01)
- **Added**: `/review-features` command for reviewing any Gherkin scenarios
- **Added**: Internal `brainstorming` skill (no longer requires superpowers plugin)
- **Added**: 6 code review agents (no longer requires pr-review-toolkit):
  - code-reviewer, comment-analyzer, test-analyzer
  - silent-failure-hunter, type-design-analyzer, code-simplifier
- **Changed**: Code review gate runs all 6 agents in parallel
- **Changed**: Living specs directory from `specs/` to `features/` (Cucumber convention)
- **Changed**: `/review-plan` is now a wrapper around `/review-features`
- **Removed**: All external plugin dependencies (fully self-contained)

### v0.3.0 (2026-01-01)
- **Added**: Built-in automatic image resizing (migrated from auto-resize-images)
- **Added**: Configuration support via `.claude/tommymorgan.local.md`
- Automatically resizes images >2000px before submission
- Conflict detection warns if old auto-resize-images plugin installed
- Configurable per-project (enabled by default)
- Transparent operation with clear feedback

### v0.2.2 (2026-01-01)
- **Removed**: Override mechanism for stop hook
- Stop hook now strictly enforces completion
- No `TOMMYMORGAN_ALLOW_INCOMPLETE_STOP` env var

### v0.2.0 (2026-01-01)
- **Added**: `/review-plan` command with 7 domain experts
- **Added**: Stop hook for work completion enforcement
- Expert review with context-aware filtering
- Expert debates for conflicting recommendations
- Prioritized recommendations (Critical/High/Medium)

### v0.1.0 (2025-12-31)
- **Added**: Pre-push squash verification hook
- **Added**: Post-push cleanup hook
