---
name: stability-guidance
description: Guides appropriate responses to process variation using Vacanti's framework. Triggers when discussing process improvement, responding to metric changes, XmR chart signals, sprint retrospectives, or when someone asks "why did our velocity/throughput change?"
---

# Process Stability Guidance

Apply these principles when responding to variation in flow metrics.

## The Two Types of Variation

### Routine Variation (Noise)
- Variation inherent to the normal operation of your process
- Always present, unavoidable, expected
- Like rolling a die — getting different numbers each roll is normal
- **Response**: Change the SYSTEM, not individual behaviors. Routine variation requires structural improvements.

### Exceptional Variation (Signal)
- Variation that is NOT part of normal process operation
- Indicates something specific and assignable happened
- Like rolling a 13 on a six-sided die — something outside the system occurred
- **Response**: Investigate the SPECIFIC CAUSE. Find what happened and address it directly.

## How to Tell the Difference: XmR Charts

XmR charts (Process Behaviour Charts) separate signal from noise using control limits calculated from your own data.

### Reading XmR Charts
- **Central line**: Average of the metric values
- **Upper/Lower Natural Process Limits**: Average ± 2.66 × average moving range
- Points WITHIN the limits = routine variation (noise)
- Points OUTSIDE the limits = exceptional variation (signal)

### Signal Detection Rules
1. **Point outside limits**: Any single point above upper or below lower limit
2. **Run of 8**: Eight or more consecutive points on the same side of the central line
3. **Outer third rule**: 3 of 4 consecutive points in the outer third between the central line and a limit

## Critical Mistakes to Avoid

### Do NOT react to individual data points
- "Our throughput dropped from 6 to 4 this week" — is that signal or noise?
- You CANNOT tell from two data points alone
- Check the XmR chart. If both values are within limits, this is routine variation.
- Reacting to noise makes your process WORSE, not better.

### Do NOT compare to averages
- "We're below average this sprint" means nothing
- By definition, roughly half your data points will be below average
- Being below average is EXPECTED, not a problem

### Do NOT confuse predictable with good
- A predictable process may still be slow
- Predictability means the variation is routine (stable, consistent)
- Improvement means reducing the central line or tightening the limits
- But you can only improve AFTER you've achieved stability

## Responding to Variation

| What you see | What it means | What to do |
|---|---|---|
| All points within limits | Process is predictable | Improve by changing the system (reduce WIP, improve policies) |
| Point above upper limit (e.g., high cycle time) | Something exceptional happened | Investigate: what caused this specific item to take so long? |
| Point below lower limit (e.g., unusually fast) | Something exceptional happened (good!) | Investigate: what went right? Can you replicate it? |
| Run of 8 above central line | Sustained shift upward | Process has changed — investigate what shifted |
| Run of 8 below central line | Sustained shift downward | Process has improved — identify what helped |
| 3 of 4 in outer third | Early warning of potential shift | Monitor closely — may indicate emerging change |

## Voice of the Process (VoP) vs Voice of the Customer (VoC)

- **VoP**: What your process IS doing (shown by XmR limits)
- **VoC**: What your customer NEEDS (your SLE targets)
- If VoP meets VoC → process is capable
- If VoP doesn't meet VoC → improve the process (don't just set targets)
- Setting arbitrary targets without understanding VoP creates dysfunction
