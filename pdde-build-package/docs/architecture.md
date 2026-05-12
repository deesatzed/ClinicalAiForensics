# Architecture — 6-Layer Detail

PDDE's design philosophy: **AI parameterizes; classical math propagates; provenance governs.**

## Layer 1: Belief Network Structure

**What:** YAML-declared DAG of nodes with their dependencies.

**Why:** Explicit, version-controlled, interpretable, governable.

**Where:** `networks/hf_ed_discharge_v0.yaml`

**Key responsibilities:**
- Declare decision options
- Declare nodes (priors per claim type)
- Declare gates (patient eligibility thresholds)
- Declare prohibited recommendations (with detection patterns)
- Declare local overlay (institution-specific rules)
- Declare computed-node formulas

**Phase 0:** Hand-curated YAML for HF case.
**Phase 1+:** Editing tools, version control, governance workflow.

---

## Layer 2: LLM-Assisted Node Parameterization

**What:** Claude estimates probability distributions for nodes that aren't pre-defined in the YAML.

**Why:** YAMLs can't anticipate every claim. LLM-elicited priors bootstrap unknown nodes but are marked unverified.

**Where:** `pdde/parameterizer.py` (Phase 0); LLM via `prompts/node_parameterization.md`

**Key responsibility:** Never let LLM be the oracle. LLM only parameterizes; classical math does the rest. Every LLM-elicited prior carries `provenance_class: llm_unverified` and a warning.

---

## Layer 3: Prior Governance and Provenance

**What:** Every probability distribution carries a source dossier. Provenance is mandatory infrastructure.

**Why:** Without provenance, Monte Carlo is numerology — it makes weak evidence look mathematical and authoritative.

**Where:**
- YAML declares `provenance_class`, `provenance_detail`, `confidence_class`, `last_reviewed` per prior
- Pydantic schemas reject priors without these fields
- Logger persists every prior used in every run
- Report surfaces provenance warnings prominently

**Provenance classes (in order of trust):**

1. `guideline_mapped` — derived from guideline Class/LOE via documented rules
2. `trial_parsed` — parameters fit from published RCT confidence intervals
3. `panel_elicited` — formal Delphi-style elicitation from named clinicians
4. `local_outcome` — derived from local institutional outcome data
5. `panel_elicited_pending` — placeholder for nodes awaiting formal elicitation
6. `llm_unverified` — LLM-generated estimate, lowest confidence

**Confidence classes:**

- `high` — provenance well-established, defensible for deployment
- `moderate_unverified` — provenance plausible but not formally validated
- `low_unverified` — speculative, must be calibrated before clinical use

---

## Layer 4: Probabilistic Inference

**What:** Monte Carlo simulation propagates uncertainty across the belief network.

**Why:** Avoids false precision. Wide intervals are visible.

**Where:** `pdde/monte_carlo.py`

**Approach:** Pure NumPy in Phase 0. NumPyro/JAX considered for Phase 1 if needed.

**Workflow:**
1. For each iteration, sample from every node's prior distribution
2. Evaluate patient gates against the case
3. Apply local overlay constraints
4. Compute per-option fitness via formula in `computed_nodes.decision_fitness`
5. Apply harm penalty
6. Clip to [0, 1] and classify

After 10,000 iterations: per-option posterior distribution with median, intervals, and category probabilities.

---

## Layer 5: Distributional Report

**What:** Markdown Decision Fitness Report.

**Why:** Output is a distribution, not a verdict. Clinician sees the uncertainty, not a single score.

**Where:** `pdde/report.py`; template structure in `examples/sample_report_HF-001.md`

**Required content:**
- Provenance warnings (when applicable)
- Ranked decision options with credible intervals
- Sensitivity drivers
- Patient eligibility gate evaluation
- Local overlay status
- Prohibited recommendation check
- Evidence-in-motion (recent trials/guidelines)
- Defensible conclusion (prose synthesis)
- "Reasonable clinicians could defend" (alternatives)
- Non-negotiable reminders

---

## Layer 6: Calibration and Outcome Updating

**What:** Track predictions over time; update priors as outcomes accumulate.

**Why:** This is how the system stays calibrated. Without this, priors drift and outputs become unreliable.

**Where:** `pdde/provenance_logger.py` (Phase 0 logging); Phase 4 adds outcome linkage.

**Phase 0 minimum:** JSONL logging of every run, prior used, and prediction.

**Phase 1:** Migrate to SQLite, add basic calibration metrics (Brier, ECE).

**Phase 4:** IRB-approved retrospective outcome linkage; quarterly calibration review.

**Phase 5+:** Bayesian prior updating from observed outcomes; drift detection alerts.

---

## Data flow (end-to-end)

```
[Clinician]
   │
   │ pastes AI answer (Workflow A) or case context (Workflow B)
   ▼
[CLI Runner]
   │
   ├── Load BeliefNetwork (Layer 1)
   ├── Load Case
   │
   ├── Workflow A: Claim Extraction
   │     │
   │     ├── Anthropic API call
   │     ├── Normalize therapy names
   │     └── Validate against Claim schema
   │
   ├── Workflow A: Node Parameterization (Layer 2)
   │     │
   │     ├── Map known claims to YAML nodes
   │     └── LLM-elicit priors for unknown claims (Layer 3 tags)
   │
   ├── Prohibited Recommendation Detection
   │
   ├── Monte Carlo Simulation (Layer 4)
   │     │
   │     ├── 10K iterations
   │     ├── Sample priors, evaluate gates
   │     ├── Compute per-option fitness
   │     └── Classify each sample
   │
   ├── Sensitivity Analysis
   │     │
   │     └── Spearman rank correlation per input variable
   │
   ├── Report Generation (Layer 5)
   │
   └── Provenance Logging (Layer 6)
         │
         ├── runs.jsonl
         ├── priors.jsonl
         └── predictions.jsonl
   │
   ▼
[Decision Fitness Report (markdown)]
   │
   ▼
[Clinician reads, decides; report is advisory only]
```

---

## What this architecture explicitly avoids

- **Single source of truth.** Output is a distribution. Period.
- **LLM as oracle.** LLM is a parameter estimator, not a decision maker.
- **Hidden uncertainty.** Wide intervals are surfaced, not hidden.
- **Provenance-less probabilities.** Every prior has a source dossier.
- **Asymmetric burden.** Calibration is the evaluation metric, not correctness against an expert.

---

## What this architecture explicitly enables

- **Honest decision support.** Clinicians see what the system does and doesn't know.
- **Auditable governance.** Every prediction can be traced to its priors and inputs.
- **Calibration over time.** Logging from day one means Phase 4 can do outcome analysis.
- **Vendor-agnostic operation.** Evaluates any AI clinical answer; doesn't depend on a specific tool.
- **Federation-ready.** Multi-institution adoption requires only domain-specific YAML edits.
