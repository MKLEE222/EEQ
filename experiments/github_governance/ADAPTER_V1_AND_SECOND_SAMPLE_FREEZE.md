# GitHub governance adapter v1 and second-sample freeze

Frozen as a development-family instance extension under `parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md`. The G4 schema, core semantics, labels, exclusions, and fifth-family holdout remain unchanged. This document and `adapter_v1.py` must be committed before the second native sample runs.

## Source and counting

First native sample: Actions run 37270160203, artifact 11327648114, ZIP SHA256 `851ac6dce9070be3947010d9e889b4043fc2b58eb5343cb7939e5cac32a50541`. The 100 PR IDs in `FIRST_SAMPLE_IDS.json` are the only data carried into second-sample selection. No first-sample native label controls selection.

Second sample: the same four repositories, each with 25 open PRs. Query `state=open&sort=updated&direction=desc` in pages of 100 at execution time. Traverse the returned order and select the first 25 PR IDs absent from the frozen first-sample ID list for that repository. Archive every selection page, selected IDs, raw PR and governance evidence, timestamp, and hashes. Duplicates across mutable pages are skipped by ID. If fewer than 25 new PRs are available or any selection request fails, retain the failure and do not silently replace the repository.

The native label and non-scored states follow `GITHUB_NATIVE_ORACLE_PROTOCOL.md` exactly. Semantic counting uses the G4 signature, including the preregistered governance/qualification state, MERGE_PR action, continuation contract, and native vocabulary. PR count is never semantic-case count. Distinct PR IDs or SHAs alone do not establish distinct semantic cases. V1 records a hash of the raw lawful state for provenance, explicitly marks `g4_count_eligible=false`, and contributes zero cases to the 250-case threshold until C1 and semantic-equivalence normalization close.

## V0 + C1-C3 adapter inputs

- V0: PR base/head identity, public effective branch rules, public branch metadata, reviews, check-runs, combined status, commit verification, and rule source identities. The adapter never reads `mergeable`, `mergeable_state`, `native_label`, or a native decision field. The validation join reads native labels only after adapting each row.
- C1: preserve all effective merge-rule sources and parameters, legacy branch protection metadata, required check identities, review identities, and commit verification. Rules that cannot be completely evaluated are retained as unresolved predicates, never dropped.
- C2: distinguish review approval and signed-commit qualification from mere authentication. The latest submitted state per reviewer is used for the visible review-count lower bound. Required app identities remain attached to checks.
- C3: registered action is `MERGE_PR`; continuation is branch governance. V1 exposes the required check observations and rule parameters but has no lawful synthetic-merge-commit checks, code-owner graph, complete legacy branch-protection predicates, or bypass-actor evaluation. These are explicit unresolved predicates.

V1 predicts `NATIVE_BLOCKED` only when an ordinary merger lacks the visible required approval count or a required signed commit is explicitly unverified. It never predicts `NATIVE_ADMISSIBLE` from incomplete input. Missing or failed checks on the PR head do not prove a native blocker because GitHub may evaluate a synthetic merge commit. Remaining rows are `INSUFFICIENT_EVIDENCE_REFUSE`; this is an adapter coverage result, not a native label. Any wrong sufficient-blocker prediction is retained as a mismatch. V1 is an intentionally conservative frozen instance, and C1 closure must be assessed separately from native-label accuracy.

First-sample diagnostic after defining this rule: 100 collected, 74 scored native rows, 31 scored sufficient-blocker predictions, 31 matches, 0 mismatches, 50 adapter refusals across all 100 rows. This diagnostic is development evidence; it is not the second-sample result or a final method score.

## Frozen file identities before second-sample native execution

| File | SHA256 |
|---|---|
| `adapter_v1.py` | `86eff9f35f55c3b1f7b020a86e7809ede4f135be3f73606dc97c68c1ea0809ce` |
| `FIRST_SAMPLE_IDS.json` | `136dbe6cc62f740d16bf571d7defbf2eb218433e66fcfcc281d1c4b52d9d1d9e` |
| `collect_native_oracle.py` | `2995f53ee174cbde6890d9a2109fe7d7a042843ae713cff5c415defbfff84158` |

Any edit to these files after second-sample execution begins requires a new adapter version and retains the v1 result unchanged.
