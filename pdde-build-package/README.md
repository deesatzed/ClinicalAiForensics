# PDDE — Probabilistic Defensible Decision Engine

**Build package for Claude Code.** v0.1 · 2026-05-11

## What this is

A complete specification + scaffold for building Phase 0 of PDDE, an AI-enhanced probabilistic expert system that evaluates AI-generated clinical recommendations by producing calibrated defensibility distributions over decision options rather than verdicts against a mythical gold standard.

## How to use this package

1. Drop the whole directory into a new repo
2. Open Claude Code in the repo root
3. Claude Code will read `CLAUDE.md` first and follow the build order
4. After ~2 weeks of solo effort or ~1 week with Claude Code, you should have a working CLI that produces a Decision Fitness Report from a sample HF case

## Package contents

```
pdde-build-package/
├── CLAUDE.md                 # READ FIRST — Claude Code entry point
├── README.md                 # This file
├── docs/
│   ├── master_plan.md        # Strategic plan, roadmap, risk register
│   ├── architecture.md       # 6-layer architecture detail
│   ├── non_negotiable_constraints.md   # The 10 inviolable design rules
│   ├── risk_register.md      # Risks to watch during build
│   └── glossary.md           # Clinical + technical terms
├── networks/
│   └── hf_ed_discharge_v0.yaml         # The belief network (clinical model)
├── examples/
│   ├── sample_case_HF-001.json         # Sample patient case
│   ├── sample_report_HF-001.md         # Target output report
│   ├── adversarial_sotalol.txt         # AI answer that should be flagged
│   └── adversarial_glp1.txt            # AI answer that should be flagged
├── specs/
│   ├── 01_data_models.md     # Pydantic schemas
│   ├── 02_claim_extractor.md # LLM-based claim extraction (Workflow A)
│   ├── 03_node_parameterizer.md
│   ├── 04_monte_carlo_engine.md
│   ├── 05_sensitivity_analyzer.md
│   ├── 06_report_generator.md
│   ├── 07_provenance_manager.md
│   └── 08_cli_runner.md
├── prompts/
│   ├── claim_extraction.md   # LLM prompt template
│   └── node_parameterization.md
├── tests/
│   ├── phase_0_acceptance.md # The 6 sharp Phase 0 tests
│   ├── adversarial_suite.md  # 10 categories × 1 case
│   └── unit_test_specs.md    # Per-component unit tests
└── build/
    ├── build_order.md        # Dependency-ordered task list
    ├── tech_stack.md         # Versions, deps, environment setup
    └── pyproject_template.toml
```

## Quick start (after build)

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Set Anthropic API key
export ANTHROPIC_API_KEY="..."

# Run on sample case (Workflow B — decision simulation)
python -m pdde run \
  --case examples/sample_case_HF-001.json \
  --network networks/hf_ed_discharge_v0.yaml \
  --output report.md

# Run on sample case with AI answer to adjudicate (Workflow A)
python -m pdde run \
  --case examples/sample_case_HF-001.json \
  --network networks/hf_ed_discharge_v0.yaml \
  --ai-answer examples/adversarial_sotalol.txt \
  --output report.md
```

## Project context

This is Phase 0 of a multi-phase effort. The full strategic plan, including Phases 1-6, publication strategy, and federation roadmap, is in `docs/master_plan.md`. Read it once for context, then ignore it during the build — focus on `CLAUDE.md` and the specs.

## Important constraints

- **No PHI.** All sample data is synthetic.
- **No clinical deployment.** v0 is a development artifact, not a clinical tool.
- **No vendor ranking as primary artifact.** This project evaluates AI clinical answers; it is not a competitive benchmark.
- **Provenance is mandatory.** Every probability has a source dossier.

## Author

Wayne A. Satz, MD · Clinical Informatics

## License

TBD (suggest MIT or Apache-2.0 for the codebase; CC-BY for the belief networks and prompts)
