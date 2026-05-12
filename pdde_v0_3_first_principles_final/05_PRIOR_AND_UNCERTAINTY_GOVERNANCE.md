# Prior and Uncertainty Governance v0.3

## Central Warning

Monte Carlo simulation can create false precision. PDDE must never display precise probabilities without showing where they came from and how uncertain the priors are.

## Prior Classes

### Verified Classes

- guideline_mapped
- trial_parsed
- expert_panel_elicited
- local_outcome_calibrated

### Draft Classes

- draft_expert_policy
- llm_unverified

## Phase 0 Policy

Do not allow LLM-unverified priors.

Use policy priors only, visibly labeled as draft and uncalibrated.

## Required Prior Fields

```yaml
prior_id:
node_id:
distribution:
parameters:
provenance_class:
elicitation_method:
source_basis:
confidence_class:
review_status:
calibration_status:
owner:
last_reviewed:
```

## Uncertainty Budget

Every output interval must be accompanied by a budget:

```json
{
  "evidence_uncertainty": 0.20,
  "patient_context_uncertainty": 0.35,
  "local_execution_uncertainty": 0.15,
  "monitoring_uncertainty": 0.10,
  "harm_uncertainty": 0.10,
  "preference_feasibility_uncertainty": 0.05,
  "prior_quality_uncertainty": 0.05
}
```

The values do not have to be perfect in Phase 0, but the structure must exist.

## Calibration Targets

PDDE can be calibrated against:

1. expert defensibility labels,
2. clinician action distribution,
3. outcome anchors,
4. adverse event or near-miss review.

Each run must specify which target is pending or active.

## Language Rules

Use:

- uncertainty interval,
- draft prior,
- policy prior,
- calibration pending.

Avoid:

- true probability,
- validated risk,
- AI confidence,
- trust score,
- gold standard.
