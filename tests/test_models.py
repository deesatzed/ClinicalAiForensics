from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from pdde.models import (
    ClinicalDecisionEpisode,
    DecisionProfile,
    DomainPack,
    LocalOverlayRule,
    PredictionLog,
    Prior,
    PriorUsageLog,
    RunMetadata,
    UncertaintyBudget,
    ValueOfInformationItem,
)


ROOT = Path(__file__).resolve().parents[1]


def test_clinical_decision_episode_accepts_v03_fixture() -> None:
    payload = json.loads(
        (ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json").read_text()
    )

    cde = ClinicalDecisionEpisode.model_validate(payload)

    assert cde.cde_id == "hf_cde_stable"
    assert "discharge_add_sglt2" in cde.candidate_options
    assert json.loads(cde.model_dump_json())["patient_state"]["egfr"] == 42


def test_domain_pack_accepts_v03_fixture() -> None:
    payload = yaml.safe_load(
        (
            ROOT
            / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
        ).read_text()
    )

    domain_pack = DomainPack.model_validate(payload)

    assert domain_pack.domain_pack_id == "hf_ed_discharge_v0_3"
    assert len(domain_pack.decision_options) == 5
    assert domain_pack.prior_policy["sglt2_ed_discharge"].alpha == 14


def test_prior_without_provenance_fails_validation() -> None:
    with pytest.raises(ValidationError):
        Prior.model_validate(
            {
                "distribution": "beta",
                "alpha": 14,
                "beta": 5,
                "elicitation_method": "draft policy mapping; calibration pending",
                "confidence_class": "moderate",
                "calibration_status": "uncalibrated",
                "warning": "illustrative prior",
            }
        )


def test_low_confidence_prior_requires_warning() -> None:
    with pytest.raises(ValidationError, match="require a warning"):
        Prior.model_validate(
            {
                "distribution": "beta",
                "alpha": 9,
                "beta": 8,
                "provenance_class": "guideline_mapped_policy_prior",
                "elicitation_method": "draft policy mapping; calibration pending",
                "confidence_class": "low",
                "calibration_status": "uncalibrated",
            }
        )


def test_local_overlay_rule_requires_owner_and_verified_metadata() -> None:
    with pytest.raises(ValidationError):
        LocalOverlayRule.model_validate({"value": "HF clinic within 7 days", "status": "draft"})

    with pytest.raises(ValidationError, match="verified_by and verified_date"):
        LocalOverlayRule.model_validate(
            {"value": "HF clinic within 7 days", "status": "verified", "owner": "cardiology"}
        )

    rule = LocalOverlayRule.model_validate(
        {
            "value": "HF clinic within 7 days",
            "status": "verified",
            "owner": "cardiology",
            "verified_by": "clinical_owner",
            "verified_date": "2026-05-11",
        }
    )
    assert rule.status == "verified"


def test_decision_profile_serializes_and_rejects_reversed_interval() -> None:
    budget = UncertaintyBudget(
        evidence_uncertainty=0.2,
        patient_context_uncertainty=0.2,
        local_execution_uncertainty=0.2,
        monitoring_rescue_uncertainty=0.1,
        harm_uncertainty=0.1,
        preference_feasibility_uncertainty=0.1,
        prior_quality_uncertainty=0.1,
    )
    profile = DecisionProfile(
        option_id="discharge_add_sglt2",
        category="conditionally_defensible",
        median_fitness=0.71,
        uncertainty_interval=(0.48, 0.86),
        hard_stops=[],
        missing_variables=["follow_up_available"],
        uncertainty_budget=budget,
        value_of_information=[ValueOfInformationItem(variable="egfr", rank=1)],
    )

    serialized = json.loads(profile.model_dump_json())
    assert serialized["uncertainty_interval"] == [0.48, 0.86]
    assert serialized["uncertainty_budget"]["evidence_uncertainty"] == 0.2

    with pytest.raises(ValidationError, match="lower bound"):
        DecisionProfile(
            option_id="discharge_add_sglt2",
            category="conditionally_defensible",
            uncertainty_interval=(0.9, 0.1),
            missing_variables=[],
            uncertainty_budget=budget,
        )


def test_log_records_are_serializable() -> None:
    run = RunMetadata(
        run_id="run-001",
        cde_id="hf_cde_stable",
        domain_pack_id="hf_ed_discharge_v0_3",
        domain_pack_version="0.3",
        engine_version="0.1.0",
    )
    prior = PriorUsageLog(
        run_id=run.run_id,
        prior_id="sglt2_ed_discharge",
        distribution="beta",
        provenance_class="guideline_mapped_policy_prior",
        confidence_class="moderate",
        calibration_status="uncalibrated",
        warning_displayed=True,
    )
    prediction = PredictionLog(
        run_id=run.run_id,
        cde_id=run.cde_id,
        option_id="discharge_add_sglt2",
        category="conditionally_defensible",
        uncertainty_interval=(0.48, 0.86),
        median_fitness=0.71,
    )

    assert json.loads(run.model_dump_json())["log_type"] == "run_metadata"
    assert json.loads(prior.model_dump_json())["warning_displayed"] is True
    assert json.loads(prediction.model_dump_json())["option_id"] == "discharge_add_sglt2"
