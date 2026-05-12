Done. I reassessed the plan using first-principles and “alien goggles” thinking, then created a revised v0.3 build-guide package.

Download it here:

[PDDE v0.3 First-Principles Final Build Guide](sandbox:/mnt/data/pdde_v0_3_first_principles_final.zip)

## Core reassessment

The prior plan was strong, but it still had one hidden assumption:

> The AI answer was treated as the primitive object.

From first principles, that is wrong.

The primitive object should be the **clinical decision episode**, not the AI answer. An AI answer is only one possible input into a decision. The thing that matters clinically is: **what decision was made, under what uncertainty, with what missing data, using what evidence, in what local system, and with what eventual outcome?**

So the revised architecture pivots from:

> **AI answer → claim scoring → Monte Carlo report**

to:

> **Clinical Decision Episode → safety gates → decision options → uncertainty simulation → decision profile → calibration/outcome tracking**

That is the major v0.3 change.

## Main critique of the previous plan

The earlier master plan correctly positioned PDDE as an AI-enhanced probabilistic expert system that decomposes recommendations into nodes, assigns provenance-bound probabilities, and propagates uncertainty instead of producing a false verdict. 

But the latest critique exposed the key flaw: a YAML line like `sglt2_ed_discharge: alpha: 14, beta: 5` creates false precision unless we can explain exactly where those parameters came from. The review correctly identified that the foundational unresolved problem was **prior provenance and elicitation**. 

The plan also had several operational risks already identified: garbage priors, LLM-hallucinated provenance, LLM variance being mistaken for epistemic uncertainty, Monte Carlo false precision, overfitting to HF, outcome attribution problems, and clinician over-reliance. Those risks remain central. 

## Alien-goggles critique

An outsider would ask:

1. Why grade chatbot answers instead of clinical decisions?
2. Why produce precise probabilities before priors are validated?
3. Why combine evidence, risk, local execution, missing data, and patient preference into one score?
4. Why is “admit/observe/escalate” not a first-class option?
5. Why would clinicians safely interpret Monte Carlo intervals during a busy ED shift?
6. Why should missing data ever permit a confident recommendation?
7. Why is patient feasibility/preference not a core node?
8. Why are outcomes deferred rather than represented in the data model from day one?

Those questions forced the v0.3 redesign.

## Revised architecture

The final improved plan uses two separate engines:

### 1. Deterministic Safety Gate Engine

This handles hard stops.

Examples:

* SBP too low.
* Persistent hypoxia.
* Severe residual congestion.
* eGFR or potassium thresholds.
* Active ketosis or high euglycemic DKA risk.
* No follow-up when monitoring is required.
* Sotalol as HF GDMT beta blocker.
* GLP-1i as HFrEF/HFmrEF ED anti-admission therapy.

Hard stops cannot be overridden by favorable Monte Carlo scores.

### 2. Probabilistic Decision Simulator

This handles soft, uncertain tradeoffs.

It models:

* evidence applicability,
* evidence maturity,
* patient eligibility,
* acute stability,
* harm susceptibility,
* benefit opportunity,
* local executability,
* monitoring/rescue capacity,
* patient feasibility/preference,
* uncertainty burden.

The output is no longer primarily a “score.” It is a **Decision Profile**.

## Revised output artifact

Instead of a “Trust Receipt,” the system now produces a:

# **Decision Profile**

Each candidate option gets:

* category: action-ready, conditionally defensible, needs more data, escalate/observe/admit, locally infeasible, discouraged, unsafe/wrong indication;
* median decision fitness;
* uncertainty interval;
* hard stops;
* missing variables;
* value-of-information ranking;
* uncertainty budget;
* local execution checklist;
* prior provenance;
* calibration status.

The key new requirement is the **value-of-information statement**:

> “What missing data would most reduce uncertainty or flip the decision?”

For the HF case, that may be:

1. current eGFR,
2. potassium,
3. post-diuresis SBP,
4. volume status,
5. DKA/ketosis risk,
6. follow-up/lab feasibility,
7. medication access,
8. patient preference.

## Revised build order

The previous plan started too close to AI-answer parsing. The v0.3 plan starts with direct decision simulation.

### Phase -1: Tabletop design

Manually run three cases:

1. clearly safe discharge candidate,
2. clearly unsafe discharge candidate,
3. ambiguous candidate.

Goal: validate nodes before code.

### Phase 0: CLI CDE simulator

Build:

* Clinical Decision Episode schema,
* HF domain pack,
* safety gate engine,
* prior resolver,
* Monte Carlo simulator,
* uncertainty budget generator,
* value-of-information ranking,
* Markdown report.

No UI. No auth. No citation audit. No AI extraction yet.

### Phase 1: AI answer mapping

Only after the CDE simulator works:

* extract claims from AI answers,
* map claims to decision options,
* flag omissions and overstatements.

### Phase 2: local overlay verification

Add institution-specific workflow, but every local rule must have:

* owner,
* status,
* verification date,
* source,
* review cadence.

### Phase 3: citation/evidence audit

Add source verification and citation-support checks.

### Phase 4: calibration/outcome anchoring

Use expert review and, later, real outcomes to calibrate the system.

## Key design change

The old plan asked:

> “How do we assess this AI answer?”

The revised plan asks:

> **“For this clinical decision episode, which actions are defensible, what data are missing, what risks dominate, what local pathway is required, and what outcome should later calibrate the model?”**

That is the stronger product and research framing.

## What is in the v0.3 package

The new ZIP includes:

* `01_FIRST_PRINCIPLES_REASSESSMENT.md`
* `02_REVISED_FINAL_PLAN.md`
* `03_CODEX_BUILD_SPEC.md`
* `04_TESTING_ALGORITHM.md`
* `05_PRIOR_AND_UNCERTAINTY_GOVERNANCE.md`
* `06_UI_AND_REPORTING_SPEC.md`
* `schemas/clinical_decision_episode.schema.json`
* `schemas/decision_profile.schema.json`
* `domain_packs/hf_ed_discharge/domain_pack.yaml`
* `codex_tasks/PHASE0_TASKS.md`
* `examples/hf_cde_stable.json`
* `README.md`

## Final improved principle

The project should not say:

> “This AI answer is correct.”

It should say:

> **“For this clinical decision episode, this option is defensible within this uncertainty range, under these assumptions, with these missing variables, these hard stops, these local execution requirements, and this calibration status.”**

