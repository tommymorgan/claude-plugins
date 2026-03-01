---
name: Browser Testing Patterns
description: This skill should be used when performing browser-based exploratory testing of web applications, including functional testing, visual inspection, accessibility checks, and performance analysis. Triggers when testing web UIs, checking for browser bugs, validating WCAG compliance, or measuring Core Web Vitals.
version: 0.2.0
---

# Browser Testing Patterns

## Purpose

Provide systematic patterns and best practices for autonomous browser-based exploratory testing using CLI tools. Guide agents through comprehensive web application testing including functional validation, visual inspection, accessibility compliance, and performance measurement.

## Tools

Browser testing uses three tools, each for a specific purpose:

| Tool | Purpose | Required |
|------|---------|----------|
| [agent-browser](https://github.com/vercel-labs/agent-browser) | Primary browser automation | Always |
| [playwright-cli](https://github.com/microsoft/playwright-cli) | Video demo recording | Only when video requested |
| [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Deep performance profiling | Only for performance scenarios |

See `testing/README.md` for installation instructions.

## Shell Safety

CLI commands run through Bash. Always quote user-controlled values to prevent shell injection:

```bash
# CORRECT — all values quoted
agent-browser -s=my-session open "https://example.com/path?q=search term"
agent-browser -s=my-session fill @e3 "user's input value"
agent-browser -s=my-session eval "document.querySelector('.class').textContent"

# INCORRECT — unquoted values risk injection
agent-browser open $url
agent-browser fill @ref $text
agent-browser eval $script
```

**Rules:**
- Always double-quote URLs, form values, JavaScript expressions, and selectors
- Never interpolate unquoted variables into commands
- This applies to all values from plan files, user input, or page content

## Core Testing Methodology

### Systematic Exploration Approach

Test web applications using a structured layered approach:

1. **Pre-flight check**: Verify agent-browser is installed and functional
2. **Initial reconnaissance**: Navigate to target, capture state
3. **Functional testing**: Interact with elements, test workflows
4. **Accessibility validation**: Check WCAG compliance
5. **Performance measurement**: Analyze Core Web Vitals
6. **Visual inspection**: Detect layout issues
7. **Session cleanup**: Close browser sessions
8. **Reporting**: Categorize and document findings

### Prioritization Framework

Focus testing effort based on user impact:

**Critical (test thoroughly):**
- User authentication and authorization
- Payment and transaction flows
- Data submission and persistence
- Primary user workflows

**Important (test systematically):**
- Navigation and routing
- Form validation and error handling
- Search and filtering
- Content display

**Secondary (spot check):**
- Footer links and secondary pages
- Help documentation
- Administrative features

## Functional Testing Patterns

### Element Interaction Strategy

Test interactive elements systematically using the ref system:

1. **Discover interactive elements**:
   ```bash
   agent-browser -s=test snapshot -i
   ```
   Returns elements with refs: `button "Sign In" [ref=e1]`, `textbox "Email" [ref=e2]`

2. **Click elements by ref**:
   ```bash
   agent-browser -s=test click @e1
   ```

3. **Fill form fields**:
   ```bash
   agent-browser -s=test fill @e2 "test@example.com"
   ```

4. **Re-snapshot after DOM changes**: Refs become stale after navigation or significant DOM mutations. Always re-snapshot before interacting with elements on a changed page:
   ```bash
   agent-browser -s=test snapshot -i
   ```

5. **Keyboard testing**:
   ```bash
   agent-browser -s=test press Tab
   agent-browser -s=test press Enter
   agent-browser -s=test press Escape
   ```

6. **Error states**: Trigger validation errors, check messages

### Console Error Detection

Check for JavaScript errors:

```bash
agent-browser -s=test console error
```

Categorize console errors:
- **Critical**: Breaks functionality (TypeError, ReferenceError)
- **Warning**: Degraded experience (404 for non-critical resources)
- **Info**: Non-blocking issues (deprecation warnings)

### Network Request Validation

Analyze network traffic:

```bash
agent-browser -s=test network requests
```

Check for:
- Failed requests (404, 500 errors)
- Slow requests (>2 seconds)
- Large responses (>1MB)
- Excessive request count (>50 per page)

## Accessibility Testing Patterns

### WCAG 2.1 Level AA Checklist

Test for common accessibility violations:

**Perceivable:**
- All images have alt text
- Video/audio has captions or transcripts
- Color contrast meets 4.5:1 ratio
- Content is not conveyed by color alone

**Operable:**
- All functionality available via keyboard
- No keyboard traps
- Sufficient time for interactions
- Focus visible on interactive elements

**Understandable:**
- Form labels are clear and associated
- Error messages are helpful
- Consistent navigation
- Predictable behavior

**Robust:**
- Valid HTML structure
- Proper heading hierarchy (h1 → h2 → h3)
- ARIA labels where needed
- Form controls have accessible names

### Keyboard Navigation Testing

Test keyboard usability:

```bash
# Test tab navigation
agent-browser -s=test press Tab
agent-browser -s=test press Shift+Tab

# Test activation
agent-browser -s=test press Enter

# Test dismissal
agent-browser -s=test press Escape

# Test within components
agent-browser -s=test press ArrowDown
agent-browser -s=test press ArrowUp
```

Verify:
- Focus is visible (outline/highlight)
- Tab order is logical
- All interactive elements reachable
- No keyboard traps

## Performance Testing Patterns

### Two-Tier Profiling Approach

**Tier 1: Basic profiling** (always available via agent-browser):

```bash
agent-browser -s=test eval "JSON.stringify({
  lcp: (() => { const e = performance.getEntriesByType('largest-contentful-paint').slice(-1)[0]; return e ? (e.renderTime || e.startTime) : 0; })(),
  cls: performance.getEntriesByType('layout-shift')
    .reduce((sum, e) => sum + (e.hadRecentInput ? 0 : e.value), 0)
})"
```

**Thresholds (Google standards):**
- LCP: <2.5s (good), 2.5-4s (needs improvement), >4s (poor)
- CLS: <0.1 (good), 0.1-0.25 (needs improvement), >0.25 (poor)

**INP** (Interaction to Next Paint) measures responsiveness across all interactions. It cannot be measured with a single `eval` call — it requires observing user interactions over time via PerformanceObserver. Use Lighthouse (Tier 2) for INP measurement, or check for long tasks as a proxy:

```bash
agent-browser -s=test eval "JSON.stringify(
  performance.getEntriesByType('longtask').map(t => ({ duration: t.duration, startTime: t.startTime }))
)"
```

**INP thresholds:** <200ms (good), 200-500ms (needs improvement), >500ms (poor)

**Tier 2: Deep profiling** (conditional, via chrome-devtools-mcp):

When scenarios mention Lighthouse, memory analysis, or detailed performance tracing:

1. Use ToolSearch to load chrome-devtools-mcp:
   ```
   ToolSearch(query: "+chrome-devtools")
   ```

2. If tools are found:
   - `lighthouse_audit` — full Lighthouse analysis
   - `performance_start_trace` / `performance_stop_trace` — detailed tracing
   - `take_memory_snapshot` — memory profiling

3. If chrome-devtools-mcp is not available:
   - Fall back to Tier 1 metrics
   - Note in report that deep profiling was unavailable

Do NOT load chrome-devtools-mcp for non-performance scenarios.

### Network Performance Analysis

```bash
agent-browser -s=test network requests
```

Check for:
- Total request count (>50 = potential issue)
- Total data transferred (>2MB = optimization needed)
- Slow requests (>2s)
- Failed requests (404, 500)
- Unnecessary requests (duplicate fetches)

## Visual Testing Patterns

### Layout Issue Detection

**Look for:**
- Overlapping elements (z-index issues)
- Cut-off text or content (overflow problems)
- Elements positioned outside viewport
- Missing spacing (elements touching)
- Inconsistent styling

**When to screenshot:**
- Visual issue detected (not routinely)
- Layout appears broken
- Content is cut off or overlapping
- Responsive design fails

### Screenshot Strategy

```bash
agent-browser -s=test screenshot
```

- ONLY when visual issue detected
- Reference in report clearly

Avoid:
- Screenshots of every action
- Screenshots with no issues
- Redundant screenshots

## Testing Depth Management

### Single Page Testing (depth=1)

Test only the provided URL:
- Complete functional testing
- Full accessibility audit
- Performance measurement
- Visual inspection
- Console error check

### Shallow Crawl (depth=2)

Test main page + linked pages:
- Identify all links on main page
- Follow internal links (same domain)
- Apply smoke tests to linked pages
- Report critical issues on any page

### Deep Crawl (depth=3+)

Recursive exploration:
- Track visited URLs (avoid loops)
- Follow links up to specified depth
- Prioritize critical flows over exhaustive crawling
- Respect time limits (don't test forever)

## Session Cleanup

Always close sessions after testing, even if errors occurred:

```bash
agent-browser -s=test close 2>/dev/null || true
```

If the `close` command fails (e.g., daemon already stopped), verify no orphaned processes remain:

```bash
pgrep -f "agent-browser.*-s=test" && echo "WARNING: orphaned agent-browser process found" || true
```

## Reporting Best Practices

### Categorize by Severity

**Critical:**
- Prevents core functionality
- Blocks users from completing tasks
- Exposes security vulnerabilities
- Causes data loss

**Warning:**
- Degrades user experience
- Inconsistent behavior
- Poor error messages
- Performance issues

**Info:**
- Best practice violations
- Accessibility improvements
- Performance optimizations
- UX enhancements

### Provide Actionable Details

For each issue include:
- **Location**: Specific element ref or URL
- **Reproduction**: Steps to reproduce
- **Expected vs Actual**: What should happen vs what happens
- **Impact**: How this affects users
- **Priority**: Critical/High/Medium/Low

### Balance Thoroughness with Clarity

Report both problems and successes:
- Don't only report failures (show what works)
- Don't report every minor issue (focus on impactful findings)
- Group related issues (don't duplicate similar problems)
- Prioritize by user impact, not alphabetically

## Additional Resources

### Reference Files

For detailed testing techniques, consult:
- **`references/agent-browser-cli.md`** - Complete agent-browser CLI command reference
- **`references/accessibility-testing.md`** - Comprehensive WCAG testing guide
- **`references/performance-metrics.md`** - Detailed performance analysis patterns (two-tier approach)

## Quick Reference

**Testing checklist:**
- [ ] Pre-flight check (agent-browser installed and functional)
- [ ] Navigate to target URL
- [ ] Capture initial state (snapshot, console, network)
- [ ] Test interactive elements
- [ ] Validate accessibility
- [ ] Measure performance
- [ ] Inspect for visual issues
- [ ] Clean up browser session
- [ ] Report findings by severity

**Remember:** Focus on finding real bugs autonomously. Be thorough but scoped to context. Report actionably. Always quote values in CLI commands.
