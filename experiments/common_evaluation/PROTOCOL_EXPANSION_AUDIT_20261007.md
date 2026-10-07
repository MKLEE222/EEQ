# EEQ parity+ completion-line expansion audit — 2026-10-07

Protocol authority:
- `parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md`
- freeze commit `c15b212ad0c2be3856a03d38802aaffa628aefd1`

This ledger restores the original completion line. Passing the >=250 semantic
case floor or the generic WFC development evaluation does **not** authorize
opening the final holdout or making a KBS-strength conclusion.

## Completion-line obligations

| Obligation | Current disposition | Evidence / gap |
|---|---|---|
| 4 heterogeneous native families: APT, Kubernetes, TUF, GitHub | **OPEN** | APT/Kubernetes/TUF have native evidence; GitHub has 64/64 sufficient-blocker matches but family-complete C1 is not established under the frozen public-evidence model. |
| >=8 independent environments | **PASS: 12** | Counted by distinct source/contract execution context, never by software-version replication: APT exhaustive, Debian stable, Ubuntu noble; Flux, GCS Fuse, Volcano, 5-Spot; Bottlerocket root chain; nodejs/node, microsoft/vscode, home-assistant/core, llvm/llvm-project. |
| >=6 real public production/history sources | **PASS: 7** | Conservative count excludes PUBLIC_MAINTAINED_CONFIG_NATIVE_REPLAY and version repeats: Debian stable snapshots, Ubuntu noble snapshots, Bottlerocket production-root history, and the four independent GitHub repository PR histories. |
| >=250 deduplicated semantic native cases | **PASS** | G5 result: 285 unique scored semantic cases; version replication does not inflate the count. |
| ~10 baseline families / full frozen B0-B10 taxonomy | **PARTIAL** | Full 19-ID matrices exist for several closed carriers, but GitHub cannot yet support a family-complete interpretation. |
| >=8 ablations / frozen O1-O8 | **PARTIAL** | O1-O8 are frozen and evaluated where structurally applicable on closed carriers; family-complete coverage is not yet established across all four intended native families. |
| >=2 protocol-negative controls per development family | **OPEN** | APT has Suite/Version zero-effect controls; Kubernetes has 5-Spot unscoped controls; TUF Section-7 invariant controls now pass 2/2 at run `37576522839` with byte changes and unchanged ACCEPT actions. GitHub still needs protocol-negative controls or a preregistered structural impossibility disposition. |
| robustness categories 1-10 | **OPEN** | No unified preregistered cross-family robustness matrix/results artifact closes all applicable categories. |
| synthetic scaling over sources/claims/actions/density/contracts/horizon | **OPEN** | No frozen scaling result currently closes Section 11. |
| downstream correction/audit task per family where feasible | **OPEN** | No unified downstream task result currently closes Section 8. |
| clean reproduction of the expanded suite | **OPEN** | Earlier CI reconstructions and the generic-WFC workflow are valuable partial evidence, but the final expanded suite has not yet been independently reconstructed end to end. |
| final unseen fifth-family holdout | **G7 SEALED** | Original ordering is G0-G4 prerequisites -> G5 breadth -> G6 baselines/omissions/negative controls -> G7 unseen fifth-family holdout -> G8 scaling/robustness/downstream/clean reproduction. Holdout stays unopened until G6 closes. |

## Already closed development facts

- G5 breadth floor: 285 deduplicated scored semantic cases.
- Generic WFC v1: one domain-agnostic compiler evaluated on all 285 closed
  development cases, with zero mixed classes/conflict pairs and oracle-optimal
  accuracy 1.0 in each closed domain.
- Generic compiler label-permutation leakage audit: PASS.
- TUF representation matrix: all 19 frozen B0-B10/O1-O8 identifiers present;
  production chain is all-ACCEPT and therefore is not discrimination evidence.
- GitHub v1: 64/64 scored sufficient-blocker predictions matched across two
  mechanical samples; this remains a partial-claim result, not family parity.

## Expansion discipline

1. Do not create semantic cases merely to satisfy a count already passed.
2. Do not reinterpret version repeats as new semantic cases.
3. Do not rename adversarial rejection tests as Section 7 negative controls.
4. Negative controls must change real bytes/metadata/history while preserving
   the frozen decision-relevant qualification/continuation relation.
5. Robustness predictions are frozen before native execution.
6. Synthetic scaling is separate from natural/native breadth and never inflates
   the native-case denominator.
7. GitHub missing public evidence is retained as C1 coverage limitation; 403 or
   unavailable actor data is never imputed as false.
8. G7 fifth-family holdout remains unopened until G6 closes. G8 scaling, robustness, downstream and clean reproduction follow G7 under the original gate ordering.

No KBS-strength conclusion follows until all original completion-line
obligations are closed.
