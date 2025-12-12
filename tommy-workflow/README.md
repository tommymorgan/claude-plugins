# Tommy Workflow Plugin

Automated workflow orchestration for quality-first development. Enforces best practices through intelligent agent coordination: brainstorming → code review → test-first development → exploratory testing → todo tracking → conventional commits.

## Features

- **Automated Quality Gates**: Agents replace manual approval with automated validation
- **Test-First Development**: Validates test quality before allowing implementation
- **Exploratory Testing**: Verifies features work in localhost with zero console errors
- **Todo-Driven Tracking**: Maintains structured todos with automatic changelog generation
- **Conventional Commits**: Auto-formats commit messages from changed files
- **Multi-Language Support**: Works with top 10 programming languages
- **Bug Reporting**: Automatically reports bugs found in monorepo libraries

## Installation

### Prerequisites

This plugin requires the following plugins to be installed:

```bash
# Install required plugins
cc plugins install superpowers
cc plugins install code-reviewer
cc plugins install exploratory-tester
cc plugins install root-cause-analysis
```

### Install Tommy Workflow

```bash
# From marketplace (when published)
cc plugins install tommy-workflow

# Or install locally
cc plugins install --local /path/to/tommy-workflow
```

## Usage

### Quick Start

```bash
# Start a new feature with full workflow orchestration
/tommy-workflow:execute "Add user authentication with JWT tokens"
```

The workflow automatically:
1. ✅ **Brainstorms** the feature design (superpowers:brainstorm)
2. ✅ **Reviews** implementation plan (code-reviewer)
3. ✅ **Enforces** test-first development
4. ✅ **Validates** feature works in localhost (exploratory-tester)
5. ✅ **Tracks** progress in structured todos
6. ✅ **Formats** conventional commit message

### Configuration

#### User-Level Defaults

Create `~/.claude/tommy-workflow.local.md`:

```yaml
---
strictQualityGates: true
reportBugsToLibrary: true
todoLocation: "."
changelogLocation: "CHANGELOG.md"
changelogFormat: "user-facing"
autoCommit: false
---

# Global workflow settings
```

#### Project-Level Overrides

Create `.claude/tommy-workflow.local.md` in your project:

```yaml
---
strictQualityGates: false  # More relaxed for this project
todoLocation: "docs/todos"
---

# Project-specific settings
```

### Settings Reference

| Setting | Default | Description |
|---------|---------|-------------|
| `strictQualityGates` | `true` | Enforce strict quality validation between phases |
| `reportBugsToLibrary` | `true` | Write BUGS.md in library root when bugs found during testing |
| `todoLocation` | `"."` | Where to create todo files (relative to project root) |
| `changelogLocation` | `"CHANGELOG.md"` | Changelog file location |
| `changelogFormat` | `"user-facing"` | Format style (user-facing vs detailed) |
| `autoCommit` | `false` | Automatically commit after workflow completion |

## Workflow Phases

### Phase 0: Brainstorming (superpowers:brainstorm)
Refines rough feature idea into concrete design through collaborative questioning.

### Phase 1: Plan Review (code-reviewer)
Reviews implementation plan for quality, security, and best practices.

### Phase 2: Test-First Development
Validates test quality before allowing implementation:
- Tests describe behavior, not implementation
- Test titles are meaningful
- Red-green-refactor cycle followed

**Supported frameworks** (auto-detected):
- JavaScript/TypeScript: Jest, Vitest, Mocha, Jasmine
- Python: pytest, unittest, nose
- Java: JUnit, TestNG
- Go: testing package
- Rust: cargo test
- Ruby: RSpec, Minitest
- PHP: PHPUnit
- C#: NUnit, xUnit
- C++: Google Test, Catch2

### Phase 3: Implementation
User implements feature guided by TDD skill and test-first-guide agent.

### Phase 4: Exploratory Testing (exploratory-tester)
Validates feature in localhost:
- Feature works as specified
- Zero console errors
- All acceptance criteria met

### Phase 5: Todo Tracking
Creates structured todo file:
- Filename: `yyyymmdd-feature-name.md`
- Tracks implementation progress
- Auto-generates changelog entry

### Phase 6: Commit Formatting
Generates conventional commit:
- Auto-detects scope from changed files
- Formats type(scope): subject
- Includes detailed body and footer

## Error Handling

### Automatic Rework
If any agent fails, the workflow:
1. Reports the failure with details
2. Allows user to fix issues
3. Re-runs the failed phase
4. Continues when validation passes

### Bug Reporting
When `reportBugsToLibrary: true` (default), bugs found in other monorepo libraries during testing are reported to `BUGS.md` in that library's root directory.

## Examples

### Example: New Feature
```
/tommy-workflow:execute "Add password reset flow"

✓ Brainstormed design with 3 user flows
✓ Plan reviewed by code-reviewer (approved with minor suggestions)
✓ Tests written and validated (5 tests, all behavior-focused)
✓ Implementation complete
✓ Exploratory testing passed (localhost verified, 0 console errors)
✓ Todo created: 20241212-password-reset.md
✓ Commit formatted: feat(auth): add password reset flow
```

### Example: Bug Fix with Library Issue
```
/tommy-workflow:execute "Fix dashboard loading spinner"

✓ Brainstormed root cause analysis
✓ Plan reviewed and approved
✓ Tests written (regression test added)
⚠ Exploratory testing found bug in shared-ui library
  → Reported to: ../shared-ui/BUGS.md
✓ Todo updated with library bug reference
✓ Commit formatted: fix(dashboard): resolve loading spinner timing
```

## Development

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - See [LICENSE](./LICENSE) for details.

## Support

- Issues: https://github.com/tommy/tommy-workflow/issues
- Discussions: https://github.com/tommy/tommy-workflow/discussions
