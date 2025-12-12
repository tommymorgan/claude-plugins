---
name: api
description: Launch autonomous API exploratory testing for REST or GraphQL APIs
argument-hint: API base URL, OpenAPI spec path, or context
allowed-tools: ["Task"]
---

Launch the api-explorer agent to autonomously test API endpoints.

## How This Command Works

When this command is invoked, use the Task tool to launch the api-explorer agent with the user's context.

## Execution Steps

1. **Parse user input**: The argument may be:
   - API base URL: `https://api.example.com/v1`
   - OpenAPI spec path: `./openapi.yaml` or `./swagger.json`
   - OpenAPI spec URL: `https://api.example.com/openapi.json`
   - Context description: "my user API" or "the authentication endpoints"

2. **Launch api-explorer agent**:
   ```
   Use Task tool with:
   - subagent_type: "exploratory-tester:api-explorer"
   - description: "Test API endpoints"
   - prompt: Pass user's context, including:
     - API base URL or OpenAPI spec location
     - Specific endpoints to focus on (if mentioned)
     - Testing scope (comprehensive vs focused)
     - Any authentication details or test data location
     - Any other relevant context
   ```

3. **Let agent work autonomously**: The api-explorer agent will discover endpoints, test them comprehensively, and report findings

## Usage Examples

```
/exploratory:api https://api.example.com/v1
/exploratory:api ./openapi.yaml
/exploratory:api test the user endpoints
/exploratory:api https://api.example.com/openapi.json
/exploratory:api my authentication API (agent determines URL from context)
```

## Tips

- Provide OpenAPI/Swagger spec for comprehensive testing
- Agent will discover endpoints via common patterns if no spec
- Agent reports undocumented endpoints if spec is provided but discovery finds extras
- Specify focus area if testing specific changes
- Agent uses test data generators if application provides them

## Related Skills

The api-explorer agent uses the api-testing-patterns skill for testing methodology.
