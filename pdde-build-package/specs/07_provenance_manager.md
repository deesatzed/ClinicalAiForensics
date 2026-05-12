# 07 — Provenance Manager

Phase 0 minimum: log all priors used and predictions made to JSONL files. No database yet.

## Purpose

Provide audit-grade logging of every prior used in a simulation and every prediction generated. This is the foundation for Phase 4 calibration analysis.

## What gets logged

Each simulation run produces these log entries:

### Run metadata (one entry per `simulate()` call)

```json
{
  "log_type": "run_metadata",
  "run_id": "uuid",
  "timestamp": "2026-05-11T14:32:00Z",
  "case_id": "HF-001-stable-postdiuresis",
  "network_id": "hf_ed_discharge_v0",
  "network_version": "0.1",
  "workflow_mode": "B_decision_simulation",
  "n_iterations": 10000,
  "random_seed": null,
  "ai_answer_provided": false,
  "engine_version": "0.1.0"
}
```

### Priors used (one entry per Prior consumed in a run)

```json
{
  "log_type": "prior_used",
  "run_id": "uuid",
  "node_name": "sglt2_ed_discharge_initiation",
  "distribution_type": "beta",
  "parameters": {"alpha": 11, "beta": 6},
  "provenance_class": "panel_elicited_pending",
  "confidence_class": "moderate_unverified",
  "provenance_detail": "Guideline Class I HFrEF + EMPULSE inpatient stabilization; ED-discharge extrapolation",
  "warning_displayed": true
}
```

### Predictions produced (one entry per decision option in the result)

```json
{
  "log_type": "prediction",
  "run_id": "uuid",
  "case_id": "HF-001-stable-postdiuresis",
  "option_id": "discharge_add_sglt2",
  "median_fitness": 0.71,
  "p5": 0.48,
  "p95": 0.86,
  "interval_width": 0.38,
  "classification": "conditionally_defensible",
  "category_probabilities": {
    "action_ready": 0.18,
    "conditionally_defensible": 0.52,
    "needs_more_data": 0.24,
    "discouraged": 0.0,
    "unsafe": 0.06
  },
  "timestamp": "2026-05-11T14:32:03Z"
}
```

## Function signatures

```python
class ProvenanceLogger:
    def __init__(self, log_dir: Path = Path("logs")):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)
        self.run_id: str | None = None

    def start_run(self, case: ClinicalCase, network: BeliefNetwork, ...) -> str:
        """Start a new run; returns run_id."""

    def log_prior(self, node_name: str, prior: Prior, warning_displayed: bool) -> None:
        """Log a prior used in the current run."""

    def log_prediction(self, option_posterior: OptionPosterior) -> None:
        """Log a prediction from the current run."""

    def end_run(self) -> None:
        """Finalize the current run."""
```

## File layout

```
logs/
├── runs.jsonl           # One line per run_metadata
├── priors.jsonl         # One line per prior_used
└── predictions.jsonl    # One line per prediction
```

All files are append-only JSONL.

## Phase 1 evolution

Phase 1 will migrate this to SQLite, then Postgres. The JSONL format is intentionally compatible — each line is a complete record.

Phase 4 will add an outcomes table for retrospective linkage.

## Concurrent access

Phase 0 assumes single-process CLI usage. No locking needed. Phase 1 will add file locking or move to SQLite.

## Acceptance tests

1. Running `simulate()` produces exactly one entry in `runs.jsonl`
2. Each prior used produces an entry in `priors.jsonl`
3. Each option in the result produces an entry in `predictions.jsonl`
4. All entries share the same `run_id`
5. JSONL files are valid (each line parses as JSON)
6. Running the same simulation twice produces two distinct run_ids

## Things to NOT do in Phase 0

- Do not use a real database (SQLite is Phase 1)
- Do not implement query interface (Phase 1)
- Do not add encryption at rest (Phase 1)
- Do not implement log rotation (Phase 1)
