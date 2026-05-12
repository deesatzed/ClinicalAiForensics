# PDDE v0.3 — First-Principles / Alien-Goggles Revision

This package revises the PDDE build plan after reassessing the previous roadmap from first principles and a radical outsider lens.

The major change:

**The primitive object is no longer an AI answer. The primitive object is a Clinical Decision Episode (CDE).**

AI-generated answers are only one possible input to a decision episode. The engine evaluates decision fitness, missing information, safety gates, local executability, and outcome-trackable decision profiles.

## Contents

- `01_FIRST_PRINCIPLES_REASSESSMENT.md`
- `02_REVISED_FINAL_PLAN.md`
- `03_CODEX_BUILD_SPEC.md`
- `04_TESTING_ALGORITHM.md`
- `05_PRIOR_AND_UNCERTAINTY_GOVERNANCE.md`
- `06_UI_AND_REPORTING_SPEC.md`
- `schemas/clinical_decision_episode.schema.json`
- `schemas/decision_profile.schema.json`
- `domain_packs/hf_ed_discharge/domain_pack.yaml`
- `codex_tasks/PHASE0_TASKS.md`

## Revised Core Rule

No probability without provenance.  
No composite score without its uncertainty budget.  
No clinical recommendation without a value-of-information statement.  
No AI-answer audit unless mapped to a clinical decision episode.  
No clinical deployment until priors, local rules, and calibration status are visible.
