# OpenAPI/Swagger Specification Parsing

Guide for parsing and using OpenAPI specifications in API testing.

## OpenAPI Structure

### Specification Versions

**OpenAPI 3.x** (current):
```yaml
openapi: 3.0.0
info:
  title: API Name
  version: 1.0.0
servers:
  - url: https://api.example.com/v1
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: Success
components:
  schemas:
    User:
      type: object
      properties:
        id: integer
        email: string
```

**Swagger 2.0** (legacy):
```yaml
swagger: '2.0'
info:
  title: API Name
  version: 1.0.0
basePath: /v1
paths:
  /users:
    get:
      summary: List users
definitions:
  User:
    type: object
```

## Parsing Endpoints

### Extract All Endpoints

From OpenAPI spec, extract:
- Path (e.g., `/users/{id}`)
- HTTP methods (GET, POST, PUT, DELETE)
- Parameters (path, query, body)
- Expected responses
- Authentication requirements

### Example Parsing Logic

```markdown
For each path in spec.paths:
  For each method in path methods:
    Create test case:
      - URL: basePath + path
      - Method: HTTP method
      - Parameters: Extract from spec
      - Auth: Check security field
      - Expected: Parse responses
```

## Schema-Based Test Data Generation

### Generate Valid Data

From schema definition:

```json
// Schema
{
  "type": "object",
  "required": ["email", "name"],
  "properties": {
    "email": {"type": "string", "format": "email"},
    "name": {"type": "string", "minLength": 2, "maxLength": 100},
    "age": {"type": "integer", "minimum": 0, "maximum": 150}
  }
}

// Generated test data
{
  "email": "test@example.com",
  "name": "Test User",
  "age": 25
}
```

### Generate Invalid Data

Test validation by violating constraints:

```json
// Wrong type
{"email": 123, "name": "Test", "age": 25}

// Missing required
{"name": "Test"}

// Below minimum
{"email": "test@example.com", "name": "Test", "age": -1}

// Above maximum
{"email": "test@example.com", "name": "Test", "age": 200}

// Wrong format
{"email": "not-an-email", "name": "Test", "age": 25}

// Too long
{"email": "test@example.com", "name": "A".repeat(200), "age": 25}
```

## Parameter Testing

### Path Parameters

```markdown
Endpoint: /users/{id}

Tests:
- Valid ID: /users/123
- Invalid ID: /users/abc
- Non-existent: /users/999999
- Negative: /users/-1
- Special chars: /users/%20
```

### Query Parameters

```markdown
Endpoint: /users?page=1&limit=20

Tests:
- Valid: ?page=1&limit=20
- Missing: /users (should use defaults)
- Invalid type: ?page=abc&limit=xyz
- Negative: ?page=-1&limit=-10
- Too large: ?page=1&limit=99999
- Injection: ?page=1'; DROP TABLE--
```

### Body Parameters

Test JSON request bodies:

```markdown
Valid:
POST /users {"email": "test@example.com", "name": "Test"}

Invalid type:
POST /users {"email": 123, "name": 456}

Missing required:
POST /users {"name": "Test"}

Extra fields:
POST /users {"email": "test@example.com", "name": "Test", "hacker": "payload"}

Malformed JSON:
POST /users {invalid json}
```

## Response Validation

### Status Code Validation

Verify status codes match spec:

```markdown
Spec says:
  200: Success
  400: Bad Request
  401: Unauthorized
  404: Not Found

Test:
- Valid request → Should return 200
- Invalid data → Should return 400
- No auth → Should return 401
- Bad ID → Should return 404
```

### Schema Validation

Check response matches schema:

```markdown
Expected schema:
{
  "id": integer,
  "email": string,
  "name": string
}

Validate response:
- Has all required fields
- Fields have correct types
- No unexpected fields (if strict)
- Nested objects match schemas
```

## Common API Issues

### Missing Input Validation

**Issue**: API accepts invalid data
**Test**: Send schema-violating data
**Expected**: 400/422 with validation error
**If passes**: Report as bug

### Weak Authentication

**Issue**: Endpoints accessible without auth
**Test**: Request without Authorization header
**Expected**: 401 Unauthorized
**If succeeds**: Critical security issue

### Authorization Bypass

**Issue**: Users can access others' data
**Test**: Request user A's data with user B's token
**Expected**: 403 Forbidden
**If succeeds**: Critical security issue

### Information Disclosure

**Issue**: Errors reveal sensitive information
**Test**: Send invalid requests, check error messages
**Bad**: Stack traces, SQL queries, file paths in errors
**Good**: Generic errors to client, detailed logs server-side

### Inconsistent Responses

**Issue**: Same endpoint returns different formats
**Test**: Call endpoint multiple times, compare responses
**Expected**: Consistent structure
**If varies**: Report as bug

## Testing Workflow

### Complete API Test Flow

```markdown
1. Discover endpoints (spec + crawling)
2. For each endpoint:
   a. Test happy path (valid data, proper auth)
   b. Test authentication (no auth, invalid auth)
   c. Test authorization (cross-user access)
   d. Test input validation (invalid data)
   e. Test error handling (various error conditions)
3. Measure response times
4. Validate response schemas
5. Check security headers
6. Report findings categorized by severity
```

### Scoped Testing

When context indicates specific changes:

```markdown
If context says "I updated the user endpoint":
- Comprehensive tests on /users endpoints
- Smoke tests on related endpoints (/auth, /profile)
- Quick validation on unrelated endpoints

Balance thoroughness with efficiency based on scope.
```

## Test Data Strategies

### Using Test Data Generators

Check for test data endpoints:

```bash
# Common patterns
GET /api/test/seed
POST /api/test/generate
GET /api/fixtures
```

If found:
- Use generated data for testing
- More realistic and comprehensive
- Follows app's data model

### Inferring from Schemas

If no test data generator:

```markdown
From OpenAPI schema:
1. Identify required fields
2. Note field types and constraints
3. Generate minimal valid object
4. Generate edge case variations
5. Generate invalid variations for validation testing
```

## Additional Resources

For detailed API testing techniques, consult:
- **`references/authentication-patterns.md`** - Complete authentication testing guide
- **`references/security-testing.md`** - Security vulnerability testing patterns
- **`references/graphql-testing.md`** - GraphQL-specific testing strategies

## Quick Reference

**Testing checklist:**
- [ ] Discover all endpoints (spec + crawling)
- [ ] Test authentication enforcement
- [ ] Test authorization boundaries
- [ ] Validate input handling
- [ ] Check error responses
- [ ] Validate response schemas
- [ ] Measure performance
- [ ] Check security headers
- [ ] Report findings by severity

**Remember:** Focus on finding real API bugs. Test comprehensively but scope to context. Use test data generators when available.
