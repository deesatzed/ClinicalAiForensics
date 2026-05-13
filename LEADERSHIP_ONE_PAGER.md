# ClinAIForensics Leadership One-Pager

## The Problem

Clinical AI answers can sound confident while hiding safety concerns, missing case context, unsupported claims, weak evidence links, and governance gaps.

Before clinical AI output can be trusted, reviewers need a repeatable way to ask:

- What did the AI output imply?
- Which explicit safety boundaries did it touch?
- What evidence was referenced?
- What is missing or unsupported?
- What remains governance-blocked?
- Why is the result still advisory only?

## What ClinAIForensics Is

ClinAIForensics is a clinical AI safety/audit workbench.

It is not a clinical decision engine. It does not decide whether to discharge, admit, prescribe, stop, or approve care.

The current demo uses a synthetic heart failure ED discharge scenario to show how the workbench preserves safety, uncertainty, evidence-reference, governance, and provenance status.

## What The Demo Shows

The demo runs:

```bash
python -m pdde demo
```

It generates:

- `reports/demo_report.md`
- `logs/demo_run.jsonl`

The report shows:

- advisory status.
- deterministic safety-gate status.
- missing, unsupported, deferred, and draft items.
- prior provenance and uncalibrated Monte Carlo prior summaries.
- uncertainty and value-of-information status.
- evidence-reference status without evidence truth claims.
- local governance status without activating local clinical rules.
- provenance references.

## Why It Matters

The value is not that the system says what to do.

The value is that it prevents unsupported AI claims, hidden uncertainty, missing data, and unapproved governance assumptions from disappearing inside a confident answer.

## What Is Novel

- It treats clinical AI output as something to audit, not blindly trust.
- It separates safety gates, evidence links, uncertainty, governance status, and provenance.
- It keeps missing and unsupported items visible.
- It rejects hidden scoring and final recommendations unless explicitly governed.
- It preserves an audit trail without storing PHI or raw AI-answer text in logs.

## What It Can Be Used For

- Demonstrating clinical AI safety governance.
- Reviewing synthetic clinical AI answer risks.
- Testing deterministic safety-gate behavior.
- Showing missing data and unresolved uncertainty.
- Showing evidence-reference status without claiming source truth.
- Creating an auditable path toward governed AI output review.

## What It Must Not Be Used For

- Making clinical decisions.
- Replacing clinician judgment.
- Automatically approving discharge, admission, or medication decisions.
- Claiming evidence is clinically true.
- Claiming outcome calibration.
- Claiming institutional approval.
- Processing PHI.

## Current State

The current demo package is ready for organization-neutral leadership and technical review.

It is synthetic, non-PHI, advisory-only, uncalibrated, and not approved for clinical use.

## Next Work After Demo

- Define governed `audit-answer` command semantics.
- Decide which AI-answer examples and mapping boundaries are approved.
- Define evidence review governance before truth/citation validation.
- Define calibration/outcome prerequisites before outcome claims.
- Keep local overlay rules non-activating until explicit governance approval exists.
