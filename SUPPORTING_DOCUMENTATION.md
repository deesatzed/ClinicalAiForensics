# Supporting Documentation

## Purpose

This file is the navigation guide for reviewers, leadership, and developers.

It organizes the current ClinAIForensics documentation into a recommended reading order so a reviewer can understand the demo package, safety boundaries, architecture, provenance model, and maintenance workflow without reading the full build history.

## Start Here

| Document | Why Read It |
|---|---|
| `README.md` | Technical reviewer overview, setup, commands, architecture, guardrails, and test status. |
| `LEADERSHIP_ONE_PAGER.md` | Concise leadership-facing explanation of the problem, value, novelty, and limits. |
| `FINAL_DEMO_PACKAGE.md` | Demo package index, artifact manifest, run command, generated-output policy, and claim boundaries. |
| `DEMO_TALK_TRACK.md` | Five-minute presenter script with safe language and claims to avoid. |
| `UX_SPEC.md` | Product UX contract for leadership, clinical safety reviewer, and developer workflows. |

## Leadership / Executive Review

| Document | Purpose |
|---|---|
| `LEADERSHIP_ONE_PAGER.md` | One-page explanation of what the project solves, why it matters, and what it must not claim. |
| `LEADERSHIP_DEMO_REPORT.md` | Leadership-facing demo report/excerpt showing safety, evidence, uncertainty, governance, and provenance status. |
| `FINAL_DEMO_PACKAGE.md` | Main demo package index for what to open, what to show, and what not to claim. |
| `DEMO_TALK_TRACK.md` | Presenter script for a five-minute leadership or mixed-audience walkthrough. |

## Technical Reviewer

| Document | Purpose |
|---|---|
| `README.md` | Main technical overview with setup, commands, module map, generated outputs, guardrails, and test command. |
| `DEMO.md` | Command-by-command local demo script and reviewer checks. |
| `UX_SPEC.md` | End-user workflow, required outputs, non-goals, and UX milestone status. |
| `PHASE0_HANDOFF.md` | Phase 0 handoff with what works, how to run it, limitations, and stop/go recommendation. |
| `PHASE1_COMPLETION_REVIEW.md` | Phase 1 review of completed tasks, runtime changes, guardrails, limitations, and Phase 2 candidates. |
| `BUILD_LOG.md` | Phase 0 build log, architecture summary, structural review, and ranked improvement opportunities. |
| `REPO_MAP.md` | Current repository map, source-material inventory, architecture, tests, and implementation status. |

## Safety / Governance Reviewer

| Document | Purpose |
|---|---|
| `STANDARDS.md` | Project safety, output, prior governance, engineering, verification, and audit standards. |
| `DECISIONS.md` | Architecture, safety, scope, governance, UX, and demo-package decision log. |
| `BASELINE_POLICY.md` | Baseline, submodule, generated-artifact, and phase-boundary policy. |
| `LOCAL_OVERLAY_GOVERNANCE_INTAKE.md` | Metadata-only template for local overlay governance; explicitly non-activating. |
| `AI_ANSWER_MAPPING_GOVERNANCE_INTAKE.md` | Intake template for governed AI-answer examples and deterministic mapping boundaries. |
| `EVIDENCE_AUDIT_HANDOFF.md` | Evidence/citation audit handoff defining what is ready, deferred, and not implemented. |
| `CALIBRATION_OUTCOME_PREREQUISITES.md` | Prerequisites for future calibration or outcome-linkage work before outcome claims can be made. |

## Evidence / Provenance Reviewer

| Document | Purpose |
|---|---|
| `docs/architecture/evidence_registry_decision.md` | Evidence-registry architecture decision and immutable-receipt boundary. |
| `docs/architecture/evidence_identity_model.md` | Evidence identity model for stable evidence objects and contextual links/assessments. |
| `docs/architecture/evidence_lineage_rules.md` | Lineage rules for observed, inferred, synthesized, and speculative derivations. |
| `docs/architecture/evidence_storage_matrix.md` | Storage-option matrix and persistence/linking tradeoffs. |
| `DEMO_PROVENANCE_EXCERPT.md` | Status-only provenance excerpt for the `python -m pdde demo` workflow and privacy boundary. |

## Developer / Maintainer

| Document | Purpose |
|---|---|
| `GOAL.md` | Mission, source priority, Phase 0 target, non-goals, and success criteria. |
| `IMPLEMENT.md` | Implementation plan and expected package/module shape. |
| `TASK_QUEUE.md` | Ordered task queue, statuses, acceptance criteria, blockers, and deferred work. |
| `PROGRESS.md` | Work log and verification history. |
| `REPO_MAP.md` | Repository structure, current architecture, and implementation status. |
| `pyproject.toml` | Python package metadata, dependencies, and pytest configuration. |
| `tests/` | Unit, integration, CLI, report, provenance, and acceptance tests. |

## Generated Outputs

Generated reports and logs are ignored by git by default:

- `reports/demo_report.md`
- `logs/demo_run.jsonl`

Regenerate them with:

```bash
python -m pdde demo
```

The tracked source of truth is the command, fixtures, code, and Markdown package docs. Generated outputs are reproducible local artifacts with run-specific timestamps and append-only JSONL records.

## What Not To Claim

- Not a clinical decision engine.
- Not an AI doctor.
- Not production deployed.
- Not institutionally approved.
- Not evidence truth scoring.
- Not answer grading.
- Not outcome-calibrated.
- Not PHI-ready.

## Current Demo Command

```bash
python -m pdde demo
```

## Verification

Current expected verification:

```bash
python -m pdde demo
python -m pytest
python -m py_compile pdde/*.py
python -m pdde --help
```

Expected current test status: 156 passing tests.
