# Decision Fitness Report

**Case ID:** HF-001-stable-postdiuresis
**Generated:** 2026-05-11 14:32:00
**Network:** hf_ed_discharge_v0 (version 0.1)
**Workflow:** B — Decision Simulation
**Iterations:** 10,000

---

## ⚠️ PROVENANCE WARNING

This report uses placeholder priors (`confidence_class: moderate_unverified` or `low_unverified`) for SGLT2 ED-initiation, MRA ED-initiation, local executability, and monitoring feasibility. These values **have not been formally elicited from a clinician panel** and should be treated as illustrative until prior elicitation is complete. Calibration is pending outcome data.

Do not use this output for actual clinical decision-making in v0.

---

## Executive Summary

For a 62-year-old with known HFrEF (LVEF 32%) improved after ED diuresis, with stable hemodynamics (SBP 118, eGFR 45, K 4.2), no DKA risk, available follow-up, and verified medication access:

**Top-ranked defensible options:**
1. Discharge with loop + continue existing GDMT (median fitness 0.81)
2. Discharge with loop + initiate SGLT2i (median fitness 0.71, *wide interval — see below*)
3. Discharge with urgent HF follow-up, no new med (median fitness 0.69)

**Most sensitive variables driving uncertainty:** follow-up reliability, local SGLT2 formulary status, BMP follow-up pathway.

---

## Ranked Decision Options

| Rank | Option | Median Fitness | 90% Credible Interval | Category Probabilities |
|------|--------|---------------:|----------------------:|------------------------|
| 1 | Discharge + loop + continue GDMT | **0.81** | [0.71 – 0.89] | action-ready: 41%, conditional: 49%, needs-more-data: 8%, unsafe: 2% |
| 2 | Discharge + loop + initiate SGLT2i | **0.71** | [0.48 – 0.86] | action-ready: 18%, conditional: 52%, needs-more-data: 24%, unsafe: 6% |
| 3 | Discharge + urgent HF follow-up only | **0.69** | [0.58 – 0.79] | action-ready: 22%, conditional: 56%, needs-more-data: 19%, unsafe: 3% |
| 4 | Admit / observe | **0.42** | [0.21 – 0.68] | action-ready: 7%, conditional: 18%, needs-more-data: 51%, discouraged: 24% |
| 5 | Discharge + loop + initiate MRA | **0.38** | [0.12 – 0.71] | action-ready: 8%, conditional: 26%, needs-more-data: 47%, discouraged: 19% |
| 6 | Discharge + loop only | **0.34** | [0.24 – 0.46] | action-ready: 4%, conditional: 22%, discouraged: 67%, unsafe: 7% |

**Note:** Option 2 (SGLT2 initiation) carries a wide credible interval [0.48–0.86]. The width itself is information — it tells the clinician this decision hinges on variables the system isn't fully confident about. See sensitivity drivers below.

---

## Sensitivity Drivers (variance decomposition)

For Option 2 (Discharge + initiate SGLT2i):

| Variable | Variance Contribution | Status |
|----------|----------------------:|--------|
| Follow-up reliability | 24% | reported available, but local clinic capacity placeholder |
| Local formulary status | 21% | **draft** — Temple SGLT2 preferred agent not verified |
| BMP follow-up pathway | 17% | **draft** — Temple lab pathway not verified |
| eGFR | 12% | verified at 45; within action-ready range |
| DKA risk | 8% | verified low |
| Affordability | 6% | medication access reported verified |
| Other | 12% | — |

**Best next data to collect:**
1. Verify Temple HF clinic appointment for ≤7 days
2. Verify Temple-preferred SGLT2 formulary agent
3. Confirm BMP follow-up at 72h pathway

---

## Claim-Level Evidence Maturity

(Workflow A would populate this section from a pasted AI answer. For Workflow B with no AI answer to adjudicate, this section reflects the engine's own claim set.)

| Claim | Evidence Maturity | Confidence Class |
|-------|-------------------|------------------|
| Continue current GDMT (ARNI + metoprolol succinate) | standard_action_ready | high |
| Loop diuretic plan after ED diuresis | standard_action_ready | high |
| SGLT2 initiation if eligible | conditional_protocol_dependent | moderate_unverified ⚠️ |
| MRA initiation in ED | conditional_protocol_dependent | moderate_unverified ⚠️ |
| Early HF clinic follow-up | standard_action_ready | high (STRONG-HF) |

---

## Patient Eligibility Gates

| Gate | Value | Status | Impact |
|------|------:|--------|--------|
| SBP | 118 | action_ready | supports all discharge options |
| eGFR | 45 | action_ready | supports SGLT2 (≥25), supports MRA (>30) |
| Potassium | 4.2 | action_ready | supports MRA initiation |
| Volume status | improved | action_ready | supports discharge |
| DKA risk | low | action_ready | supports SGLT2 |
| Oral intake | adequate | action_ready | supports oral discharge plan |
| Follow-up | available | action_ready | supports all discharge options |

**No avoid-tier gates triggered.** Caution-tier: none.

---

## Local Overlay Status (Temple)

⚠️ **All Temple-specific rules below are status: draft. They have not been verified by local owners.**

| Item | Draft Value | Verification Status |
|------|-------------|---------------------|
| Preferred SGLT2 | dapagliflozin OR empagliflozin | pending pharmacy |
| HF clinic timing | ≤7 days | pending cardiology |
| BMP timing | 72h–1 week post-discharge | pending |
| Cardiology callback triggers | eGFR<30, K≥5, SBP<100 | pending |
| Discharge requirements | 6-item checklist | pending |

Local rule verification is the Phase 1 deliverable. Until then, treat as illustrative only.

---

## Prohibited Recommendation Check

The system scanned for known unsafe/unsupported patterns:

| Pattern | Detected? |
|---------|-----------|
| Sotalol as HF beta-blocker | No |
| GLP-1 RA for HFrEF admission prevention | No |
| Digoxin as acute ED disposition-saver | No |

---

## Evidence-in-Motion (recent trials/guidelines)

| Item | Date | Implication |
|------|------|-------------|
| DECISION trial (low-dose digoxin) | 2026-05-10 (Nature Med) | Primary endpoint missed; meta-analysis with DIGIT-HF + DIG positive in aggregate. Affects digoxin priors at next quarterly review. |
| 2024 ACC Expert Consensus on Worsening HF | 2024 | Current; in use |
| 2022 AHA/ACC/HFSA HF Guideline | 2022 | Current backbone |

---

## Defensible Conclusion

For this patient, **continuing existing GDMT plus a robust oral loop plan and early HF follow-up is the highest-fitness defensible decision** (median 0.81, narrow interval).

**SGLT2 initiation is conditionally defensible (median 0.71, wide interval [0.48–0.86]).** The width is driven by unverified local pathway variables, not by the patient's clinical profile (which supports SGLT2). Before this option becomes action-ready, Temple should verify: (a) HF clinic appointment availability, (b) preferred SGLT2 formulary agent, (c) BMP follow-up pathway.

**MRA initiation is not recommended in the ED for this case** despite favorable labs, because the credible interval is wide (0.12–0.71) and depends heavily on unverified monitoring infrastructure. Defer to HF clinic.

**Admit/observe is not indicated** based on current data, but the system flags the credible interval as wide because residual congestion and renal trend cannot be fully verified from a single-point snapshot.

---

## Reasonable clinicians could defend

Either:
- The top option (continue GDMT + loop + follow-up) without ED initiation of new agents
- The second option (add SGLT2i) **if local pathway gates are confirmed at the time of discharge**

Both fall within the defensible decision space. The engine does not adjudicate between them.

---

## Non-Negotiable Reminders

- This is not a verdict. It is a defensibility distribution.
- Placeholder priors are clearly labeled and should not be treated as validated.
- The engine cannot replace clinician judgment, especially for missing variables it flagged.
- Calibration data is not yet collected; predicted confidence has not been empirically validated.

---

*End of Decision Fitness Report. Version: v0.1. Engine: PDDE. Build: Phase 0 toy.*
