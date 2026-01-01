#!/usr/bin/env python3
"""
Tests for Stop Hook - Work Completion Enforcement

Tests follow TDD approach - write tests first, then implement.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch


class TestStopHookRegistration(unittest.TestCase):
    """Test hook is properly registered in hooks.json"""

    def test_hooks_json_exists(self):
        """Should have hooks.json file"""
        hooks_file = Path(__file__).parent / "hooks.json"
        self.assertTrue(hooks_file.exists(), "hooks.json should exist")

    def test_stop_hook_registered(self):
        """Should register Stop hook in hooks.json"""
        hooks_file = Path(__file__).parent / "hooks.json"
        with open(hooks_file, "r") as f:
            config = json.load(f)

        self.assertIn("Stop", config, "Stop hook should be registered")

    def test_stop_hook_points_to_script(self):
        """Should point to stop_if_incomplete.py script"""
        hooks_file = Path(__file__).parent / "hooks.json"
        with open(hooks_file, "r") as f:
            config = json.load(f)

        stop_config = config.get("Stop", {})
        self.assertIn("command", stop_config)
        self.assertIn("stop_if_incomplete.py", stop_config["command"])

    def test_stop_hook_has_timeout(self):
        """Should configure timeout of 5000ms"""
        hooks_file = Path(__file__).parent / "hooks.json"
        with open(hooks_file, "r") as f:
            config = json.load(f)

        stop_config = config.get("Stop", {})
        self.assertEqual(stop_config.get("timeout"), 5000)


class TestWorkSessionDetection(unittest.TestCase):
    """Test detecting active work sessions"""

    def test_finds_plan_file_in_current_directory(self):
        """Should find plan file in current directory"""
        from stop_if_incomplete import find_plan_file

        with tempfile.TemporaryDirectory() as tmpdir:
            plan_path = Path(tmpdir) / "plan.md"
            plan_path.write_text(
                "## User Requirements\n<!-- TODO -->\nScenario: Test"
            )

            with patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                result = find_plan_file()

            self.assertIsNotNone(result)
            self.assertEqual(result.name, "plan.md")

    def test_searches_parent_directories(self):
        """Should search up to 3 parent directory levels"""
        from stop_if_incomplete import find_plan_file

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create plan in parent directory
            plan_path = Path(tmpdir) / "plan.md"
            plan_path.write_text(
                "## User Requirements\n<!-- TODO -->\nScenario: Test"
            )

            # Work from subdirectory
            subdir = Path(tmpdir) / "sub1" / "sub2"
            subdir.mkdir(parents=True)

            with patch("pathlib.Path.cwd", return_value=subdir):
                result = find_plan_file()

            self.assertIsNotNone(result)
            self.assertEqual(result.name, "plan.md")

    def test_recognizes_tommymorgan_plan_pattern(self):
        """Should check for TODO/DONE markers to identify tommymorgan plan"""
        from stop_if_incomplete import is_tommymorgan_plan

        valid_plan = """# Feature: Test
**Goal**: Test

## User Requirements
<!-- TODO -->
Scenario: Test scenario

## Technical Specifications
<!-- DONE -->
Scenario: Done scenario
"""

        self.assertTrue(is_tommymorgan_plan(valid_plan))

    def test_rejects_non_tommymorgan_plans(self):
        """Should reject files without TODO/DONE markers"""
        from stop_if_incomplete import is_tommymorgan_plan

        invalid_plan = """# Just a README
This is not a plan file.
"""

        self.assertFalse(is_tommymorgan_plan(invalid_plan))


class TestCompletionChecking(unittest.TestCase):
    """Test completion status checking"""

    def test_parses_todo_markers(self):
        """Should count <!-- TODO --> markers"""
        from stop_if_incomplete import check_completion

        plan_content = """## User Requirements
<!-- TODO -->
Scenario: Test 1

<!-- TODO -->
Scenario: Test 2

<!-- DONE -->
Scenario: Done 1
"""

        result = check_completion(plan_content)

        self.assertEqual(result["todo_count"], 2)

    def test_parses_done_markers(self):
        """Should count <!-- DONE --> markers"""
        from stop_if_incomplete import check_completion

        plan_content = """## User Requirements
<!-- TODO -->
Scenario: Test 1

<!-- DONE -->
Scenario: Done 1

<!-- DONE -->
Scenario: Done 2
"""

        result = check_completion(plan_content)

        self.assertEqual(result["done_count"], 2)

    def test_calculates_completion_percentage(self):
        """Should calculate completion as done / (todo + done)"""
        from stop_if_incomplete import check_completion

        plan_content = """## User Requirements
<!-- TODO -->
Scenario: Test 1

<!-- TODO -->
Scenario: Test 2

<!-- DONE -->
Scenario: Done 1

<!-- DONE -->
Scenario: Done 2

<!-- DONE -->
Scenario: Done 3
"""

        result = check_completion(plan_content)

        # 3 done / 5 total = 60%
        self.assertEqual(result["completion_percentage"], 60)


class TestStopDecisions(unittest.TestCase):
    """Test stop allow/block decisions"""

    def test_blocks_when_work_incomplete(self):
        """Should block stop when completion < 100%"""
        from stop_if_incomplete import make_stop_decision

        completion = {"completion_percentage": 40, "todo_count": 3, "done_count": 2}

        decision = make_stop_decision(completion)

        self.assertEqual(decision["stopDecision"], "block")
        self.assertIn("Work incomplete", decision["stopDecisionReason"])

    def test_allows_stop_when_work_complete(self):
        """Should allow stop when completion = 100%"""
        from stop_if_incomplete import make_stop_decision

        completion = {"completion_percentage": 100, "todo_count": 0, "done_count": 5}

        decision = make_stop_decision(completion)

        self.assertEqual(decision["stopDecision"], "allow")

    def test_allows_stop_when_no_plan_found(self):
        """Should allow stop when no active work session detected"""
        from stop_if_incomplete import make_stop_decision

        decision = make_stop_decision(None)

        self.assertEqual(decision["stopDecision"], "allow")


class TestOverrideMechanism(unittest.TestCase):
    """Test override via environment variable"""

    def test_allows_override_via_env_var(self):
        """Should allow stop with TOMMYMORGAN_ALLOW_INCOMPLETE_STOP=true"""
        from stop_if_incomplete import make_stop_decision

        completion = {"completion_percentage": 40, "todo_count": 3, "done_count": 2}

        with patch.dict(os.environ, {"TOMMYMORGAN_ALLOW_INCOMPLETE_STOP": "true"}):
            decision = make_stop_decision(completion)

        self.assertEqual(decision["stopDecision"], "allow")

    def test_logs_override_usage(self):
        """Should log warning when override is used"""
        from stop_if_incomplete import make_stop_decision

        completion = {"completion_percentage": 40, "todo_count": 3, "done_count": 2}

        with patch.dict(os.environ, {"TOMMYMORGAN_ALLOW_INCOMPLETE_STOP": "true"}):
            with patch("sys.stderr") as mock_stderr:
                decision = make_stop_decision(completion)

        # Should write warning to stderr
        self.assertTrue(mock_stderr.write.called)


class TestPathValidation(unittest.TestCase):
    """Test plan file path validation"""

    def test_rejects_path_traversal(self):
        """Should reject paths with ../ or absolute paths outside project"""
        from stop_if_incomplete import is_safe_path

        self.assertFalse(is_safe_path("/etc/passwd"))
        self.assertFalse(is_safe_path("../../etc/passwd"))
        self.assertFalse(is_safe_path("../../../sensitive"))

    def test_allows_paths_within_project(self):
        """Should allow relative paths within project"""
        from stop_if_incomplete import is_safe_path

        self.assertTrue(is_safe_path("plan.md"))
        self.assertTrue(is_safe_path("./plans/feature.md"))
        self.assertTrue(is_safe_path("docs/plans/2026-01-01-feature.md"))


class TestJSONOutput(unittest.TestCase):
    """Test JSON output format"""

    def test_outputs_valid_json_for_block(self):
        """Should output valid JSON with stopDecision: block"""
        from stop_if_incomplete import format_output

        decision = {
            "stopDecision": "block",
            "stopDecisionReason": "Work incomplete: 3/5 scenarios TODO (60%)",
        }

        output = format_output(decision)

        parsed = json.loads(output)
        self.assertEqual(parsed["hookSpecificOutput"]["stopDecision"], "block")
        self.assertIn("Work incomplete", parsed["hookSpecificOutput"]["stopDecisionReason"])

    def test_outputs_valid_json_for_allow(self):
        """Should output valid JSON with stopDecision: allow"""
        from stop_if_incomplete import format_output

        decision = {"stopDecision": "allow"}

        output = format_output(decision)

        parsed = json.loads(output)
        self.assertEqual(parsed["hookSpecificOutput"]["stopDecision"], "allow")


if __name__ == "__main__":
    unittest.main()
