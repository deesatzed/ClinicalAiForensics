# 01 — Data Models

All structured data uses Pydantic v2 models. Define these in `pdde/models.py`.

## Provenance and confidence enums

```python
from enum import Enum

class ProvenanceClass(str, Enum):
    GUIDELINE_MAPPED = "guideline_mapped"
    TRIAL_PARSED = "trial_parsed"
    PANEL_ELICITED = "panel_elicited"
    LOCAL_OUTCOME = "local_outcome"
    PANEL_ELICITED_PENDING = "panel_elicited_pending"
    LLM_UNVERIFIED = "llm_unverified"

class ConfidenceClass(str, Enum):
    HIGH = "high"
    MODERATE_UNVERIFIED = "moderate_unverified"
    LOW_UNVERIFIED = "low_unverified"

class RuleStatus(str, Enum):
    DRAFT = "draft"
    VERIFIED = "verified"
    DEPRECATED = "deprecated"
    RETIRED = "retired"

class ProhibitedSeverity(str, Enum):
    UNSAFE_WRONG_INDICATION = "unsafe_wrong_indication"
    UNSUPPORTED = "unsupported"
    OVEREXTENDED = "overextended"
```

## Core models

### `Prior`

A probability distribution with mandatory provenance.

```python
class Prior(BaseModel):
    distribution_type: Literal["beta", "normal", "categorical", "composite_gate", "expected_harm", "expected_benefit"]
    parameters: dict[str, float | list[float]]  # e.g., {"alpha": 14, "beta": 5}
    provenance_class: ProvenanceClass
    provenance_detail: str
    confidence_class: ConfidenceClass
    last_reviewed: date | None
    warning: str | None = None  # surfaced in report
```

Validation rules:
- If `confidence_class` is `low_unverified` or `moderate_unverified`, `warning` must be non-null
- If `distribution_type == "beta"`, `parameters` must contain `alpha` and `beta`, both > 0

### `DecisionOption`

```python
class DecisionOption(BaseModel):
    id: str
    label: str
    requires: list[str] = []  # gate IDs that must be satisfied
```

### `ProhibitedRecommendation`

```python
class ProhibitedRecommendation(BaseModel):
    id: str
    description: str
    rationale: str
    severity: ProhibitedSeverity
    detection_pattern: str  # simple keyword AND/OR pattern for Phase 0
```

### `Gate`

```python
class Gate(BaseModel):
    name: str  # e.g., "egfr"
    action_ready: str | list[str]  # e.g., ">=25" or ["euvolemic", "improved"]
    caution: str | list[str] | None = None
    avoid: str | list[str]
    impact_when_missing: Literal["wide_distribution", "moderate_distribution", "wide_distribution_for_sglt2_only", "wide_distribution_for_mra_only"] = "moderate_distribution"
```

### `LocalRule`

```python
class LocalRule(BaseModel):
    value: str | list[str]
    status: RuleStatus
    owner: str
    verified_by: str | None = None
    verified_date: date | None = None
```

Validation: if `status == "verified"`, both `verified_by` and `verified_date` must be non-null.

### `BeliefNetwork`

```python
class BeliefNetwork(BaseModel):
    network_id: str
    domain: str
    version: str
    schema_version: str
    clinical_governance: ClinicalGovernance
    provenance_classes: dict[str, ProvenanceClassDef]
    guideline_mapping: dict[str, BetaParams]
    workflow_modes: list[WorkflowMode]
    decision_options: list[DecisionOption]
    prohibited_recommendations: list[ProhibitedRecommendation]
    nodes: dict[str, NetworkNode]
    computed_nodes: dict[str, ComputedNode]
    classification: dict[str, ClassificationRule]
    local_overlay: LocalOverlay
    simulation: SimulationParams
```

### `ClinicalCase`

```python
class ClinicalCase(BaseModel):
    case_id: str
    schema_version: str
    domain: str
    network_id: str  # must match the network being used
    case_description: str
    patient_context: dict  # flexible; varies by domain
    clinical_question: str
    ai_answer_to_evaluate: str | None = None
    workflow_mode: Literal["A_answer_adjudication", "B_decision_simulation"]
    notes: str | None = None
```

### `Claim`

Extracted from an AI clinical answer (Workflow A).

```python
class Claim(BaseModel):
    claim_id: str
    claim_text: str
    action: Literal["prescribe_or_adjust", "start_or_continue", "stop", "avoid", "consider", "monitor", "refer"]
    therapy: str  # normalized therapy name
    target_condition: str
    setting: str
    intended_outcome: str | None = None
    extraction_confidence: float  # 0-1
```

### `SimulationResult`

```python
class OptionPosterior(BaseModel):
    option_id: str
    samples: list[float]  # raw MC samples
    median: float
    p5: float  # 5th percentile
    p95: float  # 95th percentile
    interval_width: float  # p95 - p5
    category_probabilities: dict[str, float]  # action_ready, conditional, etc.
    classification: str  # the dominant category

class SimulationResult(BaseModel):
    case_id: str
    network_id: str
    network_version: str
    n_iterations: int
    random_seed: int | None
    timestamp: datetime
    per_option: list[OptionPosterior]
    sample_metadata: dict  # which priors were sampled, etc.
```

### `SensitivityAnalysis`

```python
class SensitivityDriver(BaseModel):
    variable: str
    variance_contribution: float  # 0-1
    rank: int

class SensitivityAnalysis(BaseModel):
    option_id: str  # which option this analysis is for
    drivers: list[SensitivityDriver]
    best_next_data_to_collect: list[str]
```

### `ProhibitedHit`

```python
class ProhibitedHit(BaseModel):
    prohibited_id: str
    matched_text: str  # the snippet that triggered
    severity: ProhibitedSeverity
    rationale: str
```

### `DecisionFitnessReport`

The full structured output that gets rendered to markdown.

```python
class DecisionFitnessReport(BaseModel):
    case_id: str
    network_id: str
    network_version: str
    workflow_mode: str
    generated_at: datetime
    provenance_warnings: list[str]  # populated if any prior is unverified
    executive_summary: str
    ranked_options: list[OptionPosterior]
    sensitivity_drivers: list[SensitivityDriver]
    claim_evaluations: list[ClaimEvaluation] | None = None  # Workflow A only
    patient_gates: list[GateEvaluation]
    local_overlay_status: list[LocalRuleStatus]
    prohibited_hits: list[ProhibitedHit]
    evidence_in_motion: list[str]
    defensible_conclusion: str
    non_negotiable_reminders: list[str]
```

## Validation philosophy

- Strict validation at module boundaries
- Use `model_validator` for cross-field constraints
- Raise `ValueError` early; don't propagate bad data
- Tests for every validation rule

## Acceptance tests for this module

1. Loading a Prior without `provenance_class` raises ValidationError
2. Loading a LocalRule with `status=verified` but `verified_by=None` raises ValidationError
3. Loading a Prior with `confidence_class=low_unverified` but no `warning` raises ValidationError
4. All models from `networks/hf_ed_discharge_v0.yaml` load without error
5. All models from `examples/sample_case_HF-001.json` load without error
