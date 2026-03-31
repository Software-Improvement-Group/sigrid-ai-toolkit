#!/usr/bin/env python3
"""Tests for fetch-refactoring-candidates.py markdown generation and CLI behavior."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

# Import the module under test
sys.path.insert(0, os.path.dirname(__file__))
import importlib
fetch = importlib.import_module("fetch-refactoring-candidates")


# ── Test fixtures ─────────────────────────────────────────────────────────


def make_candidate(severity="HIGH", filePath="src/main.py", startLine=10, endLine=50, **extra):
    return {"severity": severity, "filePath": filePath, "startLine": startLine, "endLine": endLine, **extra}


SAMPLE_CANDIDATES = {
    "duplication": [
        make_candidate(
            severity="VERY_HIGH", filePath="src/a.py", startLine=1, endLine=20,
            loc=20, sameFile=True, sameComponent=True,
            locations=[{"filePath": "src/a.py", "startLine": 30, "endLine": 50}],
        ),
    ],
    "unitSize": [
        make_candidate(severity="HIGH", unitName="processData", filePath="src/b.py", startLine=5, endLine=100),
        make_candidate(severity="MEDIUM", unitName="helper", filePath="src/b.py", startLine=110, endLine=130),
    ],
    "unitComplexity": [
        make_candidate(severity="VERY_HIGH", unitName="parseInput", filePath="src/c.py", startLine=1, endLine=80, mcCabe=25),
    ],
    "unitInterfacing": [
        make_candidate(severity="LOW", unitName="configure", filePath="src/d.py", startLine=1, endLine=10, parameters=8),
    ],
    "moduleCoupling": [],
    "componentIndependence": [
        make_candidate(severity="HIGH", componentName="auth", filePath="src/auth/init.py", startLine=1, endLine=200),
    ],
    "componentEntanglement": [
        make_candidate(
            severity="MEDIUM", componentName="billing",
            filePath="src/billing/core.py", startLine=1, endLine=50,
            componentEntanglementType="CYCLIC_DEPENDENCY",
        ),
    ],
}

EMPTY_CANDIDATES = {prop: [] for prop in fetch.PROPERTIES}

ERROR_CANDIDATES = {
    "duplication": {"error": 403, "message": "Forbidden"},
    "unitSize": [],
    "unitComplexity": [],
    "unitInterfacing": [],
    "moduleCoupling": [],
    "componentIndependence": [],
    "componentEntanglement": [],
}


# ── Tests ─────────────────────────────────────────────────────────────────


class TestBuildSummary(unittest.TestCase):

    def test_counts_by_severity(self):
        summary = fetch.build_summary(SAMPLE_CANDIDATES)
        self.assertEqual(summary["duplication"]["VERY_HIGH"], 1)
        self.assertEqual(summary["duplication"]["total"], 1)
        self.assertEqual(summary["unitSize"]["HIGH"], 1)
        self.assertEqual(summary["unitSize"]["MEDIUM"], 1)
        self.assertEqual(summary["unitSize"]["total"], 2)

    def test_empty_property(self):
        summary = fetch.build_summary(SAMPLE_CANDIDATES)
        self.assertEqual(summary["moduleCoupling"]["total"], 0)
        self.assertEqual(summary["moduleCoupling"]["VERY_HIGH"], 0)

    def test_error_property(self):
        summary = fetch.build_summary(ERROR_CANDIDATES)
        self.assertIn("error", summary["duplication"])
        self.assertEqual(summary["duplication"]["error"], 403)

    def test_all_empty(self):
        summary = fetch.build_summary(EMPTY_CANDIDATES)
        for prop in fetch.PROPERTIES:
            self.assertEqual(summary[prop]["total"], 0)


class TestFormatCandidate(unittest.TestCase):

    def test_duplication(self):
        c = SAMPLE_CANDIDATES["duplication"][0]
        result = fetch.format_candidate("duplication", c)
        self.assertIn("[VERY_HIGH]", result)
        self.assertIn("src/a.py", result)
        self.assertIn("20 duplicated lines", result)
        self.assertIn("same file: yes", result)

    def test_duplication_not_same_file(self):
        c = {**SAMPLE_CANDIDATES["duplication"][0], "sameFile": False}
        result = fetch.format_candidate("duplication", c)
        self.assertIn("same file: no", result)

    def test_unit_size(self):
        c = SAMPLE_CANDIDATES["unitSize"][0]
        result = fetch.format_candidate("unitSize", c)
        self.assertIn("[HIGH]", result)
        self.assertIn("processData", result)
        self.assertIn("src/b.py", result)

    def test_unit_complexity(self):
        c = SAMPLE_CANDIDATES["unitComplexity"][0]
        result = fetch.format_candidate("unitComplexity", c)
        self.assertIn("McCabe complexity: 25", result)

    def test_unit_interfacing(self):
        c = SAMPLE_CANDIDATES["unitInterfacing"][0]
        result = fetch.format_candidate("unitInterfacing", c)
        self.assertIn("parameters: 8", result)

    def test_module_coupling(self):
        c = make_candidate(componentName="core")
        result = fetch.format_candidate("moduleCoupling", c)
        self.assertIn("component: core", result)

    def test_component_independence(self):
        c = SAMPLE_CANDIDATES["componentIndependence"][0]
        result = fetch.format_candidate("componentIndependence", c)
        self.assertIn("auth", result)

    def test_component_entanglement(self):
        c = SAMPLE_CANDIDATES["componentEntanglement"][0]
        result = fetch.format_candidate("componentEntanglement", c)
        self.assertIn("billing", result)
        self.assertIn("CYCLIC_DEPENDENCY", result)

    def test_unknown_property_fallback(self):
        c = make_candidate()
        result = fetch.format_candidate("unknownProp", c)
        self.assertIn("[HIGH]", result)
        self.assertIn("src/main.py", result)


class TestGenerateSummaryTable(unittest.TestCase):

    def test_table_has_header(self):
        summary = fetch.build_summary(SAMPLE_CANDIDATES)
        table = fetch.generate_summary_table(summary)
        self.assertIn("| Property |", table)
        self.assertIn("Very High", table)

    def test_table_has_all_properties(self):
        summary = fetch.build_summary(SAMPLE_CANDIDATES)
        table = fetch.generate_summary_table(summary)
        for prop in fetch.PROPERTIES:
            self.assertIn(fetch.PROPERTY_NAMES[prop], table)

    def test_table_shows_error(self):
        summary = fetch.build_summary(ERROR_CANDIDATES)
        table = fetch.generate_summary_table(summary)
        self.assertIn("Error: 403", table)


class TestGeneratePropertyListings(unittest.TestCase):

    def test_lists_all_properties(self):
        listings = fetch.generate_property_listings(SAMPLE_CANDIDATES)
        for prop in fetch.PROPERTIES:
            self.assertIn(f"### {fetch.PROPERTY_NAMES[prop]}", listings)

    def test_empty_property_says_no_candidates(self):
        listings = fetch.generate_property_listings(SAMPLE_CANDIDATES)
        # moduleCoupling is empty
        self.assertIn("### Module Coupling\n\nNo candidates found.", listings)

    def test_error_property_shows_error(self):
        listings = fetch.generate_property_listings(ERROR_CANDIDATES)
        self.assertIn("Error fetching data: 403", listings)

    def test_candidates_sorted_by_severity(self):
        listings = fetch.generate_property_listings(SAMPLE_CANDIDATES)
        # unitSize has HIGH before MEDIUM
        high_pos = listings.index("[HIGH]")
        medium_pos = listings.index("[MEDIUM]")
        self.assertLess(high_pos, medium_pos)


class TestGeneratePriorities(unittest.TestCase):

    def test_empty_candidates(self):
        result = fetch.generate_priorities(EMPTY_CANDIDATES)
        self.assertIn("No refactoring candidates", result)

    def test_very_high_comes_first(self):
        result = fetch.generate_priorities(SAMPLE_CANDIDATES)
        lines = result.strip().split("\n")
        self.assertIn("VERY_HIGH", lines[0])

    def test_low_comes_last(self):
        result = fetch.generate_priorities(SAMPLE_CANDIDATES)
        lines = result.strip().split("\n")
        self.assertIn("LOW", lines[-1])

    def test_all_candidates_present(self):
        result = fetch.generate_priorities(SAMPLE_CANDIDATES)
        # Total candidates: 1 + 2 + 1 + 1 + 0 + 1 + 1 = 7
        lines = [l for l in result.strip().split("\n") if l.strip()]
        self.assertEqual(len(lines), 7)

    def test_numbered_sequentially(self):
        result = fetch.generate_priorities(SAMPLE_CANDIDATES)
        lines = [l for l in result.strip().split("\n") if l.strip()]
        for i, line in enumerate(lines, 1):
            self.assertTrue(line.startswith(f"{i}. "), f"Line {i} doesn't start with '{i}. ': {line}")

    def test_skips_error_properties(self):
        result = fetch.generate_priorities(ERROR_CANDIDATES)
        self.assertIn("No refactoring candidates", result)

    def test_same_severity_sorted_by_property_count(self):
        """Within same severity, properties with more candidates should come first."""
        candidates = {
            "duplication": [],
            "unitSize": [
                make_candidate(severity="HIGH", unitName="a"),
                make_candidate(severity="HIGH", unitName="b"),
            ],
            "unitComplexity": [
                make_candidate(severity="HIGH", unitName="c", mcCabe=10),
            ],
            "unitInterfacing": [],
            "moduleCoupling": [],
            "componentIndependence": [],
            "componentEntanglement": [],
        }
        result = fetch.generate_priorities(candidates)
        lines = result.strip().split("\n")
        # unitSize has 2 candidates, unitComplexity has 1 — unitSize should come first
        self.assertIn("Unit Size", lines[0])
        self.assertIn("Unit Size", lines[1])
        self.assertIn("Unit Complexity", lines[2])


class TestGenerateMarkdown(unittest.TestCase):

    def test_contains_all_sections(self):
        summary = fetch.build_summary(SAMPLE_CANDIDATES)
        md = fetch.generate_markdown("acme", "portal", summary, SAMPLE_CANDIDATES)
        self.assertIn("# Sigrid Refactoring Candidates", md)
        self.assertIn("**System:** portal", md)
        self.assertIn("**Customer:** acme", md)
        self.assertIn("## Summary", md)
        self.assertIn("## Candidates by Property", md)
        self.assertIn("## Prioritized Actions", md)

    def test_contains_date(self):
        summary = fetch.build_summary(SAMPLE_CANDIDATES)
        md = fetch.generate_markdown("acme", "portal", summary, SAMPLE_CANDIDATES)
        # Should contain a date in YYYY-MM-DD format
        import re
        self.assertRegex(md, r"\d{4}-\d{2}-\d{2}")


class TestCLIArguments(unittest.TestCase):
    """Test CLI argument validation by running the script as a subprocess."""

    SCRIPT = os.path.join(os.path.dirname(__file__), "fetch-refactoring-candidates.py")

    def run_script(self, args):
        env = {**os.environ, "SIGRID_TOKEN": "fake-token-for-testing"}
        result = subprocess.run(
            [sys.executable, self.SCRIPT] + args,
            capture_output=True, text=True, env=env, timeout=10,
        )
        return result

    def test_missing_all_or_count_fails(self):
        result = self.run_script(["acme", "portal"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--all", result.stderr)

    def test_both_all_and_count_fails(self):
        result = self.run_script(["acme", "portal", "--all", "--count", "10"])
        self.assertNotEqual(result.returncode, 0)

    def test_missing_customer_fails(self):
        result = self.run_script(["--all"])
        self.assertNotEqual(result.returncode, 0)

    def test_missing_token_fails(self):
        env = {k: v for k, v in os.environ.items() if k != "SIGRID_TOKEN"}
        result = subprocess.run(
            [sys.executable, self.SCRIPT, "acme", "portal", "--all"],
            capture_output=True, text=True, env=env, timeout=10,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SIGRID_TOKEN", result.stderr)


class TestOutputFile(unittest.TestCase):
    """Test that --output writes the markdown file correctly."""

    def test_output_writes_file(self):
        # We can't call main() easily due to API calls, but we can test generate_markdown + file write
        summary = fetch.build_summary(SAMPLE_CANDIDATES)
        md = fetch.generate_markdown("acme", "portal", summary, SAMPLE_CANDIDATES)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(md)
            path = f.name

        try:
            with open(path) as f:
                content = f.read()
            self.assertIn("# Sigrid Refactoring Candidates", content)
            self.assertIn("## Prioritized Actions", content)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
