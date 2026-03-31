#!/usr/bin/env python3
"""Fetch and aggregate Sigrid refactoring candidates across all maintainability properties.

Usage:
    python fetch-refactoring-candidates.py <customer> <system> --all
    python fetch-refactoring-candidates.py <customer> <system> --count N

Requires SIGRID_TOKEN environment variable.
Outputs JSON with summary and candidates to stdout.
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError
from urllib.request import Request, urlopen

API_BASE = "https://sigrid-says.com/rest/analysis-results/api/v1"

PROPERTIES = [
    "duplication",
    "unitSize",
    "unitComplexity",
    "unitInterfacing",
    "moduleCoupling",
    "componentIndependence",
    "componentEntanglement",
]

SEVERITIES = ["VERY_HIGH", "HIGH", "MEDIUM", "LOW"]


def api_get(path, token):
    """Make an authenticated GET request to the Sigrid API."""
    req = Request(f"{API_BASE}/{path}")
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        body = ""
        try:
            body = e.read().decode()
        except Exception:
            pass
        return {"error": e.code, "message": body, "path": path}


def fetch_candidates(token, customer, system, prop, count):
    """Fetch refactoring candidates for a single property."""
    path = f"refactoring-candidates/{customer}/{system}/{prop}"
    if count:
        path += f"?count={count}"
    data = api_get(path, token)
    if "error" in data:
        return prop, data
    return prop, data.get("refactoringCandidates", [])


def build_summary(candidates_by_prop):
    """Build a severity count summary per property."""
    summary = {}
    for prop in PROPERTIES:
        candidates = candidates_by_prop.get(prop, [])
        if isinstance(candidates, dict) and "error" in candidates:
            summary[prop] = {"error": candidates["error"], "message": candidates.get("message", "")}
            continue
        counts = {s: 0 for s in SEVERITIES}
        for c in candidates:
            sev = c.get("severity", "LOW")
            if sev in counts:
                counts[sev] += 1
        summary[prop] = {"total": len(candidates), **counts}
    return summary


def main():
    parser = argparse.ArgumentParser(description="Fetch Sigrid refactoring candidates")
    parser.add_argument("customer", help="Sigrid account name")
    parser.add_argument("system", help="System name in Sigrid")

    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--all", action="store_true", help="Fetch all candidates")
    scope.add_argument("--count", type=int, help="Limit candidates per property (e.g. 10)")

    args = parser.parse_args()

    token = os.environ.get("SIGRID_TOKEN")
    if not token:
        print("Error: SIGRID_TOKEN environment variable is not set.", file=sys.stderr)
        print("Set it with: export SIGRID_TOKEN=<your-token>", file=sys.stderr)
        print("Obtain a token from your Sigrid account settings at https://sigrid-says.com", file=sys.stderr)
        sys.exit(1)

    count = args.count if args.count else None

    candidates_by_prop = {}
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = {
            executor.submit(fetch_candidates, token, args.customer, args.system, prop, count): prop
            for prop in PROPERTIES
        }
        for future in as_completed(futures):
            prop, result = future.result()
            candidates_by_prop[prop] = result

    output = {
        "system": args.system,
        "customer": args.customer,
        "summary": build_summary(candidates_by_prop),
        "candidates": candidates_by_prop,
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
