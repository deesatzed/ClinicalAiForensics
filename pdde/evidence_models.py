"""Evidence-source registry contracts.

These models are governance metadata only. They do not validate source truth,
score citations, fetch external metadata, or activate clinical logic.
"""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from .model_base import JsonObject, NonEmptyString, StrictModel


EvidenceSourceType = Literal[
    "guideline",
    "trial",
    "review",
    "local_policy",
    "expert_panel",
    "registry",
    "model_generated_draft",
    "other",
]

EvidenceReviewStatus = Literal[
    "draft",
    "pending_review",
    "reviewed",
    "superseded",
    "retracted",
    "conflicting",
    "out_of_scope",
    "deferred",
    "unknown",
]

SupportedEntityType = Literal[
    "prior",
    "safety_gate",
    "mapping",
    "voi_variable",
    "uncertainty_category",
    "local_overlay",
    "mapped_claim_type",
    "report_statement",
    "domain_pack",
    "decision_option",
    "other",
]

EvidenceSupportStatus = Literal[
    "pending_review",
    "supported",
    "partial_support",
    "conflicting",
    "unsupported",
    "out_of_scope",
    "deferred",
    "unknown",
]

FINAL_SOURCE_REVIEW_STATUSES = {"reviewed", "superseded", "retracted", "conflicting"}
FINAL_SUPPORT_STATUSES = {"supported", "partial_support", "conflicting", "unsupported", "out_of_scope"}


class BibliographicIdentifier(StrictModel):
    id_type: NonEmptyString
    value: NonEmptyString


class EvidenceSource(StrictModel):
    evidence_source_id: NonEmptyString
    source_type: EvidenceSourceType
    title_or_label: NonEmptyString
    review_status: EvidenceReviewStatus = "pending_review"
    bibliographic_ids: list[BibliographicIdentifier] = Field(default_factory=list)
    canonical_url: str | None = None
    publisher_or_organization: str | None = None
    publication_date: str | None = None
    version: str | None = None
    retrieved_at: str | None = None
    evidence_owner: str | None = None
    last_reviewed: str | None = None
    review_cadence: str | None = None

    @model_validator(mode="after")
    def require_review_metadata_for_final_status(self) -> Self:
        if self.review_status in FINAL_SOURCE_REVIEW_STATUSES:
            missing = [
                field_name
                for field_name in ("evidence_owner", "last_reviewed")
                if not getattr(self, field_name)
            ]
            if missing:
                raise ValueError(
                    "reviewed evidence sources require evidence_owner and last_reviewed"
                )
        return self


class EvidenceSupportLink(StrictModel):
    evidence_source_id: NonEmptyString
    supported_entity_type: SupportedEntityType
    supported_entity_id: NonEmptyString
    support_status: EvidenceSupportStatus = "pending_review"
    support_scope: JsonObject = Field(default_factory=dict)
    limitations: list[NonEmptyString] = Field(default_factory=list)
    audit_decision_by: str | None = None
    audit_decision_at: str | None = None
    audit_notes_reference: str | None = None

    @model_validator(mode="after")
    def require_audit_metadata_for_final_support_status(self) -> Self:
        if self.support_status in FINAL_SUPPORT_STATUSES:
            missing = [
                field_name
                for field_name in ("audit_decision_by", "audit_decision_at")
                if not getattr(self, field_name)
            ]
            if missing:
                raise ValueError(
                    "reviewed evidence support links require audit_decision_by "
                    "and audit_decision_at"
                )
        return self


class EvidenceRegistry(StrictModel):
    sources: list[EvidenceSource] = Field(default_factory=list)
    support_links: list[EvidenceSupportLink] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_registry_references(self) -> Self:
        source_ids = [source.evidence_source_id for source in self.sources]
        if len(set(source_ids)) != len(source_ids):
            raise ValueError("evidence source ids must be unique")

        source_id_set = set(source_ids)
        link_keys: list[tuple[str, str, str]] = []
        for link in self.support_links:
            if link.evidence_source_id not in source_id_set:
                raise ValueError(
                    "evidence support link references unknown evidence_source_id "
                    f"{link.evidence_source_id!r}"
                )
            link_keys.append(
                (
                    link.evidence_source_id,
                    link.supported_entity_type,
                    link.supported_entity_id,
                )
            )

        if len(set(link_keys)) != len(link_keys):
            raise ValueError("evidence support links must be unique per source and entity")
        return self
