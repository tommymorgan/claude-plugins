# Playwright MCP Tools Reference

Complete reference for using Playwright MCP tools in browser testing.

## Navigation Tools

### browser_navigate

Navigate to a URL.

**Usage:**
```javascript
await mcp__plugin_compound-engineering_pw__browser_navigate({ url: "https://example.com" });
```

**Best practices:**
- Always wait for navigation to complete before next action
- Check for successful load (not 404/500)
- Use full URLs including protocol (https://)

### browser_navigate_back

Navigate to previous page.

**Usage:**
```javascript
await mcp__plugin_compound-engineering_pw__browser_navigate_back({});
```

**Use when:**
- Testing browser back button functionality
- Returning from deep navigation

## Interaction Tools

### browser_click

Click an element on the page.

**Usage:**
```javascript
await mcp__plugin_compound-engineering_pw__browser_click({
  element: "Submit button",
  ref: "button[type='submit']"
});
```

**Parameters:**
- `element`: Human-readable description
- `ref`: CSS selector from snapshot
- `button`: Optional (left/right/middle)
- `modifiers`: Optional (Alt, Control, Shift)
- `doubleClick`: Optional boolean

**Best practices:**
- Get ref from browser_snapshot first
- Use descriptive element names
- Wait for elements to be visible before clicking

### browser_type

Type text into an input field.

**Usage:**
```javascript
await mcp__plugin_compound-engineering_pw__browser_type({
  element: "Email input",
  ref: "input[name='email']",
  text: "test@example.com",
  submit: false
});
```

**Parameters:**
- `element`: Human-readable description
- `ref`: CSS selector
- `text`: Text to type
- `slowly`: Optional (type character by character)
- `submit`: Optional (press Enter after typing)

### browser_fill_form

Fill multiple form fields at once.

**Usage:**
```javascript
await mcp__plugin_compound-engineering_pw__browser_fill_form({
  fields: [
    { name: "Username", type: "textbox", ref: "input[name='username']", value: "testuser" },
    { name: "Password", type: "textbox", ref: "input[name='password']", value: "password123" },
    { name: "Remember me", type: "checkbox", ref: "input[name='remember']", value: "true" }
  ]
});
```

**Field types:**
- textbox
- checkbox
- radio
- combobox
- slider

### browser_press_key

Press keyboard keys.

**Usage:**
```javascript
await mcp__plugin_compound-engineering_pw__browser_press_key({ key: "Tab" });
await mcp__plugin_compound-engineering_pw__browser_press_key({ key: "Enter" });
await mcp__plugin_compound-engineering_pw__browser_press_key({ key: "Escape" });
```

**Common keys:**
- Tab, Shift+Tab (focus navigation)
- Enter (activate/submit)
- Escape (close modals)
- ArrowLeft, ArrowRight, ArrowUp, ArrowDown

### browser_hover

Hover over an element.

**Usage:**
```javascript
await mcp__plugin_compound-engineering_pw__browser_hover({
  element: "Tooltip trigger",
  ref: ".tooltip-icon"
});
```

**Use for:**
- Testing tooltips
- Testing hover states
- Triggering dropdown menus

## Inspection Tools

### browser_snapshot

Capture accessibility snapshot of current page.

**Usage:**
```javascript
const snapshot = await mcp__plugin_compound-engineering_pw__browser_snapshot({});
```

**Returns:**
- Accessibility tree with all interactive elements
- Element roles, names, and properties
- Hierarchical structure

**Use for:**
- Finding element selectors (refs)
- Understanding page structure
- Accessibility analysis

### browser_take_screenshot

Take a screenshot of the page or element.

**Usage:**
```javascript
await mcp__plugin_compound-engineering_pw__browser_take_screenshot({
  filename: "issue-screenshot.png",
  fullPage: true
});
```

**Parameters:**
- `filename`: Optional filename
- `fullPage`: Capture entire page (scrolls automatically)
- `element`/`ref`: Screenshot specific element
- `type`: png or jpeg

**Best practices:**
- Use ONLY when visual issue detected
- Use descriptive filenames
- Use fullPage for layout issues
- Use element screenshots for specific component issues

### browser_console_messages

Get console messages.

**Usage:**
```javascript
const messages = await mcp__plugin_compound-engineering_pw__browser_console_messages({
  level: "error"
});
```

**Levels:**
- error: Only errors
- warning: Warnings and errors
- info: Info, warnings, and errors
- debug: Everything

**Returns:**
Array of console messages with type, text, and location.

### browser_network_requests

Get all network requests.

**Usage:**
```javascript
const requests = await mcp__plugin_compound-engineering_pw__browser_network_requests({
  includeStatic: false
});
```

**Returns:**
- URL, method, status code
- Response time
- Response size
- Request/response headers

**Analysis:**
- Failed requests (status >= 400)
- Slow requests (time > 2000ms)
- Large responses (size > 1MB)

## Evaluation Tools

### browser_evaluate

Execute JavaScript in page context.

**Usage:**
```javascript
const vitals = await mcp__plugin_compound-engineering_pw__browser_evaluate({
  function: `() => {
    const paint = performance.getEntriesByType('paint');
    const fcp = paint.find(e => e.name === 'first-contentful-paint');
    return {
      fcp: fcp?.startTime,
      domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart
    };
  }`
});
```

**Use for:**
- Measuring performance metrics
- Accessing page state
- Running custom checks

**Safety:**
- Use arrow functions: `() => { }`
- Return serializable data only
- Handle errors in JavaScript code

## Waiting and Timing Tools

### browser_wait_for

Wait for conditions.

**Usage:**
```javascript
// Wait for text to appear
await mcp__plugin_compound-engineering_pw__browser_wait_for({ text: "Loading complete" });

// Wait for text to disappear
await mcp__plugin_compound-engineering_pw__browser_wait_for({ textGone: "Loading..." });

// Wait for time
await mcp__plugin_compound-engineering_pw__browser_wait_for({ time: 2 });
```

**Use for:**
- Waiting for async content to load
- Waiting for animations to complete
- Waiting for loading states to finish

**Best practices:**
- Prefer waiting for specific text over arbitrary timeouts
- Use textGone for loading indicators
- Keep waits under 10 seconds when possible

## Testing Workflows

### Login Flow Testing

```markdown
1. Navigate to login page
2. Take snapshot to find form fields
3. Fill email and password using browser_fill_form
4. Click login button
5. Wait for navigation or error message
6. Verify successful login (check URL change, user menu, etc.)
7. Check console for auth errors
```

### Form Submission Testing

```markdown
1. Navigate to form page
2. Identify all form fields via snapshot
3. Test with valid data (should succeed)
4. Test with invalid data (should show errors)
5. Test with missing required fields (should prevent submission)
6. Verify error messages are helpful
7. Check form resets or preserves data appropriately
```

### Navigation Testing

```markdown
1. Capture snapshot to find all links
2. Click each navigation link
3. Verify page loads correctly (no 404)
4. Check console for errors
5. Verify back button works
6. Test breadcrumbs if present
```

## Common Issues and Detection

### Broken Links

```markdown
Detection:
1. Get all network_requests after page load
2. Filter for status >= 400
3. Report 404 Not Found and 500 errors

Severity:
- Critical: Broken functionality (404 for API endpoints)
- Warning: Broken links (404 for internal pages)
- Info: Missing assets (404 for images/fonts)
```

### JavaScript Errors

```markdown
Detection:
1. Get console_messages with level "error"
2. Categorize by error type (TypeError, ReferenceError, etc.)
3. Check if error prevents functionality

Severity:
- Critical: Prevents page from working
- High: Breaks specific feature
- Medium: Degraded experience
- Low: Non-blocking errors
```

### Layout Issues

```markdown
Detection:
1. Take snapshot or screenshot
2. Look for accessibility tree anomalies
3. Check for elements with role "none" when they should be interactive
4. Verify heading hierarchy

Common issues:
- Overlapping elements
- Text cut off
- Elements outside viewport
- Broken responsive design
```

## Additional Resources

For comprehensive testing guides, see:
- **`references/accessibility-testing.md`** - Complete WCAG testing procedures
- **`references/performance-metrics.md`** - Detailed performance analysis techniques
