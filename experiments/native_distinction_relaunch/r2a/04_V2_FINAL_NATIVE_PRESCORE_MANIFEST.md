# R2-A FINAL PRESCORE MANIFEST v2 — native input schema retry

Date: 2026-10-09, BEFORE native v2 retry.

Inherits ALL scientific scope/predictions/source and original
native pre-scoring assertions from immutable
01_FINAL_PRESCORE_MANIFEST.md (committed
4c52badcc139231247642a55f49c9b000b72d0f6).
No score predicted from the failed v1 native execution.

## Why a v2 workflow exists

First v1 native workflow Actions 37900621767 **FAIL**; archived artifact
11602247238 outer SHA256
5fee6caafb7f7f27eab8c1d06d45775cbfb79579f9a993388d1176d698575063.
Kind startup and exact binding PATCH were successful in WORLD_GATE
(resourceVersion 488 -> 499); Pod metadata.name contained an RFC1123-
invalid underscore world_gate, so all current admissions and probe
returned NATIVE_ORACLE_AMBIGUOUS. The script inherited bash -e, so the
WORLD_STANDBY cluster was not executed.
See 02_NATIVE_V1_FAILURE_AND_SCHEMA_REPAIR_FREEZE.md and
03_NATIVE_V2_RETRY_CORRECTIONS_FREEZE.md, both committed before retry.

## Only approved corrections

- New native driver r2a_native_episode_v2.py, Git blob
  e38a94841a3005085fa2d3fc1bc044d73d6c1a08
  (original native driver remains blob b0eed161c5591c89d20d9349b92d5a14857cb720).
- New static regression test test_native_pod_name_repair.py, Git blob
  9e55bace2a3c0ab76d5f3eea2310c76161f94645;
  checks valid DNS Pod names and exact equivalence of all other Pod
  fields across v1/v2 for ALL registered worlds, phases and identities.
- V2 GitHub Actions wrapper explicitly disables inherited shell -e
  during the two-world execution/cleanup loop, guarantees retention of
  both result JSONs and then runs the UNCHANGED scorer.

No scientific source, label, policy, binding selector, authorization,
horizon, native error attribution, observation count, or strong B9
comparator changes.

## Old exact pins remain mandatory

- Old G4 protocol blob:
  3eeaeeb828d2fcf7ec4487da06489fee3146c920
- Source-only predictions artifact:
  11602065738, ZIP SHA256
  6651d5a42615f1f6656f7dc8892369070dfad0a7be568c2ab4c3f1c759c82dc4
- Source-only predictions JSON SHA256:
  a8a504506236853949dc82da4acf35cc90e95349dae58d669028ebc8546d8dc5
- Source-only compiler Git blob:
  0f4441673ec3cae69cba4b7878f3789b7e60b8b9
- Original native evaluator (unchanged):
  20036bb05ebdf26bd72ddd43688af36a49209dd3
- Evaluator unit tests (unchanged):
  f77aac0f8e30030493e4b51421e720491eebbd28
- Exact source blobs (all eight) and pinned kind node image SHA
  remain those in 01_FINAL_PRESCORE_MANIFEST.md.

## Native scoring remains exactly the same as original pre-score

Two ISOLATED kind v1.35.0 clusters:
each creates registered policy/binding/namespace/SAs, runs
flux/default Pod CREATE dry-run CURRENT, executes the SAME real binding
PATCH selector never -> gate, independently verifies VAP policy
activation using a separate probe namespace, and runs two FUTURE
dry-run requests. Eight registered decisions plus two real source
mutations are evaluated.

Frozen prediction:
- CURRENT both worlds: flux ACCEPT, default ACCEPT.
- POST PATCH WORLD_GATE: flux REJECT from exact registered VAP;
  default ACCEPT.
- POST PATCH WORLD_STANDBY: flux ACCEPT, default ACCEPT.

Any missing activation, Pod schema invalid, wrong rejection attribution,
source mismatch or invalid source state = failure (NOT method success).

If v2 still fails, do NOT revise this manifest or the native outcome
categories. Preserve the result and perform only separately versioned,
mechanistically justified repair.
