# Non-Negotiable Design Constraints

These ten rules are inviolable. Any code that violates them is wrong even if it compiles, passes tests, or "works."

If a spec elsewhere in this package appears to conflict with a constraint here, the constraint wins and the spec is wrong. Flag the conflict and ask.

---

## 1. No single truth score

The system never collapses output into a single "correctness" number. Output is always a distribution with at least:

- Median
- 90% credible interval
- Category probabilities (action-ready / conditional / needs-more-data / discouraged / unsafe)

A summary statistic alone is forbidden in the report. The distribution is the answer.

## 2. No probability without provenance

Every probability distribution in the system carries:

- `provenance_class`: one of `guideline_mapped`, `trial_parsed`, `panel_elicited`, `local_outcome`, `panel_elicited_pending`, `llm_unverified`
- `confidence_class`: one of `high`, `moderate_unverified`, `low_unverified`
- `last_reviewed` date (may be null for placeholders)
- `provenance_detail` string explaining the source

A probability without these fields is not allowed to enter the Monte Carlo engine.

## 3. No local rule without owner and status

Every Temple-specific rule in the local overlay YAML has:

- `status`: one of `draft`, `verified`, `deprecated`, `retired`
- `owner`: named clinical or operational role (may be `pending`)
- `verified_by`: name or `null`
- `verified_date`: ISO date or `null`

The report visibly distinguishes draft from verified rules. A draft rule cannot drive a recommendation without a visible warning.

## 4. No LLM-only prior displayed without warning

If a prior has `provenance_class: llm_unverified` or `confidence_class: low_unverified`, the report must include a prominent warning that the value is illustrative only and has not been formally elicited or calibrated.

LLM-only priors are allowed in Phase 0 to bootstrap the system. They are not allowed in any clinical deployment.

## 5. No recommendation without missing-variable analysis

Every Decision Fitness Report contains a section listing variables that, if changed or filled in, could flip the top-ranked recommendation. This list is generated from sensitivity analysis, not added as boilerplate.

If sensitivity analysis returns no drivers above threshold, the section says "no single variable would flip the recommendation; uncertainty is distributed" — never silently omitted.

## 6. No clinical deployment before calibration logging exists

The system cannot be deployed in any clinical workflow (including advisory mode) until predictions are being logged with full metadata for later calibration analysis. This includes:

- Case UUID
- Network version
- All sampled priors (or seed for reproducibility)
- All decision option scores with intervals
- Timestamp

Phase 0 is allowed to skip persistence to a database, but the logging structure must exist as JSON output.

## 7. No outcome claims without IRB-approved outcome linkage

The system does not make claims like "this decision will reduce 30-day readmission" or "this option produces better outcomes." Until an IRB-approved retrospective outcome linkage exists (Phase 4+), the system only reports defensibility distributions.

Phase 0 reports may state "outcome data not yet linked" where outcome information would otherwise appear.

## 8. No UI that hides uncertainty behind green/yellow/red badges alone

Future UI work (Phase 1+) may use color coding, but the credible interval and category probabilities must remain visible alongside any color summary. A clinician must always be able to see the distribution.

Phase 0 has no UI, so this constraint applies to future work.

## 9. No vendor ranking as the primary artifact

This project does not produce "Tool A beats Tool B" rankings as a primary deliverable. It evaluates AI clinical answers (Workflow A) and simulates decision spaces (Workflow B). Comparative outputs across vendors are derived artifacts, never the primary report.

## 10. No claim that Monte Carlo makes weak evidence strong

The system's outputs are no stronger than its inputs. If priors are weak (placeholder / LLM-unverified), the outputs inherit that weakness regardless of how many Monte Carlo iterations run. The report must reflect this honestly.

Wide credible intervals are a feature, not a bug. The system is honest about uncertainty, not confident in spite of it.

---

## Enforcement

These constraints are enforced by:

- **Code review** — every PR is checked against this list
- **Schema validation** — Pydantic models reject probabilities without provenance
- **Report tests** — automated tests verify each report contains required sections
- **Acceptance tests** — Phase 0 acceptance includes "report does not violate any constraint"

When in doubt, ask. Do not assume a workaround is acceptable.
