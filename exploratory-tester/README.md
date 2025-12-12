# Exploratory Tester Plugin

Autonomous exploratory testing for web applications, APIs, and CLI tools with automated browser testing capabilities.

## Overview

This plugin provides specialized agents that autonomously test different types of software:
- **Web applications**: Functional, visual, accessibility, and performance testing via browser automation
- **REST/GraphQL APIs**: Endpoint discovery, validation, and error handling testing
- **CLI tools**: Command execution, output validation, and error case testing

## Features

### Agents

- **browser-explorer**: Autonomous web application testing using Playwright
  - Functional testing (navigation, forms, interactions)
  - Visual testing (screenshots, layout issues)
  - Accessibility testing (WCAG compliance)
  - Performance testing (Core Web Vitals)

- **api-explorer**: Autonomous API testing
  - OpenAPI/Swagger spec parsing
  - Endpoint discovery
  - Request/response validation
  - Authentication and authorization testing

- **cli-tester**: Autonomous CLI tool testing
  - Help text discovery
  - Command execution with various inputs
  - Output and error validation
  - Exit code verification

### Commands

- `/exploratory:browser <context>` - Test web application
- `/exploratory:api <context>` - Test API endpoints
- `/exploratory:cli <context>` - Test CLI tool

### Skills

- **browser-testing-patterns**: Best practices for browser-based testing
- **api-testing-patterns**: Best practices for API testing
- **cli-testing-patterns**: Best practices for CLI testing

## Prerequisites

**Required:**
- Playwright MCP server must be installed and configured in Claude Code

**Optional:**
- OpenAPI/Swagger specifications for comprehensive API testing
- Test data generators for more realistic testing scenarios

## Installation

This plugin is part of the tommy-marketplace. It will be automatically available when you install the marketplace.

## Usage

### Testing a Web Application

```
/exploratory:browser https://myapp.com/dashboard
```

The browser-explorer agent will:
1. Navigate to the specified URL
2. Explore interactive elements (buttons, forms, links)
3. Check for console errors and broken functionality
4. Test accessibility and performance
5. Report findings in markdown format

### Testing an API

```
/exploratory:api https://api.myapp.com/v1
```

Or provide an OpenAPI spec:

```
/exploratory:api ./openapi.yaml
```

The api-explorer agent will:
1. Discover or parse API endpoints
2. Test each endpoint with valid and invalid inputs
3. Verify response schemas and status codes
4. Check authentication and authorization
5. Report findings and potential issues

### Testing a CLI Tool

```
/exploratory:cli npm run build
```

The cli-tester agent will:
1. Execute the command with various inputs
2. Validate output and error messages
3. Check exit codes
4. Test edge cases and error conditions
5. Report findings and suggestions

## Output Format

All agents report findings as markdown in chat:
- Summary of what was tested
- Issues found (categorized by severity)
- Successful validations
- Recommendations for improvements

Users can ask Claude Code to save reports to files if desired.

## License

MIT
