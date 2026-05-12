# Calibration And Outcome Anchoring Prerequisites

## Status

P1-010 is a handoff/specification task only. It defines what a later calibration and outcome-anchoring layer would need, but it does not implement calibration curves, reliability metrics, prior updating, drift detection, outcome linkage, outcome claims, or clinical deployment behavior.

Current PDDE reports and logs preserve calibration status as pending or uncalibrated. They do not claim validated risk, calibrated risk, outcome improvement, or clinical effectiveness.

## Purpose

The future calibration and outcome-anchoring layer should answer narrow governance questions:

- What labels are needed to evaluate whether Decision Profile statuses match expert review?
- What clinician action and local execution facts are needed to compare displayed profiles with real workflow choices?
- What outcome anchors are governed, available, and appropriate for the specific CDE domain?
- What data approvals, privacy constraints, and review protocols are required before real cases or outcomes are linked?
- What report and provenance fields can show calibration status without implying clinical validation?

It should not produce a final clinical recommendation, safe-discharge conclusion, unsafe-discharge conclusion, outcome benefit claim, calibrated risk claim, hidden score, or answer grade.

## Controlling Source Direction

`pdde_v0_3_first_principles_final/05_PRIOR_AND_UNCERTAINTY_GOVERNANCE.md` identifies four possible calibration targets:

- expert defensibility labels
- clinician action distribution
- outcome anchors
- adverse event or near-miss review

`pdde_v0_3_first_principles_final/02_REVISED_FINAL_PLAN.md` places calibration and outcome anchoring after direct CDE simulation, AI answer mapping, local overlay verification, and citation/evidence audit. `STANDARDS.md` requires no outcome claims without outcome data and appropriate governance, and no clinical deployment until calibration logging exists and governance approves the mode.

P1-010 keeps those boundaries intact.

## Required Label Families

These label families are prerequisites for later calibration. They are not runtime fields in P1-010.

| Label Family | Needed For | Required Governance Detail |
|---|---|---|
| `expert_defensibility_label` | Evaluate whether an option status is defensible under the displayed assumptions. | Reviewer role, review protocol, allowed label set, disagreement workflow, review date, case blinding policy. |
| `expert_missingness_label` | Evaluate whether missing inputs were surfaced with appropriate urgency. | Required data dictionary, missingness categories, reviewer instructions, adjudication policy. |
| `expert_safety_gate_label` | Evaluate whether hard-gate status matched expert assessment. | Gate-specific review criteria, reviewer role, adjudication policy, source version. |
| `clinician_action_taken` | Compare displayed option profiles with actual clinician choices. | Action taxonomy, local workflow context, timestamp, whether PDDE output was visible or silent. |
| `local_execution_label` | Assess whether local workflow assumptions were executable. | Local owner, operational source, verification status, review cadence, site applicability. |
| `adverse_event_or_near_miss_label` | Support safety review and error analysis. | Event taxonomy, attribution rules, reviewer role, escalation workflow, privacy handling. |
| `case_inclusion_label` | Define whether a CDE belongs in a calibration cohort. | Domain inclusion/exclusion criteria, synthetic vs real status, data completeness requirements. |
| `review_quality_label` | Track whether labels themselves are usable. | Inter-reviewer agreement plan, audit trail, incomplete/disputed label status. |

No label family should be treated as a gold standard without a documented review protocol and disagreement process.

## Candidate Outcome Anchors Requiring Governance

Outcome anchors must be selected and governed before implementation. Candidate anchors for the HF ED discharge domain may include:

- return acute-care encounter after the indexed decision
- hospitalization after the indexed decision
- medication-related harm or contraindication event
- lab-monitoring completion after discharge when relevant
- follow-up completion when relevant
- clinician-documented near miss or adverse event review
- patient-centered feasibility signal when governed and available

The actual time horizons, attribution rules, censoring rules, and data source definitions are not defined in the current canonical files. They require explicit user, clinical, operational, and privacy governance before any implementation.

## Required Governance Approvals

Later calibration or outcome linkage requires explicit governance before code activation:

- IRB, exempt determination, or equivalent human-subjects review decision.
- HIPAA/privacy review and data-use approval for any PHI or real patient data.
- Data owner approval for source systems, extracts, logs, and retention.
- Clinical owner approval for label definitions, outcome anchors, and review protocol.
- Security approval for storage, access control, encryption, and audit trails.
- Statistical review for metrics, cohort definitions, time horizons, and sample-size expectations.
- Documentation of whether PDDE output is silent, research-only, governance-review-only, or visible to clinicians.
- A release decision describing whether generated logs are local artifacts, governed research records, or release artifacts.

Without those approvals, calibration remains pending and outcome anchoring remains deferred.

## Data Handling Constraints

Current Phase 0 and Phase 1 fixtures are synthetic and non-PHI. Future calibration data must preserve this separation unless governance explicitly changes the mode.

Minimum constraints for real or retrospective data:

- Use de-identified or limited datasets where possible.
- Keep PHI out of source control, generated Markdown reports, and ordinary development logs.
- Use stable non-identifying case/run keys for calibration linkage.
- Store outcome labels and reviewer labels in a governed location, not in ad hoc append-only local logs.
- Avoid copying raw chart text, raw patient-state payloads, gate evidence strings, raw AI answers, local owner/source/review values, or source passages into calibration logs unless explicitly approved.
- Preserve model/package version, domain-pack version, CDE schema version, seed, iteration count, and source references for reproducibility.
- Maintain a retention and deletion policy before collecting real cases.

## Metric Prerequisites

Calibration metrics cannot be computed from the current Phase 1 outputs alone.

| Metric Or Analysis | Required Before Use | Current Status |
|---|---|---|
| Expert-label agreement | At least two governed reviewers, a label rubric, and disagreement handling. | Not available. |
| Reliability curve | Numeric prediction or probability target plus observed label/outcome. | Not supported because current PDDE does not emit option-level calibrated probabilities. |
| Brier score | Numeric probability and binary or multiclass observed outcome. | Not supported. |
| Expected calibration error | Numeric probability bins and governed observed outcomes. | Not supported. |
| Prior drift review | Repeated governed cases, source versions, prior versions, and review cadence. | Not supported beyond provenance references and uncalibrated status. |
| Local pathway gap review | Verified local overlay metadata and governed execution labels. | Deferred because local overlay metadata remains draft/incomplete in canonical fixtures. |
| Near-miss review | Event taxonomy, reviewer protocol, and privacy-approved event data. | Not available. |

Until those prerequisites exist, reports must continue to say calibration is pending or uncalibrated.

## Current JSONL Log Suitability Assessment

Current provenance JSONL records are useful as a calibration-seed inventory, but they are not sufficient for calibration metrics.

| Current Log Content | Calibration-Seed Use | Gap |
|---|---|---|
| `run_id`, timestamp, CDE ID, domain-pack ID | Can identify run records and group component outputs. | Real-data mode would need non-identifying governed case keys and linkage rules. |
| CDE source path and domain-pack source path | Can reproduce synthetic fixture runs. | Real-data paths may reveal sensitive context and need redaction or controlled storage. |
| package version, workflow mode, seed, iteration count | Supports reproducibility and run stratification. | Needs schema version and release governance before regulated use. |
| component status summaries | Helps find missing, unsupported, blocked, deferred, active, resolved, sampled, and eligible states. | Does not contain labels or outcomes. |
| safety gate statuses | Supports gate-status review. | Does not contain expert gate labels or adjudicated correctness. |
| prior resolution and Monte Carlo prior statuses | Preserves provenance class, confidence class, calibration status, and sampled/non-sampled state. | Does not log full prior parameters or observed calibration outcomes. |
| uncertainty, VOI, local overlay, and decision profile statuses | Supports review of visible unresolved states. | Does not include expert usefulness labels, clinician action, or outcome anchors. |
| status-only privacy design | Avoids raw clinical content in logs. | Must remain true if future real-data linkage is added. |

Current logs can seed a run registry and audit checklist. They cannot support Brier scores, expected calibration error, reliability diagrams, outcome claims, or prior updating without governed labels, outcomes, and metric definitions.

## Current Report Language Guardrails

Current Markdown reports should keep these guardrails:

- advisory-only
- uncalibrated or calibration pending
- not clinically validated
- not a final clinical recommendation
- no safe-discharge or unsafe-discharge conclusion
- no validated risk language
- no outcome benefit claim
- no top option or option ranking
- no hidden score or utility formula

Future calibration sections may say what is pending, governed, reviewed, linked, or unavailable. They should not imply validation until the actual governed evidence and metrics exist.

## Deferred Implementation Boundary

A later implementation should proceed only after governance input exists:

1. Define the label taxonomy and reviewer protocol.
2. Define allowed outcome anchors, time horizons, attribution rules, and censoring rules.
3. Define the data storage boundary for labels, outcomes, case keys, and real-data linkage.
4. Decide whether calibration records remain JSONL, move to SQLite/Postgres, or live in a governed research data store.
5. Add typed calibration label and outcome-anchor models only after the schema is approved.
6. Add report/provenance fields that show calibration state without outcome claims.
7. Add metrics only for outputs that have valid numeric targets and governed observed labels/outcomes.

## Out Of Scope For P1-010

- Calibration curves.
- Reliability diagrams.
- Brier score or expected calibration error computation.
- Prior updating.
- Drift detection.
- Outcome linkage.
- Expert label collection.
- Clinician action distribution analysis.
- Near-miss adjudication.
- PHI handling or real patient data storage.
- Report wording that implies validation, calibrated risk, or outcome benefit.
- CLI behavior changes.
- Final clinical recommendations.
- AI/LLM judgment or answer grading.
- New clinical thresholds, priors, utilities, weights, or formulas.

## Open User And Governance Inputs

- Which clinical owner governs the HF ED discharge calibration protocol?
- Which expert label set should be used for option defensibility and missingness review?
- How many reviewers are required, and how should disagreement be handled?
- Which clinician action taxonomy should be used?
- Which outcome anchors are allowed for this domain?
- What time horizons are clinically and statistically appropriate?
- What data source will provide outcomes, and under what approval?
- Is PDDE output silent, reviewer-visible, or clinician-visible during data collection?
- What case key is safe for linking logs to labels and outcomes?
- Where should labels and outcomes be stored?
- Which metrics are approved once numeric targets and labels exist?
- What sample size or stability threshold is required before any calibration statement can be made?

## Recommended Next Step

Keep calibration and outcome anchoring deferred. The current system is suitable for synthetic, advisory-only direct CDE review and status-only provenance logging, but not for outcome claims, clinical deployment, or calibrated-risk language.
