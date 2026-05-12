from __future__ import annotations

import json
from pathlib import Path

from pdde.cde_loader import load_cde
from pdde.domain_pack_loader import load_domain_pack
from pdde.models import (
    ClinicalDecisionEpisode,
    DomainPack,
    UncertaintyBudgetEvaluationItem,
    ValueOfInformationEvaluation,
)
from pdde.monte_carlo_engine import simulate_resolved_priors
from pdde.prior_resolver import resolve_priors
from pdde.safety_gate_engine import evaluate_safety_gates
from pdde.uncertainty_budget import evaluate_uncertainty_budget
from pdde.value_of_information import evaluate_value_of_information


ROOT = Path(__file__).resolve().parents[1]
V03_CDE = ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)


def _cde(**patient_state_updates: object) -> ClinicalDecisionEpisode:
    cde = load_cde(V03_CDE)
    patient_state = dict(cde.patient_state)
    patient_state.update(patient_state_updates)
    return cde.model_copy(update={"patient_state": patient_state})


def _cde_without(*variables: str) -> ClinicalDecisionEpisode:
    cde = load_cde(V03_CDE)
    patient_state = dict(cde.patient_state)
    for variable in variables:
        patient_state.pop(variable, None)
    return cde.model_copy(update={"patient_state": patient_state})


def _domain() -> DomainPack:
    return load_domain_pack(V03_DOMAIN)


def _budget_item(
    items: list[UncertaintyBudgetEvaluationItem],
    category: str,
) -> UncertaintyBudgetEvaluationItem:
    for item in items:
        if item.category == category:
            return item
    raise AssertionError(f"uncertainty budget item not found for {category!r}")


def _voi_item(
    items: list[ValueOfInformationEvaluation],
    variable: str,
) -> ValueOfInformationEvaluation:
    for item in items:
        if item.variable == variable:
            return item
    raise AssertionError(f"VOI item not found for {variable!r}")


def test_explicit_uncertainty_budget_items_are_evaluated_with_traceability() -> None:
    cde = _cde()
    domain = _domain()
    safety = evaluate_safety_gates(cde, domain)
    priors = resolve_priors(domain, cde=cde)
    simulation = simulate_resolved_priors(priors, n_iterations=20, random_seed=3)

    result = evaluate_uncertainty_budget(
        cde,
        domain,
        safety_gates=safety,
        prior_resolutions=priors,
        simulation=simulation,
    )
    categories = [item.category for item in result.items]
    prior_quality = _budget_item(result.items, "prior_quality_uncertainty")
    harm = _budget_item(result.items, "harm_uncertainty")

    assert result.cde_id == "hf_cde_stable"
    assert result.domain_pack_id == "hf_ed_discharge_v0_3"
    assert categories == [
        "evidence_uncertainty",
        "patient_context_uncertainty",
        "local_execution_uncertainty",
        "monitoring_rescue_uncertainty",
        "harm_uncertainty",
        "preference_feasibility_uncertainty",
        "prior_quality_uncertainty",
    ]
    assert all(item.source.startswith("pdde_v0_3_first_principles_final/05") for item in result.items)
    assert prior_quality.status == "active"
    assert set(prior_quality.related_prior_ids) == {
        "sglt2_ed_discharge",
        "mra_ed_start",
        "loop_continue_gdmt",
    }
    assert prior_quality.actionable is True
    assert harm.status == "deferred"
    assert "harm ranges" in harm.required_data[0]
    assert "numeric harm attribution formula" in harm.reason


def test_explicit_domain_pack_voi_items_are_evaluated_in_source_order() -> None:
    cde = _cde()
    domain = _domain()
    safety = evaluate_safety_gates(cde, domain)

    result = evaluate_value_of_information(cde, domain, safety_gates=safety)
    egfr = _voi_item(result.items, "egfr")
    sbp = _voi_item(result.items, "post_diuresis_sbp")

    assert [item.variable for item in result.items] == domain.value_of_information_variables
    assert [item.rank for item in result.items] == list(range(1, 9))
    assert egfr.status == "present"
    assert egfr.source == "domain_pack:hf_ed_discharge_v0_3.value_of_information_variables"
    assert egfr.source_field == "patient_state.egfr"
    assert egfr.actionable is False
    assert sbp.status == "present"
    assert sbp.source_field == "patient_state.sbp"
    assert "no numeric VOI score" in sbp.reason


def test_missing_voi_items_are_actionable_and_feed_patient_context_uncertainty() -> None:
    cde = _cde_without("egfr", "potassium")
    domain = _domain()
    safety = evaluate_safety_gates(cde, domain)

    voi = evaluate_value_of_information(cde, domain, safety_gates=safety)
    budget = evaluate_uncertainty_budget(
        cde,
        domain,
        safety_gates=safety,
        prior_resolutions=resolve_priors(domain, cde=cde),
        value_of_information=voi,
    )
    egfr = _voi_item(voi.items, "egfr")
    potassium = _voi_item(voi.items, "potassium")
    patient_context = _budget_item(budget.items, "patient_context_uncertainty")

    assert egfr.status == "missing"
    assert egfr.actionable is True
    assert egfr.could_change_decision is True
    assert egfr.required_data == ["Provide CDE patient_state.egfr."]
    assert "sglt2_blocks" in egfr.related_gate_groups
    assert potassium.status == "missing"
    assert potassium.rank == 2
    assert patient_context.status == "active"
    assert set(patient_context.related_variables) >= {"egfr", "potassium"}
    assert patient_context.actionable is True


def test_unsupported_or_malformed_voi_definitions_remain_visible() -> None:
    domain = _domain().model_copy(
        update={"value_of_information_variables": ["egfr", "", None]}
    )

    result = evaluate_value_of_information(_cde(), domain)

    unsupported = [item for item in result.items if item.status == "unsupported"]
    assert len(unsupported) == 2
    assert unsupported[0].variable == "<invalid:''>"
    assert unsupported[1].variable == "<invalid:None>"
    assert all("must be non-empty strings" in item.reason for item in unsupported)


def test_evaluator_does_not_invent_voi_thresholds_or_numeric_values() -> None:
    result = evaluate_value_of_information(
        _cde_without("egfr"),
        _domain(),
    )
    egfr = _voi_item(result.items, "egfr")
    serialized = json.loads(egfr.model_dump_json())

    assert egfr.status == "missing"
    assert egfr.required_data == ["Provide CDE patient_state.egfr."]
    assert "threshold" not in egfr.reason.lower()
    assert "probability" not in egfr.reason.lower()
    assert "threshold" not in json.dumps(serialized).lower()


def test_deferred_voi_definitions_are_returned_when_domain_pack_has_no_voi_list() -> None:
    domain = _domain().model_copy(update={"value_of_information_variables": []})

    result = evaluate_value_of_information(_cde(), domain)
    deferred = result.deferred_items()[0]

    assert deferred.variable == "value_of_information_variables"
    assert deferred.status == "deferred"
    assert "does not define explicit value-of-information variables" in deferred.reason
    assert deferred.required_data == ["Add explicit value_of_information_variables to the domain pack."]


def test_uncertainty_budget_result_serializes() -> None:
    cde = _cde()
    domain = _domain()
    priors = resolve_priors(domain, cde=cde)

    result = evaluate_uncertainty_budget(
        cde,
        domain,
        safety_gates=evaluate_safety_gates(cde, domain),
        prior_resolutions=priors,
        simulation=simulate_resolved_priors(priors, n_iterations=10, random_seed=5),
    )
    serialized = json.loads(result.model_dump_json())

    assert serialized["items"][0]["category"] == "evidence_uncertainty"
    assert serialized["items"][-1]["category"] == "prior_quality_uncertainty"
