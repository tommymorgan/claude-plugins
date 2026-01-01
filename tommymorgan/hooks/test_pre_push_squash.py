#!/usr/bin/env python3
"""
Tests for Pre-Push Squash Verification Hook

Tests follow TDD approach - write tests first, then implement.
"""

import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestCommandInterception(unittest.TestCase):
    """Test hook intercepts git push commands correctly"""

    def test_intercepts_git_push(self):
        """Should detect git push command and process it"""
        hook_input = {
            "tool_name": "Bash",
            "tool_input": {"command": "git push"}
        }

        # Hook should recognize this as a push command
        # Test will fail until we implement command detection
        from pre_push_squash import is_push_command
        self.assertTrue(is_push_command("git push"))

    def test_intercepts_git_push_with_remote(self):
        """Should detect git push origin main"""
        from pre_push_squash import is_push_command
        self.assertTrue(is_push_command("git push origin main"))

    def test_intercepts_jj_git_push(self):
        """Should detect jj git push command"""
        from pre_push_squash import is_push_command
        self.assertTrue(is_push_command("jj git push"))

    def test_rejects_command_injection(self):
        """Should reject git push with command injection attempt"""
        from pre_push_squash import is_push_command
        self.assertFalse(is_push_command("git push; rm -rf /"))
        self.assertFalse(is_push_command("git push && malicious"))
        self.assertFalse(is_push_command("git push | cat /etc/passwd"))

    def test_allows_non_push_commands(self):
        """Should not intercept non-push git commands"""
        from pre_push_squash import is_push_command
        self.assertFalse(is_push_command("git status"))
        self.assertFalse(is_push_command("git commit -m 'test'"))
        self.assertFalse(is_push_command("git log"))


class TestWIPDetection(unittest.TestCase):
    """Test WIP commit detection"""

    def test_detects_wip_commits(self):
        """Should detect commits with WIP: prefix"""
        commits = [
            "abc123 WIP: add feature",
            "def456 WIP: fix bug",
            "ghi789 feat: normal commit"
        ]

        from pre_push_squash import has_wip_commits
        self.assertTrue(has_wip_commits(commits))

    def test_no_wip_in_normal_commits(self):
        """Should return false when no WIP commits exist"""
        commits = [
            "abc123 feat: add feature",
            "def456 fix: bug fix"
        ]

        from pre_push_squash import has_wip_commits
        self.assertFalse(has_wip_commits(commits))


if __name__ == "__main__":
    unittest.main()
