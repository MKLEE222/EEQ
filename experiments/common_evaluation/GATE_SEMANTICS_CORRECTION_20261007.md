# Gate-semantics correction note — 2026-10-07

Scope: status/disposition wording only.

Protocol authority remains unchanged:
`parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md` at
`c15b212ad0c2be3856a03d38802aaffa628aefd1`.

This note records a correction to later gate-status narration. It is **not** a
protocol amendment and changes no experimental result.

## Corrected distinction

The phrase `G6 CLOSED` had been used operationally to mean that G6 baseline,
omission and negative-control work had been executed or explicitly
dispositioned. That wording was too strong for a scientific gate.

The corrected status is:

- **G5 breadth: PASS** — four native families, 12 independent environments,
  seven public production/history sources, 285 deduplicated semantic cases.
- **G6 experimental obligations: dispositioned**.
- **G6 overall gate: NOT PASS**, because the intended GitHub development family
  retains `C1_COVERAGE_FAILURE` and therefore has no lawful family-complete
  governance representation / full baseline-omission interpretation.
- **X.509 holdout result: retained unchanged** — the sealed holdout produced
  7/7 frozen prediction matches, pre/post-native B10 identity, and zero
  adapter-schema or generic-core changes. Its result-level disposition
  `G7_HOLDOUT_SUCCESS` remains a valid description of that experiment.
- **Sequence narration:** the X.509 holdout must not be used to imply
  `G6 PASS -> G7 PASS` or to retroactively repair G6.
- **G8:** not started as an automatically authorized continuation of a clean
  G6/G7 gate progression. Further G8 execution requires explicit review of the
  original gate semantics while retaining the GitHub C1 failure.

## Files corrected

- `experiments/common_evaluation/G5_BREADTH_AUDIT_20261007.md`
- `experiments/common_evaluation/G6_GATE_DISPOSITION_20261007.md`
- `experiments/common_evaluation/PROTOCOL_EXPANSION_AUDIT_20261007.md`

## Files deliberately unchanged

- frozen G4 protocol and taxonomy;
- G5/G6 result artifacts and hashes;
- X.509 pre-native freeze;
- X.509 native holdout result;
- generic WFC compiler freeze;
- GitHub C1 evidence and negative-control results.

No score, label, case, representation, prediction or artifact hash is altered
by this correction.
