---
name: execute
description: Execute Tommy's complete development workflow with automated quality gates
argument-hint: "[feature-description]"
allowed-tools:
  - Task
  - Read
  - Write
  - Bash
  - TodoWrite
  - Grep
  - Glob
---

# Tommy Workflow Execution Command

Execute the complete quality-first development workflow for a feature.

## Purpose

Orchestrate Tommy's proven development workflow through intelligent agent coordination, replacing manual approval gates with automated validation while maintaining strict quality standards.

## Usage

When the user invokes this command with a feature description, orchestrate the following workflow:

```
/tommy-workflow:execute "Add user authentication"
```

## Workflow Sequence

### Phase 0: Brainstorming (Required First Step)

Use the Skill tool to invoke the brainstorming skill:

```
Skill("superpowers:brainstorm")
```

This refines the rough feature idea into a concrete, well-thought-out design through collaborative questioning. **Do not proceed** until brainstorming is complete and the design is clear.

### Phase 1: Plan Review

After brainstorming produces a detailed plan, invoke the code-reviewer agent using the Task tool:

```typescript
const reviewResult = await Task({
  subagent_type: "code-reviewer",
  prompt: `Review this implementation plan for quality, security, and best practices:

${plan}

Provide specific feedback on:
- Architecture and design decisions
- Potential security vulnerabilities
- Performance considerations
- Test coverage strategy
- Edge cases and error handling`
});
```

**Quality Gate**: If code-reviewer identifies critical issues, work with user to address them before proceeding.

### Phase 2: Test-First Development

Invoke the test-first-guide agent to ensure tests are written before implementation:

```typescript
const testGuideResult = await Task({
  subagent_type: "test-first-guide",
  prompt: `Guide test-first development for: ${featureName}

Ensure:
- Tests written before implementation code
- Tests validate behavior, not implementation details
- Test quality meets standards
- Red-green-refactor cycle followed`
});
```

**Quality Gate**: Block implementation until test quality is validated.

### Phase 3: Implementation

Guide the user through implementation:
1. Reference the test-driven-development skill for TDD principles
2. User implements feature to pass tests
3. Monitor for quality and adherence to plan

### Phase 4: Exploratory Testing

After implementation, invoke exploratory-tester to validate in localhost:

```typescript
const testResult = await Task({
  subagent_type: "exploratory-tester",
  prompt: `Verify this feature works correctly in localhost:

Feature: ${featureName}
Acceptance Criteria: ${criteria}

Validate:
- Feature works as specified
- Zero console errors
- All user flows function correctly
- Performance is acceptable
- No regressions in existing features`
});
```

**Bug Reporting**: If exploratory testing finds bugs in other monorepo libraries:
1. Check setting `reportBugsToLibrary` (default: true)
2. If enabled, identify the library path
3. Write or append to `<library-root>/BUGS.md`:
   ```markdown
   ## [Date] Bug Found During Testing of ${featureName}

   **Context**: Testing ${featureName} in ${projectName}
   **Issue**: [Description of bug]
   **Impact**: [How it affects this feature]
   **Steps to Reproduce**: [Clear reproduction steps]
   **Expected**: [What should happen]
   **Actual**: [What actually happens]
   ```

**Quality Gate**: Feature must pass exploratory testing with zero console errors.

### Phase 5: Todo Tracking

Invoke todo-manager agent to track completion:

```typescript
const todoResult = await Task({
  subagent_type: "todo-manager",
  prompt: `Create structured todo and changelog entry for completed feature:

Feature: ${featureName}
Files Changed: ${changedFiles}
Tests Added: ${testFiles}
Status: Completed and verified`
});
```

The agent creates:
- **Todo file**: `${todoLocation}/yyyymmdd-feature-name.md`
- **Changelog entry**: High-level, user-facing summary in CHANGELOG.md

### Phase 6: Commit Formatting

Invoke git-commit-formatter agent to create conventional commit:

```typescript
const commitResult = await Task({
  subagent_type: "git-commit-formatter",
  prompt: `Generate conventional commit message for this feature:

Feature: ${featureName}
Changed Files: ${changedFiles}
Change Summary: ${summary}`
});
```

The agent generates a conventional commit message with:
- Auto-detected type and scope
- Clear subject line
- Detailed body explaining what and why
- Footer with references

**Final Step**: If `autoCommit: true` in settings, create the commit. Otherwise, display the formatted commit message for user to review and commit manually.

## Progress Reporting

Provide real-time updates as each phase completes:

```
🔄 Phase 0/6: Brainstorming design...
✅ Phase 0 Complete: Design refined and approved

🔄 Phase 1/6: Code review in progress...
✅ Phase 1 Complete: Plan approved with minor suggestions

🔄 Phase 2/6: Validating test quality...
✅ Phase 2 Complete: Tests validated (5 tests, all behavior-focused)

🔄 Phase 3/6: Implementation guided...
✅ Phase 3 Complete: Feature implemented

🔄 Phase 4/6: Exploratory testing...
⚠️  Bug found in shared-ui library (reported to ../shared-ui/BUGS.md)
✅ Phase 4 Complete: Feature verified in localhost

🔄 Phase 5/6: Updating todo and changelog...
✅ Phase 5 Complete: Todo created (20241212-user-auth.md)

🔄 Phase 6/6: Formatting commit...
✅ Phase 6 Complete: Commit message ready

✅ Workflow Complete!
```

## Error Handling

### Agent Failure Recovery

If any agent fails:
1. Report the specific failure with details
2. Provide guidance on how to fix
3. Ask user if ready to retry the phase
4. Re-invoke the failed agent after fixes
5. Continue workflow when phase passes

### Settings Loading

Read settings with cascading precedence:
1. Try project-level: `.claude/tommy-workflow.local.md`
2. Try user-level: `~/.claude/tommy-workflow.local.md`
3. Fall back to defaults if neither exists

Parse YAML frontmatter and merge settings appropriately.

## Best Practices

- **Always start with brainstorming**: Never skip Phase 0
- **Respect quality gates**: Don't proceed on agent failures
- **Real-time feedback**: Keep user informed of progress
- **Graceful degradation**: If dependencies missing, provide clear installation guidance
- **Settings validation**: Validate settings values and provide helpful errors

## Related Skills

- `workflow-orchestration`: Deep dive into workflow patterns
- `test-driven-development`: TDD principles and practices
- `quality-gates`: Validation criteria for each phase
