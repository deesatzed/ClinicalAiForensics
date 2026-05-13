# Repository Map

Last updated: 2026-05-12

## Recon Summary

This root folder is now a git-backed project-planning and source-material workspace with an initial Python package scaffold for building `ClinAIForensics`. It has a root `pyproject.toml`, a scaffolded `pdde/` package, focused Pydantic model modules with a backwards-compatible `pdde.models` facade, minimal CDE/domain-pack loaders, explicit domain-pack mapping models, optional domain-pack evidence-reference models, an API-only evidence-link validator, a deterministic safety gate engine, an API-only deterministic AI-answer claim mapping boundary, deterministic evidence registry models, a deterministic prior resolver, a seeded Monte Carlo prior sampler, uncertainty-budget and value-of-information item evaluators, a local overlay verification contract layer, a deterministic Decision Profiler assembly layer, a typed end-to-end evaluation pipeline, a normalized status-ledger projection layer, an explicit report section contract, a deterministic Markdown report renderer, CLI report/run wiring, JSONL provenance logging, canonical synthetic example CDE fixtures, Phase 0 acceptance tests, a Phase 0 build log/manual structural review, a Phase 0 handoff package, technical reviewer documentation, Phase 1 and Phase 2 planning artifacts, baseline/artifact policy, Phase 1 evidence/calibration handoffs, a Phase 1 completion review, a focused `tests/` directory, canonical support directories, and a root remote at `https://github.com/deesatzed/ClinicalAiForensics.git`.

The intended project appears to be a Phase 0/Phase 1/Phase 2 Python CLI/API for PDDE: a Clinical Decision Episode simulator and governance engine for HF ED discharge decisions. It should load synthetic CDE fixtures and an HF domain pack, run deterministic safety gates before probabilistic simulation, keep local overlay verification metadata visible without activating draft local rules, preserve evidence-source registry metadata and optional domain-pack evidence references without source truth validation, and render advisory-only Markdown Decision Profiles with provenance, uncertainty budget, value-of-information, local overlay status, and calibration status.

No `AGENTS.md` file is present in the repository tree. The effective operating instructions are the conversation-provided AGENTS instructions plus the root control files.

The supporting `ClinSafer/` and `Agent_Pidgeon/` workspaces are tracked from the root as git submodules because they are independent repositories with their own GitHub remotes.

## Root Files

| Path | Role |
| --- | --- |
| `GOAL.md` | Project mission, source priority, Phase 0 target, non-goals, success criteria. |
| `STANDARDS.md` | Operating, clinical safety, output, prior governance, engineering, verification, and audit standards. |
| `IMPLEMENT.md` | Phase -1 and Phase 0 implementation plan and target module layout. |
| `DECISIONS.md` | Current architectural and scope decisions. |
| `PROGRESS.md` | Work log and verification record. |
| `TASK_QUEUE.md` | Ordered task queue for future implementation. |
| `REPO_MAP.md` | This recon artifact. |
| `.gitmodules` | Submodule declarations for `Agent_Pidgeon/` and `ClinSafer/`. |
| `README.md` | Technical reviewer overview for `PDDE Phase 0`, including plain-language scope, quickstart, exact commands, output files, architecture, guardrails, tests, and Phase 1 pointer. |
| `DEMO.md` | Five-minute technical reviewer demo script for CLI validation, report generation, provenance JSONL inspection, test verification, and safe explanation language. |
| `BUILD_LOG.md` | Phase 0 build log, manual structural review, first-principles review, alien-goggles review, and ranked improvement opportunities. |
| `PHASE0_HANDOFF.md` | Concise operator-facing Phase 0 handoff package with commands, limitations, deferred items, next tasks, and stop/go recommendation. |
| `PHASE1_PLAN.md` | Planning-only Phase 1 roadmap with ranked tasks, acceptance criteria, verification expectations, user-input needs, and stop conditions. |
| `PHASE2_PLAN.md` | Phase 2 roadmap for governance-contract hardening, beginning with evidence source registry models and preserving Phase 0/1 guardrails. |
| `BASELINE_POLICY.md` | Phase 0 baseline tag, root git strategy, submodule policy, generated report/log artifact policy, and Phase 1 boundary guardrails. |
| `EVIDENCE_AUDIT_HANDOFF.md` | P1-009 documentation-only handoff for future citation/evidence audit fields, report/provenance gaps, governance inputs, and out-of-scope boundaries. |
| `CALIBRATION_OUTCOME_PREREQUISITES.md` | P1-010 documentation-only handoff for future calibration/outcome labels, governance approvals, data constraints, metric prerequisites, log suitability, and out-of-scope boundaries. |
| `PHASE1_COMPLETION_REVIEW.md` | Phase 1 completion review summarizing `P1-001` through `P1-010`, runtime/documentation changes, guardrails, limitations, deferred work, Phase 2 candidate directions, and stop/go recommendation. |
| `pyproject.toml` | Initial Python package metadata and dependency groups. |
| `.gitignore` | Local/generated-file ignore rules, including ignored generated `reports/*.md` and `logs/*.jsonl`. |
| `docs/architecture/` | Phase 2 architecture decision documents for evidence registry identity, immutability, lineage, storage options, and persistence/linking open questions. |
| `pdde/` | Phase 0/Phase 1/Phase 2 implementation package. Contains CLI wiring, focused Pydantic model modules, a compatibility `pdde.models` facade, explicit domain-pack mapping models, optional domain-pack evidence-reference models, API-only evidence-link validation, evidence-source registry models, CDE/domain-pack loaders, deterministic safety gate evaluation, API-only AI-answer claim mapping, deterministic prior resolution, seeded prior-level Monte Carlo sampling, item-level uncertainty/VOI evaluation, local overlay verification, deterministic Decision Profile assembly, a typed evaluation pipeline, normalized status-ledger projection, explicit report section contract, deterministic Markdown report rendering, and JSONL provenance logging. |
| `tests/` | Focused scaffold, model-module, evidence-registry, evidence-linking, model, loader, safety gate, AI-answer mapping, prior resolver, Monte Carlo prior-sampling, uncertainty/VOI, local-overlay, Decision Profiler, evaluation pipeline, status-ledger, report-contract, report-renderer, CLI report, provenance-logger, and acceptance tests. |
| `domain_packs/` | Canonical future domain-pack location. |
| `examples/` | Canonical root synthetic CDE fixture location. Contains stable, low eGFR, high potassium, low SBP, no follow-up, prior DKA, and missing-labs/missing-oxygen CDE fixtures derived from the v0.3 stable fixture. |
| `reports/` | Canonical generated report output location. Contains generated fixture reports from TQ-011 verification. |
| `logs/` | Canonical generated JSONL audit log location. Contains generated fixture log `logs/hf_cde_stable.jsonl` from TQ-012/TQ-013 verification. |
| `instruc1.md` | Primary rationale for the v0.3 pivot from AI-answer grading to CDE-first decision simulation. |
| `hf_ed_discharge_v0.yaml` | Rich v0.1 belief-network/reference YAML for HF ED discharge. Useful for report content, node detail, local overlay fields, and older option vocabulary. |
| `sample_case_HF-001.json` | Root synthetic v0.1 sample case. |
| `sample_report_HF-001.md` | Root v0.1 target-style Decision Fitness Report. Useful as report-shape reference. |

## Build Direction Sources

### `pdde_v0_3_first_principles_final/`

This is the controlling product-direction package.

Important files:

- `01_FIRST_PRINCIPLES_REASSESSMENT.md`: defines the CDE as the primitive object and explains the two-engine split.
- `02_REVISED_FINAL_PLAN.md`: product definition, modes, first MVP domain, node set, output categories, and phase order.
- `03_CODEX_BUILD_SPEC.md`: required Phase 0 CLI structure and implementation requirements.
- `04_TESTING_ALGORITHM.md`: unit, metamorphic, missingness, hard-stop, uncertainty-budget, and report tests.
- `05_PRIOR_AND_UNCERTAINTY_GOVERNANCE.md`: prior classes, Phase 0 prior policy, required prior fields, uncertainty budget, calibration targets, language rules.
- `06_UI_AND_REPORTING_SPEC.md`: Markdown-only Phase 0 report requirements and warning language.
- `codex_tasks/PHASE0_TASKS.md`: ordered direct-simulation tasks.
- `schemas/clinical_decision_episode.schema.json`: minimal CDE schema.
- `schemas/decision_profile.schema.json`: minimal Decision Profile schema.
- `domain_packs/hf_ed_discharge/domain_pack.yaml`: v0.3 draft HF domain pack with Phase 1 explicit gate-target and prior-to-option mappings.
- `examples/hf_cde_stable.json`: v0.3 CDE fixture.

Use this package as the source of truth when it conflicts with older PDDE materials.

### `pdde-build-package/`

This is an older but detailed implementation package. It is useful for concrete specs, tests, and fixtures when compatible with v0.3.

Important files:

- `build/pyproject_template.toml`: good starting point for Python 3.12 packaging and dependency versions.
- `build/tech_stack.md`: Python/Pydantic/PyYAML/NumPy/SciPy/pytest stack.
- `build/build_order.md`: detailed older Phase 0 task list.
- `docs/non_negotiable_constraints.md`: still applicable safety constraints.
- `docs/architecture.md`: six-layer architecture; adapt to v0.3 by making direct CDE simulation primary.
- `docs/risk_register.md`: useful Phase 0 risk list.
- `specs/01_data_models.md`: Pydantic model detail; should be adapted to v0.3 CDE/domain-pack schema.
- `specs/04_monte_carlo_engine.md`: vectorized simulation guidance.
- `specs/05_sensitivity_analyzer.md`: variance-driver / value-of-information basis.
- `specs/06_report_generator.md`: report rendering details; adapt from "Decision Fitness Report" to v0.3 "Decision Profile".
- `specs/07_provenance_manager.md`: JSONL logging structure.
- `specs/08_cli_runner.md`: CLI error-handling and pipeline guidance.
- `specs/02_claim_extractor.md` and `03_node_parameterizer.md`: defer until AI answer mapping after direct simulation works.
- `tests/phase_0_acceptance.md`, `tests/adversarial_suite.md`, `tests/unit_test_specs.md`: acceptance and unit-test ideas.
- `examples/`: older sample and adversarial fixtures.
- `networks/hf_ed_discharge_v0.yaml`: copy of the richer v0.1 root YAML.

## Supporting Example Sources

| Path | Use |
| --- | --- |
| `pdde_v0_3_first_principles_final/examples/hf_cde_stable.json` | Canonical starting CDE fixture shape for Phase 0. |
| `examples/hf_cde_stable.json` | Root synthetic non-PHI stable CDE fixture derived from the v0.3 source fixture. |
| `examples/hf_cde_low_egfr.json` | Root synthetic low-eGFR CDE fixture. |
| `examples/hf_cde_high_k.json` | Root synthetic high-potassium CDE fixture. |
| `examples/hf_cde_low_sbp.json` | Root synthetic low-SBP CDE fixture. |
| `examples/hf_cde_no_followup.json` | Root synthetic no-follow-up CDE fixture. |
| `examples/hf_cde_prior_dka.json` | Root synthetic prior-DKA CDE fixture. |
| `examples/hf_cde_missing_labs.json` | Root synthetic missing-labs/missing-oxygen CDE fixture. |
| `pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml` | Canonical starting domain-pack shape for Phase 0. |
| `pdde-build-package/examples/sample_case_HF-001.json` | Older sample case useful for patient-context fields and regression expectations. |
| `pdde-build-package/examples/case_egfr_15.json` | Low-eGFR fixture idea. |
| `pdde-build-package/examples/case_potassium_57.json` | High-potassium fixture idea. |
| `pdde-build-package/examples/case_sbp_86.json` | Low-SBP fixture idea. |
| `pdde-build-package/examples/case_missing_labs.json` | Missingness fixture idea. |
| `pdde-build-package/examples/adversarial_sotalol.txt` | Source-material prohibited-claim fixture used by the P1-008 typed AI-answer mapping tests. |
| `pdde-build-package/examples/adversarial_glp1.txt` | Source-material prohibited-claim fixture used by the P1-008 typed AI-answer mapping tests. |
| `sample_case_HF-001.json` | Root reference sample case. |
| `sample_report_HF-001.md` | Root reference report format. |

## Supporting Codebases And Reuse Candidates

### `ClinSafer/`

ClinSafer is a working clinical-AI boundary-layer prototype. It should inform design and tests, but it should not become a Phase 0 dependency unless explicitly approved later.

Reusable concepts:

- Unknowns-first framing: missing, uncertain, distorted, contradictory, objective-needed, remote-unknowable information.
- Deterministic guardrails before autonomy or recommendation.
- Most-restrictive governor pattern.
- Explicit clinical uncertainty graph with typed nodes, source reliability, range bands, missingness state, uncertainty distribution, boundary fragility, and action implications.
- Black-swan assumption-breach state machine and autonomy-tier caps.
- Governed medical knowledge as reviewed configuration rather than model vibes.
- Structured observability and case trace pattern.
- Synthetic benchmark / retrospective validation harness concepts.

Candidate files to study or selectively adapt:

- `ClinSafer/jre/models.py`: lightweight dataclass model pattern and `most_restrictive` function.
- `ClinSafer/jre/uncertainty_graph.py`: typed node-state pattern, range bands, missingness and boundary-fragility summaries.
- `ClinSafer/jre/black_swan.py`: hard-stop/assumption-breach rule structure.
- `ClinSafer/jre/any_disposition.py`: disposition review report structure.
- `ClinSafer/jre/disposition_handoff.py`: retrospective disposition snapshot and benchmark harness ideas.
- `ClinSafer/jre/observability.py`: structured trace/logging pattern.
- `ClinSafer/jre/sensitivity.py`: sensitivity/reporting workflow ideas.
- `ClinSafer/docs/CLINICAL_UNCERTAINTY_GRAPH.md`: conceptual foundation for CDE node handling.
- `ClinSafer/docs/GOVERNED_MEDICAL_KNOWLEDGE_LAYER.md`: governance pattern for medical knowledge.
- `ClinSafer/BLACK_SWAN_GUARDRAILS.md`: assumption-boundary framing.

Compatibility notes:

- ClinSafer uses dependency-light dataclasses and Python >=3.10.
- The new PDDE plan calls for Pydantic v2 models and Python 3.12+.
- Reuse patterns and tests first; avoid direct imports in Phase 0.

### `Agent_Pidgeon/`

Agent_Pidgeon is a deterministic semantic-contract, receipt, policy, and flight-recorder codebase. It should inform PDDE provenance and audit design, but it should not become a Phase 0 runtime dependency.

Reusable concepts:

- Schema validation before resolution/execution.
- Deterministic policy findings with severity, code, and message.
- Receipt records that answer what a compact pointer meant at resolution time.
- Hashing/canonical JSON patterns for tamper-evident artifacts.
- Flight-recorder event chains with payload hashes and trace integrity checks.
- Semantic diffs that treat removed guardrails as high-risk.
- Sensitive clinical pointer metadata and receipt requirements.

Candidate files to study or selectively adapt:

- `Agent_Pidgeon/src/agent_pidgin/schema_validator.py`: concise JSON Schema validation and field-specific error formatting.
- `Agent_Pidgeon/src/agent_pidgin/policy.py`: deterministic policy/finding structure.
- `Agent_Pidgeon/src/agent_pidgin/receipt.py`: receipt record shape.
- `Agent_Pidgeon/src/agent_pidgin/flight_recorder.py`: trace event, hash-chain, integrity-check patterns.
- `Agent_Pidgeon/src/agent_pidgin/hash_utils.py`: canonical JSON and SHA-256 helpers.
- `Agent_Pidgeon/schemas/pidgin-receipt.schema.json`: receipt schema style.
- `Agent_Pidgeon/policies/default_policy.json`: policy-as-data pattern.
- `Agent_Pidgeon/catalogs/clinical_safety.json`: example of explicitly non-diagnostic clinical safety primitives.

Compatibility notes:

- Agent_Pidgeon targets Python >=3.13 and depends on `jsonschema` and `fastmcp`.
- PDDE Phase 0 targets Python 3.12+ and should avoid adding Agent_Pidgeon dependency weight.
- Reuse audit shapes and deterministic policy style, not the runtime package.

## Likely Architecture

The first implemented architecture should be a CLI-only Python package:

```text
CLI
  -> Evaluation pipeline
    -> CDE loader
    -> Domain pack loader
    -> Schema/model validation
    -> Explicit domain-pack mappings
    -> Deterministic safety gate engine
    -> Prior resolver and provenance validator
    -> Monte Carlo soft-node simulator
    -> Value-of-information ranker
    -> Uncertainty budget generator
    -> Decision profiler
    -> Status ledger projection
  -> Markdown report renderer
  -> JSONL provenance logger
```

Key module boundaries from `IMPLEMENT.md`:

```text
pdde/
  model_base.py
  input_models.py
  component_models.py
  evidence_models.py
  evidence_linking.py
  pipeline_models.py
  legacy_models.py
  models.py
  cde_loader.py
  domain_pack_loader.py
  safety_gate_engine.py
  prior_resolver.py
  monte_carlo_engine.py
  uncertainty_budget.py
  value_of_information.py
  decision_profiler.py
  evaluation_pipeline.py
  status_ledger.py
  report_contract.py
  report_renderer.py
  provenance_logger.py
  run_cde.py
```

Expected data flow:

1. Load a CDE JSON fixture.
2. Load an HF domain pack YAML.
3. Validate both into typed models.
4. Resolve allowed priors and reject/quarantine disallowed prior classes.
5. Optionally accept a typed AI-answer mapping result; direct CDE CLI runs do not parse free text.
6. Evaluate deterministic hard gates through explicit domain-pack gate-target mappings and explicit mapped claim types when supplied.
7. Run Monte Carlo only for soft, non-overriding tradeoffs.
8. Generate one Decision Profile per option using explicit prior-to-option mappings.
9. Record local overlay verification state without applying draft local workflow rules.
10. Project component statuses into a normalized status ledger for report/log visibility.
11. Render Markdown and append JSONL-compatible audit records.

## Current Build Status

`TQ-001: Project Setup And Source Normalization`, `TQ-002: Data Models`, `TQ-003: CDE And Domain-Pack Loaders`, `TQ-004: Deterministic Safety Gate Engine`, `TQ-005: Prior Resolver`, `TQ-006: Monte Carlo Engine`, `TQ-007: Uncertainty Budget And Value Of Information`, `TQ-008: Decision Profiler`, `TQ-009: Evaluation Pipeline`, `TQ-010: Markdown Report Renderer`, `TQ-011: CLI Run And Validate Commands`, `TQ-012: Provenance Logging`, `TQ-013: Phase 0 Acceptance Tests`, `TQ-014: Build Log And Manual Structural Review`, `TQ-015: Phase 0 Handoff Package`, `P1-001: Phase 0 Baseline And Artifact Policy`, `P1-002: Explicit Domain-Pack Mappings`, `P1-003: Canonical Synthetic Variant Fixtures`, `P1-004: Normalized Status Ledger`, `P1-005: Model Module Split`, `P1-006: Report Section Registry Or Schema Contract`, `P1-007: Local Overlay Verification Contract`, `P1-008: AI Answer Mapping Interface`, `P1-009: Citation/Evidence Audit Handoff`, `P1-010: Calibration And Outcome Anchoring Prerequisites`, `P2-001: Evidence Source Registry Models`, `P2-002A: Evidence Registry Architecture Decisions`, and `P2-002B: Domain-Pack Evidence Link Scaffold` are complete. Phase 2 is active, and `P2-003: Evidence Status Report And Provenance Visibility` is the next unstarted task.

Completed setup/model work:

- root `pyproject.toml`,
- root `.gitignore`,
- `pdde/` package scaffold,
- `run-cde`, `report`, and `validate` CLI parser,
- `validate` CLI wiring for structural CDE/domain-pack loading,
- placeholder modules for planned Phase 0 boundaries,
- canonical support directories,
- focused CLI help test,
- focused Pydantic v2 model modules in `pdde/model_base.py`, `pdde/input_models.py`, `pdde/component_models.py`, `pdde/pipeline_models.py`, and `pdde/legacy_models.py`,
- backwards-compatible model re-export facade in `pdde/models.py`,
- evidence-source registry contracts in `pdde/evidence_models.py`,
- optional domain-pack evidence-reference contracts in `pdde/input_models.py`,
- API-only domain-pack evidence reference validation in `pdde/evidence_linking.py`,
- evidence registry architecture docs under `docs/architecture/`,
- explicit domain-pack mapping models in `pdde/input_models.py`,
- safety gate result models in `pdde/component_models.py`,
- model-module compatibility tests in `tests/test_model_modules.py`,
- model validation and serialization tests in `tests/test_models.py`,
- domain-pack evidence-linking tests in `tests/test_evidence_linking.py`,
- CDE JSON loader in `pdde/cde_loader.py`,
- domain-pack YAML loader in `pdde/domain_pack_loader.py`,
- shared loader error formatting in `pdde/loader_errors.py`,
- loader API and CLI validation tests in `tests/test_loaders.py`,
- deterministic safety gate evaluator using explicit gate-target mappings in `pdde/safety_gate_engine.py`,
- safety gate tests in `tests/test_safety_gate_engine.py`,
- API-only AI-answer claim mapper in `pdde/ai_answer_mapping.py`,
- AI-answer mapping models in `pdde/component_models.py`,
- safety gate, pipeline, status-ledger, report, and provenance integration for explicit mapped claim types,
- AI-answer mapping tests in `tests/test_ai_answer_mapping.py`,
- prior resolution result models in `pdde/component_models.py`,
- deterministic prior resolver in `pdde/prior_resolver.py`,
- prior resolver tests in `tests/test_prior_resolver.py`,
- Monte Carlo prior-sampling result models in `pdde/component_models.py`,
- seeded Monte Carlo prior sampler in `pdde/monte_carlo_engine.py`,
- Monte Carlo prior-sampling tests in `tests/test_monte_carlo_engine.py`,
- uncertainty-budget and VOI result models in `pdde/component_models.py`,
- uncertainty-budget item evaluator in `pdde/uncertainty_budget.py`,
- value-of-information item evaluator in `pdde/value_of_information.py`,
- uncertainty/VOI tests in `tests/test_uncertainty_and_voi.py`,
- local overlay verification result models in `pdde/component_models.py`,
- local overlay verification evaluator in `pdde/local_overlay.py`,
- local overlay verification tests in `tests/test_local_overlay.py`,
- Decision Profiler result models in `pdde/component_models.py`,
- deterministic Decision Profile assembler using explicit prior-to-option mappings in `pdde/decision_profiler.py`,
- Decision Profiler tests in `tests/test_decision_profiler.py`,
- evaluation pipeline result model in `pdde/pipeline_models.py`,
- direct CDE evaluation pipeline in `pdde/evaluation_pipeline.py`,
- evaluation pipeline tests in `tests/test_evaluation_pipeline.py`,
- normalized status-ledger models in `pdde/component_models.py`,
- deterministic status-ledger projection in `pdde/status_ledger.py`,
- status-ledger tests in `tests/test_status_ledger.py`,
- explicit report section and guardrail contract in `pdde/report_contract.py`,
- report-contract tests in `tests/test_report_contract.py`,
- deterministic Markdown report renderer in `pdde/report_renderer.py`,
- report renderer tests in `tests/test_report_renderer.py`,
- `report` CLI command that prints Markdown to stdout or writes `--output`,
- implemented `run-cde` compatibility command that writes `--out`,
- direct `python -m pdde.run_cde --cde ... --domain ... --out ...` compatibility path,
- CLI report tests in `tests/test_cli_report.py`,
- generated verification reports in `reports/hf_cde_stable_report.md` and `reports/hf_cde_stable_run_cde_report.md`,
- appendable JSONL provenance logger in `pdde/provenance_logger.py`,
- optional CLI `--log` support for report/run-cde commands,
- provenance logger tests in `tests/test_provenance_logger.py`,
- Phase 0 acceptance tests in `tests/test_phase0_acceptance.py`,
- Phase 0 build log and structural review in `BUILD_LOG.md`,
- Phase 0 handoff package in `PHASE0_HANDOFF.md`,
- technical reviewer overview in `README.md`,
- five-minute technical reviewer demo guide in `DEMO.md`,
- Phase 1 planning artifact in `PHASE1_PLAN.md`,
- Phase 0 baseline/artifact policy in `BASELINE_POLICY.md`,
- citation/evidence audit handoff in `EVIDENCE_AUDIT_HANDOFF.md`,
- calibration/outcome anchoring prerequisites handoff in `CALIBRATION_OUTCOME_PREREQUISITES.md`,
- root synthetic CDE fixtures under `examples/`,
- generated verification log in `logs/hf_cde_stable.jsonl`.

The package intentionally does not include final recommendation ranking, numeric decision-fitness synthesis, database logging, external telemetry, AI/LLM logging, production monitoring, or PHI storage.

## Next Build Task

No non-deferred Phase 0 implementation task remains in the current task queue, and the Phase 0 handoff package is complete.

`P2-002B: Domain-Pack Evidence Link Scaffold` is complete. The next unstarted Phase 2 task is `P2-003: Evidence Status Report And Provenance Visibility`.

## Risks And Blockers

### Source Conflicts

- v0.3 domain pack and CDE schema are simpler than the older v0.1 YAML/report.
- The older package starts with AI-answer adjudication in several places, while the root decisions require direct CDE simulation first.
- Decision option IDs differ between v0.3 and v0.1 artifacts.
- v0.3 `wrong_indication_blocks` are claim-type gates, but direct CDE simulation does not yet have mapped claim-type inputs.

Mitigation: keep the current loaders strict to the canonical v0.3 fixtures; handle v0.1 compatibility only in explicit later source-normalization or prior-resolution work.

### Prior Governance

- v0.3 says no LLM-unverified priors in Phase 0 direct simulation.
- The richer v0.1 YAML includes `llm_unverified` placeholders for local executability and monitoring feasibility.

Mitigation: the current prior resolver blocks `llm_unverified` and `low_unverified` active priors, resolves only explicit domain-pack priors, and normalizes only compatible v0.1 labels. Legacy v0.1 belief-network conversion remains intentionally unimplemented until explicitly scoped.

### False Precision

- Monte Carlo output may appear authoritative despite draft priors.
- The current Monte Carlo layer samples resolved priors only; it does not produce numeric per-option posteriors.
- The current uncertainty/VOI layer returns item statuses and deferred states, not numeric sensitivity or expected-value claims.
- The current Decision Profiler assembles transparent status profiles but does not compute ranks, median fitness, final categories, or uncertainty intervals because the v0.3 source files do not define those formulas.
- The current evaluation pipeline preserves all component outputs, the status ledger projects visible component statuses without adding reasoning, the CLI/report renderer displays advisory Markdown, and the provenance logger records status-only JSONL without adding recommendation ranking or raw clinical payload logs.

Mitigation: every report needs advisory warnings, prior provenance, calibration status, uncertainty budget, and visible limitations.

### Scope Creep

- ClinSafer and Agent_Pidgeon are large working codebases.
- Direct imports could pull in unrelated architecture, dependency, and version constraints.

Mitigation: reuse patterns only in Phase 0 unless a later decision approves dependency reuse.

### Repository State

- Root is now a git repository on branch `main`.
- Root remote `origin` points to `https://github.com/deesatzed/ClinicalAiForensics.git`.
- The Phase 0 stable baseline is tagged as `phase0-baseline`.
- `ClinSafer/` and `Agent_Pidgeon/` are separate git repositories tracked from the root as submodules.
- Generated Markdown reports and JSONL logs remain ignored; `.gitkeep` files preserve the output directories.

Mitigation: keep submodule URLs current and follow `BASELINE_POLICY.md` before relying on generated reports/logs as release artifacts.

### Clinical Content Governance

- Domain thresholds, priors, and local overlay rules are draft.
- Local Temple workflow rules require owner/status/source/review cadence before clinical advisory use.

Mitigation: keep Phase 0 synthetic and advisory-only; use local overlay as draft data.

### Test Oracle

- There is no single clinical correctness oracle.

Mitigation: test invariants, hard stops, missingness, metamorphic shifts, report completeness, and provenance constraints.
