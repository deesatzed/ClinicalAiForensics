# Revised Final Plan v0.3

## 1. New Product Definition

PDDE is a **Clinical Decision Episode Simulator and Governance Engine**.

It evaluates whether candidate clinical actions are:

- evidence-applicable,
- patient-eligible,
- harm-aware,
- locally executable,
- monitorable/rescuable,
- patient-feasible,
- preference-compatible,
- and outcome-trackable.

## 2. Modes

### Mode 1 — Decision Simulation

Input:
- patient/case facts,
- decision moment,
- domain pack,
- local overlay.

Output:
- decision profiles for each option,
- uncertainty intervals,
- hard stops,
- missing data,
- value-of-information ranking.

### Mode 2 — AI Answer Mapping

Input:
- AI answer,
- case facts,
- domain pack.

Output:
- extracted claims,
- claim-to-option mapping,
- overclaim/omission flags,
- citation/provenance status,
- same decision-profile output.

### Mode 3 — Governance Calibration

Input:
- stored CDEs,
- clinician decisions,
- expert review labels,
- outcomes where available.

Output:
- calibration curves,
- reliability metrics,
- prior drift,
- local pathway gaps.

## 3. First MVP Domain

ED discharge medication/disposition strategy for known HFrEF/HFmrEF after IV diuresis.

## 4. Revised Node Set

### Primary Input Nodes

1. Evidence applicability
2. Evidence maturity
3. Patient eligibility
4. Acute severity/stability
5. Harm susceptibility
6. Benefit opportunity
7. Local executability
8. Monitoring/rescue capacity
9. Patient feasibility/preference
10. Uncertainty burden

### Deterministic Safety Gates

Hard gates include:

- unstable vital signs,
- persistent hypoxia,
- severe residual congestion,
- severe AKI or unknown renal trajectory,
- potassium danger thresholds for MRA,
- active ketosis/high euglycemic DKA risk for SGLT2i,
- no follow-up or monitoring capacity when required,
- wrong-indication medications such as sotalol as HF GDMT beta blocker.

### Computed Output Objects

1. Decision profile
2. Uncertainty budget
3. Value-of-information ranking
4. Escalation recommendation
5. Local execution checklist
6. Outcome-tracking keys

## 5. Output Categories

- Action-ready
- Conditionally defensible
- Needs more data
- Escalate/observe/admit
- Locally infeasible
- Discouraged
- Unsafe/wrong indication

## 6. Recommended Build Order

### Phase -1 — Tabletop Design

Before code, manually run three cases:

1. clearly eligible discharge candidate,
2. clearly unsafe discharge candidate,
3. ambiguous candidate.

Deliverable:
- revised node definitions,
- hard stop list,
- value-of-information list.

### Phase 0 — CLI Decision Simulator

Build direct CDE simulation first. Do not start with AI answer extraction.

Deliverables:
- domain pack YAML,
- CDE schema,
- Monte Carlo engine,
- safety gate engine,
- Markdown decision profile.

### Phase 1 — AI Answer Mapping

Add AI claim extraction and map claims to decision options.

### Phase 2 — Local Overlay Verification

Add real local owners/status/verification.

### Phase 3 — Citation and Evidence Audit

Add source support checking.

### Phase 4 — Calibration

Add expert review and outcome anchoring.

## 7. Non-Negotiable Constraints

1. No single trust score.
2. No probability without provenance.
3. No prior without elicitation method.
4. No local rule without owner/status.
5. No LLM-only prior in clinical advisory mode.
6. No clinical recommendation without missing-variable analysis.
7. No visible composite without uncertainty budget.
8. No outcome claim without outcome data.
9. No AI answer evaluation unless mapped to a decision episode.
10. No clinical deployment until calibration logging exists.
