# Performance Metrics Guide

Detailed guide for measuring and analyzing web application performance.

## Core Web Vitals

### Largest Contentful Paint (LCP)

**What it measures**: Time until largest content element renders

**How to measure:**
```javascript
const lcp = await browser_evaluate({
  function: `() => {
    const entries = performance.getEntriesByType('largest-contentful-paint');
    return entries[entries.length - 1]?.renderTime || 0;
  }`
});
```

**Thresholds:**
- Good: <2.5 seconds
- Needs improvement: 2.5-4 seconds
- Poor: >4 seconds

**Common causes of slow LCP:**
- Large images without optimization
- Render-blocking JavaScript/CSS
- Slow server response time
- Client-side rendering delays

### First Input Delay (FID)

**What it measures**: Time from first user interaction to browser response

**How to measure:**
```javascript
const fid = await browser_evaluate({
  function: `() => {
    const fidEntry = performance.getEntriesByType('first-input')[0];
    return fidEntry ? fidEntry.processingStart - fidEntry.startTime : null;
  }`
});
```

**Thresholds:**
- Good: <100ms
- Needs improvement: 100-300ms
- Poor: >300ms

**Common causes:**
- Heavy JavaScript execution
- Long tasks blocking main thread
- Large bundle sizes

### Cumulative Layout Shift (CLS)

**What it measures**: Visual stability (unexpected layout shifts)

**How to measure:**
```javascript
const cls = await browser_evaluate({
  function: `() => {
    const shifts = performance.getEntriesByType('layout-shift');
    return shifts.reduce((sum, entry) => sum + (entry.hadRecentInput ? 0 : entry.value), 0);
  }`
});
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

## Additional Performance Metrics

### First Contentful Paint (FCP)

**What it measures**: Time until first content renders

```javascript
const fcp = await browser_evaluate({
  function: `() => {
    const paint = performance.getEntriesByType('paint');
    return paint.find(e => e.name === 'first-contentful-paint')?.startTime || 0;
  }`
});
```

**Threshold**: <1.8s is good

### Time to Interactive (TTI)

**What it measures**: Time until page is fully interactive

```javascript
const tti = await browser_evaluate({
  function: `() => {
    return performance.timing.domInteractive - performance.timing.navigationStart;
  }`
});
```

**Threshold**: <3.8s is good

### Total Blocking Time (TBT)

**What it measures**: Total time main thread is blocked

**Manual calculation**: Sum of long tasks (>50ms) minus 50ms

**Threshold**: <200ms is good

## Network Performance Analysis

### Request Analysis

Using browser_network_requests:

```markdown
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
```

### Request Waterfall Analysis

Look for:
- **Sequential loading**: Resources loading one at a time (slow)
- **Blocking resources**: JavaScript/CSS delaying other loads
- **Redundant requests**: Same resource fetched multiple times
- **Large resources**: Individual files >500KB

## Bundle Size Analysis

### JavaScript Bundle

```javascript
const bundles = await browser_network_requests({});
const jsFiles = bundles.filter(r => r.url.endsWith('.js'));
const totalJS = jsFiles.reduce((sum, file) => sum + file.size, 0);
```

**Thresholds:**
- Good: <200KB gzipped
- Warning: 200-500KB
- Poor: >500KB

### CSS Bundle

```javascript
const cssFiles = bundles.filter(r => r.url.endsWith('.css'));
const totalCSS = cssFiles.reduce((sum, file) => sum + file.size, 0);
```

**Thresholds:**
- Good: <50KB
- Warning: 50-100KB
- Poor: >100KB

## Memory and CPU Usage

### Memory Leaks

```javascript
// Take memory snapshot
const memory = await browser_evaluate({
  function: `() => {
    if (performance.memory) {
      return {
        usedJSHeapSize: performance.memory.usedJSHeapSize,
        totalJSHeapSize: performance.memory.totalJSHeapSize,
        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
      };
    }
    return null;
  }`
});
```

**Signs of memory leaks:**
- Memory usage grows over time
- Page becomes sluggish after interaction
- Heap size approaches limit

### Long Tasks

```javascript
// Find long tasks blocking main thread
const longTasks = await browser_evaluate({
  function: `() => {
    const tasks = performance.getEntriesByType('longtask');
    return tasks.map(t => ({
      duration: t.duration,
      startTime: t.startTime
    }));
  }`
});
```

**Threshold:** Tasks >50ms are concerning, >300ms are critical

## Performance Testing Workflow

### Complete Performance Audit

```markdown
1. Navigate to page
2. Wait for full page load
3. Measure Core Web Vitals (LCP, FID, CLS)
4. Analyze network requests
5. Check bundle sizes
6. Test memory usage
7. Identify long tasks
8. Report findings with thresholds
```

### Performance Report Template

```markdown
## Performance Issues ⚡

### Core Web Vitals
- **LCP**: 3.2s (Poor - threshold: <2.5s)
- **FID**: 85ms (Good)
- **CLS**: 0.15 (Needs Improvement - threshold: <0.1)

### Network Performance
- **Total Requests**: 127 (Warning - threshold: <50)
- **Total Size**: 2.8MB (Warning - threshold: <1MB)
- **Failed Requests**: 3 (2× 404 for images, 1× 500 for API)
- **Slow Requests**: 5 requests >2s

### Bundle Sizes
- **JavaScript**: 450KB (Warning - threshold: <200KB)
- **CSS**: 35KB (Good)
- **Images**: 1.9MB (Optimize - threshold: <500KB per page)

### Recommendations
1. Optimize images (use WebP, lazy loading)
2. Code splitting to reduce initial JS bundle
3. Fix layout shift from late-loading ads
4. Add caching headers for static assets
```
