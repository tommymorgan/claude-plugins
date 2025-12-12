# Exit Code Standards

Standard exit codes and their meanings for CLI tools.

## Standard Exit Codes

### Success and Failure

**0 - Success**
- Command completed successfully
- No errors encountered
- Expected outcome achieved

**1 - General Error**
- Command failed
- Catchall for errors
- Most common error exit code

### Usage Errors

**2 - Misuse of Shell Command**
- Invalid arguments
- Unknown options
- Missing required parameters
- Incorrect syntax

Example:
```bash
mycommand --invalid-flag
# Exit 2: Unknown option '--invalid-flag'
```

### Execution Errors

**126 - Command Cannot Execute**
- File exists but not executable
- Permission denied
- Script lacks execute bit

```bash
./script.sh
# Exit 126: Permission denied (need chmod +x)
```

**127 - Command Not Found**
- Command doesn't exist
- Not in PATH
- Typo in command name

```bash
nonexistent-command
# Exit 127: command not found
```

### Signal-Related Exits

**128 + N - Fatal Error Signal N**

Common signals:
- **130** (128+2): SIGINT (Ctrl+C)
- **137** (128+9): SIGKILL (killed)
- **139** (128+11): SIGSEGV (segmentation fault)
- **143** (128+15): SIGTERM (terminated)

## Custom Exit Codes

### Application-Specific Codes

Many tools define custom exit codes:

```bash
# Git exit codes
0 - Success
1 - Generic error
128 - Fatal error

# Grep exit codes
0 - Match found
1 - No match
2 - Error occurred

# Diff exit codes
0 - No differences
1 - Differences found
2 - Error occurred
```

### Testing Custom Codes

When testing commands:
1. Check documentation for exit code meanings
2. Verify codes are used consistently
3. Test that errors return non-zero
4. Validate specific codes match documented behavior

## Exit Code Testing

### Test Success Cases

```bash
# Run command that should succeed
command --valid-input; EXIT_CODE=$?

# Verify exit code is 0
if [ $EXIT_CODE -ne 0 ]; then
  echo "ERROR: Expected exit 0, got $EXIT_CODE"
fi
```

### Test Error Cases

```bash
# Run command that should fail
command --invalid-input; EXIT_CODE=$?

# Verify exit code is non-zero
if [ $EXIT_CODE -eq 0 ]; then
  echo "ERROR: Command should have failed but exited 0"
fi
```

### Test Specific Exit Codes

```bash
# Test for specific exit code
command; EXIT_CODE=$?

case $EXIT_CODE in
  0)
    echo "Success"
    ;;
  1)
    echo "General error"
    ;;
  2)
    echo "Usage error"
    ;;
  *)
    echo "Unexpected exit code: $EXIT_CODE"
    ;;
esac
```

## Best Practices

### Exit Code Conventions

**DO:**
- Exit 0 only on complete success
- Use non-zero for any error condition
- Use 2 for usage/argument errors
- Document custom exit codes
- Be consistent across commands

**DON'T:**
- Exit 0 on errors
- Use random exit codes
- Change exit code meanings between versions
- Exit with codes >255 (wrapped modulo 256)

### Error Communication

Combine exit codes with helpful messages:

```bash
#!/bin/bash

if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: Config file not found: $CONFIG_FILE" >&2
  echo "Run 'mycommand init' to create config" >&2
  exit 1
fi
```

**Good practices:**
- Write errors to stderr (>&2)
- Include actionable guidance
- Reference help or documentation
- Exit with appropriate code

## Testing Report Template

```markdown
### Exit Code Issues

**Incorrect Exit Code - High**
- **Command**: `build --invalid-flag`
- **Expected Exit Code**: 2 (usage error)
- **Actual Exit Code**: 0 (success)
- **Issue**: Command silently ignores invalid flags
- **Impact**: Scripts can't detect errors

**Success on Failure - Critical**
- **Command**: `deploy production` (with invalid credentials)
- **Expected Exit Code**: 1 (deployment failed)
- **Actual Exit Code**: 0 (success)
- **Issue**: Deployment fails but exits successfully
- **Impact**: CI/CD pipelines think deployment succeeded
```

## Exit Code Reference

| Code | Meaning | Usage |
|------|---------|-------|
| 0 | Success | Command completed successfully |
| 1 | Error | General error |
| 2 | Usage error | Invalid arguments or options |
| 64 | Usage error | Bad command-line parameters (BSD) |
| 65 | Data error | Input data incorrect |
| 66 | No input | Cannot open input file |
| 69 | Service unavailable | Required service is unavailable |
| 70 | Internal error | Internal software error |
| 73 | Can't create | Cannot create output file |
| 74 | I/O error | I/O error |
| 75 | Temp failure | Temporary failure (try again) |
| 77 | Permission denied | Permission problem |
| 78 | Configuration error | Configuration error |
| 126 | Not executable | Command found but not executable |
| 127 | Not found | Command not found |
| 128+N | Signal | Killed by signal N |
| 130 | SIGINT | Interrupted (Ctrl+C) |
| 137 | SIGKILL | Killed forcefully |
| 139 | SIGSEGV | Segmentation fault |
| 143 | SIGTERM | Terminated |
| 255 | Out of range | Exit code out of range |

## Additional Resources

For detailed CLI testing techniques, consult:
- **`references/output-validation.md`** - Output format validation patterns
- **`references/test-data-generation.md`** - CLI test data generation strategies
