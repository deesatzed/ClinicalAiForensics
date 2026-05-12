# Phase 0 Handoff

## Current Status

Phase 0 is implemented as a local Python CLI and API for direct Clinical Decision Episode evaluation. It loads the canonical synthetic HF ED discharge CDE and domain pack, validates both into typed models, runs deterministic component layers, renders an advisory Markdown Decision Profile report, and can append status-only JSONL provenance logs.

No non-deferred Phase 0 implementation tasks remain in `TASK_QUEUE.md`. Phase 1 has started with baseline/artifact policy work only.

The Phase 0 stable baseline is tagged as `phase0-baseline`.

Phase 0 is not clinically validated, is not a clinical decision support system, and must not be used with PHI or real patient-care decisions.

## What Works

- Strict CDE JSON and domain-pack YAML loading with clear loader errors.
- Pydantic v2 typed models for CDEs, domain packs, component outputs, evaluation results, reports, and provenance records.
- Deterministic safety gate evaluation for explicit hard gates using domain-pack gate-target mappings.
- Deterministic prior resolution for explicit allowed priors, with blocked/unsupported/missing states preserved.
- Seeded prior-level Monte Carlo sampling for explicit numeric beta priors.
- Uncertainty-budget and value-of-information item classification without invented VOI math.
- Decision Profile assembly that uses explicit prior-to-option mappings and preserves blockers, triggers, missing data, unsupported inputs, deferred items, and provenance.
- End-to-end evaluation pipeline through `pdde/evaluation_pipeline.py`.
- Deterministic advisory Markdown report rendering.
- CLI validation, report generation to stdout, report generation to file, and optional provenance JSONL logging.
- Phase 0 acceptance tests over the CLI, Python API, report guardrails, and log guardrails.

## How To Run It

Install/setup, if dependencies are not already installed:

```bash
python -m pip install -e ".[dev]"
```

Run tests:

```bash
python -m pytest
```

Validate canonical fixtures:

```bash
python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml
```

Generate a report to stdout:

```bash
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --iterations 5 --seed 17
```

Generate a report to file:

```bash
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --output reports/hf_cde_stable_report.md --iterations 5 --seed 17
```

Generate a report and append a provenance log:

```bash
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl --iterations 5 --seed 17
```

Compile all package modules:

```bash
python -m py_compile pdde/*.py
```

## Main Files And What They Do

| Path | Purpose |
| --- | --- |
| `GOAL.md` | Project goal, source priority, Phase 0 target, non-goals, and success criteria. |
| `STANDARDS.md` | Clinical safety, engineering, provenance, testing, privacy, and output standards. |
| `IMPLEMENT.md` | Phase 0 build plan and intended module layout. |
| `DECISIONS.md` | Durable architectural, scope, safety, and release decisions. |
| `PROGRESS.md` | Work log and verification history. |
| `TASK_QUEUE.md` | Completed Phase 0 tasks and deferred Phase 1 items. |
| `REPO_MAP.md` | Repository map, source inventory, architecture summary, risks, and current status. |
| `BUILD_LOG.md` | Phase 0 build log, manual structural review, and ranked improvement opportunities. |
| `PHASE0_HANDOFF.md` | This operator-facing Phase 0 handoff package. |
| `BASELINE_POLICY.md` | Phase 0 baseline tag, root git strategy, submodule policy, and generated report/log artifact policy. |
| `pyproject.toml` | Python package metadata and dependencies. |
| `pdde/models.py` | Typed Pydantic models for inputs, component results, pipeline results, reports, and logs. |
| `pdde/cde_loader.py` | Strict CDE JSON loader. |
| `pdde/domain_pack_loader.py` | Strict domain-pack YAML loader. |
| `pdde/safety_gate_engine.py` | Deterministic explicit safety gate evaluator. |
| `pdde/prior_resolver.py` | Deterministic prior resolver with provenance and allowed-prior policy. |
| `pdde/monte_carlo_engine.py` | Seeded prior-level Monte Carlo sampler for explicit numeric priors. |
| `pdde/uncertainty_budget.py` | Explicit uncertainty-budget item evaluator. |
| `pdde/value_of_information.py` | Explicit VOI item evaluator/classifier. |
| `pdde/decision_profiler.py` | Deterministic Decision Profile assembly layer. |
| `pdde/evaluation_pipeline.py` | End-to-end orchestration of the deterministic component layers. |
| `pdde/report_renderer.py` | Deterministic advisory Markdown renderer. |
| `pdde/provenance_logger.py` | Status-only JSONL provenance record creation and writing. |
| `pdde/run_cde.py` | CLI parser and command handlers. |
| `pdde/__main__.py` | `python -m pdde` entry point. |
| `tests/` | Unit, component, CLI, provenance, report, and Phase 0 acceptance tests. |
| `reports/` | Generated example Markdown reports. |
| `logs/` | Generated appendable JSONL provenance logs. |

## Current CLI Commands

```bash
python -m pdde --help
python -m pdde validate --cde <path> --domain <path>
python -m pdde report --cde <path> --domain <path>
python -m pdde report --cde <path> --domain <path> --output <report.md>
python -m pdde report --cde <path> --domain <path> --output <report.md> --log <run.jsonl>
python -m pdde run-cde --cde <path> --domain <path> --out <report.md>
python -m pdde run-cde --cde <path> --domain <path> --out <report.md> --log <run.jsonl>
python -m pdde.run_cde --cde <path> --domain <path> --out <report.md>
```

`report` prints Markdown to stdout when `--output` is omitted. `run-cde` is the compatibility path that writes to `--out`.

## Test Summary

The current test suite contains 96 tests across 13 test files:

- models and serialization
- loaders and validate CLI behavior
- safety gates
- prior resolution
- Monte Carlo prior sampling
- uncertainty budget and VOI
- Decision Profiler
- evaluation pipeline
- Markdown report renderer
- report/run-cde CLI behavior
- provenance logger
- Phase 0 acceptance workflow

The acceptance tests verify that the public CLI and Python API work without network access, external APIs, credentials, PHI logging, hidden final recommendations, or unstable full-report snapshots.

## Generated Example Outputs

| Path | Meaning |
| --- | --- |
| `reports/hf_cde_stable_report.md` | Canonical generated advisory Decision Profile report from the `report` command. |
| `reports/hf_cde_stable_run_cde_report.md` | Compatibility report generated through the `run-cde` path. |
| `logs/hf_cde_stable.jsonl` | Appendable status-only provenance log for canonical report runs. |

The JSONL log intentionally records IDs, statuses, paths, counts, source references, package metadata, command name, iteration count, seed, and report path. It does not log full raw case text, full patient-state payloads, gate evidence strings, PHI, or simulation sample arrays.

## Known Limitations

- Phase 0 is synthetic, advisory-only, and unvalidated.
- The canonical v0.3 package includes one stable CDE fixture; variant scenarios are generated inside tests from that typed fixture.
- The domain pack is draft and uncalibrated.
- No final recommendation, safe-discharge conclusion, unsafe-discharge conclusion, top option, option ranking, or decision-fitness score is produced.
- Monte Carlo output is prior-level only; it is not mapped into per-option posteriors.
- Wrong-indication claim gates that require AI answer mapping remain unsupported in direct CDE simulation.
- Local workflow and monitoring-rescue checks remain draft/deferred unless explicit verified source data is added.
- The root workspace is a git repository on `main`; `ClinSafer/` and `Agent_Pidgeon/` are tracked as submodules.
- Generated `reports/*.md` and `logs/*.jsonl` are ignored reproducible local artifacts by default; see `BASELINE_POLICY.md`.
- `pdde/models.py` is large because Phase 0 kept typed result models centralized for consistency.

## Deferred Phase 1 Items

- `TQ-D001: AI Answer Mapping` - claim extraction, claim-to-option mapping, omission/overstatement flags, and prohibited recommendation checks.
- `TQ-D002: Local Overlay Verification` - owner/status/source/review-cadence verification for local operational rules.
- `TQ-D003: Citation/Evidence Audit` - source support checking and citation integrity.
- `TQ-D004: Calibration And Outcome Anchoring` - expert labels, calibration curves, prior drift, and outcome linkage.

## Recommended Next 5 Tasks

| Rank | Next Task | Estimated Chance Of Improving Goal | Why | Risk | Requires User Input? |
|---:|---|---:|---|---|---|
| 1 | Promote canonical synthetic variant fixtures into `examples/` | 80% | Makes low eGFR, high potassium, low SBP, no follow-up, prior DKA, and missingness cases reusable outside tests. | Low risk if labeled synthetic and derived from current fixture. | No |
| 2 | Define a normalized status-ledger model | 75% | Gives report rendering and JSONL logging one shared contract for visible unresolved statuses. | Medium abstraction risk if made too broad. | No |
| 3 | Split centralized model definitions into stable submodules | 70% | Improves maintainability before adding more schema and AI-mapping models. | Medium import/refactor risk; should be test-preserving. | No |
| 4 | Define local overlay verification metadata requirements before implementing local workflow checks | 60% | Prevents draft operational assumptions from becoming hidden clinical logic. | Low code risk; medium governance dependency. | Yes |
| 5 | Keep AI answer mapping deferred until direct-CDE fixtures and status contracts are reviewed | 45% | Protects the simulator from reverting to answer grading before its deterministic base is stable. | Medium workflow delay for AI-answer comparison use cases. | Yes |

## Stop/Go Recommendation

Go for demoing and using Phase 0 as the tagged baseline `phase0-baseline` for Phase 1 direct-CDE hardening.

Go for `P1-003: Canonical Synthetic Variant Fixtures` as the next engineering task after completed `P1-002` mapping hardening.

Stop for clinical deployment, PHI use, real patient-care use, final recommendation generation, or AI answer mapping until the corresponding deferred tasks are explicitly started and governed.
