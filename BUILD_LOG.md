# Phase 0 Build Log

Last updated: 2026-05-12

## Executive Summary

Phase 0 now has a working CLI and Python API for direct Clinical Decision Episode evaluation against the canonical v0.3 HF ED discharge fixture and domain pack. The implementation loads typed inputs, evaluates explicit deterministic safety gates, resolves allowed draft policy priors, samples only explicit resolved beta priors, preserves uncertainty and value-of-information items, assembles Decision Profile status records, renders advisory Markdown, and writes status-only JSONL provenance logs.

The build deliberately stops short of final clinical recommendation generation. The current source files do not define a validated decision-fitness formula, option utility, ranking threshold, prior-to-option weighting model, local workflow verification contract, or calibrated outcome data. The system therefore reports profile status evidence and unresolved items rather than claiming a ranked decision.

## What Was Built

- Python package scaffold under `pdde/`.
- Strict Pydantic v2 models for CDEs, domain packs, priors, safety gates, component results, evaluation results, and legacy placeholder log/profile shapes.
- JSON CDE loader and YAML domain-pack loader with clear errors.
- Deterministic hard-gate evaluator for explicit v0.3 gate groups.
- Deterministic prior resolver that admits only allowed Phase 0 provenance classes and blocks LLM-unverified active priors.
- Seeded Monte Carlo sampler over explicit resolved beta priors only.
- Item-level uncertainty-budget evaluator.
- Item-level value-of-information evaluator.
- Deterministic Decision Profiler assembly layer.
- End-to-end evaluation pipeline that preserves every component output.
- Markdown report renderer for `EvaluationPipelineResult`.
- CLI commands for help, validation, report generation, output-file writing, and provenance log writing.
- JSONL provenance logger for run metadata, component status summaries, safety gates, prior resolutions, Monte Carlo priors, uncertainty items, VOI items, and Decision Profiles.
- Focused unit/integration/acceptance tests.
- Generated canonical report and log artifacts.

## Current Architecture

The current architecture is a simple synchronous CLI pipeline:

```text
CLI
  -> strict CDE loader
  -> strict domain-pack loader
  -> safety gate engine
  -> prior resolver
  -> Monte Carlo prior sampler
  -> value-of-information evaluator
  -> uncertainty-budget evaluator
  -> Decision Profiler assembler
  -> Markdown renderer
  -> JSONL provenance logger
```

The central data contract is `EvaluationPipelineResult`. It carries the loaded CDE/domain pack plus all component outputs. Reporting and logging consume that typed object and should not recalculate clinical meaning.

## Module Responsibility Map

| Module | Responsibility | Notes |
|---|---|---|
| `pdde/__main__.py` | top-level module entry point | delegates to `run_cde.main` |
| `pdde/run_cde.py` | argparse CLI | implements `validate`, `report`, `run-cde`, output writing, and optional log writing |
| `pdde/models.py` | typed data contracts | intentionally broad; includes active component result models and earlier planned profile/log shapes |
| `pdde/cde_loader.py` | CDE JSON load/validation | returns `ClinicalDecisionEpisode`; no clinical logic |
| `pdde/domain_pack_loader.py` | domain-pack YAML load/validation | returns `DomainPack`; no normalization of v0.1 artifacts |
| `pdde/loader_errors.py` | loader exception and validation summary | gives concise user-facing errors |
| `pdde/safety_gate_engine.py` | deterministic explicit hard-gate evaluation | evaluates configured v0.3 gate groups; claim-type gates remain unsupported until AI mapping |
| `pdde/prior_resolver.py` | deterministic prior lookup/admission | resolves only `domain_pack.prior_policy`; blocks LLM-unverified active priors |
| `pdde/monte_carlo_engine.py` | seeded prior-level beta sampling | samples only resolved priors; no option posterior synthesis |
| `pdde/value_of_information.py` | explicit VOI item status evaluation | no numeric expected-value formula |
| `pdde/uncertainty_budget.py` | uncertainty-category status evaluation | no hidden weights or numeric attribution |
| `pdde/decision_profiler.py` | profile evidence assembly | combines component statuses; no final category/rank/utility formula |
| `pdde/evaluation_pipeline.py` | deterministic orchestrator | wires loaders and component modules into `EvaluationPipelineResult` |
| `pdde/report_renderer.py` | deterministic Markdown rendering | displays component outputs and deferrals |
| `pdde/provenance_logger.py` | JSONL status log creation/writing | avoids raw case text, patient-state values, and simulation samples |

## CLI Commands

These commands are implemented:

```bash
python -m pdde --help
python -m pdde validate --cde <cde.json> --domain <domain_pack.yaml>
python -m pdde report --cde <cde.json> --domain <domain_pack.yaml>
python -m pdde report --cde <cde.json> --domain <domain_pack.yaml> --output <report.md>
python -m pdde report --cde <cde.json> --domain <domain_pack.yaml> --output <report.md> --log <run.jsonl>
python -m pdde run-cde --cde <cde.json> --domain <domain_pack.yaml> --out <report.md>
python -m pdde.run_cde --cde <cde.json> --domain <domain_pack.yaml> --out <report.md>
```

Canonical fixture command:

```bash
python -m pdde report \
  --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json \
  --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml \
  --output reports/hf_cde_stable_report.md \
  --log logs/hf_cde_stable.jsonl \
  --iterations 5 \
  --seed 17
```

## Test And Verification Summary

The test suite currently has 13 test files and 103 collected pytest cases. It covers:

- CLI help.
- CDE/domain-pack loading and validation errors.
- data-model validation and serialization.
- deterministic safety gates.
- prior resolution and provenance admission.
- seeded Monte Carlo reproducibility and non-sampling of missing/blocked/unsupported priors.
- uncertainty-budget and VOI item evaluation.
- Decision Profiler assembly.
- end-to-end evaluation pipeline.
- Markdown report rendering.
- CLI report/output/log behavior.
- provenance JSONL serialization and privacy guardrails.
- Phase 0 acceptance paths across CLI, Python API, and scenario variants.

Acceptance tests now cover stable, low eGFR, high potassium, low SBP, no follow-up, prior DKA, and missing-labs/missing-oxygen behavior through root `examples/*.json` fixtures. The fixtures remain synthetic, non-PHI, and derived from the canonical v0.3 stable CDE shape.

## Generated Artifacts

| Artifact | Current Role | Notes |
|---|---|---|
| `reports/hf_cde_stable_report.md` | canonical generated Markdown report | 194 lines at inspection; advisory report, not clinical recommendation |
| `reports/hf_cde_stable_run_cde_report.md` | compatibility command generated report | produced through `run-cde`/legacy pathway |
| `logs/hf_cde_stable.jsonl` | appendable provenance JSONL log | record count grows with each canonical log command |

Generated `reports/*.md` and `logs/*.jsonl` are ignored by git by default and should be regenerated or explicitly archived as needed. The durable policy is in `BASELINE_POLICY.md`.

The report currently displays raw synthetic case text and patient-state values, which is appropriate for the human-facing synthetic report. The provenance log intentionally does not include full raw case text, patient preference text, patient-state value evidence strings, or simulation sample arrays.

## Safety And Privacy Guardrails

Working guardrails:

- Phase 0 output states advisory-only, uncalibrated, and not clinically validated.
- Reports say they are not final clinical recommendations.
- No single truth score, trust score, final recommendation, or ranked clinical conclusion is generated.
- Deterministic safety gates run before profile assembly and are not overridden by Monte Carlo summaries.
- Missing inputs become visible `missing`, `active`, or actionable VOI/uncertainty items.
- Unsupported gate groups and claim-type gates fail visibly as `unsupported`.
- LLM-unverified priors and low-unverified confidence priors are blocked from active direct simulation.
- Monte Carlo only samples explicit resolved beta priors and preserves source traceability.
- JSONL logs preserve statuses and provenance references without storing raw clinical payloads.
- Tests remove common API-key environment variables and block socket access for the Python API acceptance path.

## Current Limitations

- The controlling v0.3 source package still has one stable CDE fixture, but root `examples/` now provides inspectable synthetic variant fixtures for review and tests.
- The canonical domain pack is draft, uncalibrated, and has `clinical_owner: pending`.
- No local overlay rules have verified owners, sources, review cadence, or operational approval.
- `wrong_indication_blocks` require mapped claim types and are unsupported in direct CDE mode until AI answer mapping exists.
- Monte Carlo is prior-level only. It does not compute option-level posteriors, ranked options, category probabilities, median fitness, or decision-fitness intervals.
- VOI is item-level and source-order based. It does not compute numeric expected value of information.
- Uncertainty budget is category/status based. It does not compute numeric contribution weights.
- The report renderer is deterministic but hand-built; there is no template layer or report schema contract.
- The root workspace is a git repository on `main`; `ClinSafer/` and `Agent_Pidgeon/` are supporting codebases tracked as submodules.
- The Phase 0 stable baseline is tagged as `phase0-baseline`.
- `pdde/models.py` contains both active current result models and older planned/placeholder classes, which is understandable for Phase 0 but will become harder to maintain if the package grows.

## Structural Review

The current module split is coherent for Phase 0. The strongest design choice is that engines return typed component-specific records, and the pipeline preserves rather than collapses them. This makes missing, unsupported, blocked, and deferred states visible in both reports and logs.

Structural concerns:

- `pdde/models.py` is the main gravity well. It holds input models, active result models, legacy/planned output models, and log placeholders. This is manageable now but may obscure which models are actually used by the current pipeline.
- P1-002 moved hard-gate target routing into explicit domain-pack `mappings.safety_gate_targets`. Missing mappings now surface as unsupported instead of falling back to Python routing.
- P1-002 moved prior-to-option association into explicit domain-pack `mappings.prior_to_options`. The Decision Profiler no longer uses token overlap between option IDs and prior IDs.
- Report section generation is deterministic and readable, but section names and ordering are encoded directly in Python. A report contract test exists; a report schema or section registry may help later.
- Generated outputs are append-only/manual artifacts. They are useful for verification, but they are ignored source artifacts by default under `BASELINE_POLICY.md`.
- Root `examples/` now contains runnable synthetic CDE variants derived from the v0.3 source fixture; the active domain pack still lives under `pdde_v0_3_first_principles_final/`.

No serious defect requiring a code change was found in this review.

## First-Principles Review

Actual goal: help a user inspect a clinical decision episode under explicit assumptions, hard stops, draft priors, missing data, local execution constraints, and calibration status. The tool should expose defensibility structure, not replace clinician judgment or grade an AI answer as the primary workflow.

Simplest architecture that supports the goal:

1. Load one CDE and one domain pack.
2. Validate them strictly.
3. Evaluate deterministic safety gates.
4. Resolve only explicitly governed priors.
5. Simulate only what is explicitly numeric and allowed.
6. Surface missing/unsupported/deferred items.
7. Render a readable advisory report and audit log.

The current architecture matches that simple shape. The most important future simplification is to move more domain wiring into explicit domain-pack fields instead of expanding Python heuristics.

Assumptions that might be wrong:

- That v0.3's current domain-pack shape is enough to support multiple domains.
- That prior-level Monte Carlo output will remain useful if option-level formulas are absent.
- That source-order VOI ranking is good enough for users once more cases are added.
- That a Markdown-only report can stay readable as component outputs grow.
- That appending logs to a single JSONL file is enough for calibration/audit workflows.
- That synthetic fixture variants can reveal the same ontology issues as real retrospective cases.

What should not be added yet:

- final clinical recommendations.
- option ranking or median-fitness claims.
- hidden scoring formulas.
- LLM judgment or AI answer mapping.
- EHR integration, deployment, API service, UI, authentication, or database logging.
- new clinical thresholds or weights not present in controlled source files.

## Alien-Goggles Review

Weird or overlooked alternatives that might simplify the system:

- Treat the report as a direct projection of a status ledger instead of a narrative artifact. If every component emits a normalized `component`, `id`, `status`, `reason`, `source` row, reporting, logging, and testing become simpler.
- Make the domain pack the rule router. Instead of Python knowing `mra_blocks -> discharge_add_mra`, the domain pack could carry `target_option` and `match_status` fields for each gate.
- Create canonical variant fixtures by transforming the stable CDE with a tiny fixture-builder command, not by hand-maintaining many near-duplicate JSON files.
- Move report sections to a small data-driven registry so tests can assert the registry and renderer agree.
- Use provenance records as the calibration seed artifact and derive run summaries from logs, rather than building separate report and log summary concepts.
- Keep the current CLI and skip UI/API until at least one manually reviewed retrospective case exposes a real workflow need.

## Ranked Improvement Opportunities

| Rank | Improvement | Estimated Chance Of Improving Goal | Why | Risk | Recommended Timing |
|---:|---|---:|---|---|---|
| 1 | Define a normalized status-ledger model consumed by both report rendering and JSONL logging | 70% | Reduces duplication between report/log summaries and clarifies unresolved states | Could over-abstract if done before more examples exist | Next Phase 1 task |
| 2 | Split `pdde/models.py` into input, component result, pipeline, and legacy/planned model modules | 70% | Improves maintainability as model count grows | Refactor can cause import churn without behavior gain | After status ledger exists or before AI mapping |
| 3 | Add a report section registry or schema contract | 60% | Keeps section ordering and required advisory language explicit | Adds minor framework around a simple renderer | Before report format becomes externally shared |
| 4 | Add local overlay verification schema and fixture placeholders | 50% | Moves local workflow uncertainty from prose to structured data | Requires external owner/status input to be meaningful | After local review input is available |
| 5 | Keep AI answer mapping deferred | 45% | Protects the CDE-first architecture from reverting to answer grading | Delays Workflow A compatibility | Continue until direct simulation has reviewed fixtures |
| 6 | Document generated-artifact and root-git policy | 55% | Avoids confusion about append-only logs, generated reports, and nested repositories | Completed as `BASELINE_POLICY.md` with `phase0-baseline` tag | Completed in P1-001 |
| 7 | Add explicit prior-to-option and gate-target mappings to the domain-pack schema | 85% | Removed token-overlap and hard-coded gate routing | Completed with mapping provenance in reports/logs | Completed in P1-002 |
| 8 | Create canonical synthetic CDE fixture files under `examples/` for stable and variant cases | 80% | Makes CLI demos and acceptance coverage easier for users to inspect | Completed with synthetic/non-PHI provenance labels | Completed in P1-003 |

## Recommended Next Step

Proceed with direct-CDE hardening before new clinical logic:

1. Keep `BUILD_LOG.md` as the Phase 0 review artifact.
2. Use `BASELINE_POLICY.md` and tag `phase0-baseline` as the Phase 0 baseline/artifact policy.
3. Use root `examples/*.json` fixtures for scenario review and acceptance coverage.
4. Keep generated reports/logs reproducible and ignored unless an explicit archive/release task says otherwise.

The highest-value next engineering step is `P1-004: Normalized Status Ledger`, because the project now has explicit mappings and inspectable fixtures, so shared status projection can reduce report/log duplication without adding unsupported clinical claims.
