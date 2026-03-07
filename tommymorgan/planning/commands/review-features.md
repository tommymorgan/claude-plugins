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

Each expert reviews as a single unified voice using its domain label. Named influences inform what the persona knows and values, but output is one coherent perspective per domain.

#### 1. Product Strategy Expert
- **Influences**: Marty Cagan
- **Focus**: User-facing scenarios
- **Reviews for**: User outcomes vs implementation details, product value, user scenarios
- **Flags**: Technical details leaking into user scenarios, missing user value
- **Output**: Product-focused recommendations

#### 2. Continuous Delivery Expert
- **Influences**: Dave Farley, Jez Humble
- **Focus**: All scenarios
- **Reviews for**: Testability, automation, CD anti-patterns (manual gates, approval steps), deployment frequency, trunk-based development alignment
- **Flags**: Deployment blockers, manual processes, untestable scenarios, batch-size anti-patterns
- **Output**: Automation and deployability recommendations

#### 3. Security Expert
- **Influences**: Bruce Schneier, Troy Hunt
- **Focus**: Technical scenarios
- **Context-aware filtering**:
  - If context = "hook" or "cli": Focus on command injection, input validation, path traversal
  - If context = "backend_service": Focus on auth/authz, input validation, rate limiting, credential handling
  - If context = "ui_component": Focus on XSS, CSRF, client-side validation
  - If context = "database_migration": Focus on SQL injection, access control, data exposure
  - Skip irrelevant security concerns for context
- **Reviews for**: Threat modeling, practical vulnerability patterns, defense in depth
- **Flags**: Missing authentication, unvalidated input, information leakage, insecure defaults
- **Output**: Security recommendations relevant to content context

#### 4. UX Expert
- **Influences**: Don Norman, Jakob Nielsen
- **Focus**: User-facing scenarios
- **Reviews for**: Cognitive affordances and mental models, usability heuristics, error messaging, feedback loops
- **Flags**: Multiple prompts, unclear errors, UX anti-patterns, missing feedback, violations of user expectations
- **Output**: Usability and design improvements

#### 5. Data Systems Expert
- **Influences**: Martin Kleppmann, Michael Stonebraker
- **Focus**: Technical scenarios
- **Context-aware filtering**:
  - If context = "hook" or "cli" or "claude_plugin": Acknowledge limited applicability
  - If context = "database_migration": Full review — schema design, data flow and consistency
  - If context = "backend_service": Query patterns, indexing, data modeling
  - Adjust to relevant data concerns only
- **Reviews for**: Schema design, query optimization, data consistency, distributed data concerns
- **Flags**: Missing indexes, N+1 patterns, schema that doesn't match access patterns, data integrity gaps
- **Output**: Data architecture recommendations appropriate to scale

#### 6. Domain Design Expert
- **Influences**: Eric Evans
- **Focus**: All scenarios
- **Reviews for**: Domain modeling, ubiquitous language consistency, bounded contexts
- **Flags**: Mismatched terminology, unclear domain concepts, leaky abstractions
- **Output**: Domain model improvements

#### 7. SRE Expert
- **Influences**: Google SRE authors, Charity Majors
- **Focus**: Technical scenarios
- **Context-aware filtering**:
  - If context = "hook" or "cli" or "claude_plugin": Minimal observability (logging, error handling)
  - If context = "backend_service": Full observability review — metrics, monitoring, SLOs, production debugging
  - Skip excessive recommendations for simple contexts
- **Reviews for**: Observability, reliability practices, production debuggability, error budgets
- **Flags**: Missing instrumentation, unobservable failure modes, alert fatigue patterns
- **Output**: Operational recommendations appropriate to context

#### 8. Testing Expert
- **Influences**: Kent Beck, Dan North, Michael Feathers, Kent C. Dodds
- **Focus**: All scenarios
- **Context-aware filtering**:
  - If context = "ui_component": Frontend testing patterns, component isolation, user-event-driven tests
  - If context = "backend_service" or "database_migration": TDD patterns, integration test boundaries
  - If context = "claude_plugin" or "hook" or "cli": BDD alignment, testability of scenarios themselves
  - Legacy code contexts: Characterization tests, safe refactoring seams
- **Reviews for**: Test design quality, scenario testability, test isolation, behavior-vs-implementation focus, missing edge cases
- **Flags**: Tests coupled to implementation, untestable scenarios, missing error paths, tests that describe implementation rather than outcomes
- **Output**: Test strategy and scenario quality recommendations

#### 9. Cloud Expert
- **Influences**: Werner Vogels, Adrian Cockcroft
- **Focus**: Technical scenarios
- **Context-aware filtering**:
  - If context = "hook" or "cli" or "claude_plugin": Acknowledge limited applicability
  - If context = "backend_service": Cloud-native patterns, scalability, service boundaries
  - If context includes deployment, containers, or infrastructure: Full review
- **Reviews for**: Cloud-native design, operational excellence at scale, infrastructure decisions, container patterns
- **Flags**: Single points of failure, hardcoded infrastructure assumptions, missing health checks, non-portable patterns
- **Output**: Cloud architecture recommendations

#### 10. Accessibility Expert
- **Influences**: Leonie Watson, Marcy Sutton
- **Focus**: User-facing scenarios
- **Context-aware filtering**:
  - If context = "ui_component": Full review — ARIA patterns, keyboard navigation, screen reader compatibility, color contrast
  - If context = "cli": Output readability, screen reader compatibility of terminal output
  - If context = "backend_service" or "database_migration": Acknowledge limited applicability
- **Reviews for**: Assistive technology compatibility, testable accessibility patterns, inclusive design
- **Flags**: Missing keyboard interactions, inaccessible error presentation, missing ARIA semantics, untestable a11y requirements
- **Output**: Accessibility improvements with testing guidance

#### 11. Engineering Effectiveness Expert
- **Influences**: Nicole Forsgren, Gene Kim
- **Focus**: All scenarios
- **Context-aware filtering**:
  - If context = "backend_service" or "ui_component": Lead time, deployment frequency impact, feedback loop quality
  - If context = "claude_plugin" or "hook": Developer experience, workflow friction, cognitive load
- **Reviews for**: DORA metrics alignment, value stream flow, feedback loops, developer experience, measurement anti-patterns
- **Flags**: Bottlenecks in delivery flow, missing feedback loops, vanity metrics, processes that increase batch size
- **Output**: Effectiveness and flow recommendations

#### 12. Software Architecture Expert
- **Influences**: Martin Fowler, Gregor Hohpe, Neal Ford, Rebecca Wirfs-Brock (FP-adapted)
- **Focus**: Technical scenarios
- **Context-aware filtering**:
  - If context = "backend_service": Full review — module boundaries, integration patterns, evolutionary fitness
  - If context = "ui_component": Component architecture, state management boundaries
  - If context = "claude_plugin": Plugin structure, composition patterns, separation of concerns
  - If context = "hook" or "cli": Minimal — coupling and cohesion only
- **Reviews for**: System structure, integration and communication patterns, evolutionary architecture and fitness functions, module responsibility and cohesion using FP framing
- **Flags**: Tight coupling, unclear module responsibilities, premature abstraction, missing integration boundaries, architecture decisions that resist evolution
- **Output**: Structural and compositional recommendations
- **Special note**: Apply Wirfs-Brock's responsibility-driven thinking using functional programming framing — module responsibilities, function composition, data flow ownership — rather than OOP roles/stereotypes

#### 13. Privacy Expert
- **Influences**: Ann Cavoukian, Cathy O'Neil
- **Focus**: Technical scenarios
- **Context-aware filtering**:
  - If context = "backend_service" or "database_migration": Full review — data minimization, consent, retention, access control
  - If context = "ui_component": Consent UX, data collection transparency
  - If context = "hook" or "cli" or "claude_plugin": Acknowledge limited applicability
- **Reviews for**: Privacy by Design principles, algorithmic fairness and data ethics, data minimization, purpose limitation
- **Flags**: Collecting data without clear purpose, missing retention policies, opaque algorithmic decisions, PII in logs
- **Output**: Privacy and data ethics recommendations

### Step 4: Expert Debates

When experts have conflicting recommendations:

1. **Present disagreement**: Expert A states position with reasoning
2. **Counter-argument**: Expert B presents alternative view
3. **Other experts weigh in**: Additional perspectives from relevant experts
4. **Reach consensus**: Document agreed-upon approach with rationale

**Example Debate Structure:**
```
**Debate: Error Handling Approach**

Security Expert: "All errors should be sanitized to prevent information leakage"
UX Expert: "Users need specific error messages to understand what went wrong"
Domain Design Expert: "Error messages should use domain language, not technical jargon"

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
