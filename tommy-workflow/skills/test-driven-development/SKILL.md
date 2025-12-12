---
name: test-driven-development
description: Use when implementing features with test-first approach, validating test quality, or following red-green-refactor cycle
version: 1.0.0
---

# Test-Driven Development

Follow strict test-first development practices to ensure high-quality, maintainable code with comprehensive test coverage.

## When to Use This Skill

Use this skill when:
- Implementing new features or functionality
- Writing tests before implementation code
- Validating test quality and focus
- Following red-green-refactor methodology
- Ensuring tests describe behavior, not implementation

## The Red-Green-Refactor Cycle

### Red Phase: Write Failing Test

Write a test that describes the desired behavior:

```typescript
// Test written FIRST, before implementation exists
it("should return 404 when user does not exist", async () => {
  const response = await api.getUser("nonexistent-id");
  expect(response.status).toBe(404);
  expect(response.error).toBe("User not found");
});
```

**Validation**: Run the test - it must FAIL because feature doesn't exist yet.

### Green Phase: Minimal Implementation

Write just enough code to make the test pass:

```typescript
// Minimal implementation
async function getUser(id: string) {
  const user = await db.findUser(id);
  if (!user) {
    return { status: 404, error: "User not found" };
  }
  return { status: 200, data: user };
}
```

**Validation**: Run tests - they should now PASS.

### Refactor Phase: Improve Code

Improve code quality while keeping tests green:

```typescript
// Refactored for clarity
async function getUser(id: string): Promise<UserResponse> {
  const user = await userRepository.findById(id);
  return user
    ? createSuccessResponse(user)
    : createNotFoundError("User not found");
}
```

**Validation**: Tests still PASS after refactoring.

## Test Quality Criteria

### 1. Tests Describe Behavior

**Focus on WHAT, not HOW**:

✅ **Good** (behavior-focused):
```typescript
it("should send welcome email after registration", async () => {
  await authService.register({ email: "user@example.com" });
  expect(emailsSent).toContainEqual(
    expect.objectContaining({ to: "user@example.com", subject: "Welcome" })
  );
});
```

❌ **Bad** (implementation-focused):
```typescript
it("should call emailService.send", async () => {
  await authService.register({ email: "user@example.com" });
  expect(emailService.send).toHaveBeenCalled();
});
```

### 2. Tests Are Implementation-Independent

**Ask**: "Could I rewrite this completely without changing tests?"

✅ **Good** (implementation-independent):
```typescript
it("should authenticate user with valid credentials", async () => {
  const result = await auth.login("user@test.com", "password123");
  expect(result.authenticated).toBe(true);
  expect(result.token).toBeDefined();
});
```

You could change from JWT to sessions without touching this test.

❌ **Bad** (implementation-coupled):
```typescript
it("should generate JWT token", async () => {
  const result = await auth.login("user@test.com", "password123");
  expect(result.token).toMatch(/^eyJ/); // Checks JWT format
});
```

This test breaks if you change from JWT to session tokens.

### 3. Meaningful Test Titles

Test titles must be clear enough that:
- Another developer understands the requirement
- Someone could implement feature from title alone
- Expected behavior is obvious

✅ **Good titles**:
```
"should return 404 when user does not exist"
"displays error message when form validation fails"
"sends welcome email after successful registration"
"prevents duplicate submissions with same request ID"
```

❌ **Bad titles**:
```
"should work"
"handles errors"
"user test"
"test login"
```

### 4. Single Responsibility

Each test validates ONE behavior:

✅ **Good** (single responsibility):
```typescript
it("should validate email format", () => {
  expect(validateEmail("invalid")).toBe(false);
});

it("should validate email length", () => {
  expect(validateEmail("a".repeat(300) + "@test.com")).toBe(false);
});
```

❌ **Bad** (multiple responsibilities):
```typescript
it("should validate email", () => {
  expect(validateEmail("invalid")).toBe(false);
  expect(validateEmail("a".repeat(300) + "@test.com")).toBe(false);
  expect(validateEmail("test@example.com")).toBe(true);
});
```

## Test Organization Patterns

### AAA Pattern (Arrange-Act-Assert)

Structure all tests clearly:

```typescript
it("should create user with valid data", async () => {
  // Arrange - Set up test data
  const userData = {
    email: "test@example.com",
    name: "Test User"
  };

  // Act - Execute the operation
  const result = await userService.create(userData);

  // Assert - Verify expectations
  expect(result.id).toBeDefined();
  expect(result.email).toBe("test@example.com");
});
```

### Test File Organization

Place tests close to code:

```
src/
  features/
    auth/
      AuthService.ts
      AuthService.test.ts      ← Next to implementation
```

Or in dedicated test directory:

```
src/features/auth/AuthService.ts
tests/unit/auth/AuthService.test.ts
```

## Common Test Smells

### Testing Implementation Details

```typescript
// ❌ Bad - tests internal state
expect(component.state.isLoading).toBe(false);

// ✅ Good - tests behavior
expect(screen.queryByText("Loading...")).not.toBeInTheDocument();
```

### Too Many Assertions

```typescript
// ❌ Bad - testing too much at once
it("should handle user workflow", () => {
  // 20 different assertions
});

// ✅ Good - focused tests
it("should create user", () => { /* ... */ });
it("should validate user data", () => { /* ... */ });
it("should send confirmation email", () => { /* ... */ });
```

### Brittle Selectors (Frontend)

```typescript
// ❌ Bad - fragile CSS selector
screen.querySelector(".btn.btn-primary:nth-child(2)");

// ✅ Good - semantic selector
screen.getByRole("button", { name: "Submit" });
```

## Integration with Workflow

Called during **Phase 2** (Test-First Development) to validate:
- Tests exist before implementation
- Test quality meets standards
- Red-green-refactor cycle followed
- Framework auto-detected
- Tests can run

Blocks **Phase 3** (Implementation) until quality gate passes.

## Best Practices Summary

**DO**:
- ✅ Write tests first, before any implementation
- ✅ Focus tests on behavior and outcomes
- ✅ Use meaningful, descriptive test titles
- ✅ Keep tests implementation-independent
- ✅ Follow AAA pattern for clarity
- ✅ Validate tests can run and fail initially

**DON'T**:
- ❌ Test implementation details
- ❌ Write tests after implementation
- ❌ Use vague or generic test names
- ❌ Couple tests to specific implementation
- ❌ Write tests that always pass
- ❌ Skip the red phase

## Success Criteria

Test-first development succeeds when:
- ✅ Tests written before implementation code
- ✅ All tests focus on behavior
- ✅ Test titles are meaningful and clear
- ✅ Tests initially fail (red phase)
- ✅ Implementation makes tests pass (green phase)
- ✅ Code improved without breaking tests (refactor phase)
- ✅ Ready to proceed with confidence
