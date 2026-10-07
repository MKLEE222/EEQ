# G4 integrated execution record, 2026-10-07

Experiment branch: `kbs-parityplus-integration-20261007`. The frozen G4 protocol remains at commit `c15b212ad0c2be3856a03d38802aaffa628aefd1`. The final fifth-family holdout remains unopened.

## Pinned native evidence

| Carrier | Actions run | Artifact ID | ZIP SHA256 | Ledger treatment |
|---|---:|---:|---|---|
| APT exhaustive | 37258974581 | 11324225958 | `177fc73578c602834d19d3842a5fb8b6cf9f46155e7d4007a45bb8a1611ff966` | 576 executions, 144 semantic states |
| K8s Flux/GCS Fuse, v1.34.3 | 37257828299 | 11323401781 | `49a7113823f01f35e92fa7f5ab37f3dfab939c6334774eca9e38c2005321a61c` | 30 rows, 24 scored and 6 pre-excluded |
| K8s Volcano, v1.34.3 | 37277445478 | 11330264652 | `cc92c8ff6feee4e68763107c2cf024f9725e19bcfefa3fff82ddbc1f6889e521` | 72 semantic states |
| Bottlerocket TUF root chain | 37560789986 | 11456204296 | `50a09cbd256f5e4b6f4941ad28a6a1c087da95f6f9b0d0479aaca454fea2f156` | 7 production-authored 1→2 through 7→8 transitions |

The Bottlerocket native operation is `tuf-js@3.0.1 TrustedMetadataStore.updateRoot`. The run verified all frozen root bytes 1..8 against the preregistered inventory and accepted seven adjacent transitions. Root 9 returned HTTP 403 at the frozen source boundary; it is not a native rejection case. All seven scored transitions have the same ACCEPT label, so this chain alone cannot measure error discrimination.

## Case ledger and matrix

`build_case_ledger.py` validates all four ZIP SHA256 values before building case and execution ledgers. Its semantic signature excludes APT Suite/Version zero controls, native version replication, retries, machine identity, and PR identifiers. It retains every source execution and pre-exclusion. The closed-family base ledger has 685 execution rows, 679 scored native executions, and 247 deduplicated scored semantic cases: APT 144, Flux 10, GCS Fuse 14, Volcano 72, Bottlerocket 7. `append_github_evidence.py` validates both GitHub artifact ZIPs, requires 25 PRs per repository and zero overlap, and appends all 200 PRs with native and adapter statuses. The all-family execution ledger has 885 rows; GitHub contributes zero G4-count-eligible cases until its C1 coverage and semantic-equivalence rule close. G5 therefore remains open; the threshold is at least 250.

The evaluator runs all frozen B0–B10 and O1–O8 identifiers by semantic domain. It uses an oracle-optimal deterministic decoder, exact representation classes, lexicographic native-label tie-breaking, mixed-class histograms, conflict pairs, confusion matrices, false-accept/reject counts, and canonical byte costs. Structurally inapplicable cells carry reasons. The TUF B1–B10/O1–O8 cells are pending a pre-scoring adapter instance and should not be read as measured baselines. The B10 values for APT/K8s are an adapter-state pilot derived from frozen family mappings; the generic EEQ/WFC compiler has not yet been integrated. No KBS strength conclusion follows from this pilot.

| Saved result | SHA256 |
|---|---|
| `results/UNIFIED_CASE_LEDGER.json` | `1ca7bc1d800e5c1a2e1d4b4202f9c18ffb6c4d6a969a620608c93c9499b7d12b` |
| `results/G4_MATRIX_PILOT.json` | `38cabfa874a12834d51832fffd1e383af871d17424aaa238562674b1849bc7e6` |
| `results/UNIFIED_CASE_LEDGER_ALL.json` | `07d9137e171d1372a372302e634578b4c78a67644f1b165388e1fe52ddba4ca5` |

Independent CI reconstruction: Actions run [37562434393](https://github.com/MKLEE222/EEQ/actions/runs/37562434393) succeeded at commit `1708b339666e1c25e6e467d5d55ac9e9fced1647`. Artifact 11457138352 has ZIP SHA256 `0d15973ae7edecbfcc27576ca09c600113a5e1de8c1f6339cc25b3209078db63`. It fetched all four pinned native ZIPs, verified their SHA256 values, regenerated the ledger and 19-column matrix, and byte-compared both JSON files against the committed results. The generated representation file SHA256 is `b11f32a549224a23d0ac05444fe29f37cb6872c4353e24d4874b6553299100e2`.

## Execution bugs and corrections

1. The initial evaluator's caller could score repeated native executions as separate cases and silently omit absent baseline IDs. The integrated driver now requires unique semantic IDs and all 19 frozen matrix identifiers.
2. The initial evaluator allowed caller-defined tie order; G4 specifies lexicographic native-label order. The integrated evaluator enforces that rule and emits full confusion/mixed-class evidence.
3. The GitHub adapter initially treated absent required checks on the PR head as definitive blockers. GitHub may evaluate a synthetic merge commit. V1 retains HEAD checks but marks merge-commit check attribution unresolved, while predicting only visible sufficient review/signature blockers.
4. The first workflow draft used Windows worktree SHA256 values for two frozen files. Their committed LF Git blobs have different SHA256 values. The documentation and workflow were corrected before second-sample execution.
5. Second-sample Actions run 37562434331 failed before collection because the default shallow checkout omitted the adapter-freeze ancestor commit, making `git merge-base --is-ancestor` invalid. The workflow now fetches full history. This was an infrastructure failure, not a native-oracle or adapter result.
6. The successful second-sample artifact's outer SHA256 manifest accidentally included its own file while that file was being written. Its self-entry is invalid; all 971 other entries verified against extracted bytes. A corrected manifest, omitting the self-entry, is committed at `experiments/github_governance/evidence/SECOND_SAMPLE_SHA256SUMS_CORRECTED.txt` with SHA256 `bca33de6121acb123468e7eaec96e5d78133d2d3e9216fdccde1992a57ad24ce`. The workflow now excludes the manifest file from its input list. This repair did not resample or alter v1 results.
7. `nodejs/node` PR 66546 reported 3,109 changed files. The collector's 20-page limit archived the first 2,000 and emitted collector status 206 for the file list. A separate source supplement recovered pages 21–30 (1,000 more files), checked that pages 1 and 20 match the frozen artifact, and checked that both PR head and base SHAs stayed identical through collection. The combined 3,000 filenames are unique. Page 31 returned zero files because GitHub's [REST file-list endpoint](https://docs.github.com/en/rest/pulls/pulls#list-pull-requests-files) caps responses at 3,000. The final 109 files remain unavailable through this endpoint, so this attribution source remains incomplete. The supplement manifest SHA256 is `65df2ff687c5668cdc806316f4e70503a76fedfaa1e33989b48d0d4dd725f56c`; the frozen v1 result and ledger row remain unchanged. The v1 adapter does not use changed-file contents to make its sufficient-blocker predictions.

## GitHub second mechanical sample

Actions run [37562674312](https://github.com/MKLEE222/EEQ/actions/runs/37562674312) succeeded at commit `96c60e0b5c2c568b51ce47fe15f8268644de93a9`, after adapter freeze commit `7db1d5310ff3ba8b320b51e9283a4a3129d10816`. Artifact 11458025511 has ZIP SHA256 `6c37a1c0766158be8f1224877d014a5911ae0c937a98a080482a9508435beb83`. The second sample selected 25 PRs from each of the four frozen repositories and had zero PR-ID overlap with the first sample. It contains 72 native-scored rows: 64 blocked and 8 admissible; 20 drafts, 2 conflicts, and 6 ambiguous states remain unscored. Frozen adapter v1 made 33 scored sufficient-blocker predictions, all 33 matched, with zero mismatches; it refused 47 of all 100 rows. The full validation JSON SHA256 is `e59904231b901e9c67ab52753c03bc9dfe52dc86ccb71f5ce9c13a568cb01a17`. The compact committed result includes the exact 100 selected PR IDs.

Across both GitHub samples, 146 native rows are scorable, and 64 adapter v1 predictions are scorable and matched. The remaining scored rows require fuller governance evidence or semantic mapping. The one incomplete changed-file source and unresolved C1 predicates prevent a family-level parity claim or G5 contribution. G0–G8 closure and final KBS strength assessment remain pending.
