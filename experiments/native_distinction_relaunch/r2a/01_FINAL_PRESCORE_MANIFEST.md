# R2-A FINAL PRE-NATIVE Kubernetes Two-Cluster Binding-Mutation Manifest

Date: 2026-10-09 (UTC+8).
Status: FROZEN BEFORE ANY R2-A NATIVE Kubernetes CLUSTER EXECUTION.
Evidence class = CONTROLLED_NATIVE_DEVELOPMENT, NOT production or transfer.

## Chronology

Original EEQ G4 freeze commit:
c15b212ad0c2be3856a03d38802aaffa628aefd1.
Original G4 protocol Git blob:
3eeaeeb828d2fcf7ec4487da06489fee3146c920.
Parent new-research branch:
0c4fc8d2fec3c88550abd5b24d65cfb9656c72b3.

First R2-A pre-fixture mechanism freeze:
7411a39943fbed5cb7998df2ad11ec3dcefe0306.
Source-only implementation/files subsequently committed; no R2-A native run
occurred before this manifest.

Pure source-only stage:
Actions 37900042227 at commit
ace961de98651ffd87c1e94ce21b72f0fb1bac9c:
9/9 source and tamper kill tests PASS, eight frozen predictions,
exact CURRENT equality + AFTER_BINDING_MUTATION divergence.
Artifact 11602065738 with OUTER ZIP SHA256:
6651d5a42615f1f6656f7dc8892369070dfad0a7be568c2ab4c3f1c759c82dc4.
Source-only prediction file:
R2A_PRE_NATIVE_PREDICTIONS.json, inner SHA256
a8a504506236853949dc82da4acf35cc90e95349dae58d669028ebc8546d8dc5.

Independent no-native hash/source verification and scorer unit tests:
Actions 37900351621 at commit
d3f76ca706cd82ecc4dbd3644f2ba4743992cee3,
9/9 scorer anti-masking tests PASS. All eight code-frozen source JSON
hashes match the SHA256 embedded in the source-only prediction file.

## Exact Git blob lock

- 00_K8S_BINDING_TRANSITION_FREEZE.md:
  7c05b18ae319ec6c4bd01094b6cbd4771b97583e
- source_only_predictor.py:
  0f4441673ec3cae69cba4b7878f3789b7e60b8b9
- test_source_only_predictor.py:
  cff50145894c09ffb3c3ded4ee031e74e6081a4c
- r2a_native_episode.py (no source predictor imported):
  b0eed161c5591c89d20d9349b92d5a14857cb720
- r2a_compare_native.py (join-only):
  20036bb05ebdf26bd72ddd43688af36a49209dd3
- test_r2a_compare_native.py:
  f77aac0f8e30030493e4b51421e720491eebbd28

Exact eight source blobs:
- source/policy.json:
  b921056a88ec407008ff193bc201d76f810ab4ee
- source/binding_initial.json:
  97f7ce2cd626a9bbc19b50453cbf57d6dc0f5423
- source/binding_after.json:
  35732333028e91c227995928f52a428db2a42a4e
- source/namespace_gate.json:
  973aeee2750fcde52a85795dbe9cb009ff2eed1f
- source/namespace_standby.json:
  39b6f9217858fd02858459df2163cda63737869e
- source/namespace_probe.json:
  3885d45c61747773a2568b7e6086e81fd9765818
- source/binding_mutation.json:
  2ad8738f2ff97fe911a17478eb56a86317e07862
- source/challenges.json:
  c92f327bedc4263b36bc18b3d3b5ebaf4ce7d91f

Any mismatch aborts BEFORE native cluster creation. These files and
their prescore interpretation CANNOT be changed after native execution.

## Frozen native environment

Two complete, independently created and then discarded KIND clusters
must be used, ONE per native world, with:
- Kubernetes v1.35.0;
- node image kindest/node:v1.35.0@
  sha256:452d707d4862f52530247495d180205e029056831160e22870e37e3f6c1ac31f
- pinned kind version v0.31.0; SHA256
  eb244cbafcc157dff60cf68693c14c9a75c4e6e6fedaf9cd71c58117cb93e3fa;
- exact kubectl v1.35.0 binary using upstream published checksum;
- Ubuntu 24.04 GitHub Actions host.

Native WORLD_GATE and WORLD_STANDBY are isolated episodes and must NOT
share policy/binding state or reuse one another's cluster.

## Exact native steps per world

1. In new cluster, apply exact registered namespace (gate or standby),
   independent gate-labelled probe namespace, policy and INITIAL binding;
   create flux serviceaccount and verify default SA present.
2. GET policy, binding and namespace from native API; retain resourceVersions
   and actual namespace selector. Initial selector MUST be "never".
3. Submit registered Pod CREATE dry-run for flux and default once each,
   retain native stdout/stderr/error attribution; predicted ACCEPT/ACCEPT
   for BOTH worlds.
4. Execute the same exact Kubernetes API PATCH of target
   ValidatingAdmissionPolicyBinding, with selector "gate". Retain API return
   code, resourceVersion change, exact post-patch selector from GET.
5. WAIT for actual policy enforcement propagation via a SEPARATE gate-labelled
   probe namespace, requiring attributed registered-policy rejection of
   a flux Pod CREATE. This probe is not an R2-A scored case.
6. Submit both frozen Pod CREATE dry-run challenges once after binding
   mutation. Predicted:
   - WORLD_GATE: (flux REJECT by exact VAP, default ACCEPT)
   - WORLD_STANDBY: (flux ACCEPT, default ACCEPT).
7. Record 8 total case outcomes, two actual binding mutations,
   complete sources and full metadata before any scoring join.
8. Join against the immutable source-only predictions artifact without
   running the predictor or inspecting native outcomes to change it.

Native attribution rule:
REJECT is counted only when server response includes BOTH the exact policy
name eeq-r2a-flux-constraint and registered denial
EEQ_R2A_REGISTERED_FLUX_DENIAL. Unrelated Pod schema, RBAC or admission
errors are NATIVE_ORACLE_AMBIGUOUS, never counted as a method match.

Any absent source record, missing patch resourceVersion change, failed
separate activation probe or missing case => no full R2-A scientific credit.

## Baseline, hypotheses and interpretation

Primary scientific hypothesis: two history contexts with CURRENT
(ACCEPT,ACCEPT) have the same present decisions but diverge under
the SAME actually executed binding update due their different
lawful namespace qualification source:
WORLD_GATE -> (REJECT,ACCEPT), WORLD_STANDBY -> (ACCEPT,ACCEPT).

The strong fully informed B9 is explicitly permitted namespace labels,
VAP CEL, binding selector, the exact patch source, and future decision
semantics. It is expected to predict the divergence as well:
**B9_TIE is frozen BEFORE scoring**.

A successful native experiment is a restricted **CONTROLLED_NATIVE_A**
demonstration, not standalone algorithm novelty or a general Kubernetes
admission source-coverage theorem. It is across a different native family
from the TUF R2-B proof, so it does NOT, by itself, satisfy the original
"bidirectional per-family" generality condition in R2–R4 protocol.
R4 original-method-independent benefit still OPEN.

No old G4-v1 compiler, G5 denominator, X.509 or in-toto result modified.
