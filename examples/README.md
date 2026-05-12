# Examples

This directory contains canonical synthetic Clinical Decision Episode fixtures for local review and tests.

All fixtures are synthetic, non-PHI, advisory-only development artifacts. They are derived from `pdde_v0_3_first_principles_final/examples/hf_cde_stable.json` unless otherwise noted in each fixture's `local_context`.

| Fixture | Scenario Focus | Expected Public Behavior |
| --- | --- | --- |
| `hf_cde_stable.json` | stable baseline | validates and preserves the same baseline missing/unsupported/deferred items as the v0.3 source fixture |
| `hf_cde_low_egfr.json` | low eGFR | explicit eGFR gates block affected SGLT2 and MRA profiles |
| `hf_cde_high_k.json` | high potassium | explicit potassium gate blocks the MRA profile |
| `hf_cde_low_sbp.json` | low SBP | explicit SBP gate triggers admit/observe pressure |
| `hf_cde_no_followup.json` | no follow-up availability | explicit follow-up gate triggers admit/observe pressure |
| `hf_cde_prior_dka.json` | prior euglycemic DKA marker | explicit DKA-risk gate blocks the SGLT2 profile |
| `hf_cde_missing_labs.json` | missing eGFR, potassium, and oxygen requirement | missing inputs stay visible in gates, VOI, uncertainty, and profile status |

Use the canonical HF domain pack for these fixtures:

```bash
python -m pdde validate --cde examples/hf_cde_high_k.json --domain pdde_v0_3_first_principles_final/domain_packs/hf_ed_discharge/domain_pack.yaml
```
