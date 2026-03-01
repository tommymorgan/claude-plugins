# Performance Metrics Guide

Detailed guide for measuring and analyzing web application performance using a two-tier profiling approach.

## Two-Tier Profiling

| Tier | Tool | When to Use | Capabilities |
|------|------|-------------|-------------|
| **Tier 1: Basic** | `agent-browser eval` | Always available, default for all performance checks | Core Web Vitals, network analysis, memory/CPU checks |
| **Tier 2: Deep** | chrome-devtools-mcp | Performance-focused scenarios, Lighthouse audits, detailed tracing | Lighthouse, performance tracing, memory snapshots, CrUX data |

### When to use Tier 2

Load chrome-devtools-mcp via ToolSearch only when the scenario explicitly mentions:
- "Lighthouse audit" or "Lighthouse score"
- "performance trace" or "detailed tracing"
- "memory snapshot" or "memory leak investigation"
- "CrUX data" or "real-user metrics"

```
ToolSearch(query: "+chrome-devtools")
```

If chrome-devtools-mcp tools are found, use:
- `lighthouse_audit` — full Lighthouse analysis with scores
- `performance_start_trace` / `performance_stop_trace` — Chrome DevTools tracing
- `take_memory_snapshot` — heap snapshot for memory analysis

If chrome-devtools-mcp is not available, fall back to Tier 1 and note in the report that deep profiling was unavailable.

## Tier 1: Basic Profiling (agent-browser)

### Core Web Vitals

#### Largest Contentful Paint (LCP)

**What it measures**: Time until largest content element renders

```bash
agent-browser -s=test eval "JSON.stringify({
  lcp: (() => { const e = performance.getEntriesByType('largest-contentful-paint').slice(-1)[0]; return e ? (e.renderTime || e.startTime) : 0; })()
})"
```

**Note:** `renderTime` can be 0 for cross-origin images without `Timing-Allow-Origin` headers. Using `renderTime || startTime` ensures accurate measurement in those cases.

**Thresholds:**
- Good: <2.5 seconds
- Needs improvement: 2.5-4 seconds
- Poor: >4 seconds

**Common causes of slow LCP:**
- Large images without optimization
- Render-blocking JavaScript/CSS
- Slow server response time
- Client-side rendering delays

#### Interaction to Next Paint (INP)

**What it measures**: Responsiveness across all user interactions (replaced FID in March 2024)

INP requires a PerformanceObserver to track interactions over time, so it cannot be captured with a single `eval` call. Use Lighthouse (Tier 2) for accurate INP measurement, or check for long tasks as a proxy:

```bash
agent-browser -s=test eval "JSON.stringify(
  performance.getEntriesByType('longtask').map(t => ({
    duration: t.duration,
    startTime: t.startTime
  }))
)"
```

**Thresholds:**
- Good: <200ms
- Needs improvement: 200-500ms
- Poor: >500ms

**Common causes:**
- Heavy JavaScript execution
- Long tasks blocking main thread
- Large bundle sizes
- Expensive event handlers

#### Cumulative Layout Shift (CLS)

**What it measures**: Visual stability (unexpected layout shifts)

```bash
agent-browser -s=test eval "JSON.stringify({
  cls: performance.getEntriesByType('layout-shift')
    .reduce((sum, entry) => sum + (entry.hadRecentInput ? 0 : entry.value), 0)
})"
```

**Thresholds:**
- Good: <0.1
- Needs improvement: 0.1-0.25
- Poor: >0.25

**Common causes:**
- Images without dimensions
- Ads or embeds that load late
- Web fonts causing FOIT/FOUT
- Dynamic content injection

### Additional Performance Metrics

#### First Contentful Paint (FCP)

```bash
agent-browser -s=test eval "JSON.stringify({
  fcp: performance.getEntriesByType('paint')
    .find(e => e.name === 'first-contentful-paint')?.startTime || 0
})"
```

**Threshold**: <1.8s is good

#### DOM Interactive

**What it measures**: Time until the HTML document is fully parsed (DOM ready). This is not the same as Time to Interactive (TTI), which was a Lighthouse-computed metric deprecated in favor of TBT.

```bash
agent-browser -s=test eval "JSON.stringify({
  domInteractive: performance.getEntriesByType('navigation')[0]?.domInteractive || 0
})"
```

**Threshold**: <3.8s is good

#### Total Blocking Time (TBT)

**Manual calculation**: Sum of long tasks (>50ms) minus 50ms

**Threshold**: <200ms is good

### Network Performance Analysis

#### Request Analysis

```bash
agent-browser -s=test network requests
```

Analyze:
1. **Total requests**: Count of all requests
   - Good: <50 requests
   - Warning: 50-100 requests
   - Poor: >100 requests

2. **Total size**: Sum of all response sizes
   - Good: <1MB
   - Warning: 1-3MB
   - Poor: >3MB

3. **Failed requests**: Status >= 400
   - Critical: Any failed requests blocking functionality
   - Warning: Failed non-critical resources

4. **Slow requests**: Response time >2s
   - Critical: API calls >2s
   - Warning: Images/assets >2s

5. **Caching**: Check cache headers
   - Report resources not cached

#### Request Waterfall Analysis

Look for:
- **Sequential loading**: Resources loading one at a time (slow)
- **Blocking resources**: JavaScript/CSS delaying other loads
- **Redundant requests**: Same resource fetched multiple times
- **Large resources**: Individual files >500KB

### Bundle Size Analysis

#### JavaScript Bundle

```bash
agent-browser -s=test eval "JSON.stringify(
  performance.getEntriesByType('resource')
    .filter(r => r.name.endsWith('.js'))
    .map(r => ({ url: r.name, size: r.transferSize }))
)"
```

**Thresholds:**
- Good: <200KB gzipped
- Warning: 200-500KB
- Poor: >500KB

#### CSS Bundle

**Thresholds:**
- Good: <50KB
- Warning: 50-100KB
- Poor: >100KB

### Memory and CPU Usage

#### Memory Usage

```bash
agent-browser -s=test eval "JSON.stringify(
  performance.memory ? {
    usedJSHeapSize: performance.memory.usedJSHeapSize,
    totalJSHeapSize: performance.memory.totalJSHeapSize,
    jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
  } : null
)"
```

**Signs of memory leaks:**
- Memory usage grows over time
- Page becomes sluggish after interaction
- Heap size approaches limit

#### Long Tasks

```bash
agent-browser -s=test eval "JSON.stringify(
  performance.getEntriesByType('longtask').map(t => ({
    duration: t.duration,
    startTime: t.startTime
  }))
)"
```

**Threshold:** Tasks >50ms are concerning, >300ms are critical

#### Built-in Profiler

agent-browser includes a built-in CPU profiler:

```bash
agent-browser -s=test profiler start
# ... perform user interactions ...
agent-browser -s=test profiler stop
```

## Tier 2: Deep Profiling (chrome-devtools-mcp)

### Loading chrome-devtools-mcp

Only load when the scenario requires deep analysis:

```
ToolSearch(query: "+chrome-devtools")
```

### Lighthouse Audit

Full automated audit covering Performance, Accessibility, Best Practices, SEO:

```
lighthouse_audit()
```

Returns scores and actionable recommendations across all categories.

### Performance Tracing

Detailed Chrome DevTools performance trace:

```
performance_start_trace()
# ... perform user interactions ...
performance_stop_trace()
performance_analyze_insight()
```

Returns timeline data, flame charts, and bottleneck analysis.

### Memory Snapshots

Heap snapshot for memory leak investigation:

```
take_memory_snapshot()
```

Returns detailed heap analysis: object counts, retained sizes, and potential leak sources.

### When Deep Profiling is Unavailable

If chrome-devtools-mcp is not configured, the report should note:

```markdown
**Note:** Deep profiling (Lighthouse, performance tracing, memory snapshots) was not available.
Results below use basic Core Web Vitals measurement via agent-browser.
To enable deep profiling, configure chrome-devtools-mcp. See testing/README.md.
```

## Performance Testing Workflow

### Complete Performance Audit

1. Navigate to page
2. Wait for full page load
3. Measure Core Web Vitals via agent-browser eval (Tier 1)
4. Analyze network requests
5. Check bundle sizes
6. Test memory usage
7. Identify long tasks
8. If deep analysis needed: load chrome-devtools-mcp, run Lighthouse and tracing (Tier 2)
9. Report findings with thresholds

### Performance Report Template

```markdown
## Performance Issues

### Core Web Vitals
- **LCP**: 3.2s (Poor - threshold: <2.5s)
- **INP**: 150ms (Good - threshold: <200ms)
- **CLS**: 0.15 (Needs Improvement - threshold: <0.1)

### Network Performance
- **Total Requests**: 127 (Warning - threshold: <50)
- **Total Size**: 2.8MB (Warning - threshold: <1MB)
- **Failed Requests**: 3 (2x 404 for images, 1x 500 for API)
- **Slow Requests**: 5 requests >2s

### Bundle Sizes
- **JavaScript**: 450KB (Warning - threshold: <200KB)
- **CSS**: 35KB (Good)
- **Images**: 1.9MB (Optimize - threshold: <500KB per page)

### Deep Profiling (if available)
- **Lighthouse Performance Score**: 72/100
- **Memory**: 45MB heap used (no leaks detected)
- **Long Tasks**: 3 tasks >100ms during initial load

### Recommendations
1. Optimize images (use WebP, lazy loading)
2. Code splitting to reduce initial JS bundle
3. Fix layout shift from late-loading ads
4. Add caching headers for static assets
```
