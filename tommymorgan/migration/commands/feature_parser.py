#!/usr/bin/env python3
"""
Parser for .feature files containing living Gherkin specifications

Used by plan tool for interactive reconciliation with existing living specs.
"""

import re
from pathlib import Path
from typing import Dict, List


def load_feature_files(specs_dir: Path) -> Dict[str, dict]:
    """
    Load and parse all .feature files from specs/ directory.

    Args:
        specs_dir: Path to specs/ directory

    Returns:
        Dict mapping filename to parsed feature data:
        {
            "filename.feature": {
                "feature_name": "Feature Name",
                "scenarios": [
                    {
                        "name": "Scenario name",
                        "text": "Full scenario text with steps",
                        "tags": ["@user", "@api"]
                    }
                ]
            }
        }
    """
    features = {}

    for feature_file in specs_dir.glob("*.feature"):
        content = feature_file.read_text()

        # Extract feature name
        feature_match = re.search(r"Feature:\s*(.+)", content)
        feature_name = feature_match.group(1).strip() if feature_match else "Unknown"

        # Extract scenarios using simpler regex approach
        scenarios = []

        # Find all scenario blocks (tags + Scenario + steps)
        # Pattern matches from @ tags through scenario content
        pattern = r'((?:\s*@\w+(?:\s+@\w+)*\s*\n)*)\s*Scenario:\s*([^\n]+)((?:\n(?!\s*(?:@\w+|Scenario:)).*)*)'

        for match in re.finditer(pattern, content, re.MULTILINE):
            tags_block = match.group(1)
            scenario_name = match.group(2).strip()
            scenario_steps = match.group(3).strip()

            # Extract all @tags from the tags block
            tags = re.findall(r'@\w+', tags_block)

            # Full scenario text is name + steps
            scenario_text = scenario_name
            if scenario_steps:
                scenario_text += "\n" + scenario_steps

            scenarios.append({
                "name": scenario_name,
                "text": scenario_text,
                "tags": tags
            })

        features[feature_file.name] = {
            "feature_name": feature_name,
            "scenarios": scenarios
        }

    return features


def build_scenario_index(features: Dict[str, dict]) -> Dict[str, dict]:
    """
    Build a searchable index of all scenarios.

    Args:
        features: Output from load_feature_files()

    Returns:
        Dict mapping scenario name to scenario data:
        {
            "Scenario name": {
                "file": "filename.feature",
                "feature": "Feature Name",
                "text": "Full scenario text",
                "tags": ["@user"]
            }
        }
    """
    index = {}

    for filename, feature_data in features.items():
        for scenario in feature_data["scenarios"]:
            index[scenario["name"]] = {
                "file": filename,
                "feature": feature_data["feature_name"],
                "text": scenario["text"],
                "tags": scenario["tags"]
            }

    return index


def find_similar_scenarios(
    query: str,
    index: Dict[str, dict],
    threshold: float = 0.7
) -> List[dict]:
    """
    Find scenarios with similar names using fuzzy matching.

    Args:
        query: Scenario name to search for
        index: Scenario index from build_scenario_index()
        threshold: Similarity threshold (default 0.7)

    Returns:
        List of matching scenarios sorted by similarity:
        [
            {
                "name": "Scenario name",
                "similarity": 0.95,
                "file": "filename.feature",
                "feature": "Feature Name",
                "text": "Full scenario text",
                "tags": ["@user"]
            }
        ]
    """
    from difflib import SequenceMatcher

    matches = []

    for scenario_name, scenario_data in index.items():
        # Calculate name similarity
        similarity = SequenceMatcher(
            None,
            query.lower(),
            scenario_name.lower()
        ).ratio()

        if similarity >= threshold:
            matches.append({
                "name": scenario_name,
                "similarity": similarity,
                **scenario_data
            })

    # Sort by similarity (highest first)
    matches.sort(key=lambda x: x["similarity"], reverse=True)

    return matches


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: feature_parser.py <specs_directory>")
        sys.exit(1)

    specs_dir = Path(sys.argv[1])
    features = load_feature_files(specs_dir)
    index = build_scenario_index(features)

    print(f"Loaded {len(features)} feature files")
    print(f"Found {len(index)} scenarios")

    for name in index:
        print(f"  - {name}")
