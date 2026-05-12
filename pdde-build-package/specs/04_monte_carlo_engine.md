# 04 — Monte Carlo Engine

The probabilistic inference core. Pure NumPy for Phase 0; no PyMC, NumPyro, or pgmpy yet.

## Purpose

Given a `BeliefNetwork` and a `ClinicalCase`, produce posterior distributions over decision option fitness via Monte Carlo sampling.

## Function signature

```python
def simulate(
    network: BeliefNetwork,
    case: ClinicalCase,
    n_iterations: int = 10_000,
    random_seed: int | None = None,
) -> SimulationResult:
    ...
```

## Algorithm

```
For each Monte Carlo iteration i in 0..n_iterations:
    1. Sample evidence_applicability for relevant claim types
    2. Evaluate patient_eligibility gates against case patient_context
       - If gate is in "action_ready" range: contribute ~Beta(15, 3)
       - If gate is in "caution" range: contribute ~Beta(8, 8)
       - If gate is in "avoid" range: contribute ~Beta(2, 18)
       - If gate is missing: contribute wider distribution per impact_when_missing
    3. Sample local_executability from its prior distribution
    4. Sample monitoring_feasibility from its prior distribution
    5. Sample benefit_potential per component
    6. Sample harm_risk per component (probability × severity weighted)
    7. For each decision option:
        - Check `requires` gates; if any fail, fitness = 0 for this iteration
        - Otherwise compute decision_fitness using formula in computed_nodes:
            0.25 * evidence_applicability
            + 0.20 * patient_eligibility
            + 0.20 * local_executability
            + 0.15 * monitoring_feasibility
            + 0.20 * benefit_potential
            - harm_penalty
        - Clip to [0, 1]
        - Store sample

After all iterations:
    For each decision option:
        - median = percentile(samples, 50)
        - p5 = percentile(samples, 5)
        - p95 = percentile(samples, 95)
        - interval_width = p95 - p5
        - classify each sample (action_ready / conditional / needs_more_data / discouraged / unsafe)
        - compute category_probabilities = fraction of samples in each category
```

## Detail: gate evaluation

Each gate (sbp, egfr, potassium, volume_status, dka_risk, oral_intake) is evaluated against the case's `patient_context`.

```python
def evaluate_gate(gate: Gate, case_value: Any) -> str:
    """Returns 'action_ready', 'caution', 'avoid', or 'missing'."""
    if case_value is None:
        return "missing"
    # Parse threshold expressions like ">=100", "<90", etc.
    # Return appropriate status
```

For threshold expressions like `">=100"`:
```python
def parse_threshold(spec: str) -> Callable[[float], bool]:
    """Parse '>=100' or '90-99' into a predicate."""
```

For list-based gates like `["euvolemic", "improved"]`:
```python
def in_list(spec: list[str], value: str) -> bool:
    return value in spec
```

## Detail: missing-data handling

When a gate value is missing in the case:

| impact_when_missing | Behavior |
|---|---|
| `wide_distribution` | Sample from Beta(5, 5) — wide, mean 0.5 |
| `moderate_distribution` | Sample from Beta(8, 6) — slightly favorable |
| `wide_distribution_for_sglt2_only` | Apply wide only when scoring SGLT2 options |
| `wide_distribution_for_mra_only` | Apply wide only when scoring MRA options |

Missing data should *widen* intervals, never narrow them.

## Detail: sampling distributions

```python
import numpy as np

def sample_beta(alpha: float, beta: float, n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.beta(alpha, beta, size=n)

def sample_categorical(probs: list[float], n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.choice(len(probs), size=n, p=probs)
```

Use a single `numpy.random.Generator` instance throughout, seeded if `random_seed` is provided.

## Detail: classification per sample

For each sampled `decision_fitness` value, classify into one of five categories using thresholds from `network.classification`:

```python
def classify_sample(fitness: float, unsafe_prob: float, missing_gates: int, prohibited_hit: bool) -> str:
    if prohibited_hit or unsafe_prob >= 0.20:
        return "unsafe"
    if fitness >= 0.80 and unsafe_prob < 0.05:
        return "action_ready"
    if missing_gates >= 2:  # or interval_width > 0.30 at the aggregate level
        return "needs_more_data"
    if fitness >= 0.60:
        return "conditionally_defensible"
    if fitness < 0.40:
        return "discouraged"
    return "conditionally_defensible"  # fallback
```

Note: `interval_width > 0.30` is computed AFTER all samples; for the per-sample classification, use `missing_gates >= 2` as the proxy.

## Detail: harm penalty

For each harm component that applies to the option being scored:

```python
harm_penalty = 0
for component in harm_risk.components:
    if option_applies_to(option, component):
        p = sample_uniform(component.probability_range, n_samples)
        s = component.severity / 10.0  # normalize to [0, 1]
        harm_penalty += p * s
```

Cap `harm_penalty` at 0.5 to prevent total fitness destruction. Document this cap clearly.

## Output

```python
SimulationResult(
    case_id=case.case_id,
    network_id=network.network_id,
    network_version=network.version,
    n_iterations=n_iterations,
    random_seed=random_seed,
    timestamp=datetime.now(timezone.utc),
    per_option=[
        OptionPosterior(
            option_id="discharge_continue_gdmt",
            samples=samples_array.tolist(),
            median=...,
            p5=...,
            p95=...,
            interval_width=...,
            category_probabilities={
                "action_ready": 0.41,
                "conditionally_defensible": 0.49,
                "needs_more_data": 0.08,
                "discouraged": 0.0,
                "unsafe": 0.02,
            },
            classification="conditionally_defensible",
        ),
        # ... one per decision option
    ],
    sample_metadata={
        "priors_used": [...],
        "gates_evaluated": [...],
        "missing_gates": [...],
    },
)
```

## Reproducibility

If `random_seed` is provided, two runs with the same network and case must produce identical samples. Test this.

## Performance target

10,000 iterations on the HF sample case in <5 seconds on Apple M4. Use vectorized NumPy operations (sample all 10K iterations in one call, not in a Python loop).

## Things to NOT do in Phase 0

- Do not implement full Bayesian network propagation (no message passing, no junction trees)
- Do not implement variational inference
- Do not implement MCMC
- Do not introduce dependencies between nodes beyond the formula in `computed_nodes.decision_fitness`
- Do not add caching, persistence, or async

Phase 1 may add some of these. Phase 0 just samples and combines.

## Acceptance tests

1. `simulate(network, case)` returns a `SimulationResult` with exactly six `OptionPosterior` entries
2. Each `OptionPosterior.samples` has length `n_iterations`
3. Setting `random_seed=42` produces identical results across runs
4. Sample case produces non-zero fitness for `discharge_continue_gdmt` and zero or near-zero for `admit_or_observe`
5. Counterfactual: changing `egfr` from 45 to 15 in the case produces lower median fitness for `discharge_add_sglt2`
6. Counterfactual: setting `potassium` to 5.7 produces near-zero fitness for `discharge_add_mra`
7. Counterfactual: setting `sbp` to 86 raises `admit_or_observe` rank
8. 10K iterations completes in <5 seconds
