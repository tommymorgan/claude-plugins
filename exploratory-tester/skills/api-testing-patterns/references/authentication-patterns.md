# Authentication Testing Patterns

Complete guide for testing API authentication and authorization.

## Authentication Methods

### Bearer Token (JWT)

**Test scenarios:**
```bash
# No token
curl https://api.example.com/protected
# Expected: 401 Unauthorized

# Invalid token
curl -H "Authorization: Bearer invalid_token" https://api.example.com/protected
# Expected: 401 Unauthorized

# Valid token
curl -H "Authorization: Bearer <valid_token>" https://api.example.com/protected
# Expected: 200 OK

# Expired token
curl -H "Authorization: Bearer <expired_token>" https://api.example.com/protected
# Expected: 401 Unauthorized (with clear expiry message)
```

### API Key

**Test scenarios:**
```bash
# No key
curl https://api.example.com/data
# Expected: 401 Unauthorized

# Invalid key
curl -H "X-API-Key: wrong_key" https://api.example.com/data
# Expected: 401 Unauthorized

# Valid key
curl -H "X-API-Key: <valid_key>" https://api.example.com/data
# Expected: 200 OK
```

### OAuth 2.0

**Test flow:**
1. Authorization endpoint (GET /oauth/authorize)
2. Token endpoint (POST /oauth/token)
3. Protected resource (with access token)
4. Refresh token flow
5. Token revocation

## Authorization Testing

### Resource Access Control

Test users can only access their own resources:

```bash
# User A's token trying to access User B's data
curl -H "Authorization: Bearer user_a_token" \
  https://api.example.com/users/user_b_id/profile

# Expected: 403 Forbidden
# If 200: Critical authorization bypass bug
```

### Role-Based Access

Test role boundaries:

```bash
# Regular user accessing admin endpoint
curl -H "Authorization: Bearer user_token" \
  https://api.example.com/admin/users

# Expected: 403 Forbidden

# Admin accessing admin endpoint
curl -H "Authorization: Bearer admin_token" \
  https://api.example.com/admin/users

# Expected: 200 OK
```

### Permission Testing Matrix

For each role, test:
- ✅ Can access allowed resources
- ❌ Cannot access forbidden resources
- ✅ Can perform allowed operations
- ❌ Cannot perform forbidden operations

## Common Authentication Vulnerabilities

### Missing Authentication Check

**Symptom**: Protected endpoints accessible without auth
**Test**: Request endpoint without credentials
**Should**: Return 401
**If succeeds**: Critical vulnerability

### Weak Token Validation

**Symptom**: Invalid tokens are accepted
**Test**: Modify token, use expired token, use wrong signature
**Should**: Reject with 401
**If accepts**: Critical vulnerability

### JWT Vulnerabilities

Test for:
- **None algorithm**: Token with "alg": "none" accepted
- **Weak secrets**: Short or predictable signing keys
- **No expiration**: Tokens never expire
- **Algorithm confusion**: RS256 token accepted as HS256

### Session Fixation

**Test**: Reuse session ID from pre-login to post-login
**Should**: Generate new session ID after login
**If reuses**: Security vulnerability

## Authorization Best Practices Validation

### Principle of Least Privilege

Verify:
- Users have minimum necessary permissions
- Default is deny (not allow)
- Permissions are explicit (not inferred)

### Consistent Enforcement

Check:
- All endpoints enforce authorization
- No bypass through different HTTP methods
- No bypass through parameter manipulation

## Reporting Template

```markdown
## Security Concerns 🔒

### Authorization Bypass - Critical
- **Endpoint**: GET /users/{id}/sensitive-data
- **Issue**: User A can access User B's data
- **Test**:
  ```bash
  curl -H "Authorization: Bearer user_a_token" \
    https://api.example.com/users/user_b_id/sensitive-data
  ```
- **Expected**: 403 Forbidden
- **Actual**: 200 OK with User B's data
- **Impact**: Complete data breach for all users
- **Priority**: Fix immediately

### Missing Authentication - Critical
- **Endpoint**: DELETE /users/{id}
- **Issue**: Can delete users without authentication
- **Test**:
  ```bash
  curl -X DELETE https://api.example.com/users/123
  ```
- **Expected**: 401 Unauthorized
- **Actual**: 200 OK (user deleted)
- **Impact**: Anyone can delete any user
- **Priority**: Fix immediately
```
