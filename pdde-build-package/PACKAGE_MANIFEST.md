# Package Manifest

PDDE v0.1 Build Package · 2026-05-11

## Contents

### Root
- `CLAUDE.md` — Entry point for Claude Code (READ FIRST)
- `README.md` — Human-readable overview
- `PACKAGE_MANIFEST.md` — This file
- `FIRST_TASK.md` — Concrete first action for Claude Code

### `docs/` — Background and governance
- `master_plan.md` — Full strategic plan (Phases 0–6, publication strategy)
- `architecture.md` — 6-layer architecture detail
- `non_negotiable_constraints.md` — 10 inviolable design rules
- `risk_register.md` — Risks to watch during build
- `glossary.md` — Clinical, statistical, engineering terms

### `networks/` — Belief networks (clinical models)
- `hf_ed_discharge_v0.yaml` — HFrEF/HFmrEF ED-discharge belief network with provenance, gates, prohibited recommendations, local overlay

### `examples/` — Test fixtures
- `sample_case_HF-001.json` — Baseline patient case (favorable profile)
- `sample_report_HF-001.md` — Target output (what the engine should produce)
- `adversarial_sotalol.txt` — AI answer claiming sotalol is an HF beta-blocker
- `adversarial_glp1.txt` — AI answer claiming GLP-1 RAs prevent HF admissions
- `case_egfr_15.json` — Counterfactual: severe renal dysfunction
- `case_potassium_57.json` — Counterfactual: hyperkalemia
- `case_sbp_86.json` — Counterfactual: borderline hypotension
- `case_missing_labs.json` — Counterfactual: sparse data
- `adv_hidden_001.json` — Adversarial: hidden eGFR contraindication
- `adv_uncertain_001.json` — Adversarial: minimal data (uncertainty test)
- `adv_renal_001.json` — Adversarial: borderline eGFR for SGLT2

### `specs/` — Component specifications
- `01_data_models.md` — Pydantic schemas
- `02_claim_extractor.md` — LLM-based claim extraction (Workflow A)
- `03_node_parameterizer.md` — Claim-to-node mapping with LLM fallback
- `04_monte_carlo_engine.md` — Core inference module
- `05_sensitivity_analyzer.md` — Variance decomposition
- `06_report_generator.md` — Markdown report output
- `07_provenance_manager.md` — JSONL logging
- `08_cli_runner.md` — Entry-point CLI

### `prompts/` — LLM prompt templates
- `claim_extraction.md` — Extract claims from AI answers
- `node_parameterization.md` — LLM-elicit priors for unknown claim types

### `tests/` — Test specifications
- `phase_0_acceptance.md` — The 6 sharp tests that gate Phase 0 completion
- `adversarial_suite.md` — 10 categories × 1 case (target: 5/10 pass)
- `unit_test_specs.md` — Per-component unit tests

### `build/` — Build infrastructure
- `build_order.md` — Sequential dependency-ordered task list
- `tech_stack.md` — Versions, deps, environment setup
- `pyproject_template.toml` — Starter project file

## File count

```
Total files: 33
Total size: ~110 KB
Estimated read time: ~45 minutes
Estimated build effort: ~46 hours solo, ~20 hours with Claude Code
```

## Critical first-read order for Claude Code

1. `CLAUDE.md` — orientation (5 min)
2. `FIRST_TASK.md` — what to do right now (2 min)
3. `docs/non_negotiable_constraints.md` — the 10 rules (5 min)
4. `build/build_order.md` — task sequence (10 min)
5. `specs/01_data_models.md` — start here for actual code (15 min)
6. `networks/hf_ed_discharge_v0.yaml` — skim to understand the shape (10 min)

After that, Claude Code is calibrated and can pull specs as needed.

## What this package does NOT include

- Source code (this is a specification package; Claude Code writes the code)
- Real patient data (all examples are synthetic)
- Anthropic API key (set via env var; never commit)
- Generated reports (the sample is a target; running the system produces real ones)

## License

All package contents are released under MIT for code specifications and CC-BY-4.0 for belief networks and prompts. The clinical content reflects publicly available guidelines and should not be used for patient care decisions without independent verification.
