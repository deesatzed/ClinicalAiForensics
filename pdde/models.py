"""Compatibility re-export surface for PDDE Pydantic data contracts.

Model definitions now live in focused modules:

- ``model_base`` for shared base types.
- ``input_models`` for CDE and domain-pack inputs.
- ``component_models`` for deterministic component outputs and status ledgers.
- ``evidence_models`` for evidence-source registry contracts.
- ``pipeline_models`` for top-level evaluation results.
- ``legacy_models`` for legacy/planned report and log contracts.

Importing from ``pdde.models`` remains supported for backwards compatibility.
"""

from __future__ import annotations

from .component_models import (
    AIAnswerClaimStatus,
    AIAnswerMappedClaim,
    AIAnswerMappingResult,
    DecisionProfileEvaluation,
    DecisionProfileEvaluationSet,
    DecisionProfileEvaluationStatus,
    DecisionProfileInputSummary,
    DecisionProfileInputType,
    LocalOverlayRequiredField,
    LocalOverlayVerificationItem,
    LocalOverlayVerificationSet,
    LocalOverlayVerificationStatus,
    MonteCarloPriorSimulation,
    MonteCarloPriorStatus,
    MonteCarloSimulationResult,
    PriorResolution,
    PriorResolutionSet,
    PriorResolutionStatus,
    SafetyGateEvaluation,
    SafetyGateEvaluationSet,
    SafetyGateStatus,
    StatusLedger,
    StatusLedgerComponent,
    StatusLedgerRow,
    UncertaintyBudgetEvaluationItem,
    UncertaintyBudgetEvaluationSet,
    UncertaintyCategory,
    UncertaintyItemStatus,
    ValueOfInformationEvaluation,
    ValueOfInformationEvaluationSet,
    ValueOfInformationStatus,
)
from .evidence_models import (
    BibliographicIdentifier,
    EvidenceRegistry,
    EvidenceReviewStatus,
    EvidenceSource,
    EvidenceSourceType,
    EvidenceSupportLink,
    EvidenceSupportStatus,
    SupportedEntityType,
)
from .input_models import (
    ClinicalDecisionEpisode,
    DecisionOption,
    DomainPack,
    DomainPackMappings,
    Prior,
    PriorToOptionMapping,
    SafetyGate,
    SafetyGateMatchedStatus,
    SafetyGateTargetMapping,
    SourceRecommendation,
)
from .legacy_models import (
    DecisionCategory,
    DecisionProfile,
    LocalOverlayRule,
    PredictionLog,
    PriorProvenance,
    PriorUsageLog,
    RunMetadata,
    UncertaintyBudget,
    ValueOfInformationItem,
)
from .model_base import JsonObject, NonEmptyString, StrictModel
from .pipeline_models import EvaluationPipelineResult


__all__ = [
    "AIAnswerClaimStatus",
    "AIAnswerMappedClaim",
    "AIAnswerMappingResult",
    "BibliographicIdentifier",
    "ClinicalDecisionEpisode",
    "DecisionCategory",
    "DecisionOption",
    "DecisionProfile",
    "DecisionProfileEvaluation",
    "DecisionProfileEvaluationSet",
    "DecisionProfileEvaluationStatus",
    "DecisionProfileInputSummary",
    "DecisionProfileInputType",
    "DomainPack",
    "DomainPackMappings",
    "EvidenceRegistry",
    "EvidenceReviewStatus",
    "EvidenceSource",
    "EvidenceSourceType",
    "EvidenceSupportLink",
    "EvidenceSupportStatus",
    "EvaluationPipelineResult",
    "JsonObject",
    "LocalOverlayRequiredField",
    "LocalOverlayRule",
    "LocalOverlayVerificationItem",
    "LocalOverlayVerificationSet",
    "LocalOverlayVerificationStatus",
    "MonteCarloPriorSimulation",
    "MonteCarloPriorStatus",
    "MonteCarloSimulationResult",
    "NonEmptyString",
    "PredictionLog",
    "Prior",
    "PriorProvenance",
    "PriorResolution",
    "PriorResolutionSet",
    "PriorResolutionStatus",
    "PriorToOptionMapping",
    "PriorUsageLog",
    "RunMetadata",
    "SafetyGate",
    "SafetyGateEvaluation",
    "SafetyGateEvaluationSet",
    "SafetyGateMatchedStatus",
    "SafetyGateStatus",
    "SafetyGateTargetMapping",
    "SourceRecommendation",
    "StatusLedger",
    "StatusLedgerComponent",
    "StatusLedgerRow",
    "StrictModel",
    "SupportedEntityType",
    "UncertaintyBudget",
    "UncertaintyBudgetEvaluationItem",
    "UncertaintyBudgetEvaluationSet",
    "UncertaintyCategory",
    "UncertaintyItemStatus",
    "ValueOfInformationEvaluation",
    "ValueOfInformationEvaluationSet",
    "ValueOfInformationItem",
    "ValueOfInformationStatus",
]
