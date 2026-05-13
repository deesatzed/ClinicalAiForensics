# AI Answer Mapping Governance Intake

## Purpose

This file collects the governed inputs needed before `P2-005: Broader AI Answer Mapping Specification` can start. It is for deterministic mapping-specification metadata only: example AI-answer artifacts, allowed claim patterns, omission boundaries, overstatement boundaries, unsupported-claim boundaries, reviewer ownership, and approval status.

The goal is to make future AI-answer mapping boundaries explicit before any implementation expands beyond the current deterministic claim-pattern interface.

## Non-Activation Rule

Completing this template does not activate AI answer grading, LLM judgment, clinical recommendations, final recommendations, option rankings, scoring, or free-text AI-answer processing.

This intake only records governance metadata. P2-005 implementation remains blocked until the mapping examples and boundaries are reviewed, explicitly approved, and converted into a separate implementation task.

## Required Inputs

| Field | Required? | Description | Example | Provided Value |
|---|---|---|---|---|
| governed example AI-answer artifact ID | Yes | Stable non-PHI identifier for the example AI-answer artifact. | `hf_ed_ai_answer_demo_001` |  |
| synthetic/non-PHI status | Yes | Whether the artifact is synthetic and contains no PHI/PII. | synthetic/non-PHI |  |
| source of example artifact | Yes | Non-PHI source reference for the example artifact. | `synthetic_fixture:ai_answer_hf_ed_demo_001` |  |
| intended domain | Yes | Domain where the mapping applies. | HF ED discharge |  |
| mapped claim type | Yes | Explicit claim-type ID to map when the pattern is present. | `sotalol_as_hf_beta_blocker` |  |
| explicit claim text or claim pattern | Yes | Exact claim text or deterministic pattern to map. | "sotalol is a guideline beta blocker for HFrEF" |  |
| allowed mapping boundary | Yes | What the mapper is allowed to mark when this pattern appears. | Mark claim type only; do not grade answer correctness. |  |
| omission boundary | Yes | Explicit omission pattern or statement of no omission mapping. | Omission mapping not approved for this entry. |  |
| overstatement boundary | Yes | Explicit overstatement pattern or statement of no overstatement mapping. | Overstatement mapping not approved for this entry. |  |
| unsupported claim boundary | Yes | Claims that must remain unsupported rather than inferred. | Any beta-blocker claim not matching the approved pattern. |  |
| reviewer or approving body | Yes | Person, role, committee, or review body approving the mapping boundary. | Example governance reviewer |  |
| verification status | Yes | Current governance status using the allowed values below. | `draft` |  |
| accountable owner | Yes | Owner accountable for the mapping specification. | Example governance owner |  |
| last-reviewed date | Yes | Date the mapping specification was last reviewed. | 2026-05-13 |  |
| review cadence | Yes | Expected review frequency. | quarterly |  |
| activation status | Yes | Whether the mapping is documentation-only, approved for implementation, or inactive. | documentation-only |  |
| explicit confirmation this does not perform answer grading | Yes | Affirm that the mapping spec does not grade the answer. | Confirmed: no answer grading. |  |
| explicit confirmation this does not perform LLM judgment | Yes | Affirm that the mapping spec does not use or authorize LLM judgment. | Confirmed: no LLM judgment. |  |
| explicit confirmation this does not create final clinical recommendations | Yes | Affirm that the mapping spec does not create recommendations. | Confirmed: no final clinical recommendations. |  |

## Allowed Verification Statuses

- `draft`: Mapping metadata is incomplete or not yet reviewed.
- `pending_review`: Mapping metadata has been submitted for review but is not approved.
- `approved_mapping_spec`: Mapping metadata has been reviewed and approved as a deterministic mapping specification, but implementation still requires a separate task.
- `rejected`: Mapping metadata was reviewed and rejected.
- `superseded`: Mapping metadata has been replaced by a newer governance record.

## Example Draft Entry

This example is synthetic and non-PHI. It is metadata/specification-only and does not approve implementation.

| Field | Required? | Description | Example | Provided Value |
|---|---|---|---|---|
| governed example AI-answer artifact ID | Yes | Stable non-PHI identifier for the example AI-answer artifact. | `hf_ed_ai_answer_demo_001` | `hf_ed_ai_answer_mapping_draft_001` |
| synthetic/non-PHI status | Yes | Whether the artifact is synthetic and contains no PHI/PII. | synthetic/non-PHI | synthetic/non-PHI |
| source of example artifact | Yes | Non-PHI source reference for the example artifact. | `synthetic_fixture:ai_answer_hf_ed_demo_001` | `synthetic_governance_example:hf_ed_ai_answer_mapping_draft_001` |
| intended domain | Yes | Domain where the mapping applies. | HF ED discharge | HF ED discharge |
| mapped claim type | Yes | Explicit claim-type ID to map when the pattern is present. | `sotalol_as_hf_beta_blocker` | `sotalol_as_hf_beta_blocker` |
| explicit claim text or claim pattern | Yes | Exact claim text or deterministic pattern to map. | "sotalol is a guideline beta blocker for HFrEF" | "sotalol is a guideline beta blocker for HFrEF" |
| allowed mapping boundary | Yes | What the mapper is allowed to mark when this pattern appears. | Mark claim type only; do not grade answer correctness. | Deterministically map only this exact claim pattern to the claim type. |
| omission boundary | Yes | Explicit omission pattern or statement of no omission mapping. | Omission mapping not approved for this entry. | Omission mapping not approved in this draft entry. |
| overstatement boundary | Yes | Explicit overstatement pattern or statement of no overstatement mapping. | Overstatement mapping not approved for this entry. | Overstatement mapping not approved in this draft entry. |
| unsupported claim boundary | Yes | Claims that must remain unsupported rather than inferred. | Any beta-blocker claim not matching the approved pattern. | Do not infer mapping from general beta-blocker wording, synonyms, or clinical similarity. |
| reviewer or approving body | Yes | Person, role, committee, or review body approving the mapping boundary. | Example governance reviewer | Not yet reviewed |
| verification status | Yes | Current governance status using the allowed values below. | `draft` | `draft` |
| accountable owner | Yes | Owner accountable for the mapping specification. | Example governance owner | Example governance owner (draft) |
| last-reviewed date | Yes | Date the mapping specification was last reviewed. | 2026-05-13 | Not yet reviewed |
| review cadence | Yes | Expected review frequency. | quarterly | TBD |
| activation status | Yes | Whether the mapping is documentation-only, approved for implementation, or inactive. | documentation-only | documentation-only |
| explicit confirmation this does not perform answer grading | Yes | Affirm that the mapping spec does not grade the answer. | Confirmed: no answer grading. | Confirmed: this does not perform answer grading. |
| explicit confirmation this does not perform LLM judgment | Yes | Affirm that the mapping spec does not use or authorize LLM judgment. | Confirmed: no LLM judgment. | Confirmed: this does not perform LLM judgment. |
| explicit confirmation this does not create final clinical recommendations | Yes | Affirm that the mapping spec does not create recommendations. | Confirmed: no final clinical recommendations. | Confirmed: this does not create final clinical recommendations. |

## Questions Blocking P2-005

- What governed AI-answer examples may be used?
- What omissions should be mapped?
- What overstatements should be mapped?
- What claim types are allowed?
- Who approves the mapping boundaries?
- Is scope limited to deterministic claim-pattern mapping only?
