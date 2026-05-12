from __future__ import annotations

from pathlib import Path

import pytest

from pdde.cde_loader import load_cde
from pdde.domain_pack_loader import load_domain_pack
from pdde.loader_errors import LoaderError
from pdde.run_cde import main


ROOT = Path(__file__).resolve().parents[1]
V03_CDE = ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)


def test_load_cde_returns_typed_model() -> None:
    cde = load_cde(V03_CDE)

    assert cde.cde_id == "hf_cde_stable"
    assert cde.patient_state["sbp"] == 118


def test_load_domain_pack_returns_typed_model() -> None:
    domain_pack = load_domain_pack(V03_DOMAIN)

    assert domain_pack.domain_pack_id == "hf_ed_discharge_v0_3"
    assert domain_pack.hard_gates["mra_blocks"][0].variable == "potassium"
    assert domain_pack.mappings.safety_gate_target_by_group()["mra_blocks"].matched_status == "blocked"


def test_load_cde_reports_parse_error(tmp_path: Path) -> None:
    bad_json = tmp_path / "bad_cde.json"
    bad_json.write_text('{"cde_id": ', encoding="utf-8")

    with pytest.raises(LoaderError, match="Could not parse CDE JSON"):
        load_cde(bad_json)


def test_load_cde_reports_validation_error(tmp_path: Path) -> None:
    invalid_cde = tmp_path / "invalid_cde.json"
    invalid_cde.write_text('{"cde_id": "missing-required-fields"}', encoding="utf-8")

    with pytest.raises(LoaderError, match="CDE validation failed"):
        load_cde(invalid_cde)


def test_load_domain_pack_reports_validation_error(tmp_path: Path) -> None:
    invalid_domain = tmp_path / "invalid_domain.yaml"
    invalid_domain.write_text("domain_pack_id: missing_required_fields\n", encoding="utf-8")

    with pytest.raises(LoaderError, match="Domain pack validation failed"):
        load_domain_pack(invalid_domain)


def test_load_domain_pack_reports_malformed_explicit_mapping(tmp_path: Path) -> None:
    invalid_domain = tmp_path / "invalid_mapping.yaml"
    invalid_domain.write_text(
        """
domain_pack_id: bad_mapping
version: "0.1"
status: draft
clinical_owner: pending
calibration_status: uncalibrated
decision_options:
  - id: option_a
    label: Option A
hard_gates:
  gate_a:
    - variable: sbp
      condition: <90
      reason: hypotension
mappings:
  safety_gate_targets:
    - gate_group: gate_a
      option_id: missing_option
      matched_status: blocked
""",
        encoding="utf-8",
    )

    with pytest.raises(LoaderError, match="unknown option_id"):
        load_domain_pack(invalid_domain)


def test_load_domain_pack_reports_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.yaml"

    with pytest.raises(LoaderError, match="Domain pack file not found"):
        load_domain_pack(missing)


def test_validate_command_accepts_cde_and_domain(capsys) -> None:
    assert main(["validate", "--cde", str(V03_CDE), "--domain", str(V03_DOMAIN)]) == 0
    output = capsys.readouterr().out

    assert "CDE valid:" in output
    assert "Domain pack valid:" in output


def test_validate_command_returns_nonzero_for_invalid_file(tmp_path: Path, capsys) -> None:
    invalid_cde = tmp_path / "invalid_cde.json"
    invalid_cde.write_text('{"cde_id": "missing-required-fields"}', encoding="utf-8")

    assert main(["validate", "--cde", str(invalid_cde)]) == 1
    captured = capsys.readouterr()

    assert "CDE validation failed" in captured.err


def test_validate_command_requires_an_input(capsys) -> None:
    assert main(["validate"]) == 1
    captured = capsys.readouterr()

    assert "validate requires" in captured.err
