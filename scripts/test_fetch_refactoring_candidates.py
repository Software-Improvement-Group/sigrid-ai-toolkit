#!/usr/bin/env python3
"""Tests for fetch-refactoring-candidates.py."""

import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import importlib
fetch = importlib.import_module("fetch-refactoring-candidates")


# ── Test fixtures ─────────────────────────────────────────────────────────


def make_candidate(severity="HIGH", filePath="src/main.py", startLine=10, endLine=50, **extra):
    return {"severity": severity, "filePath": filePath, "startLine": startLine, "endLine": endLine, **extra}


SAMPLE_CANDIDATES = {
    "duplication": [
        make_candidate(severity="VERY_HIGH", filePath="src/a.py", startLine=1, endLine=20, loc=20),
    ],
    "unitSize": [
        make_candidate(severity="HIGH", unitName="processData"),
        make_candidate(severity="MEDIUM", unitName="helper"),
    ],
    "unitComplexity": [
        make_candidate(severity="VERY_HIGH", unitName="parseInput", mcCabe=25),
    ],
    "unitInterfacing": [
        make_candidate(severity="LOW", unitName="configure", parameters=8),
    ],
    "moduleCoupling": [],
    "componentIndependence": [
        make_candidate(severity="HIGH", componentName="auth"),
    ],
    "componentEntanglement": [
        make_candidate(severity="MEDIUM", componentName="billing", componentEntanglementType="CYCLIC_DEPENDENCY"),
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

    def test_all_severities_present(self):
        summary = fetch.build_summary(EMPTY_CANDIDATES)
        for prop in fetch.PROPERTIES:
            for sev in fetch.SEVERITIES:
                self.assertIn(sev, summary[prop])


class TestCLIArguments(unittest.TestCase):

    SCRIPT = os.path.join(os.path.dirname(__file__), "fetch-refactoring-candidates.py")

    def run_script(self, args):
        env = {**os.environ, "SIGRID_TOKEN": "fake-token-for-testing"}
        return subprocess.run(
            [sys.executable, self.SCRIPT] + args,
            capture_output=True, text=True, env=env, timeout=10,
        )

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

    def test_missing_token_shows_sigrid_url(self):
        env = {k: v for k, v in os.environ.items() if k != "SIGRID_TOKEN"}
        result = subprocess.run(
            [sys.executable, self.SCRIPT, "acme", "portal", "--all"],
            capture_output=True, text=True, env=env, timeout=10,
        )
        self.assertIn("sigrid-says.com", result.stderr)


if __name__ == "__main__":
    unittest.main()
