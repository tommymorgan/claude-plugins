#!/usr/bin/env python3
"""
Tests for documentation generator

Scenarios:
- User documentation excludes technical details
- Developer documentation includes technical specs
- Doc generator filters scenarios by tag
- Doc generator converts Gherkin to readable prose
- Doc generator reads existing documentation before updating
- Doc generator identifies changed scenarios through diff
- Doc generator updates only affected sections
- Doc generator preserves non-scenario content
- Doc generator creates semantic HTML structure
- Doc generator sanitizes content to prevent injection
"""

import shutil
import tempfile
import unittest
from pathlib import Path


class TestDocumentationGeneration(unittest.TestCase):
    """Test generating documentation from living specs"""

    def setUp(self):
        """Create test .feature file and existing docs"""
        self.test_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.test_dir) / "specs"
        self.docs_dir = Path(self.test_dir) / "docs"
        self.specs_dir.mkdir()
        self.docs_dir.mkdir()

        # Create .feature file with @user and @technical scenarios
        self.feature_file = self.specs_dir / "authentication.feature"
        self.feature_file.write_text("""Feature: Authentication

  @user
  Scenario: User logs in successfully
    Given I am on the login page
    When I enter valid credentials
    Then I am redirected to dashboard

  @technical @api
  Scenario: JWT token generation
    Given user authenticates successfully
    When auth service processes request
    Then JWT token is issued with user claims
    And token expires in 24 hours
""")

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_filters_user_scenarios(self):
        """Should include only @user scenarios when generating user docs"""
        from doc_generator import generate_docs

        doc_path = self.docs_dir / "user-guide.md"
        generate_docs(self.specs_dir, doc_path, tags=["@user"])

        content = doc_path.read_text()
        self.assertIn("User logs in successfully", content)
        self.assertNotIn("JWT token generation", content)

    def test_filters_technical_scenarios(self):
        """Should include only @technical scenarios when generating dev docs"""
        from doc_generator import generate_docs

        doc_path = self.docs_dir / "technical-spec.md"
        generate_docs(self.specs_dir, doc_path, tags=["@technical"])

        content = doc_path.read_text()
        self.assertIn("JWT token generation", content)
        self.assertNotIn("User logs in successfully", content)

    def test_converts_gherkin_to_prose(self):
        """Should convert Given/When/Then to readable prose"""
        from doc_generator import scenario_to_prose

        scenario_text = """Scenario: User logs in successfully
  Given I am on the login page
  When I enter valid credentials
  Then I am redirected to dashboard"""

        prose = scenario_to_prose(scenario_text)

        # Should be readable prose, not Gherkin syntax
        self.assertNotIn("Given ", prose)
        self.assertNotIn("When ", prose)
        self.assertNotIn("Then ", prose)
        # Should contain the actual content
        self.assertIn("login page", prose.lower())
        self.assertIn("credentials", prose.lower())
        self.assertIn("dashboard", prose.lower())

    def test_reads_existing_documentation(self):
        """Should read existing docs before updating"""
        from doc_generator import generate_docs_incremental

        # Create existing doc
        existing_doc = self.docs_dir / "user-guide.md"
        existing_doc.write_text("""# User Guide

## Introduction
Welcome to our app!

## Authentication

### Logging In
You can log in using your credentials.
""")

        result = generate_docs_incremental(
            self.specs_dir,
            existing_doc,
            tags=["@user"]
        )

        # Should have detected existing content
        self.assertIn("existing_content", result)
        self.assertIn("Welcome to our app!", result["existing_content"])

    def test_preserves_non_scenario_content(self):
        """Should preserve introduction and other prose"""
        from doc_generator import generate_docs_incremental

        existing_doc = self.docs_dir / "user-guide.md"
        existing_doc.write_text("""# User Guide

## Introduction
Welcome! This guide helps you get started.

## Authentication
Old authentication content.
""")

        generate_docs_incremental(
            self.specs_dir,
            existing_doc,
            tags=["@user"]
        )

        content = existing_doc.read_text()

        # Should preserve introduction
        self.assertIn("Welcome! This guide helps you get started.", content)
        # Should update authentication section
        self.assertIn("User logs in", content)

    def test_creates_semantic_html(self):
        """Should create semantic HTML structure when outputting HTML"""
        from doc_generator import generate_docs

        doc_path = self.docs_dir / "user-guide.html"
        generate_docs(self.specs_dir, doc_path, tags=["@user"], format="html")

        content = doc_path.read_text()

        # Should have proper HTML structure
        self.assertIn("<h", content)  # Headings
        self.assertIn("</h", content)
        # Should be valid HTML
        self.assertIn("<", content)
        self.assertIn(">", content)

    def test_sanitizes_content(self):
        """Should escape HTML/script to prevent injection"""
        from doc_generator import sanitize_html

        dangerous = "<script>alert('xss')</script>"
        safe = sanitize_html(dangerous)

        # Script tags should be escaped
        self.assertNotIn("<script>", safe)
        self.assertIn("&lt;script&gt;", safe)
        # Quotes should be escaped
        self.assertIn("&#x27;", safe)


class TestCoverageAnalysis(unittest.TestCase):
    """Test coverage analysis features"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.specs_dir = Path(self.test_dir) / "specs"
        self.test_files_dir = Path(self.test_dir) / "tests"
        self.specs_dir.mkdir()
        self.test_files_dir.mkdir()

        # Create .feature file
        (self.specs_dir / "auth.feature").write_text("""Feature: Authentication

  @user
  Scenario: User logs in successfully
    Given I am on login page

  @user
  Scenario: User resets password
    Given I forgot password
""")

        # Create test file
        (self.test_files_dir / "test_auth.py").write_text("""
def test_user_login_success():
    '''Test that user logs in successfully'''
    pass
""")

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_finds_test_files(self):
        """Should discover test files in project"""
        from doc_generator import find_test_files

        test_files = find_test_files(Path(self.test_dir))

        # Should find at least the test file we created
        self.assertGreaterEqual(len(test_files), 1)
        self.assertTrue(any("test_auth.py" in str(f) for f in test_files))

    def test_matches_tests_to_scenarios(self):
        """Should match test names to scenario names"""
        from doc_generator import analyze_coverage

        coverage = analyze_coverage(self.specs_dir, Path(self.test_dir))

        # Should have coverage data
        self.assertIn("scenarios", coverage)
        self.assertGreater(len(coverage["scenarios"]), 0)

        # Should show which scenarios have tests
        scenarios = coverage["scenarios"]
        login_scenario = next(
            (s for s in scenarios if "logs in" in s["name"].lower()),
            None
        )
        self.assertIsNotNone(login_scenario)

    def test_reports_coverage_percentage(self):
        """Should calculate overall coverage percentage"""
        from doc_generator import analyze_coverage

        coverage = analyze_coverage(self.specs_dir, Path(self.test_dir))

        self.assertIn("percentage", coverage)
        self.assertGreaterEqual(coverage["percentage"], 0.0)
        self.assertLessEqual(coverage["percentage"], 100.0)


if __name__ == "__main__":
    unittest.main()
