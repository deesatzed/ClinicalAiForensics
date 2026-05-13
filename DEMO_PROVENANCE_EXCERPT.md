# Demo Provenance Excerpt

## Purpose

This document gives a normalized, status-only excerpt of the provenance produced by:

```bash
python -m pdde demo
```

The generated JSONL file is `logs/demo_run.jsonl`. It is ignored by git because it is append-only and run-specific.

This excerpt is safe for review because it uses IDs, statuses, counts, paths, and source references. It does not include PHI, raw clinical text, raw patient-state payloads, raw AI-answer text, raw simulation samples, gate evidence strings, or local owner/source/review free text.

## Run Metadata Shape

```json
{
  "log_type": "run_metadata",
  "payload": {
    "command_name": "demo",
    "workflow_mode": "direct_cde_simulation",
    "cde_source": "examples/hf_cde_stable.json",
    "domain_pack_source": "pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml",
    "report_path": "reports/demo_report.md",
    "domain": "hf_ed_discharge",
    "domain_pack_version": "0.3",
    "domain_pack_status": "draft",
    "calibration_status": "uncalibrated",
    "n_iterations": 5,
    "random_seed": 17
  }
}
```

## Per-Run Record Counts

A fresh `python -m pdde demo` run emits one run worth of JSONL records with this status-only shape:

| Log type | Count |
|---|---:|
| `run_metadata` | 1 |
| `component_status_summary` | 1 |
| `evidence_link_validation` | 1 |
| `safety_gate_result` | 11 |
| `prior_resolution` | 3 |
| `monte_carlo_prior` | 3 |
| `uncertainty_budget_item` | 7 |
| `value_of_information_item` | 8 |
| `local_overlay_verification` | 1 |
| `decision_profile` | 5 |

`logs/demo_run.jsonl` is append-only, so repeated local runs add additional sets of these records.

## Component Status Summary

```json
{
  "log_type": "component_status_summary",
  "payload": {
    "safety_gates": {
      "passed": 8,
      "missing": 1,
      "unsupported": 2
    },
    "prior_resolutions": {
      "resolved": 3
    },
    "monte_carlo_priors": {
      "sampled": 3
    },
    "uncertainty_budget_items": {
      "active": 2,
      "deferred": 2,
      "defined": 3
    },
    "value_of_information_items": {
      "present": 8
    },
    "evidence_links": {
      "deferred": 1
    },
    "local_overlay_items": {
      "draft": 1
    },
    "decision_profiles": {
      "eligible": 4,
      "missing": 1
    }
  }
}
```

## Evidence Reference Status

```json
{
  "log_type": "evidence_link_validation",
  "payload": {
    "supported_entity_type": "domain_pack",
    "supported_entity_id": "hf_ed_discharge_v0_3",
    "evidence_source_present": false,
    "link_status": "deferred",
    "support_link_present": false,
    "source": "domain_pack:hf_ed_discharge_v0_3.evidence_references"
  }
}
```

Interpretation: evidence references are visible as status, not as source truth validation, citation scoring, or clinical correctness.

## Safety Gate Status

The demo includes:

- 8 passed safety-gate rows.
- 1 missing safety-gate input: `oxygen_requirement`.
- 2 unsupported claim-type gates that require explicit mapped AI-answer claims.

Interpretation: unsupported claim gates are not silently passed. They remain visible because `audit-answer` is not implemented and the demo CLI does not consume the synthetic AI-answer artifact.

## Local Governance Status

```json
{
  "log_type": "local_overlay_verification",
  "payload": {
    "overlay_id": "local_overlay",
    "status": "draft",
    "owner_present": false,
    "source_reference_present": false,
    "review_cadence_present": false,
    "last_reviewed_present": false
  }
}
```

Interpretation: local overlay metadata remains draft and non-activating. No local clinical rules are active.

## Privacy Boundary

The provenance log should be used to inspect run structure and status. It should not be used to store:

- PHI.
- raw AI-answer text.
- raw patient-state payloads.
- raw clinical notes.
- gate evidence strings.
- raw simulation samples.
- local overlay owner/source/review free text.

## Demo Claim Boundary

The provenance excerpt supports auditability. It does not prove clinical correctness, source truth, citation quality, outcome calibration, or clinical approval.
