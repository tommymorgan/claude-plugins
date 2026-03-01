# agent-browser CLI Reference

Complete reference for using agent-browser CLI in browser testing.

## Overview

[agent-browser](https://github.com/vercel-labs/agent-browser) is a CLI tool purpose-built for AI agents. It provides browser automation through shell commands, using a ref-based system for element interaction.

## Installation

```bash
npm install -g @vercel-labs/agent-browser
```

## The Ref System

agent-browser uses temporary element references (refs) for interaction:

1. Run `snapshot -i` to get interactive elements with refs
2. Elements appear as: `button "Sign In" [ref=e1]`, `textbox "Email" [ref=e2]`
3. Use refs in commands: `click @e1`, `fill @e2 "text"`
4. **Refs become stale** after navigation or DOM mutations — always re-snapshot

## Named Sessions

Use named sessions (`-s=name`) to isolate concurrent agents:

```bash
agent-browser -s=my-agent open "https://example.com"
agent-browser -s=my-agent snapshot -i
agent-browser -s=my-agent close
```

Different agents should use different session names to prevent conflicts.

## Navigation

### open / goto / navigate

Navigate to a URL.

```bash
agent-browser -s=test open "https://example.com"
agent-browser -s=test goto "https://example.com/page"
```

**Best practices:**
- Always quote URLs
- Wait for page load before interacting
- Check for successful load (not 404/500)

### go-back / go-forward / reload

```bash
agent-browser -s=test go-back
agent-browser -s=test go-forward
agent-browser -s=test reload
```

### close

Close the browser session and stop daemon if no other sessions are active.

```bash
agent-browser -s=test close
```

## Interaction

### click

Click an element by ref.

```bash
agent-browser -s=test click @e1
agent-browser -s=test dblclick @e2
```

**Best practices:**
- Get ref from snapshot first
- Re-snapshot after clicks that trigger navigation

### fill

Clear field and enter text (use for form fields).

```bash
agent-browser -s=test fill @e3 "test@example.com"
```

### type

Append text without clearing (use for search boxes, incremental input).

```bash
agent-browser -s=test type "search query"
```

### press

Press keyboard keys.

```bash
agent-browser -s=test press Tab
agent-browser -s=test press Enter
agent-browser -s=test press Escape
agent-browser -s=test press Shift+Tab
agent-browser -s=test press ArrowDown
```

**Common keys:**
- Tab, Shift+Tab (focus navigation)
- Enter (activate/submit)
- Escape (close modals)
- ArrowLeft, ArrowRight, ArrowUp, ArrowDown

### hover

Hover over an element.

```bash
agent-browser -s=test hover @e4
```

**Use for:**
- Testing tooltips
- Testing hover states
- Triggering dropdown menus

### select

Choose dropdown option.

```bash
agent-browser -s=test select @e5 "Option Text"
```

### check / uncheck

Toggle checkboxes and radio buttons.

```bash
agent-browser -s=test check @e6
agent-browser -s=test uncheck @e7
```

### drag

Drag and drop between elements.

```bash
agent-browser -s=test drag @e8 @e9
```

### upload

Handle file uploads.

```bash
agent-browser -s=test upload "path/to/file.pdf"
```

### scroll

Scroll page or element.

```bash
agent-browser -s=test scroll down
agent-browser -s=test scrollintoview @e10
```

## Inspection

### snapshot

Capture accessibility tree with interactive element refs.

```bash
# Interactive elements only
agent-browser -s=test snapshot -i

# Scoped to CSS selector
agent-browser -s=test snapshot -s "#main-content"
```

**Returns:**
- Accessibility tree with element roles, names, properties
- Refs for interactive elements (e.g., `[ref=e1]`)
- Hierarchical page structure

**Use for:**
- Finding element refs before interaction
- Understanding page structure
- Accessibility analysis

### screenshot

Take a screenshot of the page.

```bash
agent-browser -s=test screenshot
agent-browser -s=test screenshot --full-page
```

**Best practices:**
- Use ONLY when visual issue detected
- Use `--full-page` for layout issues

### console

Get console messages.

```bash
# All errors
agent-browser -s=test console error

# All messages
agent-browser -s=test console
```

**Severity mapping:**
- error: Breaks functionality (TypeError, ReferenceError)
- warning: Degraded experience (deprecation warnings)
- info: Non-blocking issues

### network requests

Get all network requests.

```bash
agent-browser -s=test network requests
```

**Analysis:**
- Failed requests (status >= 400)
- Slow requests (time > 2000ms)
- Large responses (size > 1MB)
- Total request count (>50 = concern)

### errors

Track JavaScript exceptions.

```bash
agent-browser -s=test errors
```

### get

Extract page information.

```bash
agent-browser -s=test get text @e1
agent-browser -s=test get url
agent-browser -s=test get title
```

## Evaluation

### eval

Execute JavaScript in page context.

```bash
agent-browser -s=test eval "document.title"
agent-browser -s=test eval "JSON.stringify(performance.getEntriesByType('largest-contentful-paint'))"
```

**Use for:**
- Measuring performance metrics
- Accessing page state
- Running custom checks

**Safety:**
- Always quote the JavaScript expression
- Return serializable data (use JSON.stringify for objects)

## Waiting

### wait

Wait for conditions before proceeding.

```bash
# Wait for text to appear
agent-browser -s=test wait text "Loading complete"

# Wait for element
agent-browser -s=test wait @e1

# Wait for URL pattern
agent-browser -s=test wait url "/dashboard"

# Wait for network idle
agent-browser -s=test wait networkidle
```

**Best practices:**
- Prefer waiting for specific text or elements over arbitrary timeouts
- Keep waits under 10 seconds when possible

## State Management

### Cookies and Storage

```bash
# Cookies
agent-browser -s=test cookies get
agent-browser -s=test cookies set "name" "value"
agent-browser -s=test cookies clear

# Local storage
agent-browser -s=test storage local get "key"
agent-browser -s=test storage local set "key" "value"
agent-browser -s=test storage local clear
```

### Auth State

```bash
# Save authentication state
agent-browser -s=test state save "logged-in"

# Load saved state
agent-browser -s=test state load "logged-in"
```

## Comparison

### diff

Compare states for regression detection.

```bash
# Compare accessibility trees
agent-browser -s=test diff snapshot

# Compare visual screenshots
agent-browser -s=test diff screenshot

# Compare two URLs
agent-browser -s=test diff url "https://old.example.com" "https://new.example.com"
```

## Profiling

### Built-in profiler

```bash
agent-browser -s=test profiler start
# ... perform actions ...
agent-browser -s=test profiler stop
```

### Tracing

```bash
agent-browser -s=test trace start
# ... perform actions ...
agent-browser -s=test trace stop
```

## Tab Management

```bash
agent-browser -s=test tab list
agent-browser -s=test tab new "https://example.com"
agent-browser -s=test tab close 1
agent-browser -s=test tab switch 0
```

## Network Mocking

```bash
# Mock a route
agent-browser -s=test network route "*/api/users" --status 200 --body '{"users": []}'

# Remove mock
agent-browser -s=test network unroute "*/api/users"
```

## Semantic Locators

Find elements by accessibility properties:

```bash
agent-browser -s=test find role button
agent-browser -s=test find text "Sign In"
agent-browser -s=test find label "Email"
agent-browser -s=test find placeholder "Search..."
```

## Dialog Handling

```bash
agent-browser -s=test dialog accept
agent-browser -s=test dialog dismiss
```

## Common Testing Workflows

### Login Flow

```bash
agent-browser -s=test open "https://app.example.com/login"
agent-browser -s=test snapshot -i
agent-browser -s=test fill @e1 "user@example.com"
agent-browser -s=test fill @e2 "password123"
agent-browser -s=test click @e3
agent-browser -s=test wait url "/dashboard"
agent-browser -s=test console error
agent-browser -s=test snapshot -i
```

### Form Submission

```bash
agent-browser -s=test open "https://app.example.com/form"
agent-browser -s=test snapshot -i
# Fill with valid data
agent-browser -s=test fill @e1 "John Doe"
agent-browser -s=test fill @e2 "john@example.com"
agent-browser -s=test click @e3  # Submit
agent-browser -s=test wait text "Success"
# Test with invalid data
agent-browser -s=test open "https://app.example.com/form"
agent-browser -s=test snapshot -i
agent-browser -s=test fill @e1 ""
agent-browser -s=test click @e3
# Check for error messages
agent-browser -s=test snapshot -i
```

### Navigation Testing

```bash
agent-browser -s=test open "https://app.example.com"
agent-browser -s=test snapshot -i
# Click each nav link
agent-browser -s=test click @e1
agent-browser -s=test console error
agent-browser -s=test go-back
agent-browser -s=test snapshot -i
```
