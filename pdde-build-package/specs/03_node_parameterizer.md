# 03 — Node Parameterizer

Maps an extracted `Claim` to the appropriate prior distribution(s) in the belief network.

## Purpose

For Workflow A: given a Claim extracted from an AI answer, find the matching `evidence_applicability.by_claim_type` entry in the YAML and return the prior. For claim types not present in the YAML, elicit a prior from the LLM with `provenance_class: llm_unverified`.

## Function signature

```python
def parameterize(
    claim: Claim,
    network: BeliefNetwork,
    model: str = "claude-opus-4-7",
) -> dict[str, Prior]:
    """
    Maps a Claim to its relevant priors in the belief network.

    Returns a dict mapping node names to Prior objects.
    For unknown claim types, returns LLM-elicited priors with explicit warnings.
    """
```

## Claim-to-node mapping

Build a lookup keyed by (action, therapy, target_condition) tuples:

```python
CLAIM_TO_NODE = {
    ("start_or_continue", "loop diuretic", "*"): "loop_diuretic_plan_after_diuresis",
    ("prescribe_or_adjust", "loop diuretic", "*"): "loop_diuretic_plan_after_diuresis",
    ("start_or_continue", "SGLT2 inhibitor", "HFrEF"): "sglt2_ed_discharge_initiation",
    ("start_or_continue", "SGLT2 inhibitor", "HFmrEF"): "sglt2_ed_discharge_initiation",
    ("start_or_continue", "MRA", "HFrEF"): "mra_ed_initiation",
    ("start_or_continue", "digoxin", "*"): "digoxin_acute_admission_prevention",
    ("start_or_continue", "GLP-1 RA", "HFrEF"): "glp1_hf_prevention",
    ("start_or_continue", "GLP-1 RA", "HFmrEF"): "glp1_hf_prevention",
    ("start_or_continue", "sotalol", "HFrEF"): "sotalol_as_hf_beta_blocker",
    ("start_or_continue", "evidence_based_beta_blocker", "*"): "bisoprolol_carvedilol_metoprolol_succinate_continuation",
    ("refer", "*", "HFrEF"): "early_followup_within_7_days",
}
```

The `"*"` represents wildcard match on that field.

## Lookup algorithm

```python
def find_node(claim: Claim, network: BeliefNetwork) -> str | None:
    """Find the matching node name for a claim, or None if no match."""
    # Try exact match
    key = (claim.action, claim.therapy, claim.target_condition)
    if key in CLAIM_TO_NODE:
        return CLAIM_TO_NODE[key]

    # Try wildcards
    for (action, therapy, condition), node in CLAIM_TO_NODE.items():
        if (claim.action == action or action == "*") and \
           (claim.therapy == therapy or therapy == "*") and \
           (claim.target_condition == condition or condition == "*"):
            return node

    return None
```

## LLM fallback for unknown claims

When `find_node` returns None, request an LLM-elicited prior:

```python
def elicit_prior_from_llm(claim: Claim, model: str) -> Prior:
    """
    Use Claude to estimate a prior for a claim not covered by the network.
    Returns a Prior with provenance_class=LLM_UNVERIFIED.
    """
```

Use the prompt template in `prompts/node_parameterization.md`. Substitute the claim. Use temperature=0.

LLM returns JSON like:

```json
{
  "distribution_type": "beta",
  "alpha": 6,
  "beta": 12,
  "rationale": "This claim represents [reasoning]. The Beta(6,12) reflects moderate skepticism given [reasons].",
  "estimated_class_equivalent": "class_IIb"
}
```

Construct the Prior:

```python
Prior(
    distribution_type="beta",
    parameters={"alpha": 6, "beta": 12},
    provenance_class=ProvenanceClass.LLM_UNVERIFIED,
    provenance_detail=f"LLM-elicited prior for claim not in network. Rationale: {rationale}",
    confidence_class=ConfidenceClass.LOW_UNVERIFIED,
    last_reviewed=None,
    warning="LLM-only prior; not formally elicited; do not use for clinical decisions",
)
```

## Output

A dict mapping node names to Priors used. This becomes part of the Monte Carlo input and is logged in `sample_metadata.priors_used`.

## Provenance tracking

Every Prior returned (whether from the YAML or LLM-elicited) must include:
- `provenance_class`
- `confidence_class`
- `warning` (if applicable)

These propagate to the report's provenance warning section.

## Acceptance tests

1. Claim with `therapy="sotalol", target_condition="HFrEF"` maps to `sotalol_as_hf_beta_blocker` node
2. Claim with `therapy="SGLT2 inhibitor", target_condition="HFrEF"` maps to `sglt2_ed_discharge_initiation`
3. Unknown claim (e.g., `therapy="newdrug", target_condition="unrelated"`) triggers LLM fallback
4. LLM-fallback prior has `provenance_class=LLM_UNVERIFIED` and `confidence_class=LOW_UNVERIFIED`
5. All returned Priors validate against the Pydantic model

## Things to NOT do in Phase 0

- Do not cache LLM-elicited priors across runs (Phase 1)
- Do not implement semantic similarity matching beyond exact + wildcard (Phase 1)
- Do not auto-update the YAML with LLM elicitations (Phase 2+; requires governance review)
