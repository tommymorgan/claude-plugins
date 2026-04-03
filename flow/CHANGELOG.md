# Changelog

### v0.1.0

Initial release with GitHub adapter support.

- Interactive `/flow:setup` for per-project configuration
- `/flow:fetch-data` collects merged PR data from GitHub API
- `/flow:sle` displays Cycle Time percentiles (50th/70th/85th/95th)
- `/flow:health` shows live WIP, aging items, and throughput trends
- `/flow:forecast` provides probabilistic forecasts (percentile-based SLE for single items, Monte Carlo simulation for multiple items)
- `metrics-guidance` skill applies Vacanti's flow principles
- `stability-guidance` skill guides XmR chart interpretation
- `analyst` agent for autonomous flow investigation
- Full analysis engine: cycle time, percentiles, throughput, work item age, Monte Carlo, XmR charts with 4-rule signal detection
