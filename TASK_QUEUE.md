# Task Queue

Initialized: 2026-05-11

## Queue Rules

- Work tasks in order unless a task is explicitly reprioritized in `DECISIONS.md`.
- Do not begin AI answer mapping until direct CDE simulation is accepted.
- Update `PROGRESS.md` after each completed task.
- Update `DECISIONS.md` for scope, architecture, dependency, data model, security, privacy, UI/UX, or deployment decisions.

## Current Phase

Phase 2: governance-contract hardening. Phase 0 is the stable baseline tagged as `phase0-baseline`; Phase 1 is the stable baseline tagged as `phase1-baseline`.

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

## Phase 1 Tasks

### P1-001: Phase 0 Baseline And Artifact Policy

Status: done

Scope:

- Document root version-control strategy.
- Document nested `ClinSafer/` and `Agent_Pidgeon/` handling.
- Document generated report/log policy.
- Create a Phase 0 baseline identifier.
- Keep `PHASE0_HANDOFF.md`, `BUILD_LOG.md`, `README.md`, and `DEMO.md` accurate.
- Do not change runtime behavior.

Acceptance:

- Root version-control strategy is documented.
- Nested repository handling is documented.
- Generated report/log policy is documented, including whether `reports/*.md` and `logs/*.jsonl` are committed, regenerated, ignored, or archived.
- Phase 0 baseline identifier exists.
- Phase 0 reviewer and handoff docs remain accurate.
- Verification passes.

Verification:

- `BASELINE_POLICY.md` documents root git strategy, submodule handling, generated artifact policy, and Phase 1 boundary guardrails.
- Annotated git tag `phase0-baseline` points to Phase 0 baseline commit `0662777`.
- Tag `phase0-baseline` was pushed to `origin`.
- `PHASE0_HANDOFF.md`, `BUILD_LOG.md`, `README.md`, and `DEMO.md` were refreshed for root git, submodule, and generated-artifact policy accuracy.
- No runtime behavior, clinical logic, tests, CLI behavior, report semantics, or AI/LLM mapping was added.
- `python -m pytest` passed, 91 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate` passed.
- canonical `report` to stdout passed.
- canonical `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` passed.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL and contained 312 records after the final verification append.

### P1-002: Explicit Domain-Pack Mappings

Status: done

Scope:

- Add explicit domain-pack fields for safety-gate target option IDs and prior-to-option mappings.
- Remove reliance on Python-only gate routing where source data should carry routing semantics.
- Remove token-overlap prior/profile association from the Decision Profiler.
- Preserve existing canonical fixture behavior except for improved mapping visibility.
- Do not add clinical thresholds, utilities, final recommendations, hidden scores, or LLM/AI judgment.

Acceptance:

- Domain-pack models and loaders validate mapping targets clearly.
- Safety gate evaluation and Decision Profiler use explicit source mappings where available.
- Tests prove malformed mappings fail clearly and prior/profile association no longer depends on token overlap.
- Reports and logs preserve mapping provenance.

Verification:

- `DomainPackMappings`, `SafetyGateTargetMapping`, and `PriorToOptionMapping` provide typed explicit mapping contracts.
- The canonical HF domain pack defines `mappings.safety_gate_targets` and `mappings.prior_to_options`.
- Domain-pack model validation rejects mappings to unknown gate groups, decision options, or priors.
- The safety gate engine uses explicit gate-target mappings and marks missing mappings unsupported without Python fallback.
- The Decision Profiler uses explicit prior-to-option mappings and no longer uses token-overlap association.
- Reports and JSONL logs preserve mapping source/provenance references.
- Tests cover successful mappings, missing mappings, malformed mappings, no fuzzy/invented prior/profile mapping, Phase 0 fixture compatibility, and serialization through existing result models.
- `python -m pytest` passed, 96 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate` passed.
- canonical `report` to stdout passed.
- canonical `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` passed.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL and contained 390 records after the final verification append.

### P1-003: Canonical Synthetic Variant Fixtures

Status: done

Scope:

- Promote inspectable synthetic CDE variants into `examples/` or another documented canonical fixture directory.
- Initial variants should cover stable, low eGFR, high potassium, low SBP, no follow-up, prior DKA, and missing labs/missing oxygen requirement.
- Label every fixture synthetic and non-PHI.

Acceptance:

- Fixtures validate through the public loaders/CLI.
- Expected status changes are covered through public pipeline or CLI tests.
- Tests no longer rely only on hidden in-test mutations for core scenario coverage.
- No new clinical thresholds or unsupported assumptions are introduced.

Verification:

- Root `examples/` now contains stable, low eGFR, high potassium, low SBP, no follow-up, prior DKA, and missing-labs/missing-oxygen CDE fixtures.
- Every new fixture is labeled synthetic/non-PHI in `local_context` and records derivation from the v0.3 stable fixture.
- Phase 0 variant acceptance uses fixture files through `run_evaluation_pipeline(...)` instead of hidden in-test mutations.
- CLI validation tests cover every root example fixture against the canonical HF domain pack.
- `examples/README.md`, `README.md`, `DEMO.md`, and repo-control docs list or describe the scenario fixtures.
- No runtime behavior, CLI behavior, clinical thresholds, utilities, formulas, final recommendations, PHI use, or AI/LLM judgment was added.
- `python -m pytest` passed, 103 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate` passed.
- canonical `report` to stdout passed.
- canonical `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` passed.
- all seven root `examples/*.json` CDE fixtures passed CLI validation with the canonical HF domain pack.
- all seven root `examples/*.json` CDE fixtures generated Markdown reports through the CLI.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL and contained 468 records after the final verification append.

### P1-004: Normalized Status Ledger

Status: done

Scope:

- Define a typed status-ledger row or equivalent shared contract for visible component states.
- Project safety gates, priors, Monte Carlo priors, uncertainty-budget items, VOI items, and Decision Profiles into that contract where practical.
- Preserve report/log visibility for missing, unsupported, blocked, deferred, active, present, resolved, sampled, and eligible statuses.

Acceptance:

- Report rendering and provenance logging can consume the shared status contract or a clearly equivalent projection.
- Tests prove unresolved statuses do not disappear.
- Logs remain status-only and avoid raw case text.

Verification:

- `StatusLedgerRow` and `StatusLedger` provide the typed shared status contract.
- `pdde/status_ledger.py` projects decision-option, domain-mapping, safety-gate, prior-resolution, Monte Carlo prior, uncertainty-budget, VOI, Decision Profile, and Decision Profiler statuses into deterministic ledger rows.
- The Markdown report unresolved-items section consumes `StatusLedger.unresolved_rows()` so missing, unsupported, blocked, active, and deferred items stay visible.
- JSONL provenance logging consumes `StatusLedger.status_counts_by_component()` in the component summary while avoiding ledger reasons and raw case content.
- Tests cover ledger projection, source/provenance traceability, serialization, unknown-component validation failure, unresolved status preservation, report visibility, and log status summaries.
- No runtime clinical logic, CLI behavior, final recommendations, AI/LLM judgment, hidden scoring, thresholds, utilities, formulas, or PHI handling were added.
- `python -m pytest` passed, 107 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate` passed.
- canonical `report` to stdout passed.
- canonical `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` passed.
- all seven root `examples/*.json` CDE fixtures passed CLI validation with the canonical HF domain pack.
- all seven root `examples/*.json` CDE fixtures generated Markdown reports through the CLI.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL.

### P1-005: Model Module Split

Status: done

Scope:

- Split `pdde/models.py` into focused modules only after mapping and status contracts are stable enough.
- Keep public imports backward compatible or document migration explicitly.

Acceptance:

- New modules have clear responsibility.
- Existing behavior and serialization surfaces remain covered.
- `pdde/models.py` remains a compatibility re-export module or has an explicit migration note.

Verification:

- `pdde/model_base.py` contains shared base types.
- `pdde/input_models.py` contains CDE, domain-pack, explicit mapping, safety-gate input, and prior input contracts.
- `pdde/component_models.py` contains deterministic component-result and status-ledger contracts.
- `pdde/pipeline_models.py` contains the top-level evaluation result contract.
- `pdde/legacy_models.py` contains legacy/planned report and log models kept for compatibility.
- `pdde/models.py` remains a compatibility re-export facade with an explicit migration note.
- Runtime modules import focused model modules directly while existing public `pdde.models` imports remain supported.
- `tests/test_model_modules.py` covers focused imports, facade identity, and pipeline result serialization after the split.
- No runtime clinical logic, CLI behavior, final recommendations, AI/LLM judgment, hidden scoring, thresholds, utilities, formulas, PHI handling, or provenance semantics were changed.
- `python -m pytest` passed, 110 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate` passed.
- canonical `report` to stdout passed.
- canonical `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` passed.
- all seven root `examples/*.json` CDE fixtures passed CLI validation with the canonical HF domain pack.
- all seven root `examples/*.json` CDE fixtures generated Markdown reports through the CLI.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL.

### P1-006: Report Section Registry Or Schema Contract

Status: done

Scope:

- Make report section order, required advisory language, and status-preservation obligations explicit.
- Keep Markdown rendering deterministic and simple.

Acceptance:

- Required sections are defined in one registry, schema, or equivalent contract.
- Tests assert required sections and deterministic ordering.
- Advisory-only and no-final-recommendation language remains required.

Verification:

- `pdde/report_contract.py` defines the required report title, section registry, section obligations, required advisory guardrail phrases, forbidden final-recommendation phrases, and status-preservation obligations.
- `pdde/report_renderer.py` renders by `REPORT_SECTIONS` order and validates final Markdown with `validate_report_contract`.
- tests assert required headings are included in deterministic registry order.
- tests assert advisory-only, uncalibrated, not-clinically-validated, and no-final-recommendation language remains required.
- tests assert dropped sections or dropped guardrail language fail clearly.
- tests assert missing, unsupported, blocked, and deferred status obligations remain visible across canonical and high-potassium reports.
- no CLI behavior, clinical logic, final recommendations, AI/LLM judgment, hidden scoring, thresholds, utilities, formulas, status-ledger semantics, provenance/privacy behavior, or generated-artifact policy changed.
- `python -m pytest` passed, 116 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate` passed.
- canonical `report` to stdout passed.
- canonical `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` passed.
- all seven root `examples/*.json` CDE fixtures passed CLI validation with the canonical HF domain pack.
- all seven root `examples/*.json` CDE fixtures generated Markdown reports through the CLI.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL.

### P1-007: Local Overlay Verification Contract

Status: done

Scope:

- Define schema/fields required for local operational overlay rules.
- Keep unverified local rules visibly draft or deferred.

Acceptance:

- Local overlay rules require or visibly defer owner, status, source, review cadence, and last-reviewed fields where applicable.
- Reports and logs display verification state without PHI or operationally sensitive free text.
- External local workflow owner input is documented if needed.

Verification:

- `pdde/local_overlay.py` evaluates explicit CDE `local_context` overlay metadata only.
- typed local overlay verification models require verified metadata and reject malformed verified objects.
- missing, malformed, unsupported, draft, and deferred local overlay states remain visible.
- reports display local overlay verification state and avoid raw local workflow text.
- JSONL logs record local overlay status, missing fields, and metadata-presence booleans without raw owner/source/review values.
- status ledger includes `local_overlay` rows so draft overlay status appears in unresolved items.
- no local rule becomes active solely because it exists in a draft source file.
- `python -m pytest` passed, 124 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate` passed.
- canonical `report` to stdout passed.
- canonical `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` passed.
- all seven root `examples/*.json` CDE fixtures passed CLI validation with the canonical HF domain pack.
- all seven root `examples/*.json` CDE fixtures generated Markdown reports through the CLI.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL.

### P1-008: AI Answer Mapping Interface

Status: complete

Scope:

- Prepare typed AI-answer mapping only after direct-CDE contracts are hardened and explicit user approval exists.
- Map answer content into structured claims, omissions, or overstatements that deterministic safety/profile layers can consume.

Acceptance:

- Free-text answers do not directly modify priors, thresholds, safety gates, or recommendations.
- Mapped claims feed structured deterministic inputs.
- Unsupported/unmapped claims remain visible.
- No final clinical recommendation or answer grade is produced as the primary artifact.

Verification:

- `pdde/ai_answer_mapping.py` maps only explicit source-backed patterns into typed `AIAnswerMappedClaim` records.
- the source-material sotalol-as-HF-beta-blocker and GLP-1-for-HF-admission-prevention examples are covered by tests.
- `wrong_indication_blocks` safety gates evaluate mapped structured claim types only when an `AIAnswerMappingResult` is explicitly supplied.
- unmapped and unsupported claim records remain visible in pipeline results, the status ledger, reports, and provenance records.
- raw AI answer text is not stored in pipeline results, reports, or provenance JSONL records.
- no CLI AI-answer mapping, LLM extraction, answer grading, final recommendation, hidden scoring, threshold, utility, prior, simulation, or clinical formula was added.
- `python -m pytest` passed, 131 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate` passed.
- canonical `report` to stdout passed.
- canonical `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` passed.
- all seven root `examples/*.json` CDE fixtures passed CLI validation with the canonical HF domain pack.
- all seven root `examples/*.json` CDE fixtures generated Markdown reports through the CLI.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL.

### P1-009: Citation/Evidence Audit Handoff

Status: complete

Scope:

- Define future citation/evidence-audit requirements without implementing full audit.
- Keep automated evidence validation out of scope.

Acceptance:

- Needed evidence-source fields and report/provenance gaps are documented.
- No citation scoring, source truth claims, or automated evidence validation is added.

Verification:

- `EVIDENCE_AUDIT_HANDOFF.md` documents future evidence-source fields, report/provenance gaps, relationship to prior and uncertainty governance, deferred workflow steps, out-of-scope features, and open user/governance inputs.
- no runtime behavior, CLI behavior, report wording, provenance schema, source checking, citation scoring, source truth claims, LLM judgment, answer grading, final recommendations, hidden scoring, thresholds, utilities, priors, or clinical formulas were added.
- full citation/evidence audit remains deferred until source ownership, identifiers, review statuses, support statuses, and network/data-access rules are governed.
- `python -m pytest` passed, 131 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate` passed.
- canonical `report` to stdout passed.
- canonical `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` passed.
- all seven root `examples/*.json` CDE fixtures passed CLI validation with the canonical HF domain pack.
- all seven root `examples/*.json` CDE fixtures generated Markdown reports through the CLI.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL.

### P1-010: Calibration And Outcome Anchoring Prerequisites

Status: complete

Scope:

- Define data, governance, and metric prerequisites for later calibration.
- Do not implement calibration curves or outcome claims.

Acceptance:

- Required labels/outcomes and governance approvals are listed.
- Current logs are assessed for calibration-seed suitability without PHI.
- No report language implies validation or calibrated risk.
- No outcome claims are added.
- Open user/governance inputs are listed.

Verification:

- `CALIBRATION_OUTCOME_PREREQUISITES.md` documents required label families, candidate outcome anchors needing governance, required approvals, data-handling constraints, metric prerequisites, current JSONL log suitability, report-language guardrails, deferred implementation boundaries, out-of-scope features, and open user/governance inputs.
- current logs are assessed as suitable for run inventory and audit checklist seeding, but not sufficient for Brier scores, ECE, reliability diagrams, outcome claims, or prior updating.
- no runtime behavior, CLI behavior, report wording, provenance schema, calibration curves, reliability metrics, Brier/ECE computation, prior updating, drift detection, outcome linkage, expert label collection, PHI handling, outcome claims, calibrated-risk language, final recommendations, hidden scoring, thresholds, utilities, priors, clinical formulas, LLM judgment, or answer grading were added.
- `python -m pytest` passed, 131 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate` passed.
- canonical `report` to stdout passed.
- canonical `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` passed.
- all seven root `examples/*.json` CDE fixtures passed CLI validation with the canonical HF domain pack.
- all seven root `examples/*.json` CDE fixtures generated Markdown reports through the CLI.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL.

## Queue State

Phase 2 is active. `P1-001`, `P1-002`, `P1-003`, `P1-004`, `P1-005`, `P1-006`, `P1-007`, `P1-008`, `P1-009`, and `P1-010` are complete. Phase 1 completion review is complete, and `phase1-baseline` exists locally. `P2-001: Evidence Source Registry Models`, `P2-002A: Evidence Registry Architecture Decisions`, `P2-002B: Domain-Pack Evidence Link Scaffold`, and `P2-003: Evidence Status Report And Provenance Visibility` are complete. The next Phase 2 task is `P2-004: Governed Local Overlay Metadata Completion Path`, currently blocked on local governance input.

## Phase 2 Tasks

### P2-001: Evidence Source Registry Models

Status: done

Scope:

- Add typed evidence-source, evidence-support-link, and evidence-registry models.
- Preserve strict validation and serialization.
- Preserve status-only/privacy discipline.
- Do not integrate with reports, provenance logs, loaders, or domain-pack validation yet.

Acceptance:

- Evidence sources have stable IDs, source type, title/label, and review status.
- Support links connect explicit evidence source IDs to explicit project entity IDs and entity types.
- Registry validation rejects duplicate source IDs, duplicate source/entity links, and support links to unknown evidence source IDs.
- Reviewed source/support statuses require review or audit metadata.
- Extra raw text fields such as source passages are rejected by strict models.
- `pdde.models` continues to re-export public model contracts for backwards compatibility.
- Tests cover creation, validation failure, source traceability, serialization, and no raw-source-text fields.
- No runtime pipeline, CLI, report, provenance, clinical logic, recommendation, LLM, evidence truth validation, calibration, outcome linkage, PHI, threshold, utility, prior, or formula behavior is added.

Verification:

- `pdde/evidence_models.py` defines `EvidenceSource`, `EvidenceSupportLink`, `EvidenceRegistry`, and `BibliographicIdentifier`.
- `pdde.models` re-exports the evidence registry contracts through the backwards-compatible facade.
- model tests cover successful creation/serialization, reviewed metadata requirements, final support audit metadata requirements, duplicate source IDs, duplicate support links, unknown source references, and raw-source-text field rejection.
- no runtime pipeline, CLI, report, provenance, clinical logic, recommendation, LLM, evidence truth validation, calibration, outcome linkage, PHI, threshold, utility, prior, or formula behavior was added.
- `python -m pytest tests/test_evidence_models.py tests/test_model_modules.py` passed, 8 tests.
- `python -m pytest` passed, 136 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate` passed.
- canonical `report` to stdout passed.
- canonical `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` passed.
- all seven root `examples/*.json` CDE fixtures passed CLI validation with the canonical HF domain pack.
- all seven root `examples/*.json` CDE fixtures generated Markdown reports through the CLI.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL and contained 1181 records after the final verification append.

### P2-002A: Evidence Registry Architecture Decisions

Status: done

Scope:

- Create architecture decision documents needed before implementing evidence registry persistence or linking.
- Define identity, immutability, lineage, storage options, and open questions.
- Preserve the core decision that evidence objects are immutable receipts while relationships, assessments, utility labels, trust judgments, safety judgments, and confidence scores may be mutable/versioned.
- Do not implement persistence, domain-pack linking, runtime behavior, CLI behavior, or report output changes.

Acceptance:

- `docs/architecture/evidence_registry_decision.md` exists.
- `docs/architecture/evidence_identity_model.md` exists.
- `docs/architecture/evidence_lineage_rules.md` exists.
- `docs/architecture/evidence_storage_matrix.md` exists.
- Architecture docs define `EvidenceObject`, `EvidenceLink`, `EvidenceAssessment`, and `EvidenceLineage`.
- Architecture docs define observed, inferred, synthesized, and speculative lineage.
- Architecture docs preserve open questions for P2-002B.
- Existing tests still pass.
- No runtime behavior, CLI behavior, or report output changed.

Verification:

- Architecture docs were created under `docs/architecture/`.
- Persistence and domain-pack evidence linking remain unimplemented.
- P2-002B was not started.
- `python -m pytest` passed, 136 tests.

### P2-002B: Domain-Pack Evidence Link Scaffold

Status: done

Scope:

- Add optional source-ID references to domain-pack evidence-bearing records only after P2-001 models exist.
- Keep current canonical fixtures backwards compatible.
- Validate only explicit IDs when an evidence registry is supplied.

Acceptance:

- Existing canonical CDE/domain-pack validation still passes.
- Optional evidence references can be loaded and preserved.
- Unknown evidence references fail clearly only when a registry validation path is explicitly used.
- Missing evidence references stay visible as pending/deferred rather than implying support.
- No automated evidence truth validation or source scoring is added.

Verification:

- `DomainPack.evidence_references` is optional and absent from canonical fixtures.
- domain-pack validation rejects unknown/fuzzy evidence-reference targets and duplicate entity/source references.
- `pdde/evidence_linking.py` validates explicit source IDs against a supplied `EvidenceRegistry` and distinguishes `linked`, `pending_review`, `unknown_source`, and `deferred` statuses.
- no CLI behavior, report output, provenance output, persistence, source truth validation, citation scoring, LLM judgment, calibration metrics, outcome linkage, final recommendations, PHI handling, thresholds, utilities, priors, formulas, hidden scoring, or local rule activation was added.
- focused tests passed: `python -m pytest tests/test_evidence_linking.py tests/test_evidence_models.py tests/test_model_modules.py tests/test_models.py tests/test_loaders.py`, 33 tests.
- `python -m pytest` passed, 143 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate` passed.
- canonical `report` to stdout passed.
- canonical `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` passed.
- all seven root `examples/*.json` CDE fixtures passed CLI validation with the canonical HF domain pack.
- all seven root `examples/*.json` CDE fixtures generated Markdown reports through the CLI.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL and contained 1261 records after the final verification append.

### P2-003: Evidence Status Report And Provenance Visibility

Status: done

Scope:

- Surface evidence registry/support statuses in reports and status-only provenance records.
- Preserve report-contract advisory language.

Acceptance:

- `EvaluationPipelineResult` preserves typed evidence-link validation output.
- shared status ledger includes evidence-reference status rows.
- Markdown report includes an `Evidence Reference Status` section with ID/status visibility only.
- JSONL provenance includes status-only evidence-link validation records.
- missing, malformed, unsupported, and deferred evidence references remain visible.
- no evidence truth validation, citation scoring, source-quality scoring, LLM judgment, persistence, clinical logic, final recommendations, PHI storage, hidden scoring, thresholds, utilities, priors, or formulas are added.

Verification:

- `pdde/evaluation_pipeline.py` accepts an optional API-only evidence registry and validates explicit domain-pack evidence references.
- `pdde/report_renderer.py` renders evidence-reference link/support status without raw evidence text or source truth claims.
- `pdde/provenance_logger.py` emits evidence-link status records without raw source titles, raw evidence text, gate evidence strings, patient-state values, or simulation samples.
- `tests/test_evidence_status_visibility.py` covers typed pipeline output, status-ledger projection, report visibility, provenance visibility, deferred references, and no source truth/scoring fields.
- focused integration tests passed: `python -m pytest tests/test_evidence_status_visibility.py tests/test_evaluation_pipeline.py tests/test_status_ledger.py tests/test_report_renderer.py tests/test_provenance_logger.py tests/test_phase0_acceptance.py tests/test_cli_report.py`, 52 tests.
- `python -m pytest` passed, 146 tests.
- `python -m py_compile pdde/*.py` passed.
- `python -m pdde --help` passed.
- canonical `validate` passed.
- canonical `report` to stdout passed.
- canonical `report --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl` passed.
- all seven root `examples/*.json` CDE fixtures passed CLI validation with the canonical HF domain pack.
- all seven root `examples/*.json` CDE fixtures generated Markdown reports through the CLI.
- `logs/hf_cde_stable.jsonl` parsed successfully as JSONL and contained 1383 records after the final verification append.

### P2-004: Governed Local Overlay Metadata Completion Path

Status: blocked

Scope:

- Define or load explicit local overlay owner/source/review metadata if governance input exists.
- Keep local clinical rules non-activating unless safe activation criteria are separately approved.

Reason Blocked:

- Requires local operational owner/source/review-cadence governance input.

### P2-005: Broader AI Answer Mapping Specification

Status: blocked

Scope:

- Extend the API-only deterministic mapping contract toward omissions and overstatements only with governed examples.

Reason Blocked:

- Requires example AI-answer artifacts, mapping boundaries, and explicit approval for any scope beyond the current deterministic claim-pattern interface.

### P2-006: Calibration Label And Outcome Protocol

Status: blocked

Scope:

- Define governed label and outcome schemas only after required approvals and data rules are available.

Reason Blocked:

- Requires clinical, privacy, statistical, data-owner, and label/outcome governance input.

### P2-007: Additional Synthetic Domain Or Scenario Fixtures

Status: blocked

Scope:

- Add synthetic non-PHI fixtures only from governed source material.

Reason Blocked:

- Requires a selected domain or scenario source and confirmation that no new clinical thresholds, weights, utilities, priors, or formulas are being invented.

## Deferred

### TQ-D001: AI Answer Mapping

Status: deferred

Scope:

- Claim extraction from AI answers.
- Claim-to-option mapping.
- Omission and overstatement flags.
- Prohibited recommendation checks.

Reason Deferred:

- direct CDE simulation now works and `P1-008` implements the typed deterministic mapping boundary. Broader claim extraction, omission/overstatement analysis, and answer grading remain deferred until explicitly scoped.

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

- `P1-009` documents the handoff requirements only. Full source support checking, citation integrity validation, citation scoring, source truth claims, and automated evidence validation remain explicitly deferred to a later governed scope.

### TQ-D004: Calibration And Outcome Anchoring

Status: deferred

Scope:

- Expert labels, calibration curves, prior drift, outcome linkage.

Reason Deferred:

- `P1-010` documents prerequisite labels, outcome anchors, governance approvals, data-handling constraints, metric prerequisites, and current log suitability only. Actual calibration curves, reliability metrics, outcome linkage, prior drift analysis, PHI handling, expert label collection, and outcome claims remain deferred to a later governed scope.
