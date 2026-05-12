# Codex Phase 0 Tasks v0.3

## Objective

Build direct CDE simulation first. Do not implement AI answer extraction yet.

## Ordered Tasks

1. Implement `ClinicalDecisionEpisode` Pydantic model.
2. Implement `DomainPack` loader.
3. Implement deterministic safety gate engine.
4. Implement prior resolver with provenance validation.
5. Implement Monte Carlo simulator for soft nodes.
6. Implement uncertainty budget generator.
7. Implement value-of-information ranking.
8. Implement decision profiler.
9. Implement Markdown report renderer.
10. Implement CLI `run_cde`.
11. Add fixtures:
    - stable
    - low eGFR
    - high K
    - low SBP
    - no follow-up
    - prior DKA
    - missing labs
12. Add metamorphic tests.
13. Document ontology issues.

## Hard Acceptance Rules

- Hard stops override probabilistic scores.
- Missing data cannot improve recommendation certainty.
- Every output interval must have an uncertainty budget.
- Every prior must have provenance and calibration status.
- Report must say advisory-only and uncalibrated.
