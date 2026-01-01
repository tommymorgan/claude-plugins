#!/usr/bin/env python3
"""
Review Plan Module

Loads and parses plan files, extracts metadata for expert review.
"""

import re
from pathlib import Path
from typing import Dict, Any


def load_plan_file(file_path: str) -> Dict[str, Any]:
    """
    Load and validate plan file from provided path.

    Args:
        file_path: Path to the plan markdown file

    Returns:
        Dict containing 'content' key with file contents

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file isn't readable
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Plan file not found: {file_path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except PermissionError as e:
        raise PermissionError(f"Cannot read plan file: {file_path}") from e

    return {"content": content}


def extract_metadata(plan_content: str) -> Dict[str, Any]:
    """
    Extract metadata from plan file content.

    Extracts:
    - Goal field (via **Goal**: regex)
    - Created date (via **Created**: regex)
    - User Requirements section
    - Technical Specifications section
    - TODO count (<!-- TODO --> markers)
    - DONE count (<!-- DONE --> markers)

    Args:
        plan_content: Full markdown content of plan file

    Returns:
        Dict with extracted metadata
    """
    metadata = {}

    # Extract Goal field
    goal_match = re.search(r"\*\*Goal\*\*:\s*(.+)", plan_content)
    if goal_match:
        metadata["goal"] = goal_match.group(1).strip()

    # Extract Created date
    created_match = re.search(r"\*\*Created\*\*:\s*(.+)", plan_content)
    if created_match:
        metadata["created"] = created_match.group(1).strip()

    # Split sections
    user_req_match = re.search(
        r"## User Requirements\s*\n(.*?)(?=## Technical Specifications|$)",
        plan_content,
        re.DOTALL,
    )
    if user_req_match:
        metadata["user_requirements"] = user_req_match.group(1).strip()

    tech_spec_match = re.search(
        r"## Technical Specifications\s*\n(.*?)(?=## Notes|$)", plan_content, re.DOTALL
    )
    if tech_spec_match:
        metadata["technical_specifications"] = tech_spec_match.group(1).strip()

    # Count TODO/DONE markers
    metadata["todo_count"] = len(re.findall(r"<!-- TODO -->", plan_content))
    metadata["done_count"] = len(re.findall(r"<!-- DONE -->", plan_content))

    return metadata


def detect_plan_context(plan_content: str) -> Dict[str, Any]:
    """
    Detect plan context from content by scanning for keywords.

    Keywords indicate the type of system being built:
    - API, endpoint, HTTP, REST → backend_service
    - hook, bash, CLI → hook
    - web, UI, page, component, dashboard → ui_component
    - database, schema, migration, table → database_migration

    Args:
        plan_content: Full markdown content of plan file

    Returns:
        Dict with 'categories' list of detected context types
    """
    context = {"categories": []}

    # Convert to lowercase for case-insensitive matching
    content_lower = plan_content.lower()

    # Define keyword patterns for each category
    api_keywords = ["api", "endpoint", "http", "rest", "/api/", "jwt", "auth"]
    hook_keywords = ["hook", "bash", "cli", "git push", "pre-push", "command"]
    ui_keywords = ["web", "ui", "page", "component", "dashboard", "form", "button"]
    db_keywords = ["database", "schema", "migration", "table", "postgres", "sql"]

    # Check for each category
    if any(keyword in content_lower for keyword in api_keywords):
        context["categories"].append("backend_service")

    if any(keyword in content_lower for keyword in hook_keywords):
        context["categories"].append("hook")

    if any(keyword in content_lower for keyword in ui_keywords):
        context["categories"].append("ui_component")

    if any(keyword in content_lower for keyword in db_keywords):
        context["categories"].append("database_migration")

    return context
