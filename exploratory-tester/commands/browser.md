---
name: browser
description: Launch autonomous browser-based exploratory testing of a web application
argument-hint: URL or context describing what to test
allowed-tools: ["Task"]
---

Launch the browser-explorer agent to autonomously test a web application.

## How This Command Works

When this command is invoked, use the Task tool to launch the browser-explorer agent with the user's context.

## Execution Steps

1. **Parse user input**: The argument may be:
   - Explicit URL: `https://app.example.com/dashboard`
   - Context description: "the login page" or "my app's checkout flow"
   - Path reference: "./index.html" or "the dashboard component"

2. **Launch browser-explorer agent**:
   ```
   Use Task tool with:
   - subagent_type: "exploratory-tester:browser-explorer"
   - description: "Test web application"
   - prompt: Pass user's context, including:
     - Target URL or description
     - Testing depth (if specified, default to single page)
     - Specific areas to focus on (if mentioned)
     - Any other relevant context
   ```

3. **Let agent work autonomously**: The browser-explorer agent will handle all testing and report findings

## Usage Examples

```
/exploratory:browser https://app.example.com
/exploratory:browser the dashboard (agent determines URL from context)
/exploratory:browser test the login form for accessibility issues
/exploratory:browser https://mysite.com --depth 2 (shallow crawl)
```

## Tips

- The agent will determine the actual URL if only a description is provided
- Specify depth if you want multi-page testing (default: single page)
- Agent reports findings as markdown in chat
- Browser testing uses Playwright MCP (must be available)

## Related Skills

The browser-explorer agent uses the browser-testing-patterns skill for testing methodology.
