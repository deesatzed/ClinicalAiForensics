# Decision Log

Initialized: 2026-05-11

## D-001: Use v0.3 As Product Direction

Decision: `pdde_v0_3_first_principles_final/` and `instruc1.md` are the controlling direction when they conflict with the older `pdde-build-package/`.

Reason: v0.3 corrects the central primitive from "AI answer" to "Clinical Decision Episode" and explicitly separates deterministic hard stops from probabilistic simulation.

Impact: Phase 0 starts with direct CDE simulation. AI answer extraction is deferred until the simulator works.

## D-002: Phase 0 Is CLI-Only Direct Simulation

Decision: Phase 0 will build a Python CLI only. No frontend, auth, production database, PDF, EHR integration, or citation audit.

Reason: The build goal is to discover ontology, prior, safety-gate, and report-shape issues quickly without product surface area.

Impact: Implementation tasks focus on models, loaders, hard gates, priors, Monte Carlo, uncertainty budget, value-of-information, report rendering, CLI, logs, and tests.

## D-003: Hard Safety Gates Precede Monte Carlo

Decision: Deterministic safety gates are evaluated before probabilistic scoring and cannot be overridden by favorable simulation results.

Reason: v0.3 explicitly separates hard stops from soft uncertain tradeoffs. ClinSafer's guardrail work reinforces that some assumption failures should change allowed action, not merely lower confidence.

Impact: The safety gate engine is a first-class module and affects Decision Profile categories directly.

## D-004: No LLM-Unverified Priors In Phase 0 Direct Simulation

Decision: Phase 0 direct simulation may use draft policy priors, but not active LLM-unverified priors.

Reason: v0.3 prior governance warns that Monte Carlo can create false precision, and Phase 0 policy says LLM-unverified priors are not allowed in direct simulation.

Impact: The prior resolver must reject or quarantine LLM-unverified priors in direct-simulation mode.

## D-005: Decision Profile Is The Primary Output

Decision: The primary output is a Decision Profile per candidate option, rendered in Markdown.

Reason: A single score hides uncertainty and conflicts with the non-negotiable constraints.

Impact: Every option must include category, median fitness, uncertainty interval, hard stops, missing variables, value-of-information, uncertainty budget, local execution checklist, prior provenance, and calibration status.

## D-006: Supporting Projects Inform Patterns But Are Not Dependencies

Decision: ClinSafer and Agent_Pidgeon are supporting source material, not Phase 0 runtime dependencies.

Reason: They contain relevant safety and provenance patterns, but importing their code would expand scope and couple this project to unrelated demo architectures.

Impact: Reuse concepts only: uncertainty graph discipline, most-restrictive governor, governed knowledge, receipts, deterministic policy checks, and trace/log structures.

## D-007: Root Repository Is Not Currently A Git Repository

Decision: No git initialization was performed during project initialization.

Reason: The user requested only project-control file initialization and no code implementation.

Impact: A future setup task should decide whether to initialize a root git repository before code work begins.

## D-008: Defer Root Git Initialization During Scaffold Setup

Decision: TQ-001 did not initialize a root git repository. A root `.gitignore` was added so future root git initialization has sane defaults.

Reason: The root contains nested `ClinSafer/` and `Agent_Pidgeon/` git repositories. Initializing a parent repository changes version-control boundaries and should be explicit rather than assumed during the smallest setup task.

Impact: Future work can still initialize root git, but that should be a deliberate step. The scaffold is usable without git.

## D-009: Keep AI Dependencies Optional For Direct Simulation

Decision: The initial `pyproject.toml` includes Pydantic, PyYAML, NumPy, and SciPy as base dependencies. Anthropic is placed behind an optional `ai` extra. The initial CLI uses stdlib `argparse`.

Reason: Phase 0 direct simulation explicitly defers AI answer mapping. Keeping LLM access optional avoids making credentials or network-dependent packages part of the initial CDE simulator path.

Impact: AI answer mapping can add or require the `ai` extra later. TQ-001 remains credential-free and testable locally.

## D-010: Canonical Phase 0 Paths

Decision: Canonical Phase 0 project paths are `pdde/` for source, `tests/` for tests, `domain_packs/hf_ed_discharge/domain_pack.yaml` for the first domain pack, `examples/` for synthetic CDE fixtures, `reports/` for generated Markdown reports, and `logs/` for generated JSONL audit records.

Reason: These paths match `IMPLEMENT.md` and keep build-direction packages separate from the new implementation.

Impact: TQ-002 and later tasks should populate these canonical paths rather than modifying the source-material packages directly.

## D-011: Minimal Data Model Scope For TQ-002

Decision: TQ-002 models target the v0.3 Clinical Decision Episode fixture and v0.3 HF domain-pack shape first. The model layer includes structural output/log records needed by later tasks, but it does not implement legacy v0.1 belief-network parsing or clinical reasoning behavior.

Reason: The v0.3 package is the controlling product direction, and TQ-002 requires the smallest useful typed model layer. Supporting v0.1 artifacts should inform later reconciliation but should not broaden this first data-model pass.

Impact: `ClinicalDecisionEpisode` and `DomainPack` validate the v0.3 source fixtures now. Richer v0.1 YAML compatibility is deferred to explicit source-normalization or prior-resolution work after the strict v0.3 loader boundary.

## D-012: Prior And Local Rule Validation Boundary

Decision: Priors require distribution, beta parameters, provenance class, elicitation method, confidence class, and calibration status. Low or unverified confidence priors require a warning. Owner/review metadata remains optional in the model because the current v0.3 domain pack does not yet provide those fields. Local overlay rules require owner and status now.

Reason: This preserves the current v0.3 fixture compatibility while enforcing the highest-value governance invariants from `STANDARDS.md`.

Impact: Later domain-pack normalization should add owner/review metadata where the source material supports it. The prior resolver can tighten direct-simulation admission rules without changing the base model shape.

## D-013: Loader Scope Is Structural Validation Only

Decision: TQ-003 loaders read CDE JSON and domain-pack YAML, parse them with structured parsers, and return typed Pydantic model objects. They do not normalize legacy v0.1 artifacts, resolve priors, evaluate gates, simulate outcomes, or generate reports.

Reason: TQ-003 is the smallest useful loader layer and the v0.3 CDE/domain-pack files remain the canonical Phase 0 fixtures. The root v0.1 YAML, sample case, and sample report are supporting references until a later source-normalization task has explicit scope to reconcile them.

Impact: Invalid or unsupported input fails clearly instead of being silently converted. Clinical reasoning behavior remains isolated for later task boundaries.

## D-014: Minimal Validate Command Uses Loaders Early

Decision: The CLI `validate` command now calls the CDE and domain-pack loaders and returns non-zero for parse, read, or model-validation failures. The `run-cde` command remains a stub until the engine and report pipeline exist.

Reason: TQ-003 acceptance requires invalid files to exit non-zero through `validate`, while TQ-010 still owns full run wiring.

Impact: Loader behavior is testable from both Python APIs and the CLI without implying that clinical simulation is implemented.

## D-015: Safety Gates Are Explicit Domain-Pack Rule Evaluation

Decision: TQ-004 evaluates only explicit v0.3 `hard_gates` from the loaded domain pack against the loaded CDE `patient_state`. The engine returns typed gate-evaluation records with statuses `passed`, `blocked`, `triggered`, `missing`, or `unsupported`.

Reason: The task requires deterministic, transparent rule evaluation without clinical inference, probabilistic priors, Monte Carlo, AI judgment, or unsupported rules.

Impact: `admit_or_observe_triggers`, `mra_blocks`, and `sglt2_blocks` are evaluated now. Missing variables, malformed values, unknown gate groups, and deferred claim-type gates do not silently pass.

## D-016: Claim-Type Hard Gates Remain Deferred Until AI Mapping

Decision: `wrong_indication_blocks` gates with only `claim_type` are reported as `unsupported` in direct CDE simulation because the current CDE model has no mapped claim-type input.

Reason: Detecting sotalol-as-HF-beta-blocker or GLP-1-for-HF-prevention from free text belongs to the deferred AI answer mapping / claim extraction path, not TQ-004.

Impact: The safety gate engine surfaces those gates clearly without pretending they were evaluated. Later AI mapping can feed structured claim types into this boundary.

## D-017: Prior Resolution Is Explicit Domain-Pack Lookup Only

Decision: TQ-005 resolves priors only from `DomainPack.prior_policy`, with optional requested prior IDs. It does not read free-text CDE content, infer missing priors, elicit LLM estimates, normalize the legacy v0.1 belief-network structure, or run simulation.

Reason: The task goal is the smallest deterministic prior resolver. The v0.3 domain pack is the active Phase 0 source, and the current CDE model has no explicit prior field.

Impact: Missing requested priors return a typed `missing` result and never create default values. Later source-normalization work can add v0.1 belief-network conversion if explicitly scoped.

## D-018: Phase 0 Prior Admission Policy

Decision: Active direct-simulation priors are admitted only when their provenance normalizes to `guideline_mapped_policy_prior` or `draft_expert_policy_prior`. Compatible v0.1 labels `guideline_mapped` and `panel_elicited_pending` are normalized to those Phase 0 labels. `llm_unverified` provenance and `low_unverified` confidence are blocked; malformed or otherwise unsupported prior definitions are not active.

Reason: v0.3 prior governance allows draft policy priors but forbids LLM-unverified priors in Phase 0 direct simulation.

Impact: The resolver preserves source traceability, calibration status, warning text, and original provenance while preventing disallowed priors from silently entering the simulation path.

## D-019: Monte Carlo Engine Samples Resolved Priors Before Option Profiling

Decision: TQ-006 implements a seeded NumPy sampler over explicit `PriorResolutionSet` entries and returns per-prior simulation summaries. It does not yet map priors to decision options or synthesize per-option posteriors.

Reason: The current v0.3 domain pack defines explicit beta priors but does not encode a complete prior-to-option mapping or decision-fitness formula. Creating option posteriors now would require unsupported clinical assumptions or string heuristics.

Impact: The Monte Carlo layer preserves source/provenance traceability and clearly reports missing, blocked, unsupported, or malformed priors without sampling them. Per-option combination remains the responsibility of the later decision profiler once explicit mappings and hard-gate handling are available.

## D-020: TQ-007 Uses Item-Level Uncertainty And VOI Classification

Decision: TQ-007 returns item-level uncertainty-budget and value-of-information evaluations with explicit source fields, status, required data, and deferred states. It does not compute numeric uncertainty weights, expected value of information, or sensitivity-derived ranks.

Reason: The v0.3 sources define the required uncertainty categories and VOI variables, but the current domain pack does not provide a numeric VOI formula, option-level posterior mapping, or complete sensitivity metadata.

Impact: Missing or unsupported items stay visible and actionable without hidden math. Numeric uncertainty attribution and per-option VOI optimization remain deferred until decision profiling and explicit source definitions support them.

## D-021: Decision Profiler Is Deterministic Evidence Assembly For TQ-008

Decision: TQ-008 implements Decision Profile Evaluation records with statuses such as `eligible`, `blocked`, `triggered`, `missing`, `unsupported`, and `deferred`. It assembles explicit domain-pack decision options, direct safety-gate results, related prior/simulation traceability by option/prior identifier overlap, uncertainty-budget items, and VOI items. It does not emit final recommendation categories, ranks, median decision fitness, or uncertainty intervals.

Reason: The canonical v0.3 files define decision options, hard gates, priors, uncertainty categories, and VOI variables, but they do not define a complete option utility formula, ranking threshold implementation, prior-to-option weighting model, or decision-fitness synthesis formula. Creating ranked clinical recommendations now would invent unsupported math.

Impact: Hard gate blockers, triggers, missing inputs, unsupported inputs, unresolved uncertainty, and VOI items remain visible in typed profiles. Final ranking, numeric decision-fitness, narrative recommendations, and report rendering remain deferred until explicit formulas or approved report-layer behavior are implemented.

## D-022: Insert Evaluation Pipeline Before Report Rendering

Decision: The next TQ-009 task is the evaluation pipeline requested in the current build instruction, rather than Markdown report rendering. `pdde/evaluation_pipeline.py` wires strict loaders, safety gates, prior resolution, Monte Carlo prior sampling, VOI, uncertainty budget, and Decision Profiler assembly into one typed `EvaluationPipelineResult`. Markdown report rendering is deferred to the next task.

Reason: The current instruction explicitly asks for the smallest useful evaluation pipeline and prohibits narrative report generation. Wiring component outputs before report rendering also creates a stable data contract for the eventual Markdown renderer.

Impact: TQ-009 completes an API-level end-to-end direct CDE evaluation path without adding CLI run output, recommendation text, report sections, hidden scoring, or deployment surface. The next unblocked task becomes the Markdown Report Renderer.

## D-023: Markdown Renderer Reports Status Evidence Without Final Conclusions

Decision: TQ-010 renders `EvaluationPipelineResult` into deterministic advisory Markdown that preserves component outputs, source references, calibration status, and missing/unsupported/deferred/blocked items. It does not compute or display ranked options, final clinical conclusions, clinical validation claims, hidden scores, option utilities, or synthetic decision-fitness values.

Reason: The canonical v0.3 files support transparent evidence/status reporting but still do not define a validated option-ranking formula, final recommendation rule, or local workflow verification checklist. The sample v0.1 report shape is useful for section coverage, but its ranked recommendations and fitness language are not supported by the current typed pipeline.

Impact: `pdde/report_renderer.py` is an API-level report formatter for later CLI wiring. TQ-011 should connect this renderer to `run-cde` output without changing the existing strict `validate` command.

## D-024: Expose Both Report And Run-CDE CLI Paths

Decision: TQ-011 keeps the existing `validate` command, adds a novice-friendly `report` subcommand, and converts `run-cde` from a stub into a compatibility command that writes Markdown to `--out`. `python -m pdde.run_cde --cde ... --domain ... --out ...` is also supported by treating bare `--cde` arguments as `run-cde`.

Reason: The current user-facing requirement suggests `python -m pdde report ...`, while the project queue and implementation plan still include the older `python -m pdde.run_cde --cde ... --out ...` acceptance command. Supporting both avoids a naming break and keeps `report` intuitive for the Markdown-only path.

Impact: CLI report generation is now available without adding external services, UI, deployment, AI judgment, clinical recommendations, or provenance log writing. TQ-012 remains responsible for JSONL-compatible audit logs.

## D-025: Provenance Logs Are Status-Only JSONL Records

Decision: TQ-012 creates appendable JSONL provenance records from `EvaluationPipelineResult` and wires optional `--log` support into `report` and `run-cde`. Records include run metadata, input paths, loaded IDs, package version, command name, report path, seed/iteration settings, component status summaries, safety gate statuses, prior-resolution statuses, Monte Carlo sampled/non-sampled statuses, uncertainty-budget statuses, VOI statuses, Decision Profile statuses, and provenance references.

Reason: Phase 0 needs calibration/audit structure without storing PHI or pretending production observability exists. IDs, statuses, paths, counts, and source references are enough for the current build task and are safer than logging raw case text, full patient-state values, gate evidence strings, or simulation samples.

Impact: `pdde/provenance_logger.py` is the audit-log boundary. Timestamps and run IDs can be injected for deterministic tests; CLI logs use current UTC timestamps and derived run IDs. Database logging, external telemetry, AI/LLM logging, production monitoring, and richer audit dashboards remain out of scope.

## D-026: Phase 0 Acceptance Tests Exercise Public Boundaries And Guardrails

Decision: TQ-013 acceptance coverage lives in `tests/test_phase0_acceptance.py` and exercises the public CLI and Python API boundaries rather than adding new clinical logic or full-report snapshots. It uses the canonical v0.3 stable CDE/domain pack, temporary report/log outputs, deterministic seeds, and API-level CDE variants for low eGFR, high potassium, low SBP, no follow-up, prior DKA, and missing labs.

Reason: The current v0.3 source package includes one canonical CDE fixture and explicit domain-pack gates. Mutating that typed fixture inside tests covers Phase 0 hard-stop and missingness invariants without introducing unsupported fixture formats or clinical assumptions.

Impact: Acceptance tests now verify help, validation, report generation, output-file writing, provenance JSONL writing/parsing, API pipeline execution, advisory report sections, no invented final recommendations, visible unresolved statuses, no credential/network dependence, and status-only logs that avoid raw clinical payload text.

## D-027: BUILD_LOG Is The Phase 0 Structural Review Artifact

Decision: TQ-014 creates `BUILD_LOG.md` as the durable Phase 0 build log and manual structural review artifact. The task is documentation-only and does not change runtime behavior, clinical logic, model fields, report semantics, or CLI behavior.

Reason: Phase 0 now has enough implementation surface to review architecture, guardrails, limitations, and next steps without adding unsupported clinical assumptions. Keeping this review in a root Markdown file makes the Phase 0 state easy to audit before any Phase 1 work.

Impact: Future work should treat `BUILD_LOG.md` as the review handoff for architecture risks, first-principles concerns, alien-goggles alternatives, and ranked improvement opportunities. TQ-014 closes the current non-deferred Phase 0 queue; AI answer mapping and other Phase 1 items remain deferred until explicitly started.

## D-028: Phase 0 Handoff Is Ready For Tagging Or Demo

Decision: `PHASE0_HANDOFF.md` is the concise operator-facing Phase 0 handoff package. Phase 0 is ready to tag, archive, and demo as a local synthetic advisory prototype, and it may be used as the base for Phase 1 only after an explicit Phase 1 start decision.

Reason: The current implementation has passing end-to-end acceptance coverage, working CLI validate/report/log paths, generated example artifacts, a structural build log, and a handoff document that preserves scope boundaries. No non-deferred Phase 0 implementation task remains.

Impact: Clinical deployment, PHI use, final recommendation generation, AI answer mapping, local overlay verification, citation/evidence audit, and calibration/outcome anchoring remain out of scope until explicitly authorized and governed. Future contributors should start from `PHASE0_HANDOFF.md`, `BUILD_LOG.md`, and the deferred queue rather than adding new clinical logic opportunistically.

## D-029: Phase 1 Plan Is Planning-Only Until Explicit Start

Decision: `PHASE1_PLAN.md` is the planning-only Phase 1 roadmap derived from `BUILD_LOG.md` and `PHASE0_HANDOFF.md`. It ranks `P1-001` through `P1-010`, defines acceptance criteria, and recommends `P1-001` as the first task, but it does not activate Phase 1 implementation.

Reason: The Phase 0 review identified concrete next tasks, but several require explicit user input before implementation, especially root git strategy and generated-artifact policy. Capturing the ranked plan now preserves the handoff without changing runtime behavior or slipping into Phase 1 work.

Impact: Future work should use `PHASE1_PLAN.md` when the user explicitly starts Phase 1. Until then, no Phase 1 runtime changes, clinical logic, AI answer mapping, generated-artifact policy changes, or root git initialization should be assumed.

## D-030: README And DEMO Are The Reviewer Entry Points

Decision: `README.md` and `DEMO.md` are the primary reviewer-facing entry points for understanding and running Phase 0 without reading the full build history. `README.md` explains the deterministic advisory scaffold, exact commands, output artifacts, architecture, guardrails, tests, and Phase 1 pointer. `DEMO.md` provides a 5-minute CLI demo with safe explanation language.

Reason: Phase 0 now has extensive build history and control files. A technical reviewer needs a concise path to run the project and understand what the output does and does not mean without accidentally treating Phase 0 as clinical decision support.

Impact: Future documentation updates should keep these two files concise, reviewer-oriented, and aligned with the current CLI behavior. Runtime behavior, clinical logic, final recommendations, and Phase 1 activation remain out of scope for these documentation files.

## D-031: Publish Root Repository With Supporting Codebases As Submodules

Decision: The root workspace is initialized as a git repository on branch `main` and published to `https://github.com/deesatzed/ClinicalAiForensics.git`. The supporting `ClinSafer/` and `Agent_Pidgeon/` directories are tracked as submodules using their existing GitHub remotes rather than as embedded repository contents.

Reason: The user explicitly requested committing and pushing the root project to GitHub. The supporting codebases already had independent git histories and remotes; recording them as submodules preserves that ownership boundary and avoids broken embedded-repository commits.

Impact: Cloners should use submodule-aware checkout if they need the supporting source material. Generated reports and JSONL logs remain ignored by `.gitignore`; the root repository preserves `reports/` and `logs/` via `.gitkeep` files. Runtime behavior, clinical logic, and Phase 1 implementation remain unchanged.

## D-032: Phase 1 Starts With Baseline And Artifact Policy

Decision: Phase 1 is active by explicit user instruction, and `P1-001` is completed as a documentation/process task. The Phase 0 baseline identifier is the annotated git tag `phase0-baseline` pointing at commit `0662777`. Generated `reports/*.md` and `logs/*.jsonl` remain ignored reproducible artifacts by default, with `.gitkeep` files preserving the output directories. `ClinSafer/` and `Agent_Pidgeon/` remain submodules rather than root-owned source.

Reason: Phase 1 should begin from a clear stable baseline before any schema, fixture, or runtime hardening work. The generated report/log policy prevents append-only logs and regenerated Markdown from becoming accidental source-of-truth files.

Impact: Future Phase 1 work should reference `BASELINE_POLICY.md` for root git, submodule, baseline tag, and generated-artifact rules. Runtime behavior, clinical logic, report semantics, recommendation policy, LLM/AI judgment, and provenance/privacy guardrails remain unchanged.

## D-033: Explicit Domain-Pack Mappings Replace Hidden Routing

Decision: `P1-002` adds a typed `mappings` section to `DomainPack` with `safety_gate_targets` and `prior_to_options`. The canonical HF domain pack now carries explicit safety-gate target option IDs/matched statuses and explicit prior-to-option links. The safety gate engine no longer uses the Python `_GATE_TARGETS` fallback table, and the Decision Profiler no longer associates priors to profiles by token overlap.

Reason: Phase 1 should remove hidden inference before adding domains or AI answer mapping. Gate routing and prior/profile association are domain facts, not Python heuristics or clinical guesses.

Impact: Malformed mapping targets fail strict domain-pack validation. Missing safety-gate mappings are surfaced as unsupported rather than silently routed. Profiles attach only explicitly mapped priors/simulations, and mapping provenance appears in reports/logs through source references. No thresholds, utilities, profile weights, option rankings, final clinical recommendations, or AI/LLM judgment were added.

## D-034: Canonical Synthetic Variant Fixtures Live Under Root Examples

Decision: `P1-003` promotes the stable, low eGFR, high potassium, low SBP, no follow-up, prior DKA, and missing-labs/missing-oxygen scenarios into static root `examples/*.json` CDE fixtures. Each fixture is labeled synthetic/non-PHI in `local_context` and records derivation from the v0.3 stable fixture.

Reason: Phase 1 needs inspectable scenario fixtures that reviewers can validate and run through the public CLI/API, instead of relying only on hidden in-test mutations. Keeping them under root `examples/` matches `IMPLEMENT.md` and leaves the original v0.3 source package intact.

Impact: Tests now exercise core scenario behavior through fixture files and public pipeline/CLI boundaries. No runtime behavior, CLI behavior, domain-pack mappings, clinical thresholds, utilities, scoring formulas, final recommendations, PHI handling, or AI/LLM judgment were added.

## D-035: Normalized Status Ledger Is A Projection Contract

Decision: `P1-004` adds `StatusLedgerRow`, `StatusLedger`, and `pdde/status_ledger.py` as a shared projection over existing typed component outputs. Report rendering consumes unresolved ledger rows, and provenance logging consumes ledger status counts only.

Reason: Phase 1 needs one auditable status contract for missing, unsupported, blocked, active, deferred, present, resolved, sampled, and eligible states before report/log semantics expand further. Keeping the ledger as a projection avoids turning it into a hidden reasoning layer.

Impact: The ledger preserves component identifiers, statuses, reasons for report display, source references, provenance references, and related entity IDs. JSONL logs intentionally use aggregate ledger status counts rather than ledger reasons so raw clinical evidence strings and patient-state values are not added to logs. No clinical thresholds, utilities, formulas, final recommendations, AI/LLM judgment, CLI behavior, or PHI handling were added.

## D-036: Focused Model Modules With Compatibility Facade

Decision: `P1-005` splits model definitions out of the centralized `pdde/models.py` file into focused modules: `model_base.py`, `input_models.py`, `component_models.py`, `pipeline_models.py`, and `legacy_models.py`. `pdde/models.py` remains as a backwards-compatible re-export facade.

Reason: The P1-002 explicit mapping contracts, P1-003 fixtures, and P1-004 status-ledger contract are now stable enough to reduce model-file gravity without changing runtime behavior. Focused modules make future schema work easier to review before AI mapping or local overlay work expands the model surface.

Impact: Existing imports from `pdde.models` continue to work, while internal runtime modules now import from the focused modules. No CLI behavior, clinical logic, final recommendations, AI/LLM judgment, thresholds, utilities, hidden scoring, provenance semantics, or PHI handling were changed.

## D-037: Report Section Contract Is The Renderer Source Of Truth

Decision: `P1-006` adds `pdde/report_contract.py` as the single registry for required Markdown report sections, deterministic section ordering, advisory guardrail phrases, forbidden final-recommendation phrases, and visible status-preservation obligations. `pdde/report_renderer.py` now renders sections by that registry and validates the final Markdown against the contract.

Reason: Phase 1 needs the report format to be reviewable as a stable external contract before more report/log semantics or AI-mapping inputs are added. Keeping section order and advisory language in one small module prevents tests, renderer code, and future docs from drifting independently.

Impact: The report renderer now fails clearly if a required section or required advisory phrase is dropped. Existing report content, CLI behavior, clinical logic, status ledger behavior, provenance logging, generated-artifact policy, final-recommendation prohibition, and AI/LLM boundaries remain unchanged.

## D-038: Local Overlay Verification Is Metadata-Only

Decision: `P1-007` adds a typed local overlay verification contract and evaluator that read explicit local overlay metadata from CDE `local_context` only. Required governance fields are owner, status, source, review cadence, and last reviewed. Missing or malformed metadata is surfaced as `missing`, `unsupported`, `draft`, or `deferred`; draft or incomplete local overlay rules remain inactive.

Reason: Local operational workflow assumptions are governance data, not clinical reasoning rules. The canonical fixtures only provide `overlay_status: draft`, and the older local-overlay source material is explicitly unverified. A metadata-only contract prevents draft local pathways from becoming hidden clinical logic while still making the verification gap visible to reviewers.

Impact: Pipeline results, reports, status-ledger rows, and provenance summaries now include local overlay verification state. Reports and logs avoid printing raw local overlay owner/source/review values; logs record presence booleans, statuses, missing fields, and safe source paths. No CLI behavior, final recommendation logic, AI/LLM mapping, hidden scoring, thresholds, utilities, clinical formulas, or active local workflow rules were added.

## D-039: AI Answer Mapping Is A Typed Non-Reasoning Boundary

Decision: `P1-008` adds `pdde/ai_answer_mapping.py` and typed `AIAnswerMappingResult`/`AIAnswerMappedClaim` models as an API-only deterministic boundary for explicit source-backed AI-answer claim patterns. The mapper currently recognizes the source-material sotalol-as-HF-beta-blocker and GLP-1-for-HF-admission-prevention examples, stores structured claim metadata without raw answer text, and lets the existing `wrong_indication_blocks` safety gates consume mapped claim types.

Reason: Phase 1 needed a narrow bridge from answer-derived claims to deterministic gates without reopening hidden clinical inference. The v0.3 and v0.1 source materials explicitly identify these wrong-indication claim types and detection patterns, while also requiring direct CDE simulation to remain separate from AI answer mapping.

Impact: Free-text answers do not directly modify priors, thresholds, safety gates, recommendations, simulations, or reports. Only explicit mapped claim records can activate claim-type gates, and unmapped or unsupported claims remain visible through pipeline results, the status ledger, reports, and provenance records. No CLI AI-answer mapping, LLM extraction, answer grading, final recommendation, hidden scoring, thresholds, utilities, or new clinical formulas were added.

## D-040: Citation/Evidence Audit Remains A Handoff Specification

Decision: `P1-009` creates `EVIDENCE_AUDIT_HANDOFF.md` as a documentation-only handoff for future citation/evidence audit requirements. The handoff lists candidate evidence-source fields, current report/provenance gaps, relationship to prior and uncertainty governance, deferred workflow steps, out-of-scope audit features, and open user/governance inputs.

Reason: Phase 1 can clarify what future evidence support review requires without starting Phase 3-style citation verification. The current system has provenance strings and status-only logs, but it does not have governed source registries, bibliographic IDs, support-status decisions, source freshness checks, or source-to-claim alignment.

Impact: No runtime behavior, CLI behavior, report wording, provenance schema, automated source checking, citation scoring, source truth claims, LLM judgment, answer grading, final recommendation logic, hidden scoring, thresholds, utilities, priors, or clinical formulas were added. Full citation/evidence audit remains deferred until source ownership, allowed identifiers, review statuses, support statuses, and network/data-access rules are explicitly governed.

## D-041: Calibration And Outcome Anchoring Remain Prerequisites-Only

Decision: `P1-010` creates `CALIBRATION_OUTCOME_PREREQUISITES.md` as a documentation-only handoff for future calibration and outcome anchoring. The handoff lists required label families, candidate outcome anchors that need governance, required approvals, data-handling constraints, metric prerequisites, current JSONL log suitability, report-language guardrails, out-of-scope calibration features, and open user/governance inputs.

Reason: The project has status-only provenance logs and visible calibration-pending report language, but it does not have expert labels, clinician action distributions, governed outcome anchors, PHI/data-use approvals, numeric option-level calibrated probabilities, or metric definitions. Defining prerequisites now reduces future scope risk without implying validation.

Impact: No runtime behavior, CLI behavior, report wording, provenance schema, calibration curves, reliability metrics, Brier/ECE computation, prior updating, drift detection, outcome linkage, expert label collection, PHI handling, outcome claims, calibrated-risk language, final recommendation logic, hidden scoring, thresholds, utilities, priors, clinical formulas, LLM judgment, or answer grading were added. Calibration and outcome anchoring remain deferred until governance, labels, outcomes, and data-handling rules are approved.

## D-042: Phase 1 Completion Review Is Documentation-Only And Recommends A Stable Baseline

Decision: `PHASE1_COMPLETION_REVIEW.md` records Phase 1 completion across `P1-001` through `P1-010` and recommends tagging Phase 1 as a stable baseline only after the review is committed and the user approves the tag name.

Reason: Phase 1 hardened the Phase 0 scaffold, added explicit mapping/status/report/provenance boundaries, and documented evidence and calibration prerequisites. A completion review gives the next reviewer a concise stop/go record before any Phase 2 scope begins.

Impact: No Phase 2 work, runtime behavior, CLI behavior, clinical logic, final recommendations, LLM/AI judgment, outcome linkage, calibration metrics, thresholds, utilities, priors, or formulas are added by the review. Phase 2 remains deferred until a specific candidate direction is selected and governed.

## D-043: Phase 2 Starts With Governance Contracts, Not Clinical Expansion

Decision: Phase 2 is active by explicit user instruction. `PHASE2_PLAN.md` defines Phase 2 as governance-contract hardening that starts from `phase1-baseline` and begins with `P2-001: Evidence Source Registry Models`.

Reason: Phase 1 completed the direct-CDE hardening baseline and documented evidence-audit and calibration prerequisites. The safest next step is to turn handoff prerequisites into typed, reviewable contracts before any source checking, calibration, local-rule activation, or broader AI-answer analysis.

Impact: Phase 2 does not authorize final recommendations, LLM clinical judgment, automated evidence truth validation, calibration metrics, outcome linkage, PHI handling, local clinical rule activation, hidden scoring, new thresholds, utilities, weights, priors, or formulas. Later Phase 2 tasks remain blocked when they require user/governance input.

## D-044: Evidence Registry Models Are Metadata Contracts Only

Decision: `P2-001` adds `pdde/evidence_models.py` with typed evidence-source, evidence-support-link, and evidence-registry contracts. The models validate source IDs, review/support statuses, support-link references, duplicate IDs, duplicate links, and required review/audit metadata for reviewed statuses.

Reason: P1-009 identified the need for source IDs, review status, support status, support scope, limitations, and audit metadata. Defining those contracts now makes future evidence work explicit without claiming source truth or changing runtime clinical behavior.

Impact: Evidence registry models are not wired into the CLI, report renderer, provenance logger, domain-pack loader, or evaluation pipeline in P2-001. They do not fetch sources, validate DOI/PMID existence, score citations, check retractions, align abstracts to claims, add clinical recommendations, add calibration/outcome logic, or store raw source passages.

## D-045: Evidence Receipts Are Immutable And Judgments Are Versioned

Decision: `P2-002A` defines evidence architecture before persistence or linking. `EvidenceObject` is an immutable receipt. `EvidenceLink` records the relationship between evidence and a task, component, or context. `EvidenceAssessment` records contextual trust, utility, safety, support, or confidence judgments. `EvidenceLineage` records whether a record is observed, inferred, synthesized, or speculative.

Reason: Evidence identity and evidence judgment have different lifecycles. A receipt should preserve what was observed, while relationships and assessments must be allowed to change as governance, review status, source freshness, or support context changes.

Impact: Persistence and domain-pack linking remain unimplemented. P2-002B must choose a storage/linking approach before code changes. This decision does not add runtime behavior, CLI behavior, report output changes, source truth validation, citation scoring, LLM judgment, calibration metrics, outcome linkage, final recommendations, PHI handling, thresholds, utilities, priors, formulas, or local rule activation.

## D-046: Domain-Pack Evidence Links Are Optional Explicit Source-ID References

Decision: `P2-002B` uses optional `DomainPack.evidence_references` records as domain-pack-side pointers from explicit domain-pack entities to evidence source IDs. A separate API-only validator in `pdde/evidence_linking.py` validates those source IDs against a supplied `EvidenceRegistry` and reports whether a matching registry support link exists.

Reason: P2-002A separates immutable evidence receipts from mutable/versioned links and assessments. Keeping source receipt IDs in a separate registry while allowing domain packs to point at those IDs preserves backwards compatibility and avoids embedding review judgments or raw source content in domain-pack clinical configuration.

Impact: Existing canonical fixtures remain valid without evidence references. Missing references are reported as `deferred`, explicit references without a registry or without a matching support link remain `pending_review`, and unknown source IDs fail clearly only through the explicit validation API. No CLI behavior, report output, provenance output, persistence, source truth validation, citation scoring, LLM judgment, calibration metrics, outcome linkage, final recommendations, PHI handling, thresholds, utilities, priors, formulas, or local rule activation were added.

## D-047: Evidence Status Visibility Is Status-Only

Decision: `P2-003` wires domain-pack evidence-link validation into `EvaluationPipelineResult`, the shared status ledger, Markdown report output, and JSONL provenance records as IDs, statuses, counts, and provenance references only.

Reason: Phase 2 needs evidence support state to be inspectable without making source truth, citation quality, or clinical correctness claims. The existing evidence architecture treats evidence objects as receipts and support assessments as contextual/versioned, so report and provenance visibility must preserve those distinctions.

Impact: Reports now include an `Evidence Reference Status` section and logs include `evidence_link_validation` records. No CLI argument behavior, persistence, source fetching, automated evidence truth validation, citation scoring, LLM judgment, clinical logic, final recommendations, thresholds, utilities, priors, formulas, PHI storage, raw evidence text logging, or local clinical rule activation was added.
