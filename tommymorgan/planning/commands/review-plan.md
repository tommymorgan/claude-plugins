---
name: tommymorgan:review-plan
description: Independent plan review with context-aware domain experts providing prioritized recommendations
argument-hint: "<path/to/plan.md>"
allowed-tools:
  - Read
  - Write
  - Bash
---

# Review Plan with Expert Panel

Conduct comprehensive plan review using 7 domain experts. Experts debate recommendations and provide context-aware, prioritized feedback.

## Workflow

### Step 1: Load and Analyze Plan

Read the plan file from the argument:
```
$ARGUMENTS
```

If no argument provided, find plan using same logic as `/tommymorgan:status`.

Parse the plan to extract:
- Goal and Created date
- User Requirements section
- Technical Specifications section
- TODO/DONE scenario counts
- Plan context (detect keywords: API, hook, CLI, database, UI, etc.)

### Step 2: Detect Plan Context

Scan plan content for keywords to categorize the plan type:

**Keywords → Categories:**
- `api, endpoint, http, rest, jwt` → backend_service
- `hook, bash, cli, git push, pre-push` → hook
- `web, ui, page, component, dashboard, form` → ui_component
- `database, schema, migration, table, postgres` → database_migration

Plans may have multiple categories (e.g., full-stack = backend + ui + database).

Store detected categories - experts will use this to filter relevance.

### Step 3: Simulate Expert Reviews

Invoke 7 domain experts to review the plan. Each expert:
1. Reviews their relevant section (User Requirements or Technical Specifications)
2. Considers detected plan context
3. Provides recommendations with priority (Critical/High/Medium)
4. Self-filters based on relevance to context

**Expert Panel:**

#### 1. Marty Cagan (Product Strategy)
- **Focus**: User Requirements section
- **Reviews for**: User outcomes vs implementation details, product value, user scenarios
- **Flags**: Technical details leaking into user scenarios
- **Output**: Product-focused recommendations

#### 2. Dave Farley (Continuous Delivery)
- **Focus**: Both sections
- **Reviews for**: Testability, automation, CD anti-patterns (manual gates, approval steps)
- **Flags**: Deployment blockers, manual processes
- **Output**: Automation and deployability recommendations

#### 3. OWASP Security Expert
- **Focus**: Technical Specifications
- **Context-aware filtering**:
  - If context = "hook" (not "api"): Focus on command injection, input validation, path validation
  - If context = "hook" (not "api"): Skip API auth/authz, rate limiting, CORS
  - Other experts validate relevance
- **Output**: Security recommendations relevant to plan context

#### 4. Jakob Nielsen (Usability)
- **Focus**: User Requirements
- **Reviews for**: User experience, clarity, error messaging
- **Flags**: Multiple prompts, unclear errors, UX anti-patterns
- **Output**: Usability improvements

#### 5. Martin Kleppmann (Distributed Systems)
- **Focus**: Technical Specifications
- **Context-aware filtering**:
  - If context = "cli_tool" or "hook" (not "data_intensive_system"): Acknowledge limited applicability
  - Other experts flag if scalability recommendations are overkill
  - Adjust to relevant performance concerns only
- **Output**: Performance recommendations appropriate to scale

#### 6. Eric Evans (Domain-Driven Design)
- **Focus**: Both sections
- **Reviews for**: Domain modeling, ubiquitous language consistency
- **Flags**: Mismatched terminology, unclear domain concepts
- **Output**: Domain model improvements

#### 7. Google SRE Expert
- **Focus**: Technical Specifications
- **Context-aware filtering**:
  - If context = "hook" (not "production_service"): Minimal observability needs
  - Other experts flag when monitoring/alerting is excessive
  - Adjust to: basic logging, error handling only
  - Skip: metrics, dashboards, alerting, SLOs
- **Output**: Operational recommendations appropriate to context

### Step 4: Simulate Expert Debates

When experts have conflicting recommendations:

1. **Present disagreement**: Expert A states position with reasoning
2. **Counter-argument**: Expert B presents alternative view
3. **Other experts weigh in**: Additional perspectives from relevant experts
4. **Reach consensus**: Document agreed-upon approach with rationale

**Example Debate Structure:**
```
**Debate: Stop Hook Blocking**

Farley: "Blocking stop violates CD principles - creates manual gates"
Cagan: "This is internal quality control, not deployment blocking"
Evans: "The domain is work session completion, not deployment pipeline"

**Consensus**: Acceptable with override mechanism (TOMMYMORGAN_ALLOW_INCOMPLETE_STOP)
**Reasoning**: Internal quality gate with escape hatch balances discipline and flexibility
```

### Step 5: Generate Prioritized Recommendations

Group all expert recommendations by priority:

**Critical Issues**: Must address before implementation
**High Priority**: Strongly recommended improvements
**Medium Priority**: Nice-to-have enhancements

Each recommendation includes:
- Expert name
- Specific scenario references
- Reasoning
- Suggested improvement
- Priority level

### Step 6: Output Structured Review

Generate markdown-formatted review:

```markdown
# Plan Review: <plan filename>

## Summary
- **Plan Type**: <detected contexts>
- **Goal**: <extracted goal>
- **Scenarios**: <total> total (<user_req> User Requirements, <tech_spec> Technical Specifications)
- **Completion**: <done_count>/<total> (<percentage>% DONE)

## Critical Issues

### [Expert Name] <Issue Title>
**Scenario Reference**: <which scenario(s)>

<Description of issue>

**Recommendation**: <specific suggestion>

**Reasoning**: <why this matters>

---

## High Priority

### [Expert Name] <Issue Title>
...

---

## Medium Priority

### [Expert Name] <Issue Title>
...

---

## Expert Debates & Consensus

### <Debate Topic>

**Disagreement**:
- [Expert A]: <position>
- [Expert B]: <counter-position>
- [Expert C]: <additional perspective>

**Consensus Reached**: <agreed approach>

**Reasoning**: <why this approach was chosen>

---

## Recommendations Summary

**Total Recommendations**: <count>
- Critical: <count>
- High Priority: <count>
- Medium Priority: <count>

**Next Steps**:
1. Address Critical issues before implementation
2. Consider High Priority improvements
3. Evaluate Medium Priority enhancements based on time/scope
4. Re-run `/tommymorgan:review-plan` after updates to verify improvements
```

### Step 7: Performance Budget

Complete all expert reviews and output within **30 seconds**.

Provide progress feedback during execution:
```
Analyzing plan context...
Invoking Marty Cagan review...
Invoking Dave Farley review...
Simulating expert debates...
Generating prioritized recommendations...
```

If timeout approached, gracefully complete with partial review and note which experts didn't finish.

## Important Notes

- **Context-awareness is critical**: Experts must self-filter based on plan type
- **Other experts validate**: If one expert suggests something irrelevant, others flag it
- **Debates add value**: Show reasoning when experts disagree, not just final answer
- **Prioritization helps**: User should know what to tackle first
- **This is advisory**: User manually applies recommendations, not automatic
- **Re-runnable**: User can update plan and re-run to verify improvements
- **Focus on outcomes**: Experts should reference specific scenarios and suggest concrete improvements
