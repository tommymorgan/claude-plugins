---
name: conventional-commits
description: Use when formatting git commit messages, determining commit type and scope, or ensuring commits follow conventional commits specification
version: 1.0.0
---

# Conventional Commits

Format git commit messages following the conventional commits specification for consistent, semantic version control.

## When to Use This Skill

Use this skill when:
- Formatting commit messages
- Determining commit type from changes
- Auto-detecting scope from file paths
- Ensuring commit message quality
- Generating release notes from commits

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

Determines the nature of the change:

- **feat**: New feature or functionality
- **fix**: Bug fix
- **docs**: Documentation changes only
- **style**: Code style/formatting (no logic change)
- **refactor**: Code restructuring (no functional change)
- **test**: Adding or updating tests
- **chore**: Build tasks, dependency updates
- **perf**: Performance improvements
- **ci**: CI/CD configuration changes
- **revert**: Reverts a previous commit

### Scope

Indicates what part of codebase changed:

**Auto-detection rules**:
- Single package: Use package name (`auth`, `api`, `web`)
- Single feature: Use feature name (`dashboard`, `login`)
- Config files: Use `config`
- Test files only: Use `test`
- CI files: Use `ci`
- Multiple areas: Use feature name

**Examples**:
```
feat(auth): add JWT token support
fix(api): resolve race condition
docs(readme): update installation steps
chore(deps): upgrade React to v18
```

### Subject

Clear, concise description:

**Rules**:
- Present tense, imperative mood ("add" not "added")
- Lowercase after colon
- No period at end
- Max 72 characters
- Be specific

✅ **Good**:
```
feat(auth): add JWT token refresh mechanism
fix(dashboard): resolve loading spinner timing
```

❌ **Bad**:
```
feat(auth): Added some authentication stuff.
fix: fixed bug
```

### Body

Explain what and why (optional but recommended):

**Guidelines**:
- Blank line after subject
- Explain what changed and why
- Wrap at 72 characters
- Focus on motivation, not mechanics

**Example**:
```
feat(auth): add JWT token refresh mechanism

Implement token refresh to maintain sessions without requiring
frequent re-authentication.

Refresh tokens expire after 30 days while access tokens last
1 hour, balancing security with user experience. Uses HTTP-only
cookies to prevent XSS attacks.
```

### Footer

Reference issues and note breaking changes:

**Format**:
```
Closes #234
Refs #567

BREAKING CHANGE: Auth tokens now expire after 1 hour instead
of 24 hours. Update client code to handle refresh tokens.
```

## Complete Examples

### New Feature
```
feat(payment): add Stripe payment processing

Integrate Stripe for credit card payments with support for
one-time purchases and subscription billing.

Includes webhook handlers for payment events and automatic
invoice generation. PCI compliance maintained by using Stripe
Elements for card input.

Closes #456
```

### Bug Fix
```
fix(api): prevent race condition in user updates

Wrap user update operations in database transaction to prevent
lost updates when multiple requests modify the same user
simultaneously.

Adds optimistic locking with version field to detect conflicts.

Fixes #789
```

### Documentation
```
docs(api): add endpoint documentation for v2 API

Document all v2 API endpoints with request/response examples,
authentication requirements, and error codes.

Includes OpenAPI specification for automated client generation.
```

### Breaking Change
```
feat(api): migrate to REST from GraphQL

Replace GraphQL API with RESTful endpoints for better caching
and simpler client integration.

BREAKING CHANGE: GraphQL endpoint /graphql removed. Clients
must migrate to REST endpoints. See migration guide at
docs/api-migration.md.

Closes #123
```

## Best Practices

**DO**:
- ✅ Use conventional commits format consistently
- ✅ Auto-detect type and scope when possible
- ✅ Write clear, specific subject lines
- ✅ Explain why in the body
- ✅ Reference related issues
- ✅ Document breaking changes

**DON'T**:
- ❌ Use past tense ("added", "fixed")
- ❌ Be vague ("update stuff", "fix bug")
- ❌ Exceed character limits
- ❌ Skip the body for complex changes
- ❌ Forget to reference issues
- ❌ Ignore breaking changes

## Success Criteria

Commit message succeeds when:
- ✅ Follows conventional commits format
- ✅ Type accurately reflects change
- ✅ Scope correctly auto-detected
- ✅ Subject is clear and specific
- ✅ Body explains what and why
- ✅ Footer includes relevant references
- ✅ Breaking changes documented
