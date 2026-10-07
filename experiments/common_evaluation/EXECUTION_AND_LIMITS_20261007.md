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

`build_case_ledger.py` validates all four ZIP SHA256 values before building case and execution ledgers. Its semantic signature excludes APT Suite/Version zero controls, native version replication, retries, machine identity, and PR identifiers. It retains every source execution and pre-exclusion. The current ledger has 685 execution rows, 679 scored native executions, and 247 deduplicated scored semantic cases: APT 144, Flux 10, GCS Fuse 14, Volcano 72, Bottlerocket 7. GitHub contributes zero to this count until its C1 coverage and semantic-equivalence rule close. G5 therefore remains open; the threshold is at least 250.

The evaluator runs all frozen B0–B10 and O1–O8 identifiers by semantic domain. It uses an oracle-optimal deterministic decoder, exact representation classes, lexicographic native-label tie-breaking, mixed-class histograms, conflict pairs, confusion matrices, false-accept/reject counts, and canonical byte costs. Structurally inapplicable cells carry reasons. The TUF B1–B10/O1–O8 cells are pending a pre-scoring adapter instance and should not be read as measured baselines. The B10 values for APT/K8s are an adapter-state pilot derived from frozen family mappings; the generic EEQ/WFC compiler has not yet been integrated. No KBS strength conclusion follows from this pilot.

| Saved result | SHA256 |
|---|---|
| `results/UNIFIED_CASE_LEDGER.json` | `1ca7bc1d800e5c1a2e1d4b4202f9c18ffb6c4d6a969a620608c93c9499b7d12b` |
| `results/G4_MATRIX_PILOT.json` | `38cabfa874a12834d51832fffd1e383af871d17424aaa238562674b1849bc7e6` |

## Execution bugs and corrections

1. The initial evaluator's caller could score repeated native executions as separate cases and silently omit absent baseline IDs. The integrated driver now requires unique semantic IDs and all 19 frozen matrix identifiers.
2. The initial evaluator allowed caller-defined tie order; G4 specifies lexicographic native-label order. The integrated evaluator enforces that rule and emits full confusion/mixed-class evidence.
3. The GitHub adapter initially treated absent required checks on the PR head as definitive blockers. GitHub may evaluate a synthetic merge commit. V1 retains HEAD checks but marks merge-commit check attribution unresolved, while predicting only visible sufficient review/signature blockers.
4. The first workflow draft used Windows worktree SHA256 values for two frozen files. Their committed LF Git blobs have different SHA256 values. The documentation and workflow were corrected before second-sample execution.

The second GitHub sample and integrated evaluator Actions results should be appended here only after their run IDs, conclusions, artifact IDs, and hashes are verified. G0–G8 closure and final strength assessment remain pending.
