---
description: Perform systematic root cause analysis using five whys methodology
argument-hint: [problem-description]
allowed-tools: Task
---

Perform systematic root cause analysis on the reported problem using the root-cause-analyzer agent.

**Problem Context:** $ARGUMENTS

**Instructions:**

1. Launch the root-cause-analyzer agent to investigate this problem
2. The agent will autonomously perform five whys analysis without user prompts
3. Each investigation level will be shown progressively as the agent works
4. The agent will continue until identifying an actionable root cause
5. After root cause is identified, proceed to implementing the fix

**Agent Behavior:**
- Gathers evidence from code, logs, and outputs
- Asks "why?" iteratively based on concrete findings
- Shows structured output for each investigation level
- Determines when root cause criteria are met (actionable, explanatory, terminal)
- Completes automatically when root cause is found

**Your Role:**
- Use the Task tool to launch the root-cause-analyzer agent
- Provide the problem context to the agent
- Wait for agent to complete root cause analysis
- Once agent identifies root cause, proceed with the recommended fix approach

Do not attempt speculative fixes before root cause is identified.
