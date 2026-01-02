---
name: tommymorgan:coverage-analysis
description: Analyze test coverage of living specification scenarios
argument-hint: "[project-path]"
allowed-tools:
  - Bash
  - Read
  - Glob
---

# Analyze Test Coverage of Living Specifications

Analyzes which scenarios in living .feature files have corresponding tests, identifying coverage gaps.

## Usage

```
/tommymorgan:coverage-analysis [project-path]
```

## What This Does

1. **Loads living specs** from specs/ directory
2. **Discovers test files** in project (test_*.py, *.test.js, etc.)
3. **Matches scenarios to tests** using fuzzy name matching
4. **Reports coverage percentage**
5. **Lists untested scenarios**

## Process

```bash
cd $PROJECT_PATH

python3 tools/claude-plugins/tommymorgan/migration/commands/doc_generator.py coverage specs/ .
```

## Output

```
Test Coverage Analysis

Total scenarios: 15
Tested: 10
Coverage: 66.7%

Scenarios without tests:
  ✗ User resets password (authentication.feature)
  ✗ Admin manages permissions (user-management.feature)
  ✗ Export analytics to CSV (analytics.feature)
  ✗ Bulk import test cases (test-management.feature)
  ✗ API rate limiting (api.feature)

Scenarios with tests:
  ✓ User logs in successfully (test_auth.py::test_user_login)
  ✓ User logs out (test_auth.py::test_user_logout)
  ✓ JWT token generation (test_auth.py::test_jwt_generation)
  ...
```

## Matching Algorithm

**Fuzzy matching** finds tests that likely correspond to scenarios:

- Converts scenario names to test naming conventions
- Searches test file content for scenario names
- Reports matches with test file names
- Flags scenarios with no matches

**Example matches**:
- "User logs in successfully" → test_user_login_successfully()
- "JWT token generation" → test_jwt_token_generation()
- "API returns 404 for missing resource" → test_api_404_missing_resource()

## Benefits

- **Identify gaps**: See which scenarios lack test coverage
- **Track progress**: Monitor coverage as features are implemented
- **Quality metric**: Quantify test completeness
- **Guide testing**: Prioritize writing tests for untested scenarios

## When to Use

- After implementing features (verify new scenarios are tested)
- Before releases (ensure adequate coverage)
- During code review (check test completeness)
- Sprint retrospectives (discuss coverage trends)

## Important Notes

- Uses fuzzy matching (may have false positives/negatives)
- Only analyzes scenario name matching (not step-level coverage)
- Requires test files follow naming conventions
- Manual review recommended for ambiguous matches
