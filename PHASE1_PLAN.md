# Phase 1 Plan

## Planning Status

This is a planning artifact derived from `BUILD_LOG.md` and `PHASE0_HANDOFF.md`. It does not start Phase 1 and does not implement runtime behavior.

Phase 0 remains the current completed baseline: a local synthetic advisory CLI/API that validates CDE/domain-pack inputs, runs deterministic component layers, renders Markdown Decision Profile reports, and writes status-only JSONL provenance logs.

## Phase 1 Objective

Phase 1 should harden the direct CDE simulator before adding AI answer mapping. The goal is to reduce fragile assumptions, make fixtures and domain-pack contracts easier to review, and create a stable reporting/logging contract that can later accept AI-derived structured claims without changing the safety model.

Phase 1 should not convert Phase 0 into clinical decision support.

## Non-Goals

- No clinical deployment.
- No PHI.
- No EHR integration.
- No UI/API service layer.
- No final clinical recommendation.
- No "safe discharge" or "unsafe discharge" conclusion.
- No hidden score, option ranking, validated risk, or decision-fitness formula.
- No new clinical thresholds, utilities, weights, or priors unless explicit source files and governance support them.
- No AI answer mapping until direct CDE hardening tasks are complete or explicitly waived.

## Ranking Method

Tasks are ranked by:

- value to the project goal
- risk reduction
- estimated chance of improving the project goal
- dependency position
- whether user input or governance input is required

## Ranked Task List

| Rank | Task ID | Next Task | Estimated Chance Of Improving Goal | Why | Risk | Requires User Input? |
|---:|---|---|---:|---|---|---|
| 1 | P1-001 | Tag/archive Phase 0 baseline and decide root git/generated-artifact policy | 90% | Freezes the known-good Phase 0 state and prevents confusion around nested repos, generated reports, and append-only logs. | Low code risk; moderate process risk if skipped. | Yes |
| 2 | P1-002 | Add explicit domain-pack gate-target and prior-to-option mappings | 85% | Removes the most fragile current assumptions: Python gate routing and token-overlap prior/profile association. | Medium schema and fixture migration risk. | No, unless clinical semantics change |
| 3 | P1-003 | Promote canonical synthetic CDE variant fixtures into `examples/` | 80% | Makes demo, acceptance, and review scenarios inspectable without depending on test-only mutations. | Low risk if provenance and synthetic status are documented. | No |
| 4 | P1-004 | Define a normalized status-ledger model | 75% | Gives report rendering and JSONL logging one shared contract for unresolved, missing, unsupported, blocked, and deferred states. | Medium abstraction risk if made too broad. | No |
| 5 | P1-005 | Split centralized model definitions into focused modules | 70% | Improves maintainability before adding more schema and AI-mapping models. | Medium import/refactor risk. | No |
| 6 | P1-006 | Add a report section registry or report schema contract | 65% | Makes required advisory sections, ordering, and guardrail language explicit before external review expands. | Low to medium framework risk. | No |
| 7 | P1-007 | Define local overlay verification schema and placeholders | 60% | Prevents draft local operational assumptions from becoming hidden clinical logic. | Medium governance dependency. | Yes |
| 8 | P1-008 | Prepare AI answer mapping interface only after direct-CDE contracts are hardened | 55% | Lets deferred claim-type gates receive structured claims later without reverting the system to answer grading. | Medium to high scope-creep risk. | Yes, for example answers and boundaries |
| 9 | P1-009 | Define citation/evidence-audit handoff requirements, but keep full audit deferred | 45% | Clarifies what evidence support would need without starting Phase 3 work. | Low implementation risk; high scope-expansion risk. | Yes |
| 10 | P1-010 | Define calibration/outcome anchoring prerequisites, but do not claim calibration | 40% | Documents governance/data needs before any outcome claims. | High dependency on external labels/outcomes. | Yes |

## Recommended Sequence

1. Complete `P1-001` before any implementation work.
2. Complete `P1-002` and `P1-003` before adding AI answer mapping.
3. Complete `P1-004` before broadening report/log semantics.
4. Complete `P1-005` only after the mapping and fixture contract is clear enough to avoid churn.
5. Complete `P1-006` before sharing report format as a stable external contract.
6. Complete `P1-007` only with local owner/status/source input.
7. Treat `P1-008` as gated work, not the default next task.

## Task Acceptance Criteria

### P1-001: Phase 0 Baseline And Artifact Policy

Scope:

- Decide whether the root workspace should become a git repository despite nested `ClinSafer/` and `Agent_Pidgeon/` repositories.
- Decide how generated reports and append-only logs should be treated.
- Tag, archive, or otherwise identify the Phase 0 baseline.

Acceptance criteria:

- Root version-control strategy is documented.
- Nested repository handling is documented.
- Generated report/log policy is documented, including whether `reports/*.md` and `logs/*.jsonl` are committed, regenerated, ignored, or archived.
- Phase 0 baseline identifier exists, such as a tag, archive name, release note, or explicit snapshot path.
- `PHASE0_HANDOFF.md`, `BUILD_LOG.md`, `README.md`, and `DEMO.md` remain accurate.
- No runtime behavior changes are made.
- Verification passes: `python -m pytest`, `python -m py_compile pdde/*.py`, `python -m pdde --help`, canonical `validate`, canonical `report`, and JSONL parse check.

### P1-002: Explicit Domain-Pack Mappings

Scope:

- Add explicit domain-pack fields for gate targets and prior-to-option relationships.
- Remove reliance on Python-only gate routing where the source file should carry routing semantics.
- Remove token-overlap prior/profile association from the Decision Profiler.

Acceptance criteria:

- Domain-pack schema/model supports explicit safety-gate target option IDs.
- Domain-pack schema/model supports explicit prior-to-option mappings.
- Loaders validate malformed, missing, or unknown mapping targets with clear errors.
- Safety gate evaluation uses explicit source mappings where available.
- Decision Profiler uses explicit prior-to-option mappings where available.
- Current canonical fixture behavior is preserved except for improved provenance/mapping visibility.
- Tests prove that prior/profile association no longer depends on token overlap.
- Tests cover malformed mapping targets and missing mapped priors.
- Reports and logs preserve mapping provenance.
- No clinical thresholds, utilities, final recommendations, or hidden scores are added.
- Verification passes: full pytest, py_compile, CLI help, canonical validate, canonical report, report with log, and JSONL parse.

### P1-003: Canonical Synthetic Variant Fixtures

Scope:

- Promote inspectable synthetic CDE variants into `examples/` or a documented canonical fixture directory.
- Initial variants should cover stable, low eGFR, high potassium, low SBP, no follow-up, prior DKA, and missing labs/missing oxygen requirement.

Acceptance criteria:

- Each fixture is valid against the current CDE model.
- Each fixture is explicitly labeled synthetic and non-PHI.
- Each fixture documents provenance from the canonical v0.3 stable fixture or other source material.
- CLI `validate` passes for all valid fixtures.
- Expected status changes are tested through the public pipeline or CLI boundary.
- Tests no longer rely only on hidden in-test mutations for core scenario coverage.
- No new clinical thresholds or unsupported assumptions are introduced.
- README/DEMO or fixture docs list the available scenario fixtures.
- Verification passes: full pytest, py_compile, CLI help, validate all new fixtures, at least one report generation per representative fixture class.

### P1-004: Normalized Status Ledger

Scope:

- Define a typed status-ledger row or equivalent contract for all visible component states.
- Make missing, blocked, unsupported, deferred, active, present, resolved, sampled, and eligible statuses consistently visible.
- Let report rendering and provenance logging consume the shared status contract where practical.

Acceptance criteria:

- A typed ledger model captures component, identifier, status, reason, source/provenance, and optional related entity IDs.
- Safety gates, priors, Monte Carlo priors, uncertainty-budget items, VOI items, and Decision Profiles can project into ledger rows.
- Report renderer can display unresolved items from the ledger without losing current sections.
- Provenance logger can emit status records from the ledger or a clearly equivalent projection.
- Tests prove that deferred, unsupported, missing, and blocked items do not disappear.
- Tests prove that report/log outputs remain status-only where logs are concerned and do not add raw case text.
- Existing Phase 0 report guardrails remain intact.
- Verification passes: full pytest, py_compile, CLI help, canonical validate, canonical report, report with log, and JSONL parse.

### P1-005: Model Module Split

Scope:

- Refactor `pdde/models.py` into focused modules only after the contracts from P1-002 through P1-004 are stable enough.
- Candidate split: input models, component result models, pipeline models, report/provenance models, and legacy/planned models.

Acceptance criteria:

- Public imports remain backwards compatible or migration is explicitly documented.
- Each new model module has a clear responsibility.
- No runtime behavior changes are made beyond import paths.
- Tests cover serialization/deserialization for the same model surfaces as before.
- Type-checking or import smoke checks cover all `pdde` modules.
- `pdde/models.py` either remains a compatibility re-export module or has an explicit migration note.
- Verification passes: full pytest, py_compile, CLI help, canonical validate, canonical report, report with log, and JSONL parse.

### P1-006: Report Section Registry Or Schema Contract

Scope:

- Make report section order, required advisory language, and status-preservation obligations explicit.
- Keep Markdown rendering deterministic and simple.

Acceptance criteria:

- Required report sections are defined in one registry, schema, or equivalent contract.
- Tests assert the renderer includes every required section in deterministic order.
- Advisory-only, uncalibrated, not-clinically-validated, and no-final-recommendation language remains required.
- The renderer fails clearly or tests fail if a required section is dropped.
- Reports continue to show missing, unsupported, blocked, and deferred items.
- No HTML/PDF/UI generation is added.
- No recommendation wording, option ranking, or hidden score is added.
- Verification passes: full pytest, py_compile, CLI help, canonical report, and report guardrail assertions.

### P1-007: Local Overlay Verification Contract

Scope:

- Define the schema/fields required for local operational overlay rules.
- Keep unverified local rules visibly draft/deferred.

Acceptance criteria:

- Local overlay rules have explicit owner, status, source, review cadence, and last-reviewed fields where applicable.
- Missing owner/status/source/review cadence fails validation or remains clearly deferred.
- Reports display local overlay verification state.
- JSONL logs record local overlay status without PHI or operationally sensitive free text.
- No local rule becomes active solely because it exists in a draft source file.
- External local workflow owner input is documented if needed.
- Verification passes: focused model/loader/report/log tests plus full pytest and canonical CLI checks.

### P1-008: AI Answer Mapping Interface

Scope:

- Prepare the boundary for later AI answer mapping only after direct-CDE contracts are stable.
- Map AI answer content into structured claims, omissions, or overstatements that the existing deterministic safety/profile layers can consume.

Acceptance criteria:

- Explicit user approval to start AI mapping exists.
- Input/output contract is typed and separate from direct CDE simulation.
- Free-text AI answers do not directly modify priors, safety gates, thresholds, or recommendations.
- Mapped claims feed structured claim-type fields or equivalent deterministic inputs.
- `wrong_indication_blocks` can be evaluated from structured mapped claims.
- Unsupported/unmapped claims remain visible and do not silently pass.
- Tests cover sotalol-as-HF-beta-blocker and GLP-1-for-HF-prevention examples from source materials.
- No LLM-unverified priors are admitted into direct simulation.
- No final clinical recommendation or answer grade is produced as the primary artifact.
- Verification passes: focused claim-mapping tests, full pytest, py_compile, CLI help, direct CDE canonical report unchanged except where explicitly mapped claim inputs are provided.

### P1-009: Citation/Evidence Audit Handoff

Scope:

- Define what citation/evidence audit would need later without implementing the full audit.
- Keep this as a handoff/spec task unless explicitly promoted.

Acceptance criteria:

- Evidence-source fields needed for future audit are documented.
- Report/provenance gaps are listed.
- No citation scoring, source truth claims, or automated evidence validation is added.
- Relationship to `pdde_v0_3_first_principles_final/05_PRIOR_AND_UNCERTAINTY_GOVERNANCE.md` is documented.
- Open user/governance inputs are listed.

### P1-010: Calibration And Outcome Anchoring Prerequisites

Scope:

- Define data, governance, and metric prerequisites for later calibration.
- Do not implement calibration curves or outcome claims.

Acceptance criteria:

- Required labels/outcomes are listed.
- Required governance approvals and data handling constraints are listed.
- Current logs are assessed for whether they can seed calibration workflows without PHI.
- No report language implies validation or calibrated risk.
- No outcome claims are added.
- Open user/governance inputs are listed.

## Phase 1 Definition Of Done

Phase 1 should be considered complete only when:

- Phase 0 baseline and generated-artifact policy are documented.
- Domain-pack mappings remove Python-only routing and token-overlap association.
- Canonical synthetic variant fixtures exist and are documented.
- Report/log status visibility is driven by a stable shared contract or clearly equivalent projection.
- Model organization is maintainable enough for later AI mapping.
- Local overlay verification requirements are explicit and unverified rules remain deferred.
- AI answer mapping has either remained deferred or been introduced only through a typed deterministic interface.
- All tests and canonical CLI verification commands pass.
- Reports still avoid final recommendations, rankings, hidden scores, validated-risk language, and clinical deployment claims.

## Required Verification For Any Implementation Task

Unless a task is documentation-only, run:

```bash
python -m pytest
python -m py_compile pdde/*.py
python -m pdde --help
python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --iterations 5 --seed 17
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl --iterations 5 --seed 17
python -c "from pathlib import Path; import json; records=[json.loads(line) for line in Path('logs/hf_cde_stable.jsonl').read_text(encoding='utf-8').splitlines()]; print(f'{len(records)} valid JSONL records')"
```

Task-specific tests should also be added or updated for the changed behavior.

## User Input Needed Before Implementation

- Root git strategy and generated-artifact policy for `reports/` and `logs/`.
- Whether Phase 1 should start with P1-001 as ranked.
- Whether explicit domain-pack mapping changes may alter source fixture shape.
- Local overlay owner/status/source/review-cadence details.
- Whether and when AI answer mapping should be authorized.
- Example AI answer artifacts and boundaries if AI mapping is started.
- Any retrospective/outcome data governance path for calibration planning.

## Stop Conditions

Stop and ask for user direction if a task would require:

- PHI or real patient data.
- clinical deployment or clinical decision support claims.
- new clinical thresholds, utilities, weights, priors, or recommendation labels not present in governed source files.
- root git initialization without explicit approval.
- destructive changes to generated reports/logs or nested repositories.
- AI answer mapping before the direct-CDE contract hardening gate is explicitly waived.

## Recommended First Task

The recommended first task is `P1-001: Tag/archive Phase 0 baseline and decide root git/generated-artifact policy`.

Reason: it is the only top-ranked task that clearly requires user input before safe implementation. After that, `P1-002` should be the first engineering task because explicit domain-pack mappings remove the most fragile assumptions without adding new clinical claims.
