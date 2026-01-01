# Tommy's Claude Code Marketplace

Personal collection of Claude Code plugins for disciplined development workflows.

## Installation

### First Time Setup

Add this marketplace to Claude Code:

```bash
claude plugin marketplace add tommymorgan/claude-plugins
```

### Installing Plugins

```bash
claude plugin install <plugin-name>@tommymorgan
```

## Available Plugins

### [tommymorgan](./tommymorgan/README.md) v1.2.0

**Development Workflow** - Comprehensive workflow plugin enforcing disciplined planning, autonomous TDD execution, expert code review, complete task completion, and automatic image preprocessing.

**Key Features:**
- Gherkin-based planning with TODO/DONE tracking
- Autonomous TDD execution with quality gates
- Expert plan review (7 domain experts with context-aware filtering)
- Work completion enforcement (stop hook blocks partial completion)
- Automatic image resizing (2000px limit, configurable)
- Root cause analysis (five whys methodology)
- Plan-aware testing (API, browser, CLI)

**Install:**
```bash
claude plugin install tommymorgan@tommymorgan
```

**[Full Documentation →](./tommymorgan/README.md)**

---

## Plugin Development

Plugin development happens in `homelab/tools/claude-plugins/`.

### Publishing Changes

**1. Sync files to publish repository:**
```bash
rsync -av --delete ~/src/homelab/tools/claude-plugins/ ~/src/claude-plugins-publish/ --exclude=.git --exclude=plans
```

**2. Commit and push:**
```bash
cd ~/src/claude-plugins-publish
git add -A
git commit -m "feat: <description of changes>"
git push origin main
```

**Why separate repos?**

The homelab repository contains secrets in its git history. Git subtree push includes parent commits, which would expose those secrets to GitHub's secret scanning. Using a separate publish repository ensures clean history without secrets.

**Locations:**
- **Development**: `~/src/homelab/tools/claude-plugins/`
- **Publish**: `~/src/claude-plugins-publish/`
- **Public**: https://github.com/tommymorgan/claude-plugins

## Contributing

This is a personal marketplace. Suggestions welcome via GitHub issues.

## Repository

- **GitHub**: https://github.com/tommymorgan/claude-plugins
- **Issues**: https://github.com/tommymorgan/claude-plugins/issues

## License

See individual plugin READMEs for license information. Most plugins are MIT licensed.
