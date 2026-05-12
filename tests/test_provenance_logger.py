from __future__ import annotations

import json
from pathlib import Path

from pdde.evaluation_pipeline import run_evaluation_pipeline
from pdde.provenance_logger import append_jsonl, create_provenance_records, records_to_jsonl, write_jsonl


ROOT = Path(__file__).resolve().parents[1]
V03_CDE = ROOT / "pdde_v0_3_first_principles_final/examples/hf_cde_stable.json"
V03_DOMAIN = (
    ROOT / "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml"
)
TIMESTAMP = "2026-05-11T00:00:00Z"


def _result():
    return run_evaluation_pipeline(
        cde_path=V03_CDE,
        domain_pack_path=V03_DOMAIN,
        n_iterations=5,
        random_seed=17,
    )


def _records():
    return create_provenance_records(
        _result(),
        command_name="report",
        report_path="reports/hf_cde_stable_report.md",
        timestamp=TIMESTAMP,
        run_id="run_test",
    )


def test_create_provenance_records_from_pipeline_result() -> None:
    records = _records()

    assert records[0]["log_type"] == "run_metadata"
    assert records[0]["run_id"] == "run_test"
    assert records[0]["timestamp"] == TIMESTAMP
    assert records[0]["cde_id"] == "hf_cde_stable"
    assert records[0]["domain_pack_id"] == "hf_ed_discharge_v0_3"
    assert records[0]["payload"]["cde_source"] == str(V03_CDE)
    assert records[0]["payload"]["domain_pack_source"] == str(V03_DOMAIN)
    assert records[0]["payload"]["report_path"] == "reports/hf_cde_stable_report.md"
    assert records[0]["payload"]["random_seed"] == 17
    assert [record["sequence"] for record in records] == list(range(len(records)))


def test_jsonl_serialization_round_trips() -> None:
    records = _records()
    jsonl = records_to_jsonl(records)

    parsed = [json.loads(line) for line in jsonl.splitlines()]
    assert parsed == records
    assert jsonl.endswith("\n")
    assert len(parsed) == len(records)


def test_log_records_include_key_component_statuses() -> None:
    records = _records()

    summary = next(record for record in records if record["log_type"] == "component_status_summary")
    assert summary["payload"]["safety_gates"]["missing"] == 1
    assert summary["payload"]["safety_gates"]["unsupported"] == 2
    assert summary["payload"]["prior_resolutions"] == {"resolved": 3}
    assert summary["payload"]["monte_carlo_priors"] == {"sampled": 3}
    assert summary["payload"]["uncertainty_budget_items"]["deferred"] == 2
    assert summary["payload"]["value_of_information_items"] == {"present": 8}
    assert summary["payload"]["decision_profiles"]["eligible"] == 4
    assert summary["payload"]["decision_profiles"]["missing"] == 1

    profile_records = [record for record in records if record["log_type"] == "decision_profile"]
    assert {record["payload"]["option_id"] for record in profile_records} == {
        "admit_or_observe",
        "discharge_loop_continue_gdmt",
        "discharge_add_sglt2",
        "discharge_add_mra",
        "discharge_urgent_followup_no_new_dmt",
    }

    safety_record = next(
        record
        for record in records
        if record["log_type"] == "safety_gate_result"
        and record["payload"]["gate_group"] == "sglt2_blocks"
        and record["payload"]["variable"] == "egfr"
    )
    assert safety_record["payload"]["mapping_source"] == (
        "domain_pack:hf_ed_discharge_v0_3.mappings.safety_gate_targets.sglt2_blocks"
    )
    assert (
        "domain_pack:hf_ed_discharge_v0_3.mappings.prior_to_options.sglt2_ed_discharge"
        in records[0]["payload"]["provenance_references"]
    )


def test_log_records_do_not_include_full_raw_case_content_or_values() -> None:
    jsonl = records_to_jsonl(_records())

    assert "Known HFrEF/HFmrEF" not in jsonl
    assert "wants discharge if safe" not in jsonl
    assert "sbp=118" not in jsonl
    assert "potassium=4.5" not in jsonl
    assert "samples" not in jsonl
    assert "case_text" not in jsonl
    assert '"patient_state":' not in jsonl


def test_timestamp_and_derived_run_id_can_be_deterministic() -> None:
    result = _result()
    first = create_provenance_records(result, command_name="report", timestamp=TIMESTAMP)
    second = create_provenance_records(result, command_name="report", timestamp=TIMESTAMP)

    assert first == second
    assert {record["timestamp"] for record in first} == {TIMESTAMP}
    assert first[0]["run_id"].startswith("run_")


def test_write_jsonl_creates_parseable_file(tmp_path: Path) -> None:
    path = tmp_path / "run.jsonl"
    records = _records()

    write_jsonl(records, path)

    assert path.exists()
    parsed = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert parsed == records


def test_append_jsonl_adds_parseable_records(tmp_path: Path) -> None:
    path = tmp_path / "run.jsonl"
    records = _records()

    append_jsonl(records[:2], path)
    append_jsonl(records[2:4], path)

    parsed = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert parsed == records[:4]
