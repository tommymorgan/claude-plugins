---
name: metrics-guidance
description: Provides Vacanti's flow metrics principles when discussing predictability, forecasting, cycle time, throughput, or delivery estimates. Triggers on keywords like "estimate", "when will", "how long", "velocity", "average cycle time", "story points", "deadline", "SLE", "percentile", "forecast"
---

# Flow Metrics Guidance

Apply these principles from Daniel Vacanti's framework whenever discussing flow metrics, forecasting, or predictability.

## Core Principles

### Never use averages for forecasting
- The Flaw of Averages: "plans based on average fail on average"
- Cycle Time data is NOT normally distributed — it is skewed right
- An average hides the variability that matters most for prediction
- Instead: use percentiles (50th, 70th, 85th, 95th)

### Percentiles ARE forecasts
- "85th percentile = 12 days" means "there is an 85% chance this item will finish in 12 days or less"
- No estimation required — the historical data speaks for itself
- Percentiles are robust against outliers (unlike averages)

### Every forecast must include three elements
1. **A range** of possible outcomes (not a single number)
2. **A probability** for that range
3. **A time-to-live** — when should this forecast be regenerated?

### Work Item Age is the most important metric
- Age = how long an in-progress item has been in the system
- The real reason to control WIP is to prevent unnecessary aging
- Items aging beyond the 85th percentile SLE warrant immediate investigation
- Two best ways to prevent aging: finish items, and don't start items you're not ready for

### Size does not matter for forecasting
- There is almost no correlation between Story Point estimates and actual Cycle Time
- You do NOT need same-sized items for flow metrics to work
- Estimation usually makes processes LESS predictable, not more
- Stop estimating. Start measuring.

## When someone asks "when will it be done?"

### For a single item:
- Use Cycle Time percentiles from historical data
- Present as: "Based on our data, there's an 85% chance this will finish within {n} days"
- Improve the forecast by: reducing WIP, managing Work Item Age, improving flow efficiency

### For multiple items:
- Use Monte Carlo simulation on historical Throughput data
- Present as: "There's an 85% chance all {n} items will be complete by {date}"
- NEVER divide remaining items by average throughput — that's the Flaw of Averages

## Anti-patterns to correct

| If you hear... | Respond with... |
|---|---|
| "It will be done by {date}" | "What's the probability? What range of dates is possible?" |
| "Our average cycle time is X days" | "What are the percentiles? The 85th is more useful for setting expectations." |
| "We need to estimate this in story points" | "Story points don't correlate with actual delivery time. Use historical Cycle Time data instead." |
| "Velocity says we can do X points per sprint" | "Throughput (items completed per week) is more reliable than velocity for forecasting." |
| "This sprint we did fewer points so we're slower" | "Is the change within normal variation? Check the XmR chart before reacting." |

## Reforecast when new information arrives
- Every forecast has a shelf life
- As work progresses, new information validates or invalidates assumptions
- Reforecasting is not a sign of failure — it's responsible practice
- The NHC updates hurricane forecasts every 8 hours. You should update delivery forecasts regularly too.
