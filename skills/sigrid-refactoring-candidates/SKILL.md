---
description: List refactoring candidates across all maintainability properties for a Sigrid system
---

# Sigrid Refactoring Candidates

You are helping the user retrieve and review refactoring candidates from Sigrid for a given system. A Python script handles all API calls, report generation, and formatting. Your job is to gather the inputs, run the script, and present the results.

## IMPORTANT: Do NOT use curl, wget, or any direct HTTP calls. ALL data fetching is done by the Python script.

## Token security rules (MANDATORY)

1. NEVER print, echo, or log the SIGRID_TOKEN value
2. NEVER include the token in text output to the user

## Workflow

### Step 1: Get customer and system names

Ask the user for their **customer** (Sigrid account name) and **system** name. These are required for all API calls.

### Step 2: Confirm result scope with the user (MANDATORY)

Before fetching any data, you MUST ask the user the following question and wait for their answer:

> Would you like to see **all refactoring candidates** or limit the results to the **top N candidates per property**?
>
> - **All candidates** — returns every finding across all properties. This can be a large dataset for systems with many findings.
> - **Top N per property** — returns only the N most severe candidates per maintainability property. Recommended for a focused, actionable overview (e.g. 10).

**Do NOT proceed until the user has explicitly chosen one of these options.** This is a hard requirement. The script will reject the command if neither `--all` nor `--count` is provided.

### Step 3: Run the fetch script

This is the ONLY way to fetch data. Do NOT use curl, wget, or any other HTTP tool.

If the user chose **all candidates**:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fetch-refactoring-candidates.py" {customer} {system} --all --output FULL_ANALYSIS_RESULTS.md
```

If the user chose **top N**:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fetch-refactoring-candidates.py" {customer} {system} --count {N} --output FULL_ANALYSIS_RESULTS.md
```

The script:
- Fetches candidates for all 7 maintainability properties in parallel
- Writes the complete analysis (summary table, per-property listings, prioritized actions) to `FULL_ANALYSIS_RESULTS.md`
- Prints only the prioritized action list to stdout

If the script exits with an error, relay the stderr message to the user and stop.

## Output

Show the user **only** the prioritized action list printed by the script to stdout. Then tell the user the full analysis has been written to `FULL_ANALYSIS_RESULTS.md`.

Do NOT reformat, summarize, or editorialize the script output. Show it verbatim.

## Error handling

- **Script exits with error**: relay the error message to the user. Common causes:
  - Missing `--all` or `--count`: the script requires one of these flags.
  - `SIGRID_TOKEN` not set: tell the user to set it via `export SIGRID_TOKEN=...`. They can obtain a token from https://sigrid-says.com account settings.
  - 401/403: Token expired or lacks permissions. NEVER show the token.
  - 404: Customer or system name may be incorrect.
- **No candidates**: the script reports this as a positive result.
