# API Security Testing

Comprehensive security vulnerability testing patterns for APIs.

## Input Validation Testing

### SQL Injection

**Test payloads:**
```markdown
- ' OR '1'='1
- 1' UNION SELECT * FROM users--
- '; DROP TABLE users; --
- 1' AND '1'='1
```

**Test locations:**
- Query parameters
- Path parameters
- JSON body fields
- Headers

**Expected behavior:**
- API rejects input (400/422)
- Error doesn't reveal SQL syntax
- No database errors exposed

**If vulnerable:**
- Input is executed as SQL
- Database errors in response
- Successful data extraction/modification

### NoSQL Injection

**Test payloads:**
```json
{"$gt": ""}
{"$ne": null}
{"$where": "this.password.length > 0"}
```

**Expected**: Rejected as invalid data
**If vulnerable**: Bypasses queries or exposes data

### Cross-Site Scripting (XSS)

**Test payloads:**
```markdown
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
javascript:alert('XSS')
```

**Test in:**
- Text fields
- Search parameters
- Any user input that might be reflected

**Expected**:
- Input is sanitized/escaped
- Response doesn't contain executable code

### Command Injection

**Test payloads:**
```markdown
; ls -la
| cat /etc/passwd
&& whoami
`cat /etc/passwd`
```

**Test in:**
- File upload names
- System command parameters
- Any input processed by shell

**Expected**: Input rejected or properly escaped

## Mass Assignment

**Test:**
```json
POST /users {
  "email": "test@example.com",
  "name": "Test",
  "role": "admin",
  "isVerified": true
}
```

**Should**: Ignore role and isVerified (internal fields)
**If accepts**: User can escalate privileges

## Information Disclosure

### Error Messages

**Bad error responses:**
```json
{
  "error": "Error: connect ECONNREFUSED 127.0.0.1:5432",
  "stack": "at Connection.connect (/app/node_modules/pg/lib/connection.js:123)"
}
```

Exposes:
- Database type and version
- File paths
- Stack traces

**Good error responses:**
```json
{
  "error": {
    "code": "DATABASE_ERROR",
    "message": "Unable to process request. Please try again later."
  }
}
```

### Enumeration Attacks

**Test user enumeration:**
```bash
# Different responses for existing vs non-existing users
POST /login {"email": "exists@example.com", "password": "wrong"}
# Response: "Incorrect password"

POST /login {"email": "notexist@example.com", "password": "wrong"}
# Response: "User not found"

# Should: Both return generic "Invalid credentials"
```

## Rate Limiting

### Test Rate Limits

**Methodology:**
```markdown
1. Make repeated requests to same endpoint
2. Check for rate limit headers:
   - X-RateLimit-Limit
   - X-RateLimit-Remaining
   - X-RateLimit-Reset
3. Continue until rate limited
4. Verify 429 Too Many Requests response
```

**Expected:**
- Rate limits are enforced
- Clear error message when limited
- Retry-After header provided

**If missing:**
- API vulnerable to abuse
- No protection against DoS attacks

## CORS Testing

### Check CORS Headers

**Test:**
```bash
curl -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS https://api.example.com/endpoint
```

**Expected headers:**
```
Access-Control-Allow-Origin: https://trusted.com
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Headers: Content-Type, Authorization
```

**Issues:**
- `Access-Control-Allow-Origin: *` (too permissive)
- Allows all origins without validation
- Missing CORS headers entirely

## Security Headers

### Required Headers

**Check for:**
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
```

**Test:**
```bash
curl -I https://api.example.com/endpoint | grep -i "x-"
```

**Report missing security headers**

## Sensitive Data Exposure

### Check for Exposed Data

**Test:**
- Passwords in responses (should be hashed, never exposed)
- API keys in responses
- Internal IDs or system information
- PII without proper access control

**Example issue:**
```json
GET /users/123
{
  "id": 123,
  "email": "user@example.com",
  "password_hash": "$2b$10$..." // Should not be exposed
}
```

## Reporting Template

```markdown
## Security Concerns 🔒

### SQL Injection - Critical
- **Endpoint**: GET /users?search={query}
- **Vulnerability**: User input not sanitized
- **Test**:
  ```bash
  curl "https://api.example.com/users?search=' OR '1'='1"
  ```
- **Result**: Returns all users (SQL injection successful)
- **Impact**: Complete database compromise
- **Fix**: Use parameterized queries

### Undocumented Endpoints - High
- **Endpoints Found**: 5 endpoints not in OpenAPI spec
- **Concern**: Undocumented = potentially untested/insecure
- **Examples**:
  - POST /internal/admin/users (admin endpoint not documented)
  - GET /debug/config (exposes configuration)
- **Recommendation**: Document or remove these endpoints
```
