# PDDE Phase 0 Demo

This is a 5-minute technical demo script for a reviewer. It exercises the current Phase 0 CLI with synthetic canonical fixtures and gives safe language for explaining the result.

Phase 0 is advisory-only, uncalibrated, synthetic, and not clinically validated.

## Demo Setup

Canonical CDE:

```text
pdde_v0_3_first_principles_final/examples/hf_cde_stable.json
```

Canonical domain pack:

```text
pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml
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

- commands: `validate`, `report`, and `run-cde`
- no server, UI, auth, EHR, or deployment command

Safe explanation:

> This is a local Phase 0 CLI. It validates inputs, runs a deterministic evidence-preserving pipeline, and renders an advisory report.

### 2. Validate The Canonical Inputs

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

### 3. Generate The Report To Stdout

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
- `## Prior Provenance`
- `## Monte Carlo Prior Summaries`
- `## Missing Unsupported Deferred And Blocked Items`
- `## Calibration Status`
- `## Limitations`

Reviewer checks:

- `oxygen_requirement` remains visible as missing.
- wrong-indication claim gates remain visible as unsupported because AI answer mapping is deferred.
- Monte Carlo summaries are prior-level only.
- the report says it is not clinically validated and not a final clinical recommendation.
- the report does not name a top option.

Safe explanation:

> The report preserves explicit evidence, missing data, unsupported gates, deferred items, draft priors, and calibration status. It does not make a clinical recommendation.

### 4. Generate The Report File

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

### 5. Generate Provenance JSONL

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
- `decision_profile`

Safe explanation:

> The log records statuses, IDs, paths, counts, seed, command metadata, and source references. It intentionally avoids raw clinical payloads and raw simulation samples.

### 6. Run The Test Suite

Run:

```bash
python -m pytest
```

What to look for:

- `96 passed`

Safe explanation:

> The test suite checks deterministic behavior, validation failures, missingness, hard gates, provenance, CLI behavior, and report guardrails. Passing tests do not imply clinical validity.

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

> This is a deterministic Phase 0 scaffold for preserving the structure of a clinical decision episode. It shows which explicit gates passed, which inputs are missing, which priors were sampled, which items are deferred or unsupported, and where provenance came from. It is not a clinical recommendation engine.

Avoid these claims:

- "The patient is safe to discharge."
- "The tool recommends discharge."
- "This is validated risk."
- "This is an AI clinical judgment."
- "This ranks the options."
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
