---
name: sigrid-diagnose
user-invocable: true
description: >
  Guided maintainability diagnosis for a Sigrid system. Finds the weakest property, explains what is causing it, and surfaces the top refactoring candidates. Use when the user wants to understand where to start   
  improving code quality, or asks what their biggest maintainability problem is.
---

# Sigrid Diagnose

## Goal

This skill is purely for diagnosis: identify where code quality can be improved and why. It does not prescribe how to fix anything — judge whether something is a problem (including flagging non-best-practice patterns), but stop short of implementation guidance. That belongs in `sigrid-improve`.

Not all refactoring candidates are equal. Choosing the wrong one wastes effort on low-impact or high-risk changes. This skill ranks candidates so that `sigrid-improve` acts on the highest-leverage ones first.

## Prerequisites

- Sigrid customer and system name must be in context. If not, check your context file (e.g. AGENTS.md, CLAUDE.md). If not there, ask the user and store them in the context file.
- The Sigrid MCP plugin is available: `refactoring_candidates`,
  `maintainability_ratings`, `code_quality_guardrails`

## How to determine which refactoring candidates have the most impact

### 1. Retrieve maintainability ratings from Sigrid MCP
Use `maintainability_ratings` to get maintainability ratings.

Parse the result. The ratings object contains properties: unitSize, unitComplexity,
unitInterfacing, duplication, moduleCoupling, componentIndependence, componentEntanglement.
Each is a float on a 0.5–5.5-star scale. Identify the property with the lowest value.

### 2. Get refactoring candidates for ALL properties

Retrieve top 100 candidates for every property in parallel:
- unitSize, unitComplexity, unitInterfacing, duplication, moduleCoupling, componentIndependence, componentEntanglement

Use count=100 for each call. Do not limit to the weakest property only — cross-referencing across all properties is essential (see step 3).

### 3. Choose the most impactful refactoring candidates

#### 3a. Cross-reference findings across properties

A finding that appears in multiple property lists is a higher-leverage target than one that affects only a single metric. For each candidate, note which properties it contributes to. Prioritise findings that show up in 2+ lists — fixing them improves multiple ratings simultaneously.

#### 3b. Analyse the system-level risk distribution

For each property, look at the severity distribution of the top-100 results (count of VERY_HIGH / HIGH / MEDIUM findings and their aggregate weight). Do not assume that VERY_HIGH findings dominate. In many systems, a large number of MEDIUM or HIGH findings collectively outweigh a small cluster of VERY_HIGH ones. State explicitly which tier drives the score for each property.

#### 3c. General considerations
Reason about the retrieved maintainability results and choose the most impactful refactoring candidates. Considerations:
- Prefer internal types and non-public interfaces where the blast radius is contained.
- Does the pattern across candidates point to a structural problem (e.g. a whole cluster of similar files)?
- Judge candidates against best practices for that language.
- Important to note: resolving a single finding does not move a system rating much — look for clusters.

| Property | Fixability |
|---|---|
| `unitInterfacing` | High |
| `unitSize` | High |
| `unitComplexity` | Medium |
| `duplication` | Medium |
| `moduleCoupling` | Low |
| `componentIndependence` | Low |
| `componentEntanglement` | Low |

`refactoring_candidates` results are already sorted by LOC-weighted contribution (LOC per risk category), so the first results are the highest-impact ones.

Quantized properties are scored on a risk-bracket profile weighted by LOC relative to total system volume. A finding's contribution to the score = its LOC in that bracket / total system LOC. This means there are always two ways to reduce a finding's impact: (1) move its metric value across a bracket edge (e.g. reduce params from 8 to 4), or (2) reduce the LOC carrying the bad-bracket weight (e.g. split a large unit so each piece weighs less). Both are legitimate improvement paths.

### 4. Present the results

Present in this order:

Ratings at a Glance

    <property>    <rating>    <gap to 4.0>
    ... (all 7 properties, sorted worst-first)

Risk Distribution

    For each property: state how many VERY_HIGH / HIGH / MEDIUM findings are in the top 100
    and which tier carries the most aggregate weight. Call out explicitly if medium-severity
    findings dominate.

Cross-Property Hotspots

    List files/modules that appear in 2+ property lists. For each, name the properties and
    explain why fixing it is high leverage.

Root Cause Summary

    One paragraph per weak property explaining the structural pattern behind the low score.

Prioritized Action Plan

    Numbered list. Each item: what to do, which properties it affects, rough effort.
    Do not include any projected rating improvements — describe impact qualitatively only.

---

## Avoid:
- Never make assumptions about rating improvements. Sigrid does not expose projected score changes,
  so statements like "this would move the rating by 0.3 stars" or "estimated impact: +0.2" are
  fabricated. Do not write them anywhere in the output — not in the action plan, not in hotspot
  analysis, not in passing. Describe impact in qualitative terms only (e.g. "removes the largest
  single source of duplication").
- Avoid suggesting large-scale architecture improvements, since they are often too wide-scoped to refactor in one go.
- Public API endpoints — changing their signatures breaks callers.
- Serialized types with public field names — renaming them is a breaking change for clients.
