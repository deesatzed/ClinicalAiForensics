# First-Principles and Alien-Goggles Reassessment

## 1. First-Principles Question

What are we actually trying to optimize?

Not:
- AI ranking,
- answer elegance,
- citation density,
- model trust,
- or expert agreement.

We are trying to improve:

> patient-relevant, clinician-mediated decision quality under uncertainty.

Therefore, the primitive object should not be an AI answer. It should be a **Clinical Decision Episode (CDE)**.

## 2. Clinical Decision Episode

A CDE contains:

- patient state,
- decision moment,
- available options,
- missing variables,
- source recommendations,
- clinician action,
- local execution constraints,
- eventual outcomes,
- and retrospective calibration labels.

AI output may inform the CDE, but it is not the center of gravity.

## 3. Alien-Goggles Questions

Imagine an outsider with no loyalty to medicine, AI, EHRs, vendors, or academic incentives. They would ask:

1. Why are you grading chatbot answers instead of decisions?
2. Why should an AI answer be the workflow input at all?
3. Why are you assigning precise beta distributions before you know the priors are real?
4. Why combine evidence, risk, local feasibility, and missing data into one score?
5. Why is “admit/observe/escalate” not a first-class output?
6. Why would clinicians understand or safely use Monte Carlo intervals during an ED shift?
7. Why is patient preference not represented?
8. Why is local rescue capacity not represented?
9. Why should lack of information ever produce a confident recommendation?
10. Why are outcomes deferred instead of defining their data structure now?

These questions expose the plan’s hidden assumptions.

## 4. What Survives First Principles

The following components survive:

- probabilistic expert-system approach,
- local context overlay,
- provenance-bound priors,
- Monte Carlo simulation,
- sensitivity analysis,
- calibration tracking,
- adversarial and counterfactual testing,
- outcome anchoring.

## 5. What Must Change

### Change 1 — CDE First

The engine should first simulate a decision episode, then optionally adjudicate AI answers.

### Change 2 — Two Engines, Not One

Separate:

1. **Safety Gate Engine** — deterministic hard stops and constraints.
2. **Probabilistic Decision Simulator** — uncertainty propagation for soft tradeoffs.

### Change 3 — No Single Composite as Primary Output

A composite can exist internally, but the visible output must be a **Decision Profile**.

### Change 4 — Add Value-of-Information

The report must say what missing variable would most reduce uncertainty.

### Change 5 — Add Uncertainty Budget

Every interval should be decomposed into sources:

- evidence uncertainty,
- patient-context uncertainty,
- local executability uncertainty,
- harm uncertainty,
- patient preference/feasibility uncertainty,
- prior uncertainty.

### Change 6 — Clinical Advisory Modes

Define modes:

- Sandbox/research mode.
- Governance review mode.
- Clinical advisory mode.

Each mode has different allowed prior classes and warnings.

## 6. Central Critique

The previous plan risked building a technically impressive “AI answer auditor.”

The revised plan builds a **decision-fitness simulator** that can also audit AI answers when useful.
