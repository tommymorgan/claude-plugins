---
name: tommymorgan:review-features
description: Review Gherkin scenarios with context-aware domain experts
argument-hint: "<path/to/file.feature|plan.md|directory|glob>"
allowed-tools:
  - Read
  - Glob
  - Grep
  - AskUserQuestion
---

# Review Features with Expert Panel

Review any Gherkin scenarios using a panel of domain experts. Accepts feature files, plan files, directories, or glob patterns.

## Workflow

### Step 1: Detect Input Type and Load Scenarios

Parse the argument to determine input type:
```
$ARGUMENTS
```

**Input detection:**
- Ends in `.feature` → single feature file
- Ends in `.md` → plan file (extract Gherkin scenarios)
- Is a directory (no extension, exists as dir) → all `.feature` files in directory
- Contains `*` → glob pattern for `.feature` files

**If no argument provided:**
1. Check for `features/` directory in current project
2. If exists, use `features/*.feature`
3. Otherwise, error: "No input provided. Specify a .feature file, plan file, directory, or glob pattern."

**Load scenarios based on input type:**

For `.feature` files:
- Read file content
- Extract all `Scenario:` and `Scenario Outline:` blocks
- Preserve Feature context (Feature name, Background if present)

For `.md` plan files:
- Read file content
- Extract Gherkin scenarios from User Requirements and Technical Specifications sections
- Scenarios are blocks starting with `Scenario:` after `<!-- TODO -->` or `<!-- DONE -->` markers

For directories:
- Find all `.feature` files in directory (non-recursive)
- Load scenarios from each file

For glob patterns:
- Expand glob to matching `.feature` files
- Load scenarios from each file

### Step 2: Detect Context from Content

Scan scenario content for keywords to categorize the context:

**Keywords → Categories:**
- `api, endpoint, http, rest, jwt, request, response` → backend_service
- `hook, bash, cli, git, pre-push, pre-commit, shell` → hook
- `web, ui, page, component, dashboard, form, button, click` → ui_component
- `database, schema, migration, table, postgres, sql, query` → database_migration
- `plugin, command, skill, agent, claude` → claude_plugin

Content may have multiple categories.

Store detected categories - experts will use this to filter relevance.

### Step 3: Expert Panel Review

Invoke the domain experts below to review the scenarios. Each expert:
1. Reviews scenarios relevant to their expertise
2. Considers detected content context
3. Provides recommendations with priority (Critical/High/Medium)
4. Self-filters based on relevance to context

**Expert Panel:**

#### 1. Marty Cagan (Product Strategy)
- **Focus**: User-facing scenarios
- **Reviews for**: User outcomes vs implementation details, product value, user scenarios
- **Flags**: Technical details leaking into user scenarios, missing user value
- **Output**: Product-focused recommendations

#### 2. Dave Farley (Continuous Delivery)
- **Focus**: All scenarios
- **Reviews for**: Testability, automation, CD anti-patterns (manual gates, approval steps)
- **Flags**: Deployment blockers, manual processes, untestable scenarios
- **Output**: Automation and deployability recommendations

#### 3. OWASP Security Expert
- **Focus**: Technical scenarios
- **Context-aware filtering**:
  - If context = "hook" or "cli": Focus on command injection, input validation, path traversal
  - If context = "backend_service": Focus on auth/authz, input validation, rate limiting
  - If context = "ui_component": Focus on XSS, CSRF, client-side validation
  - Skip irrelevant security concerns for context
- **Output**: Security recommendations relevant to content context

#### 4. Jakob Nielsen (Usability)
- **Focus**: User-facing scenarios
- **Reviews for**: User experience, clarity, error messaging, feedback
- **Flags**: Multiple prompts, unclear errors, UX anti-patterns, missing feedback
- **Output**: Usability improvements

#### 5. Martin Kleppmann (Data-Intensive Systems)
- **Focus**: Technical scenarios
- **Context-aware filtering**:
  - If context = "hook" or "cli" or "claude_plugin": Acknowledge limited applicability
  - If context = "database_migration" or "backend_service": Full review
  - Adjust to relevant performance concerns only
- **Output**: Performance recommendations appropriate to scale

#### 6. Eric Evans (Domain-Driven Design)
- **Focus**: All scenarios
- **Reviews for**: Domain modeling, ubiquitous language consistency, bounded contexts
- **Flags**: Mismatched terminology, unclear domain concepts, leaky abstractions
- **Output**: Domain model improvements

#### 7. Google SRE Expert
- **Focus**: Technical scenarios
- **Context-aware filtering**:
  - If context = "hook" or "cli" or "claude_plugin": Minimal observability (logging, error handling)
  - If context = "backend_service": Full observability review (metrics, monitoring, SLOs)
  - Skip excessive recommendations for simple contexts
- **Output**: Operational recommendations appropriate to context

### Step 4: Expert Debates

When experts have conflicting recommendations:

1. **Present disagreement**: Expert A states position with reasoning
2. **Counter-argument**: Expert B presents alternative view
3. **Other experts weigh in**: Additional perspectives from relevant experts
4. **Reach consensus**: Document agreed-upon approach with rationale

**Example Debate Structure:**
```
**Debate: Error Handling Approach**

OWASP: "All errors should be sanitized to prevent information leakage"
Nielsen: "Users need specific error messages to understand what went wrong"
Evans: "Error messages should use domain language, not technical jargon"

**Consensus**: Show user-friendly domain-specific errors; log technical details server-side
**Reasoning**: Balances security (no stack traces) with usability (actionable feedback)
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

Generate the review and present recommendations incrementally to the user.

**When called from the plan command**, use the incremental presentation mode:

**Critical issues — one at a time:**

For each Critical issue, present it individually using AskUserQuestion:

```
[Expert Name]: <Issue Title>
Scenario: <scenario name>

<Description of issue>

Recommendation: <specific suggestion>
Reasoning: <why this matters>

Options:
- Accept — Apply this recommendation
- Modify — Apply with changes
- Reject — Keep as-is
```

Apply accepted/modified changes to the scenarios immediately before showing the next issue.

**High Priority — user chooses review style:**

After all Critical issues are resolved, present the count and ask:
```
There are N High Priority recommendations.

Options:
- One at a time — Review and decide on each individually
- All at once — Show all, then apply accepted changes
- Skip — Trust the experts, accept all
```

**Medium Priority — user chooses review style:**

Same pattern as High Priority:
```
There are N Medium Priority recommendations.

Options:
- One at a time — Review and decide on each individually
- All at once — Show all, then apply accepted changes
- Skip — Defer to future work
```

**When called standalone** (not from the plan command), output the full structured review:

```markdown
# Feature Review: <source description>

## Summary
- **Source**: <file(s) reviewed>
- **Context**: <detected categories>
- **Scenarios**: <count> scenarios reviewed

## Critical Issues

### [Expert Name] <Issue Title>
**Scenario**: <scenario name>

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
3. Evaluate Medium Priority enhancements based on scope
```

### Step 7: Structure Output

Present progress through the review:
- Which source was loaded
- Which context was detected
- Which experts reviewed
- Summary of recommendations

## Important Notes

- **Context detection is automatic**: No section headers required
- **Experts self-filter**: Each expert only comments on relevant scenarios
- **Debates show reasoning**: When experts disagree, document the resolution
- **Prioritization helps**: Users know what to tackle first
- **Interactive when called from plan command**: Critical issues presented one at a time; High/Medium offer review style choice
- **Full output when called standalone**: Complete structured review for manual application
- **Works on any Gherkin**: Plans, feature files, directories, or globs
