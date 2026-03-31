---
description: List refactoring candidates across all maintainability properties for a Sigrid system
---

# Sigrid Refactoring Candidates

A Python script handles all API calls, report generation, and formatting. Your job is to gather the inputs, run the script, and present the results.

## Workflow

### Step 1: Get customer and system names

Ask the user for their **customer** (Sigrid account name) and **system** name.

### Step 2: Confirm result scope with the user (MANDATORY)

Ask the user: **all candidates** or **top N per property**? Do NOT proceed until they answer. The script enforces this — it rejects the command if neither `--all` nor `--count` is provided.

### Step 3: Run the fetch script

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fetch-refactoring-candidates.py" {customer} {system} {--all | --count N} --output FULL_ANALYSIS_RESULTS.md
```

The script writes the complete analysis to `FULL_ANALYSIS_RESULTS.md` and prints only the prioritized action list to stdout.

If the script exits with an error, relay the stderr message to the user and stop.

## Output

Show the user **only** the prioritized action list from stdout, then tell them the full analysis is in `FULL_ANALYSIS_RESULTS.md`. Do NOT reformat or editorialize the script output.
