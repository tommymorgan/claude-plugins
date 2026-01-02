---
name: tommymorgan:generate-docs
description: Generate user or developer documentation from living .feature files
argument-hint: "[user|dev|both] [project-path]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
---

# Generate Documentation from Living Specifications

Generate user documentation, developer documentation, or both from living .feature files.

## Usage

```
/tommymorgan:generate-docs user
/tommymorgan:generate-docs dev
/tommymorgan:generate-docs both [project-path]
```

## What This Does

**User Documentation** (@user scenarios only):
- Filters scenarios tagged @user
- Converts Gherkin to readable prose
- Excludes all technical implementation details
- Creates user-friendly guide

**Developer Documentation** (@technical scenarios):
- Filters scenarios tagged @technical
- Includes implementation requirements
- Shows expected system behavior
- Documents technical specifications

**Evolutionary Updates**:
- Preserves existing introduction and non-scenario content
- Updates only changed scenarios
- Maintains documentation voice and style
- Keeps custom examples and diagrams

## Process

```bash
cd $PROJECT_PATH

# Generate user docs
python3 tools/claude-plugins/tommymorgan/migration/commands/doc_generator.py generate specs/ docs/user-guide.md --tags @user

# Generate developer docs
python3 tools/claude-plugins/tommymorgan/migration/commands/doc_generator.py generate specs/ docs/technical-spec.md --tags @technical
```

## Output

**User Documentation** (docs/user-guide.md):
```markdown
# User Guide

## Introduction
(Preserved from existing docs)

## Authentication

### Logging In
User logs in successfully: i am on the login page, i enter valid credentials, i am redirected to dashboard.

### Resetting Password
User resets forgotten password: i click forgot password, i enter my email, i receive reset link.
```

**Developer Documentation** (docs/technical-spec.md):
```markdown
# Technical Specification

## Authentication API

### JWT Token Generation
JWT token generation: user authenticates successfully, auth service processes request, jwt token is issued with user claims, token expires in 24 hours.
```

## Benefits

- **Always accurate**: Generated from living specs (source of truth)
- **No duplication**: One source for both user and dev docs
- **Test-aligned**: Docs match what tests verify
- **Evolutionary**: Preserves manual content while updating scenarios
- **Accessible**: Generates semantic HTML when needed

## When to Use

- After implementing new features (living specs updated)
- Before releases (refresh documentation)
- When onboarding new team members
- To verify docs match current functionality
