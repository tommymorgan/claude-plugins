---
name: API Testing Patterns
description: This skill should be used when performing exploratory testing of REST or GraphQL APIs, including endpoint discovery, request/response validation, authentication testing, and error handling checks. Triggers when testing APIs, validating OpenAPI specs, checking endpoint security, or verifying API responses.
version: 0.1.0
---

# API Testing Patterns

## Purpose

Provide systematic patterns for autonomous API exploratory testing. Guide agents through comprehensive API testing including endpoint discovery, request/response validation, authentication verification, error handling checks, and security testing.

## Core Testing Methodology

### API Discovery Strategy

Discover API endpoints through multiple methods:

**1. OpenAPI/Swagger Specification**
- Parse spec to extract all endpoints
- Understand request/response schemas
- Identify authentication requirements
- Note documented error codes

**2. Common Pattern Discovery**
- Probe common API paths (/api/*, /v1/*, /graphql)
- Try standard REST conventions (GET /users, POST /users, etc.)
- Check for API documentation endpoints (/docs, /swagger, /openapi.json)

**3. Undocumented Endpoint Detection**
- Compare discovered endpoints with spec
- Report endpoints found but not documented (security concern)
- Note missing endpoints that should exist

### Comprehensive Testing Coverage

Test each endpoint across multiple dimensions:

**HTTP Methods:**
- GET: Read operations
- POST: Create operations
- PUT/PATCH: Update operations
- DELETE: Delete operations
- OPTIONS: CORS preflight

**Response Codes:**
- 200/201: Success scenarios
- 400: Bad request (invalid input)
- 401: Unauthorized (missing/invalid auth)
- 403: Forbidden (insufficient permissions)
- 404: Not found (non-existent resources)
- 500: Server errors

**Input Variations:**
- Valid data (happy path)
- Invalid data types
- Missing required fields
- Boundary values (empty, very long, negative)
- Malicious inputs (SQL injection, XSS attempts)

## Authentication Testing

### Common Authentication Patterns

**Bearer Token:**
```bash
curl -H "Authorization: Bearer <token>" https://api.example.com/endpoint
```

**API Key:**
```bash
curl -H "X-API-Key: <key>" https://api.example.com/endpoint
```

**Basic Auth:**
```bash
curl -u username:password https://api.example.com/endpoint
```

### Authentication Tests

Test authentication enforcement:

1. **No auth**: Request without credentials (should return 401)
2. **Invalid auth**: Request with malformed credentials (should return 401)
3. **Expired auth**: Request with expired token (should return 401)
4. **Valid auth**: Request with proper credentials (should succeed)

### Authorization Tests

Test permission boundaries:

1. **Own resources**: User can access their own data (should succeed)
2. **Other resources**: User cannot access other users' data (should return 403)
3. **Admin resources**: Non-admin cannot access admin endpoints (should return 403)
4. **Role boundaries**: Test each role's access limits

## Input Validation Testing

### Test Data Generation

Generate test data based on schemas:

**From OpenAPI Schema:**
```json
{
  "email": "test@example.com",
  "age": 25,
  "name": "Test User"
}
```

**Invalid Variations:**
```json
// Wrong type
{"email": 123, "age": "not a number"}

// Missing required
{"email": "test@example.com"}

// Boundary values
{"email": "", "age": -1}

// Too long
{"name": "A".repeat(1000)}
```

### SQL Injection Testing

Test for SQL injection vulnerabilities:

```markdown
Send inputs designed to break SQL queries:
- `' OR '1'='1`
- `; DROP TABLE users; --`
- `1' UNION SELECT * FROM users --`

Expected behavior:
- API rejects malicious input (400/422)
- Error message doesn't reveal SQL structure
- No database errors in response
```

### XSS Testing

Test for cross-site scripting vulnerabilities:

```markdown
Send HTML/JavaScript in inputs:
- `<script>alert('XSS')</script>`
- `<img src=x onerror=alert('XSS')>`
- `javascript:alert('XSS')`

Expected behavior:
- Input is sanitized or rejected
- Response escapes HTML properly
- No executable code in responses
```

## Response Validation

### Schema Validation

Validate responses match documented schemas:

```markdown
For each endpoint:
1. Parse response JSON
2. Check all required fields present
3. Verify field types match schema
4. Validate nested object structures
5. Check enum values are from allowed set
6. Verify array items match schema
```

### Error Response Format

Validate error responses are consistent:

```markdown
Expected error format:
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": {...}
  }
}

Check:
- Errors don't expose sensitive data
- Error codes are consistent
- Messages are helpful
- Stack traces not exposed
```

## Performance Testing

### Response Time Measurement

Measure API response times:

```markdown
Use WebFetch or Bash (curl with timing):
- Simple queries: <200ms
- Complex queries: <500ms
- Search operations: <400ms
- Bulk operations: <2s

Report slow endpoints with:
- Actual response time
- Endpoint and method
- Request parameters
- Threshold exceeded
```

### Load Testing Indicators

Check for performance under load:

```markdown
Look for:
- Rate limiting headers (X-RateLimit-*)
- Retry-After headers
- 429 Too Many Requests responses
- Increasing response times with repeated requests
```

## GraphQL Testing

### Introspection Query

Discover GraphQL schema:

```graphql
{
  __schema {
    types {
      name
      fields {
        name
        type {
          name
        }
      }
    }
  }
}
```

### GraphQL-Specific Tests

Test GraphQL endpoints:

1. **Valid queries**: Test documented queries
2. **Invalid queries**: Malformed GraphQL syntax
3. **Deep nesting**: Excessive query depth (DoS risk)
4. **Field suggestions**: Check error messages for typos
5. **Mutations**: Test data modification operations
6. **Subscriptions**: Test real-time subscriptions if supported

## Reporting Patterns

### Issue Categorization

**Critical Issues ❌:**
- Authentication bypass
- Authorization failures
- Data exposure
- SQL injection vulnerabilities
- Crashes or 500 errors on normal inputs

**Security Concerns 🔒:**
- Undocumented endpoints
- Weak input validation
- Sensitive data in errors
- Missing CORS headers
- No rate limiting

**Warnings ⚠️:**
- Inconsistent error formats
- Poor error messages
- Slow response times
- Missing validation
- Deprecated endpoints

**Tests Passed ✅:**
- Proper authentication enforcement
- Strong input validation
- Consistent response schemas
- Good performance
- Helpful error messages

### Reproduction Examples

Provide cURL examples for every issue:

```markdown
### Issue: Missing Email Validation

**Reproduction:**
```bash
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"email": "not-an-email", "name": "Test"}'
```

**Expected**: 400 Bad Request with validation error
**Actual**: 201 Created (accepted invalid email)
**Impact**: Invalid data in database
**Severity**: High
```

## Test Data Sources

### Priority Order

1. **Application test data generator**: Use /api/test/seed or similar
2. **OpenAPI schema**: Generate from documented schemas
3. **Infer from responses**: Learn from successful responses
4. **Simple defaults**: Use basic valid test data

### Realistic Test Data

Generate realistic data:

```markdown
Good:
- Emails: "test@example.com", "user@test.org"
- Names: "Test User", "Jane Doe"
- Dates: Current date ± reasonable range
- IDs: Realistic integers or UUIDs

Avoid:
- Obvious fakes: "foo", "bar", "test"
- Invalid formats: "asdf@asdf"
- Destructive: very large values
```

## Additional Resources

For complete API testing procedures, see:
- **`references/openapi-parsing.md`** - Parsing and using OpenAPI specs
- **`references/authentication-patterns.md`** - Authentication testing strategies
- **`references/security-testing.md`** - Security vulnerability testing
