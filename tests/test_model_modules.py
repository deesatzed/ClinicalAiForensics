from __future__ import annotations

import json

from pdde import component_models, input_models, legacy_models, model_base, models, pipeline_models
from pdde.evaluation_pipeline import run_evaluation_pipeline


def test_models_facade_reexports_focused_model_classes() -> None:
    assert models.StrictModel is model_base.StrictModel
    assert models.ClinicalDecisionEpisode is input_models.ClinicalDecisionEpisode
    assert models.DomainPack is input_models.DomainPack
    assert models.Prior is input_models.Prior
    assert models.SafetyGateEvaluation is component_models.SafetyGateEvaluation
    assert models.LocalOverlayVerificationSet is component_models.LocalOverlayVerificationSet
    assert models.StatusLedger is component_models.StatusLedger
    assert models.EvaluationPipelineResult is pipeline_models.EvaluationPipelineResult
    assert models.DecisionProfile is legacy_models.DecisionProfile
    assert models.RunMetadata is legacy_models.RunMetadata


def test_models_facade_all_exports_are_available() -> None:
    for name in models.__all__:
        assert getattr(models, name) is not None


def test_pipeline_result_serialization_surface_survives_module_split() -> None:
    result = run_evaluation_pipeline(
        cde_path="pdde_v0_3_first_principles_final/examples/hf_cde_stable.json",
        domain_pack_path="pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml",
        n_iterations=5,
        random_seed=17,
    )

    assert isinstance(result, pipeline_models.EvaluationPipelineResult)
    assert isinstance(result.cde, input_models.ClinicalDecisionEpisode)
    assert isinstance(result.safety_gates, component_models.SafetyGateEvaluationSet)
    assert isinstance(result.local_overlay, component_models.LocalOverlayVerificationSet)

    serialized = json.loads(result.model_dump_json())
    assert serialized["workflow_mode"] == "direct_cde_simulation"
    assert serialized["cde"]["cde_id"] == "hf_cde_stable"
    assert serialized["domain_pack"]["domain_pack_id"] == "hf_ed_discharge_v0_3"
