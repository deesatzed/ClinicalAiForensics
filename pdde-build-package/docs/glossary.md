# Glossary

Clinical, statistical, and engineering terms used across PDDE.

---

## Clinical Terms

**ACEi** — Angiotensin-converting enzyme inhibitor (e.g., lisinopril). HFrEF GDMT class; superseded by ARNI when tolerated.

**Action-ready** — In PDDE classification, a recommendation with median fitness ≥0.80 and unsafe probability <0.05. Roughly "standard of care, executable now."

**ARB** — Angiotensin receptor blocker (e.g., losartan, valsartan). HFrEF GDMT, used when ACEi not tolerated.

**ARNI** — Angiotensin receptor-neprilysin inhibitor (sacubitril/valsartan). Preferred HFrEF GDMT first-line per 2022 guideline.

**BMP** — Basic metabolic panel. Used to monitor renal function and potassium after diuretic or RAAS therapy changes.

**Class I/IIa/IIb/III (guideline classes)** — Strength of recommendation:
- Class I: Should be done; benefit >> risk
- Class IIa: Reasonable; benefit > risk
- Class IIb: May be considered; benefit ≥ risk
- Class III: Should not be done; risk > benefit (or no benefit)

**DECISION trial** — Low-dose digoxin RCT in HFrEF/HFmrEF, published Nature Medicine May 10, 2026. Missed primary composite endpoint but reduced HF hospitalizations. Meta-analysis with DIGIT-HF and DIG was positive in aggregate.

**DKA** — Diabetic ketoacidosis. Risk modifier for SGLT2 inhibitors (rare but serious).

**DOSE trial** — RCT establishing dosing strategy for IV loop diuretics in acute HF. Supports 2.5× oral dose for IV initial conversion.

**eGFR** — Estimated glomerular filtration rate (mL/min/1.73m²). Renal function measure. Gates SGLT2 (≥20-25) and MRA (>30) initiation.

**EMPULSE** — RCT showing empagliflozin benefit in hospitalized acute HF patients after stabilization. Supports in-hospital SGLT2 initiation.

**Four pillars (HFrEF GDMT)** — ARNI/ACEi/ARB + evidence-based beta blocker + MRA + SGLT2 inhibitor. Class I for HFrEF per 2022 AHA/ACC/HFSA guideline.

**GDMT** — Guideline-directed medical therapy.

**GLP-1 RA** — GLP-1 receptor agonist (semaglutide, liraglutide, tirzepatide). Used for diabetes and obesity. Not HF GDMT; FIGHT trial showed possible harm signal in recently decompensated HFrEF.

**HFmrEF** — Heart failure with mildly reduced ejection fraction (LVEF 41-49%).

**HFpEF** — Heart failure with preserved ejection fraction (LVEF ≥50%).

**HFrEF** — Heart failure with reduced ejection fraction (LVEF ≤40%).

**LOE A/B/C (level of evidence)**:
- LOE A: Multiple RCTs or meta-analyses
- LOE B: Single RCT or large observational studies
- LOE C: Expert opinion, case studies, standard of care

**LVEF** — Left ventricular ejection fraction. The fraction of blood pumped per beat.

**MRA** — Mineralocorticoid receptor antagonist (spironolactone, eplerenone). HFrEF GDMT class. Watch for hyperkalemia.

**SGLT2 inhibitor** — Sodium-glucose cotransporter 2 inhibitor (dapagliflozin, empagliflozin). HFrEF Class I, HFmrEF Class IIa per 2022 guideline. Watch for euglycemic DKA.

**Sotalol** — Class III antiarrhythmic with beta-blocker activity. NOT an HF beta-blocker; proarrhythmic risk. Used for atrial fibrillation rhythm control.

**STRONG-HF** — RCT showing rapid post-discharge GDMT optimization with structured follow-up reduces readmission and mortality.

---

## Statistical Terms

**Beta distribution** — Continuous probability distribution on [0,1], parameterized by α and β. Used for probabilities. Mean = α/(α+β).

**Bradley-Terry model** — Pairwise comparison model. Used by MedArena for LLM rankings; not used in PDDE.

**Brier score** — Mean squared error between predicted probabilities and observed outcomes. Lower is better. Used for calibration assessment.

**Credible interval** — Bayesian analog of confidence interval. "There is X% probability the true value lies in this interval."

**Delphi method** — Structured technique for expert elicitation involving iterative anonymous voting and feedback toward convergence.

**ECE** — Expected Calibration Error. Measures how well predicted probabilities match observed frequencies. Lower is better.

**Monte Carlo simulation** — Repeated random sampling to estimate distributions of complex functions. PDDE uses 10,000 iterations.

**Posterior distribution** — In Bayesian inference, the updated belief about a parameter after observing data.

**PRCC** — Partial rank correlation coefficient. Sensitivity analysis method.

**Prior distribution** — Initial belief about a parameter before observing data.

**Reliability diagram** — Plot of predicted probability vs observed frequency. Diagonal = perfectly calibrated.

**Sobol indices** — Variance-based sensitivity analysis. More rigorous than Spearman correlation but more sampling-intensive.

**Spearman rank correlation** — Non-parametric correlation measure. Used in PDDE Phase 0 for sensitivity analysis.

**Variance decomposition** — Breaking down total output variance into contributions from each input variable.

---

## Engineering Terms

**Adversarial test** — Test designed to elicit a specific failure mode. PDDE has 10 categories.

**Anthropic API** — REST API for Claude language models. Used by PDDE for claim extraction and node parameterization fallback.

**Bayesian network** — Probabilistic graphical model (DAG) representing dependencies between random variables. PDDE uses a simplified version.

**Belief network** — In PDDE, the YAML-declared graph of clinical decision nodes with priors and dependencies.

**Calibration** — The property that a system's stated confidence matches its actual accuracy. A 70%-confident system should be right 70% of the time.

**Claim** — Atomic clinical assertion extracted from an AI answer (e.g., "start SGLT2 inhibitor for HFrEF").

**Decision Fitness Report** — The primary PDDE output. Markdown document with ranked options, intervals, sensitivity drivers, and provenance warnings.

**Defensibility** — Property of a decision: whether reasonable clinicians could support it given the evidence, context, and risks.

**FastAPI** — Python web framework. Deferred to Phase 1.

**Gate** — In PDDE, a patient-eligibility threshold (e.g., "eGFR ≥ 25 for SGLT2 initiation").

**JSONL** — JSON Lines. One JSON object per line. Used for PDDE Phase 0 logging.

**MCP** — Model Context Protocol. Standard for connecting LLMs to external tools and data sources.

**NumPyro** — Probabilistic programming library on JAX. Considered for Phase 1 if needed.

**Posterior** — In PDDE output, the per-option fitness distribution from Monte Carlo.

**Provenance** — In PDDE, the metadata describing where a prior probability came from.

**Pydantic** — Python data validation library. Used throughout PDDE.

**Workflow A** — PDDE mode where user pastes an AI clinical answer; system adjudicates it.

**Workflow B** — PDDE mode where user provides case facts; system simulates decision space without an AI answer to evaluate.

**YAML** — Human-readable data serialization format. Used for belief networks and configuration.

---

## Project-Specific Terms

**Belief Network YAML** — Structured declaration of a clinical decision domain. Each domain has its own YAML.

**Confidence Class** — Trust level of a prior: `high`, `moderate_unverified`, or `low_unverified`.

**Decision Option** — A discrete action the clinician might take (e.g., "Discharge with loop + SGLT2").

**Local Overlay** — Institution-specific rules layered on top of generic clinical recommendations.

**Phase 0** — Disposable toy prototype; goal is ontology discovery.

**Phase 1** — Clinically credible CLI + UI; CMIO demo ready.

**Phase 2** — Generalization to second clinical case (e.g., chest pain).

**Phase 3** — IRB approval + internal Temple pilot.

**Phase 4** — Calibration data collection + outcome linkage.

**Phase 5** — Methods paper + viewpoint paper submission.

**Phase 6** — Multi-site federation.

**Provenance Class** — Source category of a prior: `guideline_mapped`, `trial_parsed`, `panel_elicited`, `local_outcome`, `panel_elicited_pending`, or `llm_unverified`.

**Rule Status** — Verification state of a local rule: `draft`, `verified`, `deprecated`, or `retired`.
