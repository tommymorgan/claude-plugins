---
name: rest-api-guidelines
description: Opinionated REST API design guidance for resource naming, HTTP semantics, error formats, pagination, versioning, and more. Use when designing REST APIs during brainstorming or plan creation.
version: 0.1.0
---

# REST API Design Guidelines

Opinionated guidance for designing consistent, developer-friendly REST APIs. Apply these guidelines when designing new APIs or reviewing existing API designs.

## URL Structure

**Pattern**: `/{serviceRoot}/{collection}/{id}`

URLs should be human-readable and hierarchical:
- `https://api.example.com/v1/people/jdoe@example.com/inbox`
- `https://api.example.com/v1/orders/12345/items`

**Rules:**
- Collection names: unabbreviated, pluralized nouns (`/users`, `/orders`, `/messages`)
- Use path segments for hierarchy, not query parameters
- Keep URLs short and predictable
- Resources that can move or rename should expose stable identifier URLs

**URL length**: Design for under 2,083 characters to accommodate all clients.

## HTTP Methods

| Method | Purpose | Idempotent | Key Rules |
|--------|---------|-----------|-----------|
| **GET** | Retrieve resource | Yes | Safe, cacheable, no side effects |
| **POST** | Create resource or submit command | No | Return 201 Created with Location header |
| **PUT** | Replace entire resource | Yes | Full replacement — unspecified properties are removed |
| **PATCH** | Partial update | No | Preferred over PUT for updates; supports UPSERT |
| **DELETE** | Remove resource | Yes | Return 204 No Content |
| **HEAD** | Metadata only (no body) | Yes | Same as GET without response body |
| **OPTIONS** | Discover capabilities | Yes | Return Allow header listing supported methods |

**PATCH for UPSERT:**
- Without precondition headers: service determines create vs. update
- With `If-Match`: update only (409 if missing)
- With `If-None-Match: *`: create only (409 if exists)

## Status Codes

### Success
| Code | Meaning | Use When |
|------|---------|----------|
| **200** | OK | Standard success with response body |
| **201** | Created | Resource created; include Location header |
| **202** | Accepted | Long-running operation initiated |
| **204** | No Content | Success with no response body (DELETE, some updates) |

### Client Errors
| Code | Meaning | Use When |
|------|---------|----------|
| **400** | Bad Request | Invalid request syntax or parameters |
| **401** | Unauthorized | Authentication required or failed |
| **403** | Forbidden | Authenticated but lacks permission |
| **404** | Not Found | Resource does not exist |
| **405** | Method Not Allowed | HTTP method not supported on this resource |
| **409** | Conflict | Request conflicts with current state |
| **429** | Too Many Requests | Rate limit or quota exceeded |

### Server Errors
| Code | Meaning | Use When |
|------|---------|----------|
| **500** | Internal Server Error | Unhandled server failure |
| **503** | Service Unavailable | Server overloaded or in maintenance |

**Important**: Rate-limit failures (429) are client errors, not faults. Only 5xx errors count as faults affecting availability.

## Error Response Format

All error responses use a single JSON object with a mandatory `error` property:

```json
{
  "error": {
    "code": "BadArgument",
    "message": "Human-readable description for developers",
    "target": "propertyName",
    "details": [],
    "innererror": {}
  }
}
```

### Error Object Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `code` | string | Yes | Language-independent, stable error code (~20 possible values) |
| `message` | string | Yes | Developer-facing description; do not localize; not for end-user display |
| `target` | string | No | What caused the error (e.g., property name) |
| `details` | Error[] | No | Array of related errors, each with `code` and `message` |
| `innererror` | object | No | More specific nested error detail |

### Nested Error Example

```json
{
  "error": {
    "code": "BadArgument",
    "message": "Previous passwords may not be reused",
    "target": "password",
    "innererror": {
      "code": "PasswordError",
      "innererror": {
        "code": "PasswordDoesNotMeetPolicy",
        "minLength": "6",
        "maxLength": "64"
      }
    }
  }
}
```

### Multiple Errors Example

```json
{
  "error": {
    "code": "BadArgument",
    "message": "Multiple validation errors",
    "details": [
      { "code": "NullValue", "target": "phoneNumber", "message": "Phone number is required" },
      { "code": "NullValue", "target": "lastName", "message": "Last name is required" }
    ]
  }
}
```

**Rules:**
- Changing visible `code` values is a breaking change
- Use `innererror` for new granular codes without breaking clients
- Clients should traverse `innererror` chain and act on the deepest understood code
- Include `Retry-After` header for transient errors

## Collections and Pagination

### Collection Representation

Wrap collections in a `value` property:
```json
{
  "value": [
    { "id": "1", "name": "Item One" },
    { "id": "2", "name": "Item Two" }
  ]
}
```

Empty collections return 200 OK with empty array:
```json
{
  "value": []
}
```

### Server-Driven Pagination

Include a continuation token as `@nextLink` (an opaque URL):
```json
{
  "value": [ ... ],
  "@nextLink": "https://api.example.com/v1/people?$skip=20"
}
```

- Absence of `@nextLink` indicates the final page
- Clients must treat continuation URLs as opaque — no modification

### Client-Driven Pagination

| Parameter | Purpose |
|-----------|---------|
| `$top` | Maximum number of items to return |
| `$skip` | Number of items to skip |

Server applies `$skip` first, then `$top`. The server must return an error if it cannot honor the parameters (never silently ignore them).

### Page Size Preference

Clients may specify `$maxpagesize` as a preferred page size. Servers should honor it if smaller than the server default.

Use `$count=true` to include total item count across all pages.

## Filtering

**Parameter**: `$filter`

Boolean expression evaluated for each resource. Only items where the expression is true are included.

### Operators

| Category | Operator | Example |
|----------|----------|---------|
| Comparison | `eq` | `city eq 'Portland'` |
| | `ne` | `city ne 'Portland'` |
| | `gt` | `price gt 20` |
| | `ge` | `price ge 10` |
| | `lt` | `price lt 20` |
| | `le` | `price le 100` |
| Logical | `and` | `price le 200 and price gt 3.5` |
| | `or` | `price le 3.5 or price gt 200` |
| | `not` | `not price le 3.5` |
| Grouping | `( )` | `(status eq 'active' or status eq 'pending') and price gt 100` |

### Operator Precedence (highest to lowest)

1. `( )` — Grouping
2. `not` — Unary
3. `gt`, `ge`, `lt`, `le` — Relational
4. `eq`, `ne` — Equality
5. `and` — Conditional AND
6. `or` — Conditional OR

## Sorting

**Parameter**: `$orderBy`

| Syntax | Example |
|--------|---------|
| Property name | `$orderBy=name` |
| Descending | `$orderBy=name desc` |
| Multiple properties | `$orderBy=name desc,createdDate` |

Default direction is ascending. NULL values sort before non-NULL values.

Sorting composes with filtering: `GET /people?$filter=status eq 'active'&$orderBy=name`

If the server doesn't support sorting by a requested property, return an error.

## Versioning

All APIs must support explicit versioning.

**Format**: Major.Minor (e.g., `1.0`, `2.1`)

**Two mechanisms:**

1. **URL path (recommended)**: `https://api.example.com/v1/products`
2. **Query parameter**: `https://api.example.com/products?api-version=1.0`

**When to version:**
- Major increment: breaking changes (signals future deprecation of previous version)
- Minor increment: non-breaking additions

**Breaking changes include:**
- Removing or renaming APIs or parameters
- Changing behavior of existing APIs
- Changing error codes or fault contracts

**Documentation**: indicate support status of each previous version and the path to the latest.

## Naming Conventions

### JSON Properties

Use **camelCase** for all JSON property names:
- `firstName`, `lastName`, `dateOfBirth`
- Not: `first_name`, `FirstName`, `FIRST_NAME`

### Common Property Names

| Name | Purpose |
|------|---------|
| `id` | Unique identifier |
| `name` | Display or primary name |
| `description` | Textual description |
| `createdDateTime` | Creation timestamp |
| `lastModifiedDateTime` | Last modification timestamp |
| `status` | Current state |
| `type` | Resource type classification |

### Date/Time Properties

Use ISO 8601 format: `2025-02-13T13:15:00Z`

Suffixes: `Date`, `Time`, `DateTime`, `Timestamp`
- `createdDate`, `lastModifiedTime`, `expirationDateTime`

### Collections

- Collection names: plural nouns (`addresses`, `orders`)
- Count properties: `count` suffix (`addressCount`)

### General Rules

- Use full words, not abbreviations (`emailAddress` not `email_addr`)
- Avoid acronyms without context
- Avoid language-specific keywords

## CORS (Cross-Origin Resource Sharing)

All APIs should support CORS.

**For every request with an Origin header:**
1. Return `Access-Control-Allow-Origin` echoing the request's Origin value
2. Include `Access-Control-Expose-Headers` listing non-simple response headers
3. Set `Access-Control-Allow-Credentials: true` if cookies are required

**For OPTIONS preflight requests**, additionally include:
- `Access-Control-Allow-Headers`: permitted request headers
- `Access-Control-Allow-Methods`: permitted HTTP methods
- `Access-Control-Max-Age`: how long the preflight response is cached (in seconds)

Return 200 OK for preflight requests with no additional processing.

**Authorization strategy**: enforce authorization through valid tokens, not origin validation.

## Throttling and Rate Limiting

### Response Codes

| Code | Use When |
|------|----------|
| **429** | Client rate limit or quota exceeded |
| **503** | Server overload protection (fast-fail) |

### Response Headers

| Header | Purpose |
|--------|---------|
| `Retry-After` | Seconds to wait before retrying |
| `RateLimit-Limit` | Quota window size (e.g., requests per hour) |
| `RateLimit-Remaining` | Remaining quota in current window |
| `RateLimit-Reset` | Seconds until quota resets |

### Example 429 Response

```
HTTP/1.1 429 Too Many Requests
Retry-After: 30
RateLimit-Limit: 1000
RateLimit-Remaining: 0
RateLimit-Reset: 1800
```

### Design Principles

- Respond quickly with errors when overloaded — don't let requests hang
- Document rate limits and quota scopes (per user, per application, per IP)
- Rate-limit failures (429) must not count as faults in availability metrics

### Client Behavior

- Respect `Retry-After` header
- Implement exponential backoff
- Cache responses where appropriate
- Design for graceful degradation under rate limits

## Webhooks

### Subscription Model

Clients create subscriptions for specific resource changes:

```http
POST https://api.example.com/v1/subscriptions
Content-Type: application/json

{
  "notificationUrl": "https://client.example.com/webhook",
  "resource": "/users/123/messages",
  "changeType": "created,updated,deleted",
  "clientState": "client-context-value"
}
```

### Subscription Management

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Create | POST | `/subscriptions` |
| Update | PATCH | `/subscriptions/{id}` |
| Delete | DELETE | `/subscriptions/{id}` |
| List | GET | `/subscriptions` |

### Subscription Verification (Handshake)

When a subscription is created:
1. Service sends POST to `notificationUrl` with `validationToken` query parameter
2. Client responds with 200 OK and echoes the token in the response body (`text/plain`)
3. Service activates the subscription only after successful validation

This prevents malicious subscription creation to third-party endpoints.

### Notification Payload

```json
{
  "value": [
    {
      "subscriptionId": "sub-123",
      "clientState": "client-context-value",
      "changeType": "created",
      "resource": "/users/123/messages/456",
      "resourceData": {
        "id": "456"
      },
      "sequenceNumber": 1
    }
  ]
}
```

### Reliability

- Services should retry delivery with backoff
- Notifications should be delivered in order (best-effort)
- Clients must handle duplicate deliveries (idempotency)

### Security

- HTTPS only for webhook endpoints
- Services should include HMAC signature in headers (e.g., `X-Webhook-Signature: sha256=...`)
- Clients should validate signatures using the shared secret
- `clientState` provides additional verification that the notification originated from the expected service

## Long-Running Operations

For operations expected to take more than 0.5 seconds (99th percentile):

1. Return **202 Accepted** with `Operation-Location` header
2. Client polls the operation status URL
3. Operation resource reports status: `notStarted`, `running`, `succeeded`, `failed`

```json
{
  "createdDateTime": "2025-02-13T12:01:03Z",
  "lastActionDateTime": "2025-02-13T12:06:03Z",
  "status": "running",
  "percentComplete": 45,
  "resourceLocation": "https://api.example.com/v1/exports/export-789"
}
```

Include `Retry-After` header to indicate polling interval.

## Client Behavior Rules

1. **Ignore unknown fields**: clients must safely ignore unexpected response properties
2. **Don't assume field order**: JSON property order is not guaranteed
3. **Handle graceful degradation**: optional server features may not be available
4. **Support pagination**: handle both server-driven and client-driven paging
5. **Implement backoff**: exponential backoff for rate-limited retries
6. **Validate webhooks**: verify signatures and handle duplicates
