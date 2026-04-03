# Flow Metrics Plugin

**Version**: 0.1.0

Data-source agnostic flow metrics, probabilistic forecasting, and process stability analysis based on Daniel Vacanti's framework.

## Installation

```bash
claude plugin install flow@tommymorgan
```

## Commands

| Command | Description |
|---------|-------------|
| `/flow:setup` | Interactive setup to configure flow metrics for the current project |
| `/flow:fetch-data` | Fetch work item data from the configured source |
| `/flow:sle` | Display Service Level Expectations (Cycle Time percentiles) |
| `/flow:health` | Show current WIP, aging items, and throughput trends |
| `/flow:forecast` | Probabilistic delivery forecast (single or multiple items) |

## Skills

- **metrics-guidance** — Applies Vacanti's flow metrics principles when discussing predictability and forecasting
- **stability-guidance** — Guides appropriate responses to process variation using XmR chart interpretation

## Agent

- **analyst** — Autonomous flow metrics analyst that investigates process health and interprets data

## Supported Data Sources

- **GitHub PRs** (Phase 1 — available now)
- **Linear issues** (Phase 2 — planned)
- **Git history** (Phase 2 — planned)

## Quick Start

1. Navigate to a project with a git remote
2. Run `/flow:setup` to configure your data source and process boundaries
3. Run `/flow:fetch-data` to collect historical data
4. Run `/flow:sle` to see your Service Level Expectations

## Configuration

Per-project configuration is stored in `~/.tommymorgan/flows/`, keyed by git remote URL. Run `/flow:setup` to create or update configuration.

## License

MIT
