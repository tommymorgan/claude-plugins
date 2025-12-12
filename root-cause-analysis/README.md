# Root Cause Analysis Plugin

Enforces the five whys methodology to identify root causes before attempting solutions, preventing speculation-driven debugging that wastes effort and creates harmful changes.

## Problem

Claude Code tends to jump to speculative solutions without identifying actual root causes, leading to:
- Never-ending loops of useless fixes
- Potentially harmful changes
- Wasted time and effort
- Frustration from treating symptoms instead of causes

## Solution

This plugin automatically applies the "five whys" technique when problems are detected:
1. Detects problem-solving scenarios (keywords or errors)
2. Autonomously iterates through "why?" questions
3. Shows progressive analysis as it works
4. Identifies actionable root cause
5. Only then proceeds to solution

## Features

- **Automatic activation**: Triggers on problem keywords or tool errors
- **Autonomous execution**: Runs without user prompts between steps
- **Progressive output**: Shows each "why" iteration as investigation proceeds
- **Smart completion**: Determines when true root cause is reached
- **User control**: Can be interrupted/bypassed if needed
- **Manual invocation**: `/debug:root-cause` command for explicit analysis

## Installation

```bash
# Install from marketplace
cc plugin install root-cause-analysis@tommy-marketplace

# Or install locally
cc --plugin-dir /path/to/root-cause-analysis
```

## Usage

### Automatic (Recommended)

The plugin activates automatically when you're solving problems:

```
You: "The login is broken, let me fix the auth endpoint"
Claude: [Triggers root-cause-analyzer agent automatically]
        Investigating root cause before proceeding to solution...

        Investigation Level 1
        Observation: Login functionality failing
        Evidence: [checks error logs, code]
        Next question: Why is the login failing?

        Investigation Level 2
        ...
```

### Manual Invocation

Explicitly request root cause analysis:

```
/debug:root-cause "API returning 500 errors"
```

## Components

- **Skill**: `five-whys-methodology` - Describes when and how to apply the five whys approach
- **Agent**: `root-cause-analyzer` - Autonomously performs root cause analysis
- **Command**: `/debug:root-cause` - Manual trigger for analysis

## Examples

**Before this plugin** (speculation-driven):
```
User: Login is broken
Claude: Let me fix the authentication middleware [starts making changes]
[10 iterations later, still broken]
```

**With this plugin** (root-cause-driven):
```
User: Login is broken
Claude: Investigating root cause...
        Why #1: Login returning 401 → Database connection timing out
        Why #2: Database timing out → Connection pool exhausted
        Why #3: Pool exhausted → Connection leak in session handler
        Why #4: Leak in handler → Missing connection.release() call

        Root cause identified: Missing connection.release() in session handler
        This is actionable - we can add the missing release call.

        Now proceeding to fix...
```

## Configuration

No configuration required - works out of the box.

## License

MIT
