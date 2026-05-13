"""Input and domain-pack data contracts."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, PositiveFloat, model_validator

from .evidence_models import SupportedEntityType
from .model_base import JsonObject, NonEmptyString, StrictModel


class SourceRecommendation(StrictModel):
    source: NonEmptyString
    text: NonEmptyString


class ClinicalDecisionEpisode(StrictModel):
    cde_id: NonEmptyString
    domain: NonEmptyString
    decision_moment: NonEmptyString
    case_text: str | None = None
    patient_state: JsonObject = Field(default_factory=dict)
    candidate_options: list[NonEmptyString] = Field(min_length=1)
    source_recommendations: list[SourceRecommendation] = Field(default_factory=list)
    local_context: JsonObject = Field(default_factory=dict)
    outcome_tracking: JsonObject = Field(default_factory=dict)


class DecisionOption(StrictModel):
    id: NonEmptyString
    label: NonEmptyString


class SafetyGate(StrictModel):
    reason: NonEmptyString
    variable: NonEmptyString | None = None
    condition: NonEmptyString | None = None
    claim_type: NonEmptyString | None = None

    @model_validator(mode="after")
    def require_variable_or_claim_type(self) -> Self:
        if self.variable is None and self.claim_type is None:
            raise ValueError("safety gate requires either variable or claim_type")
        if self.variable is not None and self.condition is None:
            raise ValueError("variable safety gate requires condition")
        return self


SafetyGateMatchedStatus = Literal["blocked", "triggered"]


class SafetyGateTargetMapping(StrictModel):
    gate_group: NonEmptyString
    option_id: NonEmptyString
    matched_status: SafetyGateMatchedStatus


class PriorToOptionMapping(StrictModel):
    prior_id: NonEmptyString
    option_ids: list[NonEmptyString] = Field(min_length=1)

    @model_validator(mode="after")
    def require_unique_option_ids(self) -> Self:
        if len(set(self.option_ids)) != len(self.option_ids):
            raise ValueError("prior-to-option mappings cannot repeat option ids")
        return self


DomainPackEvidenceEntityType = Literal[
    "domain_pack",
    "decision_option",
    "prior",
    "safety_gate",
    "mapping",
    "voi_variable",
    "uncertainty_category",
    "mapped_claim_type",
]


class DomainPackEvidenceReference(StrictModel):
    supported_entity_type: DomainPackEvidenceEntityType
    supported_entity_id: NonEmptyString
    evidence_source_ids: list[NonEmptyString] = Field(min_length=1)

    @model_validator(mode="after")
    def require_unique_source_ids(self) -> Self:
        if len(set(self.evidence_source_ids)) != len(self.evidence_source_ids):
            raise ValueError("domain-pack evidence references cannot repeat source ids")
        return self


class DomainPackMappings(StrictModel):
    safety_gate_targets: list[SafetyGateTargetMapping] = Field(default_factory=list)
    prior_to_options: list[PriorToOptionMapping] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_unique_mapping_keys(self) -> Self:
        gate_groups = [mapping.gate_group for mapping in self.safety_gate_targets]
        if len(set(gate_groups)) != len(gate_groups):
            raise ValueError("safety gate target mappings must use unique gate_group values")

        prior_ids = [mapping.prior_id for mapping in self.prior_to_options]
        if len(set(prior_ids)) != len(prior_ids):
            raise ValueError("prior-to-option mappings must use unique prior_id values")
        return self

    def safety_gate_target_by_group(self) -> dict[str, SafetyGateTargetMapping]:
        return {mapping.gate_group: mapping for mapping in self.safety_gate_targets}

    def prior_ids_by_option(self) -> dict[str, list[str]]:
        by_option: dict[str, list[str]] = {}
        for mapping in self.prior_to_options:
            for option_id in mapping.option_ids:
                by_option.setdefault(option_id, []).append(mapping.prior_id)
        return by_option


class Prior(StrictModel):
    distribution: Literal["beta"]
    alpha: PositiveFloat
    beta: PositiveFloat
    provenance_class: NonEmptyString
    elicitation_method: NonEmptyString
    confidence_class: NonEmptyString
    calibration_status: NonEmptyString
    warning: str | None = None
    owner: str | None = None
    review_status: str | None = None
    source_basis: str | None = None
    last_reviewed: str | None = None

    @model_validator(mode="after")
    def require_warning_for_low_confidence(self) -> Self:
        confidence = self.confidence_class.lower()
        if confidence in {"low", "moderate", "low_unverified", "moderate_unverified"}:
            if not self.warning:
                raise ValueError("low or unverified confidence priors require a warning")
        return self


class DomainPack(StrictModel):
    domain_pack_id: NonEmptyString
    version: NonEmptyString
    status: NonEmptyString
    clinical_owner: NonEmptyString
    calibration_status: NonEmptyString
    decision_options: list[DecisionOption] = Field(min_length=1)
    hard_gates: dict[str, list[SafetyGate]] = Field(default_factory=dict)
    mappings: DomainPackMappings = Field(default_factory=DomainPackMappings)
    evidence_references: list[DomainPackEvidenceReference] = Field(default_factory=list)
    soft_nodes: list[NonEmptyString] = Field(default_factory=list)
    prior_policy: dict[str, Prior] = Field(default_factory=dict)
    value_of_information_variables: list[NonEmptyString] = Field(default_factory=list)
    reporting_rules: dict[str, bool] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_unique_decision_option_ids(self) -> Self:
        option_ids = [option.id for option in self.decision_options]
        if len(set(option_ids)) != len(option_ids):
            raise ValueError("decision option ids must be unique")
        return self

    @model_validator(mode="after")
    def validate_explicit_mappings(self) -> Self:
        option_ids = {option.id for option in self.decision_options}
        gate_groups = set(self.hard_gates)
        prior_ids = set(self.prior_policy)

        for mapping in self.mappings.safety_gate_targets:
            if mapping.gate_group not in gate_groups:
                raise ValueError(
                    f"safety gate mapping references unknown gate_group {mapping.gate_group!r}"
                )
            if mapping.option_id not in option_ids:
                raise ValueError(
                    f"safety gate mapping for {mapping.gate_group!r} references "
                    f"unknown option_id {mapping.option_id!r}"
                )

        for mapping in self.mappings.prior_to_options:
            if mapping.prior_id not in prior_ids:
                raise ValueError(
                    f"prior-to-option mapping references unknown prior_id {mapping.prior_id!r}"
                )
            unknown_option_ids = [
                option_id for option_id in mapping.option_ids if option_id not in option_ids
            ]
            if unknown_option_ids:
                raise ValueError(
                    f"prior-to-option mapping for {mapping.prior_id!r} references "
                    f"unknown option_id(s): {', '.join(unknown_option_ids)}"
                )
        return self

    @model_validator(mode="after")
    def validate_evidence_references(self) -> Self:
        known_ids = self._known_evidence_entity_ids()
        reference_keys: list[tuple[str, str, str]] = []

        for reference in self.evidence_references:
            allowed_ids = known_ids[reference.supported_entity_type]
            if reference.supported_entity_id not in allowed_ids:
                raise ValueError(
                    "evidence reference for "
                    f"{reference.supported_entity_type!r} references unknown "
                    f"supported_entity_id {reference.supported_entity_id!r}"
                )
            for evidence_source_id in reference.evidence_source_ids:
                reference_keys.append(
                    (
                        reference.supported_entity_type,
                        reference.supported_entity_id,
                        evidence_source_id,
                    )
                )

        if len(set(reference_keys)) != len(reference_keys):
            raise ValueError(
                "domain-pack evidence references must be unique per entity and source id"
            )
        return self

    def _known_evidence_entity_ids(self) -> dict[SupportedEntityType, set[str]]:
        claim_types = {
            gate.claim_type
            for gate_group in self.hard_gates.values()
            for gate in gate_group
            if gate.claim_type is not None
        }
        mapping_ids = {
            f"safety_gate_targets.{mapping.gate_group}"
            for mapping in self.mappings.safety_gate_targets
        } | {
            f"prior_to_options.{mapping.prior_id}"
            for mapping in self.mappings.prior_to_options
        }
        return {
            "domain_pack": {self.domain_pack_id},
            "decision_option": {option.id for option in self.decision_options},
            "prior": set(self.prior_policy),
            "safety_gate": set(self.hard_gates),
            "mapping": mapping_ids,
            "voi_variable": set(self.value_of_information_variables),
            "uncertainty_category": set(self.soft_nodes),
            "mapped_claim_type": {claim_type for claim_type in claim_types if claim_type},
            "local_overlay": set(),
            "report_statement": set(),
            "other": set(),
        }
