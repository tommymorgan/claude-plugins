---
name: quality-gates
description: Use when validating phase transitions, enforcing quality standards, or determining if workflow can proceed to next phase
version: 1.0.0
---

# Quality Gates

Enforce strict quality standards at workflow phase transitions to ensure consistent, high-quality outcomes.

## When to Use This Skill

Use this skill when:
- Validating if a workflow phase can complete
- Determining if next phase can begin
- Enforcing quality standards
- Deciding between strict and relaxed validation
- Checking phase completion criteria

## Quality Gate Principles

### Core Concepts

**Quality Gate**: A checkpoint between phases that must pass before proceeding.

**Entry Criteria**: Conditions that must be met to begin a phase.

**Exit Criteria**: Conditions that must be met to complete a phase.

**Strict Mode**: Zero tolerance for issues - blocks on warnings.

**Relaxed Mode**: Warnings don't block - focus on critical issues only.

## Phase-Specific Quality Gates

### Phase 0: Brainstorming → Plan Review

**Exit Criteria**:
- ✅ Design is concrete and actionable
- ✅ User flows clearly defined
- ✅ Acceptance criteria established
- ✅ Technical approach specified
- ✅ File changes identified

**Strict Mode**: All details must be comprehensive
**Relaxed Mode**: Basic design sufficient

### Phase 1: Plan Review → Test-First Development

**Exit Criteria**:
- ✅ No critical architecture issues
- ✅ Security considerations addressed
- ✅ Performance implications understood
- ✅ Test strategy approved
- ✅ Edge cases identified

**Strict Mode**: Zero critical issues, all suggestions addressed
**Relaxed Mode**: Critical issues only, suggestions noted

### Phase 2: Test-First → Implementation

**Exit Criteria** (Most Strict):
- ✅ Tests exist before implementation code
- ✅ All tests focus on behavior (not implementation)
- ✅ Test titles are meaningful and clear
- ✅ Tests can run and initially fail (red phase)
- ✅ Test framework successfully detected
- ✅ Test quality validated

**Strict Mode**:
- Zero implementation-focused tests
- All titles must be crystal clear
- Perfect red-green-refactor setup

**Relaxed Mode**:
- Warnings for quality issues
- Minor improvements can come later
- Focus on behavior vs implementation

**BLOCKS IMPLEMENTATION**: This gate cannot be bypassed - tests must exist and meet standards.

### Phase 3: Implementation → Exploratory Testing

**Exit Criteria**:
- ✅ Implementation complete
- ✅ All tests passing (green phase)
- ✅ Code quality maintained
- ✅ No new linting errors
- ✅ Type checking passes

**Strict Mode**: Zero warnings, perfect code quality
**Relaxed Mode**: Critical errors only

### Phase 4: Exploratory Testing → Todo/Changelog

**Exit Criteria** (Most Strict):
- ✅ Feature works as specified
- ✅ **ZERO console errors** (red messages)
- ✅ **ZERO console warnings** (yellow messages)
- ✅ All user flows functional
- ✅ Performance acceptable
- ✅ No regressions in existing features

**Strict Mode**:
- Absolute zero tolerance for console messages
- Perfect functionality required
- All edge cases must work

**Relaxed Mode**:
- Console errors block, warnings acceptable
- Core functionality must work
- Edge cases can be addressed later

**BLOCKS COMPLETION**: Cannot proceed with console errors.

### Phase 5: Todo/Changelog → Commit

**Exit Criteria**:
- ✅ Todo file created with proper naming
- ✅ Acceptance criteria marked complete
- ✅ Changelog entry generated
- ✅ User-facing summary clear

**Strict Mode**: Comprehensive documentation
**Relaxed Mode**: Basic documentation sufficient

### Phase 6: Commit Formatting → Complete

**Exit Criteria**:
- ✅ Conventional commits format followed
- ✅ Type correctly detected
- ✅ Scope auto-detected or specified
- ✅ Subject clear and concise
- ✅ Body explains what and why

**Strict Mode**: Perfect formatting, comprehensive body
**Relaxed Mode**: Valid format, body optional for simple changes

## Quality Validation Functions

### Check Phase Completion

```typescript
function canCompletePhase(phase, result, settings) {
  const issues = identifyIssues(result);
  const critical = issues.filter(i => i.severity === 'critical');
  const warnings = issues.filter(i => i.severity === 'warning');

  // Critical issues always block
  if (critical.length > 0) {
    return {
      canProceed: false,
      reason: `${critical.length} critical issues must be resolved`,
      issues: critical
    };
  }

  // Warnings block in strict mode
  if (settings.strictQualityGates && warnings.length > 0) {
    return {
      canProceed: false,
      reason: `${warnings.length} warnings in strict mode`,
      issues: warnings
    };
  }

  return {
    canProceed: true,
    warnings: warnings
  };
}
```

## Strict vs Relaxed Mode

### When to Use Strict Mode (Default)

Use strict mode (`strictQualityGates: true`) when:
- Building production features
- High-stakes code changes
- Public-facing functionality
- Security-sensitive features
- Team learning/training

**Behavior**: Zero tolerance, blocks on any quality issue.

### When to Use Relaxed Mode

Use relaxed mode (`strictQualityGates: false`) when:
- Experimental features
- Rapid prototyping
- Internal tools
- Exploratory development
- Time-critical hotfixes

**Behavior**: Critical issues block, warnings noted but don't block.

## Zero-Tolerance Gates

Some criteria have **zero tolerance** regardless of mode:

1. **Tests must exist** before implementation (Phase 2)
2. **Console errors must be zero** in exploratory testing (Phase 4)
3. **Tests must pass** before completion (Phase 3)
4. **Critical security issues** must be addressed (Phase 1)

These cannot be bypassed even in relaxed mode.

## Integration with Workflow

Used throughout workflow to:
- Validate phase completion
- Determine if next phase can begin
- Apply strict or relaxed standards
- Report quality status
- Block or allow progression

## Best Practices

**DO**:
- ✅ Apply appropriate strictness based on context
- ✅ Clearly report why gates fail
- ✅ Provide actionable guidance to pass
- ✅ Respect zero-tolerance gates
- ✅ Document quality criteria

**DON'T**:
- ❌ Skip quality gates to save time
- ❌ Lower standards without reason
- ❌ Bypass zero-tolerance gates
- ❌ Ignore warnings in strict mode
- ❌ Proceed on critical failures

## Success Criteria

Quality gates succeed when:
- ✅ All phase exit criteria met
- ✅ Appropriate mode applied (strict/relaxed)
- ✅ Zero-tolerance gates never bypassed
- ✅ Clear pass/fail decision provided
- ✅ Actionable feedback on failures
