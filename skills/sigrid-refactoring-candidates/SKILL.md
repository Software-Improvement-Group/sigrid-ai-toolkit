---
description: List refactoring candidates across all maintainability properties for a Sigrid system
---

# Sigrid Refactoring Candidates

A Python script fetches refactoring candidates from the Sigrid API. Your job is to gather the inputs, run the script, and present the JSON results.

## Workflow

### Step 1: Get customer and system names

Ask the user for their **customer** (Sigrid account name) and **system** name.

### Step 2: Confirm result scope with the user (MANDATORY)

Ask the user: **all candidates** or **top N per property**? Do NOT proceed until they answer. The script enforces this — it rejects the command if neither `--all` nor `--count` is provided.

### Step 3: Run the fetch script

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fetch-refactoring-candidates.py" {customer} {system} {--all | --count N}
```

The script outputs JSON to stdout with `summary` (severity counts per property) and `candidates` (per-property arrays). If it exits with an error, relay the stderr message to the user and stop.

## Output

Present the JSON results to the user. Summarize the key findings and highlight the highest-severity candidates that should be addressed first.
