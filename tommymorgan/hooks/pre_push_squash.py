#!/usr/bin/env python3
"""
Pre-Push Squash Verification Hook

PreToolUse:Bash hook that intercepts git push commands and enforces
commit squashing for /tommymorgan:work workflow.
"""

import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


# Configuration
FETCH_TIMEOUT = 60  # seconds (increased for slow networks/large repos)
DIFF_TIMEOUT = 10   # seconds
LOG_FILE = Path.home() / ".claude" / "hooks" / "pre-push-squash.log"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_MAX_BACKUPS = 5
DEBUG = os.environ.get('CLAUDE_DEBUG') == 'true'

# Safe push command patterns - prevent command injection
SAFE_PUSH_PATTERNS = [
    r'^git\s+push(\s+[\w\-/]+)*$',
    r'^jj\s+git\s+push(\s+[\w\-/]+)*$'
]

# Global state for signal handling
interrupted = False
backup_tag_global = None


def signal_handler(signum, frame):
    """Handle SIGINT and SIGTERM"""
    global interrupted, backup_tag_global
    interrupted = True
    if backup_tag_global:
        deny_command(f"Interrupted - backup tag preserved: {backup_tag_global}")
    else:
        deny_command("Interrupted")


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def debug_log(message: str):
    """Log debug message if CLAUDE_DEBUG is enabled"""
    if DEBUG:
        print(f"[DEBUG] {message}", file=sys.stderr)


def log_execution(result: str, wip_count: int = 0, duration_ms: int = 0, plan_file: Optional[str] = None):
    """Log execution to file"""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Rotate if needed
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > LOG_MAX_SIZE:
            rotate_logs()

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "wip_count": wip_count,
            "duration_ms": duration_ms,
            "plan_file": plan_file
        }

        with open(LOG_FILE, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        debug_log(f"Failed to write log: {e}")


def rotate_logs():
    """Rotate log files"""
    try:
        for i in range(LOG_MAX_BACKUPS - 1, 0, -1):
            old = LOG_FILE.with_suffix(f'.log.{i}')
            new = LOG_FILE.with_suffix(f'.log.{i + 1}')
            if old.exists():
                old.rename(new)

        if LOG_FILE.exists():
            LOG_FILE.rename(LOG_FILE.with_suffix('.log.1'))
    except Exception as e:
        debug_log(f"Failed to rotate logs: {e}")


def is_push_command(command: str) -> bool:
    """Check if command is a safe push command"""
    for pattern in SAFE_PUSH_PATTERNS:
        if re.match(pattern, command):
            debug_log(f"Matched push pattern: {pattern}")
            return True
    debug_log(f"No push pattern matched for: {command}")
    return False


def has_wip_commits(commits: List[str]) -> bool:
    """Check if any commits have WIP: prefix"""
    for commit in commits:
        if ' ' in commit:
            message = commit.split(' ', 1)[1]
            if message.startswith('WIP: ') or message.startswith('WIP:'):
                return True
    return False


def run_git(args: List[str], check=True, capture_output=True, timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    """Run git command with optional timeout"""
    debug_log(f"Running git {' '.join(args)}")
    try:
        result = subprocess.run(
            ['git'] + args,
            check=check,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        debug_log(f"Git command succeeded")
        return result
    except subprocess.TimeoutExpired:
        debug_log(f"Git command timed out after {timeout}s")
        raise
    except subprocess.CalledProcessError as e:
        debug_log(f"Git command failed with exit code {e.returncode}")
        raise


def get_current_branch() -> str:
    """Get current git branch name"""
    result = run_git(['branch', '--show-current'])
    return result.stdout.strip()


def get_commits_to_push() -> List[str]:
    """Get list of commits that would be pushed"""
    try:
        debug_log("Fetching origin...")
        run_git(['fetch', 'origin'], check=True, capture_output=True, timeout=FETCH_TIMEOUT)
        debug_log("Fetch complete")

        result = run_git(['rev-list', 'origin/main..HEAD', '--oneline'], timeout=DIFF_TIMEOUT)
        commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
        debug_log(f"Found {len(commits)} commits to push")
        return commits
    except subprocess.TimeoutExpired as e:
        deny_command(f"Fetch timeout - check network connection (waited {e.timeout}s)")
    except subprocess.CalledProcessError:
        return []


def has_unstaged_changes() -> bool:
    """Check if there are unstaged changes"""
    try:
        run_git(['diff', '--quiet'], timeout=DIFF_TIMEOUT)
        run_git(['diff', '--cached', '--quiet'], timeout=DIFF_TIMEOUT)
        return False
    except subprocess.TimeoutExpired:
        debug_log("Diff check timed out, assuming no unstaged changes")
        return False
    except subprocess.CalledProcessError:
        return True


def has_merge_conflicts() -> bool:
    """Check if there are merge conflicts with origin/main"""
    try:
        debug_log("Checking for merge conflicts...")
        result = run_git(['merge-tree', 'origin/main', 'HEAD'], check=False, timeout=DIFF_TIMEOUT)
        has_conflict = '<<<<<' in result.stdout or 'conflict' in result.stdout.lower()
        debug_log(f"Merge conflicts: {has_conflict}")
        return has_conflict
    except subprocess.TimeoutExpired:
        debug_log("Merge conflict check timed out, assuming conflicts exist")
        return True
    except subprocess.CalledProcessError:
        return True


def auto_commit_unstaged() -> None:
    """Automatically stage and commit unstaged changes"""
    debug_log("Auto-committing unstaged changes...")
    run_git(['add', '-A'])
    run_git(['commit', '-m', 'WIP: auto-commit unstaged changes'])
    print("Auto-staged and committed unstaged changes", file=sys.stderr)


def find_plan_file() -> Optional[str]:
    """Find the plan file modified in current commits"""
    try:
        result = run_git(['diff', '--name-only', 'origin/main..HEAD'], timeout=DIFF_TIMEOUT)
        files = result.stdout.strip().split('\n')
        plan_files = [f for f in files if 'plans/' in f and f.endswith('.md')]
        if plan_files:
            debug_log(f"Found plan file: {plan_files[0]}")
        return plan_files[0] if plan_files else None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None


def parse_completed_scenarios(content: str) -> List[str]:
    """Extract DONE scenarios from plan file"""
    scenarios = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '<!-- DONE -->' in line:
            # Get the next line which should be the scenario title
            if i + 1 < len(lines):
                scenario_line = lines[i + 1].strip()
                if scenario_line.startswith('Scenario:'):
                    scenarios.append(scenario_line.replace('Scenario:', '').strip())
    return scenarios


def analyze_diff() -> str:
    """Analyze git diff for key changes"""
    try:
        # Get diff stat
        stat_result = run_git(['diff', '--stat', 'origin/main', 'HEAD'], timeout=DIFF_TIMEOUT)

        # Get detailed diff to identify major changes
        diff_result = run_git(['diff', 'origin/main', 'HEAD'], timeout=DIFF_TIMEOUT)

        # Parse diff stat to find files with most changes
        stat_lines = stat_result.stdout.strip().split('\n')
        files_changed = []
        for line in stat_lines:
            if '|' in line:
                filename = line.split('|')[0].strip()
                files_changed.append(filename)

        if not files_changed:
            return "No file changes"

        # Summarize
        summary = f"{len(files_changed)} files changed"
        if len(files_changed) <= 3:
            summary += f": {', '.join(files_changed)}"

        return summary
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return "Unable to analyze diff"


def generate_commit_message(plan_file: Optional[str], wip_count: int) -> str:
    """Generate commit message from plan file or WIP commits"""
    if plan_file and Path(plan_file).exists():
        with open(plan_file) as f:
            content = f.read()

            # Extract goal
            goal_match = re.search(r'\*\*Goal\*\*:\s*(.+)', content)
            if not goal_match:
                goal = "Complete /tommymorgan:work session"
            else:
                goal = goal_match.group(1).strip()

            # Extract completed scenarios
            completed = parse_completed_scenarios(content)

            # Analyze diff for key changes
            diff_summary = analyze_diff()

            # Build commit message
            parts = [goal, ""]

            if completed:
                parts.append("Completed scenarios:")
                for scenario in completed:
                    parts.append(f"- {scenario}")
                parts.append("")

            # Add key changes
            parts.append(f"Key changes: {diff_summary}")
            parts.append("")

            # Add squash info
            parts.append(f"Squashed {wip_count} WIP commits")
            parts.append("")

            # Add attribution
            parts.append("🤖 Generated with [Claude Code](https://claude.com/claude-code)")
            parts.append("")
            parts.append("Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>")

            return '\n'.join(parts)

    # Fallback: combine WIP commit messages
    result = run_git(['log', '--format=%s', 'origin/main..HEAD'])
    messages = result.stdout.strip().split('\n')
    combined = '\n'.join([m.replace('WIP: ', '') for m in messages if m])
    return f"feat: {combined}\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nCo-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"


def create_backup_tag() -> str:
    """Create backup tag before squashing"""
    global backup_tag_global
    sha = run_git(['rev-parse', '--short', 'HEAD']).stdout.strip()
    timestamp = int(time.time())
    tag_name = f"backup/pre-squash-{sha}-{timestamp}"
    run_git(['tag', tag_name])
    debug_log(f"Created backup tag: {tag_name}")
    backup_tag_global = tag_name
    return tag_name


def squash_commits(commit_message: str) -> None:
    """Squash all commits into one"""
    debug_log("Squashing commits...")
    run_git(['reset', '--soft', 'origin/main'])
    run_git(['commit', '-m', commit_message])
    debug_log("Squash complete")


def validate_squash(backup_tag: str) -> bool:
    """Validate squash result"""
    try:
        # Verify exactly 1 commit exists
        result = run_git(['rev-list', '--count', 'origin/main..HEAD'])
        count = int(result.stdout.strip())

        # Verify backup tag exists
        tag_result = run_git(['tag', '-l', backup_tag])
        tag_exists = backup_tag in tag_result.stdout

        if count != 1:
            debug_log(f"Squash validation failed: {count} commits instead of 1")
            return False

        if not tag_exists:
            debug_log(f"Squash validation failed: backup tag {backup_tag} not found")
            return False

        debug_log("Squash validation passed")
        return True
    except (subprocess.CalledProcessError, ValueError):
        return False


def show_pre_push_summary(auto_staged: bool, wip_count: int, plan_file: Optional[str], commit_message: str) -> None:
    """Show consolidated pre-push summary"""
    print("\n━━━ Pre-Push Summary ━━━", file=sys.stderr)
    if auto_staged:
        print("Auto-staged: unstaged changes committed", file=sys.stderr)
    print(f"Squashing: {wip_count} WIP commits → 1 commit", file=sys.stderr)
    if plan_file:
        print(f"Plan: {plan_file}", file=sys.stderr)
    print(f"\nFinal commit message:\n{commit_message}\n", file=sys.stderr)


def get_user_confirmation(prompt: str) -> bool:
    """Get user confirmation from /dev/tty"""
    try:
        with open('/dev/tty', 'r') as tty_in:
            print(f"{prompt} ", file=sys.stderr, end='', flush=True)
            response = tty_in.readline().strip().lower()
            return response in ['y', 'yes', '']
    except OSError:
        deny_command("Non-interactive environment - manual squash required")


def allow_command():
    """Output JSON to allow command execution"""
    output = {
        "hookSpecificOutput": {
            "permissionDecision": "allow"
        }
    }
    print(json.dumps(output))
    sys.exit(0)


def deny_command(reason: str):
    """Output JSON to block command execution"""
    output = {
        "hookSpecificOutput": {
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }
    print(json.dumps(output))
    sys.exit(0)


def validate_dependencies():
    """Validate Python and git are available"""
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        deny_command("Git command not found - please install git")


def main():
    """Main hook execution"""
    start_time = time.time()

    try:
        # Validate dependencies
        validate_dependencies()

        # Read hook input
        try:
            hook_input = json.loads(sys.stdin.read())
        except json.JSONDecodeError as e:
            deny_command(f"Error parsing hook input: {e}")

        # Extract command
        command = hook_input.get("tool_input", {}).get("command", "")
        debug_log(f"Received command: {command}")

        # Check if this is a push command
        if not is_push_command(command):
            log_execution("allow_non_push", duration_ms=int((time.time() - start_time) * 1000))
            allow_command()

        # Check current branch
        branch = get_current_branch()
        debug_log(f"Current branch: {branch}")
        if branch not in ['main', 'master']:
            log_execution("allow_feature_branch", duration_ms=int((time.time() - start_time) * 1000))
            allow_command()

        # Get commits to push
        commits = get_commits_to_push()
        if not commits:
            log_execution("allow_no_commits", duration_ms=int((time.time() - start_time) * 1000))
            allow_command()

        # Check for WIP commits
        if not has_wip_commits(commits):
            log_execution("allow_no_wip", duration_ms=int((time.time() - start_time) * 1000))
            allow_command()

        wip_count = len(commits)
        debug_log(f"Found {wip_count} WIP commits")

        # Handle single WIP commit specially
        if wip_count == 1:
            debug_log("Single WIP commit - removing prefix")
            commit_msg = run_git(['log', '--format=%B', '-n', '1', 'HEAD']).stdout.strip()
            if commit_msg.startswith('WIP: '):
                new_msg = commit_msg.replace('WIP: ', '', 1)
                run_git(['commit', '--amend', '-m', new_msg])
                print("Removed WIP prefix from single commit", file=sys.stderr)
            log_execution("allow_single_wip", wip_count=1, duration_ms=int((time.time() - start_time) * 1000))
            allow_command()

        # Check for merge conflicts
        if has_merge_conflicts():
            log_execution("deny_conflicts", wip_count=wip_count, duration_ms=int((time.time() - start_time) * 1000))
            deny_command("❌ Merge conflicts with origin/main\nResolve conflicts first: git rebase origin/main")

        # Check for interruption
        if interrupted:
            log_execution("deny_interrupted", wip_count=wip_count, duration_ms=int((time.time() - start_time) * 1000))
            deny_command("Interrupted by user")

        # Auto-commit unstaged changes if any
        auto_staged = False
        if has_unstaged_changes():
            auto_commit_unstaged()
            auto_staged = True
            wip_count += 1

        # Find plan file
        plan_file = find_plan_file()

        # Generate commit message
        commit_message = generate_commit_message(plan_file, wip_count)

        # Show summary and get confirmation
        show_pre_push_summary(auto_staged, wip_count, plan_file, commit_message)

        if not get_user_confirmation("Ready to squash and push? (Y/n)"):
            log_execution("deny_user_cancelled", wip_count=wip_count, duration_ms=int((time.time() - start_time) * 1000))
            deny_command("Push cancelled by user")

        # Create backup tag
        backup_tag = create_backup_tag()
        print(f"\nBackup tag created: {backup_tag}", file=sys.stderr)

        # Check for interruption before destructive operation
        if interrupted:
            log_execution("deny_interrupted", wip_count=wip_count, duration_ms=int((time.time() - start_time) * 1000))
            deny_command(f"Interrupted - backup tag preserved: {backup_tag}")

        # Squash commits
        try:
            squash_commits(commit_message)

            # Validate squash result
            if not validate_squash(backup_tag):
                log_execution("deny_squash_invalid", wip_count=wip_count, duration_ms=int((time.time() - start_time) * 1000))
                deny_command(f"Squash validation failed\nBackup tag preserved: {backup_tag}")

            print(f"✓ Squashed {wip_count} commits into 1", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            log_execution("deny_squash_failed", wip_count=wip_count, duration_ms=int((time.time() - start_time) * 1000))
            deny_command(f"Squash failed: {e}\nBackup tag preserved: {backup_tag}")

        # Show squashed commit for final review
        print("\n━━━ Squashed Commit ━━━", file=sys.stderr)
        result = run_git(['log', '-1', '--pretty=format:%B'])
        print(result.stdout, file=sys.stderr)
        print("━━━━━━━━━━━━━━━━━━━━━━━\n", file=sys.stderr)

        if not get_user_confirmation("Push this commit? (Y/n)"):
            # Restore from backup
            run_git(['reset', '--hard', backup_tag])
            log_execution("deny_final_cancelled", wip_count=wip_count, duration_ms=int((time.time() - start_time) * 1000))
            deny_command("Squash cancelled - restored to original state")

        # Allow the push
        log_execution("allow_squash_success", wip_count=wip_count, plan_file=plan_file, duration_ms=int((time.time() - start_time) * 1000))
        allow_command()

    except Exception as e:
        log_execution("error", duration_ms=int((time.time() - start_time) * 1000))
        debug_log(f"Unexpected error: {e}")
        deny_command(f"Hook error: {e}")


if __name__ == "__main__":
    main()
