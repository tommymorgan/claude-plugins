#!/usr/bin/env python3
"""
Tests for Review-Plan Command

Tests follow TDD approach - write tests first, then implement.
"""

import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch


class TestPlanFileLoading(unittest.TestCase):
    """Test command can accept and load plan files"""

    def test_accepts_plan_file_path_argument(self):
        """Should read plan file from provided path argument"""
        from review_plan import load_plan_file

        mock_plan_content = """# Feature: Test Plan
**Goal**: Test goal

## User Requirements
<!-- TODO -->
Scenario: Test scenario
  Given context
  When action
  Then outcome
"""

        with patch("builtins.open", mock_open(read_data=mock_plan_content)):
            with patch("pathlib.Path.exists", return_value=True):
                result = load_plan_file("test-plan.md")

        self.assertIsNotNone(result)
        self.assertIn("content", result)
        self.assertEqual(result["content"], mock_plan_content)

    def test_validates_file_exists(self):
        """Should raise error when file doesn't exist"""
        from review_plan import load_plan_file

        with patch("pathlib.Path.exists", return_value=False):
            with self.assertRaises(FileNotFoundError):
                load_plan_file("nonexistent.md")

    def test_validates_file_is_readable(self):
        """Should raise error when file isn't readable"""
        from review_plan import load_plan_file

        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", side_effect=PermissionError("Access denied")):
                with self.assertRaises(PermissionError):
                    load_plan_file("unreadable.md")


class TestPlanMetadataExtraction(unittest.TestCase):
    """Test extracting metadata from plan files"""

    def test_extracts_goal_field(self):
        """Should extract **Goal** field from plan"""
        from review_plan import extract_metadata

        plan_content = """# Feature: Test Plan
**Created**: 2026-01-01
**Goal**: Add authentication to the API

## User Requirements
"""

        metadata = extract_metadata(plan_content)

        self.assertEqual(metadata["goal"], "Add authentication to the API")

    def test_extracts_created_date(self):
        """Should extract **Created** date from plan"""
        from review_plan import extract_metadata

        plan_content = """# Feature: Test Plan
**Created**: 2026-01-01
**Goal**: Test goal

## User Requirements
"""

        metadata = extract_metadata(plan_content)

        self.assertEqual(metadata["created"], "2026-01-01")

    def test_splits_user_requirements_section(self):
        """Should extract User Requirements section"""
        from review_plan import extract_metadata

        plan_content = """# Feature: Test Plan
**Goal**: Test goal

## User Requirements

<!-- TODO -->
Scenario: User scenario
  Given context
  When action
  Then outcome

## Technical Specifications

<!-- TODO -->
Scenario: Tech scenario
  Given context
"""

        metadata = extract_metadata(plan_content)

        self.assertIn("user_requirements", metadata)
        self.assertIn("User scenario", metadata["user_requirements"])

    def test_splits_technical_specifications_section(self):
        """Should extract Technical Specifications section"""
        from review_plan import extract_metadata

        plan_content = """# Feature: Test Plan
**Goal**: Test goal

## User Requirements
<!-- TODO -->
Scenario: User scenario

## Technical Specifications

<!-- TODO -->
Scenario: Tech scenario
  Given context
  When action
  Then outcome
"""

        metadata = extract_metadata(plan_content)

        self.assertIn("technical_specifications", metadata)
        self.assertIn("Tech scenario", metadata["technical_specifications"])

    def test_counts_todo_and_done_markers(self):
        """Should count <!-- TODO --> vs <!-- DONE --> markers"""
        from review_plan import extract_metadata

        plan_content = """# Feature: Test Plan
**Goal**: Test goal

## User Requirements

<!-- TODO -->
Scenario: Todo 1

<!-- DONE -->
Scenario: Done 1

<!-- TODO -->
Scenario: Todo 2

## Technical Specifications

<!-- TODO -->
Scenario: Todo 3

<!-- DONE -->
Scenario: Done 2
"""

        metadata = extract_metadata(plan_content)

        self.assertEqual(metadata["todo_count"], 3)
        self.assertEqual(metadata["done_count"], 2)


class TestContextDetection(unittest.TestCase):
    """Test detecting plan context from content"""

    def test_detects_api_context(self):
        """Should categorize as backend_service when API keywords present"""
        from review_plan import detect_plan_context

        plan_content = """# Feature: User Authentication API
**Goal**: Add user authentication endpoints

## User Requirements
Scenario: User logs in via API
  Given I have valid credentials
  When I POST to /api/auth/login with credentials
  Then I receive a JWT token
"""

        context = detect_plan_context(plan_content)

        self.assertIn("backend_service", context["categories"])

    def test_detects_cli_hook_context(self):
        """Should categorize as hook when hook keywords present"""
        from review_plan import detect_plan_context

        plan_content = """# Feature: Pre-push Hook
**Goal**: Add bash hook to verify commits

## Technical Specifications
Scenario: Hook intercepts push command
  Given hook is registered
  When user runs git push
  Then hook validates commits
"""

        context = detect_plan_context(plan_content)

        self.assertIn("hook", context["categories"])

    def test_detects_ui_component_context(self):
        """Should categorize as ui_component when UI keywords present"""
        from review_plan import detect_plan_context

        plan_content = """# Feature: Dashboard Component
**Goal**: Add dashboard web UI

## User Requirements
Scenario: User views dashboard
  Given I'm logged in
  When I navigate to the dashboard page
  Then I see my metrics
"""

        context = detect_plan_context(plan_content)

        self.assertIn("ui_component", context["categories"])

    def test_detects_database_context(self):
        """Should categorize as database_migration when database keywords present"""
        from review_plan import detect_plan_context

        plan_content = """# Feature: User Table Migration
**Goal**: Add database schema for users

## Technical Specifications
Scenario: Migration adds user table
  Given database is initialized
  When migration runs
  Then users table exists
"""

        context = detect_plan_context(plan_content)

        self.assertIn("database_migration", context["categories"])

    def test_detects_multiple_contexts(self):
        """Should detect multiple applicable contexts"""
        from review_plan import detect_plan_context

        plan_content = """# Feature: Full-stack Authentication
**Goal**: Add authentication API and UI

## User Requirements
Scenario: User logs in via web UI
  When I submit login form
  Then API validates credentials

## Technical Specifications
Scenario: Database stores users
  Given users table exists
  When user registers
  Then record saved to database
"""

        context = detect_plan_context(plan_content)

        self.assertIn("backend_service", context["categories"])
        self.assertIn("ui_component", context["categories"])
        self.assertIn("database_migration", context["categories"])


if __name__ == "__main__":
    unittest.main()
