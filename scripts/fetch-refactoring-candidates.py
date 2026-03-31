#!/usr/bin/env python3
"""Fetch Sigrid refactoring candidates and generate a prioritized markdown report.

Usage:
    python fetch-refactoring-candidates.py <customer> <system> --all [--output FILE]
    python fetch-refactoring-candidates.py <customer> <system> --count N [--output FILE]

Requires SIGRID_TOKEN environment variable.
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timezone, datetime
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

PROPERTY_NAMES = {
    "duplication": "Duplication",
    "unitSize": "Unit Size",
    "unitComplexity": "Unit Complexity",
    "unitInterfacing": "Unit Interfacing",
    "moduleCoupling": "Module Coupling",
    "componentIndependence": "Component Independence",
    "componentEntanglement": "Component Entanglement",
}

SEVERITIES = ["VERY_HIGH", "HIGH", "MEDIUM", "LOW"]
SEVERITY_ORDER = {s: i for i, s in enumerate(SEVERITIES)}


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


# ── Markdown formatting ──────────────────────────────────────────────────


def format_candidate(prop, c):
    """Format a single candidate as a markdown line."""
    sev = c.get("severity", "LOW")
    fp = c.get("filePath", "unknown")
    start = c.get("startLine", "?")
    end = c.get("endLine", "?")

    if prop == "duplication":
        loc = c.get("loc", "?")
        locations = c.get("locations", [])
        loc_strs = [f"`{l['filePath']}` (lines {l['startLine']}\u2013{l['endLine']})" for l in locations]
        same_file = "yes" if c.get("sameFile") else "no"
        dup_with = ", ".join(loc_strs) if loc_strs else "unknown"
        return f"[{sev}] Duplication in `{fp}` \u2014 lines {start}\u2013{end}, {loc} duplicated lines, duplicated with {dup_with}, same file: {same_file}"

    if prop == "unitSize":
        unit = c.get("unitName", "unknown")
        return f"[{sev}] `{unit}` in `{fp}` \u2014 lines {start}\u2013{end}"

    if prop == "unitComplexity":
        unit = c.get("unitName", "unknown")
        mccabe = c.get("mcCabe", "?")
        return f"[{sev}] `{unit}` in `{fp}` \u2014 lines {start}\u2013{end}, McCabe complexity: {mccabe}"

    if prop == "unitInterfacing":
        unit = c.get("unitName", "unknown")
        params = c.get("parameters", "?")
        return f"[{sev}] `{unit}` in `{fp}` \u2014 lines {start}\u2013{end}, parameters: {params}"

    if prop == "moduleCoupling":
        comp = c.get("componentName", "unknown")
        return f"[{sev}] `{fp}` \u2014 lines {start}\u2013{end}, component: {comp}"

    if prop == "componentIndependence":
        comp = c.get("componentName", "unknown")
        return f"[{sev}] {comp} \u2014 `{fp}`, lines {start}\u2013{end}"

    if prop == "componentEntanglement":
        comp = c.get("componentName", "unknown")
        etype = c.get("componentEntanglementType", "unknown")
        return f"[{sev}] {comp} \u2014 {etype} \u2014 `{fp}`, lines {start}\u2013{end}"

    return f"[{sev}] `{fp}` \u2014 lines {start}\u2013{end}"


def generate_summary_table(summary):
    """Generate the severity-count summary table."""
    lines = [
        "| Property | Very High | High | Medium | Low | Total |",
        "|---|---|---|---|---|---|",
    ]
    for prop in PROPERTIES:
        name = PROPERTY_NAMES[prop]
        s = summary.get(prop, {})
        if "error" in s:
            lines.append(f"| {name} | Error: {s['error']} | | | | |")
        else:
            vh = s.get("VERY_HIGH", 0)
            h = s.get("HIGH", 0)
            m = s.get("MEDIUM", 0)
            lo = s.get("LOW", 0)
            total = s.get("total", 0)
            lines.append(f"| {name} | {vh} | {h} | {m} | {lo} | {total} |")
    return "\n".join(lines)


def generate_property_listings(candidates_by_prop):
    """Generate per-property candidate listings sorted by severity."""
    sections = []
    for prop in PROPERTIES:
        candidates = candidates_by_prop.get(prop, [])
        name = PROPERTY_NAMES[prop]

        if isinstance(candidates, dict) and "error" in candidates:
            sections.append(f"### {name}\n\nError fetching data: {candidates['error']} \u2014 {candidates.get('message', '')}")
            continue

        if not candidates:
            sections.append(f"### {name}\n\nNo candidates found.")
            continue

        sorted_candidates = sorted(candidates, key=lambda c: SEVERITY_ORDER.get(c.get("severity", "LOW"), 3))
        lines = [f"### {name}\n"]
        for c in sorted_candidates:
            lines.append(f"- {format_candidate(prop, c)}")
        sections.append("\n".join(lines))

    return "\n\n".join(sections)


def generate_priorities(candidates_by_prop):
    """Generate a flat prioritized action list sorted by severity, property density, and effort."""
    all_candidates = []
    prop_counts = {}

    for prop in PROPERTIES:
        candidates = candidates_by_prop.get(prop, [])
        if isinstance(candidates, dict) and "error" in candidates:
            continue
        prop_counts[prop] = len(candidates)
        for c in candidates:
            all_candidates.append((prop, c))

    if not all_candidates:
        return "No refactoring candidates found \u2014 the system is in good shape."

    def sort_key(item):
        prop, c = item
        sev = SEVERITY_ORDER.get(c.get("severity", "LOW"), 3)
        count = -(prop_counts.get(prop, 0))  # negative for descending
        start = c.get("startLine", 0) or 0
        end = c.get("endLine", 0) or 0
        span = end - start if isinstance(end, int) and isinstance(start, int) else 999999
        return (sev, count, span)

    all_candidates.sort(key=sort_key)

    lines = []
    for i, (prop, c) in enumerate(all_candidates, 1):
        lines.append(f"{i}. **{PROPERTY_NAMES[prop]}**: {format_candidate(prop, c)}")
    return "\n".join(lines)


def generate_markdown(customer, system, summary, candidates_by_prop):
    """Generate the full analysis markdown document."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return "\n".join([
        f"# Sigrid Refactoring Candidates \u2014 Full Analysis",
        f"",
        f"**System:** {system} | **Customer:** {customer} | **Date:** {today}",
        f"",
        f"## Summary",
        f"",
        generate_summary_table(summary),
        f"",
        f"## Candidates by Property",
        f"",
        generate_property_listings(candidates_by_prop),
        f"",
        f"## Prioritized Actions",
        f"",
        generate_priorities(candidates_by_prop),
        f"",
    ])


# ── Main ─────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Fetch Sigrid refactoring candidates")
    parser.add_argument("customer", help="Sigrid account name")
    parser.add_argument("system", help="System name in Sigrid")

    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--all", action="store_true", help="Fetch all candidates")
    scope.add_argument("--count", type=int, help="Limit candidates per property (e.g. 10)")

    parser.add_argument("--output", metavar="FILE", help="Write full analysis markdown to FILE")
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

    summary = build_summary(candidates_by_prop)
    markdown = generate_markdown(args.customer, args.system, summary, candidates_by_prop)

    if args.output:
        with open(args.output, "w") as f:
            f.write(markdown)
        print(f"Full analysis written to {args.output}", file=sys.stderr)

    # Only the prioritized action list goes to stdout
    print(generate_priorities(candidates_by_prop))


if __name__ == "__main__":
    main()
