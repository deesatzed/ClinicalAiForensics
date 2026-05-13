# Evidence Identity Model

## Purpose

This document defines identity and immutability rules for future evidence registry work.

It does not implement persistence, domain-pack linking, report rendering, provenance logging, evidence truth validation, or clinical logic.

## Identity Classes

### EvidenceObject

`EvidenceObject` is the stable receipt identity.

It identifies a source, source snapshot, local policy artifact, expert panel artifact, registry artifact, model-generated draft, or other evidence-like object.

Receipt identity should be stable enough that later reviewers can distinguish:

- source A from source B
- version A from version B
- observed source metadata from later assessment
- original receipt from correction or supersession

### EvidenceLink

`EvidenceLink` is the relationship identity.

It connects one evidence object to one project entity in one context. The same source can have multiple links because it may support a prior in one context, be out of scope for a gate in another context, and be conflicting for a mapped claim in a third context.

### EvidenceAssessment

`EvidenceAssessment` is the judgment identity.

It captures a contextual review decision about an object or link. It may change over time and must therefore be versioned or append-only.

### EvidenceLineage

`EvidenceLineage` is the derivation identity.

It records how an object, link, or assessment was produced and whether it is observed, inferred, synthesized, or speculative.

## Immutable Receipt Fields

Candidate immutable `EvidenceObject` fields:

- `evidence_object_id`
- `object_type`
- `source_type`
- `title_or_label`
- `bibliographic_ids`
- `canonical_url`
- `publisher_or_organization`
- `publication_date`
- `version`
- `retrieved_at`
- `receipt_created_at`
- `receipt_created_by`
- `source_locator`
- `content_hash`
- `metadata_hash`
- `phi_status`
- `copyright_status`

If an immutable field is wrong, do not edit it in place. Create a correction receipt or superseding receipt and link it through lineage.

## Mutable Or Versioned Fields

These fields should not define evidence object identity:

- review status
- support status
- trust status
- utility label
- confidence score or confidence label
- safety relevance
- source quality judgment
- freshness judgment
- conflict judgment
- reviewer notes
- domain applicability
- clinical applicability
- supported entity IDs

They belong on `EvidenceLink`, `EvidenceAssessment`, or `EvidenceLineage`.

## ID Rules

Evidence IDs should be:

- stable within the project
- opaque enough to avoid clinical claims
- safe to log
- independent of mutable review status
- independent of source support judgments

Recommended ID prefixes:

- `evobj_` for evidence objects
- `evlink_` for evidence links
- `evassess_` for evidence assessments
- `evlineage_` for lineage records

IDs should not encode PHI, raw source text, patient-state values, reviewer names, or clinical recommendations.

## Hashing Rules

Hashes are optional in Phase 2 until storage is selected.

When used:

- hash only governed canonical metadata or governed content snapshots
- record hash algorithm
- avoid hashing raw PHI inside source-controlled files
- do not treat a hash as source truth or clinical support

Hashes can prove receipt stability. They cannot prove clinical relevance.

## Versioning Rules

Evidence object corrections should create new receipt identities or explicit supersession lineage.

Evidence links and assessments should be versioned or append-only when:

- support status changes
- trust/utility/safety judgment changes
- supported entity changes
- review protocol changes
- source freshness changes
- source conflict or retraction status changes

## Privacy And Copyright Rules

Evidence identity records should prefer:

- IDs
- source types
- bibliographic IDs
- safe titles or labels
- dates
- versions
- organization names
- governed storage pointers

Evidence identity records should avoid:

- copied source passages
- raw clinical text
- raw patient-state values
- raw AI answer text
- PHI
- local operational owner/source/review raw values in ordinary logs
- copyrighted excerpts unless explicitly governed

## Open Questions

- Which fields are mandatory for guideline, trial, review, local policy, and expert panel sources?
- Should content hashes be mandatory for local policies?
- Should evidence objects be immutable by file append policy, object hash, git history, database immutability, or all of these?
- What correction workflow should be used if an evidence object contains incorrect metadata?
- Should reviewer identity be stored directly, as a team role, or as a governed external reference?
