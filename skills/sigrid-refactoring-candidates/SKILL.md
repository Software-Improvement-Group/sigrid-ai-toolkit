---
description: List refactoring candidates across all maintainability properties for a Sigrid system
---

# Sigrid Refactoring Candidates

You are helping the user retrieve and review refactoring candidates from Sigrid for a given system. You will fetch candidates across all maintainability properties and present them in an organized, severity-prioritized format.

## Token security rules (MANDATORY)

1. NEVER print, echo, or log the token value
2. NEVER include the token in text output to the user
3. Only use the token in the `Authorization` header for requests to `sigrid-says.com`
4. Use `--fail-with-body` on all curl calls to prevent request headers from leaking on error
5. Use `-s` (silent) on all curl calls to suppress progress output
6. Validate token existence without exposing its value

## API base URL

```
https://sigrid-says.com/rest/analysis-results/api/v1
```

## Workflow

### Step 0: Verify token availability (MUST run first)

Run this command EXACTLY:

```bash
if [ -n "$SIGRID_CI_TOKEN" ]; then
  echo "SIGRID_CI_TOKEN is set (${#SIGRID_CI_TOKEN} characters)"
else
  echo "SIGRID_CI_TOKEN is NOT set"
fi
```

- If NOT set: stop and tell the user to set it via their terminal (`export SIGRID_CI_TOKEN=...`). Remind them to never paste the token in the chat. They can obtain a token from their Sigrid account settings at https://sigrid-says.com.
- If set: proceed to Step 1.

### Step 1: Get customer and system names

Ask the user for their **customer** (Sigrid account name) and **system** name if not already known. These are required for all API calls.

### Step 2: Confirm result scope with the user (MANDATORY)

Before fetching any data, you MUST ask the user the following question and wait for their answer:

> Would you like to see **all refactoring candidates** or limit the results to the **top 10 candidates per property**?
>
> - **All candidates** - returns every finding across all properties. This can be a large dataset for systems with many findings.
> - **Top 10 per property** - returns only the 10 most severe candidates per maintainability property. Recommended for a focused, actionable overview.

**Do NOT proceed until the user has explicitly chosen one of these options.** This is a hard requirement.

Store their choice:
- If the user chose "all": do NOT include the `count` query parameter in API calls.
- If the user chose "top 10": include `count=10` in every refactoring candidates API call.

### Step 3: Fetch maintainability ratings

This provides the quality context for interpreting refactoring candidates.

```bash
curl -s --fail-with-body \
  -H "Authorization: Bearer $SIGRID_CI_TOKEN" \
  "https://sigrid-says.com/rest/analysis-results/api/v1/maintainability/{customer}/{system}"
```

From the response, extract the **latest entry** in `allRatings` and record the rating for each property:

| Property                 | API field                |
| ------------------------ | ------------------------ |
| Duplication              | `duplication`            |
| Unit Size                | `unitSize`               |
| Unit Complexity          | `unitComplexity`         |
| Unit Interfacing         | `unitInterfacing`        |
| Module Coupling          | `moduleCoupling`         |
| Component Independence   | `componentIndependence`  |
| Component Entanglement   | `componentEntanglement`  |

Also record the overall `maintainability` score.

### Step 4: Fetch refactoring candidates for all properties

For **each** of the seven properties, make a separate API call:

```bash
curl -s --fail-with-body \
  -H "Authorization: Bearer $SIGRID_CI_TOKEN" \
  "https://sigrid-says.com/rest/analysis-results/api/v1/refactoring-candidates/{customer}/{system}/{property}?count={n}"
```

Replace `{property}` with each of these values:
- `duplication`
- `unitSize`
- `unitComplexity`
- `unitInterfacing`
- `moduleCoupling`
- `componentIndependence`
- `componentEntanglement`

Only include `?count=10` if the user chose the top-10 option. Omit the parameter entirely for "all candidates".

You may run these curl calls in parallel to save time.

#### Response structure

Each response contains a `refactoringCandidates` array. Fields vary by property:

**Common fields (all properties):**
- `severity` — `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`
- `filePath` — relative file path
- `startLine`, `endLine` — line range of the finding
- `technology` — programming language
- `componentName` — component containing the finding

**Duplication-specific fields:**
- `loc` — number of duplicated lines
- `sameFile` — whether both fragments are in the same file
- `sameComponent` — whether both fragments are in the same component
- `locations` — array of `{filePath, startLine, endLine}` for each duplicated fragment

**Unit-level fields (unitSize, unitComplexity, unitInterfacing):**
- `unitName` — name of the function/method
- `mcCabe` — McCabe cyclomatic complexity (unitComplexity)
- `parameters` — number of parameters (unitInterfacing)

**Component Entanglement fields:**
- `componentEntanglementType` — one of: `CYCLIC_DEPENDENCY`, `INDIRECT_CYCLIC_DEPENDENCY`, `LAYER_BYPASSING_DEPENDENCY`, `COMMUNICATION_DENSITY`

## Presentation

### 1. Quality overview

Start with a summary table of the system's maintainability profile:

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

Use these interpretation ranges:
- 4.0+ = Good
- 3.0–3.9 = Adequate
- 2.0–2.9 = Below average
- < 2.0 = Needs attention

### 2. Candidate summary

Show a count of candidates found per property and severity:

```
## Refactoring Candidates Summary

| Property                 | Critical | High | Medium | Low | Total |
| ...                      | ...      | ...  | ...    | ... | ...   |
```

### 3. Per-property candidate listings

For each property that has candidates, list them sorted by severity (CRITICAL first, then HIGH, MEDIUM, LOW). For each candidate, show:

**Duplication candidates:**
```
### [{severity}] Duplication in {filePath}
- Lines {startLine}–{endLine} ({loc} duplicated lines)
- Duplicated with: {other locations from the locations array}
- Same file: {yes/no} | Same component: {yes/no}
```

**Unit Size candidates:**
```
### [{severity}] {unitName} in {filePath}
- Lines {startLine}–{endLine}
- Unit is too large — consider extracting logical sections into separate functions
```

**Unit Complexity candidates:**
```
### [{severity}] {unitName} in {filePath}
- Lines {startLine}–{endLine}
- McCabe complexity: {mcCabe}
- Simplify branching logic or extract complex conditions
```

**Unit Interfacing candidates:**
```
### [{severity}] {unitName} in {filePath}
- Lines {startLine}–{endLine}
- Parameters: {parameters}
- Reduce parameter count by grouping related parameters or using configuration objects
```

**Module Coupling candidates:**
```
### [{severity}] {filePath}
- Lines {startLine}–{endLine}
- Component: {componentName}
- Reduce coupling by introducing abstractions or restructuring dependencies
```

**Component Independence candidates:**
```
### [{severity}] {componentName}
- File: {filePath}, lines {startLine}–{endLine}
- Increase independence by reducing cross-component dependencies
```

**Component Entanglement candidates:**
```
### [{severity}] {componentName} — {componentEntanglementType}
- File: {filePath}, lines {startLine}–{endLine}
- Type: {human-readable description of entanglement type}
```

### 4. Prioritized action items

End with a short list of the top recommended actions, prioritized by:
1. Severity (CRITICAL > HIGH > MEDIUM > LOW)
2. Properties with the lowest ratings (from Step 3)
3. Quick wins — candidates that are likely easy to fix

## Error handling

- **401/403**: Token is expired or lacks permissions. Tell the user to check their token. NEVER show the request or token value.
- **404**: Customer or system name may be incorrect. Ask the user to verify.
- **No candidates for a property**: Report that the property has no refactoring candidates — this is a positive result.
- **No candidates at all**: Congratulate the user — their system has no refactoring candidates.
