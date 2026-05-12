# Codex Build Spec v0.3

## Build Objective

Create a Phase 0 CLI that performs direct Clinical Decision Episode simulation for the HF ED discharge domain.

Do not build frontend, auth, PDF, database, or citation audit in Phase 0.

## Package Structure

```text
pdde/
  models.py
  cde_loader.py
  domain_pack_loader.py
  safety_gate_engine.py
  prior_resolver.py
  monte_carlo_engine.py
  decision_profiler.py
  uncertainty_budget.py
  value_of_information.py
  report_renderer.py
  run_cde.py
```

## Required CLI

```bash
python -m pdde.run_cde \
  --cde examples/hf_cde_stable.json \
  --domain domain_packs/hf_ed_discharge/domain_pack.yaml \
  --out reports/hf_cde_stable_report.md
```

## Implementation Requirements

### 1. CDE Loader

Load and validate Clinical Decision Episode JSON.

### 2. Domain Pack Loader

Load:

- decision options,
- nodes,
- priors,
- hard gates,
- local overlay placeholders,
- testing expectations.

### 3. Safety Gate Engine

Evaluate deterministic hard stops before Monte Carlo.

If hard stop exists, probabilistic score cannot override it.

### 4. Prior Resolver

Resolve priors only from allowed classes.

Phase 0 allowed:

- guideline_mapped_policy_prior
- draft_expert_policy_prior

LLM priors are not allowed in Phase 0 direct simulation.

### 5. Monte Carlo Engine

Sample soft nodes.

Use NumPy.

Default iterations: 10,000.

### 6. Decision Profiler

Return for each option:

- category,
- median fitness,
- interval,
- hard stops,
- soft concerns,
- missing variables,
- uncertainty budget,
- value-of-information ranking.

### 7. Report Renderer

Markdown only.

Required report sections:

1. Advisory warning.
2. Decision episode summary.
3. Hard stops.
4. Ranked decision profiles.
5. Missing variables.
6. Value-of-information.
7. Uncertainty budget.
8. Local execution checklist.
9. Prior provenance.
10. Calibration status.

## Phase 0 Acceptance Criteria

1. Stable case: discharge + loop + continue GDMT and conditional SGLT2 rank high.
2. Low SBP case: admit/observe/escalate rises.
3. Low eGFR case: SGLT2 and MRA drop.
4. High K case: MRA unsafe.
5. No follow-up case: local executability low and monitoring failure flagged.
6. Prior DKA case: SGLT2 discouraged or escalated.
7. Missing labs case: interval widens and value-of-information ranks labs high.
8. No output claims clinical validation.
