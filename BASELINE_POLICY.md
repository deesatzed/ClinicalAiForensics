# Phase 0 Baseline And Artifact Policy

Last updated: 2026-05-12

## Baseline Identifier

The Phase 0 stable baseline is the annotated git tag:

```text
phase0-baseline
```

The tag points to commit:

```text
0662777 Initial PDDE Phase 0 scaffold
```

This tag identifies the Phase 0 advisory-only scaffold before Phase 1 activation. Phase 1 work should build on this baseline without rewriting the Phase 0 architecture or weakening safety, privacy, or provenance guardrails.

## Root Version-Control Strategy

The root workspace is a git repository on branch `main`.

Root remote:

```text
origin https://github.com/deesatzed/ClinicalAiForensics.git
```

The root repository owns:

- PDDE source code under `pdde/`.
- tests under `tests/`.
- project-control and reviewer documents.
- canonical source-material snapshots already present in this workspace.
- output directories via `.gitkeep` placeholders.

The root repository does not own generated Markdown reports or appendable JSONL logs by default.

## Supporting Codebase Strategy

`ClinSafer/` and `Agent_Pidgeon/` remain independent supporting codebases. The root repository tracks them as submodules rather than embedding their file contents.

Submodule URLs:

- `ClinSafer/` -> `https://github.com/deesatzed/ClinSafer.git`
- `Agent_Pidgeon/` -> `https://github.com/deesatzed/Agent_Pidgeon.git`

Use a submodule-aware checkout when the supporting source material is needed:

```bash
git clone --recurse-submodules https://github.com/deesatzed/ClinicalAiForensics.git
```

For an existing checkout:

```bash
git submodule update --init --recursive
```

Do not edit, reset, or repoint these submodules as part of PDDE runtime work unless a later task explicitly scopes that repository-boundary change.

## Generated Artifact Policy

Generated reports and logs are reproducible local artifacts, not root source-of-truth files.

Default policy:

- `reports/*.md` is ignored by git.
- `logs/*.jsonl` is ignored by git.
- `reports/.gitkeep` and `logs/.gitkeep` keep output directories present.
- canonical generated outputs should be regenerated from fixtures during verification.
- appendable logs may grow with repeated local runs and should not be used as stable test fixtures.

Regenerate the canonical report and provenance log with:

```bash
python -m pdde report \
  --cde pdde_v0_3_first_principles_final/examples/hf_cde_stable.json \
  --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml \
  --output reports/hf_cde_stable_report.md \
  --log logs/hf_cde_stable.jsonl \
  --iterations 5 \
  --seed 17
```

If a generated report or log must be shared externally, prefer one of these explicit archival paths:

- attach it to a release or review package outside normal source commits;
- store it under a clearly named archive path with date, fixture, seed, and iteration count;
- document why that generated artifact is being preserved.

Generated artifacts must not contain PHI. Provenance JSONL logs should remain status-only and avoid full raw case content, patient-state payloads, gate evidence strings, and raw simulation samples.

## Phase 1 Boundary

This policy activates Phase 1 process work only. It does not add runtime behavior, clinical logic, AI answer mapping, final recommendation language, hidden scoring, or deployment surface.

Phase 1 tasks must continue to preserve:

- advisory-only report language;
- explicit missing, unsupported, blocked, and deferred statuses;
- deterministic seeded simulation behavior;
- status-only JSONL provenance logs;
- the prohibition on PHI and production clinical use;
- the prohibition on LLM/AI clinical judgment unless a later scoped task explicitly allows it.
