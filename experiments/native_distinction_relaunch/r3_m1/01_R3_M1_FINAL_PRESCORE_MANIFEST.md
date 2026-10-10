# R3-M1 FINAL PRESCORE FREEZE: two genuine native-binding support paths

Date: 2026-10-10
Status: **PRESCORE SEALED BEFORE ANY R3-M1 NATIVE OPERATION**.
Experiment branch: `eeq-r3-multibinding-controlled-20261010`.
Authority: `00_R3_M1_PRESOURCE_PRENATIVE_FREEZE.md` (Git blob `fa2b894e37b413038438fd596f29983390d116c9`) created at commit `3c5d846a0926a28c810fe09b9149b63bba928009`.
Historical original G4 commit `c15b212ad0c2be3856a03d38802aaffa628aefd1` and G4 Git blob `3eeaeeb828d2fcf7ec4487da06489fee3146c920` unchanged.
Historical generic WFC v1 Git blob `9a6bff7a2b8db73b86b6952c706852c92b1a4b1d` unchanged.

## Immutable Stage1 source-only evidence (produced before native)

GitHub Actions run `38018010171`, `SUCCESS`. Ten source-only tests passed, 12 source-only primary predictions/12 control expectations/4 real-update obligations registered, no native client invoked.
Source-only stage1 workflow commit `a4900ba0eac0efbb23fc8b3f8d2a0a6983b1a6f9`.

| Property | Frozen value |
|---|---|
| SOURCE capsule GitHub artifact ID | **11656908306** |
| Source-inner-ZIP file | `R3_M1_SOURCE_ONLY_CAPSULE.zip` |
| Source-inner-ZIP SHA256 | `5b3af48b42ac649a9949a4a5d5ba4709981466264afa1dd2e4f511e2452cad48` |
| Source-manifest JSON SHA256 | `822ee381d26dff290b3f3fbe89c545d9b84fcf704e86cf9355b7582a276f1b32` |
| Sealed PREDICTIONS capsule artifact ID | **11656568596** |
| Prediction-inner-ZIP file | `R3_M1_PREDICTIONS_CAPSULE.zip` |
| Prediction-inner-ZIP SHA256 | `8b1d59e702660c53d534c85bc26ee59eb22db098671f6eb32cde2c552c7020ec` |
| Source-only PREDICTIONS JSON SHA256 | `f90c0efd27d667f3d46cac9076b20ab51063a9782aeec823c65cafdcb80c4a84` |
| Separate pin-summary artifact ID | **11656943291** |

Stage1 source capsule does NOT contain predictions. Stage2 native runner may only download/use source capsule before BOTH native raw outcome files have been saved and hashed. Prediction capsule is fetched only in the final join-only scorer step AFTER native observation.

## Immutable source and code Git blob pins (the exact pinned content)

All paths relative to `experiments/native_distinction_relaunch/r3_m1/`.
| Path | Git blob SHA |
|---|---|
| `r3_m1_source_only.py` | `4357fcc69acc735cd78fc26558aa19debd5d1213` |
| `test_r3_m1_source_only.py` | `508c0516147445d57ee2ba18225a970f5bce4e5e` |
| `r3_m1_native_k8s.py` | `0d1e4ef5c3491f5eb5592dca7b50dc6c7a3877ea` |
| `r3_m1_join_only_scorer.py` | `afe8f5251b18a252d87f598b614a982d038dac3c` |
| `test_r3_m1_join_only_scorer.py` | `b367b8ef83e0df824a50c6b490b74599ef676eac` |
| `sources/policy.json` | `c22a8134447649d202a49b644ddb8485835c0fc2` |
| `sources/binding-team.json` | `2bc5a5706910196c5cd0631c4034ca3ccdbb890b` |
| `sources/binding-mode.json` | `357ef4bd582f47e2308f6e640307077bafe47b68` |
| `sources/namespace.json` | `428f16bc92ac27dec26b87ad24951113cf463922` |
| `sources/pod-flux.json` | `def429a28e90544d9f2274101b97950801e8d924` |
| `sources/pod-default.json` | `9f82b811c2c6154ed20e1145f926be1d45f2c1fc` |
| `sources/action-team.json` | `288da2227b2e6161cd711cae99e3fa47e38aa00d` |
| `sources/action-mode.json` | `9561ce22cbddd68dcda196eb87db7fa35a8db827` |

## Frozen native runner/scorer and source-value chronology

Scorer tests conducted BEFORE first native call. Final green GitHub Actions run **38018301050**, commit `6a53a550afd4e95796b8dcb9c2720d505f3b88ab`, 10/10 source-only unit tests + 15/15 synthetic scorer anti-masking tests, native runner/scorer Python compilation success. The original failed scorer test runs remain in GitHub Actions:
- `38018159968`: test fixture mutation leaked into subsequent synthetic tests, later corrected.
- `38018246582` / `38018256475`: scorer action-revision enhancement and expected error classification were out of sync, later corrected.
- `38018279359`: literal escaped newline typo in test, later corrected.
These failures produced **NO** native test labels, no source/prediction edits and cannot be called native method failures.

The Stage2 native exact runtime:
- Kind v0.31.0 binary SHA256 `eb244cbafcc157dff60cf68693c14c9a75c4e6e6fedaf9cd71c58117cb93e3fa`;
- Kubernetes kindest/node:v1.35.0 SHA256 `452d707d4862f52530247495d180205e029056831160e22870e37e3f6c1ac31f`;
- kubectl v1.35.0 vendor SHA256 verification;
- TWO independently created/destroyed Kind clusters, contexts checked not equal;
- after installing each isolated Binding, wait 10s fixed; after deleting each isolated binding, wait 10s fixed; after installing BOTH bindings, wait 10s fixed; after EACH of the 4 namespace-label mutations, wait 6s fixed. NO outcome-driven retry/reordering.
- exact allowed native actors/contract as pre-source freeze.

## Frozen scoring rules
Two action orders `TM` and `MT`, six main Pod CREATE decisions each: exact **12** primary denominator.
6 no-binding + per-binding isolated controls per order (2 unbound + 2 TEAM-only + 2 MODE-only): exact **12** controls.
2 real labeled namespace mutations per order with unchanged UID and updated resourceVersion and exact other labels: **4** actions.
Original SCOPE includes named source binding IDs, policy, Namespace/POD actor, native API branch context and a one-step effect within a two-action registered sequence; no other action can be selected after seeing native outcomes.
Expected main native vectors each order: `REJECT,ACCEPT` phase0; `REJECT,ACCEPT` phase1; `ACCEPT,ACCEPT` phase2.
Strong B9 with equal legal inputs should tie 12/12; conventional exact rule eval may tie. One-binding omission is diagnostic, not legitimate strongest baseline.
Raw native JSON MUST be written to disk before the scorer is permitted to read sealed predictions. The scorer must preserve all mismatches/ambiguities, failing controls, dropped cells, failed actions and resourceVersion/label inconsistencies, with explicit denominators. No post-outcome source/label reclassification.

Scientific status from a perfect score is at most `R3_M1_CONTROLLED_NATIVE_TWO_SUPPORT_PATHS_FEASIBLE_B9_TIE` in this **authored controlled carrier**. Neither cross-family generic extractor, H3 advantage, independent P3 maintainer work, original G6 global C1, G8, nor unseen R5 claims follow. Old v1 G5 stays 285.
