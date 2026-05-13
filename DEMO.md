# PDDE Phase 0 Demo

This is a 5-minute technical demo script for a reviewer. It exercises the current Phase 0 CLI with synthetic canonical fixtures and gives safe language for explaining the result.

Phase 0 is advisory-only, uncalibrated, synthetic, and not clinically validated.

For the final organization-neutral demo package, start with `FINAL_DEMO_PACKAGE.md`, then use this file for the command-by-command walkthrough.

## Demo Setup

Canonical CDE:

```text
pdde_v0_3_first_principles_final/examples/hf_cde_stable.json
```

Canonical domain pack:

```text
pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml
```

Root synthetic scenario fixtures:

```text
examples/hf_cde_stable.json
examples/hf_cde_low_egfr.json
examples/hf_cde_high_k.json
examples/hf_cde_low_sbp.json
examples/hf_cde_no_followup.json
examples/hf_cde_prior_dka.json
examples/hf_cde_missing_labs.json
```

Optional environment setup:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## 5-Minute Demo Script

### 1. Show The CLI Surface

Run:

```bash
python -m pdde --help
```

What to look for:

- commands: `validate`, `report`, `demo`, and `run-cde`
- no server, UI, auth, EHR, or deployment command

Safe explanation:

> This is a local Phase 0 CLI. It validates inputs, runs a deterministic evidence-preserving pipeline, and renders an advisory report.

### 2. Run The Short Synthetic Demo

Run:

```bash
python -m pdde demo
```

What to look for:

- `Report written: reports/demo_report.md`
- `Log written: logs/demo_run.jsonl`
- `Demo complete: synthetic/non-PHI advisory output only; not approved for clinical use.`

Safe explanation:

> This is the short organization-neutral demo wrapper. It uses the synthetic stable CDE and canonical HF ED discharge domain pack, writes an advisory Markdown report, and writes a status-only provenance log. It does not consume the synthetic AI-answer artifact or perform answer grading.

### 3. Validate The Canonical Inputs

Run:

```bash
python -m pdde validate --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml
```

What to look for:

- `CDE valid`
- `Domain pack valid`
- loaded IDs: `hf_cde_stable` and `hf_ed_discharge_v0_3`

Safe explanation:

> The pipeline starts from structured synthetic inputs. It does not parse a real chart or use PHI.

### 4. Generate The Report To Stdout

Run:

```bash
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --iterations 5 --seed 17
```

What to look for:

- `# PDDE Decision Profile Report`
- `## Advisory Status`
- `## Safety Gate Results`
- `## Decision Profile Statuses`
- `## Why There Is No Top Option`
- `## Missing Variables And Value Of Information`
- `## Uncertainty Budget`
- `### Local Overlay Verification`
- `## Prior Provenance`
- `## Monte Carlo Prior Summaries`
- `## Missing Unsupported Deferred And Blocked Items`
- `## Calibration Status`
- `## Limitations`

Reviewer checks:

- `oxygen_requirement` remains visible as missing.
- wrong-indication claim gates remain visible as unsupported in the direct CLI path because no explicit mapped AI-answer claim input is supplied.
- local overlay verification remains visible as draft/deferred unless owner/source/review metadata is explicit.
- Monte Carlo summaries are prior-level only.
- the report says it is not clinically validated and not a final clinical recommendation.
- the report does not name a top option.

Safe explanation:

> The report preserves explicit evidence, missing data, unsupported gates, deferred items, draft priors, and calibration status. It does not make a clinical recommendation. AI-answer claim mapping is available only as a typed API boundary, not as CLI free-text judgment.

### 5. Generate The Report File

Run:

```bash
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --output reports/hf_cde_stable_report.md --iterations 5 --seed 17
```

What to look for:

- `Report written: reports/hf_cde_stable_report.md`

Optional inspection:

```bash
sed -n '1,120p' reports/hf_cde_stable_report.md
```

Safe explanation:

> The Markdown artifact is deterministic for a fixed input, seed, and iteration count. It is intended for review of the decision-profile structure, not patient care.

### 6. Generate Provenance JSONL

Run:

```bash
python -m pdde report --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --output reports/hf_cde_stable_report.md --log logs/hf_cde_stable.jsonl --iterations 5 --seed 17
```

What to look for:

- `Report written: reports/hf_cde_stable_report.md`
- `Log written: logs/hf_cde_stable.jsonl`

Parse the log:

```bash
python -c "from pathlib import Path; import json; records=[json.loads(line) for line in Path('logs/hf_cde_stable.jsonl').read_text(encoding='utf-8').splitlines()]; print(f'{len(records)} valid JSONL records')"
```

Inspect record types:

```bash
python -c "from pathlib import Path; import json, collections; records=[json.loads(line) for line in Path('logs/hf_cde_stable.jsonl').read_text(encoding='utf-8').splitlines()]; counts=collections.Counter(record.get('log_type') for record in records); print(dict(sorted(counts.items())))"
```

What to look for:

- parseable JSONL
- `run_metadata`
- `component_status_summary`
- `safety_gate_result`
- `prior_resolution`
- `monte_carlo_prior`
- `uncertainty_budget_item`
- `value_of_information_item`
- `local_overlay_verification`
- `decision_profile`

Safe explanation:

> The log records statuses, IDs, paths, counts, seed, command metadata, and source references. It intentionally avoids raw clinical payloads, raw simulation samples, and raw local overlay owner/source/review values.

### 7. Run The Test Suite

Run:

```bash
python -m pytest
```

What to look for:

- `131 passed`

Safe explanation:

> The test suite checks deterministic behavior, validation failures, missingness, hard gates, API-only AI-answer claim mapping, local overlay verification, provenance, CLI behavior, and report guardrails. Passing tests do not imply clinical validity.

## Optional Scenario Fixture Check

Run:

```bash
python -m pdde validate --cde examples/hf_cde_high_k.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml
python -m pdde report --cde examples/hf_cde_missing_labs.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml --iterations 5 --seed 17
```

What to look for:

- the high-potassium fixture validates as a synthetic CDE.
- the missing-labs fixture keeps eGFR, potassium, and oxygen-requirement gaps visible.

Safe explanation:

> These are synthetic non-PHI scenario fixtures for reviewing gate and missingness behavior. They do not add clinical thresholds or recommendations.

## Optional Negative-Path Check

Run:

```bash
python -m pdde validate --cde does-not-exist.json
```

What to look for:

- nonzero exit status
- clear loader/read error
- no report generated

Safe explanation:

> Invalid inputs fail clearly rather than falling back silently.

## How To Explain The Result Safely

Use this framing:

> This is a deterministic Phase 0 scaffold for preserving the structure of a clinical decision episode. It shows which explicit gates passed, which inputs are missing, which priors were sampled, which local overlay verification metadata is still draft or deferred, which items are unsupported, and where provenance came from. It is not a clinical recommendation engine.

Avoid these claims:

- "The patient is safe to discharge."
- "The tool recommends discharge."
- "This is validated risk."
- "This is an AI clinical judgment."
- "This ranks the options."
- "The CLI grades free-text AI answers."
- "Draft local workflow rules are active."
- "This can run on PHI or production data."

## Files To Review After The Demo

| File | Why Review It |
| --- | --- |
| `README.md` | Reviewer overview and command reference. |
| `reports/hf_cde_stable_report.md` | Generated advisory Markdown report. |
| `logs/hf_cde_stable.jsonl` | Appendable status-only provenance log. |
| `tests/test_phase0_acceptance.py` | End-to-end CLI/API guardrail tests. |
| `pdde/evaluation_pipeline.py` | Deterministic orchestration boundary. |
| `pdde/report_renderer.py` | Report section and language boundary. |
| `pdde/provenance_logger.py` | Status-only audit-log boundary. |
| `PHASE0_HANDOFF.md` | Phase 0 status and stop/go recommendation. |
| `PHASE1_PLAN.md` | Phase 1 roadmap and acceptance criteria. |
| `BASELINE_POLICY.md` | Phase 0 baseline tag, submodule policy, and generated-artifact rules. |
