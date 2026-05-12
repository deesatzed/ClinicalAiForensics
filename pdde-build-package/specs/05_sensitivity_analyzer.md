# 05 — Sensitivity Analyzer

Variance decomposition over Monte Carlo samples to identify which input variables drive uncertainty in the output.

## Purpose

For each decision option, identify the top input variables whose variation explains the most variance in the option's fitness distribution. Use this to populate the report's "best next data to collect" section and the tornado plot data.

## Function signature

```python
def analyze(
    simulation: SimulationResult,
    option_id: str | None = None,
) -> list[SensitivityAnalysis]:
    """
    For each option (or just the specified one), compute variance contributions.

    Returns a list of SensitivityAnalysis objects, one per option.
    Each contains ranked drivers and a best-next-data-to-collect list.
    """
```

## Method (Phase 0): Spearman rank correlation

For each input variable that was sampled, compute the Spearman rank correlation between that variable's sampled values and the option's fitness samples. Square the correlation to get a variance contribution proxy.

```python
import scipy.stats as stats
import numpy as np

def compute_variance_contribution(
    input_samples: np.ndarray,  # shape (n_iterations,)
    output_samples: np.ndarray,  # shape (n_iterations,)
) -> float:
    """Squared Spearman rank correlation as variance contribution proxy."""
    rho, _ = stats.spearmanr(input_samples, output_samples)
    return rho ** 2 if not np.isnan(rho) else 0.0
```

Note: this is an approximation, not true Sobol indices or PRCC. Phase 1 will upgrade to proper variance-based sensitivity if needed.

## Input variables to track

The Monte Carlo engine must log per-iteration values for these variables so the analyzer can correlate them:

- `evidence_applicability` (per claim type used)
- Each gate evaluation (sbp, egfr, potassium, volume_status, dka_risk, oral_intake) — present even if "missing"
- `local_executability`
- `monitoring_feasibility`
- Each `benefit_potential` component
- Each `harm_risk` component

These should be returned from `simulate()` in `SimulationResult.sample_metadata`.

## Ranking and reporting

For each option:

1. Compute variance contribution for every tracked variable
2. Sort by contribution descending
3. Take top 5 (or fewer if some are <2% contribution; threshold is configurable)
4. Construct `SensitivityDriver` objects with `rank` field

## "Best next data to collect" generation

For each top driver, map to a clinical action a clinician could take to reduce that uncertainty:

```python
DRIVER_TO_ACTION = {
    "egfr": "Verify current eGFR",
    "potassium": "Check current potassium",
    "sbp": "Verify post-diuresis blood pressure",
    "volume_status": "Reassess volume status (lung auscultation, JVP, edema)",
    "dka_risk": "Screen for euglycemic DKA risk factors (T1DM, ketosis, recent fasting)",
    "follow_up_reliability": "Confirm HF clinic appointment availability",
    "local_executability": "Verify local pathway (formulary, follow-up clinic, lab pathway)",
    "monitoring_feasibility": "Confirm BMP follow-up at 72h pathway",
    # ... etc for all tracked variables
}
```

Phase 0: hardcode this mapping. Phase 1: derive from YAML metadata.

## Output

```python
SensitivityAnalysis(
    option_id="discharge_add_sglt2",
    drivers=[
        SensitivityDriver(
            variable="follow_up_reliability",
            variance_contribution=0.24,
            rank=1,
        ),
        SensitivityDriver(
            variable="local_executability",
            variance_contribution=0.21,
            rank=2,
        ),
        # ...
    ],
    best_next_data_to_collect=[
        "Confirm HF clinic appointment availability",
        "Verify local pathway (formulary, follow-up clinic, lab pathway)",
        # ...
    ],
)
```

## Performance

Should complete in <1 second for 10K iterations × 15 input variables. NumPy/SciPy operations are fast; no optimization needed.

## Acceptance tests

1. Returns one `SensitivityAnalysis` per decision option (or for the specified option_id)
2. Each analysis has ≥1 driver with contribution >0
3. Drivers are sorted by contribution descending
4. `rank` field matches sort order (1-indexed)
5. For sample case, top driver for `discharge_add_sglt2` is in the set: {follow_up_reliability, local_executability, monitoring_feasibility, egfr}
6. Sum of variance contributions does not need to equal 1 (these are correlation-based, not true Sobol)

## Things to NOT do in Phase 0

- Do not implement Sobol indices (requires careful sampling design)
- Do not implement PRCC (Phase 1 if needed)
- Do not include interaction effects (Phase 2+)
- Do not visualize (tornado plot rendering is part of report generator)
