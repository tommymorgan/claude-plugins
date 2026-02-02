# Feature: Self-Contained SDLC Plugin

**Created**: 2026-02-01
**Goal**: Remove external plugin dependencies while expanding code review capabilities

## User Requirements

<!-- DONE -->
Scenario: User reviews feature files without a plan
  Given I have existing .feature files in my project
  When I run /review-features features/
  Then I receive expert panel recommendations on my scenarios

<!-- DONE -->
Scenario: User reviews a single feature file
  Given I have a feature file at features/auth.feature
  When I run /review-features features/auth.feature
  Then I receive expert panel recommendations for that file

<!-- DONE -->
Scenario: User reviews features matching a pattern
  Given I have multiple feature files in features/
  When I run /review-features "features/user-*.feature"
  Then I receive expert panel recommendations for matching files

<!-- DONE -->
Scenario: User reviews scenarios in a plan file
  Given I have a plan at plans/2026-02-01-auth.md with Gherkin scenarios
  When I run /review-features plans/2026-02-01-auth.md
  Then I receive expert panel recommendations for those scenarios

<!-- DONE -->
Scenario: Plan creation uses internal brainstorming
  Given I want to create a new feature plan
  When I run /tommymorgan:plan
  Then brainstorming works without requiring superpowers plugin

<!-- DONE -->
Scenario: Code review gate catches quality issues
  Given I have implemented a scenario with code quality issues
  When the code review gate runs during /work
  Then I receive feedback from all 6 review perspectives
  And I see which specific issues block approval

<!-- DONE -->
Scenario: Code review gate approves clean code
  Given I have implemented a scenario following best practices
  When the code review gate runs during /work
  Then all 6 reviewers approve
  And work continues to the next scenario

## Technical Specifications

<!-- DONE -->
Scenario: review-features command detects input type
  Given the command receives an argument
  When the argument ends in .feature
  Then it processes as a feature file
  When the argument ends in .md
  Then it extracts Gherkin from the plan file
  When the argument is a directory
  Then it processes all .feature files in that directory
  When the argument contains *
  Then it processes files matching the glob pattern

<!-- DONE -->
Scenario: Expert panel filters by content not section
  Given a feature file with mixed scenario types
  When the expert panel reviews the scenarios
  Then experts filter relevance by detected keywords
  And no section headers are required

<!-- DONE -->
Scenario: Living specs use features/ directory
  Given a project with Gherkin specifications
  When /plan reconciles with living specs
  Then it looks in <project>/features/*.feature
  And it creates features/ directory if needed

<!-- DONE -->
Scenario: Brainstorming skill exists internally
  Given the tommymorgan plugin is installed
  When /plan invokes brainstorming
  Then it uses tommymorgan:brainstorming skill
  And no external plugin is required

<!-- DONE -->
Scenario: Six code review agents exist
  Given the tommymorgan plugin is installed
  When /work runs the code review gate
  Then it invokes tommymorgan:code-reviewer
  And it invokes tommymorgan:comment-analyzer
  And it invokes tommymorgan:test-analyzer
  And it invokes tommymorgan:silent-failure-hunter
  And it invokes tommymorgan:type-design-analyzer
  And it invokes tommymorgan:code-simplifier

<!-- DONE -->
Scenario: Code review gate aggregates results
  Given the 6 review agents have completed
  When aggregating results
  Then APPROVED requires all 6 agents to approve
  And NEEDS_CHANGES shows all flagged issues from all agents
  And issues include confidence scores 0-100

<!-- DONE -->
Scenario: Internal agent references are consistent
  Given any command or skill in the plugin
  When it references an internal agent
  Then it uses the tommymorgan: prefix
  And no external plugin prefixes are used

## Notes

### Design Decisions

**Directory convention**: `features/` for living specs aligns with Cucumber community standard. Plans remain in `plans/`.

**Expert filtering**: Experts filter by content keywords (api, hook, ui, database) rather than section headers. This enables reviewing standalone .feature files that have no User Requirements/Technical Specifications split.

**6 review agents**: Internalizing all 6 from pr-review-toolkit (not just code-reviewer) provides comprehensive review coverage. Running all 6 in parallel during the code review gate catches more issues earlier.

**Agent naming**: Renamed `pr-test-analyzer` to `test-analyzer` since the functionality applies to any code changes, not just PRs.

### File Changes

**New files**:
- `planning/commands/review-features.md`
- `planning/skills/brainstorming/SKILL.md`
- `review/agents/code-reviewer.md`
- `review/agents/comment-analyzer.md`
- `review/agents/test-analyzer.md`
- `review/agents/silent-failure-hunter.md`
- `review/agents/type-design-analyzer.md`
- `review/agents/code-simplifier.md`

**Modified files**:
- `planning/commands/plan.md`
- `planning/commands/review-plan.md`
- `planning/commands/work.md`
- `planning/skills/tdd-execution/SKILL.md`
- `testing/commands/test.md`

**Renamed**:
- `specs/` → `features/`

### Dependencies Removed

| Was | Now |
|-----|-----|
| `superpowers:brainstorming` | `tommymorgan:brainstorming` |
| `pr-review-toolkit:code-reviewer` | `tommymorgan:code-reviewer` (+ 5 more) |
| `root-cause-analysis:root-cause-analyzer` | `tommymorgan:root-cause-analyzer` |
| `exploratory-tester:*` | `tommymorgan:*` |
