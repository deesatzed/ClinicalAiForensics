# UI and Reporting Spec v0.3

## Phase 0

Markdown only.

## Phase 1 UI Rule

Never reduce output to a single badge.

If using color:

- it must accompany interval,
- uncertainty budget,
- hard stops,
- missing variables,
- and local execution status.

## Required Report Header

> Advisory-only decision-fitness simulation. This output is not clinically validated and does not determine truth. It estimates defensibility under explicit assumptions and draft priors.

## Required Report Sections

1. Decision episode summary.
2. Hard stops and safety gates.
3. Ranked decision profiles.
4. Why the top option is not automatically “the answer.”
5. Missing variables and value-of-information.
6. Uncertainty budget.
7. Local execution checklist.
8. Patient feasibility/preference gaps.
9. Prior provenance table.
10. Calibration status.
11. Limitations.

## Decision Profile Template

```text
Option: Start/continue SGLT2 inhibitor
Category: Conditionally defensible
Median decision fitness: 0.xx
Uncertainty interval: x–y
Hard stops: none detected / present
Critical assumptions:
- eGFR acceptable
- SBP stable
- no active ketosis/DKA risk
- not volume depleted
- medication access confirmed
- follow-up/labs feasible
Main uncertainty drivers:
- eGFR
- BP
- follow-up
- DKA risk
Value of information:
- check current BMP and post-diuresis BP
Local execution:
- pending pathway verification
```

## UI Safety Warnings

- Do not show “recommended” without category.
- Do not allow a hidden hard stop.
- Do not show decimals without provenance.
- Do not hide draft status.
