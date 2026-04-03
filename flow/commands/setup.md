---
description: "Interactive setup to configure flow metrics for the current project"
---

# Flow Setup

Configure flow metrics collection for the current project.

## Steps

1. **Detect git remote URL**:
   ```bash
   git remote get-url origin
   ```
   If no git remote found, report: "No git remote detected. Flow metrics requires a git repository with a remote." and stop.

2. **Generate project slug** from the remote URL:
   - Strip protocol (https://, git@)
   - Replace `/` and `:` with `-`
   - Strip `.git` suffix
   - Lowercase

3. **Check for existing config** at `~/.tommymorgan/flows/<slug>.json`:
   - If exists, show current config and ask: "Reconfigure this project?"

4. **Ask: "What is your data source?"**
   Present options:
   - GitHub PRs (recommended for teams using pull request workflows)
   - Linear issues (for teams tracking work in Linear)
   - Git history (for any repo — no external tools required)

   Note: Linear and git adapters are not yet implemented. If selected, inform the user and suggest GitHub PRs for now.

5. **Ask: "What does 'started' mean for this project?"**
   Present source-appropriate options:
   - **GitHub**: Earliest commit authored date on PR branch (recommended), PR opened, PR created
   - **Linear**: Issue moved to In Progress, issue created, custom state name
   - **Git**: First commit on branch, branch created

6. **Ask: "What does 'finished' mean for this project?"**
   Present source-appropriate options:
   - **GitHub**: PR merged (recommended), PR closed
   - **Linear**: Issue moved to Done, issue closed, custom state name
   - **Git**: Merged to main/master, tagged

7. **Ask source-specific connection details**:
   - **GitHub**: owner/repo (can list multiple, comma-separated). Default: infer from git remote.
   - **Linear**: team slug or project name
   - **Git**: main branch name (default: main)

8. **Show summary**:
   ```
   Flow Configuration Summary:
   - Project: <remote URL>
   - Source: <source>
   - Started: <boundary definition>
   - Finished: <boundary definition>
   - Connection: <details>

   Save this configuration?
   ```

9. **Save config** to `~/.tommymorgan/flows/<slug>.json` atomically

10. **Report**:
    ```
    Configuration saved. Run /flow:fetch-data to collect your first batch of flow data.
    ```
