# Clinical AI Safety Audit Demo

## Advisory Status

This is a synthetic, non-PHI leadership demo artifact for ClinAIForensics.

It is not approved for clinical use. It is not a clinical decision, clinical recommendation, model score, answer grade, evidence-truth claim, or institutional approval statement.

The purpose of this demo report is to show how a clinical AI safety/audit workbench can make safety, evidence, uncertainty, provenance, and governance gaps visible before an AI-generated clinical answer is trusted.

## Executive Summary

Clinical AI outputs can sound complete even when they contain unsupported claims, missing context, unreviewed local workflow assumptions, or unapproved governance dependencies.

ClinAIForensics is designed as an audit layer around those outputs. In this synthetic heart failure ED discharge scenario, the workbench can show:

- what deterministic safety checks passed, failed, or remained unsupported.
- which AI-answer claims matched governed risky-claim patterns.
- which evidence references are linked, pending, missing, or not yet truth-validated.
- which uncertainty and value-of-information items remain visible.
- which local governance items are draft, deferred, or non-activating.
- why the result remains advisory only.

The value is not that the system says what to do. The value is that it prevents unsupported AI claims, hidden uncertainty, missing governance, and unreviewed local assumptions from disappearing.

## Demo Inputs

| Input | Path | Demo Role |
|---|---|---|
| Synthetic case | `examples/hf_cde_stable.json` | Synthetic/non-PHI heart failure ED discharge CDE. |
| Domain pack | `pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml` | Explicit rules, gates, priors, uncertainty items, VOI items, and mappings. |
| Synthetic AI answer artifact | `examples/synthetic_ai_answer.json` | Governed synthetic/non-PHI AI-answer artifact with mapped, unmapped, omission, overstatement, and unsupported boundaries. |

Current real CLI report command:

```bash
python -m pdde report \
  --cde examples/hf_cde_stable.json \
  --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml \
  --output reports/demo_report.md \
  --log logs/demo_run.jsonl
```

Important limitation: the current CLI report path audits the CDE and domain pack. It does not yet accept `examples/synthetic_ai_answer.json`. AI-answer mapped-claim behavior currently exists through the API-only deterministic mapper and tests.

Deferred future command shape:

```bash
python -m pdde audit-answer \
  --cde examples/hf_cde_stable.json \
  --domain domain_packs/hf_ed_discharge/domain_pack.yaml \
  --ai-answer examples/synthetic_ai_answer.json \
  --output reports/ai_answer_audit.md
```

`audit-answer` does not exist yet and must not be implemented until governed command semantics are approved.

## What Passed

The current synthetic CDE fixture can be loaded and validated against the canonical heart failure ED discharge domain pack.

The existing Phase 0/1/2 pipeline can produce:

- an advisory Markdown report.
- a provenance JSONL log.
- a status ledger.
- deterministic safety-gate visibility.
- prior-resolution visibility.
- Monte Carlo summaries for explicit supported priors.
- uncertainty-budget and value-of-information visibility.
- evidence-reference status visibility.
- governance and local-overlay status visibility.

This means the demo can show a working audit pipeline without using PHI, live EHR data, external services, or LLM judgment.

## Safety Gate Status

Safety gates are deterministic checks defined by the domain pack. They run before probabilistic or advisory presentation.

| Safety Area | Leadership Interpretation | Demo Status |
|---|---|---|
| Blood pressure, kidney function, potassium, follow-up, DKA risk, volume status | Explicit case-context checks are evaluated and surfaced as passed, blocked, triggered, missing, or unsupported. | Visible in report/status ledger. |
| Wrong-indication claim gates | These require structured AI-answer mapped claims. Direct CDE-only runs keep unsupported claim gates visible rather than silently passing them. | Visible as unsupported in CDE-only report. |
| AI-answer mapped risky claims | When the governed synthetic AI-answer artifact is supplied through the API boundary, two risky claim types can become visible as structured mapped claims. | API/test path only; no CLI command yet. |

Leadership takeaway: the system is built to expose safety concerns, not to approve clinical action.

## AI Mapped-Claim Status

The governed synthetic AI-answer artifact includes two deterministic risky-claim examples:

| Claim Type | Why It Matters | Current Boundary |
|---|---|---|
| `sotalol_as_hf_beta_blocker` | Represents a wrong-indication pattern where sotalol is framed as part of HFrEF/HFmrEF beta-blocker GDMT. | Mapped only when the explicit governed pattern is present. |
| `glp1_hf_admission_prevention` | Represents an unsupported HFrEF/HFmrEF ED anti-admission claim pattern. | Mapped only when the explicit governed pattern is present. |

The artifact also defines boundaries that must not be over-interpreted:

| Boundary | Demo Meaning | Activation Status |
|---|---|---|
| Unmapped contextual mention | Similar medication mentions do not activate gates unless the explicit pattern matches. | Non-activating. |
| Omission | Missing content is documented as a future review need, not graded. | Not approved for mapping. |
| Overstatement | Broad assurance language is documented as a future review need, not scored. | Not approved for mapping. |
| Unsupported similarity | Similarity, synonyms, and clinical intuition cannot create a mapped claim. | Non-activating. |

Leadership takeaway: the project uses deterministic, governed mapping boundaries rather than free-text AI judgment.

## Evidence Reference Status

Evidence references are treated as explicit links and receipts, not automatic truth claims.

| Evidence UX Principle | Demo Behavior |
|---|---|
| Evidence object identity should be stable. | Evidence objects are modeled as immutable receipts. |
| Evidence links are contextual. | Links can show whether a component references an evidence object. |
| Evidence assessment is separate from evidence existence. | The system does not claim evidence is true, sufficient, or clinically validated. |
| Missing or pending references stay visible. | Missing, pending, unsupported, and deferred evidence-reference statuses are not silently dropped. |

Leadership takeaway: the workbench supports evidence accountability without pretending to automate evidence truth validation.

## Uncertainty And Value-Of-Information Status

The workbench keeps uncertainty visible instead of converting missing information into false confidence.

Visible uncertainty categories include:

- patient context uncertainty.
- evidence uncertainty.
- local execution uncertainty.
- monitoring and rescue uncertainty.
- harm uncertainty.
- preference or feasibility uncertainty.
- prior quality uncertainty.

Value-of-information items identify what additional information could matter to interpretation, such as labs, follow-up availability, volume status, medication access, or patient preference.

Leadership takeaway: the output is designed to make review pressure visible when data is missing or assumptions are weak.

## Governance Status

Governance metadata is intentionally conservative.

| Governance Area | Demo Status |
|---|---|
| Local overlay metadata | Metadata-only, draft/deferred, non-activating unless separate approval exists. |
| AI-answer artifact | Synthetic/non-PHI, documentation-only, not approved for clinical use. |
| Evidence audit | Evidence-reference status is visible; source truth validation is not implemented. |
| Calibration/outcome linkage | Deferred until governance, labels, outcomes, and data-handling rules exist. |
| Clinical deployment | Not authorized. |

Leadership takeaway: the system makes governance gaps explicit instead of hiding them behind a confident answer.

## Unresolved Items

The current demo package intentionally leaves several items unresolved:

- `audit-answer` CLI command is not implemented.
- AI-answer omission and overstatement mapping are documented but not active.
- Evidence truth validation and citation correctness scoring are not implemented.
- Calibration and outcome linkage are not implemented.
- Local clinical rules are not active.
- No PHI workflow exists.
- No institutional approval is claimed.

These are not bugs in the demo. They are guardrails that prevent the workbench from overstating its authority.

## Provenance References

The demo should use provenance references rather than raw clinical text:

| Provenance Item | Safe Reference |
|---|---|
| Case fixture | `examples/hf_cde_stable.json` |
| Domain pack | `pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml` |
| Synthetic AI answer artifact | `examples/synthetic_ai_answer.json` |
| Report output | `reports/demo_report.md` |
| Provenance log output | `logs/demo_run.jsonl` |

Provenance logs should use IDs, statuses, source references, and counts. They should not store raw AI-answer text, raw patient-state values, gate evidence strings, simulation samples, PHI, or local owner/source/review free text.

## What Leadership Should Remember

ClinAIForensics is a safety inspection system for clinical AI output.

It helps answer:

- What did the AI output imply?
- Which explicit safety or governance boundaries did it touch?
- Which evidence references were visible?
- What was missing or unsupported?
- What remains deferred or blocked?
- Why is this still advisory only?

It must not be described as:

- an AI doctor.
- a final clinical decision engine.
- an evidence truth engine.
- an answer grader.
- a discharge approval tool.
- an institutional approval mechanism.
- a production clinical deployment.

## Recommended Demo Close

Use this closing language:

> ClinAIForensics does not tell clinicians what to do. It creates an auditable safety layer around clinical AI output so reviewers can see what passed, what triggered concern, what evidence was referenced, what is missing, what governance has not approved, and why the result remains advisory only.
