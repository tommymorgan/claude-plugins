---
name: tommymorgan:review-features
description: Review Gherkin scenarios with context-aware domain experts
argument-hint: "<path/to/file.feature|plan.md|directory|glob>"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Task
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

Dispatch a Task to the `tommymorgan:expert-panel` agent with:

- `subagent_type`: `tommymorgan:expert-panel`
- Prompt containing:
  1. All loaded scenarios, each formatted as a finding:
     - **Source**: "Scenario review"
     - **Location**: Scenario name and source file/section
     - **Context**: The full Gherkin text (Given/When/Then)
     - **Issue**: "Review this scenario for quality, completeness, and correctness"
     - **Suggestion**: (none — the panel generates recommendations)
  2. The detected content categories from Step 2
  3. The instruction: "Review each scenario from your domain perspective. For each issue found, provide a priority (Critical/High/Medium), the specific scenario reference, reasoning, and a suggested improvement. Debate any conflicts between experts."

The expert panel agent (defined in `review/agents/expert-panel.md`) handles expert selection, review, debates, and consensus internally.

### Step 4: Process Panel Output

Parse the expert panel's output and group recommendations by priority:

**Critical Issues**: Must address before implementation
**High Priority**: Strongly recommended improvements
**Medium Priority**: Nice-to-have enhancements

Each recommendation includes:
- Expert name
- Specific scenario references
- Reasoning
- Suggested improvement
- Priority level

### Step 5: Output Structured Review

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

### Step 6: Structure Output

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
