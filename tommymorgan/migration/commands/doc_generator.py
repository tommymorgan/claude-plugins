#!/usr/bin/env python3
"""
Documentation generator from living .feature files

Generates user and developer documentation from @user and @technical scenarios.
Supports evolutionary updates (preserves existing content while updating scenarios).
"""

import html
import re
from pathlib import Path
from typing import Dict, List, Optional

from feature_parser import build_scenario_index, load_feature_files


def scenario_to_prose(scenario_text: str) -> str:
    """
    Convert Gherkin scenario to readable prose.

    Args:
        scenario_text: Full scenario text with Given/When/Then

    Returns:
        Readable prose description
    """
    lines = scenario_text.split("\n")
    prose_parts = []

    # Extract scenario name
    name_match = re.search(r"Scenario:\s*(.+)", scenario_text)
    if name_match:
        prose_parts.append(name_match.group(1).strip())

    # Convert steps to prose
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Given "):
            prose_parts.append(stripped[6:].strip().capitalize())
        elif stripped.startswith("When "):
            prose_parts.append(stripped[5:].strip().lower())
        elif stripped.startswith("Then "):
            prose_parts.append(stripped[5:].strip().lower())
        elif stripped.startswith("And "):
            prose_parts.append(stripped[4:].strip().lower())
        elif stripped.startswith("But "):
            prose_parts.append(stripped[4:].strip().lower())

    # Join with proper punctuation
    if len(prose_parts) > 1:
        # First part (scenario name) as is, rest as continuous prose
        result = prose_parts[0] + ": " + ", ".join(prose_parts[1:]) + "."
    else:
        result = prose_parts[0] + "." if prose_parts else ""

    return result


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML content to prevent injection attacks.

    Args:
        text: Text to sanitize

    Returns:
        Escaped HTML-safe text
    """
    return html.escape(text)


def filter_scenarios_by_tags(
    scenarios: List[dict],
    tags: List[str]
) -> List[dict]:
    """
    Filter scenarios that have any of the specified tags.

    Args:
        scenarios: List of scenario dicts with 'tags' field
        tags: List of tags to filter by (e.g., ['@user', '@technical'])

    Returns:
        Filtered list of scenarios
    """
    filtered = []
    for scenario in scenarios:
        scenario_tags = scenario.get("tags", [])
        if any(tag in scenario_tags for tag in tags):
            filtered.append(scenario)
    return filtered


def generate_docs(
    specs_dir: Path,
    output_path: Path,
    tags: List[str],
    format: str = "markdown"
) -> None:
    """
    Generate documentation from living specs filtered by tags.

    Args:
        specs_dir: Path to specs/ directory
        output_path: Where to write documentation
        tags: Tags to filter scenarios (e.g., ['@user'])
        format: Output format ('markdown' or 'html')
    """
    # Load all .feature files
    features = load_feature_files(specs_dir)

    # Collect all scenarios with matching tags
    all_scenarios = []
    for feature_data in features.values():
        filtered = filter_scenarios_by_tags(feature_data["scenarios"], tags)
        for scenario in filtered:
            scenario["feature"] = feature_data["feature_name"]
            all_scenarios.append(scenario)

    # Generate output
    if format == "markdown":
        content = generate_markdown(all_scenarios)
    elif format == "html":
        content = generate_html(all_scenarios)
    else:
        raise ValueError(f"Unknown format: {format}")

    # Write output
    output_path.write_text(content)


def generate_markdown(scenarios: List[dict]) -> str:
    """Generate markdown documentation"""
    lines = ["# Documentation", ""]

    # Group by feature
    by_feature: Dict[str, List[dict]] = {}
    for scenario in scenarios:
        feature = scenario.get("feature", "Unknown")
        if feature not in by_feature:
            by_feature[feature] = []
        by_feature[feature].append(scenario)

    for feature_name, feature_scenarios in by_feature.items():
        lines.append(f"## {feature_name}")
        lines.append("")

        for scenario in feature_scenarios:
            lines.append(f"### {scenario['name']}")
            prose = scenario_to_prose(scenario["text"])
            lines.append(prose)
            lines.append("")

    return "\n".join(lines)


def generate_html(scenarios: List[dict]) -> str:
    """Generate semantic HTML documentation"""
    lines = [
        "<!DOCTYPE html>",
        "<html lang=\"en\">",
        "<head>",
        "  <meta charset=\"UTF-8\">",
        "  <title>Documentation</title>",
        "</head>",
        "<body>",
        "  <h1>Documentation</h1>",
    ]

    # Group by feature
    by_feature: Dict[str, List[dict]] = {}
    for scenario in scenarios:
        feature = scenario.get("feature", "Unknown")
        if feature not in by_feature:
            by_feature[feature] = []
        by_feature[feature].append(scenario)

    for feature_name, feature_scenarios in by_feature.items():
        lines.append(f"  <h2>{sanitize_html(feature_name)}</h2>")

        for scenario in feature_scenarios:
            lines.append(f"  <h3>{sanitize_html(scenario['name'])}</h3>")
            prose = scenario_to_prose(scenario["text"])
            lines.append(f"  <p>{sanitize_html(prose)}</p>")

    lines.append("</body>")
    lines.append("</html>")

    return "\n".join(lines)


def generate_docs_incremental(
    specs_dir: Path,
    doc_path: Path,
    tags: List[str]
) -> dict:
    """
    Generate documentation incrementally, preserving existing content.

    Args:
        specs_dir: Path to specs/ directory
        doc_path: Path to existing documentation file
        tags: Tags to filter scenarios

    Returns:
        dict: Result with existing_content, updated_sections, etc.
    """
    # Read existing documentation
    existing_content = ""
    introduction = ""

    if doc_path.exists():
        existing_content = doc_path.read_text()

        # Extract introduction and non-scenario sections
        # Look for feature-named sections that will be regenerated
        feature_names = set()
        features_data = load_feature_files(specs_dir)
        for feature_data in features_data.values():
            feature_names.add(feature_data["feature_name"])

        # Split by ## headings
        sections = re.split(r'\n(##\s+.+)', existing_content)

        # Preserve title and any sections not matching feature names
        preserved = [sections[0]] if sections else []

        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                heading = sections[i]
                content_part = sections[i + 1]

                # Check if this is a feature section
                heading_text = re.sub(r'##\s+', '', heading).strip()
                if heading_text not in feature_names:
                    # Not a feature section - preserve it
                    preserved.append(heading)
                    preserved.append(content_part)

        introduction = "".join(preserved).strip()

    # Load scenarios from specs
    features = load_feature_files(specs_dir)
    all_scenarios = []

    for feature_data in features.values():
        filtered = filter_scenarios_by_tags(feature_data["scenarios"], tags)
        for scenario in filtered:
            scenario["feature"] = feature_data["feature_name"]
            all_scenarios.append(scenario)

    # Generate scenario content
    scenario_content = generate_markdown(all_scenarios)

    # If we have an introduction, prepend it
    if introduction:
        # Remove the "# Documentation" heading from generated content
        scenario_content = re.sub(r'^#\s+Documentation\s*\n+', '', scenario_content)
        new_content = introduction + "\n\n" + scenario_content
    else:
        new_content = scenario_content

    # Write updated documentation
    doc_path.write_text(new_content)

    return {
        "existing_content": existing_content,
        "scenarios_count": len(all_scenarios),
        "updated": True
    }


def find_test_files(project_dir: Path) -> List[Path]:
    """
    Find test files in a project.

    Args:
        project_dir: Root project directory

    Returns:
        List of test file paths
    """
    test_files = []

    # Common test patterns
    patterns = [
        "**/test_*.py",
        "**/*_test.py",
        "**/test*.py",
        "**/*.test.js",
        "**/*.test.ts",
        "**/*.spec.js",
        "**/*.spec.ts"
    ]

    for pattern in patterns:
        test_files.extend(project_dir.glob(pattern))

    return test_files


def analyze_coverage(specs_dir: Path, project_dir: Path) -> dict:
    """
    Analyze test coverage of scenarios.

    Args:
        specs_dir: Path to specs/ directory
        project_dir: Root project directory

    Returns:
        dict: Coverage analysis with scenarios and percentage
    """
    # Load scenarios
    features = load_feature_files(specs_dir)
    all_scenarios = []

    for filename, feature_data in features.items():
        for scenario in feature_data["scenarios"]:
            all_scenarios.append({
                "name": scenario["name"],
                "file": filename,
                "feature": feature_data["feature_name"],
                "has_test": False,
                "test_file": None
            })

    # Find test files
    test_files = find_test_files(project_dir)

    # Match scenarios to tests (simple fuzzy matching)
    for scenario in all_scenarios:
        scenario_name_lower = scenario["name"].lower().replace(" ", "_")

        for test_file in test_files:
            test_content = test_file.read_text().lower()
            # Check if test name appears in file
            if scenario_name_lower in test_content or \
               scenario["name"].lower() in test_content:
                scenario["has_test"] = True
                scenario["test_file"] = str(test_file.name)
                break

    # Calculate coverage
    tested = sum(1 for s in all_scenarios if s["has_test"])
    total = len(all_scenarios)
    percentage = (tested / total * 100) if total > 0 else 0.0

    return {
        "scenarios": all_scenarios,
        "tested": tested,
        "total": total,
        "percentage": percentage
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: doc_generator.py <command> <specs_dir> <output_path> [--tags @user,@technical]")
        print("Commands: generate, coverage")
        sys.exit(1)

    command = sys.argv[1]
    specs_dir = Path(sys.argv[2])

    if command == "generate":
        output_path = Path(sys.argv[3])
        tags = ["@user"]  # Default
        if "--tags" in sys.argv:
            tags_arg = sys.argv[sys.argv.index("--tags") + 1]
            tags = tags_arg.split(",")

        generate_docs(specs_dir, output_path, tags)
        print(f"Documentation generated at {output_path}")

    elif command == "coverage":
        project_dir = Path(sys.argv[3])
        coverage = analyze_coverage(specs_dir, project_dir)

        print(f"\nTest Coverage Analysis:")
        print(f"Total scenarios: {coverage['total']}")
        print(f"Tested: {coverage['tested']}")
        print(f"Coverage: {coverage['percentage']:.1f}%")
        print(f"\nScenarios without tests:")

        for scenario in coverage["scenarios"]:
            if not scenario["has_test"]:
                print(f"  ✗ {scenario['name']} ({scenario['file']})")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
