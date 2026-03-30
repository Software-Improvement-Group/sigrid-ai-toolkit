---
description: List refactoring candidates across all maintainability properties for a Sigrid system
---

# Sigrid Refactoring Candidates

You are helping the user retrieve and review refactoring candidates from Sigrid for a given system. A Python script handles all API calls and aggregation. Your job is to gather the inputs, run the script, and present the results.

## Token security rules (MANDATORY)

1. NEVER print, echo, or log the token value
2. NEVER include the token in text output to the user
3. Validate token existence without exposing its value

## Workflow

### Step 0: Verify token availability (MUST run first)

Run this command EXACTLY:

```bash
if [ -n "$SIGRID_CI_TOKEN" ]; then
  echo "SIGRID_CI_TOKEN is set"
else
  echo "SIGRID_CI_TOKEN is NOT set"
fi
```

- If NOT set: stop and tell the user to set it via their terminal (`export SIGRID_CI_TOKEN=...`). Remind them to never paste the token in the chat. They can obtain a token from their Sigrid account settings at https://sigrid-says.com.
- If set: proceed to Step 1.

### Step 1: Get customer and system names

Ask the user for their **customer** (Sigrid account name) and **system** name. These are required for all API calls.

### Step 2: Confirm result scope with the user (MANDATORY)

Before fetching any data, you MUST ask the user the following question and wait for their answer:

> Would you like to see **all refactoring candidates** or limit the results to the **top 10 candidates per property**?
>
> - **All candidates** - returns every finding across all properties. This can be a large dataset for systems with many findings.
> - **Top 10 per property** - returns only the 10 most severe candidates per maintainability property. Recommended for a focused, actionable overview.

**Do NOT proceed until the user has explicitly chosen one of these options.** This is a hard requirement.

### Step 3: Run the fetch script

Run the Python script with the values collected in Steps 1 and 2:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fetch-refactoring-candidates.py" {customer} {system}
```

If the user chose top-10, add `--count 10`:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fetch-refactoring-candidates.py" {customer} {system} --count 10
```

The script outputs a single JSON object with all data. If it exits with an error, relay the stderr message to the user and stop.

### Script output structure

The JSON output contains:

- `maintainability` — overall score (0–5.5)
- `ratings` — per-property object with `value`, `label`, and `interpretation`
- `summary` — per-property candidate counts by severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `total`)
- `candidates` — per-property arrays of refactoring candidate objects

Candidate fields vary by property:

**Common fields:** `severity`, `filePath`, `startLine`, `endLine`, `technology`, `componentName`

**Duplication:** `loc`, `sameFile`, `sameComponent`, `locations` (array of `{filePath, startLine, endLine}`)

**Unit-level (unitSize, unitComplexity, unitInterfacing):** `unitName`, `mcCabe`, `parameters`

**Component Entanglement:** `componentEntanglementType` (`CYCLIC_DEPENDENCY`, `INDIRECT_CYCLIC_DEPENDENCY`, `LAYER_BYPASSING_DEPENDENCY`, `COMMUNICATION_DENSITY`)

## Presentation

### 1. Quality overview

Start with a summary table using the `ratings` object:

```
## Maintainability Overview for {system}

Overall rating: {maintainability} / 5.0

| Property                 | Rating | Interpretation     |
| ------------------------ | ------ | ------------------ |
| Duplication              | {x.x}  | {interpretation}   |
| Unit Size                | {x.x}  | {interpretation}   |
| Unit Complexity          | {x.x}  | {interpretation}   |
| Unit Interfacing         | {x.x}  | {interpretation}   |
| Module Coupling          | {x.x}  | {interpretation}   |
| Component Independence   | {x.x}  | {interpretation}   |
| Component Entanglement   | {x.x}  | {interpretation}   |
```

### 2. Candidate summary

Render the `summary` object as a table:

```
## Refactoring Candidates Summary

| Property                 | Critical | High | Medium | Low | Total |
| ...                      | ...      | ...  | ...    | ... | ...   |
```

### 3. Per-property candidate listings

For each property with candidates, list them sorted by severity (CRITICAL first). For each candidate:

**Duplication:**
- `[{severity}] Duplication in {filePath}` — lines {startLine}–{endLine}, {loc} duplicated lines, duplicated with {locations}, same file: {yes/no}

**Unit Size:**
- `[{severity}] {unitName} in {filePath}` — lines {startLine}–{endLine}

**Unit Complexity:**
- `[{severity}] {unitName} in {filePath}` — lines {startLine}–{endLine}, McCabe complexity: {mcCabe}

**Unit Interfacing:**
- `[{severity}] {unitName} in {filePath}` — lines {startLine}–{endLine}, parameters: {parameters}

**Module Coupling:**
- `[{severity}] {filePath}` — lines {startLine}–{endLine}, component: {componentName}

**Component Independence:**
- `[{severity}] {componentName}` — {filePath}, lines {startLine}–{endLine}

**Component Entanglement:**
- `[{severity}] {componentName} — {componentEntanglementType}` — {filePath}, lines {startLine}–{endLine}

### 4. Prioritized action items

End with a short list of top recommended actions, prioritized by:
1. Severity (CRITICAL > HIGH > MEDIUM > LOW)
2. Properties with the lowest ratings
3. Quick wins — candidates that are likely easy to fix

## Error handling

- **Script exits with error**: relay the error message to the user. Common causes:
  - 401/403: Token expired or lacks permissions. NEVER show the token.
  - 404: Customer or system name may be incorrect.
- **No candidates for a property**: report it as a positive result.
- **No candidates at all**: congratulate the user.
