# Accessibility Testing Guide

Comprehensive guide for testing WCAG 2.1 Level AA compliance.

## WCAG 2.1 Principles

### 1. Perceivable

Information and UI components must be presentable to users in ways they can perceive.

**Tests:**
- **Images**: All `<img>` tags have meaningful alt text
- **Form labels**: All inputs have associated `<label>` elements
- **Color contrast**: Text meets 4.5:1 ratio (3:1 for large text)
- **Audio/Video**: Captions or transcripts available

**Detection methods:**
- Use browser_snapshot to find images without alt
- Check form inputs for aria-label or associated labels
- Report missing text alternatives

### 2. Operable

UI components and navigation must be operable.

**Tests:**
- **Keyboard access**: All functionality available via keyboard
- **No keyboard traps**: Users can tab away from all elements
- **Timing**: Sufficient time for reading and interaction
- **Seizures**: No flashing content >3 times per second

**Detection methods:**
- Use browser_press_key to test Tab navigation
- Verify focus moves logically through page
- Test Escape key closes modals/dropdowns
- Check Enter activates buttons/links

### 3. Understandable

Information and operation of UI must be understandable.

**Tests:**
- **Labels**: Form controls have clear labels
- **Error messages**: Validation errors are specific and helpful
- **Consistent navigation**: Navigation is predictable
- **Input assistance**: Help text provided for complex inputs

**Detection methods:**
- Check form labels are descriptive
- Trigger validation errors and verify messages
- Test navigation consistency across pages

### 4. Robust

Content must be robust enough for assistive technologies.

**Tests:**
- **Valid HTML**: Proper element nesting and structure
- **Heading hierarchy**: h1 → h2 → h3 (no skipping)
- **ARIA**: Proper ARIA labels where needed
- **Name/Role/Value**: Form controls have accessible names

**Detection methods:**
- Use browser_snapshot to check accessibility tree
- Verify heading levels in sequence
- Check ARIA attributes on custom controls

## Automated Checks

### Alt Text Validation

```javascript
// Find images without alt text
const result = await browser_evaluate({
  function: `() => {
    const images = Array.from(document.querySelectorAll('img'));
    const missing = images.filter(img => !img.alt || img.alt.trim() === '');
    return missing.map(img => ({
      src: img.src,
      location: img.getBoundingClientRect()
    }));
  }`
});
```

### Form Label Validation

```javascript
// Find inputs without labels
const result = await browser_evaluate({
  function: `() => {
    const inputs = Array.from(document.querySelectorAll('input, textarea, select'));
    const unlabeled = inputs.filter(input => {
      const hasLabel = !!document.querySelector(\`label[for="\${input.id}"]\`);
      const hasAriaLabel = !!input.getAttribute('aria-label');
      return !hasLabel && !hasAriaLabel && input.type !== 'hidden';
    });
    return unlabeled.map(i => ({
      type: i.type,
      name: i.name,
      id: i.id
    }));
  }`
});
```

### Heading Hierarchy Check

```javascript
// Check heading order
const result = await browser_evaluate({
  function: `() => {
    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
    const levels = headings.map(h => parseInt(h.tagName.slice(1)));
    const issues = [];
    for (let i = 1; i < levels.length; i++) {
      if (levels[i] > levels[i-1] + 1) {
        issues.push(\`Heading skip: h\${levels[i-1]} to h\${levels[i]}\`);
      }
    }
    return { headings: levels, issues };
  }`
});
```

## Keyboard Navigation Testing

### Tab Order Testing

```markdown
1. Press Tab to move focus forward
2. Press Shift+Tab to move focus backward
3. Verify logical tab order (top to bottom, left to right)
4. Ensure all interactive elements are reachable
5. Check focus is visible (outline, highlight, or border)
```

### Keyboard Shortcuts Testing

Common keyboard shortcuts to test:
- Enter: Submit forms, activate buttons
- Escape: Close modals, cancel operations
- Space: Toggle checkboxes, activate buttons
- Arrow keys: Navigate within components (dropdowns, carousels)

## Color Contrast Validation

### Minimum Ratios

**WCAG 2.1 Level AA:**
- Normal text: 4.5:1
- Large text (18pt+ or 14pt+ bold): 3:1
- UI components and graphics: 3:1

### Testing Method

```javascript
// Check color contrast (requires color analysis)
const result = await browser_evaluate({
  function: `() => {
    // Get computed styles
    const element = document.querySelector('.text-element');
    const styles = window.getComputedStyle(element);
    return {
      color: styles.color,
      backgroundColor: styles.backgroundColor,
      fontSize: styles.fontSize,
      fontWeight: styles.fontWeight
    };
  }`
});

// Report if contrast appears low (manual judgment or calculation needed)
```

## Common Accessibility Violations

### Missing Alt Text

**Issue**: Images without alternative text
**Impact**: Screen readers can't describe images
**Detection**: Find img elements without alt attribute
**Fix**: Add descriptive alt text

### Unlabeled Form Controls

**Issue**: Inputs without associated labels
**Impact**: Screen readers can't identify input purpose
**Detection**: Find inputs without label or aria-label
**Fix**: Add proper label element or aria-label

### Poor Heading Hierarchy

**Issue**: Skipping heading levels (h1 → h3)
**Impact**: Confuses screen reader navigation
**Detection**: Check heading sequence
**Fix**: Use proper heading order

### Missing Focus Indicators

**Issue**: No visible outline when tabbing
**Impact**: Keyboard users can't see where they are
**Detection**: Tab through page, check visibility
**Fix**: Ensure :focus styles are visible

### Low Color Contrast

**Issue**: Text hard to read against background
**Impact**: Users with vision impairments struggle
**Detection**: Calculate contrast ratios
**Fix**: Adjust colors to meet 4.5:1 ratio

## Reporting Template

```markdown
## Accessibility Issues ♿

### Missing Alt Text - Critical
- **Count**: 12 images
- **Impact**: Screen readers cannot describe images
- **Examples**:
  - Logo image at top of page
  - Product images in gallery
  - Icon images in navigation
- **Fix**: Add descriptive alt attributes

### Unlabeled Inputs - High
- **Count**: 3 form controls
- **Impact**: Screen readers can't identify field purpose
- **Location**:
  - Search input in header
  - Email input in footer
  - Filter dropdown in sidebar
- **Fix**: Add associated label elements

### Keyboard Navigation - Medium
- **Issue**: Modal dialog traps focus
- **Impact**: Keyboard users cannot exit modal with Tab
- **Fix**: Add keyboard event handler for Escape key
```
