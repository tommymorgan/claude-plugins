---
name: workflow-orchestration
description: Use when orchestrating multi-phase development workflows, coordinating specialized agents, or implementing quality-first development processes with automated gates
version: 1.0.0
---

# Workflow Orchestration

Orchestrate quality-first development workflows through intelligent agent coordination, replacing manual approval gates with automated validation while maintaining strict quality standards.

## When to Use This Skill

Use this skill when:
- Implementing features with multiple quality gates
- Coordinating specialized agents (code review, testing, etc.)
- Enforcing systematic development processes
- Need deterministic workflow execution
- Automating best practices enforcement

## Core Workflow Pattern

### The Six-Phase Quality-First Workflow

```
Phase 0: Brainstorming    → Refine idea into concrete design
Phase 1: Plan Review      → Validate architecture and approach
Phase 2: Test-First Dev   → Write and validate tests first
Phase 3: Implementation   → Build feature following TDD
Phase 4: Exploratory Test → Verify in localhost, zero errors
Phase 5: Todo & Changelog → Track completion, update docs
Phase 6: Commit Format    → Generate conventional commit
```

### Phase Execution Principles

**Sequential Execution**: Phases run in strict order, never skip or reorder.

**Quality Gates**: Each phase has entry and exit criteria that must be met.

**Auto-Proceed on Success**: If phase passes quality gate, automatically continue to next phase.

**Intelligent Rework on Failure**: If phase fails, invoke root-cause-analysis, allow fixes, then retry the phase.

**Real-Time Progress**: Report completion after each phase with clear status.

## Phase Details

### Phase 0: Brainstorming (superpowers:brainstorm)

**Purpose**: Transform rough feature idea into concrete, well-thought-out design.

**Invocation**:
```typescript
await Skill("superpowers:brainstorm");
```

**Entry Criteria**:
- User provided feature description
- Context is loaded and understood

**Exit Criteria**:
- Design is concrete and actionable
- User flows clearly defined
- Acceptance criteria established
- Technical approach specified

**Quality Gate**: Design must be sufficiently detailed for code review.

### Phase 1: Plan Review (code-reviewer)

**Purpose**: Validate implementation plan for quality, security, and best practices.

**Invocation**:
```typescript
const reviewResult = await Task({
  subagent_type: "code-reviewer",
  description: "Review implementation plan",
  prompt: `Review this implementation plan: ${plan}`
});
```

**Entry Criteria**:
- Detailed design from brainstorming
- Technical approach defined
- File changes identified

**Exit Criteria**:
- No critical architecture issues
- Security considerations addressed
- Performance implications understood
- Test strategy approved

**Quality Gate**: Code reviewer must approve plan or all critical issues resolved.

**Rework Trigger**: Critical issues found → Invoke root-cause-analysis → Fix → Re-review

### Phase 2: Test-First Development (test-first-guide)

**Purpose**: Ensure tests written before implementation, validate test quality.

**Invocation**:
```typescript
const testGuide = await Task({
  subagent_type: "test-first-guide",
  description: "Validate test quality",
  prompt: `Ensure tests written and validated for: ${feature}`
});
```

**Entry Criteria**:
- Implementation plan approved
- Test framework auto-discovered
- Acceptance criteria clear

**Exit Criteria**:
- Tests exist before implementation code
- Tests focus on behavior, not implementation
- Test titles are meaningful
- Tests can run and initially fail (red phase)
- Test quality meets standards

**Quality Gate**: All test quality checks pass (strict mode) or warnings only (relaxed mode).

**Rework Trigger**: Poor test quality → Guidance provided → Improve tests → Re-validate

### Phase 3: Implementation

**Purpose**: Build feature following TDD principles.

**Guidance**: Reference test-driven-development skill.

**Entry Criteria**:
- Tests written and validated
- Implementation plan clear
- Quality gates passed

**Exit Criteria**:
- Implementation makes tests pass (green phase)
- Code quality maintained
- No new console errors introduced

**Quality Gate**: All tests must pass, feature must work.

**Rework Trigger**: Tests still failing → Invoke root-cause-analysis → Debug → Fix → Retest

### Phase 4: Exploratory Testing (exploratory-tester)

**Purpose**: Verify feature works correctly in localhost environment.

**Invocation**:
```typescript
const testResult = await Task({
  subagent_type: "exploratory-tester",
  description: "Verify feature in localhost",
  prompt: `Verify feature works: ${feature}
Acceptance criteria: ${criteria}`
});
```

**Entry Criteria**:
- Implementation complete
- All tests passing
- Feature ready for validation

**Exit Criteria**:
- Feature works as specified
- Zero console errors (red or yellow)
- All user flows functional
- Performance acceptable
- No regressions

**Quality Gate**: Perfect localhost functionality with zero console errors.

**Rework Trigger**: Errors found → Invoke root-cause-analysis → Fix root cause → Retest

**Bug Reporting** (if `reportBugsToLibrary: true`):
When bugs found in other monorepo libraries during testing, create or append to `<library-root>/BUGS.md`:

```markdown
## [Date] Bug Found During ${feature} Testing

**Context**: Testing ${feature} in ${project}
**Library**: ${libraryName}
**Issue**: ${description}
**Impact**: ${impact}
**Reproduction**: ${steps}
**Expected**: ${expected}
**Actual**: ${actual}
```

### Phase 5: Todo and Changelog (todo-manager)

**Purpose**: Track completion and generate user-facing changelog.

**Invocation**:
```typescript
const todoResult = await Task({
  subagent_type: "todo-manager",
  description: "Update todo and changelog",
  prompt: `Create todo and changelog for: ${feature}`
});
```

**Entry Criteria**:
- Feature verified in localhost
- All quality gates passed
- Ready to document completion

**Exit Criteria**:
- Todo file created: `yyyymmdd-feature-name.md`
- Changelog entry generated (user-facing format)
- Completion tracked

**Quality Gate**: Todo and changelog must be updated.

### Phase 6: Commit Formatting (git-commit-formatter)

**Purpose**: Generate properly formatted conventional commit.

**Invocation**:
```typescript
const commit = await Task({
  subagent_type: "git-commit-formatter",
  description: "Format commit message",
  prompt: `Generate conventional commit for: ${feature}`
});
```

**Entry Criteria**:
- All phases complete
- Changes ready to commit
- Todo and changelog updated

**Exit Criteria**:
- Conventional commit message generated
- Type and scope auto-detected
- Body explains what and why
- Commit created (if autoCommit: true)

**Quality Gate**: Message follows conventional commits specification.

## Settings Management

### Cascading Settings

Load settings with precedence order (later overrides earlier):

1. **Built-in defaults**: Hardcoded sensible defaults
2. **User-level**: `~/.claude/tommy-workflow.local.md` (global)
3. **Project-level**: `.claude/tommy-workflow.local.md` (project-specific)

**Implementation**:
```typescript
const defaults = {
  strictQualityGates: true,
  reportBugsToLibrary: true,
  todoLocation: ".",
  changelogLocation: "CHANGELOG.md",
  changelogFormat: "user-facing",
  autoCommit: false
};

const userSettings = loadYamlFrontmatter("~/.claude/tommy-workflow.local.md");
const projectSettings = loadYamlFrontmatter("./.claude/tommy-workflow.local.md");

const finalSettings = {
  ...defaults,
  ...userSettings,
  ...projectSettings
};
```

### Available Settings

- **strictQualityGates** (boolean, default: true): Enforce strict validation or allow warnings
- **reportBugsToLibrary** (boolean, default: true): Write BUGS.md in library roots
- **todoLocation** (string, default: "."): Where to create todo files
- **changelogLocation** (string, default: "CHANGELOG.md"): Changelog file path
- **changelogFormat** (string, default: "user-facing"): Entry format style
- **autoCommit** (boolean, default: false): Auto-create commit or manual

## Progress Reporting

Provide real-time updates using consistent format:

```markdown
🔄 Phase 0/6: Brainstorming design...
✅ Phase 0 Complete: Design refined with 3 user flows identified

🔄 Phase 1/6: Code review in progress...
✅ Phase 1 Complete: Plan approved (minor suggestions addressed)

🔄 Phase 2/6: Validating test quality...
✅ Phase 2 Complete: 5 tests validated, all behavior-focused

🔄 Phase 3/6: Implementation guided...
✅ Phase 3 Complete: Feature implemented, tests passing

🔄 Phase 4/6: Exploratory testing in localhost...
⚠️  Bug found in shared-ui library (reported to ../shared-ui/BUGS.md)
✅ Phase 4 Complete: Feature verified, zero console errors

🔄 Phase 5/6: Updating todo and changelog...
✅ Phase 5 Complete: Created 20241212-user-auth.md

🔄 Phase 6/6: Formatting commit message...
✅ Phase 6 Complete: Commit ready (feat(auth): add JWT authentication)

✅ WORKFLOW COMPLETE
```

## Error Recovery with Root Cause Analysis

### Never Speculate on Errors

When any agent encounters an error, failure, or unexpected behavior:

**NEVER**:
- Guess at the cause
- Try random fixes
- Chase red herrings
- Make assumptions

**ALWAYS**:
- Invoke root-cause-analysis agent
- Use systematic investigation
- Follow evidence
- Apply five-whys methodology

**Implementation**:
```typescript
// When agent fails
if (!agentResult.success) {
  const rootCause = await Task({
    subagent_type: "root-cause-analyzer",
    description: "Analyze failure root cause",
    prompt: `Systematic root cause analysis for:

Error: ${agentResult.error}
Context: ${phaseContext}
Agent: ${agentName}
Phase: ${phaseName}

Use five-whys to identify true root cause.
Avoid speculation.
Provide evidence-based analysis.`
  });

  // Report findings
  reportRootCause(rootCause);

  // Wait for user to fix root cause
  await waitForFixes();

  // Retry the failed phase
  return retryPhase(phaseName);
}
```

### Common Scenarios for Root Cause Analysis

**Test failures**:
```
Test fails → Don't guess why → Invoke root-cause-analysis → Identify actual issue → Fix → Retest
```

**Exploratory testing errors**:
```
Console error in localhost → Don't assume cause → Root cause analysis → Find source → Fix → Reverify
```

**Code review issues**:
```
Design flaw identified → Don't patch symptoms → Analyze root design problem → Redesign → Re-review
```

**Performance problems**:
```
Slow operation detected → Don't optimize randomly → Analyze bottleneck → Target fix → Retest
```

## Agent Coordination Patterns

### Deterministic Invocation

Use Task tool with explicit subagent_type for deterministic agent selection:

```typescript
// ✅ Deterministic - explicit agent
await Task({
  subagent_type: "code-reviewer",
  description: "Review plan",
  prompt: detailedPrompt
});

// ❌ Non-deterministic - Claude chooses
await Task({
  description: "Review this code", // Might pick wrong agent
  prompt: code
});
```

### Context Passing

Pass complete context to each agent:

```typescript
const context = {
  feature: featureName,
  plan: brainstormingOutput,
  criteria: acceptanceCriteria,
  constraints: technicalConstraints,
  settings: workflowSettings
};

const result = await Task({
  subagent_type: agentName,
  prompt: JSON.stringify(context, null, 2) + "\n\n" + specificInstructions
});
```

### Result Validation

Validate agent output before proceeding:

```typescript
if (!validateAgentResult(result)) {
  throw new Error(`Agent ${agentName} produced invalid output`);
}

if (result.qualityGate === 'FAILED') {
  return await handleQualityGateFailure(result);
}
```

## Quality Gate Implementation

### Strict vs Relaxed Modes

**Strict Mode** (`strictQualityGates: true`):
- Zero tolerance for quality issues
- Block on any failure
- Require perfect compliance
- No warnings allowed to proceed

**Relaxed Mode** (`strictQualityGates: false`):
- Warnings don't block progress
- Minor issues can be addressed later
- Focus on critical issues only
- Faster iteration

**Implementation**:
```typescript
function evaluateQualityGate(result, phase, settings) {
  const issues = result.issues || [];
  const critical = issues.filter(i => i.severity === 'critical');
  const warnings = issues.filter(i => i.severity === 'warning');

  if (critical.length > 0) {
    return {
      passed: false,
      reason: `${critical.length} critical issues found`,
      blocking: true
    };
  }

  if (settings.strictQualityGates && warnings.length > 0) {
    return {
      passed: false,
      reason: `${warnings.length} warnings in strict mode`,
      blocking: true
    };
  }

  return {
    passed: true,
    warnings: warnings.length
  };
}
```

## Workflow Variations

### Standard Feature Development
```
Brainstorm → Review → Test-First → Implement → Explore Test → Todo → Commit
```

### Bug Fix Workflow
```
Brainstorm (root cause) → Review → Test (regression) → Fix → Verify → Todo → Commit
```

### Refactoring Workflow
```
Brainstorm (strategy) → Review → Tests (existing) → Refactor → Verify → Todo → Commit
```

All variations follow same phase structure, adapted to task type.

## Best Practices

### Always Start with Brainstorming

Never skip Phase 0, even for seemingly simple tasks:
- Clarifies requirements
- Identifies edge cases
- Plans test strategy
- Considers alternatives

### Respect Quality Gates

Never proceed past a failed quality gate:
- Understand why it failed
- Fix the root cause (use root-cause-analysis)
- Re-validate the phase
- Only then continue

### Use Root Cause Analysis

When agents report errors or unexpected behavior:
- Invoke root-cause-analyzer immediately
- Don't speculate or guess
- Follow systematic investigation
- Fix root cause, not symptoms

### Provide Clear Progress Updates

Keep user informed with consistent format:
```
🔄 Phase X/6: [Action]...
✅ Phase X Complete: [Result]
```

Show:
- Current phase number and total
- What's happening now
- What was accomplished
- What's next

### Maintain Context Continuity

Pass relevant context from phase to phase:
- Brainstorming output → Plan review
- Plan → Test-first guide
- Tests → Implementation
- Implementation → Exploratory testing
- All → Todo manager and commit formatter

## Error Handling

### Agent Failures

When an agent fails:
1. **Capture** error details and context
2. **Analyze** using root-cause-analyzer agent
3. **Report** findings to user with actionable guidance
4. **Wait** for user to address root cause
5. **Retry** the failed phase
6. **Validate** quality gate now passes
7. **Continue** to next phase

### Dependency Missing

When required plugin not installed:
```markdown
❌ Phase ${X} Failed: Required plugin '${pluginName}' not installed

Install with: cc plugins install ${pluginName}

After installation, retry this workflow.
```

### Settings Invalid

When settings validation fails:
```markdown
⚠️  Invalid setting: ${settingName} = ${value}
Expected: ${expectedType}
Using default: ${defaultValue}
```

Continue with defaults, but warn user to fix settings.

## Progress Tracking

Use TodoWrite to track overall workflow:

```typescript
// Create workflow tracking todo
TodoWrite({
  todos: [
    { content: "Phase 0: Brainstorming", status: "pending" },
    { content: "Phase 1: Plan Review", status: "pending" },
    { content: "Phase 2: Test-First", status: "pending" },
    { content: "Phase 3: Implementation", status: "pending" },
    { content: "Phase 4: Exploratory Testing", status: "pending" },
    { content: "Phase 5: Todo & Changelog", status: "pending" },
    { content: "Phase 6: Commit Formatting", status: "pending" }
  ]
});

// Update as phases complete
updateTodoStatus(currentPhase, "completed");
updateTodoStatus(nextPhase, "in_progress");
```

## Final Summary

After all phases complete, provide comprehensive summary:

```markdown
## ✅ Workflow Complete: ${featureName}

**Phases Completed**: 6/6
**Time Elapsed**: ${duration}
**Status**: Success

### Changes Made
- **Files**: ${fileCount} changed
- **Tests**: ${testCount} created
- **LoC**: +${added} -${removed}

### Quality Validation
✅ Design reviewed and approved
✅ Test-first development followed
✅ Feature verified in localhost
✅ Zero console errors
✅ Todo and changelog updated

### Bugs Reported
${bugsReported > 0 ? `⚠️ ${bugsReported} bugs reported in:
${bugsList}` : "None"}

### Commit Message
${autoCommit ? "✅ Committed" : "📋 Ready to commit:"}
```
${commitMessage}
```

### Next Steps
${nextSteps}
```

## Integration with Related Skills

- **test-driven-development**: Deep dive into TDD principles
- **todo-driven-workflow**: Todo file structure and management
- **conventional-commits**: Commit message formatting rules
- **quality-gates**: Detailed criteria for each phase

## Success Metrics

Workflow succeeds when:
- ✅ All 6 phases completed
- ✅ All quality gates passed
- ✅ Feature works perfectly in localhost
- ✅ Tests comprehensive and high-quality
- ✅ Documentation updated
- ✅ Commit properly formatted
- ✅ User satisfied with result

## Common Pitfalls

### Skipping Brainstorming
**Problem**: Jumping straight to code without design
**Solution**: Always run Phase 0, even for "simple" tasks

### Ignoring Quality Gates
**Problem**: Proceeding despite failed validation
**Solution**: Respect quality gates, fix issues, retry phase

### Speculating on Errors
**Problem**: Guessing at error causes, chasing red herrings
**Solution**: Invoke root-cause-analyzer for systematic investigation

### Poor Test Quality
**Problem**: Tests that test implementation details
**Solution**: test-first-guide blocks until tests are behavior-focused

### Skipping Exploratory Testing
**Problem**: Feature "works" but has console errors
**Solution**: Phase 4 enforces zero console errors

## Workflow Customization

Adapt workflow based on task type:

**New Feature**: All 6 phases
**Bug Fix**: Emphasize root cause analysis in brainstorming
**Refactoring**: Ensure existing tests pass throughout
**Documentation**: Skip some phases, focus on clarity

While structure remains same, guidance and emphasis shift based on context.
