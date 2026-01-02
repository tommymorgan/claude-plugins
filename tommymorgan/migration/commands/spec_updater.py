#!/usr/bin/env python3
"""
Living specification updater

Applies actions (creates/replaces/extends/removes/deprecates) to .feature files
based on plan scenario metadata.
"""

import re
from pathlib import Path
from typing import Optional


def find_scenario_in_content(content: str, scenario_name: str) -> Optional[tuple]:
    """
    Find a scenario in .feature file content.

    Returns:
        Tuple of (start_pos, end_pos, full_scenario_text) or None
    """
    # Pattern to match scenario with its tags and content
    # Captures from any @tags through the scenario until next scenario or EOF
    pattern = rf"((?:@\w+\s+)*)\s*Scenario:\s*{re.escape(scenario_name)}.*?(?=(?:@\w+\s+)?Scenario:|$)"

    match = re.search(pattern, content, re.DOTALL)
    if match:
        return (match.start(), match.end(), match.group(0))

    return None


def apply_action(
    feature_file: Path,
    action: str,
    scenario_text: str = "",
    scenario_name: str = "",
    additional_steps: str = "",
    deprecation_note: str = ""
) -> None:
    """
    Apply an action to a .feature file.

    Args:
        feature_file: Path to .feature file
        action: One of creates/replaces/extends/removes/deprecates
        scenario_text: Full new scenario text (for creates/replaces)
        scenario_name: Name of scenario to modify (for replaces/extends/removes/deprecates)
        additional_steps: Steps to add (for extends)
        deprecation_note: Note explaining deprecation (for deprecates)
    """
    content = feature_file.read_text()

    if action == "creates":
        # Append new scenario to end of file
        if not content.endswith("\n"):
            content += "\n"
        content += "\n" + scenario_text + "\n"

    elif action == "replaces":
        # Find and replace existing scenario
        result = find_scenario_in_content(content, scenario_name)
        if result:
            start, end, _old_text = result
            content = content[:start] + scenario_text + content[end:]
        else:
            raise ValueError(f"Scenario '{scenario_name}' not found for replacement")

    elif action == "extends":
        # Find scenario and add steps before the next scenario
        result = find_scenario_in_content(content, scenario_name)
        if result:
            start, end, old_text = result
            # Add additional steps at the end of the scenario
            extended = old_text.rstrip() + "\n" + additional_steps
            content = content[:start] + extended + content[end:]
        else:
            raise ValueError(f"Scenario '{scenario_name}' not found for extension")

    elif action == "removes":
        # Find and delete scenario
        result = find_scenario_in_content(content, scenario_name)
        if result:
            start, end, _old_text = result
            # Remove the scenario and clean up extra newlines
            content = content[:start] + content[end:]
            # Clean up multiple consecutive newlines
            content = re.sub(r"\n{3,}", "\n\n", content)
        else:
            raise ValueError(f"Scenario '{scenario_name}' not found for removal")

    elif action == "deprecates":
        # Find scenario and add @deprecated tag + comment
        result = find_scenario_in_content(content, scenario_name)
        if result:
            start, end, old_text = result
            # Add @deprecated tag at the start (before other tags)
            deprecated_text = f"@deprecated\n  # {deprecation_note}\n{old_text}"
            content = content[:start] + deprecated_text + content[end:]
        else:
            raise ValueError(f"Scenario '{scenario_name}' not found for deprecation")

    else:
        raise ValueError(f"Unknown action: {action}")

    # Write updated content
    feature_file.write_text(content)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: spec_updater.py <feature_file> <action> <scenario_name> [scenario_text]")
        sys.exit(1)

    feature_file = Path(sys.argv[1])
    action = sys.argv[2]
    scenario_name = sys.argv[3]
    scenario_text = sys.argv[4] if len(sys.argv) > 4 else ""

    apply_action(feature_file, action, scenario_text, scenario_name)
    print(f"Applied action '{action}' to {feature_file}")
