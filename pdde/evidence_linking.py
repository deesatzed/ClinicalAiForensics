"""Domain-pack evidence reference validation.

This module validates explicit evidence IDs only. It does not fetch sources,
score citations, validate clinical truth, or activate report/provenance output.
"""

from __future__ import annotations

from .evidence_models import (
    DomainPackEvidenceLinkValidation,
    DomainPackEvidenceLinkValidationSet,
    EvidenceRegistry,
    EvidenceSupportLink,
)
from .input_models import DomainPack, DomainPackEvidenceReference


def validate_domain_pack_evidence_links(
    domain_pack: DomainPack,
    evidence_registry: EvidenceRegistry | None = None,
) -> DomainPackEvidenceLinkValidationSet:
    """Validate explicit domain-pack evidence references against a registry.

    Without a registry, explicit source IDs are preserved as pending review.
    With a registry, source IDs must exist. A matching support link is reported
    when present, but no support status is converted into a truth claim.
    """

    if not domain_pack.evidence_references:
        return DomainPackEvidenceLinkValidationSet(
            domain_pack_id=domain_pack.domain_pack_id,
            items=[
                DomainPackEvidenceLinkValidation(
                    supported_entity_type="domain_pack",
                    supported_entity_id=domain_pack.domain_pack_id,
                    status="deferred",
                    reason=(
                        "domain pack has no explicit evidence references; no source "
                        "support is implied"
                    ),
                    source=f"domain_pack:{domain_pack.domain_pack_id}.evidence_references",
                    provenance_references=[
                        f"domain_pack:{domain_pack.domain_pack_id}.evidence_references"
                    ],
                )
            ],
        )

    source_ids = (
        {source.evidence_source_id for source in evidence_registry.sources}
        if evidence_registry is not None
        else set()
    )
    support_links = (
        _support_links_by_key(evidence_registry.support_links)
        if evidence_registry is not None
        else {}
    )

    items: list[DomainPackEvidenceLinkValidation] = []
    for reference in domain_pack.evidence_references:
        for evidence_source_id in reference.evidence_source_ids:
            items.append(
                _validate_reference_source(
                    domain_pack_id=domain_pack.domain_pack_id,
                    reference=reference,
                    evidence_source_id=evidence_source_id,
                    registry_supplied=evidence_registry is not None,
                    source_ids=source_ids,
                    support_links=support_links,
                )
            )

    return DomainPackEvidenceLinkValidationSet(
        domain_pack_id=domain_pack.domain_pack_id,
        items=items,
    )


def _validate_reference_source(
    *,
    domain_pack_id: str,
    reference: DomainPackEvidenceReference,
    evidence_source_id: str,
    registry_supplied: bool,
    source_ids: set[str],
    support_links: dict[tuple[str, str, str], EvidenceSupportLink],
) -> DomainPackEvidenceLinkValidation:
    source = _reference_source(domain_pack_id, reference)
    provenance_references = [source, f"evidence_source:{evidence_source_id}"]

    if not registry_supplied:
        return DomainPackEvidenceLinkValidation(
            supported_entity_type=reference.supported_entity_type,
            supported_entity_id=reference.supported_entity_id,
            evidence_source_id=evidence_source_id,
            status="pending_review",
            reason=(
                "domain-pack evidence source id is present, but no evidence registry "
                "was supplied for validation"
            ),
            source=source,
            provenance_references=provenance_references,
        )

    if evidence_source_id not in source_ids:
        return DomainPackEvidenceLinkValidation(
            supported_entity_type=reference.supported_entity_type,
            supported_entity_id=reference.supported_entity_id,
            evidence_source_id=evidence_source_id,
            status="unknown_source",
            reason=(
                f"domain-pack evidence reference uses unknown evidence_source_id "
                f"{evidence_source_id!r}"
            ),
            source=source,
            provenance_references=provenance_references,
        )

    support_link = support_links.get(
        (
            evidence_source_id,
            reference.supported_entity_type,
            reference.supported_entity_id,
        )
    )
    if support_link is None:
        return DomainPackEvidenceLinkValidation(
            supported_entity_type=reference.supported_entity_type,
            supported_entity_id=reference.supported_entity_id,
            evidence_source_id=evidence_source_id,
            status="pending_review",
            reason=(
                "evidence source exists in registry, but no explicit registry support "
                "link exists for this domain-pack entity"
            ),
            source=source,
            provenance_references=provenance_references,
        )

    return DomainPackEvidenceLinkValidation(
        supported_entity_type=reference.supported_entity_type,
        supported_entity_id=reference.supported_entity_id,
        evidence_source_id=evidence_source_id,
        status="linked",
        support_status=support_link.support_status,
        reason=(
            "evidence source and explicit registry support link are present; support "
            f"status is {support_link.support_status!r} and no truth validation was performed"
        ),
        source=source,
        provenance_references=provenance_references,
    )


def _support_links_by_key(
    support_links: list[EvidenceSupportLink],
) -> dict[tuple[str, str, str], EvidenceSupportLink]:
    return {
        (
            link.evidence_source_id,
            link.supported_entity_type,
            link.supported_entity_id,
        ): link
        for link in support_links
    }


def _reference_source(domain_pack_id: str, reference: DomainPackEvidenceReference) -> str:
    return (
        f"domain_pack:{domain_pack_id}.evidence_references."
        f"{reference.supported_entity_type}.{reference.supported_entity_id}"
    )
