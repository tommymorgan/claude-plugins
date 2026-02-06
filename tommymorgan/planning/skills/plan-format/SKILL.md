---
name: plan-format
description: This skill should be used when creating plan files, writing Gherkin requirements, or parsing plan file structure. Provides the plan file template and format specifications.
version: 0.2.0
---

# Plan File Format

Specification for plan files used by the tommymorgan plugin. Plan files capture feature requirements as Gherkin scenarios with TODO/DONE tracking.

## Plan File Purpose

Plan files serve as the single source of truth for feature development:
- Capture requirements as Gherkin scenarios (User Requirements + Technical Specifications)
- Track progress via `<!-- TODO -->` / `<!-- DONE -->` comment markers
- Enable autonomous TDD execution via the work command
- Scenarios ARE the plan — no separate task lists

## File Location

Plan files live in the project's plans directory:

```
<project>/plans/YYYY-MM-DD-<slug>.md
```

Where:
- `<project>` is the project path (e.g., `apps/web`, `libs/shared`, `tools/cli`)
- `YYYY-MM-DD` is the creation date
- `<slug>` is a kebab-case version of the feature name

Example: `apps/web/plans/2025-12-15-user-authentication.md`

## Plan File Template

```markdown
# Feature: <Title>

**Created**: YYYY-MM-DD
**Goal**: <One-sentence description of user-facing outcome>

## User Requirements

<!-- TODO -->
# Living: <project>/features/<file>.feature::<scenario-name>
# Action: creates|replaces|extends|removes|deprecates
# Status: TODO
# Living updated: NO
Scenario: <user-focused behavior>
  Given <user context>
  When <user action>
  Then <user outcome>

## Technical Specifications

<!-- TODO -->
# Living: <project>/features/<file>.feature::<scenario-name>
# Action: creates|replaces|extends|removes|deprecates
# Status: TODO
# Living updated: NO
Scenario: <technical requirement>
  Given <system state>
  When <technical action>
  Then <technical outcome>

## Affected Documentation

- [ ] Update <path> — <brief description of needed update>

## Notes

<Design decisions, constraints, and context for future sessions>
```

## Section Specifications

### Header Section

**Required fields:**
- `**Created**`: Date in YYYY-MM-DD format
- `**Goal**`: Single sentence describing user-facing outcome

### User Requirements Section

Language/framework agnostic Gherkin scenarios describing user-facing behavior.

**Rules:**
- No mention of specific frameworks, databases, or technologies
- Describe outcomes, not implementation
- Focus on what the user experiences

### Technical Specifications Section

Implementation-specific Gherkin scenarios with actual technology versions.

**Rules:**
- Reference actual project technologies and versions
- Describe system behavior and technical constraints
- Include integration points, data formats, API contracts

### Scenario Metadata

Each scenario has metadata comments:

```gherkin
# Living: <project>/features/<file>.feature::<scenario-name>
# Action: creates|replaces|extends|removes|deprecates
# Status: TODO
# Living updated: NO
```

**Living**: Path to the corresponding living specification file, or `none (initial implementation)` for new features.

**Action**: Relationship to existing living specs:
- `creates` — New, independent scenario
- `replaces` — Completely replaces an existing scenario
- `extends` — Adds to an existing scenario
- `removes` — Deletes an existing scenario from the living spec
- `deprecates` — Marks an old scenario as obsolete

**Status**: `TODO` or `DONE` — matches the `<!-- TODO -->` / `<!-- DONE -->` HTML comment marker.

**Living updated**: `NO`, `YES`, or `N/A` — whether the living spec file has been updated.

### Affected Documentation Section

Markdown checklist of documentation files affected by the planned changes. Appears after Technical Specifications and before Notes.

```markdown
## Affected Documentation

- [ ] Update README.md — describe new feature in usage section
- [ ] Update CLAUDE.md — document new commands
```

If no documentation is affected:
```markdown
## Affected Documentation

No existing documentation is affected by these changes.
```

### Notes Section

Preserve context for future sessions:
- Design decisions and rationale
- Constraints and dependencies
- Implementation approach chosen
- Rejected alternatives and why

## Progress Tracking

Progress is tracked via HTML comment markers above each scenario:

- `<!-- TODO -->` — Scenario not yet implemented
- `<!-- DONE -->` — Scenario implemented and verified

The `status` and `work` commands parse these markers to determine progress.

## Gherkin Writing Guidelines

**Coverage requirements:**
- Happy path scenarios (successful operations)
- Error cases (invalid input, failures)
- Edge cases (boundaries, empty states)
- Security considerations (authorization, validation)
- Accessibility (table stakes)
- Performance (table stakes)

**Writing tips:**
- Use concrete values in examples ("user@example.com" not "an email")
- One behavior per scenario
- Focus on user-observable outcomes
- Avoid implementation details in User Requirements scenarios

## Validation Rules

**Plan file validation:**
- [ ] Has title starting with `# Feature:`
- [ ] Has Created and Goal header fields
- [ ] Has User Requirements section with Gherkin scenarios
- [ ] Has Technical Specifications section with Gherkin scenarios
- [ ] Has Affected Documentation section
- [ ] Each scenario has `<!-- TODO -->` or `<!-- DONE -->` marker
- [ ] Each scenario has Living/Action/Status/Living updated metadata
- [ ] User Requirements are language/framework agnostic
- [ ] Technical Specifications use actual project versions
