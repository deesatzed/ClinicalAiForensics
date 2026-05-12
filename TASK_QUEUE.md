# Task Queue

Initialized: 2026-05-11

## Queue Rules

- Work tasks in order unless a task is explicitly reprioritized in `DECISIONS.md`.
- Do not begin AI answer mapping until direct CDE simulation is accepted.
- Update `PROGRESS.md` after each completed task.
- Update `DECISIONS.md` for scope, architecture, dependency, data model, security, privacy, UI/UX, or deployment decisions.

## Current Phase

Phase 0: CLI Clinical Decision Episode simulator.

## Tasks

### TQ-000: Initialize Project-Control Files

Status: done

Acceptance:

- Root `GOAL.md`, `STANDARDS.md`, `IMPLEMENT.md`, `DECISIONS.md`, `PROGRESS.md`, and `TASK_QUEUE.md` exist.
- No code implemented.
- Source review summarized.

### TQ-000A: Repository Recon And Map

Status: done

Scope:

- Inspect root workspace and supporting folders without implementing code.
- Identify build-direction files, supporting examples, reusable codebase patterns, likely architecture, first build task, and risks.
- Create `REPO_MAP.md`.
- Update `PROGRESS.md` and `TASK_QUEUE.md`.

Acceptance:

- `REPO_MAP.md` exists.
- `REPO_MAP.md` distinguishes controlling v0.3 build directions from older PDDE specs and supporting codebases.
- `PROGRESS.md` records recon findings and verification.
- No code implemented.

### TQ-001: Project Setup And Source Normalization

Status: done

Scope:

- Decide whether to initialize root git repository.
- Create `pyproject.toml`.
- Create `pdde/` package skeleton.
- Create test skeleton.
- Decide where canonical `domain_pack.yaml`, CDE examples, and reports will live.
- Use `REPO_MAP.md` to keep build-direction sources, support examples, and reusable codebase patterns separated.
- Reconcile the v0.3 domain pack with the richer v0.1 YAML at the fixture/schema boundary, not by implementing clinical logic.
- Add CLI help stub only.

Acceptance:

- `python -m pdde --help` exits successfully.
- Project structure matches `IMPLEMENT.md` or deviations are documented in `DECISIONS.md`.
- No clinical simulation logic implemented yet.

Verification:

- Root git initialization was deferred and documented in `DECISIONS.md`.
- `pyproject.toml`, `.gitignore`, `pdde/`, `tests/`, `domain_packs/`, `examples/`, `reports/`, and `logs/` scaffold were created.
- `python -m pdde --help` passed.
- `python -m pytest tests/test_cli_help.py` passed.
- No clinical simulation logic was implemented.

### TQ-002: Data Models

Status: done

Scope:

- Implement Pydantic models for CDE, domain pack, priors, hard gates, local overlay rules, decision profiles, uncertainty budget, value-of-information, and log records.

Acceptance:

- Priors without provenance fail validation.
- local rules without owner/status fail validation.
- Stable CDE and HF domain pack can validate.

Verification:

- `ClinicalDecisionEpisode` validates `pdde_v0_3_first_principles_final/examples/hf_cde_stable.json`.
- `DomainPack` validates `pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml`.
- Prior provenance and low-confidence warning validation are covered by tests.
- Local overlay owner/status and verified metadata validation are covered by tests.
- Decision Profile serialization and interval validation are covered by tests.
- Run/prior/prediction log record serialization is covered by tests.
- `python -m pytest` passed, 8 tests.
- No clinical reasoning logic was implemented.

### TQ-003: CDE And Domain-Pack Loaders

Status: done

Scope:

- Implement JSON/YAML loaders using structured parsers.
- Produce clear validation errors.

Acceptance:

- Stable CDE fixture loads.
- HF domain pack fixture loads.
- Invalid files exit non-zero through `validate`.

Verification:

- `load_cde` loads `pdde_v0_3_first_principles_final/examples/hf_cde_stable.json` into a typed `ClinicalDecisionEpisode`.
- `load_domain_pack` loads `pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml` into a typed `DomainPack`.
- Loader tests cover malformed JSON, invalid CDE shape, invalid domain-pack shape, and missing domain-pack files.
- CLI `validate` tests cover success, invalid-file non-zero exit, and missing-input non-zero exit.
- `python -m pytest` passed, 17 tests.
- `python -m py_compile` on all `pdde/` modules passed.
- `python -m pdde --help` passed.
- `python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml` passed.

### TQ-004: Deterministic Safety Gate Engine

Status: done

Scope:

- Implement hard-stop evaluation for HF ED discharge domain pack.
- Return explicit hard-stop records per option.

Acceptance:

- Low SBP triggers admit/observe/escalate pressure.
- High K blocks or marks MRA unsafe.
- Low eGFR lowers or blocks SGLT2/MRA as configured.
- Prior DKA blocks or discourages SGLT2.
- Hard stops cannot be overridden by simulation.

Verification:

- `SafetyGateEvaluation` and `SafetyGateEvaluationSet` provide typed safety-gate result records.
- Stable v0.3 CDE passes explicit SBP and potassium hard gates.
- High potassium blocks `discharge_add_mra`.
- Low SBP triggers `admit_or_observe` pressure.
- Low eGFR blocks `discharge_add_sglt2` and `discharge_add_mra`.
- Prior euglycemic DKA blocks the SGLT2 DKA gate.
- Missing gate inputs return `missing`.
- Malformed gate inputs return `unsupported`.
- Wrong-indication claim-type gates and unknown hard-gate groups return `unsupported` rather than silently passing.
- `python -m pytest` passed, 26 tests.
- `python -m py_compile` on all `pdde/` modules passed.
- `python -m pdde --help` passed.
- `python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml` passed.

### TQ-005: Prior Resolver

Status: done

Scope:

- Resolve allowed Phase 0 priors.
- Normalize v0.3 and compatible v0.1 provenance labels where needed.
- Reject or quarantine LLM-unverified priors in direct-simulation mode.

Acceptance:

- Every active prior has provenance and calibration status.
- LLM-unverified priors cannot silently enter direct simulation.

Verification:

- `PriorResolution` and `PriorResolutionSet` provide typed prior-resolution result records.
- Canonical v0.3 domain-pack priors resolve with distribution, parameters, provenance, normalized provenance, warnings, calibration status, and source traceability.
- Requested missing priors return `missing` and do not create defaults.
- Empty prior policies do not invent requested priors.
- Malformed prior definitions return `unsupported` with validation details.
- Unsupported provenance classes return `unsupported`.
- LLM-unverified priors return `blocked` and never appear in active priors.
- Compatible v0.1 labels `guideline_mapped` and `panel_elicited_pending` normalize for Phase 0 direct simulation.
- `python -m pytest` passed, 33 tests.
- `python -m py_compile` on all `pdde/` modules passed.
- `python -m pdde --help` passed.
- `python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml` passed.

### TQ-006: Monte Carlo Engine

Status: done

Scope:

- Implement vectorized NumPy sampling for explicit resolved priors.
- Preserve prior-level provenance and simulation status.
- Defer option posterior synthesis until explicit prior-to-option mapping and decision-profile combination are implemented.

Acceptance:

- Seeded runs are reproducible.
- 10,000 iterations complete within budget.
- Stable case resolved priors return reproducible sampled summaries.

Acceptance note:

- TQ-006 was completed as the smallest safe Monte Carlo boundary over explicit resolved priors. Per-option posterior synthesis is deferred to TQ-008 because the current v0.3 domain pack does not explicitly map every prior to every decision option or define a complete decision-fitness formula.

Verification:

- `MonteCarloPriorSimulation` and `MonteCarloSimulationResult` provide typed simulation result records.
- Canonical v0.3 resolved beta priors sample successfully with source, parameters, provenance, confidence, warnings, calibration status, and summary statistics preserved.
- Fixed seeds produce identical samples and summary statistics.
- The default run samples 10,000 values for each resolved canonical prior.
- Missing requested priors return `missing` and do not produce samples or summary statistics.
- Empty prior policies do not invent requested prior values.
- Unsupported provenance and malformed prior definitions return `unsupported` and do not produce samples.
- LLM-unverified priors return `blocked` and do not produce samples.
- Simulation results serialize through Pydantic.
- `python -m pytest` passed, 42 tests.
- `python -m py_compile` on all `pdde/` modules passed.
- `python -m pdde --help` passed.
- `python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml` passed.

### TQ-007: Uncertainty Budget And Value Of Information

Status: done

Scope:

- Generate explicit uncertainty-budget category evaluations.
- Evaluate explicit domain-pack value-of-information variables.
- Preserve missing, unsupported, malformed, and deferred items.

Acceptance:

- Missing variables become actionable VOI items.
- Missing eGFR/potassium rank high by explicit domain-pack order.
- Every uncertainty-budget category is present as a typed item.

Acceptance note:

- TQ-007 was completed as the smallest safe uncertainty/VOI boundary. Numeric uncertainty weights, expected value-of-information math, and sensitivity-derived rankings are deferred because the current v0.3 domain pack does not define those formulas.

Verification:

- `UncertaintyBudgetEvaluationItem` and `UncertaintyBudgetEvaluationSet` provide typed uncertainty-budget records.
- `ValueOfInformationEvaluation` and `ValueOfInformationEvaluationSet` provide typed VOI records.
- The seven v0.3 uncertainty-budget categories are returned.
- Canonical v0.3 VOI variables are returned in source order with source-field traceability.
- Missing eGFR and potassium become actionable VOI items and feed patient-context uncertainty.
- Unsupported or malformed VOI definitions stay visible as `unsupported`.
- Empty VOI definitions return a visible `deferred` placeholder.
- Deferred monitoring/rescue and harm uncertainty stay visible when numeric definitions are absent.
- Tests prove the evaluator does not invent thresholds or numeric VOI values.
- Result model serialization is covered.
- `python -m pytest` passed, 49 tests.
- `python -m py_compile` on all `pdde/` modules passed.
- `python -m pdde --help` passed.
- `python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml` passed.

### TQ-008: Decision Profiler

Status: done

Scope:

- Combine gates, simulation, priors, uncertainty budget, and value-of-information into Decision Profiles.

Acceptance:

- Stable explicit discharge profiles assemble without active blockers.
- Direct gate blockers, triggers, missing inputs, and unsupported inputs determine transparent profile status.
- Uncertainty-budget and VOI items remain visible.
- No final recommendation, rank, median fitness, uncertainty interval, or hidden scoring formula is invented.

Acceptance note:

- TQ-008 was completed as the smallest safe Decision Profiler boundary. The current v0.3 source files do not define complete decision-fitness formulas, option-ranking thresholds, or prior-to-option weighting models, so numeric ranking and final categories remain deferred.

Verification:

- `DecisionProfileInputSummary`, `DecisionProfileEvaluation`, and `DecisionProfileEvaluationSet` provide typed Decision Profiler result records.
- Stable SGLT2 profile is `eligible` from explicit safety-gate definitions and carries related prior/simulation provenance.
- High potassium makes `discharge_add_mra` `blocked`.
- Missing potassium makes `discharge_add_mra` `missing`.
- Malformed decision-option definitions remain `unsupported` and visible.
- Deferred uncertainty-budget and VOI items remain visible in profiles and input summaries.
- Tests prove no final recommendation, rank, category, median fitness, or uncertainty interval is invented.
- `python -m pytest` passed, 56 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- `python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml` passed.

### TQ-009: Evaluation Pipeline

Status: done

Scope:

- Wire the existing deterministic components into one typed direct CDE evaluation pipeline.
- Load CDE and domain pack through strict loaders.
- Run safety gates, prior resolution, Monte Carlo prior sampling, VOI, uncertainty budget, and Decision Profiler assembly.
- Preserve every component output and status visibly.

Acceptance:

- Canonical v0.3 fixtures run end-to-end through the pipeline.
- Component outputs are preserved in the final typed result.
- Blocked, missing, unsupported, malformed, and deferred statuses remain visible.
- No final recommendation, rank, median fitness, uncertainty interval, or hidden scoring formula is invented.

Acceptance note:

- TQ-009 was completed as the smallest useful API-level evaluation pipeline. Markdown report rendering remains deferred because the current task explicitly prohibited narrative report generation.

Verification:

- `EvaluationPipelineResult` provides a typed top-level result record.
- `pdde/evaluation_pipeline.py` exposes `run_evaluation_pipeline(...)` for file paths and `evaluate_cde(...)` for typed inputs.
- Canonical v0.3 CDE/domain-pack fixtures run through the full component chain.
- Safety gate, prior, simulation, VOI, uncertainty-budget, and Decision Profiler outputs are preserved.
- High potassium remains visible as an MRA blocker.
- Missing potassium remains visible as missing gate input and missing VOI.
- Deferred uncertainty-budget and Decision Profiler inputs remain visible.
- Tests prove no final recommendation, rank, category, median fitness, or uncertainty interval is invented.
- `python -m pytest` passed, 61 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- `python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml` passed.

### TQ-010: Markdown Report Renderer

Status: done

Scope:

- Render advisory-only Markdown Decision Profile report from `EvaluationPipelineResult`.

Acceptance:

- All required report sections appear.
- Draft priors and draft local overlays are visible.
- The report avoids clinical validation or outcome claims.
- Unsupported/deferred inputs remain visible and are not converted into recommendations.

Acceptance note:

- TQ-010 was completed as an API-level renderer. CLI report writing is deferred to TQ-011 so `validate` remains unchanged and report generation can be wired deliberately.

Verification:

- `pdde/report_renderer.py` exposes `render_markdown_report(...)`.
- Canonical v0.3 pipeline results render to deterministic Markdown.
- Major report sections are present.
- Draft priors, local overlay status, calibration status, source references, and unresolved items remain visible.
- Blocked, missing, unsupported, and deferred statuses remain visible.
- Tests prove no final clinical conclusion, ranked option table, category probabilities, synthetic fitness language, or recommendation wording is invented.
- `python -m pytest` passed, 66 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- `python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml` passed.

### TQ-011: CLI Run And Validate Commands

Status: done

Scope:

- Wire loaders, gates, priors, simulation, profile generation, report rendering, and logs into CLI.

Acceptance:

- `python -m pdde.run_cde --cde examples/hf_cde_stable.json --domain domain_packs/hf_ed_discharge/domain_pack.yaml --out reports/hf_cde_stable_report.md` writes a report.
- `validate` checks CDE and domain pack.
- Errors are clear and non-zero.

Acceptance note:

- TQ-011 wires loaders, deterministic evaluation, and Markdown report rendering into the CLI. JSONL-compatible logs remain deferred to TQ-012, so the CLI does not yet create run/prior/profile audit records.

Verification:

- `python -m pdde --help` lists `run-cde`, `report`, and `validate`.
- `python -m pdde validate --cde <path> --domain <path>` remains functional.
- `python -m pdde report --cde <path> --domain <path>` prints Markdown to stdout.
- `python -m pdde report --cde <path> --domain <path> --output <path>` writes Markdown to the explicit path.
- `python -m pdde run-cde --cde <path> --domain <path> --out <path>` writes Markdown through the existing command name.
- `python -m pdde.run_cde --cde <path> --domain <path> --out <path>` is supported for compatibility with the implementation-plan command shape.
- CLI tests cover help, validate success, validate failure, report stdout, report output file, `run-cde` output file, legacy module arguments, invalid paths, malformed CDE files, invalid iteration counts, and no invented final-recommendation language.
- `python -m pytest` passed, 74 tests.
- `python -m py_compile pdde/*.py` passed.
- fixture `validate`, `report`, and `pdde.run_cde` commands passed.
- generated report files were verified in `reports/`.

### TQ-012: Provenance Logging

Status: done

Scope:

- Add JSONL-compatible run, prior, and prediction logs.

Acceptance:

- Each run creates run metadata.
- Each prior used is logged.
- Each option profile is logged.

Acceptance note:

- TQ-012 logs current Decision Profile status records rather than legacy prediction categories, because TQ-008 intentionally does not synthesize final recommendation categories or decision-fitness intervals.

Verification:

- `pdde/provenance_logger.py` creates JSONL-ready provenance records from `EvaluationPipelineResult`.
- run metadata includes command name, package version, input paths, loaded IDs, report path when applicable, seed, iteration count, component counts, status summaries, and provenance references.
- prior-resolution records are logged.
- Decision Profile status records are logged.
- safety gate, Monte Carlo, uncertainty-budget, and VOI statuses are logged.
- timestamp and run ID injection support deterministic tests.
- JSONL write and append behavior are covered.
- logs exclude full raw case text, patient preference text, patient-state value evidence strings, and simulation sample arrays.
- `report --log <path>` and `run-cde --log <path>` write provenance logs without changing existing report/validate behavior.
- `python -m pytest` passed, 82 tests.
- `python -m py_compile pdde/*.py` passed.
- canonical `validate`, `report`, and `report --log logs/hf_cde_stable.jsonl` commands passed.
- `logs/hf_cde_stable.jsonl` exists and parses as JSONL.

### TQ-013: Phase 0 Acceptance Tests

Status: done

Scope:

- Implement automated unit, hard-stop, missingness, metamorphic, report, and CLI tests.

Acceptance:

- Stable, low eGFR, high K, low SBP, no follow-up, prior DKA, and missing labs fixtures are covered.
- All automated Phase 0 tests pass.

Acceptance note:

- TQ-013 adds acceptance-level coverage over the current public CLI and Python API boundaries. The v0.3 package currently provides one canonical stable CDE fixture, so low eGFR, high potassium, low SBP, no follow-up, prior DKA, and missing-labs scenarios are covered by deterministic typed CDE variants derived from that fixture rather than by introducing new domain-pack formats or clinical assumptions.

Verification:

- `tests/test_phase0_acceptance.py` covers CLI help, canonical validation, report stdout, report output file writing, provenance JSONL writing/parsing, Python API load/pipeline/render/provenance calls, advisory report sections, no invented final recommendation text, visible unresolved statuses, status-only provenance records, and no network/API-key dependence.
- `python -m pytest tests/test_phase0_acceptance.py` passed, 9 tests.
- `python -m pytest` passed, 91 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate`, `report`, and `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` commands passed.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL.

### TQ-014: Build Log And Manual Structural Review

Status: done

Scope:

- Create `BUILD_LOG.md`.
- Document ontology problems, spec conflicts, assumptions, failed adversarial cases, and Phase 1 recommendations.
- Record manual report-structure review.

Acceptance:

- `BUILD_LOG.md` gives a clear path from Phase 0 to Phase 1.

Acceptance note:

- `BUILD_LOG.md` was created as a documentation-only Phase 0 build log and manual structural review. No runtime behavior, clinical logic, CLI behavior, or report semantics were changed.

Verification:

- `BUILD_LOG.md` includes executive summary, what was built, architecture, module map, CLI commands, test/verification summary, generated artifacts, safety/privacy guardrails, limitations, structural review, first-principles review, alien-goggles review, ranked improvements, and recommended next step.
- `python -m pytest` passed, 91 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate`, `report`, and `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` commands passed.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL.

### TQ-015: Phase 0 Handoff Package

Status: done

Scope:

- Create `PHASE0_HANDOFF.md`.
- Summarize Phase 0 current status, working commands, main files, tests, generated outputs, limitations, deferred Phase 1 items, next tasks, and stop/go recommendation.
- Do not implement runtime behavior, clinical logic, or Phase 1 work.

Acceptance:

- `PHASE0_HANDOFF.md` exists and includes exact setup, test, validate, report, report-output, and provenance-log commands.
- Handoff identifies that Phase 0 is ready to tag/archive/demo as a local synthetic advisory prototype.
- Handoff states that clinical deployment, PHI use, final recommendation generation, and AI answer mapping remain out of scope.
- Project-control files record handoff completion.

Verification:

- `python -m pytest` passed, 91 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate`, `report`, and `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` commands passed.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL and contained 195 records after the verification append.

## Queue State

No non-deferred Phase 0 implementation task remains in this queue. Phase 0 handoff is complete. Next work should be explicitly selected from deferred Phase 1 items or from the ranked improvement opportunities in `BUILD_LOG.md` and `PHASE0_HANDOFF.md`.

## Deferred

### TQ-D001: AI Answer Mapping

Status: deferred

Scope:

- Claim extraction from AI answers.
- Claim-to-option mapping.
- Omission and overstatement flags.
- Prohibited recommendation checks.

Reason Deferred:

- v0.3 requires direct CDE simulation to work first.

### TQ-D002: Local Overlay Verification

Status: deferred

Scope:

- Replace draft Temple local overlay placeholders with owner/status/source/review-cadence verified rules.

Reason Deferred:

- Requires local operational review outside code implementation.

### TQ-D003: Citation/Evidence Audit

Status: deferred

Scope:

- Source support checking and citation integrity.

Reason Deferred:

- Explicitly Phase 3 in v0.3.

### TQ-D004: Calibration And Outcome Anchoring

Status: deferred

Scope:

- Expert labels, calibration curves, prior drift, outcome linkage.

Reason Deferred:

- Requires governance, labels, and outcome data beyond Phase 0.
