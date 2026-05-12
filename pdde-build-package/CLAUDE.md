# CLAUDE.md — Project Orientation for Claude Code

You are building **PDDE (Probabilistic Defensible Decision Engine)** v0 — a clinical AI evaluation layer that produces calibrated decision-fitness distributions, not verdicts.

Read this file completely before doing anything else.

## What you are building

A Python CLI (Phase 0) that:

1. Loads a belief network YAML describing clinical decision nodes (`networks/hf_ed_discharge_v0.yaml`)
2. Loads a case JSON describing a patient (`examples/sample_case_HF-001.json`)
3. Optionally accepts a pasted AI clinical answer (Workflow A)
4. Extracts clinical claims, assigns probability distributions to each node, runs Monte Carlo simulation, and outputs a Decision Fitness Report (`examples/sample_report_HF-001.md` is the target output)

**You are NOT building:**
- A frontend (deferred to Phase 1)
- Authentication (deferred to Phase 3)
- A PDF exporter (deferred to Phase 1)
- A database persistence layer beyond simple JSON logging (deferred to Phase 1)
- An EHR integration (never in scope)
- A citation auditor beyond DOI/PMID existence check (deferred to Phase 1)

## Build philosophy

Phase 0 code is **expected to be thrown away**. The deliverable is not polished code; it is *documented ontology problems and a working end-to-end pipeline*. Do not over-engineer.

When you face a choice between "thorough" and "shippable in Phase 0," ship.

## Non-negotiable design constraints

Read `docs/non_negotiable_constraints.md` in full. The ten constraints are inviolable. Any code that violates them is wrong even if it works.

Most critical:

- **No probability without provenance.** Every distribution carries `provenance_class` and `confidence_class`.
- **No clinical recommendation without missing-variable analysis.** Reports must list what could flip the decision.
- **No claim that Monte Carlo makes weak evidence strong.** Wide intervals are a feature, not a bug.
- **No single truth score.** Output is a distribution, never a verdict.
- **No LLM-only prior displayed without explicit warning.**

## Where to look for what

| You need... | Look in... |
|---|---|
| Project overview, philosophy | This file, then `README.md` |
| What to build first, second, third | `build/build_order.md` |
| Component specs (what each module does) | `specs/01_data_models.md` through `specs/08_cli_runner.md` |
| Belief network structure (the clinical model) | `networks/hf_ed_discharge_v0.yaml` |
| LLM prompts | `prompts/claim_extraction.md`, `prompts/node_parameterization.md` |
| Test fixtures | `examples/` |
| Phase 0 acceptance criteria | `tests/phase_0_acceptance.md` |
| Adversarial test cases | `tests/adversarial_suite.md` |
| Per-component unit tests | `tests/unit_test_specs.md` |
| Tech stack and dependencies | `build/tech_stack.md` |
| Master strategic plan (skim only) | `docs/master_plan.md` |
| Glossary of clinical terms | `docs/glossary.md` |
| Risks to watch for during build | `docs/risk_register.md` |

## Build order (high-level)

1. **Setup** — `pyproject.toml`, dependencies, directory skeleton
2. **Data models** — Pydantic schemas (`specs/01_data_models.md`)
3. **YAML loader** — Read `networks/hf_ed_discharge_v0.yaml` into typed objects
4. **Monte Carlo engine** — Pure NumPy sampling (`specs/04_monte_carlo_engine.md`)
5. **Decision option scorer** — Combine sampled nodes into per-option fitness
6. **Sensitivity analyzer** — Variance decomposition (`specs/05_sensitivity_analyzer.md`)
7. **Report generator** — Markdown output matching the target (`specs/06_report_generator.md`)
8. **CLI runner** — Glue: parse args, load files, run pipeline, write report (`specs/08_cli_runner.md`)
9. **Claim extractor** — Anthropic API call for Workflow A (`specs/02_claim_extractor.md`)
10. **Node parameterizer** — Maps claim type to prior, with provenance (`specs/03_node_parameterizer.md`)

Acceptance: `python -m pdde run --case examples/sample_case_HF-001.json --network networks/hf_ed_discharge_v0.yaml --output report.md` produces output similar in structure to `examples/sample_report_HF-001.md`.

## When to ask vs proceed

**Proceed without asking when:**
- A spec is ambiguous about implementation detail; pick the simplest path
- A test fixture is missing; create a placeholder consistent with the data models
- A library choice is reasonable; document your choice in a code comment

**Ask when:**
- You believe a spec contradicts a non-negotiable constraint
- A Phase 0 acceptance test would fail even with correct implementation due to spec bug
- A clinical content question requires real domain expertise (e.g., "should this prior really be Beta(14,5)?")

## Definition of done for Phase 0

Phase 0 is complete when:

1. The CLI runs end-to-end on `sample_case_HF-001.json` and produces a report
2. The Monte Carlo engine produces a posterior distribution over the six decision options
3. The report includes: ranked options with credible intervals, sensitivity drivers, prohibited-recommendation check, provenance warnings, and a "missing variables that would flip the decision" section
4. All six Phase 0 acceptance tests in `tests/phase_0_acceptance.md` pass
5. At least 5 of 10 adversarial tests in `tests/adversarial_suite.md` pass (the rest can fail in Phase 0; the failures themselves are the deliverable)
6. The codebase is under ~1500 lines of Python (toy v0 should not be larger)

## Last thing

The point of this build is not to produce a beautiful product. It is to discover what is wrong with the ontology, the priors, the YAML structure, and the output format **by building it once**. The Phase 1 rewrite will be vastly better because of what you learn in Phase 0.

Be fast. Be honest about placeholders. Make the failures visible.
