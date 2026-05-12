# Implementation Plan

Initialized: 2026-05-11

## Direction

Use the v0.3 first-principles package as the implementation anchor.

The first build is a direct Clinical Decision Episode simulator, not an AI-answer auditor. Older `pdde-build-package` Workflow A specs remain useful later, but direct simulation must work first.

## Target Package Shape

Phase 0 should converge on this package shape:

```text
pdde/
  __init__.py
  __main__.py
  models.py
  cde_loader.py
  domain_pack_loader.py
  safety_gate_engine.py
  prior_resolver.py
  monte_carlo_engine.py
  uncertainty_budget.py
  value_of_information.py
  decision_profiler.py
  report_renderer.py
  provenance_logger.py
  run_cde.py
```

Expected support directories:

```text
domain_packs/hf_ed_discharge/domain_pack.yaml
examples/
  hf_cde_stable.json
  hf_cde_low_egfr.json
  hf_cde_high_k.json
  hf_cde_low_sbp.json
  hf_cde_no_followup.json
  hf_cde_prior_dka.json
  hf_cde_missing_labs.json
reports/
logs/
tests/
```

## Phase -1: Tabletop And Source Reconciliation

Status: partially satisfied by existing source material; not yet formalized as tests.

Tasks:

- Reconcile v0.3 `domain_pack.yaml` with root `hf_ed_discharge_v0.yaml`.
- Prefer the v0.3 CDE/domain-pack vocabulary where conflicts exist.
- Keep the richer v0.1 YAML and sample report as reference for report structure and clinical dimensions.
- Manually reason through at least three CDEs: stable, unsafe, ambiguous.
- Record ontology issues in a future `BUILD_LOG.md`.

Acceptance:

- A single chosen Phase 0 domain-pack schema is documented.
- Fixture list covers stable, low SBP, low eGFR, high potassium, no follow-up, prior DKA, and missing labs.

## Phase 0: CLI CDE Simulator

### 0.0 Project Setup

Create `pyproject.toml`, package skeleton, test skeleton, and CLI help stub.

Acceptance:

- `python -m pdde --help` exits successfully.
- No clinical logic implemented before package scaffolding is testable.

### 0.1 Data Models

Implement Pydantic models for:

- ClinicalDecisionEpisode,
- DomainPack,
- DecisionOption,
- SafetyGate,
- Prior,
- LocalOverlayRule,
- DecisionProfile,
- UncertaintyBudget,
- ValueOfInformationItem,
- RunMetadata,
- PriorUsageLog,
- PredictionLog.

Acceptance:

- Priors without provenance fail validation.
- local rules without owner/status fail validation.
- CDE and domain-pack fixtures load into typed models.

### 0.2 Loaders

Implement CDE JSON and domain-pack YAML loaders.

Acceptance:

- `hf_cde_stable.json` loads.
- HF domain pack loads.
- validation errors identify specific missing or invalid fields.

### 0.3 Deterministic Safety Gate Engine

Evaluate hard stops before probabilistic simulation.

Initial hard-stop categories:

- SBP below threshold,
- persistent/worsening oxygen requirement,
- severe residual congestion,
- no required follow-up,
- eGFR threshold blocks for SGLT2/MRA,
- potassium threshold blocks for MRA,
- active ketosis/high euglycemic DKA risk for SGLT2,
- wrong-indication claims such as sotalol as HF GDMT beta blocker.

Acceptance:

- Hard stops produce explicit `hard_stops` in affected decision profiles.
- A blocked option cannot become action-ready from Monte Carlo scoring.

### 0.4 Prior Resolver

Resolve only allowed Phase 0 prior classes.

Allowed for direct simulation:

- `guideline_mapped_policy_prior`,
- `draft_expert_policy_prior`,
- compatible v0.1 `guideline_mapped` or `panel_elicited_pending` priors if normalized and visibly marked.

Not allowed in Phase 0 direct simulation:

- `llm_unverified` as an active prior.

Acceptance:

- LLM-unverified priors fail or are quarantined in direct-simulation mode.
- Every prior used appears in run metadata.

### 0.5 Monte Carlo Engine

Use vectorized NumPy sampling for soft nodes.

Default iterations: 10,000.

Acceptance:

- Results are reproducible with a seed.
- Each option returns median, 5th percentile, 95th percentile, interval width, and category probabilities.
- 10,000 iterations on the stable fixture meet the Phase 0 performance budget.

### 0.6 Uncertainty Budget

Every option interval must include an uncertainty budget.

Minimum categories:

- evidence uncertainty,
- patient context uncertainty,
- local execution uncertainty,
- monitoring/rescue uncertainty,
- harm uncertainty,
- preference/feasibility uncertainty,
- prior quality uncertainty.

Acceptance:

- Every Decision Profile has all required uncertainty-budget keys.
- Report rendering fails loudly if an option lacks a budget.

### 0.7 Value Of Information

Rank missing or fragile variables by expected influence on the decision.

Initial HF candidates:

- eGFR,
- potassium,
- post-diuresis SBP,
- volume status,
- DKA risk,
- follow-up availability,
- medication access,
- patient preference.

Acceptance:

- Missing labs rank high in missing-labs fixture.
- No report omits value-of-information content.

### 0.8 Decision Profiler

Combine hard gates, soft simulation, uncertainty budget, and value-of-information into Decision Profiles.

Categories:

- action-ready,
- conditionally defensible,
- needs more data,
- escalate/observe/admit,
- locally infeasible,
- discouraged,
- unsafe/wrong indication.

Acceptance:

- Stable case ranks loop/continue GDMT high and SGLT2 as conditional.
- Low SBP raises admit/observe/escalate.
- High K makes MRA unsafe or blocked.
- Low eGFR lowers SGLT2 and MRA.

### 0.9 Report Renderer

Render Markdown only.

Required sections:

1. Advisory warning.
2. Decision episode summary.
3. Hard stops.
4. Ranked decision profiles.
5. Why the top option is not automatically the answer.
6. Missing variables and value-of-information.
7. Uncertainty budget.
8. Local execution checklist.
9. Patient feasibility/preference gaps.
10. Prior provenance.
11. Calibration status.
12. Limitations.

Acceptance:

- Report includes every required section.
- Draft/unverified priors and local rules are visibly marked.
- Report does not make clinical validation or outcome claims.

### 0.10 CLI

Required command:

```bash
python -m pdde.run_cde \
  --cde examples/hf_cde_stable.json \
  --domain domain_packs/hf_ed_discharge/domain_pack.yaml \
  --out reports/hf_cde_stable_report.md
```

Preferred top-level command may also be exposed as:

```bash
python -m pdde run-cde ...
python -m pdde validate ...
```

Acceptance:

- CLI writes a Markdown report.
- `validate` checks CDE and domain-pack structure.
- Missing files and validation errors exit non-zero with clear messages.

### 0.11 Provenance Logging

Implement append-only JSONL-compatible logs for:

- run metadata,
- priors used,
- predictions/decision profiles.

Acceptance:

- Each CLI run creates one run metadata record.
- Each prior used is logged.
- Each option profile is logged.

### 0.12 Tests And Acceptance Suite

Implement unit, integration, metamorphic, missingness, hard-stop, uncertainty-budget, report, and CLI tests.

Acceptance:

- All automated Phase 0 tests pass.
- Manual structural report review is documented in `BUILD_LOG.md`.

## Deferred Phase 1: AI Answer Mapping

After direct CDE simulation works:

- claim extraction from AI answers,
- claim-to-option mapping,
- omissions and overstatement flags,
- prohibited recommendation scanning,
- citation/evidence audit preparation.

The older `pdde-build-package/specs/02_claim_extractor.md` and `03_node_parameterizer.md` should be reused at that point, but they should not block the Phase 0 direct simulator.

