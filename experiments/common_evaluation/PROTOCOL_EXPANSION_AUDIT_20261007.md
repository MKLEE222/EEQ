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
| ~10 baseline families / full frozen B0-B10 taxonomy | **G6 CLOSED** | Final 285-case strict matrix run `37577515052` reconstructs frozen B0-B9/O1-O8 and integrates generic WFC v1 as B10. GitHub family-complete matrix remains C1_COVERAGE_FAILURE and is not fabricated. |
| >=8 ablations / frozen O1-O8 | **G6 CLOSED** | O1-O8 are present on every 285-case matrix row and evaluated wherever structurally applicable; structural N/A cells retain frozen reasons. GitHub C1 coverage failure remains a separate retained limitation. |
| >=2 protocol-negative controls per development family | **G6 CLOSED** | APT Suite/Version controls agree for all 144 templates; Kubernetes 5-Spot has five unscoped ACCEPT controls; TUF invariant controls pass 2/2; GitHub controlled PR #2 body/title invariants pass 2/2 without changing head/base SHA. |
| robustness categories 1-10 | **G8 OPEN** | No unified preregistered cross-family robustness matrix/results artifact closes all applicable categories. |
| synthetic scaling over sources/claims/actions/density/contracts/horizon | **G8 OPEN** | No frozen scaling result currently closes Section 11. |
| downstream correction/audit task per family where feasible | **G8 OPEN** | No unified downstream task result currently closes Section 8. |
| clean reproduction of the expanded suite | **G8 OPEN** | Earlier CI reconstructions and the generic-WFC workflow are valuable partial evidence, but the final expanded suite including G7 has not yet been independently reconstructed end to end. |
| final unseen fifth-family holdout | **G7 PASS** | Sealed OpenSSL/X.509 holdout at freeze `9615663c...` scored 7/7 frozen predictions correctly in run `37579211753`; pre-native/post-native generic B10 identity PASS; zero schema/core changes. |

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
