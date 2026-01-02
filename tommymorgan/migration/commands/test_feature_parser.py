#!/usr/bin/env python3
"""
Tests for .feature file parsing

Scenario: Plan tool loads existing living specs
  Given a project path is determined
  When the plan tool starts reconciliation
  Then it reads all .feature files from specs/ directory
  And it parses Feature and Scenario names
  And it builds a searchable index of existing scenarios
  And the index supports fuzzy name matching
"""

import shutil
import tempfile
import unittest
from pathlib import Path


class TestFeatureFileParsing(unittest.TestCase):
    """Test parsing .feature files for living specs"""

    def setUp(self):
        """Create test specs directory"""
        self.test_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.test_dir) / "specs"
        self.specs_dir.mkdir()

        # Create sample .feature file
        feature_content = """Feature: User Authentication

  @user
  Scenario: User logs in successfully
    Given I am on the login page
    When I enter valid credentials
    Then I am redirected to dashboard

  @technical
  Scenario: JWT token generation
    Given user authenticates
    When auth service processes request
    Then JWT token is issued
"""
        (self.specs_dir / "authentication.feature").write_text(feature_content)

    def tearDown(self):
        """Clean up test directory"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_reads_all_feature_files(self):
        """Should find and read all .feature files in specs/ directory"""
        from feature_parser import load_feature_files

        features = load_feature_files(self.specs_dir)

        self.assertEqual(len(features), 1)
        self.assertIn("authentication.feature", features)

    def test_parses_feature_name(self):
        """Should extract Feature name from .feature file"""
        from feature_parser import load_feature_files

        features = load_feature_files(self.specs_dir)
        auth_feature = features["authentication.feature"]

        self.assertEqual(auth_feature["feature_name"], "User Authentication")

    def test_parses_scenario_names(self):
        """Should extract all scenario names"""
        from feature_parser import load_feature_files

        features = load_feature_files(self.specs_dir)
        auth_feature = features["authentication.feature"]

        self.assertEqual(len(auth_feature["scenarios"]), 2)
        scenario_names = [s["name"] for s in auth_feature["scenarios"]]

        self.assertIn("User logs in successfully", scenario_names)
        self.assertIn("JWT token generation", scenario_names)

    def test_builds_searchable_index(self):
        """Should build searchable index of scenarios"""
        from feature_parser import build_scenario_index, load_feature_files

        features = load_feature_files(self.specs_dir)
        index = build_scenario_index(features)

        # Should be able to find scenarios
        self.assertIn("User logs in successfully", index)
        self.assertIn("JWT token generation", index)

        # Index should include file and full scenario text
        login_entry = index["User logs in successfully"]
        self.assertEqual(login_entry["file"], "authentication.feature")
        self.assertIn("Given I am on the login page", login_entry["text"])

    def test_supports_fuzzy_name_matching(self):
        """Should support finding scenarios with similar names"""
        from feature_parser import find_similar_scenarios, load_feature_files, build_scenario_index

        features = load_feature_files(self.specs_dir)
        index = build_scenario_index(features)

        # Search for similar scenario
        matches = find_similar_scenarios(
            "User login successful",
            index,
            threshold=0.7
        )

        self.assertGreater(len(matches), 0)
        # Should find "User logs in successfully"
        self.assertTrue(
            any("User logs in successfully" in m["name"] for m in matches)
        )


if __name__ == "__main__":
    unittest.main()
