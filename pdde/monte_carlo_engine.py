"""Seeded Monte Carlo sampling for explicit resolved priors.

This module samples only priors that were already resolved by the deterministic
prior resolver. It does not map priors to clinical recommendations, infer
missing probabilities, or override deterministic safety gates.
"""

from __future__ import annotations

import numpy as np

from .component_models import (
    MonteCarloPriorSimulation,
    MonteCarloSimulationResult,
    PriorResolution,
    PriorResolutionSet,
)


DEFAULT_ITERATIONS = 10_000


def simulate_resolved_priors(
    prior_resolutions: PriorResolutionSet,
    *,
    n_iterations: int = DEFAULT_ITERATIONS,
    random_seed: int | None = None,
) -> MonteCarloSimulationResult:
    """Sample explicit numeric prior distributions with deterministic seeding."""

    if n_iterations < 1:
        raise ValueError("n_iterations must be >= 1")

    rng = np.random.default_rng(random_seed)
    simulations = [
        _simulate_prior(resolution, n_iterations=n_iterations, rng=rng)
        for resolution in prior_resolutions.resolutions
    ]
    return MonteCarloSimulationResult(
        cde_id=prior_resolutions.cde_id,
        domain_pack_id=prior_resolutions.domain_pack_id,
        n_iterations=n_iterations,
        random_seed=random_seed,
        prior_simulations=simulations,
    )


def _simulate_prior(
    resolution: PriorResolution,
    *,
    n_iterations: int,
    rng: np.random.Generator,
) -> MonteCarloPriorSimulation:
    if resolution.status != "resolved":
        return MonteCarloPriorSimulation(
            prior_id=resolution.prior_id,
            status=resolution.status,
            reason=f"prior was not sampled because resolution status is {resolution.status!r}: {resolution.reason}",
            source=resolution.source,
            distribution=resolution.distribution,
            parameters=resolution.parameters,
            provenance_class=resolution.provenance_class,
            normalized_provenance_class=resolution.normalized_provenance_class,
            confidence_class=resolution.confidence_class,
            calibration_status=resolution.calibration_status,
            warning=resolution.warning,
        )

    if resolution.distribution != "beta":
        return _unsupported_sample(
            resolution,
            reason=f"unsupported prior distribution {resolution.distribution!r}; only beta is supported",
        )

    parameters = resolution.parameters or {}
    alpha = parameters.get("alpha")
    beta = parameters.get("beta")
    if alpha is None or beta is None:
        return _unsupported_sample(
            resolution,
            reason="beta prior requires alpha and beta parameters",
        )
    if alpha <= 0 or beta <= 0:
        return _unsupported_sample(
            resolution,
            reason=f"beta prior parameters must be positive, got alpha={alpha!r}, beta={beta!r}",
        )

    samples = rng.beta(alpha, beta, size=n_iterations)
    return _sampled_simulation(resolution, samples)


def _unsupported_sample(resolution: PriorResolution, *, reason: str) -> MonteCarloPriorSimulation:
    return MonteCarloPriorSimulation(
        prior_id=resolution.prior_id,
        status="unsupported",
        reason=reason,
        source=resolution.source,
        distribution=resolution.distribution,
        parameters=resolution.parameters,
        provenance_class=resolution.provenance_class,
        normalized_provenance_class=resolution.normalized_provenance_class,
        confidence_class=resolution.confidence_class,
        calibration_status=resolution.calibration_status,
        warning=resolution.warning,
    )


def _sampled_simulation(
    resolution: PriorResolution,
    samples: np.ndarray,
) -> MonteCarloPriorSimulation:
    p5, median, p95 = np.percentile(samples, [5, 50, 95])
    minimum = float(np.min(samples))
    maximum = float(np.max(samples))
    sample_values = [float(sample) for sample in samples.tolist()]

    return MonteCarloPriorSimulation(
        prior_id=resolution.prior_id,
        status="sampled",
        reason=f"sampled beta prior {resolution.prior_id!r} from explicit resolved prior parameters",
        source=resolution.source,
        distribution=resolution.distribution,
        parameters=resolution.parameters,
        provenance_class=resolution.provenance_class,
        normalized_provenance_class=resolution.normalized_provenance_class,
        confidence_class=resolution.confidence_class,
        calibration_status=resolution.calibration_status,
        warning=resolution.warning,
        sample_count=len(sample_values),
        samples=sample_values,
        sample_mean=float(np.mean(samples)),
        sample_median=float(median),
        p5=float(p5),
        p95=float(p95),
        interval_width=float(p95 - p5),
        minimum=minimum,
        maximum=maximum,
    )
