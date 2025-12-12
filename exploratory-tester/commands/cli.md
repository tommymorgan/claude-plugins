---
name: cli
description: Launch autonomous CLI tool exploratory testing for command-line tools and scripts
argument-hint: Command to test or context
allowed-tools: ["Task"]
---

Launch the cli-tester agent to autonomously test command-line tools and scripts.

## How This Command Works

When this command is invoked, use the Task tool to launch the cli-tester agent with the user's context.

## Execution Steps

1. **Parse user input**: The argument may be:
   - Explicit command: `npm run build`
   - Script path: `./scripts/deploy.sh`
   - Binary name: `mycommand`
   - Context description: "my build script" or "the deployment tool"

2. **Launch cli-tester agent**:
   ```
   Use Task tool with:
   - subagent_type: "exploratory-tester:cli-tester"
   - description: "Test CLI tool"
   - prompt: Pass user's context, including:
     - Command or script to test
     - Specific flags/options to focus on (if mentioned)
     - Testing scope (comprehensive vs focused on changes)
     - Any test data location or generation details
     - Any other relevant context
   ```

3. **Let agent work autonomously**: The cli-tester agent will discover options, test the command comprehensively, and report findings

## Usage Examples

```
/exploratory:cli npm run build
/exploratory:cli ./scripts/deploy.sh
/exploratory:cli mycommand
/exploratory:cli test the build script
/exploratory:cli the deployment tool --config flag (focuses testing on --config)
```

## Tips

- Agent discovers command options via --help flags
- Specify focus area if testing specific changes (e.g., "the --config flag")
- Agent scopes testing: comprehensive for changed areas, smoke tests for rest
- Agent uses test data generators if application provides them
- Agent creates temporary test data when needed
- Safe testing: agent avoids destructive operations without confirmation

## Related Skills

The cli-tester agent uses the cli-testing-patterns skill for testing methodology.
