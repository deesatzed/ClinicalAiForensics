# Probabilistic Defensible Decision Engine (PDDE)
## Master Plan — Roadmap, Build Spec, To-Do, Testing Algorithm
**Version:** v0.1 · **Date:** May 11, 2026 · **Author:** WAS

---

## 0. EXECUTIVE SUMMARY

PDDE is an AI-enhanced probabilistic expert system that evaluates AI-generated clinical recommendations by decomposing them into structured decision nodes, eliciting probability distributions per node (with provenance), and propagating uncertainty via Monte Carlo simulation to produce calibrated defensibility distributions over decision options — rather than verdicts against a mythical gold-standard answer.

**Core thesis:** AI does not earn trust; it earns *bounded use*. We measure decision fitness under uncertainty, not model correctness against expert consensus.

**v0 domain:** ED discharge medication decisions for HFrEF/HFmrEF after IV diuresis. Six decision options scored across nine input axes with three computed summary axes.

**v0 deliverable:** Clinician pastes any AI clinical answer; system returns a Decision Fitness Report with ranked decision options, credible intervals, sensitivity drivers, provenance dossier, and Temple-specific local overlay.

**Strategic position:** Vendor-agnostic governance-grade layer that sits *above* OpenEvidence / UpToDate Expert AI / Doximity Ask / ChatGPT for Clinicians. Not a competitor; an oversight engine.

---

## 1. ROADMAP

### Phase 0 — Toy Prototype (Weeks 1–2)
**Goal:** Discover ontology and architecture problems before over-investing.

| Deliverable | Notes |
|---|---|
| End-to-end CLI on HF case | Disposable; expect to throw most of it away |
| HF belief network YAML v0 | First-pass node definitions |
| Monte Carlo engine (pure NumPy) | 10K iterations, no fancy tooling |
| Markdown Decision Fitness Report | No PDF yet, no UI |
| Documented ontology problems | The actual deliverable |

**Success:** Wayne face-validates output on the HF case we've already worked through. Ontology gaps identified.

**Effort:** ~37h solo

---

### Phase 1 — Clinically Credible v0 (Weeks 3–6)
**Goal:** Production-grade prototype suitable for CMIO demo.

| Deliverable | Notes |
|---|---|
| React + Tailwind frontend | Paste-in, streaming display, PDF export |
| Provenance manager + SQLite | Every distribution carries source dossier |
| Citation auditor (programmatic) | Crossref + NCBI + Retraction Watch + claim-paper alignment |
| Sensitivity analyzer | Tornado plot data + viz |
| Temple HF local overlay | Formulary, pathway, follow-up, escalation thresholds |
| NPPES NPI auth | Light, free, official |
| Adversarial test suite | 10 categories × 5 cases = 50 |
| Calibration logging | Predictions stored for future scoring |

**Success:** CMIO demo lands; ≥80% adversarial test pass on HF; clinical face-validity from 2–3 reviewers.

**Effort:** ~92h

---

### Phase 2 — Generalization (Weeks 7–12)
**Goal:** Prove the framework isn't HF-specific.

| Deliverable | Notes |
|---|---|
| Generic belief network framework | YAML schema generalized |
| Second case: chest pain disposition | Different decision tree shape |
| Cross-case test harness | Validates reusability |
| "How to add a new case" doc | For collaborators |
| Validation: sepsis case in <1 day | Acceptance test |

**Effort:** ~54h

---

### Phase 3 — IRB + Internal Pilot (Weeks 13–16)
| Deliverable | Notes |
|---|---|
| IRB exempt determination | Synthetic cases, no PHI in v0 |
| OSF pre-registration | Public protocol commitment |
| 3–5 Temple clinician beta testers | Advisory-only mode |
| Pilot feedback + iteration | UI and ontology refinement |

---

### Phase 4 — Calibration Data Collection (Months 5–9)
| Deliverable | Notes |
|---|---|
| Silent prospective collection | System generates outputs not shown |
| 200–500 logged cases with metadata | Volume target for power |
| Retrospective outcome linkage (IRB-approved) | Temple data warehouse pull |
| Calibration metrics | Brier, ECE, reliability diagrams |

**Decision point:** if ECE >0.10, return to prior elicitation methodology.

---

### Phase 5 — Methods Paper + Viewpoint (Months 10–15)
| Deliverable | Venue |
|---|---|
| Methods paper | NEJM AI or JAMIA |
| Companion viewpoint | "Against the Myth of the Gold Standard Answer" — JAMA or Health Affairs |
| Open-source code release | GitHub with versioned belief network YAMLs |
| Supplementary materials | Prompt templates, prior dossiers, calibration data |

---

### Phase 6 — Federation (Year 2)
Multi-site adoption (Penn, Jefferson, Geisinger). Temple as methodological hub. Consortium paper.

---

## 2. BUILD SPEC GUIDE

### 2.1 Architecture (Six Layers)

1. **Belief network structure** — YAML-declared DAG of nodes and dependencies
2. **LLM-assisted node parameterization** — Claude estimates priors; never decides
3. **Prior governance and provenance** — every distribution has a source dossier
4. **Probabilistic inference** — NumPy Monte Carlo (v0) → NumPyro (v1+ if needed)
5. **Distributional report** — decision-option ranking + tornado plot + provenance table
6. **Calibration and outcome updating** — quarterly review cadence + drift detection

### 2.2 System Diagram

```
┌──────────────────────────────────────────────────────────────┐
│  USER INTERFACE (React + Tailwind + Recharts)                │
│  paste AI answer → Decision Fitness Report                   │
└──────────┬───────────────────────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────────────────────┐
│  API LAYER (FastAPI)                                         │
│  /extract  /parameterize  /infer  /report  /audit  /history  │
└──────────┬───────────────────────────────────────────────────┘
           │
   ┌───────┼───────────┬──────────┬──────────┬──────────┐
   ▼       ▼           ▼          ▼          ▼          ▼
┌─────┐ ┌──────┐  ┌──────────┐ ┌──────┐  ┌──────┐  ┌───────────┐
│Claim│ │ Node │  │Provenance│ │  MC  │  │Local │  │Calibration│
│ Ext │ │ Param│  │  Manager │ │Engine│  │Overlay│ │  Tracker  │
└─────┘ └──────┘  └──────────┘ └──────┘  └──────┘  └───────────┘
   │       │           │          │
   └───────┴───────────┴──────────┴───────┐
                                          ▼
                  ┌─────────────────────────────────────┐
                  │  SHARED RESOURCES                    │
                  │  - Belief Network YAML               │
                  │  - Provenance DB (SQLite → Postgres) │
                  │  - Citation cache                    │
                  │  - LLM API client (Anthropic)        │
                  │  - Crossref / NCBI / Retraction      │
                  └─────────────────────────────────────┘
```

### 2.3 Components

**Claim Extractor**
- Input: raw AI answer text + optional context
- Output: `List[Claim]` where `Claim = {id, text, assertion_type, entities, qualifiers, source_attribution}`
- LLM: Claude Opus 4.7, structured JSON output, T=0
- Self-consistency check: extract N=3 times, merge equivalents

**Node Parameterizer**
- Input: `(Claim, Axis, EvidenceContext)`
- Output: `Prior = {distribution_type, parameters, provenance, confidence_class, uncertainty_drivers}`
- Distribution families: Beta (bounded [0,1]), Normal (unbounded), Categorical (discrete options)
- Critical: every output prior carries provenance; ungrounded LLM priors flagged as `confidence_class: "llm_only_weakest"`

**Provenance Manager**
- SQLite tables: `priors`, `sources`, `calibrations`, `reviews`, `drift_alerts`
- Mandatory fields per prior:
  ```yaml
  node_id: sglt2_ed_initiation_defensibility
  distribution: beta(α=12, β=4)
  source_type: guideline_extrapolation
  provenance:
    - "2022 AHA/ACC/HFSA HF Guideline, Class I HFrEF, LOE A"
    - "EMPULSE 2022 (inpatient stabilization)"
    - "Local Temple expert panel May 2026, n=3 cardiology + 2 EM"
  confidence_class: moderate
  review_cadence: quarterly
  last_reviewed: 2026-05-11
  calibration_status: pending_outcome_data
  ```
- Audit log for every modification

**Monte Carlo Engine**
- Pure NumPy v0; NumPyro v1+ if needed
- 10,000 iterations default
- Samples joint distribution across belief network nodes
- Outputs: per-node posterior, per-decision-option score distributions, sensitivity rankings

**Local Overlay Engine**
- YAML-driven Temple rules
- Formulary defaults (e.g., dapagliflozin as SGLT2i)
- Order set triggers (Epic order set IDs)
- Follow-up clinic capacity
- Pathway gating logic (e.g., eGFR<30 → cardiology callback)

**Citation Auditor**
- Crossref REST (DOI resolution + currency)
- NCBI E-utilities (PubMed validation)
- Retraction Watch dataset (downloadable; weekly refresh)
- Abstract-claim alignment via `sentence-transformers` (cosine similarity threshold tunable)
- Returns: `{exists, current, retracted, supports_claim_score, retrieved_at}`

**Calibration Tracker**
- Logs every prediction with full metadata
- Outcome linkage (Phase 4+) via case UUID + Temple EHR query
- Computes: Brier score, ECE, reliability diagrams
- Flags drift over time (alert if quarterly ECE shifts by >0.05)

**Report Generator**
- Markdown → PDF via WeasyPrint
- Sections: decision-option ranking, tornado plot, claim-level scores, provenance table, evidence-in-motion (recent trials), local overlay additions, defensibility summary
- Version-stamped, archivable, exportable

### 2.4 Data Flow

1. User pastes AI answer + optional case context
2. Claim Extractor → `List[Claim]`
3. For each `(Claim × Axis)`: Node Parameterizer → Prior distribution
   - Provenance Manager logs prior with source dossier
4. Belief Network YAML loaded → DAG structure
5. Monte Carlo Engine propagates uncertainty (10K iterations)
6. Decision options scored → ranked with credible intervals
7. Sensitivity Analyzer → tornado plot data
8. Local Overlay Engine → Temple-specific additions
9. Citation Auditor → verify all cited sources in the input answer
10. Report Generator → markdown + PDF
11. Calibration Tracker → log full prediction
12. User views report; can export, share, save

### 2.5 Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Backend | Python 3.12, FastAPI | Wayne's expertise, async, mature |
| Inference | NumPy v0 → NumPyro v1+ | M4-optimized, JAX-fast |
| LLM | Anthropic Claude Opus 4.7 | Best structured extraction, prompt caching |
| Database | SQLite v0 → Postgres v1+ | Simple → scalable |
| Frontend | React + Tailwind + Recharts | Wayne's expertise |
| PDF | WeasyPrint | Pure Python, no Chrome deps |
| Auth | NPPES NPI API | Free, official |
| Citations | Crossref + NCBI E-utils + Retraction Watch | Standard, free |
| Embeddings | sentence-transformers (local) | M4 runs locally, PHI-safe path later |
| Deployment | M4 local → VPS | Iterative |

### 2.6 Existing Infrastructure to Reuse

| Existing Asset | Reuse |
|---|---|
| Home transition simulation engine | Gaussian copula MC + Factor Research Objects → direct port to belief network propagator |
| CAM_CAM Bayesian Kelly routing | Conditional probability infrastructure |
| CAM_CAM 7-gate validation | Adversarial test framework |
| ACE Forecaster | Calibration methodology (1.4–2.9% MAPE playbook) |
| imbora 9-phase pipeline | Uncertainty handling patterns |
| LogSwarm | Anomaly detection over AI outputs (drift detection) |
| Mira (Precision Medicine Studio) | Voice-native integration target (Phase 2+) |
| Agent Pidgin | Structured claim payload format (Phase 2+) |

---

## 3. BUILD TO-DO LIST

### Phase 0: Toy Prototype (Weeks 1–2, ~37h)

| # | Task | Effort | Depends on |
|---|---|---|---|
| 0.1 | Repo scaffold (FastAPI + Pydantic models) | 2h | — |
| 0.2 | Core data structures (Claim, Prior, BeliefNetwork, DecisionOption) | 3h | 0.1 |
| 0.3 | HF belief network YAML v0 (DAG + node defs) | 6h | 0.2 |
| 0.4 | Claim extractor prompt + Anthropic API integration | 4h | 0.1 |
| 0.5 | Node parameterizer prompt + LLM call | 4h | 0.4 |
| 0.6 | Simple NumPy Monte Carlo engine (10K iter) | 6h | 0.3, 0.5 |
| 0.7 | Decision option scorer | 3h | 0.6 |
| 0.8 | Markdown report renderer | 3h | 0.7 |
| 0.9 | CLI: `pdde run hf_response.txt` | 2h | 0.8 |
| 0.10 | End-to-end smoke test on HF case | 2h | 0.9 |
| 0.11 | Document ontology problems discovered | 2h | 0.10 |

### Phase 1: Clinically Credible v0 (Weeks 3–6, ~92h)

| # | Task | Effort |
|---|---|---|
| 1.1 | Refactor based on Phase 0 lessons | 8h |
| 1.2 | Provenance manager + SQLite schema | 6h |
| 1.3 | Citation auditor (Crossref + PubMed + Retraction Watch) | 8h |
| 1.4 | Abstract-claim alignment (sentence-transformers) | 6h |
| 1.5 | Sensitivity analyzer (tornado data) | 4h |
| 1.6 | Local overlay engine + Temple HF YAML | 8h |
| 1.7 | React frontend scaffold | 6h |
| 1.8 | Report display (decision-option table + tornado) | 8h |
| 1.9 | PDF export (WeasyPrint) | 4h |
| 1.10 | NPPES NPI auth | 4h |
| 1.11 | Calibration tracker (logging only) | 4h |
| 1.12 | Adversarial test suite (10 categories × 5 cases) | 12h |
| 1.13 | Run adversarial tests, document failures | 6h |
| 1.14 | Polish + CMIO demo prep | 8h |

### Phase 2: Generalization (Weeks 7–12, ~54h)

| # | Task | Effort |
|---|---|---|
| 2.1 | Identify reusability boundaries from HF | 4h |
| 2.2 | Refactor to generic belief network framework | 16h |
| 2.3 | Chest pain disposition YAML | 12h |
| 2.4 | Cross-case test harness | 8h |
| 2.5 | "How to add a new case" doc | 6h |
| 2.6 | Validation: sepsis case in <1 day | 8h |

---

## 4. TESTING ALGORITHM

### 4.1 Hierarchy (six levels)

```
Level 5: Outcome-Anchored (prospective)    ← months/years
Level 4: Calibration (longitudinal)        ← weeks/months
Level 3: Expert Adjudication (cross-sect)  ← days
Level 2: Adversarial (synthetic stress)    ← per build
Level 1: Integration (end-to-end)          ← per commit
Level 0: Unit (component-level)            ← per commit
```

### 4.2 Level 0 — Unit Tests
- Each component tested in isolation
- Claim extractor: known inputs → expected claim structure
- Monte Carlo: deterministic given seed
- Citation auditor: known DOIs → expected results (existence, currency, retraction)
- Provenance manager: CRUD + audit log integrity

### 4.3 Level 1 — Integration Tests
- Full pipeline: HF answer → complete Report
- Fixture cases with expected output ranges (not exact values; ranges)
- Run on every PR

### 4.4 Level 2 — Adversarial Tests (10 categories)

| # | Category | What it probes |
|---|---|---|
| 1 | Differential generation | Undifferentiated complaint, correct DDx surfaced |
| 2 | Hidden contraindication | Buried detail should change management |
| 3 | Appropriate uncertainty | Right answer is "uncertain" — overclaim? |
| 4 | Counterfactual pair | Flip one variable, advice shifts appropriately |
| 5 | Citation integrity | Fabricated or misattributed citations caught |
| 6 | Freshness probe | Trial published last 30 days (e.g., DECISION) — surfaced? |
| 7 | Press-release framing | Positive press vs. neutral primary endpoint distinguished |
| 8 | Out-of-domain confidence | "73% mortality reduction" misapplied to wrong window |
| 9 | Drug-renal-dose | Renal-adjusted dosing probe |
| 10 | Conflicting guidelines | ESC vs. ACC divergence handled |

5 cases per category = 50 adversarial cases.

**Pass criteria:** system surfaces the trap OR appropriately widens uncertainty interval in ≥80% of cases per category.

### 4.5 Level 3 — Expert Adjudication
- 2–3 blinded clinician raters per case
- 50-case test set
- Inter-rater κ reported
- Compare system's defensibility ranking to expert panel ranking (Spearman correlation; concordance proportion)

### 4.6 Level 4 — Calibration (quarterly)
- Reliability diagrams (predicted defensibility vs. observed)
- Brier scores per decision option
- Expected Calibration Error (ECE)
- Drift detection: compare current quarter to baseline

### 4.7 Level 5 — Outcome-Anchored (Phase 4+)
After IRB-approved retrospective linkage:
- 30-day readmission
- 90-day mortality
- ED revisits
- AKI / hyperkalemia events
- Medication persistence
- Propensity-matched comparison: AI-augmented vs. usual care decisions

### 4.8 Continuous Monitoring
- Citation drift: are previously-valid sources now retracted?
- Guideline drift: have cited guidelines updated?
- Calibration drift: predictions getting worse over time?
- Prior staleness: priors reviewed in last 90 days?

---

## 5. RISK REGISTER

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Garbage priors → confident wrong outputs | High | High | Provenance labels, confidence_class on every prior; LLM-only priors flagged |
| LLM-hallucinated provenance | Medium | High | Programmatic citation verification mandatory before display |
| Overfitting to HF case | High | Medium | Phase 2 generalization with second case mandatory before v1 declared |
| Calibration drift over time | High (long-term) | Medium | Quarterly review cadence baked into operational layer |
| Clinician over-reliance on output | Medium | High | UI emphasizes uncertainty; "advisory only" prominent; wide intervals visible |
| Clinician under-reliance | Low | Medium | Workflow integration in Phase 2; usability testing |
| IRB delays | Medium | Medium | Submit in Phase 1, not Phase 4 |
| Vendor lock-in (Anthropic) | Low | Medium | Provider abstraction layer; design for swap |
| Outcome attribution problems | High | High | Propensity matching + sensitivity analyses mandatory; not optional |
| OE/Doximity litigation context | Medium | Medium | Pre-registration + IRB exempt + neutral methodology = legal armor |
| LLM variance ≠ epistemic uncertainty | High | High | Calibrate against expert adjudication and outcomes; don't trust raw model variance |
| False precision in Monte Carlo output | High | High | Provenance labels on every distribution; uncertainty class visible in report |

---

## 6. DECISION POINTS

Pre-committed points where direction can pivot:

- **End of Phase 0:** Is the ontology stable? If not, redesign nodes before Phase 1.
- **End of Phase 1:** Does CMIO demo land? If not, refocus messaging or scope.
- **End of Phase 2:** Does generalization work? If not, scope back to single-case product.
- **Mid Phase 4:** Calibration ECE acceptable (<0.10)? If not, return to prior elicitation.
- **End of Phase 4:** Outcome linkage feasible at Temple? If not, federate earlier.

---

## 7. SUCCESS METRICS

### Phase-Level
- Phase 0: end-to-end pipeline runs on 1 case; ontology problems documented
- Phase 1: ≥80% adversarial test pass; clinician inter-rater κ ≥0.6 on output usefulness
- Phase 2: new case added in <1 day by someone other than Wayne
- Phase 3: IRB exempt determination obtained; OSF pre-registration filed
- Phase 4: ECE <0.10 on calibration cohort; outcome data linked for ≥200 cases
- Phase 5: paper submitted to NEJM AI / JAMIA

### Project-Level
- Methodological novelty (cited as foundational in 12 months)
- Institutional adoption (≥3 Temple departments in 18 months)
- Federation (≥3 partner AMCs in 24 months)
- Career positioning (CMIO/advisory transition by 24 months)

---

## 8. PUBLICATION STRATEGY

| Paper | Venue | Timing | Position |
|---|---|---|---|
| Viewpoint: "Against the Myth of the Gold Standard Answer" | JAMA / Health Affairs | Month 6–9 | Epistemological argument; positions Wayne |
| Methods: "Probabilistic Expert Systems for Clinical AI Governance" | NEJM AI / JAMIA | Month 10–15 | Operationalizes the framework |
| Empirical: "Outcome-Anchored Evaluation of AI-Augmented Clinical Decisions" | Annals EM / Circulation: HF | Year 2 | Real-world calibration + outcome data |
| Consortium: Multi-site federation paper | JAMA Network Open | Year 2–3 | Establishes Temple as methodological hub |

---

## 9. OPEN QUESTIONS (DEFERRED DECISIONS)

- Naming: PDDE working name; final clinical brand TBD (candidates: Defensible Decision Engine, ClinProof, CalibratedCare)
- Voice integration: Mira pathway in Phase 2 or 3?
- Federation API design: Phase 2 placeholder or Year 2 commitment?
- Commercial vs. open source: defer until Phase 3 evidence of value
- PHI handling v1: still deidentified-only or expand?

---

## APPENDICES (to be drafted in Phase 0)

- **A.** Prompt templates (Claim Extractor, Node Parameterizer)
- **B.** HF Belief Network YAML structure
- **C.** Provenance schema (full SQL DDL)
- **D.** Adversarial test case library
- **E.** Local Temple Overlay YAML

---

*End of v0.1 master plan. Iterate freely.*
