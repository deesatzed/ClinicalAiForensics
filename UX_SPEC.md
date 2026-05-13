# ClinAIForensics UX Specification

## Purpose

This UX specification defines how ClinAIForensics should be presented and used before additional implementation work. It is a product and review contract, not a runtime feature request.

ClinAIForensics is a clinical AI safety and audit workbench. It helps reviewers inspect whether a synthetic clinical decision episode, a domain pack, optional governed AI-answer mapping inputs, evidence references, uncertainty, provenance, and governance metadata are visible and auditable.

It is not a clinical decision engine.

## Users

### Leadership / Buyer

Leadership users need to understand what problem the project solves, why it is differentiated, what safeguards exist, and what investment or governance work remains.

Primary jobs:

- Understand that the tool makes clinical AI risk visible before deployment.
- See a safe synthetic demo without PHI or institutional approval claims.
- Compare the approach to generic AI evaluation, model confidence, or chatbot grading.
- Decide whether the workbench is worth further governance, validation, staffing, or integration investment.

Leadership should not be asked to interpret clinical thresholds, raw priors, or code internals during a short demo.

### Clinical AI Safety Reviewer

Clinical AI safety reviewers need to inspect whether the audit output exposes safety gates, missing data, uncertainty, evidence-reference status, AI-answer mapped-claim status when available, local governance status, and unresolved blockers.

Primary jobs:

- Verify that hard safety gates are visible and cannot be overridden.
- Check that missing, unsupported, blocked, malformed, deferred, and draft items remain visible.
- Confirm that advisory output does not become a final clinical recommendation.
- Review evidence-reference status without assuming source truth validation.
- Review governance metadata without activating local rules.
- Identify what additional review, evidence, or governance input is required.

### Developer / Informaticist

Developers and informaticists need a safe way to add synthetic fixtures, domain packs, evidence references, mapping specs, tests, and report visibility without weakening guardrails.

Primary jobs:

- Add or update synthetic CDE examples.
- Add or update explicit domain-pack mappings.
- Add evidence registry/linking metadata without truth scoring.
- Add deterministic AI-answer mapping specifications only from governed synthetic inputs.
- Add local overlay metadata only as non-activating governance visibility unless activation is separately approved.
- Preserve test coverage, provenance, privacy, and report contract guardrails.

## Product Definition

ClinAIForensics is a clinical AI safety/audit workbench for synthetic Clinical Decision Episode review.

It currently provides:

- strict loading of synthetic CDE and domain-pack files.
- deterministic safety-gate evaluation.
- explicit prior resolution.
- deterministic seeded Monte Carlo sampling for explicit supported priors.
- uncertainty-budget and value-of-information visibility.
- deterministic decision-profile assembly.
- status ledger projection.
- evidence-reference status visibility.
- API-only deterministic AI-answer mapped-claim status when governed mapped claims are supplied.
- metadata-only local overlay governance intake validation.
- advisory Markdown report rendering.
- JSONL provenance logging.

ClinAIForensics does not decide what a clinician should do. It shows what is known, missing, blocked, unsupported, deferred, draft, or explicitly mapped.

## Core Demo Workflow

The safe demo path uses synthetic/non-PHI materials only.

1. Input a synthetic case.
   - Use a root `examples/*.json` CDE fixture or the canonical v0.3 stable fixture.
   - Do not use patient records, raw notes, identifiers, or production EHR exports.

2. Input a domain pack.
   - Use `pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml`.
   - Domain-pack mappings must be explicit. Do not infer clinical meaning from labels or token overlap.

3. Optionally input synthetic AI-answer mapping data.
   - Current mapping is API-only and deterministic.
   - Only governed synthetic mapped claims should be used.
   - Raw AI-answer text should not be stored in pipeline results, reports, or provenance logs.
   - Absence of an AI answer is acceptable for the core CDE audit demo.

4. Run the audit.
   - Run validation and report generation through the CLI.
   - Use deterministic iterations and seed values for reproducible demos.

Current real demo command:

```bash
python -m pdde report \
  --cde examples/hf_cde_stable.json \
  --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml \
  --output reports/demo_report.md \
  --log logs/demo_run.jsonl
```

Deferred future command shape:

```bash
python -m pdde audit-answer \
  --cde examples/hf_cde_stable.json \
  --domain domain_packs/hf_ed_discharge/domain_pack.yaml \
  --ai-answer examples/synthetic_ai_answer.json \
  --output reports/ai_answer_audit.md
```

`audit-answer` does not exist yet. It must not be implemented until governed synthetic AI-answer examples, deterministic mapping boundaries, omission boundaries, overstatement boundaries, unsupported-claim boundaries, approval ownership, and explicit non-grading scope are defined.

5. Generate a Markdown report.
   - The report is advisory and evidence-preserving.
   - It should show safety, evidence-reference, prior, simulation, uncertainty, VOI, decision-profile, local overlay, AI-answer mapping, and governance status where available.

6. Generate a provenance log.
   - The JSONL log should preserve run metadata and status summaries.
   - It should avoid raw clinical text, raw patient-state values, raw owner/source/review free text, raw AI-answer text, gate evidence strings, and simulation samples.

7. Review safety/evidence/uncertainty/governance status.
   - The reviewer should look for visible blocked, missing, deferred, unsupported, malformed, draft, and pending-review items.
   - The reviewer should not treat the report as a clinical recommendation.

## Leadership Demo Flow

### Five-Minute Script

Minute 0 to 1: Problem framing.

- "Clinical AI failures often happen at the boundary between a model answer, patient context, local workflow, evidence support, and governance status."
- "This workbench does not replace clinical judgment. It makes safety, evidence, uncertainty, and governance gaps explicit before anyone claims an AI answer is safe."

Minute 1 to 2: Inputs.

- Show a synthetic case fixture.
- Show the domain pack.
- Point out that the demo uses synthetic/non-PHI data and neutral Example Health System wording.

Minute 2 to 3: Run.

- Run `python -m pdde validate`.
- Run `python -m pdde report`.
- Optionally show report generation with `--output` and `--log`.

Minute 3 to 4: Outputs.

- Show the Markdown report sections:
  - advisory status.
  - safety gate results.
  - evidence reference status.
  - prior and simulation summaries.
  - uncertainty and VOI status.
  - decision profile status.
  - local overlay/governance status.
  - AI-answer mapped-claim status if a governed synthetic mapping is supplied.

Minute 4 to 5: Why it matters.

- "The value is not that it says yes or no. The value is that it prevents missing assumptions, unsupported claims, hidden uncertainty, and unapproved local rules from disappearing."
- "The current next gate is governance input, not more autonomous clinical logic."

### What To Show

- The synthetic fixture path.
- The domain-pack path.
- A short CLI validation command.
- A Markdown report excerpt with status sections.
- A JSONL provenance record excerpt with IDs and statuses only.
- The task queue showing governance blockers.

### What To Avoid Claiming

- Do not claim clinical approval.
- Do not claim validated risk prediction.
- Do not claim evidence truth validation.
- Do not claim automated clinical action.
- Do not claim outcome calibration.
- Do not claim the tool grades free-text AI answers unless a governed deterministic mapped-claim artifact is explicitly supplied.
- Do not claim the system says "safe discharge" or "unsafe discharge."

## Reviewer Workflow

Reviewers inspect status visibility and guardrail behavior.

### What Reviewers Inspect

- CDE and domain-pack load status.
- Explicit domain-pack mapping status.
- Safety gate statuses.
- Prior resolution statuses.
- Monte Carlo sampled versus non-sampled prior status.
- Uncertainty-budget items.
- Value-of-information items.
- Decision profile statuses.
- Evidence-reference link statuses.
- AI-answer mapped-claim statuses when available.
- Local overlay and governance intake statuses.
- Provenance log redaction boundaries.
- Report contract language.

### Status Meaning

- `passed`: A deterministic rule or validation item was satisfied.
- `failed`: A deterministic rule found a blocking or failing condition.
- `blocked`: The item cannot be used because a guardrail prevents it.
- `missing`: Required explicit input is absent.
- `unsupported`: The input type or definition is outside the current implementation boundary.
- `malformed`: The input exists but fails structural validation.
- `deferred`: The item is visible but awaiting governance, data, or implementation prerequisites.
- `draft`: The item is metadata-only, not reviewed, or not ready for active use.
- `pending_review`: The item has been submitted for governance review but is not approved.
- `linked`: An explicit evidence reference matches a supplied evidence registry object.
- `unknown_source`: An evidence reference points to a source not present in the supplied registry.

These statuses are review signals, not clinical recommendations.

### How Unresolved Or Blocking Items Appear

Unresolved or blocking items should remain visible in at least one of:

- status ledger.
- Markdown report.
- typed pipeline result.
- provenance JSONL log.
- task queue or governance intake template.

They must not be silently dropped, converted into favorable certainty, or hidden behind a composite score.

## Developer Workflow

Developers and informaticists add new materials through explicit, testable artifacts.

### Adding New Synthetic CDE Examples

1. Confirm the example is synthetic and non-PHI.
2. Add the fixture under `examples/`.
3. Preserve the existing CDE schema.
4. Add tests or extend acceptance coverage.
5. Validate through the CLI.
6. Generate a report and inspect visible missing/blocked/deferred statuses.

### Adding New Domain Packs

1. Use explicit IDs for options, gates, priors, evidence references, uncertainty items, and VOI items.
2. Avoid fuzzy mapping or label-derived clinical inference.
3. Add explicit mapping sections where components depend on each other.
4. Add loader and validation tests.
5. Keep clinical assumptions in the domain pack, not hidden in Python code.

### Adding Mapping Specifications

1. Use governance intake templates first.
2. Use deterministic claim patterns only.
3. Store mapped claim metadata, not raw AI-answer text.
4. Add tests for mapped, unmapped, unsupported, mismatched, redacted, and blocked cases.
5. Keep mapping API-only unless a later task explicitly approves CLI behavior.

### Adding Evidence References

1. Treat evidence objects as immutable receipts.
2. Treat links and assessments as contextual and versioned.
3. Validate explicit IDs only.
4. Do not implement source truth scoring unless a future governed task explicitly authorizes it.

### Adding Local Overlay Metadata

1. Use `LOCAL_OVERLAY_GOVERNANCE_INTAKE.md`.
2. Treat entries as metadata-only unless future activation is separately approved.
3. Redact raw owner/source/review free text from report and provenance outputs where required.
4. Keep local clinical rules inactive until explicit approval, tests, safety review, rollback plan, audit trail, and a decision entry exist.

## Required Outputs

ClinAIForensics UX must preserve these outputs:

- Advisory Markdown report.
- Provenance JSONL log.
- Status ledger.
- Evidence reference status.
- AI-answer mapped-claim status when available.
- Governance status.

Each output should be deterministic, reviewable, and safe for synthetic/non-PHI demo use.

## Explicit Non-Goals

- No final clinical recommendations.
- No AI doctor.
- No automated clinical action.
- No evidence truth scoring.
- No citation correctness scoring.
- No PHI.
- No institutional approval claims.
- No hidden scoring.
- No invented thresholds, utilities, priors, weights, or clinical formulas.
- No local clinical rule activation without separate governance approval.
- No LLM clinical judgment.

## Remaining UX Gaps

### Synthetic AI Answer Artifact

`examples/synthetic_ai_answer.json` now provides a governed synthetic/non-PHI AI-answer artifact for demonstrations and reviewer workflow tests. It exercises mapped, unmapped, unsupported, omission, and overstatement boundaries without adding LLM judgment or answer grading.

Remaining gap: the artifact is not wired into a CLI command. `audit-answer` remains deferred and non-existent until a later governed implementation task explicitly authorizes command behavior.

### Simple Demo Command

The current CLI is usable, and the real demo command is documented above. A shorter demo command or wrapper would reduce leadership-demo friction. Any new command should preserve current report/provenance behavior and avoid hidden defaults that imply clinical approval.

### Leadership One-Pager

A one-page PDF or Markdown summary would help leadership audiences understand the problem, workbench concept, novelty, safeguards, current limits, and governance asks without reading the full build history.

### Final Demo Package

A final demo package should include:

- synthetic case fixture.
- domain pack.
- optional governed mapped-claim artifact.
- generated Markdown report.
- provenance JSONL excerpt.
- leadership one-pager.
- short talk track.
- explicit "not approved for clinical use" disclaimer.

## UX Milestones

- `UX-001: Define end-user demo flow`: complete in this specification.
- `UX-002: Create governed synthetic AI answer artifact`: complete with `examples/synthetic_ai_answer.json`.
- `UX-003: Create leadership-friendly demo report`: blocked until the desired leadership report framing and demo-report scope are approved.
- `UX-004: Create simple demo command or wrapper`: blocked until the demo artifact set is stable and the command semantics are approved.
- `UX-005: Create final demo package`: blocked until the demo report, provenance excerpt, one-pager, talk track, and governance disclaimers are ready.

## UX Guardrails

The UX must reinforce the engineering guardrails:

- Make uncertainty visible.
- Make missingness visible.
- Make governance status visible.
- Make evidence-reference status visible without truth claims.
- Keep draft local overlay metadata non-activating.
- Keep optional AI-answer mapping deterministic and governed.
- Prefer IDs, statuses, and provenance references over raw clinical text.
- Avoid any language that implies deployment, clinical validation, or institutional approval.
