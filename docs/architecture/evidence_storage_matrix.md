# Evidence Storage Matrix

## Purpose

This document compares storage options for future evidence registry persistence and linking.

It does not choose or implement persistence. It exists so P2-002B can make a narrower implementation decision.

## Storage Dimensions

Evidence registry storage needs to handle four different lifecycles:

- immutable `EvidenceObject` receipts
- mutable/versioned `EvidenceLink` relationships
- mutable/versioned `EvidenceAssessment` judgments
- append-only or versioned `EvidenceLineage` derivation chains

These lifecycles do not need to share the same storage backend.

## Matrix

| Storage Option | EvidenceObject Receipts | EvidenceLink Relationships | EvidenceAssessment Judgments | EvidenceLineage Chains | Strengths | Risks | Phase 2 Fit |
|---|---|---|---|---|---|---|---|
| Domain-pack inline fields | Weak | Medium | Weak | Weak | Keeps source references close to gates, priors, VOI items, and mappings. | Can make domain packs large and mutable; may blur receipt versus judgment. | Useful for references only, not primary receipt store. |
| Separate YAML/JSON registry files | Medium | Medium | Medium | Medium | Simple, reviewable, git-friendly, testable without services. | Immutability is social/git-based; concurrent edits can be clumsy. | Best first implementation candidate. |
| Generated release artifact | Medium | Weak | Weak | Medium | Good for sharing frozen review packages. | Poor for active editing and versioned assessments. | Good archive output, not source of truth. |
| Append-only JSONL | Medium | Medium | Medium | Strong | Natural for event history and lineage. | Harder to manually review current state; compaction needed. | Good audit trail companion. |
| SQLite | Medium | Strong | Strong | Strong | Local, queryable, supports versioned records. | Adds migration and artifact-management questions. | Possible after file registry proves schema. |
| Postgres or managed database | Strong | Strong | Strong | Strong | Multi-user governance and audit workflows. | Out of scope for current local CLI; deployment/security burden. | Not appropriate until governance/deployment exists. |
| Object store plus metadata registry | Strong | Medium | Medium | Medium | Can keep large or governed raw artifacts outside git. | Requires access control and storage policy. | Later only if raw artifacts are governed. |
| Source-control-only Markdown docs | Weak | Weak | Weak | Weak | Easy for narrative decisions. | Not structured enough for validation. | Good architecture docs, not registry persistence. |

## Recommended P2-002B Direction

The most conservative next implementation is a separate YAML or JSON evidence registry file plus optional domain-pack references to registry IDs.

Reason:

- it keeps receipts separate from domain logic
- it is easy to validate with typed models
- it avoids databases and deployment
- it keeps generated reports/logs reproducible and ignored
- it can preserve strict no-PHI/no-raw-passage boundaries

This is not yet accepted as an implementation decision. P2-002B should decide it explicitly before code changes.

## Storage Rules By Artifact Type

### EvidenceObject

Should be immutable or superseded.

Best early storage:

- separate registry file
- optional hash fields
- optional external storage pointer

Avoid:

- inline mutable domain-pack fields as the only identity
- raw source passages in git
- PHI

### EvidenceLink

Should be versioned or replaceable with clear review history.

Best early storage:

- separate registry file
- explicit target entity type and ID
- optional domain-pack references to link IDs or source IDs

Avoid:

- hidden Python routing
- token overlap
- inferred clinical meaning from labels

### EvidenceAssessment

Should be versioned or append-only.

Best early storage:

- separate registry file for draft work
- JSONL audit trail when assessment changes need event history

Avoid:

- treating assessment as source truth
- storing reviewer free text in ordinary logs
- numeric scoring without governance

### EvidenceLineage

Should be append-only or versioned.

Best early storage:

- registry file for current lineage state
- JSONL companion for lineage events if needed

Avoid:

- overwriting speculative records as observed
- hiding synthesized or inferred provenance

## Generated Artifact Policy

Generated reports and logs remain ignored reproducible artifacts by default.

Evidence registry source files, if later added, may become source-of-truth files only after a separate decision. Generated evidence summaries should not be treated as source-of-truth registries unless explicitly archived and documented.

## Open Questions

- Should P2-002B use YAML or JSON for the first registry file?
- Should registry files live under `domain_packs/`, `evidence/`, or `examples/`?
- Should domain packs reference evidence source IDs, evidence link IDs, or both?
- Should registry validation be part of `validate` CLI immediately or remain API-only first?
- What fields are safe for generated provenance logs?
- Should assessment changes be represented by version fields, append-only event records, or both?
- What storage option is acceptable if future governed raw source artifacts exist?
