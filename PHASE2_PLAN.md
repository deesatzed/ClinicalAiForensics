# Phase 2 Plan

## Planning Status

Phase 2 is active by explicit user instruction after completion of `phase1-baseline`.

The Phase 1 baseline is the annotated git tag:

```text
phase1-baseline
```

At Phase 2 activation, `phase1-baseline` points to:

```text
06c5d3e docs: complete phase 1 review
```

Phase 2 starts from the existing local, synthetic, deterministic, advisory-only CLI/API. It must not weaken Phase 0 or Phase 1 safety, privacy, provenance, explicit-mapping, status-ledger, report-contract, local-overlay, or deterministic AI-answer mapping guardrails.

## Phase 2 Objective

Phase 2 should convert the Phase 1 handoff documents into explicit governance contracts that can be reviewed before any clinical validation, evidence checking, calibration, local-rule activation, or broader AI-answer analysis.

The first Phase 2 slice is deliberately narrow: define typed evidence-source and evidence-support registry models without automated source truth validation.

## Non-Goals

- No final clinical recommendations.
- No safe-discharge or unsafe-discharge conclusion.
- No option ranking, validated risk, calibrated-risk language, hidden score, utility, threshold, weight, prior, or decision-fitness formula.
- No LLM clinical judgment, LLM extraction, answer grading, or CLI free-text AI-answer mapping.
- No automated evidence truth validation, citation scoring, source-quality scoring, web lookup, retraction lookup, DOI/PMID validation, or abstract-claim alignment.
- No calibration metrics, outcome linkage, expert-label collection, clinician-action analysis, prior updating, drift detection, or outcome claims.
- No PHI handling or production deployment.
- No activation of local clinical rules from draft or incomplete metadata.

## Ranked Task List

| Rank | Task ID | Next Task | Estimated Chance Of Improving Goal | Why | Risk | Requires User Input? |
|---:|---|---|---:|---|---|---|
| 1 | P2-001 | Evidence Source Registry Models | 70% | Turns P1-009 evidence-audit prerequisites into strict typed contracts without validating source truth. | Low to medium; model names can churn if overfit. | No |
| 2 | P2-002 | Domain-Pack Evidence Link Scaffold | 65% | Lets domain-pack gates, priors, mappings, VOI items, uncertainty categories, and mapped claim types reference explicit evidence IDs. | Medium; requires careful backwards compatibility with current fixtures. | Possibly |
| 3 | P2-003 | Evidence Status Report And Provenance Visibility | 60% | Makes source review state visible while keeping logs status-only and avoiding truth claims. | Medium; report wording can imply too much if careless. | Possibly |
| 4 | P2-004 | Governed Local Overlay Metadata Completion Path | 55% | Converts draft local overlay gaps into explicit owner/source/review requirements without activating local rules. | Medium; needs operational governance details. | Yes |
| 5 | P2-005 | Broader AI Answer Mapping Specification | 50% | Extends the API-only deterministic boundary toward omissions and overstatements without answer grading. | High scope-creep risk. | Yes |
| 6 | P2-006 | Calibration Label And Outcome Protocol | 45% | Converts P1-010 prerequisites into a governed schema/protocol before metrics. | High; requires clinical, privacy, statistical, and data-owner governance. | Yes |
| 7 | P2-007 | Additional Synthetic Domain Or Scenario Fixtures | 40% | Tests whether the contracts generalize without PHI or deployment. | Medium; needs domain selection and source governance. | Yes |

## Task Acceptance Criteria

### P2-001: Evidence Source Registry Models

Scope:

- Add typed evidence-source, evidence-support-link, and evidence-registry models.
- Preserve strict validation and serialization.
- Preserve status-only/privacy discipline.
- Do not integrate with reports, provenance logs, loaders, or domain-pack validation yet unless a later task explicitly scopes that work.

Acceptance criteria:

- Evidence sources have stable IDs, source type, title/label, and review status.
- Support links connect explicit evidence source IDs to explicit project entity IDs and entity types.
- Registry validation rejects duplicate source IDs, duplicate source/entity links, and support links to unknown evidence source IDs.
- Reviewed source/support statuses require review or audit metadata.
- Extra raw text fields such as source passages are rejected by strict models.
- `pdde.models` continues to re-export public model contracts for backwards compatibility.
- Tests cover creation, validation failure, source traceability, serialization, and no raw-source-text fields.
- No runtime pipeline, CLI, report, provenance, clinical logic, recommendation, LLM, evidence truth validation, calibration, outcome linkage, PHI, threshold, utility, prior, or formula behavior is added.

### P2-002: Domain-Pack Evidence Link Scaffold

Scope:

- Add optional source-ID references to domain-pack evidence-bearing records only after P2-001 models exist.
- Keep current canonical fixtures backwards compatible.
- Validate only explicit IDs when an evidence registry is supplied.

Acceptance criteria:

- Existing canonical CDE/domain-pack validation still passes.
- Optional evidence references can be loaded and preserved.
- Unknown evidence references fail clearly only when a registry validation path is explicitly used.
- Missing evidence references stay visible as pending/deferred rather than implying support.
- No automated evidence truth validation or source scoring is added.

### P2-003: Evidence Status Report And Provenance Visibility

Scope:

- Surface evidence registry/support statuses in reports and status-only provenance records.
- Preserve report-contract advisory language.

Acceptance criteria:

- Reports distinguish source existence from reviewed support status.
- Logs emit IDs/statuses/presence booleans only, not source passages or copied citations.
- Missing, pending, conflicting, superseded, retracted, and out-of-scope evidence states remain visible.
- No source truth claims, source-quality scores, citation scores, or automated evidence validation are added.

### P2-004: Governed Local Overlay Metadata Completion Path

Scope:

- Define or load explicit local overlay owner/source/review metadata if governance input exists.
- Keep local clinical rules non-activating unless safe activation criteria are separately approved.

Acceptance criteria:

- Missing owner/source/review fields remain visible.
- Verified metadata can be represented without logging raw operational details.
- No local workflow rule becomes active solely because metadata exists.
- User/governance input is documented if unavailable.

### P2-005: Broader AI Answer Mapping Specification

Scope:

- Extend the API-only deterministic mapping contract toward omissions and overstatements only with governed examples.

Acceptance criteria:

- No CLI free-text mapping is added unless explicitly approved.
- Raw AI answer text is not stored in pipeline results, reports, or logs.
- Mapped claims remain explicit, source-backed, and deterministic.
- No answer grade or final recommendation is produced.

### P2-006: Calibration Label And Outcome Protocol

Scope:

- Define governed label and outcome schemas only after required approvals and data rules are available.

Acceptance criteria:

- Label/outcome schemas do not store PHI in source control or ordinary logs.
- No calibration metric is computed without numeric targets and governed labels/outcomes.
- Report language remains calibration-pending until real governance and data exist.

### P2-007: Additional Synthetic Domain Or Scenario Fixtures

Scope:

- Add synthetic non-PHI fixtures only from governed source material.

Acceptance criteria:

- Fixtures are explicitly synthetic/non-PHI.
- Existing Phase 0/1 CLI and report guardrails remain intact.
- No new clinical thresholds, weights, utilities, priors, or formulas are invented.

## Required Verification

For any Phase 2 task, run:

```bash
python -m pytest
python -m py_compile pdde/*.py
python -m pdde --help
python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --iterations 5 --seed 17
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl --iterations 5 --seed 17
```

Also validate all seven root `examples/*.json` fixtures, generate Markdown reports for all seven fixtures, parse `logs/hf_cde_stable.jsonl` as JSONL, and run any task-specific tests.

## Stop Conditions

Stop and request user input before any task that would require:

- PHI or real patient data.
- clinical deployment or clinical decision support claims.
- final recommendations, option ranking, outcome claims, calibrated risk, or hidden scoring.
- LLM extraction, LLM clinical judgment, answer grading, or free-text CLI answer mapping.
- automated evidence truth validation, citation scoring, source-quality scoring, or network source checks.
- calibration metrics, outcome linkage, expert labels, clinician action capture, or prior updating without governed prerequisites.
- local clinical rule activation.
- new clinical thresholds, utilities, weights, priors, formulas, or recommendation labels not present in governed source files.

## Recommended First Task

The recommended first Phase 2 task is `P2-001: Evidence Source Registry Models`.

Reason: it is unblocked, directly follows `EVIDENCE_AUDIT_HANDOFF.md`, and creates a typed review contract without changing runtime clinical behavior, report wording, provenance semantics, or CLI behavior.
