# Citation/Evidence Audit Handoff

## Status

P1-009 is a handoff/specification task only. It documents what a later citation and evidence-support audit would need, but it does not implement citation scoring, source truth claims, network lookups, retraction checks, abstract-claim alignment, or automated evidence validation.

Current PDDE reports and logs preserve source references and provenance strings. They do not claim that those sources have been independently verified.

## Purpose

The future citation/evidence audit layer should answer narrow governance questions:

- Which controlled source or evidence object supports each domain-pack prior, hard gate, VOI item, uncertainty category, local overlay item, and mapped AI-answer claim?
- Is the support relationship reviewed, pending, conflicting, stale, retracted, or out of scope?
- Who owns the evidence review, when was it last reviewed, and what update cadence applies?
- What report and provenance fields should show that status without implying clinical validation?

It should not produce a clinical recommendation, truth score, trust score, source-quality score, or answer grade.

## Relationship To Prior And Uncertainty Governance

`pdde_v0_3_first_principles_final/05_PRIOR_AND_UNCERTAINTY_GOVERNANCE.md` is the controlling Phase 0 governance anchor for prior provenance and uncertainty language. It requires every prior to carry provenance and calibration metadata, and it warns that Monte Carlo can create false precision unless source and uncertainty are visible.

The future evidence audit should extend that governance discipline from priors to all evidence-bearing artifacts:

- priors in `domain_pack.prior_policy`
- hard gates in `domain_pack.hard_gates`
- explicit mappings in `domain_pack.mappings`
- VOI variables and uncertainty-budget categories
- local overlay verification metadata
- mapped AI-answer claims from `AIAnswerMappingResult`
- report sections that cite or summarize source support

The audit layer should remain subordinate to the current advisory-only, uncalibrated, non-deployment guardrails.

## Future Evidence-Source Fields

These fields are candidates for a later source registry or evidence dossier model. They are not runtime requirements in P1-009.

| Field | Needed For | Why |
|---|---|---|
| `evidence_source_id` | all evidence-bearing records | Stable source key for reports/logs without raw citation text duplication. |
| `source_type` | all evidence sources | Distinguish guideline, trial, review, local policy, expert panel, registry, model-generated draft, or other source class. |
| `bibliographic_ids` | literature sources | Store DOI, PMID, guideline ID, NCT, ISBN, or other stable IDs when available. |
| `canonical_url` | online sources | Preserve source location without asserting freshness. |
| `title_or_label` | human review | Let reviewers identify the source without full raw document storage. |
| `publisher_or_organization` | guidelines/policies | Identify source governance body. |
| `publication_date` | literature/guidelines | Support freshness review. |
| `version` | guidelines/local policies | Identify which version was reviewed. |
| `retrieved_at` | online sources | Record when a source was last fetched or inspected. |
| `evidence_owner` | all governed sources | Name accountable review owner or team. |
| `review_status` | all governed sources | Preserve draft, pending_review, reviewed, superseded, retracted, conflicting, or out_of_scope state. |
| `last_reviewed` | all governed sources | Support review cadence and drift checks. |
| `review_cadence` | all governed sources | Define expected refresh interval. |
| `supported_entity_type` | source-to-project mapping | Identify prior, gate, claim type, VOI variable, uncertainty category, local overlay item, or report statement. |
| `supported_entity_id` | source-to-project mapping | Link the source to a concrete project entity. |
| `support_scope` | source-to-project mapping | Capture population, intervention, comparator, outcome, setting, and time horizon when applicable. |
| `support_status` | source-to-project mapping | Record reviewed support state without a numeric score. |
| `limitations` | source-to-project mapping | Preserve caveats, extrapolation, mismatch, or uncertainty notes. |
| `audit_decision_by` | review workflow | Identify reviewer or governance group. |
| `audit_decision_at` | review workflow | Date the support decision was made. |
| `audit_notes_reference` | review workflow | Point to a governed review note without logging sensitive free text. |

## Current Report Gaps

Current Markdown reports preserve source references and advisory warnings, but they do not yet include:

- a dedicated evidence-source registry section
- bibliographic identifiers such as DOI, PMID, guideline ID, or canonical URL
- source freshness, retrieval date, or retraction state
- explicit source-to-entity support status for each prior, gate, VOI item, uncertainty item, or mapped claim
- reviewer/owner identity for evidence support decisions beyond existing local overlay metadata presence
- population, setting, outcome, and time-horizon matching for cited support
- distinction between source existence and source support for a specific claim
- citation conflict/supersession visibility

Reports must continue to avoid final recommendation language, source truth claims, and clinical validation claims.

## Current Provenance Gaps

Current JSONL provenance records are status-only and intentionally privacy-preserving. They do not log full raw case text, patient-state payloads, gate evidence strings, local overlay owner/source/review values, raw AI answer text, or simulation sample arrays.

For future evidence audit, provenance logs would need additional status-safe fields:

- `evidence_source_id`
- `source_type`
- `supported_entity_type`
- `supported_entity_id`
- `support_status`
- `review_status`
- `last_reviewed`
- `retrieved_at`
- `bibliographic_id_present`
- `canonical_url_present`
- `retraction_status`
- `conflict_status`

The log should continue to prefer IDs, statuses, counts, timestamps, paths, and safe references over raw clinical text or copied source passages.

## Deferred Audit Workflow

A later implementation should proceed only after governance input exists:

1. Create a governed evidence-source registry.
2. Link domain-pack priors, hard gates, mappings, uncertainty/VOI items, local overlay items, and mapped claim types to explicit `evidence_source_id` values.
3. Add strict loader validation for required evidence metadata only after the schema is approved.
4. Add report/provenance visibility for audit status without numeric source scoring.
5. Add automated metadata checks only if explicitly scoped, reviewed, and network/data-access rules are clear.

## Out Of Scope For P1-009

- Citation scoring.
- Source truth claims.
- Automated source verification.
- DOI/PMID existence checks.
- Retraction Watch, Crossref, PubMed, guideline, or web lookups.
- Abstract-claim alignment.
- LLM-based citation judgment.
- Answer grading.
- New clinical thresholds, priors, utilities, or formulas.
- Final clinical recommendations.
- CLI behavior changes.
- Report wording that implies validation or source support has been audited.

## Open User And Governance Inputs

- Who owns evidence review for the HF ED discharge domain pack?
- What source types are allowed for each entity class: gate, prior, VOI item, uncertainty item, local overlay item, mapped claim type?
- Which bibliographic identifiers are required: DOI, PMID, guideline ID, NCT, URL, local policy ID, or other IDs?
- Is network access allowed for future source metadata checks, and from which sources?
- Should source metadata be committed in domain packs, stored in separate evidence registries, or generated as release artifacts?
- What review statuses and support statuses are acceptable?
- What cadence should govern source refresh and retirement review?
- How should conflicting, superseded, or retracted sources be displayed?
- What source snippets, if any, may be stored without creating copyright, PHI, or governance risk?
- What audit trail is required for reviewer decisions?

## Recommended Next Step

Keep full citation/evidence audit deferred. The next queued Phase 1 handoff task is `P1-010: Calibration And Outcome Anchoring Prerequisites`, which should define labels, outcomes, governance approvals, and data-handling constraints without adding calibration curves or outcome claims.
