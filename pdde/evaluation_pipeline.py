"""Direct CDE evaluation pipeline.

This module wires together the deterministic Phase 0 components. It preserves
component outputs as typed records and does not add clinical recommendations,
ranking formulas, narrative reports, or AI judgment.
"""

from __future__ import annotations

from pathlib import Path

from .cde_loader import load_cde
from .decision_profiler import assemble_decision_profiles
from .domain_pack_loader import load_domain_pack
from .input_models import ClinicalDecisionEpisode, DomainPack
from .monte_carlo_engine import DEFAULT_ITERATIONS, simulate_resolved_priors
from .pipeline_models import EvaluationPipelineResult
from .prior_resolver import resolve_priors
from .safety_gate_engine import evaluate_safety_gates
from .uncertainty_budget import evaluate_uncertainty_budget
from .value_of_information import evaluate_value_of_information


def run_evaluation_pipeline(
    *,
    cde_path: str | Path,
    domain_pack_path: str | Path,
    n_iterations: int = DEFAULT_ITERATIONS,
    random_seed: int | None = None,
) -> EvaluationPipelineResult:
    """Load CDE/domain-pack files and run the deterministic evaluation pipeline."""

    cde = load_cde(cde_path)
    domain_pack = load_domain_pack(domain_pack_path)
    return evaluate_cde(
        cde,
        domain_pack,
        n_iterations=n_iterations,
        random_seed=random_seed,
        cde_source=str(cde_path),
        domain_pack_source=str(domain_pack_path),
    )


def evaluate_cde(
    cde: ClinicalDecisionEpisode,
    domain_pack: DomainPack,
    *,
    n_iterations: int = DEFAULT_ITERATIONS,
    random_seed: int | None = None,
    cde_source: str | None = None,
    domain_pack_source: str | None = None,
) -> EvaluationPipelineResult:
    """Run already-built deterministic components over typed inputs."""

    safety_gates = evaluate_safety_gates(cde, domain_pack)
    prior_resolutions = resolve_priors(domain_pack, cde=cde)
    simulation = simulate_resolved_priors(
        prior_resolutions,
        n_iterations=n_iterations,
        random_seed=random_seed,
    )
    value_of_information = evaluate_value_of_information(
        cde,
        domain_pack,
        safety_gates=safety_gates,
    )
    uncertainty_budget = evaluate_uncertainty_budget(
        cde,
        domain_pack,
        safety_gates=safety_gates,
        prior_resolutions=prior_resolutions,
        simulation=simulation,
        value_of_information=value_of_information,
    )
    decision_profiles = assemble_decision_profiles(
        cde,
        domain_pack,
        safety_gates=safety_gates,
        prior_resolutions=prior_resolutions,
        simulation=simulation,
        uncertainty_budget=uncertainty_budget,
        value_of_information=value_of_information,
    )

    return EvaluationPipelineResult(
        cde_source=cde_source,
        domain_pack_source=domain_pack_source,
        n_iterations=n_iterations,
        random_seed=random_seed,
        cde=cde,
        domain_pack=domain_pack,
        safety_gates=safety_gates,
        prior_resolutions=prior_resolutions,
        simulation=simulation,
        value_of_information=value_of_information,
        uncertainty_budget=uncertainty_budget,
        decision_profiles=decision_profiles,
    )
