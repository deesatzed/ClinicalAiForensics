# PDDE Phase 0

## What This Is

PDDE Phase 0 is a deterministic, evidence-preserving clinical decision-profile scaffold. It loads a synthetic Clinical Decision Episode (CDE), evaluates it against an explicit HF ED discharge domain pack, and renders an advisory Decision Profile report.

It is not a final clinical decision engine. It does not decide whether a patient should be discharged, admitted, or treated. Its purpose is to preserve assumptions, safety gates, priors, uncertainty, missing data, deferred inputs, and provenance so a technical reviewer can inspect the shape of the decision workflow.

Phase 0 is local, CLI-only, synthetic, advisory-only, uncalibrated, and not clinically validated.

## What It Does

- Loads CDE JSON and domain-pack YAML files through strict typed loaders.
- Provides inspectable synthetic CDE scenario fixtures under `examples/`.
- Validates explicit domain-pack mappings for safety-gate targets and prior-to-option links.
- Surfaces explicit evidence-reference link status without validating source truth.
- Evaluates deterministic safety gates before probabilistic sampling.
- Provides an API-only deterministic AI-answer claim mapping boundary for explicit source-backed prohibited-claim patterns.
- Resolves explicit priors from the domain pack while preserving provenance.
- Samples explicit beta priors with deterministic seeding.
- Evaluates explicit uncertainty-budget and value-of-information definitions.
- Records local overlay verification metadata while leaving draft or incomplete local rules inactive.
- Assembles Decision Profile status records.
- Renders advisory Markdown reports.
- Writes status-only provenance JSONL logs.
- Runs local pytest coverage for models, loaders, engines, CLI behavior, reports, logs, and Phase 0 acceptance paths.

## What It Does Not Do

- No final clinical recommendations.
- No LLM/AI clinical judgment.
- No hidden scoring, trust score, truth score, option ranking, or decision-fitness formula.
- No invented thresholds, utilities, weights, or priors.
- No PHI storage.
- No production deployment.
- No EHR integration, auth, UI, API service, PDF export, or production database.
- No LLM answer extraction, free-text clinical judgment, answer grading, or CLI AI-answer mapping.
- No free-text answer content directly modifying priors, thresholds, gates, or recommendations.
- No active local operational overlay rules without explicit owner/source/review metadata.
- No validated risk, outcome claim, or calibration claim.
- No automated evidence truth validation, citation correctness scoring, or source-quality scoring.

## Quickstart

Clone with supporting submodules when starting from GitHub:

```bash
git clone --recurse-submodules https://github.com/deesatzed/ClinicalAiForensics.git
cd ClinicalAiForensics
```

For an existing checkout that lacks supporting folders:

```bash
git submodule update --init --recursive
```

Optional virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install package locally:

```bash
python -m pip install -e ".[dev]"
```

Run tests:

```bash
python -m pytest
```

Run help:

```bash
python -m pdde --help
```

Validate canonical fixtures:

```bash
python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml
```

Generate report to stdout:

```bash
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --iterations 5 --seed 17
```

Generate report to file:

```bash
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --output reports/hf_cde_stable_report.md --iterations 5 --seed 17
```

Generate report and provenance log:

```bash
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl --iterations 5 --seed 17
```

## Example Commands

Canonical CDE:

```text
pdde_v0_3_first_principles_final/examples/hf_cde_stable.json
```

Canonical domain pack:

```text
pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml
```

Root scenario fixtures:

```text
examples/hf_cde_stable.json
examples/hf_cde_low_egfr.json
examples/hf_cde_high_k.json
examples/hf_cde_low_sbp.json
examples/hf_cde_no_followup.json
examples/hf_cde_prior_dka.json
examples/hf_cde_missing_labs.json
```

Common review commands:

```bash
python -m pdde --help
python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --iterations 5 --seed 17
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl --iterations 5 --seed 17
python -m pdde validate --cde examples/hf_cde_high_k.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml
python -m pdde report --cde examples/hf_cde_missing_labs.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --iterations 5 --seed 17
```

Compatibility command:

```bash
python -m pdde run-cde --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --out reports/hf_cde_stable_run_cde_report.md --iterations 5 --seed 17
```

## Output Files

`reports/hf_cde_stable_report.md`

- Generated advisory Markdown report.
- Ignored by git by default; regenerate it from the canonical fixtures when needed.
- Shows case/domain identifiers, safety gate results, Decision Profile statuses, VOI items, uncertainty-budget items, prior provenance, Monte Carlo prior summaries, unresolved items, calibration status, provenance references, and limitations.
- Shows evidence-reference link status as IDs and statuses only; it does not claim cited sources are true or clinically correct.
- Displays synthetic case text and patient-state values because the report is a human-facing synthetic artifact.
- Displays local overlay verification state, but does not print raw local workflow text.
- Does not provide a final recommendation or top option.

`logs/hf_cde_stable.jsonl`

- Appendable provenance log.
- Ignored by git by default; repeated local runs append records and should not be treated as a stable source fixture.
- Each line is JSON.
- Records run metadata, component status summaries, evidence-reference link statuses, safety gate statuses, prior-resolution statuses, Monte Carlo prior statuses, uncertainty-budget statuses, VOI statuses, Decision Profile statuses, source references, command name, package version, seed, iteration count, and report path.
- Intentionally avoids full raw case text, full patient-state payloads, PHI, gate evidence strings, raw simulation sample arrays, and raw local overlay owner/source/review values.

## Architecture Overview

```text
CLI
  -> strict CDE loader
  -> strict domain-pack loader
  -> explicit domain-pack mappings
  -> optional typed AI-answer claim mapping boundary
  -> safety gate engine
  -> prior resolver
  -> Monte Carlo prior sampler
  -> value-of-information evaluator
  -> uncertainty-budget evaluator
  -> local overlay verification evaluator
  -> Decision Profiler assembler
  -> evidence-reference link status projection
  -> status ledger projection
  -> report section contract
  -> Markdown renderer
  -> JSONL provenance logger
```

| Module | Responsibility |
| --- | --- |
| `pdde/run_cde.py` | CLI parser and handlers for `validate`, `report`, and `run-cde`. |
| `pdde/cde_loader.py` | Reads and validates CDE JSON. |
| `pdde/domain_pack_loader.py` | Reads and validates domain-pack YAML. |
| `pdde/model_base.py`, `pdde/input_models.py`, `pdde/component_models.py`, `pdde/pipeline_models.py`, `pdde/legacy_models.py` | Focused Pydantic data contracts for inputs, explicit domain-pack mappings, component results, pipeline results, and legacy report/log models. |
| `pdde/models.py` | Backwards-compatible re-export facade for model imports. |
| `pdde/ai_answer_mapping.py` | API-only deterministic mapper for explicit source-backed AI-answer prohibited-claim patterns; stores structured claim metadata, not raw answers. |
| `pdde/evidence_linking.py` | API-only validator for explicit domain-pack evidence-reference IDs against an optional evidence registry; reports link/support status without source truth validation. |
| `pdde/safety_gate_engine.py` | Evaluates explicit deterministic safety gates using domain-pack gate-target mappings. |
| `pdde/prior_resolver.py` | Resolves explicit allowed priors and blocks unsupported prior classes. |
| `pdde/monte_carlo_engine.py` | Samples explicit resolved beta priors with deterministic seeds. |
| `pdde/value_of_information.py` | Evaluates explicit VOI definitions without inventing VOI math. |
| `pdde/uncertainty_budget.py` | Evaluates uncertainty-budget categories and deferred items. |
| `pdde/local_overlay.py` | Evaluates local overlay verification metadata and keeps draft/incomplete local rules inactive. |
| `pdde/decision_profiler.py` | Assembles Decision Profile statuses using explicit prior-to-option mappings without ranking or recommendation logic. |
| `pdde/evaluation_pipeline.py` | Orchestrates the deterministic component chain. |
| `pdde/status_ledger.py` | Projects visible component statuses into a shared ledger for report and provenance summaries. |
| `pdde/report_contract.py` | Defines required Markdown report sections, ordering, advisory language, and forbidden recommendation phrases. |
| `pdde/report_renderer.py` | Renders advisory Markdown from the typed pipeline result. |
| `pdde/provenance_logger.py` | Writes status-only JSONL provenance records. |

## Safety And Privacy Guardrails

- Synthetic fixtures only.
- Advisory-only output.
- Reports state that output is not clinically validated and not a final clinical recommendation.
- Deterministic safety gates run before Monte Carlo sampling.
- Favorable prior samples cannot override a hard safety gate.
- Missing inputs remain visible as missing, actionable, or deferred; they do not increase certainty.
- Unsupported gates and deferred claim-type gates remain visible rather than silently passing.
- AI-answer mapping is API-only, deterministic, source-backed, and separate from direct CDE simulation; raw answer text is not stored in pipeline results, reports, or logs.
- LLM-unverified priors are blocked from active direct simulation.
- Monte Carlo is prior-level only and does not produce option rankings.
- Local overlay rules remain draft, deferred, missing, or unsupported unless explicit verification metadata is complete; even verified metadata does not create local clinical logic.
- Evidence-reference status is link/support visibility only, not citation scoring or evidence truth validation.
- Provenance logs use IDs, statuses, counts, paths, and source references rather than raw clinical payloads.
- Provenance logs redact raw local overlay owner, source, review-cadence, and last-reviewed values.
- Tests remove common API-key environment variables and block network access in acceptance coverage.

## Test Status

Current test status: 146 passing tests across 21 test files.

Run:

```bash
python -m pytest
```

The suite covers model validation, loaders, deterministic safety gates, explicit AI-answer claim mapping, prior resolution, Monte Carlo reproducibility, uncertainty/VOI evaluation, local overlay verification, Decision Profiler assembly, evaluation pipeline, status-ledger projection, report-contract guardrails, report rendering, CLI behavior, provenance logging, and Phase 0 acceptance workflows.

## Phase 2

Phase 2 is active for governance-contract hardening. The Phase 0 stable baseline is tagged as `phase0-baseline`, and the Phase 1 stable baseline is tagged as `phase1-baseline`.

See `PHASE2_PLAN.md` for the current roadmap, `PHASE1_COMPLETION_REVIEW.md` for the Phase 1 baseline review, and `BASELINE_POLICY.md` for the baseline, submodule, and generated-artifact policy. Runtime clinical behavior remains advisory-only until a later governed task explicitly changes it.
