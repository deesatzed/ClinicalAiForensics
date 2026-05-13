# Evidence Registry Decision

## Status

Accepted for Phase 2 architecture planning.

This document defines the evidence registry shape needed before implementing persistence or domain-pack evidence linking. It is documentation-only and does not add runtime behavior.

## Core Decision

Evidence objects are immutable receipts.

Relationships, trust assessments, utility labels, safety judgments, confidence scores, and review states are mutable or versioned records layered on top of those receipts.

Working model:

- `EvidenceObject` = stable receipt.
- `EvidenceLink` = relationship between evidence and task/component/context.
- `EvidenceAssessment` = contextual trust, utility, relevance, safety, or support judgment.
- `EvidenceLineage` = derivation chain showing whether a record is observed, inferred, synthesized, or speculative.

## Rationale

Evidence identity and evidence judgment need different lifecycles.

An evidence receipt should answer: what was observed, where did it come from, when was it recorded, and what stable identifiers or safe metadata identify it?

An assessment should answer: how is this evidence being used in this domain, for this prior, gate, mapped claim, local overlay item, report statement, or future calibration protocol?

Keeping receipts immutable prevents later review decisions from changing what was originally seen. Keeping links and assessments versioned allows governance to evolve without rewriting evidence identity.

## Boundaries

This decision allows:

- stable evidence receipt IDs
- versioned source-to-entity links
- versioned review/support/trust/utility/safety assessments
- lineage records that preserve derivation type
- separate storage decisions for receipts, links, assessments, and lineage

This decision does not allow:

- automated evidence truth validation
- source-quality scoring
- citation scoring
- web or DOI/PMID lookups
- retraction checks
- abstract-to-claim alignment
- LLM evidence judgment
- clinical recommendations
- calibrated risk or outcome claims
- PHI storage
- copied source passages in source-controlled metadata

## Evidence Object

An `EvidenceObject` should be an immutable receipt for a source or observation. It should contain stable identifiers and safe metadata, not mutable judgments.

Candidate fields:

- `evidence_object_id`
- `object_type`
- `title_or_label`
- `source_type`
- `bibliographic_ids`
- `canonical_url`
- `publisher_or_organization`
- `publication_date`
- `version`
- `retrieved_at`
- `receipt_created_at`
- `receipt_created_by`
- `content_hash` or metadata hash when available and safe
- `storage_pointer` to governed storage, if raw content is stored outside source control
- `phi_status`
- `copyright_status`

Immutable means the receipt should not be edited in place after creation. Corrections should create a new receipt or a superseding receipt relationship.

## Evidence Link

An `EvidenceLink` connects an evidence object to a project entity in a specific context.

Candidate target entity types:

- `prior`
- `safety_gate`
- `mapping`
- `voi_variable`
- `uncertainty_category`
- `local_overlay`
- `mapped_claim_type`
- `report_statement`
- `domain_pack`
- `decision_option`
- `calibration_label_family`
- `outcome_anchor`

Links are mutable or versioned because a source may later be linked to additional entities, removed from an entity, superseded, or scoped more narrowly.

## Evidence Assessment

An `EvidenceAssessment` is a contextual judgment about a link or object. It should never be mistaken for source truth.

Candidate assessment dimensions:

- `review_status`
- `support_status`
- `trust_status`
- `utility_label`
- `safety_relevance`
- `confidence_label`
- `conflict_status`
- `freshness_status`
- `scope_match_status`
- `limitations`
- `reviewer_or_group`
- `reviewed_at`
- `review_protocol_reference`

Assessments are versioned because review decisions can change when sources are updated, governance changes, or conflicts are found.

## Evidence Lineage

An `EvidenceLineage` record captures how an evidence object, link, or assessment came to exist.

Allowed derivation classes:

- `observed`
- `inferred`
- `synthesized`
- `speculative`

Lineage must stay visible when evidence is displayed or logged in later phases. Synthesized and speculative records must never be silently promoted to observed evidence.

## Storage Decision

Persistence is intentionally deferred.

The Phase 2 architecture should support separate storage policies for:

- immutable evidence receipts
- mutable/versioned evidence links
- mutable/versioned assessments
- lineage records

`P2-002A` does not choose a concrete persistence implementation. `P2-002B` should decide whether the first implementation uses separate registry files, domain-pack embedded references, generated review artifacts, or another governed store.

## Open Questions

- Should `EvidenceObject` receipts live in a separate registry file, inside domain packs, or in release artifacts?
- Which identifiers are mandatory for each source type?
- Should source snippets ever be stored, or only governed storage pointers?
- How should corrections to an evidence receipt be represented?
- What review statuses and support statuses are allowed by governance?
- Who can create or approve assessments?
- What fields can appear in status-only JSONL logs without leaking sensitive review data?
- What storage model is acceptable if future work involves real-world sources or PHI-adjacent metadata?
