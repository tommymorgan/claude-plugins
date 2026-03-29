---
name: tommymorgan:jj-setup
description: Audit and configure jj safety checks for the current repository
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - Edit
---

# Set Up jj Safety Checks

Audit the current repository for jj usage and set up safeguards to prevent accidental git commands.

## Workflow

### Step 1: Verify jj Environment

Check that jj is available and the repository is jj-managed:

```bash
# Check jj is in PATH
which jj || echo "NOT_FOUND"

# Check .jj directory exists
ls -d .jj 2>/dev/null || echo "NOT_JJ_REPO"
```

**If jj is not found**: Tell the user to install jj and stop.
**If .jj/ doesn't exist**: Tell the user this isn't a jj repo and stop.

### Step 2: Check for Colocated Git

```bash
# Check if this is a colocated jj+git repo
ls -d .git 2>/dev/null && echo "COLOCATED" || echo "PURE_JJ"
```

If colocated, the risk of accidental git commands is highest. All subsequent checks are especially important.

### Step 3: Audit CLAUDE.md

Check if the project's CLAUDE.md mentions jj:

```bash
grep -i "jj\|jujutsu" CLAUDE.md 2>/dev/null
```

**If no mention found**, add a section to CLAUDE.md:

```markdown
## Version Control

This repository uses [Jujutsu (jj)](https://martinvonz.github.io/jj/) for version control. **Always use jj commands, never raw git commands.** See the `jj` skill for the full command reference.

Key rules:
- `jj status` not `git status`
- `jj describe -m "..."` + `jj new` not `git commit`
- `jj bookmark set <name>` not `git branch`
- `jj git push` not `git push`
- `jj git fetch` not `git fetch`
```

**If already mentioned**, report what's there and skip.

### Step 4: Audit Claude Code Settings for Git-Blocking Hook

Check if there's a PreToolUse hook that blocks git commands in Bash:

```bash
# Check project-level settings
cat .claude/settings.json 2>/dev/null | grep -A5 "PreToolUse"

# Check user-level settings
cat ~/.claude/settings.json 2>/dev/null | grep -A5 "PreToolUse"
```

**If no git-blocking hook exists**, recommend adding one. Show the user what to add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"import sys,json; d=json.loads(sys.stdin.read()); cmd=d.get('tool_input',{}).get('command',''); git_cmds=['git commit','git add','git checkout','git branch','git stash','git merge','git rebase','git push','git pull','git reset','git cherry-pick']; matches=[c for c in git_cmds if c in cmd]; sys.exit(0) if not matches else (print(json.dumps({'decision':'block','reason':f'Use jj instead of {matches[0]}. This repo is managed by jj — raw git commands can corrupt state.'})), sys.exit(0))\"",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

Note: Do NOT write this automatically. The user must review and install it themselves since it affects all Claude Code sessions in this project.

### Step 5: Check Memory System

If the project has a Claude Code memory directory, check for jj-related feedback:

```bash
# Check for existing jj memory
find .claude/projects/ -name "*.md" -exec grep -l "jj\|jujutsu\|git" {} \; 2>/dev/null
cat .claude/projects/*/memory/MEMORY.md 2>/dev/null | grep -i "jj\|git"
```

**If no jj feedback memory exists**, note that the `jj` skill will be injected automatically when jj commands are used, so explicit memory isn't strictly required.

### Step 6: Report

Output a summary:

```
## jj Setup Audit

| Check | Status |
|-------|--------|
| jj installed | ✓/✗ |
| .jj/ directory | ✓/✗ |
| Colocated with git | Yes/No |
| CLAUDE.md mentions jj | ✓/✗ (added/already present) |
| Git-blocking hook | ✓/✗ (recommendation shown) |
| Memory/feedback | ✓/✗ |

### Actions Taken
- [list what was added/changed]

### Manual Steps Required
- [list what the user needs to do themselves]
```
