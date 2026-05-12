"""Top-level pipeline result data contracts."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from .component_models import (
    DecisionProfileEvaluationSet,
    LocalOverlayVerificationSet,
    MonteCarloSimulationResult,
    PriorResolutionSet,
    SafetyGateEvaluationSet,
    UncertaintyBudgetEvaluationSet,
    ValueOfInformationEvaluationSet,
)
from .input_models import ClinicalDecisionEpisode, DomainPack
from .model_base import NonEmptyString, StrictModel


class EvaluationPipelineResult(StrictModel):
    workflow_mode: Literal["direct_cde_simulation"] = "direct_cde_simulation"
    cde_source: NonEmptyString | None = None
    domain_pack_source: NonEmptyString | None = None
    n_iterations: int = Field(ge=1)
    random_seed: int | None = None
    cde: ClinicalDecisionEpisode
    domain_pack: DomainPack
    safety_gates: SafetyGateEvaluationSet
    prior_resolutions: PriorResolutionSet
    simulation: MonteCarloSimulationResult
    value_of_information: ValueOfInformationEvaluationSet
    uncertainty_budget: UncertaintyBudgetEvaluationSet
    local_overlay: LocalOverlayVerificationSet
    decision_profiles: DecisionProfileEvaluationSet

    @model_validator(mode="after")
    def require_matching_component_ids(self) -> Self:
        cde_id = self.cde.cde_id
        domain_pack_id = self.domain_pack.domain_pack_id
        component_pairs = [
            (self.safety_gates.cde_id, self.safety_gates.domain_pack_id, "safety_gates"),
            (self.prior_resolutions.cde_id, self.prior_resolutions.domain_pack_id, "prior_resolutions"),
            (self.simulation.cde_id, self.simulation.domain_pack_id, "simulation"),
            (self.value_of_information.cde_id, self.value_of_information.domain_pack_id, "value_of_information"),
            (self.uncertainty_budget.cde_id, self.uncertainty_budget.domain_pack_id, "uncertainty_budget"),
            (self.local_overlay.cde_id, self.local_overlay.domain_pack_id, "local_overlay"),
            (self.decision_profiles.cde_id, self.decision_profiles.domain_pack_id, "decision_profiles"),
        ]
        for component_cde_id, component_domain_pack_id, name in component_pairs:
            if component_cde_id is not None and component_cde_id != cde_id:
                raise ValueError(f"{name} cde_id does not match cde.cde_id")
            if component_domain_pack_id != domain_pack_id:
                raise ValueError(f"{name} domain_pack_id does not match domain_pack.domain_pack_id")
        if self.simulation.n_iterations != self.n_iterations:
            raise ValueError("simulation n_iterations does not match pipeline n_iterations")
        if self.simulation.random_seed != self.random_seed:
            raise ValueError("simulation random_seed does not match pipeline random_seed")
        return self
