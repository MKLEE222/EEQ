# R2A-v1 FINAL PRESCORE NATIVE KIND MANIFEST — IMMUTABLE BEFORE FIRST CLUSTER

Date: 2026-10-09. Status: FROZEN PRE-NATIVE.
Scope: two clean Kubernetes v1.35.0 clusters, one actual namespace label
UPDATE each, 8 primary native Pod decisions, 4 no-binding native controls.
This is a controlled native developmental A-contrast ONLY, not an EEQ
unique method claim and not new holdout.

## Freezes and SHA locks

- Original R2A full protocol + expected current/future contrast:
  00_K8S_DYNAMIC_A_PRESOURCE_FREEZE.md
  Git blob cd3b0abf649ff0071a724250fc21d06ecb60b1ba.
- Source-only exact 7 JSON Kubernetes source fixtures, 8 registered
  labels predicted without any kubectl/native cluster:
  Actions 37906108793 at commit
  aa5d4823d7958457630c54c0d00d86b088d72ce6.
- Stage-I source-only artifact ID **11604865804**,
  outer ZIP SHA256:
  84704d3e070bcc20543278c76166fedcdff2a73dcbe9762b7a2236c954a7a00e.
- Internally SHA-pinned source manifest:
  c9a5b954d3b3e93ebbe9e55fc1a26885dbcef6e241cc6c0c93af2159f8cb0efa.
- Internally SHA-pinned source predictions:
  c5a8050790648afe6d28c4c444ec0b256d1cca56e40b5404e4b24c55810765e1.
- Hash-only independent pre-native run 37906223965.
- Source-only tests 9/9 PASS, stage-I 37906108793.
- Join-only scorer anti-masking 9/9 PASS, run 37906496012,
  executed without any kubectl or native Kubernetes cluster.

## Exact Git blob pins for source, predictor, native runner, scorer

- Source-only predictor: ab20320e894312f94e1ebcc08b69734e0064be14
- Source-only tests: 2630b0a0559cc71158e4decc7123c38cc5feea27
- Native Kubernetes runner (never reads predictions):
  c0daf5b2765197049a9ee56a6d07d85701cdd89c
- Join-only scorer:
  9d5d4d207a20b681cd075a1194b3c156ea15fe17
- Scorer tests: bca2487a8eb87db5747d2fe221ae04a1c1aeddb4
- policy.json bf5b9f7a99e3cbd11713352e83be2a4e345a03fc
- binding-a.json 4dff26ab237254d7de45c2008d68dd03800b4346
- binding-b.json d78be9f01690f4c65b8bff78069dc1ed2aecdd2d
- namespace-before.json b998f3e99380e8a04e34629048724726a591dbc1
- pod-flux.json de2f62f788726ed90d5f76889fb33126850d770b
- pod-default.json 2dce4b8e5e69b9333d63e24885f94e5639b2d51a
- update-namespace-label.json 778c7a043daa2e3c5048a6cd5ed27b4563133368

Keep original frozen EEQ G4 protocol blob
3eeaeeb828d2fcf7ec4487da06489fee3146c920
and common WFC v1 compiler blob
9a6bff7a2b8db73b86b6952c706852c92b1a4b1d.

ANY changed Git blob invalidates this native version; record failure rather
than silently retuning. No original G5/G6/G7, old EEQ B10, main or fifth
family holdout may be changed.

## Exact source-only pre-native predictions

All registered CURRENT native Pod CREATE decisions (strict namespace):
 H_A flux: REJECT; H_A default: ACCEPT
 H_B flux: REJECT; H_B default: ACCEPT

Same future action in BOTH histories:
 kubectl label namespace eeq-r2a r2a.mode=relaxed --overwrite
must ACTUALLY change namespace resourceVersion and persisted native labels.

All registered FUTURE decisions after real action (relaxed namespace):
 H_A flux: REJECT; H_A default: ACCEPT
 H_B flux: ACCEPT; H_B default: ACCEPT

The only H_A/H_B difference is the exact VAP Binding namespaceSelector:
 A: {'r2a.team':'tenant'}
 B: {'r2a.team':'tenant', 'r2a.mode':'strict'}.
Same immutable policy, Pod source, namespace source, label action, version
and cluster image in two separate native environments.

Extra frozen NO_BINDING controls, two probes per fresh cluster:
 flux=ACCEPT, default=ACCEPT in both branches (4 total).
These identify unrelated admission errors, which never count as target
REJECT. Count 8 main rows even when deployment/timing failures occur;
classify such cases as NATIVE_AMBIGUOUS / INFRA_FAILURE rather than matches.

Fully informed B9 sees selectors, namespace labels, serviceAccountName and
CEL expression. It predicts all 8 labels, meaning NO EEQ-only accuracy
advantage. A selector-blind ablation intentionally predicts 7/8 and is a
mechanism diagnostic only, NOT the strong baseline.

## Native execution, no post-hoc retries

Fixed primary native:
- kind v0.31.0 binary SHA256
  eb244cbafcc157dff60cf68693c14c9a75c4e6e6fedaf9cd71c58117cb93e3fa
- Kubernetes v1.35.0 node image
  kindest/node:v1.35.0@sha256:452d707d4862f52530247495d180205e029056831160e22870e37e3f6c1ac31f
- kubectl matching server version v1.35.0, official SHA256 checksum fetched
  from dl.k8s.io and verified before installation;
- Ubuntu 24.04; Python3.11; all installed binaries version-printed.

For branch A: create new Kind cluster eeq-r2a-a, run code-pinned native
runner to completion, capture raw evidence and deletion logs, delete cluster.
For branch B: create a SECOND FRESH cluster eeq-r2a-b, same exact input
files and pin/version, run native once, capture raw evidence and delete.
Fail if clusters cannot be isolated or namespace identities not verified.
No use of old scored G5 5-Spot static adapter as new native test labels.

Within each branch:
1. Apply exact namespace source; confirm r2a.team=tenant and mode=strict;
2. create/confirm service accounts, native no-binding Pod dry-run controls;
3. apply one policy and exact branch binding, read API objects and compare;
4. fixed 10-second activation settling time, NOT an outcome-dependent retry;
5. observe CURRENT two Pod dry-runs ONCE each;
6. execute the exact namespace-label update ONCE and verify native
   resourceVersion change plus expected labels;
7. observe FUTURE two Pod dry-runs ONCE each;
8. save raw API responses, errors, native decisions and label transitions;
9. only AFTER both raw native branch outputs are saved, invoke the
   join-only scorer with frozen Stage-I source predictions.

A native REJECT counts only if the exact registered VAP
eeq-r2a-flux-deny / message EEQ_R2A_FLUX_SA_DENIED caused it.
A non-target rejection is NATIVE_ORACLE_AMBIGUOUS, not a method win.

## Success / failure and gate scope

Success = exactly 8/8 native decision matches, 4/4 no-binding
controls, 2/2 real native namespace updates and a true A separation:
current vectors both (REJECT,ACCEPT), future A (REJECT,ACCEPT) and
future B (ACCEPT,ACCEPT). Admit status
CONTROLLED_K8S_NATIVE_ACTION_INDUCED_A_SPLIT_B9_TIE.

Mismatches, wrong resourceVersion/labels, unexpected policy/binding, native
denial attribution error or incomplete branch are retained negative/native
infrastructure dispositions, never selectively retried to create success.

Even if successful:
- native A action-induced witness shown in ONE bounded Kubernetes carrier;
- prior TUF B shown in ONE different bounded TUF carrier;
- not native A+B demonstrated in both domains, no R2 universal PASS;
- strong B9 ties and independent unique EEQ gain R4 remains OPEN;
- original G5 still 285 and legacy protocol untouched.
