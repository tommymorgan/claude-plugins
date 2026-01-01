# Tommy's Claude Code Marketplace

A curated collection of Claude Code plugins for debugging, development workflow, and productivity.

## Installation

### First Time Setup

Add this marketplace to Claude Code:

```bash
claude plugin marketplace add tommymorgan/claude-plugins
```

### Installing Plugins

```bash
claude plugin install <plugin-name>@tommy-marketplace
```

## Available Plugins

### root-cause-analysis v0.1.0

**Category:** Debugging

Prevents speculation-driven debugging by enforcing the five whys methodology to identify root causes before attempting solutions.

**Problem it solves:** Claude Code tends to jump to speculative solutions without identifying actual root causes, leading to wasted effort, potentially harmful changes, and never-ending fix loops.

**Install:**
```bash
claude plugin install root-cause-analysis@tommy-marketplace
```

**Usage:**

*Automatic (Recommended):*
```
You: "I'm getting an error in my API"
Claude: [Automatically performs root cause analysis before attempting fixes]
```

*Manual:*
```
/root-cause-analysis:debug:root-cause [problem description]
```

**Components:**
- **Skill:** five-whys-methodology - Triggers on problem keywords
- **Agent:** root-cause-analyzer - Autonomous five whys investigation
- **Command:** /root-cause-analysis:debug:root-cause - Manual invocation

**Example workflow:**
```
User: "Login is broken, need to fix it"

Claude: Investigating root cause...

Investigation Level 1
Observation: Login returning 500 errors
Evidence: [reads error logs and code]
Finding: Database connection timeout
Next Question: Why is database timing out?

Investigation Level 2
Observation: Database connection timeout
Evidence: [checks config and metrics]
Finding: Connection pool exhausted (5 connections, 50 concurrent requests)
Next Question: Why is pool exhausted?

Investigation Level 3
Observation: Pool exhausted by concurrent requests
Evidence: [reads session handler code]
Finding: Connections not being released - missing connection.release() call
Root Cause: Missing connection.release() in session handler

Root cause identified. Now proceeding to fix...
```

[More plugins coming soon]

## Publishing Changes

To push plugin updates to GitHub:

```bash
git push claude-plugins main
```

This publishes changes to the public marketplace at https://github.com/tommymorgan/claude-plugins.

## Contributing

This is a personal marketplace. Suggestions welcome via GitHub issues.

## Repository

- **GitHub:** https://github.com/tommymorgan/claude-plugins
- **Issues:** https://github.com/tommymorgan/claude-plugins/issues

## License

See LICENSE file. Individual plugins may have different licenses - check each plugin's README.
