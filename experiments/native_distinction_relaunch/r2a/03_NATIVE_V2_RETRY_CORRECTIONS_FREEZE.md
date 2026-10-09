# R2-A v2 Native Retry — Frozen schema/diagnostic corrections

Date: 2026-10-09, BEFORE native retry.

First native attempt 37900621767 failed without native A scoring.
Raw artifact 11602247238 ZIP SHA256
5fee6caafb7f7f27eab8c1d06d45775cbfb79579f9a993388d1176d698575063.

Previously recorded detailed cause in
02_NATIVE_V1_FAILURE_AND_SCHEMA_REPAIR_FREEZE.md:
all Pod challenges (including non-scoring activation probe) used an
invalid world token WORLD_GATE -> world_gate in metadata.name.
The native Kubernetes API rejected Pod names under RFC 1123,
resulting in NATIVE_ORACLE_AMBIGUOUS, and activation failure.
Native binding patch WAS successfully applied and confirmed by GET and
resourceVersion change 488 -> 499, but no R2-A decision result exists.

## Repair 1 — only native Pod name field (frozen BEFORE retry)

New versioned driver r2a_native_episode_v2.py, Git blob:
e38a94841a3005085fa2d3fc1bc044d73d6c1a08.
Old driver blob unchanged:
b0eed161c5591c89d20d9349b92d5a14857cb720.

Single line changes world-token formatting in Pod.metadata.name:
  world.lower() -> world.lower().replace('_','-').

A new no-native test, Git blob
9e55bace2a3c0ab76d5f3eea2310c76161f94645, asserts
RFC1123-compliant name for each world, phase and service account,
and byte-structural equality of all Pod fields EXCEPT metadata.name.
All policy, source, actor, group, label, condition, hypothesis,
evaluation/horizon and scoring fields are preserved.

## Repair 2 — preserve both independent worlds after infrastructure failure

The original GitHub Actions native step inherits shell -e from the runner.
Its line "set -uo pipefail" does NOT disable inherited -e. Thus a nonzero
first-world Python exit terminated the entire shell action BEFORE
WORLD_STANDBY, leaving only the WORLD_GATE failure artifact.

New v2 workflow explicitly calls "set +e" before the two-world native
execution loop, and restores -e only after both world JSONs have been
generated or synthesized with an explicit infrastructure-failure status.
This changes only how failures are retained, not any native decision.

The v2 workflow MUST retain all failed native episodes and not award
scientific success unless BOTH worlds are complete, two actual binding
patches and independent policy activations are demonstrated, and every
one of eight frozen admission challenges is correctly attributed.

## Unchanged frozen scientific inputs and comparator

R2-A source-only predictions: Actions 37900042227, artifact 11602065738,
outer SHA256:
6651d5a42615f1f6656f7dc8892369070dfad0a7be568c2ab4c3f1c759c82dc4,
inner JSON SHA256:
a8a504506236853949dc82da4acf35cc90e95349dae58d669028ebc8546d8dc5.

Original source mechanism freeze, eight exact source JSON files, policy
selector mutation, case IDs (world,phase,service_account), expected native
actions, strong-B9 tie, comparison scorer blob
20036bb05ebdf26bd72ddd43688af36a49209dd3,
and original G4 freeze MUST remain unchanged.

No original source-only predictions are regenerated. No native outcome is
used to select cases, policy rules, or exception attribution. Next negative
outcome, if any, remains a negative outcome; not a reason to silently
rewrite the frozen claim.
