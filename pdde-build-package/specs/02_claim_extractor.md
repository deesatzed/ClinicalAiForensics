# 02 — Claim Extractor

Workflow A only: extracts atomic clinical claims from a pasted AI clinical answer using Claude.

## Purpose

Convert messy clinical AI text into a structured list of `Claim` objects. Each Claim represents an atomic recommendation, contraindication, or assertion.

## Function signature

```python
def extract_claims(
    ai_answer_text: str,
    model: str = "claude-opus-4-7",
    max_retries: int = 2,
) -> list[Claim]:
    """
    Extract atomic clinical claims from a pasted AI clinical answer.

    Returns empty list on persistent extraction failure.
    Never raises; logs errors and continues so report generation isn't blocked.
    """
```

## Prompt

Use the prompt template in `prompts/claim_extraction.md`. Substitute the AI answer text. Use Anthropic API with:

- `model`: configurable via env var `PDDE_LLM_MODEL`, default `claude-opus-4-7`
- `temperature`: 0 (deterministic extraction)
- `max_tokens`: 2048
- Response format: JSON

## Self-consistency strategy

For Phase 0, do one extraction call. Phase 1 will add self-consistency via 3-call ensemble.

## Output schema

The LLM returns JSON conforming to:

```json
{
  "claims": [
    {
      "claim_id": "claim_001",
      "claim_text": "Verbatim or near-verbatim sentence from the answer",
      "action": "prescribe_or_adjust | start_or_continue | stop | avoid | consider | monitor | refer",
      "therapy": "Normalized therapy name (e.g., 'SGLT2 inhibitor', 'sotalol', 'loop diuretic')",
      "target_condition": "e.g., 'HFrEF', 'HFmrEF', 'ED post-diuresis discharge'",
      "setting": "e.g., 'ED discharge', 'outpatient', 'observation'",
      "intended_outcome": "e.g., 'prevent readmission', 'symptom control' (may be null)",
      "extraction_confidence": 0.85
    }
  ]
}
```

Parse this JSON, validate against the `Claim` Pydantic model, and return.

## Therapy normalization

Build a small mapping for Phase 0 to handle common synonyms:

```python
THERAPY_ALIASES = {
    "dapagliflozin": "SGLT2 inhibitor",
    "empagliflozin": "SGLT2 inhibitor",
    "sotagliflozin": "SGLT2 inhibitor",
    "sacubitril/valsartan": "ARNI",
    "sacubitril-valsartan": "ARNI",
    "entresto": "ARNI",
    "spironolactone": "MRA",
    "eplerenone": "MRA",
    "carvedilol": "evidence_based_beta_blocker",
    "metoprolol succinate": "evidence_based_beta_blocker",
    "bisoprolol": "evidence_based_beta_blocker",
    "sotalol": "sotalol",  # specifically not normalized to beta blocker
    "furosemide": "loop diuretic",
    "bumetanide": "loop diuretic",
    "torsemide": "loop diuretic",
    "digoxin": "digoxin",
    "liraglutide": "GLP-1 RA",
    "semaglutide": "GLP-1 RA",
    "tirzepatide": "GLP-1 RA",
}
```

Apply these post-extraction to normalize the `therapy` field. Document in code comment that this is a Phase 0 stopgap.

## Error handling

- If the LLM returns malformed JSON, retry up to `max_retries` times with a "repair this JSON" follow-up prompt
- If still malformed after retries, log and return empty list
- Never raise; report generation should proceed even with no claims extracted
- Log all LLM interactions (request, response, latency, tokens) to a structured log file

## Telemetry

For each extraction, log:

```python
{
    "timestamp": "...",
    "model": "claude-opus-4-7",
    "answer_length_chars": 2048,
    "claims_extracted": 7,
    "extraction_latency_ms": 3200,
    "input_tokens": 1100,
    "output_tokens": 850,
    "retries_used": 0,
    "success": True,
}
```

Phase 0 logs to a JSONL file `logs/extraction.jsonl`. Phase 1 will move to a proper log infrastructure.

## Acceptance tests

1. Extracts ≥3 distinct claims from `examples/adversarial_sotalol.txt`
2. Identifies sotalol therapy in at least one claim
3. Action field is one of the valid enum values for every claim
4. Returns empty list (not exception) when given empty string
5. Returns empty list when LLM is unreachable (mocked failure)
6. With `random_seed`-equivalent (temperature=0), repeated calls on same input return structurally similar results

## Things to NOT do in Phase 0

- Do not extract reasoning chains, just claims
- Do not attempt to resolve contradictions between claims
- Do not call multiple LLMs for ensemble (Phase 1)
- Do not implement semantic deduplication (Phase 1)
- Do not extract citations from the answer text (separate spec, Phase 1)
