# Demo Talk Track

## Setup

Audience: leadership, clinical AI safety reviewers, and technical reviewers.

Scenario: an organization-neutral, synthetic heart failure ED discharge case.

Positioning: ClinAIForensics is a clinical AI safety/audit workbench, not a clinical decision engine.

## Five-Minute Script

### 0:00 - 0:45: Problem

Clinical AI answers can look complete even when they contain unsafe implications, missing patient context, weak evidence references, uncalibrated priors, or unapproved local workflow assumptions.

ClinAIForensics is designed to inspect those outputs before anyone trusts them.

Safe language:

> This system does not tell a clinician what to do. It shows what must be reviewed before a clinical AI answer can be trusted.

### 0:45 - 1:30: Inputs

Show the package inputs:

- `examples/hf_cde_stable.json`
- `pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml`
- `examples/synthetic_ai_answer.json`

Safe language:

> These are synthetic, non-PHI demo artifacts. The current CLI audits the CDE and domain pack. The synthetic AI-answer artifact documents governed mapping boundaries, but the CLI does not consume it yet.

### 1:30 - 2:00: Run

Run:

```bash
python -m pdde demo
```

Expected output:

```text
Log written: logs/demo_run.jsonl
Report written: reports/demo_report.md
Demo complete: synthetic/non-PHI advisory output only; not approved for clinical use.
```

Safe language:

> This is a deterministic local demo. It does not call an LLM, read an EHR, use PHI, or deploy a service.

### 2:00 - 3:15: Report

Open `reports/demo_report.md`.

Point to:

- `Advisory Status`
- `Safety Gate Results`
- `Decision Profile Statuses`
- `Why There Is No Top Option`
- `Evidence Reference Status`
- `Missing Unsupported Deferred And Blocked Items`
- `Calibration Status`
- `Limitations`

Safe language:

> The report makes status visible. It does not produce a recommendation, truth score, trust score, or discharge approval.

### 3:15 - 4:00: Provenance

Open `DEMO_PROVENANCE_EXCERPT.md`.

Point to:

- command name: `demo`
- CDE and domain-pack paths
- component status counts
- evidence-reference status
- safety-gate status counts
- local overlay draft status
- decision-profile status counts

Safe language:

> The provenance log records IDs, statuses, counts, paths, and source references. It avoids PHI, raw AI-answer text, raw patient-state payloads, raw simulation samples, and local owner/source/review free text.

### 4:00 - 4:45: Value

Use this framing:

> The value is not automated clinical action. The value is an auditable safety layer that prevents missing data, unsupported claims, unreviewed evidence links, and governance gaps from being hidden inside a confident AI answer.

### 4:45 - 5:00: Close

Use this exact close:

> ClinAIForensics does not tell clinicians what to do. It creates an auditable safety layer around clinical AI output so reviewers can see what passed, what triggered concern, what evidence was referenced, what is missing, what governance has not approved, and why the result remains advisory only.

## Avoid Saying

- The system recommends discharge.
- The system recommends admission.
- The AI answer is correct.
- The evidence is true.
- The output is outcome-calibrated.
- The demo is approved for clinical use.
- The demo is production-ready.
- Local clinical rules are active.
