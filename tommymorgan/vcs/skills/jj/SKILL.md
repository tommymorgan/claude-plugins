---
name: jj
description: Use when working with Jujutsu (jj) version control system, creating changes, managing bookmarks, or pushing code. Triggers on jj commands and .jj/ directory presence.
allowed-tools: Bash, Read, Grep, Glob, Edit, Write
metadata:
  filePattern: ".jj/**"
  bashPattern: "\\bjj\\b"
---

# jj (Jujutsu VCS) Guide

When a `.jj/` directory is present, the repository is managed by jj. **Use jj commands for all version control operations. Never use raw git commands.**

## Communication Convention

**Use jj commands but speak in git terminology.** Since the canonical remote is typically a git repository (GitHub/GitLab), use familiar git terms when communicating:

| jj term | Say this instead |
|---------|-----------------|
| change | commit |
| bookmark | branch |
| `@` (working copy) | current commit / working copy |
| `@-` (parent) | parent commit |
| describe | set commit message |

This keeps communication clear for all team members regardless of their jj familiarity.

## Critical Safety Rules

### Never use raw git commands

In a colocated jj+git repository, raw git commands bypass jj's operation log and can corrupt repository state. The following are **forbidden**:

- `git commit` — use `jj describe` + `jj new`
- `git add` — not needed, jj auto-tracks all changes
- `git checkout` — use `jj edit` or `jj new`
- `git branch` — use `jj bookmark`
- `git stash` — not needed, just `jj new`
- `git merge` — use `jj new commit1 commit2` (merge commit)
- `git rebase` — use `jj rebase`

**Exception**: `gh` CLI is acceptable (it uses git internally for PR operations).

### Always create a new commit before editing pushed code

If the current commit (`@`) has a branch that has been pushed to the remote, **do not edit files directly**. This rewrites history and causes force pushes.

Instead:
1. Run `jj new` to create a fresh empty commit on top
2. Then make edits

### Always verify a bookmark exists before pushing

`jj git push` only pushes bookmarks. If the current commit has no bookmark, nothing gets pushed.

Before pushing:
1. Check for a bookmark: `jj log -r @ --no-graph -T 'bookmarks'`
2. If none exists: `jj bookmark set <name> -r @`
3. Then push: `jj git push --bookmark <name>`

## Command Reference

| Git operation | jj command | Notes |
|---|---|---|
| `git status` | `jj status` | Shows working copy changes |
| `git diff` | `jj diff` | Diff of working copy |
| `git show <commit>` | `jj diff -r <rev>` | Shows what a specific commit changed |
| `git diff --staged` | Not needed | No staging area in jj |
| `git log` | `jj log` | Shows change graph |
| `git log --oneline` | `jj log --no-graph` | Compact log output |
| `git add` | Not needed | jj auto-snapshots all changes |
| `git commit -m "..."` | `jj describe -m "..."` then `jj new` | Describe current commit, start a new one |
| `git commit --amend` | `jj describe -m "..."` | Message only — file changes are auto-snapshotted (no explicit amend needed for content) |
| `git branch <name>` | `jj bookmark set <name>` | Create/move bookmark |
| `git branch -d <name>` | `jj bookmark delete <name>` | Delete bookmark |
| `git branch -l` | `jj bookmark list` | List bookmarks |
| `git checkout -b <name>` | `jj new` + `jj bookmark set <name>` | New commit with bookmark |
| `git checkout <branch>` | `jj new <bookmark>` | Creates a new empty commit on top of the branch tip; use `jj edit <bookmark>` to work directly on an existing commit (will rewrite history if pushed) |
| `git push` | `jj git push` | Push bookmarks to remote |
| `git push -u origin <name>` | `jj git push --bookmark <name>` | Push specific bookmark |
| `git fetch` | `jj git fetch` | Fetch from remote |
| `git pull` | `jj git fetch` then `jj rebase -d main@origin` | Fetch + rebase onto upstream |
| `git stash` | `jj new` | Previous commit is preserved automatically |
| `git stash pop` | `jj new <previous-change-id>` | Creates a new commit on top of the previous one (unlike git stash pop, this moves you rather than applying changes in place) |
| `git worktree add <path>` | `jj workspace add <path>` | Create parallel working copy |
| `git worktree remove` | `jj workspace forget <name>` | Remove workspace |
| `git worktree list` | `jj workspace list` | List workspaces |

## Common Workflows

### Making changes (the standard workflow)

```bash
# 1. Check current state
jj status
jj log

# 2. Make edits (jj auto-tracks everything, no git add needed)
# ... edit files ...

# 3. Set the commit message
jj describe -m "feat: add new feature"

# 4. Create a new empty commit for future work
jj new
```

### Starting a new feature branch

```bash
# 1. Make sure we're on the latest main
jj git fetch
jj new main@origin

# 2. Set a bookmark (branch name) for the new commit
jj bookmark set feat/my-feature

# 3. Make edits, describe, push
# ... edit files ...
jj describe -m "feat: implement my feature"
jj git push --bookmark feat/my-feature
```

### Adding commits to an existing PR

```bash
# 1. Create a new commit on top (do NOT edit the pushed commit)
jj new

# 2. Make edits
# ... edit files ...

# 3. Describe and push
jj describe -m "fix: address PR feedback"
jj bookmark set feat/my-feature  # moves bookmark to new commit
jj git push --bookmark feat/my-feature
```

### Syncing with upstream

```bash
# Fetch latest changes
jj git fetch

# Rebase current work onto updated main
jj rebase -d main@origin
```

### Parallel work with workspaces

```bash
# Create a new workspace for parallel work
jj workspace add ../workspace-name

# Work independently in that directory
cd ../workspace-name
jj new main@origin
jj bookmark set feat/other-feature
# ... edit files ...

# Changes are visible across workspaces via jj log

# Clean up when done
cd ../original-dir
jj workspace forget workspace-name
```

### Viewing what changed

```bash
# What changed in the working copy
jj diff

# What changed in the parent commit
jj diff -r @-

# Show a specific commit
jj show <change-id>

# Compare two commits
jj diff --from <id1> --to <id2>
```

## Key Differences from Git

1. **No staging area** — all file changes are automatically tracked. There is no `git add`.
2. **Commits are mutable** — `jj describe` changes the message, edits to files are auto-snapshotted.
3. **Working copy is always a commit** — `@` always refers to a real commit, not uncommitted changes.
4. **Bookmarks are just pointers** — they're like git branches but more lightweight. They must be explicitly set.
5. **Operations are logged** — every jj operation is recorded. Use `jj op log` to see history and `jj op restore` to undo.
6. **Git hooks are bypassed** — jj commands do not trigger git-style hooks (pre-commit, pre-push, etc.), even in colocated repos. Quality checks should be handled by Claude Code hooks or CI instead.

## When jj Is Not Available

If the `.jj/` directory exists but `jj` is not found in PATH, **do not fall back to git commands**. This would corrupt jj's internal state. Instead, tell the developer:

> "This repository is managed by jj, but jj is not found in PATH. Please install jj or add it to your PATH before performing version control operations."
