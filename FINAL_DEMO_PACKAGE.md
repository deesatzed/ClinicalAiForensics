# Final Demo Package

## Package Status

This is the organization-neutral ClinAIForensics demo package for leadership and technical review.

It is synthetic, non-PHI, advisory-only, uncalibrated, and not approved for clinical use.

This package demonstrates a clinical AI safety/audit workbench. It does not demonstrate a clinical decision engine, answer grader, evidence truth engine, production deployment, or AI doctor.

## What To Open First

| Audience | Start Here | Purpose |
|---|---|---|
| Leadership or buyer | `LEADERSHIP_ONE_PAGER.md` | One-page value, risk, and guardrail framing. |
| Demo presenter | `DEMO_TALK_TRACK.md` | Five-minute talk track with safe language. |
| Technical reviewer | `DEMO.md` | Command-by-command local demo instructions. |
| Architecture reviewer | `README.md` and `UX_SPEC.md` | Product boundary, CLI/API behavior, and UX contract. |
| Audit reviewer | `DEMO_PROVENANCE_EXCERPT.md` | Status-only provenance shape and privacy boundary. |

## Demo Artifacts

| Artifact | Path | Status |
|---|---|---|
| Synthetic case | `examples/hf_cde_stable.json` | Tracked synthetic/non-PHI fixture. |
| Domain pack | `pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml` | Tracked canonical v0.3 domain pack. |
| Synthetic AI answer artifact | `examples/synthetic_ai_answer.json` | Tracked governed demo artifact; API/test boundary only. |
| Leadership demo report | `LEADERSHIP_DEMO_REPORT.md` | Tracked curated leadership-facing explanation. |
| Leadership one-pager | `LEADERSHIP_ONE_PAGER.md` | Tracked concise leadership handout. |
| Demo talk track | `DEMO_TALK_TRACK.md` | Tracked five-minute script. |
| Provenance excerpt | `DEMO_PROVENANCE_EXCERPT.md` | Tracked normalized status-only excerpt. |
| Generated Markdown report | `reports/demo_report.md` | Ignored; regenerate with `python -m pdde demo`. |
| Generated JSONL log | `logs/demo_run.jsonl` | Ignored; regenerate with `python -m pdde demo`. |

## Run The Demo

```bash
python -m pdde demo
```

Expected console output:

```text
Log written: logs/demo_run.jsonl
Report written: reports/demo_report.md
Demo complete: synthetic/non-PHI advisory output only; not approved for clinical use.
```

The command uses:

- `examples/hf_cde_stable.json`
- `pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml`
- `reports/demo_report.md`
- `logs/demo_run.jsonl`
- 5 Monte Carlo iterations
- random seed 17

## What To Show

1. `LEADERSHIP_ONE_PAGER.md`
2. `python -m pdde demo`
3. `reports/demo_report.md`
4. `DEMO_PROVENANCE_EXCERPT.md`
5. `LEADERSHIP_DEMO_REPORT.md` if more explanation is useful

## What To Emphasize

- The workbench makes safety, evidence-reference, uncertainty, and governance status visible.
- Missing, unsupported, deferred, draft, and blocked items remain visible.
- The demo does not use PHI, EHR data, external services, or LLM judgment.
- The current CLI audits the CDE and domain pack.
- The governed synthetic AI-answer artifact exists for demo/reviewer workflow context, but the CLI does not consume it yet.
- `audit-answer` remains deferred until governed command semantics are approved.

## What Not To Claim

- Do not say the system recommends discharge, admission, medication starts, or medication stops.
- Do not say the AI answer is correct or incorrect.
- Do not say the evidence is true, sufficient, or clinically validated.
- Do not say the output is outcome-calibrated.
- Do not say this is approved for clinical use.
- Do not say this is production-ready.
- Do not say local clinical rules are active.

## Generated Artifact Policy

Generated demo artifacts are intentionally ignored by git:

- `reports/demo_report.md`
- `logs/demo_run.jsonl`

This prevents run-specific timestamps, append-only JSONL records, and generated Markdown from becoming source-of-truth files. The tracked package documents how to regenerate and inspect them.

## Verification

Run:

```bash
python -m pdde demo
python -m pytest
python -m py_compile pdde/*.py
python -m pdde --help
```

Expected current test status: 156 passing tests.

## Current Limitations

- `audit-answer` CLI does not exist.
- The synthetic AI-answer artifact is not consumed by `python -m pdde demo`.
- AI-answer omission and overstatement boundaries are documented but not active.
- Evidence-reference visibility is status-only; evidence truth validation is not implemented.
- Calibration and outcome linkage are not implemented.
- Local overlay metadata remains non-activating.
- No PHI workflow exists.

## Safe Close

ClinAIForensics does not tell clinicians what to do. It creates an auditable safety layer around clinical AI output so reviewers can see what passed, what triggered concern, what evidence was referenced, what is missing, what governance has not approved, and why the result remains advisory only.
