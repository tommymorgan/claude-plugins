#!/usr/bin/env python3
"""
Tests for living spec updater

Scenarios:
- Work tool applies "creates" action
- Work tool applies "replaces" action
- Work tool applies "extends" action
- Work tool applies "removes" action
- Work tool applies "deprecates" action
"""

import shutil
import tempfile
import unittest
from pathlib import Path


class TestSpecUpdater(unittest.TestCase):
    """Test updating .feature files based on plan scenario actions"""

    def setUp(self):
        """Create test .feature file"""
        self.test_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.test_dir) / "specs"
        self.specs_dir.mkdir()

        self.feature_file = self.specs_dir / "authentication.feature"
        self.feature_file.write_text("""Feature: Authentication

  @user
  Scenario: User logs in
    Given I am on login page
    When I enter credentials
    Then I see dashboard
""")

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_creates_action_appends_new_scenario(self):
        """Should append new scenario when action is 'creates'"""
        from spec_updater import apply_action

        new_scenario = """@user
Scenario: User logs out
  Given I am logged in
  When I click logout
  Then I am logged out"""

        apply_action(
            self.feature_file,
            action="creates",
            scenario_text=new_scenario
        )

        content = self.feature_file.read_text()
        self.assertIn("Scenario: User logs out", content)
        self.assertIn("Scenario: User logs in", content)  # Original preserved

    def test_replaces_action_overwrites_existing(self):
        """Should completely replace existing scenario when action is 'replaces'"""
        from spec_updater import apply_action

        new_scenario = """@user
Scenario: User logs in
  Given I am on new login page
  When I enter new credentials
  Then I see new dashboard"""

        apply_action(
            self.feature_file,
            action="replaces",
            scenario_name="User logs in",
            scenario_text=new_scenario
        )

        content = self.feature_file.read_text()
        self.assertIn("new login page", content)
        self.assertNotIn("Given I am on login page", content)  # Old removed

    def test_extends_action_adds_steps(self):
        """Should add new steps to existing scenario when action is 'extends'"""
        from spec_updater import apply_action

        additional_steps = """  And I see welcome message
  And session is created"""

        apply_action(
            self.feature_file,
            action="extends",
            scenario_name="User logs in",
            additional_steps=additional_steps
        )

        content = self.feature_file.read_text()
        # Should have both old and new steps
        self.assertIn("Given I am on login page", content)  # Original
        self.assertIn("And I see welcome message", content)  # New
        self.assertIn("And session is created", content)  # New

    def test_removes_action_deletes_scenario(self):
        """Should delete scenario when action is 'removes'"""
        from spec_updater import apply_action

        apply_action(
            self.feature_file,
            action="removes",
            scenario_name="User logs in"
        )

        content = self.feature_file.read_text()
        self.assertNotIn("Scenario: User logs in", content)
        self.assertIn("Feature: Authentication", content)  # Feature preserved

    def test_deprecates_action_adds_tag(self):
        """Should add @deprecated tag when action is 'deprecates'"""
        from spec_updater import apply_action

        apply_action(
            self.feature_file,
            action="deprecates",
            scenario_name="User logs in",
            deprecation_note="Use SSO instead"
        )

        content = self.feature_file.read_text()
        self.assertIn("@deprecated", content)
        self.assertIn("Use SSO instead", content)
        self.assertIn("Scenario: User logs in", content)  # Scenario preserved


if __name__ == "__main__":
    unittest.main()
