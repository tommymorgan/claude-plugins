#!/usr/bin/env python3
"""
Migration tool to create living .feature files from historical plan files

This tool:
1. Scans a project's plans/ directory
2. Extracts Gherkin scenarios from User Requirements and Technical Specifications
3. Groups scenarios by feature area
4. Creates .feature files in specs/ directory with appropriate tags
"""

import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import List, Tuple


def extract_scenarios_from_plan(plan_content: str) -> Tuple[List[str], List[str]]:
    """
    Extract scenarios from a plan file's User Requirements and Technical Specifications sections.

    Args:
        plan_content: Full content of the plan markdown file

    Returns:
        Tuple of (user_scenarios, technical_scenarios)
    """
    user_scenarios = []
    tech_scenarios = []

    # Find all gherkin blocks and intelligently infer user vs technical
    gherkin_blocks = re.finditer(
        r"##\s+([^\n]+).*?```gherkin\s*(.*?)```",
        plan_content,
        re.DOTALL | re.MULTILINE
    )

    for block_match in gherkin_blocks:
        section_name = block_match.group(1).strip().lower()
        gherkin_content = block_match.group(2)

        # Extract scenarios from this block
        scenarios = re.findall(
            r"Scenario:.*?(?=Scenario:|$)",
            gherkin_content,
            re.DOTALL
        )
        scenarios = [s.strip() for s in scenarios if s.strip()]

        # Intelligent inference: determine if user or technical
        is_technical = any(keyword in section_name for keyword in [
            'technical', 'specification', 'implementation', 'api', 'database'
        ])

        is_user = any(keyword in section_name for keyword in [
            'user', 'requirement', 'feature', 'behavior'
        ]) or not is_technical  # Default to user if ambiguous

        if is_user and not is_technical:
            user_scenarios.extend(scenarios)
        else:
            tech_scenarios.extend(scenarios)

    return user_scenarios, tech_scenarios


def extract_feature_name_from_plan(plan_content: str) -> str:
    """
    Extract the feature name from the plan title.

    Args:
        plan_content: Full content of the plan markdown file

    Returns:
        Feature name in Title Case
    """
    # Try to extract from "# Feature: <name>"
    feature_match = re.search(r"#\s+Feature:\s+(.+)", plan_content)
    if feature_match:
        return feature_match.group(1).strip()

    # Fallback: use first heading
    heading_match = re.search(r"#\s+(.+)", plan_content)
    if heading_match:
        return heading_match.group(1).strip()

    return "Unknown Feature"


def extract_scenario_name(scenario: str) -> str:
    """
    Extract the name from a scenario.

    Args:
        scenario: Full scenario text

    Returns:
        Scenario name (text after "Scenario:")
    """
    match = re.search(r"Scenario:\s*(.+?)(?:\n|$)", scenario)
    if match:
        return match.group(1).strip()
    return ""


def extract_scenario_steps(scenario: str) -> List[str]:
    """
    Extract Given/When/Then/And steps from a scenario.

    Args:
        scenario: Full scenario text

    Returns:
        List of step lines
    """
    steps = []
    lines = scenario.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("Given ", "When ", "Then ", "And ", "But ")):
            steps.append(stripped)
    return steps


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two text strings using SequenceMatcher.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity score from 0.0 to 1.0
    """
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def calculate_scenario_similarity(scenario1: str, scenario2: str) -> float:
    """
    Calculate semantic similarity between two scenarios.

    Uses weighted similarity:
    - 60% scenario name similarity
    - 40% steps similarity

    Args:
        scenario1: First scenario text
        scenario2: Second scenario text

    Returns:
        Similarity score from 0.0 to 1.0
    """
    # Extract names and steps
    name1 = extract_scenario_name(scenario1)
    name2 = extract_scenario_name(scenario2)
    steps1 = extract_scenario_steps(scenario1)
    steps2 = extract_scenario_steps(scenario2)

    # Calculate name similarity (60% weight)
    name_similarity = calculate_text_similarity(name1, name2)

    # Calculate steps similarity (40% weight)
    if not steps1 and not steps2:
        # No steps in either - only compare names
        steps_similarity = 1.0
    elif not steps1 or not steps2:
        # One has steps, other doesn't
        steps_similarity = 0.0
    else:
        # Compare all steps as concatenated text
        steps1_text = " ".join(steps1)
        steps2_text = " ".join(steps2)
        steps_similarity = calculate_text_similarity(steps1_text, steps2_text)

    # Weighted average: 60% name, 40% steps
    similarity = (0.6 * name_similarity) + (0.4 * steps_similarity)

    return similarity


def are_scenarios_similar(
    scenario1: str,
    scenario2: str,
    threshold: float = 0.8
) -> bool:
    """
    Determine if two scenarios are similar enough to be considered matches.

    Args:
        scenario1: First scenario text
        scenario2: Second scenario text
        threshold: Similarity threshold (default 0.8)

    Returns:
        True if similarity >= threshold, False otherwise
    """
    similarity = calculate_scenario_similarity(scenario1, scenario2)
    return similarity >= threshold


def create_feature_file_content(
    feature_name: str,
    user_scenarios: List[str],
    tech_scenarios: List[str]
) -> str:
    """
    Create the content for a .feature file.

    Args:
        feature_name: Name of the feature
        user_scenarios: List of user-facing scenarios
        tech_scenarios: List of technical scenarios

    Returns:
        Complete .feature file content with proper tags
    """
    lines = [f"Feature: {feature_name}", ""]

    # Add user scenarios with @user tag
    for scenario in user_scenarios:
        lines.append("  @user")
        # Indent scenario lines
        for line in scenario.split("\n"):
            lines.append(f"  {line}")
        lines.append("")

    # Add technical scenarios with @technical tag
    for scenario in tech_scenarios:
        lines.append("  @technical")
        # Indent scenario lines
        for line in scenario.split("\n"):
            lines.append(f"  {line}")
        lines.append("")

    return "\n".join(lines)


def migrate_project(project_path: str) -> None:
    """
    Migrate a project's historical plans to living .feature files.

    Args:
        project_path: Path to the project directory
    """
    # Call the progress version without callbacks
    migrate_project_with_progress(project_path)


def migrate_project_with_progress(
    project_path: str,
    batch_size: int = 10,
    progress_callback=None
):
    """
    Migrate a project's historical plans with progress reporting and error handling.

    Args:
        project_path: Path to the project directory
        batch_size: Number of plans to process per batch (default 10)
        progress_callback: Optional callback(current, total, batch_num)

    Returns:
        dict: Summary with successes, failures, errors, total_plans
    """
    project_dir = Path(project_path)
    plans_dir = project_dir / "plans"
    specs_dir = project_dir / "specs"

    # Create specs directory if it doesn't exist
    specs_dir.mkdir(exist_ok=True)

    # Find all plan files
    plan_files = sorted(plans_dir.glob("*.md"))
    total_plans = len(plan_files)

    # Initialize tracking
    features = {}
    successes = 0
    failures = 0
    errors = []

    # Process in batches
    for batch_num, i in enumerate(range(0, total_plans, batch_size), 1):
        batch = plan_files[i:i + batch_size]

        for plan_file in batch:
            try:
                plan_content = plan_file.read_text()

                # Extract scenarios
                user_scenarios, tech_scenarios = extract_scenarios_from_plan(plan_content)

                # Skip if no scenarios
                if not user_scenarios and not tech_scenarios:
                    failures += 1
                    errors.append({
                        "file": str(plan_file.name),
                        "error": "No scenarios found"
                    })
                    continue

                # Extract feature name
                feature_name = extract_feature_name_from_plan(plan_content)

                # Group by feature
                if feature_name not in features:
                    features[feature_name] = {"user": [], "tech": []}

                features[feature_name]["user"].extend(user_scenarios)
                features[feature_name]["tech"].extend(tech_scenarios)

                successes += 1

            except Exception as e:
                # Log error and continue
                failures += 1
                errors.append({
                    "file": str(plan_file.name),
                    "error": str(e)
                })

        # Report progress after batch
        current = min(i + batch_size, total_plans)
        if progress_callback:
            progress_callback(current, total_plans, batch_num)

    # Create .feature files
    for feature_name, scenarios in features.items():
        # Convert feature name to kebab-case filename
        filename = feature_name.lower().replace(" ", "-") + ".feature"
        feature_file = specs_dir / filename

        # Create content
        content = create_feature_file_content(
            feature_name,
            scenarios["user"],
            scenarios["tech"]
        )

        # Write file
        feature_file.write_text(content)

    # Return summary
    return {
        "total_plans": total_plans,
        "successes": successes,
        "failures": failures,
        "errors": errors
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: migrate.py <project_path>")
        sys.exit(1)

    project_path = sys.argv[1]
    migrate_project(project_path)
    print(f"Migration complete! Check {project_path}/specs/ for .feature files")
