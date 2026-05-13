# Evidence Lineage Rules

## Purpose

Evidence lineage records how an evidence object, link, or assessment was derived.

Lineage is required because future evidence records may come from direct observation, manual inference, synthesis across sources, or speculative planning placeholders. Those categories must not collapse into one visible status.

This document is documentation-only and does not implement lineage storage.

## Derivation Classes

### Observed

Observed evidence is directly recorded from a source or governed artifact.

Examples:

- a guideline version and bibliographic identifier
- a trial registry ID
- a local policy document receipt
- a manually captured source metadata receipt

Observed does not mean clinically true. It only means the evidence object was directly observed as a source artifact.

### Inferred

Inferred evidence is derived from an observed object using a documented rule or reviewer interpretation.

Examples:

- source applies to an HF ED discharge prior after reviewer scope review
- source is stale because publication date exceeds a governance cadence
- source supports a mapped claim type under a documented support rubric

Inference must name the rule, reviewer group, or protocol reference.

### Synthesized

Synthesized evidence combines multiple observed or inferred records.

Examples:

- evidence summary assembled from several guidelines
- consensus support status across multiple sources
- aggregate review status for a domain-pack prior

Synthesized evidence must list input lineage references.

### Speculative

Speculative evidence is a placeholder, hypothesis, or planning note that has not been reviewed.

Examples:

- candidate source to find later
- proposed evidence relationship without source ownership
- draft support claim created for planning

Speculative evidence must remain visibly speculative and must not activate clinical logic.

## Lineage Record Requirements

Candidate fields:

- `lineage_id`
- `target_type`
- `target_id`
- `derivation_class`
- `input_ids`
- `method_or_protocol`
- `created_by`
- `created_at`
- `review_status`
- `limitations`

Lineage records should be append-only or versioned.

## Promotion Rules

Speculative can become inferred only through explicit review.

Inferred can become synthesized only when inputs and synthesis method are recorded.

Synthesized cannot become observed. If a direct source is later observed, create a separate observed evidence object and link it through lineage.

Observed can be superseded, corrected, or retracted, but it should not be edited in place.

## Visibility Rules

Reports and logs in later phases should preserve lineage class using status-safe fields.

Minimum visibility:

- observed
- inferred
- synthesized
- speculative
- unknown

Speculative, inferred, and synthesized items must not be displayed as if they were observed source receipts.

## Relationship To Assessments

Assessments may depend on lineage but should not replace lineage.

For example, a support assessment may say `supported`, while lineage says the support was `inferred` from a reviewed source under a specific protocol.

Both facts matter:

- support status says what the reviewer decided
- lineage says how that decision was derived

## Relationship To Provenance Logs

JSONL provenance logs should prefer lineage IDs, derivation class, status, and counts.

They should not log:

- source passages
- raw clinical text
- raw patient-state values
- raw AI answer text
- sensitive reviewer notes
- local operational owner/source/review raw values

## Relationship To AI Answer Mapping

Current AI answer mapping is API-only and deterministic. If later mapped-claim evidence is linked to AI-answer-derived artifacts, lineage must distinguish:

- source-backed claim pattern
- mapped claim record
- answer-derived observation
- inferred omission or overstatement
- synthesized answer audit summary

Raw AI answer text should remain out of ordinary pipeline results, reports, and logs unless a later governed mode explicitly changes that boundary.

## Open Questions

- Which lineage classes should block report display versus display as deferred?
- Should lineage IDs be required on every support link in P2-002B?
- Should lineage be stored in the same registry as evidence objects or in append-only logs?
- What reviewer protocol is required to promote speculative records?
- How should retracted or superseded sources affect downstream links and assessments?
