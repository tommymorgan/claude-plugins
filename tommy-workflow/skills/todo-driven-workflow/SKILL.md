---
name: todo-driven-workflow
description: Use when creating structured todo files, tracking feature completion, or generating user-facing changelog entries
version: 1.0.0
---

# Todo-Driven Workflow

Maintain structured todo files for feature tracking with automatic changelog generation.

## When to Use This Skill

Use this skill when:
- Creating todo files for new features
- Breaking large features into tasks
- Tracking implementation progress
- Generating changelog entries
- Documenting feature completion

## Todo File Structure

### File Naming Convention

```
yyyymmdd-feature-slug.md
```

**Examples**:
- `20241212-user-authentication.md`
- `20241215-password-reset-flow.md`
- `20241220-api-rate-limiting.md`

**Date prefix**: Use implementation start date (YYYYMMDD format)
**Feature slug**: Kebab-case, descriptive, 2-4 words

### File Template

```markdown
# Feature: ${featureName}

**Created**: 2024-12-12
**Status**: In Progress
**Priority**: High

## Overview

${briefDescription}

## Acceptance Criteria

- [ ] ${criterion1}
- [ ] ${criterion2}
- [ ] ${criterion3}

## Implementation Tasks

### Task 1: ${taskName}
- **Status**: Pending
- **Files**: src/auth/AuthService.ts, src/api/login.ts
- **Estimated LoC**: ~50
- **Tests Required**: Unit tests for AuthService, integration test for login flow

### Task 2: ${taskName}
...

## Testing Status

- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Feature verified in localhost
- [ ] Zero console errors confirmed

## Files Changed

- src/auth/AuthService.ts - JWT authentication implementation
- tests/auth/AuthService.test.ts - Comprehensive auth tests

## Changelog Entry

Added JWT token authentication with secure refresh token mechanism.
Users can now maintain persistent sessions across devices.

## Notes

${additionalContext}
```

## Task Breakdown Guidelines

### Sizing Tasks for Context Windows

Break features to fit within context limits:

- **Small feature**: < 5 files, < 200 LoC → 1 task
- **Medium feature**: 5-10 files, 200-500 LoC → 2-3 tasks
- **Large feature**: > 10 files, > 500 LoC → 4+ tasks

**Each task ≤ 70% of context window** to leave buffer for:
- Error handling
- File reading
- Unexpected complexity

### Logical Task Boundaries

Split tasks by:
1. **Layer**: UI components, API endpoints, database, tests
2. **Dependencies**: Tasks that must complete before others
3. **Complexity**: Isolate complex logic into separate tasks
4. **Testability**: Group code that shares test scenarios

**Example breakdown**:
```
Large feature: "User Authentication System"

Task 1: Database schema and user model (~40% context)
Task 2: Authentication API endpoints (~50% context)
Task 3: Frontend login UI (~45% context)
Task 4: Integration tests and E2E tests (~60% context)
```

## Changelog Generation

### User-Facing Format (Default)

Focus on what users can now do:

✅ **Good** (user-facing):
```markdown
## [0.2.0] - 2024-12-12

### Added
- User authentication with JWT tokens and refresh token support
- Persistent sessions across devices with automatic token refresh
- Password reset flow with email verification

### Impact
Users can now securely sign in and maintain their sessions
without frequent re-authentication.
```

❌ **Bad** (too technical):
```markdown
## Changes
- Modified AuthService.ts line 45-67
- Added useAuth hook
- Updated LoginForm props interface
- Fixed type error in AuthContext
```

### Changelog Entry Guidelines

**Include**:
- What users can now do
- Business value delivered
- User-visible improvements
- Breaking changes affecting users

**Exclude**:
- Implementation details
- File-level changes
- Internal refactoring
- Developer-only improvements

**Format**: Use semantic versioning categories:
- **Added**: New features
- **Changed**: Changes to existing features
- **Deprecated**: Soon-to-be-removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

## Todo Status Tracking

Update task status as work progresses:

```markdown
### Task 1: Authentication Service
- **Status**: Completed ✅
- **Files**: src/auth/AuthService.ts
- **Actual LoC**: 48 (estimated: ~50)
- **Tests**: 8 tests, all passing

### Task 2: Login API Endpoint
- **Status**: In Progress 🔄
- **Files**: src/api/login.ts
- **Progress**: 70% complete
```

**Status values**:
- `Pending`: Not started
- `In Progress`: Currently working
- `Completed`: Finished and verified
- `Blocked`: Waiting on dependency
- `Skipped`: Not needed

## Moving to Changelog

When feature complete, extract high-level summary for changelog:

1. **Read todo file** to understand what was built
2. **Identify user impact**: What can users now do?
3. **Categorize change**: Added, Changed, Fixed, etc.
4. **Write summary**: 1-2 sentences, user-facing language
5. **Update changelog**: Add entry with proper version and date

**Preserve todo file**: Keep completed todos for project history.

## Integration with Workflow

### Created During
- **Phase 5**: After exploratory testing succeeds

### Updated Throughout
- Track task completion during implementation
- Update status as tests pass
- Document files changed
- Note any blockers or issues

### Used For
- Progress tracking during development
- Historical record of implementation
- Changelog generation
- Project documentation

## Best Practices

**DO**:
- ✅ Use date-prefixed filenames
- ✅ Break large features into manageable tasks
- ✅ Track progress with status updates
- ✅ Generate user-facing changelog entries
- ✅ Keep todos as project history

**DON'T**:
- ❌ Create todos without clear acceptance criteria
- ❌ Make tasks too large (>70% context)
- ❌ Write technical changelogs
- ❌ Delete completed todos
- ❌ Skip task breakdown for large features

## Success Criteria

Todo-driven workflow succeeds when:
- ✅ Todo file created with proper naming
- ✅ Tasks appropriately sized for context
- ✅ Acceptance criteria clearly defined
- ✅ Progress tracked throughout implementation
- ✅ Changelog entry is user-facing and clear
- ✅ Feature completion properly documented
