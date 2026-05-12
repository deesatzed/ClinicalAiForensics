from __future__ import annotations

from pathlib import Path

from pdde.cde_loader import load_cde
from pdde.domain_pack_loader import load_domain_pack
from pdde.models import ClinicalDecisionEpisode, DomainPack, SafetyGate, SafetyGateEvaluation
from pdde.safety_gate_engine import evaluate_safety_gates


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


def _find(
    evaluations: list[SafetyGateEvaluation],
    *,
    gate_group: str,
    variable: str | None = None,
    option_id: str | None = None,
    claim_type: str | None = None,
) -> SafetyGateEvaluation:
    for evaluation in evaluations:
        if evaluation.gate_group != gate_group:
            continue
        if variable is not None and evaluation.variable != variable:
            continue
        if option_id is not None and evaluation.option_id != option_id:
            continue
        if claim_type is not None and evaluation.claim_type != claim_type:
            continue
        return evaluation
    raise AssertionError(f"evaluation not found for {gate_group=} {variable=} {option_id=} {claim_type=}")


def test_stable_case_passes_explicit_numeric_hard_gates() -> None:
    result = evaluate_safety_gates(_cde(), _domain())

    potassium = _find(
        result.evaluations,
        gate_group="mra_blocks",
        option_id="discharge_add_mra",
        variable="potassium",
    )
    sbp = _find(
        result.evaluations,
        gate_group="admit_or_observe_triggers",
        option_id="admit_or_observe",
        variable="sbp",
    )

    assert potassium.status == "passed"
    assert potassium.evidence == "potassium=4.5 does not meet >=5.5"
    assert sbp.status == "passed"
    assert result.active_hard_stops() == []


def test_high_potassium_blocks_mra_with_evidence() -> None:
    result = evaluate_safety_gates(_cde(potassium=5.7), _domain())

    potassium = _find(
        result.evaluations,
        gate_group="mra_blocks",
        option_id="discharge_add_mra",
        variable="potassium",
    )

    assert potassium.status == "blocked"
    assert potassium.reason == "hyperkalemia risk"
    assert potassium.evidence == "potassium=5.7 meets >=5.5"
    assert result.hard_stops_by_option()["discharge_add_mra"] == [
        "hyperkalemia risk: potassium=5.7 meets >=5.5"
    ]


def test_low_sbp_triggers_admit_or_observe_pressure() -> None:
    result = evaluate_safety_gates(_cde(sbp=86), _domain())

    sbp = _find(
        result.evaluations,
        gate_group="admit_or_observe_triggers",
        option_id="admit_or_observe",
        variable="sbp",
    )

    assert sbp.status == "triggered"
    assert sbp.reason == "hypotension"
    assert result.hard_stops_by_option()["admit_or_observe"] == ["hypotension: sbp=86 meets <90"]


def test_low_egfr_blocks_sglt2_and_mra_gates() -> None:
    result = evaluate_safety_gates(_cde(egfr=15), _domain())

    sglt2 = _find(
        result.evaluations,
        gate_group="sglt2_blocks",
        option_id="discharge_add_sglt2",
        variable="egfr",
    )
    mra = _find(
        result.evaluations,
        gate_group="mra_blocks",
        option_id="discharge_add_mra",
        variable="egfr",
    )

    assert sglt2.status == "blocked"
    assert sglt2.evidence == "egfr=15 meets <20"
    assert mra.status == "blocked"
    assert mra.evidence == "egfr=15 meets <30"


def test_prior_euglycemic_dka_blocks_sglt2_compound_gate() -> None:
    result = evaluate_safety_gates(_cde(dka_risk="prior_euglycemic_dka"), _domain())

    dka = _find(
        result.evaluations,
        gate_group="sglt2_blocks",
        option_id="discharge_add_sglt2",
        variable="dka_risk",
    )

    assert dka.status == "blocked"
    assert dka.evidence == (
        "dka_risk='prior_euglycemic_dka' meets active_ketosis_or_prior_euglycemic_dka_high_risk"
    )


def test_missing_gate_input_is_not_silently_passed() -> None:
    result = evaluate_safety_gates(_cde_without("potassium"), _domain())

    potassium = _find(
        result.evaluations,
        gate_group="mra_blocks",
        option_id="discharge_add_mra",
        variable="potassium",
    )

    assert potassium.status == "missing"
    assert potassium.evidence == "potassium is missing; condition >=5.5 was not evaluated"


def test_malformed_gate_input_is_unsupported_not_passed() -> None:
    result = evaluate_safety_gates(_cde(sbp="low"), _domain())

    sbp = _find(
        result.evaluations,
        gate_group="admit_or_observe_triggers",
        option_id="admit_or_observe",
        variable="sbp",
    )

    assert sbp.status == "unsupported"
    assert "requires a numeric value" in sbp.evidence


def test_claim_type_gates_are_explicitly_unsupported_until_claim_mapping() -> None:
    result = evaluate_safety_gates(_cde(), _domain())

    sotalol = _find(
        result.evaluations,
        gate_group="wrong_indication_blocks",
        claim_type="sotalol_as_hf_beta_blocker",
    )

    assert sotalol.status == "unsupported"
    assert "AI answer mapping is deferred" in sotalol.evidence


def test_unknown_gate_group_is_unsupported_not_passed() -> None:
    domain = _domain()
    hard_gates = {
        **domain.hard_gates,
        "custom_blocks": [SafetyGate(variable="sbp", condition="<90", reason="custom rule")],
    }
    domain = domain.model_copy(update={"hard_gates": hard_gates})

    result = evaluate_safety_gates(_cde(), domain)
    custom = _find(result.evaluations, gate_group="custom_blocks", variable="sbp")

    assert custom.status == "unsupported"
    assert "unsupported hard gate group" in custom.evidence
