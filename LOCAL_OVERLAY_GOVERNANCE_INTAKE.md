# Local Overlay Governance Intake

## Purpose

This template collects the minimum governed metadata required before local overlay records can move beyond draft or deferred visibility. It is intended for local workflow, monitoring, rescue-pathway, or operational-context metadata that may affect how a decision profile is interpreted, but that is not yet verified enough to activate any local clinical rule.

Use this document to gather accountable ownership, source, review, version, applicability, and safety/privacy metadata before any implementation task changes local overlay behavior.

## Non-Activation Rule

Completing this template does not activate local clinical rules. It only supplies metadata that may later let PDDE validate local overlay records as metadata-complete.

Local overlay metadata remains non-activating unless a later governed task explicitly approves activation criteria, adds tests, updates project-control decisions, and preserves all safety/privacy guardrails.

## Required Metadata

| Field | Required? | Description | Example | Provided Value |
|---|---|---|---|---|
| local overlay/workflow item ID | Yes | Stable identifier for the local metadata item. | `hf_ed_followup_workflow` |  |
| local overlay title/name | Yes | Human-readable name for the local metadata item. | HF ED follow-up scheduling workflow |  |
| domain/site applicability | Yes | Domain, site, unit, service, or workflow context where the metadata applies. | Synthetic HF ED discharge demo site |  |
| accountable owner | Yes | Accountable person, role, committee, or operational group. | ED-HF workflow governance committee |  |
| owner role | Yes | Role of the accountable owner. | Local clinical operations owner |  |
| authoritative source reference | Yes | Non-PHI pointer to the source that governs the metadata. Avoid copying raw operational text. | `local_policy:HF-ED-FU-v0-demo` |  |
| source type | Yes | Type of source that supports the metadata. | policy, workflow document, committee decision, protocol, memo |  |
| verification status | Yes | Current governance status using the allowed values below. | `verified_metadata_only` |  |
| reviewer or review body | Yes | Person, role, committee, or review body that verified the metadata. | HF ED governance review group |  |
| review cadence | Yes | Expected review frequency. | quarterly |  |
| last-reviewed date | Yes | Date the metadata was last reviewed. | 2026-05-13 |  |
| next-review due date | Yes | Date by which the metadata should be reviewed again. | 2026-08-13 |  |
| version | Yes | Version or revision identifier for the metadata source. | `v0-demo` |  |
| effective date | Yes | Date the metadata became applicable. | 2026-05-13 |  |
| expiration date if applicable | Conditional | Required if the source or governance approval has an expiration. | 2026-12-31 |  |
| change history reference | Yes | Non-PHI pointer to a changelog, decision log, or governance record. | `governance_log:HF-ED-FU-demo-001` |  |
| whether this is metadata-only or activation-seeking | Yes | State whether the submission requests metadata visibility only or future activation review. | metadata-only |  |
| explicit confirmation that metadata remains non-activating | Yes | Affirm that the metadata should not activate a local clinical rule. | Confirmed metadata-only, non-activating |  |
| explicit activation criteria if future activation is ever requested | Conditional | Required only for future activation review; leave as not requested for metadata-only intake. | Not requested; would require separate approval and tests |  |
| safety/privacy notes | Yes | Notes about safety, audit, rollback, and privacy boundaries. | No PHI, no raw operational text, no clinical recommendation |  |
| PHI/PII handling statement | Yes | State whether the source contains PHI/PII and how it is kept out of PDDE artifacts. | Synthetic/non-PHI metadata only |  |

## Verification Status Options

Allowed governance-intake values:

- `draft`: Metadata is incomplete or not yet reviewed.
- `pending_review`: Metadata has been submitted but not reviewed.
- `verified_metadata_only`: Metadata has been reviewed as complete, but it does not activate any local clinical rule.
- `rejected`: Metadata was reviewed and rejected.
- `expired`: Metadata was previously reviewed but is now outside its review window or expiration date.
- `superseded`: Metadata has been replaced by a newer governance record.

These intake statuses are governance-documentation values. Mapping them into runtime local overlay statuses requires a separate implementation task and must not imply local rule activation.

## Activation Boundary

Before any local rule could become active, the project would require all of the following:

- explicit user/governance approval for activation scope.
- source review confirming the local rule text, source, owner, applicability, and review status.
- test cases covering active, blocked, missing, expired, superseded, rejected, and malformed local overlay records.
- safety review confirming that local rules cannot create final clinical recommendations, hidden scores, option rankings, or unsupported clinical thresholds.
- rollback plan describing how to disable or revert the local rule.
- audit trail recording who approved activation, when, why, and against which source version.
- clear non-PHI handling for all source references, tests, reports, and logs.
- project-control decision entry in `DECISIONS.md` before activation behavior is implemented.

## Example Completed Metadata-Only Entry

This example is synthetic and non-PHI. It does not describe a real hospital policy.

| Field | Required? | Description | Example | Provided Value |
|---|---|---|---|---|
| local overlay/workflow item ID | Yes | Stable identifier for the local metadata item. | `hf_ed_followup_workflow` | `demo_hf_ed_followup_metadata` |
| local overlay title/name | Yes | Human-readable name for the local metadata item. | HF ED follow-up scheduling workflow | Synthetic HF ED follow-up metadata |
| domain/site applicability | Yes | Domain, site, unit, service, or workflow context where the metadata applies. | Synthetic HF ED discharge demo site | Synthetic HF ED discharge demo only |
| accountable owner | Yes | Accountable person, role, committee, or operational group. | ED-HF workflow governance committee | Synthetic workflow review group |
| owner role | Yes | Role of the accountable owner. | Local clinical operations owner | Demo governance owner |
| authoritative source reference | Yes | Non-PHI pointer to the source that governs the metadata. | `local_policy:HF-ED-FU-v0-demo` | `demo_source:HF-ED-FU-v0` |
| source type | Yes | Type of source that supports the metadata. | policy, workflow document, committee decision, protocol, memo | synthetic workflow memo |
| verification status | Yes | Current governance status using the allowed values below. | `verified_metadata_only` | `verified_metadata_only` |
| reviewer or review body | Yes | Person, role, committee, or review body that verified the metadata. | HF ED governance review group | Synthetic governance reviewer |
| review cadence | Yes | Expected review frequency. | quarterly | quarterly |
| last-reviewed date | Yes | Date the metadata was last reviewed. | 2026-05-13 | 2026-05-13 |
| next-review due date | Yes | Date by which the metadata should be reviewed again. | 2026-08-13 | 2026-08-13 |
| version | Yes | Version or revision identifier for the metadata source. | `v0-demo` | `v0-demo` |
| effective date | Yes | Date the metadata became applicable. | 2026-05-13 | 2026-05-13 |
| expiration date if applicable | Conditional | Required if the source or governance approval has an expiration. | 2026-12-31 | 2026-12-31 |
| change history reference | Yes | Non-PHI pointer to a changelog, decision log, or governance record. | `governance_log:HF-ED-FU-demo-001` | `demo_governance_log:001` |
| whether this is metadata-only or activation-seeking | Yes | State whether the submission requests metadata visibility only or future activation review. | metadata-only | metadata-only |
| explicit confirmation that metadata remains non-activating | Yes | Affirm that the metadata should not activate a local clinical rule. | Confirmed metadata-only, non-activating | Confirmed non-activating |
| explicit activation criteria if future activation is ever requested | Conditional | Required only for future activation review; leave as not requested for metadata-only intake. | Not requested; would require separate approval and tests | Not requested |
| safety/privacy notes | Yes | Notes about safety, audit, rollback, and privacy boundaries. | No PHI, no raw operational text, no clinical recommendation | Synthetic only; no PHI; no local rule activation |
| PHI/PII handling statement | Yes | State whether the source contains PHI/PII and how it is kept out of PDDE artifacts. | Synthetic/non-PHI metadata only | Synthetic/non-PHI metadata only |

## Questions Needing User/Governance Input

- Which local overlay or workflow item IDs should PDDE represent?
- What local title/name should each item use?
- Which domain, site, unit, service, or workflow context does each item apply to?
- Who is the accountable owner for each item?
- What is the owner's role?
- What authoritative source reference should PDDE store for each item?
- What source type should be used?
- What verification status should be assigned?
- Who reviewed the metadata, or which review body owns the review?
- What review cadence applies?
- What was the last-reviewed date?
- What is the next-review due date?
- What version is being represented?
- What effective date applies?
- Does the metadata expire, and if so when?
- What non-PHI change-history reference should be retained?
- Is this request metadata-only or activation-seeking?
- Can governance explicitly confirm that the metadata remains non-activating?
- If activation is ever requested, what explicit activation criteria, tests, safety review, rollback plan, and audit trail are required?
- What safety/privacy notes must be preserved?
- Can governance confirm that no PHI/PII or raw operational text should be stored in PDDE reports, logs, fixtures, or source control?

---

## My First Local Overlay Entry

| Field | Provided Value |
|---|---|
| Local overlay/workflow item ID | TUH-HF-ED-FOLLOWUP-001 |
| Local overlay title/name | Heart Failure ED Discharge Follow-up Visibility Item |
| Domain/site applicability | Temple University Hospital ED; adult heart failure ED discharge workflow |
| Accountable owner | Wayne Satz, MD |
| Owner role | Physician informaticist |
| Authoritative source reference | Draft local workflow notes; not formally approved |
| Source type | Draft local workflow metadata |
| Verification status | draft |
| Reviewer or review body | Not yet reviewed |
| Review cadence | TBD |
| Last-reviewed date | Not yet reviewed |
| Next-review due date | TBD |
| Version | 0.1-draft |
| Effective date | Not active |
| Expiration date if applicable | Not applicable |
| Change history reference | Initial metadata-only draft entry |
| Metadata-only or activation-seeking? | metadata-only |
| Explicit confirmation that metadata remains non-activating | Yes. This entry must not activate clinical rules. |
| Explicit activation criteria if future activation is ever requested | Requires formal governance approval, reviewed source document, test cases, safety review, rollback plan, audit trail, and DECISIONS.md update. |
| Safety/privacy notes | Synthetic/non-PHI metadata only. |
| PHI/PII handling statement | Do not include patient names, MRNs, dates of birth, addresses, phone numbers, raw clinical notes, or other PHI/PII. |
