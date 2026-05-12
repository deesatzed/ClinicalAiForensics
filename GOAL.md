# Project Goal

Initialized: 2026-05-11

## Mission

ClinAIForensics will turn the PDDE build directions and supporting ClinSafer / Agent_Pidgeon material into an executable, stepwise build plan for a Phase 0 clinical decision-governance prototype.

The product direction is:

> For a Clinical Decision Episode, identify which candidate actions are defensible under explicit assumptions, hard safety gates, missing data, local execution constraints, draft priors, and calibration status.

The system must not primarily grade AI answers. An AI answer is a later optional input. The primitive object is the Clinical Decision Episode (CDE).

## Phase 0 Target

Build a Python CLI that performs direct CDE simulation for the first MVP domain:

ED discharge medication/disposition strategy for known HFrEF/HFmrEF after IV diuresis.

The CLI should load:

- a Clinical Decision Episode JSON,
- an HF ED discharge domain pack,
- deterministic hard safety gates,
- provenance-bound priors,
- local overlay placeholders,
- and simulation settings.

It should output a Markdown Decision Profile report with:

- advisory-only warning,
- decision episode summary,
- hard stops and safety gates,
- ranked decision profiles,
- missing variables,
- value-of-information ranking,
- uncertainty budget,
- local execution checklist,
- prior provenance,
- calibration status,
- and limitations.

## Source Priority

When sources conflict:

1. `pdde_v0_3_first_principles_final/` controls product direction.
2. `instruc1.md` explains the v0.3 pivot and should be treated as controlling rationale.
3. `pdde-build-package/` supplies useful granular implementation specs, tests, and older Workflow A material where compatible with v0.3.
4. `ClinSafer/` supplies supporting safety architecture patterns: uncertainty graph, black-swan guardrails, governed medical knowledge, most-restrictive governor, and unknowns handling.
5. `Agent_Pidgeon/` supplies supporting provenance patterns: deterministic contracts, policy checks, receipts, semantic diffs, and flight-recorder traces.
6. Root fixtures `hf_ed_discharge_v0.yaml`, `sample_case_HF-001.json`, and `sample_report_HF-001.md` provide concrete v0.1 reference artifacts and expected report shape.

## Non-Goals For Phase 0

- No frontend.
- No authentication.
- No EHR integration.
- No clinical deployment.
- No PDF export.
- No production database.
- No citation/evidence audit beyond explicit placeholders.
- No AI answer extraction in the first direct-simulation build path.
- No vendor ranking as a primary artifact.

## Success Criteria

Phase 0 is successful when a user can run a CLI on synthetic HF CDE fixtures and receive a Markdown report that:

- clearly separates hard safety gates from probabilistic simulation,
- never emits a single trust or truth score as the primary answer,
- widens uncertainty when important data is missing,
- ranks value-of-information drivers,
- surfaces prior provenance and local overlay status,
- states that the output is unvalidated and advisory-only,
- passes unit, hard-stop, missingness, metamorphic, and report completeness tests.

