# C1-W1 final prescore manifest — 2026-10-10

**FREEZE COMMITTED BEFORE FIRST C1-W1 NATIVE KIND EXECUTION.**
Scientific object: scoped Kubernetes source membership cursor custody; NOT 8/8 Pod accuracy, NOT global C1, NOT H3/P3 superiority.
Branch: `eeq-c1-w1-source-cursor-20261010`.
PRE-SOURCE scientific registry commit `16dae1e9db0f7e254077a7658594e055da0fb185`, Git blob `7ee66d69f208761f1040f0ebb0b825b9ded45f39`.
Historical R3-M3 latest outcome `33ad1fc790d15f6c705aa7bf0f9d833a2e6de5cd` includes a FAILED original v2 native/scorer gate and a separate retrospective 8/8 reconciliation; neither rewritten.

## Immutable pre-native evidence chronology

1. Source-only controlled event/membership forecasts sealed by native-free Actions [38028755755](https://github.com/MKLEE222/EEQ/actions/runs/38028755755), commit `2639d249894f07be3515336d3e0b78440585e63a`. **28/28** preregistered source+authority falsification tests PASSED (12 source-only +16 synthetic). Artifact ID **11660314996** `eeq-c1-w1-source-only-cursor-and-events`, Github Actions artifact outer ZIP SHA256 `202d392b01decf7e42d87429305d2b629ee8029ad91f8daa08afdf75068c1863`.
2. Inside SOURCE artifact: `SOURCE_MANIFEST.json` SHA256 `7dddf471c1c0fc53b388c47b32cebbb09caa5f0d8ca377567a9bf23dbc960304`; `SOURCE_EVENTS_ONLY.json` SHA256 `d97aa16cb8b33532e50767f4d452c58db8ac5f549dd8c1e467b01e3e16bfaffb`.
3. A later scope-hardening change required exact watch=1 request query with original opaque cursor and declared genuine WATCH transport; first intermediate CI `38028899235` FAILED because its fixtures lacked newly mandatory request-query metadata (no native calls). Subsequent code/test version fully passed.
4. **Final pre-native CI** run [38028957072](https://github.com/MKLEE222/EEQ/actions/runs/38028957072), commit `b26f3e23151fb85f9e6882d64d6c1d1f3d74dbe2`, **48/48** tests passed (12 source,16 falsifiers,10 transport parser,10 scorer anti-masking), runner and scorer Python compilation successful. No Kubernetes API calls yet; source-only predictions' bytes NEVER changed during those tests.

## Source and executable exact Git blob pins at pre-native green commit

| Path relative to `experiments/native_distinction_relaunch/c1_w1/` | Git blob SHA |
| --- | --- |
| `00_C1_W1_PRESOURCE_NATIVE_AND_EPISTEMIC_FREEZE.md` | `7ee66d69f208761f1040f0ebb0b825b9ded45f39` |
| `c1_w1_source_only.py` | `27ca6e9b8a530a2bf6339124560e5d0f746304d9` |
| `test_c1_w1_source_only.py` | `070dccbe440447c263b41f042f64b6d7a7a7c81c` |
| `c1_w1_scoped_evidence_verifier.py` | `5013a1a42a92d837cf54e4ca5d0c765d2277a0f4` |
| `test_c1_w1_scoped_evidence_verifier.py` | `c7565db967baf099a1d110f4ea327acf86f7a108` |
| `c1_w1_native_watch_capture.py` | `119d6c7bc9a249598c3549135a44722e2b6f8257` |
| `test_c1_w1_native_transport_prenative.py` | `2bd062d575321ce1fd3bd71ebe5ff5d2238b6650` |
| `c1_w1_join_only_scorer.py` | `b721e378de5406b66eaf7c9ef8f8cd30e77f7425` |
| `test_c1_w1_join_only_scorer.py` | `d6a0514516b09689f8e523c73bd384e3eb4fd7a9` |

Original source fixture blob pins (unaltered historical controlled development inputs):
- `r3_m1/sources/namespace.json` `428f16bc92ac27dec26b87ad24951113cf463922`
- `r3_m1/sources/policy.json` `c22a8134447649d202a49b644ddb8485835c0fc2`
- `r3_m1/sources/binding-team.json` `2bc5a5706910196c5cd0631c4034ca3ccdbb890b`
- `r3_m1/sources/binding-mode.json` `357ef4bd582f47e2308f6e640307077bafe47b68`
- `r3_m3/sources/policy-third.json` `ae7ab92b2d15f7793ec41232752efc2c30ebf347`
- `r3_m3/sources/binding-third.json` `e2a774ee92c2af6411e1a516e48af4695f096088`

Original G4 v1 blob `3eeaeeb828d2fcf7ec4487da06489fee3146c920`, original B10 WFC blob `9a6bff7a2b8db73b86b6952c706852c92b1a4b1d`, main commit `b5434ab1ad317e5121c88b632806880f903774db`; fifth family not opened; G5 original remains 285.

## Frozen primary native source observability denominator

Exactly **two native WATCH transport channels**, one for policy collection and one for binding collection, each using `watch=1`, `allowWatchBookmarks=true`, `timeoutSeconds=150`, `resourceVersion=` the exact independently observed opaque collection LIST RV. Only the registered raw unfiltered endpoints; no namespace selectors, field selectors, chunking/continue token. Actor's `list` and `watch` authz for BOTH source classes verified with `kubectl auth can-i` and actual native LIST/WATCH requests; does not prove that authorization never changes.

Exactly FOUR checkpoints with TWO independent raw LIST snapshots each (**8 LISTs**). Exactly THREE events:
A1 policy ADDED `eeq-r3-m3-default-deny`, A2 binding ADDED `eeq-r3-m3-binding-third`, A3 binding DELETED same source UID. Exactly 3 corresponding real `kubectl apply/apply/delete` mutation API calls, source fixture bytes pinned, every event's name/UID and documented spec tested against same-phase or prior-phase authoritative collection LIST identities.

Fixed 10s setup stabilization, 1s local kube-proxy bootstrap, 2s after watch connection before A1, 6s after each native mutation, 12s maximum additional event receipt cutoff per expected event; no retries or outcome-driven reordering. Native runner collects real HTTP WATCH event lines via localhost-only `kubectl proxy` using the same ephemeral kubeconfig actor; both original policy/binding substantive specs and native UIDs must remain stable, other newly observed sources cause explicit fail-closed REFUSE. Native run must output partial JSON even on source failure, and original complete zero/partial denominators remain.

**ZERO NEW POD DECISION SCORING**. This is a source-custody native study only, not a relabeling of M3 as new R3 correctness.
If native WATCH implementation cannot stream (e.g. proxy buffering, connection terminated, RBAC error, JSON framing, 410) record infra/authority failure and DO NOT re-run the same frozen trial to get a preferred answer. A new version must preregister any transport change, retaining failures.

## Absolute scientific ceiling and B9 fairness

Best allowed conclusion: `C1_W1_SCOPED_NATIVE_LIST_WATCH_FEASIBILITY_B9_TIE`. Per-kind WATCH-from-LIST event reconstruction is standard Kubernetes API / Reflector functionality, not H3 novelty. **Full B9** can use the very same actor, raw LIST, true WATCH, all source identities and exact evidence checker; it cannot lose by artificially withholding this tool. A watcher can fail by 410, access loss, or omission of source classes; a correct per-kind WATCH does NOT prove cross-kind atomic snapshots, absence of other admission sources, an unbounded freshness lease, or globally authorized CURRENT ACCEPT. All those claims MUST remain false in output.

If true event stream fails and fallback to raw LIST diff appears attractive, archive as FAILED, do not quietly substitute: a LIST diff is not actual event continuity.

The 16 synthetically registered gap/permission/scope refusals remain **synthetic** and do not count as real gap/410/RBAC native outcomes. Strong prior art includes Kubernetes Reflector, database provenance, possible-world certainty, XACML Indeterminate and established stream processors. P3 independent scored maintenance study unopened; original G6 global C1 disputed, G8 incomplete.
