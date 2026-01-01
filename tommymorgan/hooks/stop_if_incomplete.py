#!/usr/bin/env python3
"""
Stop Hook - Work Completion Enforcement

Enforces that work sessions are complete before stopping Claude Code.
Blocks stop if plan has TODO scenarios remaining (< 100% complete).
No exceptions - complete the work or use Ctrl+C to force quit.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def find_plan_file() -> Optional[Path]:
    """
    Search for plan file in current and parent directories (up to 3 levels).

    Returns:
        Path to plan file if found, None otherwise
    """
    current = Path.cwd()

    # Search current directory and up to 3 parent levels
    for _ in range(4):  # 0=current, 1-3=parents
        # Look for .md files in current directory
        for md_file in current.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                if is_tommymorgan_plan(content):
                    return md_file
            except (PermissionError, UnicodeDecodeError):
                continue

        # Look in common plan directories
        for subdir in ["plans", "docs/plans", "tools/claude-plugins/plans"]:
            plan_dir = current / subdir
            if plan_dir.exists():
                for md_file in plan_dir.glob("*.md"):
                    try:
                        content = md_file.read_text(encoding="utf-8")
                        if is_tommymorgan_plan(content):
                            return md_file
                    except (PermissionError, UnicodeDecodeError):
                        continue

        # Move up to parent directory
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent

    return None


def is_tommymorgan_plan(content: str) -> bool:
    """
    Check if content is a tommymorgan plan (has TODO/DONE markers).

    Args:
        content: File content to check

    Returns:
        True if file contains tommymorgan plan markers
    """
    has_user_requirements = "## User Requirements" in content
    has_tech_specs = "## Technical Specifications" in content
    has_markers = "<!-- TODO -->" in content or "<!-- DONE -->" in content

    return (has_user_requirements or has_tech_specs) and has_markers


def check_completion(plan_content: str) -> Dict[str, int]:
    """
    Parse plan and calculate completion status.

    Args:
        plan_content: Full plan file content

    Returns:
        Dict with todo_count, done_count, and completion_percentage
    """
    todo_count = len(re.findall(r"<!-- TODO -->", plan_content))
    done_count = len(re.findall(r"<!-- DONE -->", plan_content))

    total = todo_count + done_count
    if total == 0:
        completion_percentage = 100
    else:
        completion_percentage = int((done_count / total) * 100)

    return {
        "todo_count": todo_count,
        "done_count": done_count,
        "completion_percentage": completion_percentage,
    }


def make_stop_decision(completion: Optional[Dict[str, int]]) -> Dict[str, Any]:
    """
    Determine whether to allow or block stop based on completion.

    Args:
        completion: Completion info dict, or None if no plan found

    Returns:
        Dict with stopDecision and optional stopDecisionReason
    """
    # Allow stop if no active work session detected
    if completion is None:
        return {"stopDecision": "allow"}

    # Block if work is incomplete
    if completion["completion_percentage"] < 100:
        total = completion["todo_count"] + completion["done_count"]
        reason = (
            f"Work incomplete: {completion['todo_count']}/{total} scenarios TODO "
            f"({completion['completion_percentage']}%)"
        )
        return {"stopDecision": "block", "stopDecisionReason": reason}

    # Allow stop if work is complete
    return {"stopDecision": "allow"}


def is_safe_path(file_path: str) -> bool:
    """
    Validate that file path is safe (no path traversal attacks).

    Args:
        file_path: Path to validate

    Returns:
        True if path is safe, False otherwise
    """
    # Reject absolute paths outside current directory
    path = Path(file_path)

    # Allow relative paths
    if not path.is_absolute():
        # Check for ../ traversal attempts
        parts = Path(file_path).parts
        if ".." in parts:
            return False
        return True

    # Reject absolute paths
    return False


def format_output(decision: Dict[str, Any]) -> str:
    """
    Format stop decision as JSON for Claude Code.

    Args:
        decision: Dict with stopDecision and optional stopDecisionReason

    Returns:
        JSON string with hookSpecificOutput
    """
    output = {"hookSpecificOutput": decision}
    return json.dumps(output)


def main():
    """
    Main entry point for stop hook.

    Searches for plan file, checks completion, and outputs stop decision.
    """
    try:
        # Find plan file
        plan_file = find_plan_file()

        if plan_file is None:
            # No active work session detected
            decision = make_stop_decision(None)
            print(format_output(decision))
            return 0

        # Validate path safety (even though we found it ourselves)
        if not is_safe_path(str(plan_file)):
            sys.stderr.write(f"WARNING: Unsafe plan file path detected: {plan_file}\n")
            decision = make_stop_decision(None)
            print(format_output(decision))
            return 0

        # Read and check completion
        try:
            plan_content = plan_file.read_text(encoding="utf-8")
        except (PermissionError, UnicodeDecodeError) as e:
            sys.stderr.write(f"WARNING: Cannot read plan file: {e}\n")
            decision = make_stop_decision(None)
            print(format_output(decision))
            return 0

        # Validate plan format
        if not is_tommymorgan_plan(plan_content):
            sys.stderr.write(
                f"WARNING: Plan file format invalid: {plan_file}\n"
            )
            decision = make_stop_decision(None)
            print(format_output(decision))
            return 0

        # Check completion and make decision
        completion = check_completion(plan_content)
        decision = make_stop_decision(completion)

        # Output decision
        print(format_output(decision))

        # Log execution (optional, could add file logging here)
        # For now, just log to stderr for debugging
        sys.stderr.write(
            f"DEBUG: Plan: {plan_file}, Decision: {decision['stopDecision']}, "
            f"Completion: {completion['completion_percentage']}%\n"
        )

        return 0

    except Exception as e:
        # On any error, allow stop and log error
        sys.stderr.write(f"ERROR in stop hook: {e}\n")
        decision = {"stopDecision": "allow"}
        print(format_output(decision))
        return 0


if __name__ == "__main__":
    sys.exit(main())
