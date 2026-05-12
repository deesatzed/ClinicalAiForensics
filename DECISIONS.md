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
