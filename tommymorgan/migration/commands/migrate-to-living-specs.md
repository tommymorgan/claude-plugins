---
name: tommymorgan:migrate-to-living-specs
description: One-time migration to create living .feature files from historical plans
argument-hint: "[project-path]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
---

# Migrate Historical Plans to Living Specifications

One-time migration that creates living .feature files from historical plan files.

## Usage

```
/tommymorgan:migrate-to-living-specs [project-path]
```

If no path provided, uses current project (inferred from working directory).

## What This Does

1. **Scans plans/** directory for historical plan files
2. **Extracts Gherkin scenarios** from User Requirements and Technical Specifications
3. **Groups scenarios by feature** area using semantic similarity
4. **Tags scenarios** appropriately (@user, @technical)
5. **Creates .feature files** in specs/ directory
6. **Reports progress** with success/failure counts

## Process

```bash
cd $PROJECT_PATH

# Run migration tool
python3 tools/claude-plugins/tommymorgan/migration/commands/migrate.py .

# Results will be in specs/ directory
ls specs/*.feature
```

## Output

Creates `.feature` files in `<project>/specs/` directory:

```
specs/
  authentication.feature
  user-management.feature
  analytics.feature
```

Each .feature file contains:
```gherkin
Feature: <Feature Name>

  @user
  Scenario: User-facing behavior
    Given user context
    When user action
    Then user outcome

  @technical
  Scenario: Technical requirement
    Given system state
    When technical action
    Then technical outcome
```

## Summary Report

After completion, shows:
```
Migration complete!

Processed: 15 plans
Successes: 12
Failures: 3
Created: 5 .feature files

Errors:
- plan-old.md: No scenarios found
- plan-broken.md: Parse error
- plan-incomplete.md: No Gherkin blocks

Check specs/ directory for living specifications.
```

## When to Use

**Run this ONCE** to bootstrap living documentation from historical plans.

After migration:
- New plans will reference existing living specs (interactive reconciliation)
- Work tool will automatically update living specs
- Never run migration again (living specs are maintained going forward)

## Important Notes

- Historical plans remain unchanged (valuable record)
- Semantic similarity groups related scenarios (0.8 threshold)
- Processes in batches for memory efficiency
- Continues on errors, reports all issues at end
- Scenarios below 0.8 similarity flagged for manual review
