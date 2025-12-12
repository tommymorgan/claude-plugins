# CLI Output Validation

Patterns for validating command-line tool output correctness and formatting.

## Output Stream Validation

### stdout vs stderr

Verify correct stream usage:

**stdout (file descriptor 1):**
- Normal program output
- Data meant for processing
- Success messages

**stderr (file descriptor 2):**
- Error messages
- Warnings
- Diagnostic information
- Progress indicators (debatable)

### Testing Stream Usage

```bash
# Capture stdout only
OUTPUT=$(command 2>/dev/null)

# Capture stderr only
ERRORS=$(command 2>&1 >/dev/null)

# Capture both separately
OUTPUT=$(command 2>/dev/null)
ERRORS=$(command 2>&1 >/dev/null)

# Verify errors go to stderr
if [ -n "$ERRORS" ]; then
  echo "Errors correctly sent to stderr: $ERRORS"
fi
```

## Format Validation

### JSON Output

Validate JSON formatting:

```bash
# Test JSON is valid
command --json | jq . >/dev/null

# Parse and validate structure
OUTPUT=$(command --json)
echo "$OUTPUT" | jq '.users | length' # Should work

# Check required fields
echo "$OUTPUT" | jq '.id, .name' # Should exist
```

**Report issues:**
- Invalid JSON syntax
- Missing required fields
- Inconsistent structure
- Type mismatches

### CSV Output

Validate CSV formatting:

```bash
# Check header row
HEADER=$(command --csv | head -1)
echo "$HEADER" | grep -q "id,name,email" # Should match

# Check data rows
command --csv | tail -n +2 | while read line; do
  FIELDS=$(echo "$line" | awk -F',' '{print NF}')
  # Verify consistent field count
done
```

### Table Output

Validate table formatting:

```bash
# Check column alignment
command --table | column -t # Should format correctly

# Verify headers present
command --table | head -1 # Should show column names
```

## Data Correctness Validation

### Predictable Output Testing

Use known inputs to verify outputs:

```bash
# Test with known data
echo "input" | command --process

# Expected output known
EXPECTED="processed input"
ACTUAL=$(echo "input" | command --process)

if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "ERROR: Expected '$EXPECTED', got '$ACTUAL'"
fi
```

### Idempotency Testing

Verify repeated executions produce same result:

```bash
# Run command twice
OUTPUT1=$(command --args)
OUTPUT2=$(command --args)

# Should be identical
if [ "$OUTPUT1" != "$OUTPUT2" ]; then
  echo "WARNING: Non-idempotent output"
fi
```

### Determinism Testing

Check for non-deterministic output:

```bash
# Fields that should be deterministic
- IDs (if sequential)
- Names
- Calculated values

# Fields that may vary
- Timestamps
- UUIDs
- Random values
```

## Progress and Verbose Output

### Progress Indicators

Validate progress reporting:

```bash
# Long-running command should show progress
command --verbose | grep -i "progress\|%\|step"

# Progress should:
- Update regularly
- Be accurate
- Not spam output
```

### Verbose Mode

Test verbose flag:

```bash
# Normal mode (quiet)
command

# Verbose mode (detailed)
command --verbose
command -v

# Verify verbose shows additional information
```

## Color Output

### ANSI Color Codes

Check color output handling:

```bash
# Detect color codes
command | cat -v # Shows escape sequences

# No color when piped
command | cat # Should strip colors

# Color flag
command --color=never # No colors
command --color=always # Force colors
command --color=auto # Colors if TTY
```

### Color-Free Output

Verify output works without colors:

```bash
# Strip ANSI codes
command | sed 's/\x1b\[[0-9;]*m//g'

# Should still be readable
```

## Performance

### Response Time

Measure command execution time:

```bash
# Time command execution
time command

# Parse timing
real    0m0.543s
user    0m0.234s
sys     0m0.123s

# Report slow commands (>5s for typical operations)
```

### Memory Usage

Check memory consumption:

```bash
# Monitor memory during execution
/usr/bin/time -v command 2>&1 | grep "Maximum resident set size"

# Report excessive memory usage
```

## Regression Testing

### Compare Against Baseline

When testing changes:

```markdown
1. Run command before changes (baseline)
2. Capture output
3. Run command after changes
4. Compare outputs
5. Report unexpected differences

Focus on:
- Changed functionality (comprehensive)
- Related functionality (thorough)
- Core functionality (smoke test)
```

## Output Validation Checklist

**Format:**
- [ ] JSON parses correctly (if --json)
- [ ] CSV has consistent fields
- [ ] Tables are properly aligned
- [ ] No garbled characters

**Streams:**
- [ ] Normal output goes to stdout
- [ ] Errors go to stderr
- [ ] Warnings go to stderr
- [ ] Streams are separated correctly

**Correctness:**
- [ ] Data values are accurate
- [ ] Calculations are correct
- [ ] Formatting matches spec
- [ ] Idempotent (same input → same output)

**Usability:**
- [ ] Output is readable
- [ ] Colors work correctly (when enabled)
- [ ] Progress indicators update
- [ ] Verbose mode provides details

## Reporting Template

```markdown
## Output Validation Issues

### Invalid JSON - High
- **Command**: `list --json`
- **Issue**: Output is not valid JSON
- **Output**:
  ```
  {users: [malformed json}
  ```
- **Error**: `jq` parse error at line 1
- **Expected**: Valid JSON

### Incorrect Stream Usage - Medium
- **Command**: `process --verbose`
- **Issue**: Errors printed to stdout instead of stderr
- **Impact**: Errors mixed with data output
- **Fix**: Write errors to stderr (>&2)

### Inconsistent Output Format - Medium
- **Command**: `list`
- **Issue**: Sometimes returns JSON, sometimes plain text
- **Expected**: Consistent format (or --json flag to control)
```
