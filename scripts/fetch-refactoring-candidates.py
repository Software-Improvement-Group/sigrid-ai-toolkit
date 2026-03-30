#!/usr/bin/env python3
"""Fetch and aggregate Sigrid refactoring candidates across all maintainability properties.

Usage:
    python fetch-refactoring-candidates.py <customer> <system> [--count N]

Requires SIGRID_CI_TOKEN environment variable.
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

RATING_FIELDS = {
    "duplication": "Duplication",
    "unitSize": "Unit Size",
    "unitComplexity": "Unit Complexity",
    "unitInterfacing": "Unit Interfacing",
    "moduleCoupling": "Module Coupling",
    "componentIndependence": "Component Independence",
    "componentEntanglement": "Component Entanglement",
}

SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]


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


def interpret_rating(value):
    if value is None:
        return "N/A"
    if value >= 4.0:
        return "Good"
    if value >= 3.0:
        return "Adequate"
    if value >= 2.0:
        return "Below average"
    return "Needs attention"


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
    parser.add_argument("--count", type=int, default=None, help="Limit candidates per property (e.g. 10)")
    args = parser.parse_args()

    token = os.environ.get("SIGRID_CI_TOKEN")
    if not token:
        print("Error: SIGRID_CI_TOKEN environment variable is not set.", file=sys.stderr)
        print("Set it with: export SIGRID_CI_TOKEN=<your-token>", file=sys.stderr)
        sys.exit(1)

    # Fetch maintainability ratings
    maint_data = api_get(f"maintainability/{args.customer}/{args.system}", token)
    if "error" in maint_data:
        code = maint_data["error"]
        if code in (401, 403):
            print("Error: Authentication failed. Check your SIGRID_CI_TOKEN.", file=sys.stderr)
        elif code == 404:
            print(f"Error: System not found. Verify customer='{args.customer}' and system='{args.system}'.", file=sys.stderr)
        else:
            print(f"Error: HTTP {code} fetching maintainability ratings.", file=sys.stderr)
        sys.exit(1)

    # Extract latest ratings
    systems = maint_data.get("systems", [])
    if not systems:
        print("Error: No system data returned from Sigrid.", file=sys.stderr)
        sys.exit(1)

    system_data = systems[0]
    all_ratings = system_data.get("allRatings", [])
    latest = all_ratings[-1] if all_ratings else {}

    ratings = {}
    for field, label in RATING_FIELDS.items():
        value = latest.get(field)
        ratings[field] = {
            "label": label,
            "value": round(value, 2) if value is not None else None,
            "interpretation": interpret_rating(value),
        }

    # Fetch candidates for all properties in parallel
    candidates_by_prop = {}
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = {
            executor.submit(fetch_candidates, token, args.customer, args.system, prop, args.count): prop
            for prop in PROPERTIES
        }
        for future in as_completed(futures):
            prop, result = future.result()
            candidates_by_prop[prop] = result

    # Build output
    output = {
        "system": args.system,
        "customer": args.customer,
        "maintainability": round(system_data.get("maintainability", 0), 2),
        "ratings": ratings,
        "summary": build_summary(candidates_by_prop),
        "candidates": candidates_by_prop,
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
