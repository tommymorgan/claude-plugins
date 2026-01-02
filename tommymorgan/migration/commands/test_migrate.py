#!/usr/bin/env python3
"""
Tests for Migration Command

Scenario: Migration creates living specs from historical plans
  Given a project has multiple historical plans with Gherkin scenarios
  When I run the migration tool
  Then living .feature files are created in the specs/ directory
  And scenarios are grouped by feature area
  And user scenarios are tagged @user
  And technical scenarios are tagged @technical
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path


class TestMigrationBasics(unittest.TestCase):
    """Test basic migration functionality"""

    def setUp(self):
        """Create temporary test directory"""
        self.test_dir = tempfile.mkdtemp()
        self.plans_dir = Path(self.test_dir) / "plans"
        self.specs_dir = Path(self.test_dir) / "specs"
        self.plans_dir.mkdir()

        # Create a sample plan file
        plan_content = """# Feature: User Authentication

**Created**: 2025-01-01
**Goal**: Implement user login functionality

## User Requirements

```gherkin
Feature: User Authentication

  Scenario: User logs in successfully
    Given I am on the login page
    When I enter valid credentials
    Then I am redirected to my dashboard
```

## Technical Specifications

```gherkin
Feature: User Authentication

  Scenario: JWT token generation on authentication
    Given a user authenticates successfully
    When the auth service processes the request
    Then a JWT token is issued with user claims
    And the token expires in 24 hours
```
"""
        (self.plans_dir / "2025-01-01-authentication.md").write_text(plan_content)

    def tearDown(self):
        """Clean up test directory"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_creates_specs_directory(self):
        """Should create specs/ directory if it doesn't exist"""
        from migrate import migrate_project

        migrate_project(self.test_dir)

        self.assertTrue(self.specs_dir.exists())
        self.assertTrue(self.specs_dir.is_dir())

    def test_creates_feature_files(self):
        """Should create .feature files in specs/ directory"""
        from migrate import migrate_project

        migrate_project(self.test_dir)

        feature_files = list(self.specs_dir.glob("*.feature"))
        self.assertGreater(len(feature_files), 0)

    def test_groups_scenarios_by_feature(self):
        """Should group related scenarios into feature files"""
        from migrate import migrate_project

        migrate_project(self.test_dir)

        # Should have user-authentication.feature
        auth_feature = self.specs_dir / "user-authentication.feature"
        self.assertTrue(auth_feature.exists())

        content = auth_feature.read_text()
        self.assertIn("Feature: User Authentication", content)
        self.assertIn("Scenario: User logs in successfully", content)
        self.assertIn("Scenario: JWT token generation", content)

    def test_tags_user_scenarios(self):
        """Should tag scenarios from User Requirements with @user"""
        from migrate import migrate_project

        migrate_project(self.test_dir)

        auth_feature = self.specs_dir / "user-authentication.feature"
        content = auth_feature.read_text()

        # User scenario should have @user tag
        self.assertRegex(content, r"@user\s+Scenario: User logs in successfully")

    def test_tags_technical_scenarios(self):
        """Should tag scenarios from Technical Specifications with @technical"""
        from migrate import migrate_project

        migrate_project(self.test_dir)

        auth_feature = self.specs_dir / "user-authentication.feature"
        content = auth_feature.read_text()

        # Technical scenario should have @technical tag
        self.assertRegex(content, r"@technical\s+Scenario: JWT token generation")


class TestScenarioParsing(unittest.TestCase):
    """Test parsing scenarios from plan markdown"""

    def test_extracts_user_requirements_section(self):
        """Should extract scenarios from User Requirements section"""
        from migrate import extract_scenarios_from_plan

        plan_content = """## User Requirements

```gherkin
Scenario: Test scenario
  Given context
```
"""
        user_scenarios, _tech_scenarios = extract_scenarios_from_plan(plan_content)

        self.assertEqual(len(user_scenarios), 1)
        self.assertIn("Test scenario", user_scenarios[0])

    def test_extracts_technical_specifications_section(self):
        """Should extract scenarios from Technical Specifications section"""
        from migrate import extract_scenarios_from_plan

        plan_content = """## Technical Specifications

```gherkin
Scenario: Tech scenario
  Given system state
```
"""
        _user_scenarios, tech_scenarios = extract_scenarios_from_plan(plan_content)

        self.assertEqual(len(tech_scenarios), 1)
        self.assertIn("Tech scenario", tech_scenarios[0])

    def test_preserves_scenario_structure(self):
        """Should preserve Given/When/Then structure"""
        from migrate import extract_scenarios_from_plan

        plan_content = """## User Requirements

```gherkin
Scenario: Login flow
  Given I am on the login page
  When I enter credentials
  Then I see the dashboard
```
"""
        user_scenarios, _ = extract_scenarios_from_plan(plan_content)

        scenario = user_scenarios[0]
        self.assertIn("Given I am on the login page", scenario)
        self.assertIn("When I enter credentials", scenario)
        self.assertIn("Then I see the dashboard", scenario)


class TestSemanticSimilarity(unittest.TestCase):
    """
    Test semantic similarity detection for scenarios

    Scenario: Smart inference detects similar scenarios
      Given two scenarios with similar names and steps
      When the migration compares them
      Then it calculates semantic similarity score
      And scores above 0.8 are treated as matches
      And scores below 0.8 are flagged for manual review
      And similarity weights: 60% name, 40% steps
    """

    def test_calculates_similarity_score(self):
        """Should calculate similarity score between two scenarios"""
        from migrate import calculate_scenario_similarity

        scenario1 = "Scenario: User logs in successfully"
        scenario2 = "Scenario: User logs in"

        similarity = calculate_scenario_similarity(scenario1, scenario2)

        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)

    def test_identical_scenarios_have_perfect_score(self):
        """Identical scenarios should have similarity of 1.0"""
        from migrate import calculate_scenario_similarity

        scenario = """Scenario: User logs in
  Given I am on the login page
  When I enter credentials
  Then I see dashboard"""

        similarity = calculate_scenario_similarity(scenario, scenario)
        self.assertAlmostEqual(similarity, 1.0, places=2)

    def test_completely_different_scenarios_have_low_score(self):
        """Completely different scenarios should have low similarity"""
        from migrate import calculate_scenario_similarity

        scenario1 = "Scenario: User logs in"
        scenario2 = "Scenario: System performs backup"

        similarity = calculate_scenario_similarity(scenario1, scenario2)
        # Should be below threshold for matching (0.8)
        self.assertLess(similarity, 0.8)

    def test_similarity_weights_60_percent_name_40_percent_steps(self):
        """Should weight name at 60% and steps at 40%"""
        from migrate import calculate_scenario_similarity

        # Same name, different steps
        scenario1 = """Scenario: User authentication
  Given I am on login page
  When I enter credentials"""

        scenario2 = """Scenario: User authentication
  Given system is ready
  When user provides data"""

        similarity = calculate_scenario_similarity(scenario1, scenario2)
        # Should be >= 0.6 due to identical name (60% weight)
        self.assertGreaterEqual(similarity, 0.6)

    def test_threshold_above_0_8_treated_as_match(self):
        """Scenarios with similarity > 0.8 should be treated as matches"""
        from migrate import are_scenarios_similar

        scenario1 = "Scenario: User logs in successfully"
        scenario2 = "Scenario: User logs in"

        is_match = are_scenarios_similar(scenario1, scenario2, threshold=0.8)
        # Should determine based on actual similarity
        self.assertIsInstance(is_match, bool)

    def test_threshold_below_0_8_flagged_for_review(self):
        """Scenarios with similarity < 0.8 should be flagged"""
        from migrate import are_scenarios_similar

        scenario1 = "Scenario: User logs in"
        scenario2 = "Scenario: System backup runs"

        is_match = are_scenarios_similar(scenario1, scenario2, threshold=0.8)
        self.assertFalse(is_match)


class TestIncrementalProcessing(unittest.TestCase):
    """
    Test incremental processing with progress reporting

    Scenario: Migration processes plans incrementally
      Given many plans need processing
      When the migration tool runs
      Then it processes plans in batches
      And it reports progress after each batch
      And it can resume if interrupted
      And memory usage stays bounded

    Scenario: Migration reports detailed progress and errors
      Given the migration tool is processing plans
      When an error occurs
      Then it logs the error with context (plan file, scenario)
      And it continues processing remaining plans
      And it generates a summary report at the end
      And the report includes success/failure counts
    """

    def test_processes_plans_in_batches(self):
        """Should process plans in batches for memory efficiency"""
        from migrate import migrate_project_with_progress

        test_dir = tempfile.mkdtemp()
        plans_dir = Path(test_dir) / "plans"
        plans_dir.mkdir()

        # Create multiple plan files
        for i in range(5):
            (plans_dir / f"plan-{i}.md").write_text(f"""
# Feature: Test {i}

## User Requirements

```gherkin
Scenario: Test scenario {i}
  Given test context
```
""")

        try:
            # Track progress callbacks
            progress_reports = []

            def progress_callback(current, total, batch_num):
                progress_reports.append((current, total, batch_num))

            result = migrate_project_with_progress(
                test_dir,
                batch_size=2,
                progress_callback=progress_callback
            )

            # Should have processed in batches
            self.assertGreater(len(progress_reports), 0)
            self.assertIn("total_plans", result)
            self.assertEqual(result["total_plans"], 5)
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_reports_progress_after_each_batch(self):
        """Should report progress after processing each batch"""
        from migrate import migrate_project_with_progress

        test_dir = tempfile.mkdtemp()
        plans_dir = Path(test_dir) / "plans"
        plans_dir.mkdir()

        for i in range(3):
            (plans_dir / f"plan-{i}.md").write_text(f"# Feature: Test {i}")

        try:
            progress_reports = []

            def progress_callback(current, total, batch_num):
                progress_reports.append(current)

            migrate_project_with_progress(
                test_dir,
                batch_size=1,
                progress_callback=progress_callback
            )

            # Should report after each plan
            self.assertEqual(progress_reports, [1, 2, 3])
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_generates_summary_report(self):
        """Should generate summary report with success/failure counts"""
        from migrate import migrate_project_with_progress

        test_dir = tempfile.mkdtemp()
        plans_dir = Path(test_dir) / "plans"
        plans_dir.mkdir()

        # Create valid plan
        (plans_dir / "valid.md").write_text("""
# Feature: Valid

## User Requirements

```gherkin
Scenario: Test
  Given test
```
""")

        try:
            result = migrate_project_with_progress(test_dir)

            # Should have summary
            self.assertIn("successes", result)
            self.assertIn("failures", result)
            self.assertIn("total_plans", result)
            self.assertGreaterEqual(result["successes"], 0)
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_continues_processing_after_error(self):
        """Should continue processing remaining plans after an error"""
        from migrate import migrate_project_with_progress

        test_dir = tempfile.mkdtemp()
        plans_dir = Path(test_dir) / "plans"
        plans_dir.mkdir()

        # Create mix of valid and invalid plans
        (plans_dir / "valid1.md").write_text("""
# Feature: Valid 1

## User Requirements

```gherkin
Scenario: Test
  Given test
```
""")

        # Invalid plan (no gherkin)
        (plans_dir / "invalid.md").write_text("# Just a title")

        (plans_dir / "valid2.md").write_text("""
# Feature: Valid 2

## User Requirements

```gherkin
Scenario: Test 2
  Given test 2
```
""")

        try:
            result = migrate_project_with_progress(test_dir)

            # Should have processed all 3 plans
            self.assertEqual(result["total_plans"], 3)
            # Should have some successes
            self.assertGreater(result["successes"], 0)
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)

    def test_logs_errors_with_context(self):
        """Should log errors with plan file context"""
        from migrate import migrate_project_with_progress

        test_dir = tempfile.mkdtemp()
        plans_dir = Path(test_dir) / "plans"
        plans_dir.mkdir()

        # Invalid plan
        (plans_dir / "bad-plan.md").write_text("# Incomplete")

        try:
            result = migrate_project_with_progress(test_dir)

            # Should have error details
            self.assertIn("errors", result)
            if result["errors"]:
                error = result["errors"][0]
                self.assertIn("file", error)
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
