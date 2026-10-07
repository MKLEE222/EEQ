# GitHub v2 G6 matrix — final pre-scoring manifest

Date: 2026-10-07

Status: **FINAL PRE-MATRIX FREEZE**.

Protocol parent:
`parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md` at
`c15b212ad0c2be3856a03d38802aaffa628aefd1`.

GitHub v2 pre-native contract:
`c4f5defe530bae4cb134f49b0df07cd106cd3685`.

Third-sample native evidence is already collected. This is a development
post-native / pre-matrix freeze and is not represented as a holdout.

## Frozen inputs

| role | path / artifact | identity |
|---|---|---|
| representation semantics | `experiments/github_governance/GITHUB_V2_REPRESENTATION_FREEZE.md` | Git blob `47a5e3a0960266e829f6470c65b64a5036b53280` |
| representation/adapter builder | `experiments/github_governance/build_v2_g6_matrix.py` | Git blob `a4ed44d423c0044fd23d4245e54bac8f15624d07` |
| controlled admissible result | `experiments/github_governance/GITHUB_V2_CONTROLLED_ADMISSIBLE_RESULT.json` | Git blob `a1258be3ece940c906489d937303b360152de440` |
| generic compiler | `experiments/common_evaluation/compile_wfc_v1.py` | Git blob `9a6bff7a2b8db73b86b6952c706852c92b1a4b1d` |
| strict evaluator | `experiments/common_evaluation/evaluate_representations.py` | Git blob `545eb2f994796c8ef78134c4cbce9f131bab4d5d` |
| fresh third sample | Actions artifact `11495866260` | ZIP SHA256 `ff8435fbcba51e4839adc25160d4600a6a8187a05686c6b58ca9df8ffb25e64f` |

Generic compiler freeze commit remains:
`062be7f533977d45e879a8026a3034913d1a6a57`.

## Scoring population rule

The builder recomputes semantic equivalence from the frozen adapter state.

Include:
- third-sample rows with `PREDICTED_C1_COMPLETE` and a scored native label;
- the one frozen controlled admissible carrier.

No PR ID, head SHA or synthetic merge-commit SHA creates a semantic case.

Expected from the already frozen evidence is nine raw scored candidates and
nine unique semantic states, but the workflow must recompute this and fail on
any semantic-equivalence label conflict.

## Anti-label-tuning test

The workflow performs a label-permutation audit:
- swap every scored public native label
  `NATIVE_BLOCKED <-> NATIVE_ADMISSIBLE`;
- swap the controlled carrier's scored native label;
- rebuild semantic states, B0-B9/O1-O8 representations and eeq-adapter-v1
  rows;
- strip the attached `native_action` field;
- require byte-identical semantic IDs, representations and adapter payloads.

Any difference is a matrix-construction leakage failure.

## Success rule

A successful matrix requires:
- two native classes represented;
- every unique row has all B0-B10/O1-O8 IDs;
- unchanged generic WFC v1 compiles B10;
- B10 has zero mixed classes and zero conflict pairs;
- B10 oracle-optimal deterministic accuracy is 1.0;
- label-permutation audit passes;
- no adapter-schema or generic-core change.

Only after these checks may the GitHub v2 repair be considered complete enough
for a G6 gate reassessment. Broader GitHub v1 public-observability limitations
remain historical evidence and are not erased.
