#!/usr/bin/env python3
"""
Post-Push Cleanup Hook

PostToolUse:Bash hook that cleans up backup tags after successful git push.
"""

import json
import re
import subprocess
import sys


def is_push_command(command: str) -> bool:
    """Check if command is a git push"""
    patterns = [
        r'^git\s+push',
        r'^jj\s+git\s+push'
    ]
    return any(re.match(p, command) for p in patterns)


def delete_backup_tags():
    """Delete recent backup tags created by pre-push hook"""
    try:
        import time

        # List all backup tags
        result = subprocess.run(
            ['git', 'tag', '-l', 'backup/pre-squash-*'],
            capture_output=True,
            text=True,
            check=True
        )

        tags = result.stdout.strip().split('\n') if result.stdout.strip() else []
        current_time = int(time.time())

        # Delete tags only from last 5 minutes (recent pushes)
        for tag in tags:
            if tag:
                # Extract timestamp from tag name: backup/pre-squash-<sha>-<timestamp>
                parts = tag.split('-')
                if len(parts) >= 4:
                    try:
                        tag_timestamp = int(parts[-1])
                        # Only delete if tag is recent (last 5 minutes)
                        if current_time - tag_timestamp < 300:
                            subprocess.run(['git', 'tag', '-d', tag], capture_output=True, check=False)
                    except ValueError:
                        pass  # Skip tags with non-numeric timestamp

    except subprocess.CalledProcessError:
        pass  # Silently fail - cleanup is best-effort


def main():
    """Main hook execution"""
    try:
        # Read hook input
        hook_input = json.loads(sys.stdin.read())

        # Extract command and result
        command = hook_input.get("tool_input", {}).get("command", "")
        tool_result = hook_input.get("tool_result", {})
        exit_code = tool_result.get("exit_code", 0)

        # Only cleanup after successful push
        if is_push_command(command) and exit_code == 0:
            delete_backup_tags()

    except Exception:
        pass  # Silently fail - cleanup is best-effort

    sys.exit(0)


if __name__ == "__main__":
    main()
