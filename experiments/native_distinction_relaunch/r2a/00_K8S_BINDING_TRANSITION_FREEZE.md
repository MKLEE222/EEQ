# EEQ R2-A Kubernetes Native Binding-Update Distinction — Source Freeze

Date: 2026-10-09.
Parent: 0c4fc8d2fec3c88550abd5b24d65cfb9656c72b3.
Status: PRE-FIXTURE/SOURCE-ONLY FREEZE. NOT YET NATIVE SCORED.
Evidence class: CONTROLLED_NATIVE_DEVELOPMENT, not unseen holdout.

## Scientific purpose

Find two lawful native histories with the SAME outcomes on ALL current
registered admission challenges, but whose decisions diverge after the SAME
registered and ACTUALLY EXECUTED policy binding mutation. This tests
necessity of a source qualification distinction that only matters under
future policy changes. NO synthetic successor pointer may replace a real
Kubernetes API mutation.

This is NOT automatically an EEQ-specific advantage; a fully informed
domain-expert B9 with the same namespace labels and binding semantics
should also preserve the relevant distinction. Expect B9_TIE.

## Fixed public/native mechanism

Native system candidate: Kubernetes v1.35.0, single-node kindest/node image:
kindest/node:v1.35.0@sha256:452d707d4862f52530247495d180205e029056831160e22870e37e3f6c1ac31f
kind binary v0.31.0; binary SHA256:
eb244cbafcc157dff60cf68693c14c9a75c4e6e6fedaf9cd71c58117cb93e3fa.
kubectl client matched to pinned Kubernetes server version with upstream
published SHA256 check. Source structure follows Kubernetes documented VAP
and ValidatingAdmissionPolicyBinding v1 semantics.

One new test-only ValidatingAdmissionPolicy:
- name = eeq-r2a-flux-constraint
- match Pod CREATE, apiVersion v1, core apiGroup;
- failurePolicy = Fail;
- CEL validation: object.spec.serviceAccountName != 'flux';
- denial message = "EEQ_R2A_REGISTERED_FLUX_DENIAL".

One new test-only ValidatingAdmissionPolicyBinding:
- name = eeq-r2a-flux-binding
- policyName = eeq-r2a-flux-constraint
- validationActions = ["Deny"]
- initial namespaceSelector: matchLabels { "eeq.r2a/armed": "never" }
- future namespaceSelector: matchLabels { "eeq.r2a/armed": "gate" }
- ALL other binding fields unchanged.

Two independently enrolled namespace contexts, with the SAME bound
policy and initial binding state:
- WORLD_GATE: label eeq.r2a/armed=gate;
- WORLD_STANDBY: label eeq.r2a/armed=standby.

Pod CREATE request family is fixed:
- serviceAccountName = flux;
- serviceAccountName = default.
Both SAs must exist beforehand. Pod template must be schema-valid and
use registry.k8s.io/pause:3.10, restartPolicy Never.

Current challenge vector:
  (Pod CREATE flux, Pod CREATE default).
Registered future action:
  PATCH_BINDING_SELECTOR_TO_GATE
via actual Kubernetes API patch of ValidatingAdmissionPolicyBinding.
The same patch bytes and target binding object MUST be used for both
worlds. No selective targeting by WORLD ID in the future action.
Expected future challenge vector:
  WORLD_GATE = (REJECT, ACCEPT)
  WORLD_STANDBY = (ACCEPT, ACCEPT).
Expected current challenge vector for BOTH:
  (ACCEPT, ACCEPT).

These expectations are SOURCE-DERIVED from registered VAP/binding/namespace
labels and CEL semantics, before any native action/label. Any native
non-target admission rejection is NATIVE_ORACLE_AMBIGUOUS.

## Native independence and action evidence (future separate freeze)

Each world must execute as an independent native episode with an isolated
kind cluster, or else report SHARED_CLUSTER_LIMITATION, not full R2-A.
A native episode will:
1. create clean pinned kind cluster and namespace/SA sources;
2. install the frozen policy and INITIAL binding;
3. GET native policy/binding/namespace source records and hash them;
4. wait for initial binding state to be visible, then evaluate BOTH current
   dry-run Pod CREATE challenges;
5. issue the SAME actual binding update request; retain API response,
   resulting resourceVersion, GET of successor binding source and a
   rollout/activation diagnostic using a separate probe namespace;
6. evaluate BOTH future dry-run Pod CREATE challenges in same world,
   retaining raw stdout, stderr, attribution, request/response status and
   observable namespace/policy/binding state;
7. persist all native facts BEFORE matching source-only prediction JSON.

Two episode results and the raw mutation histories must be combined by
a join-only evaluator under separately frozen source/artifact/code hashes.
If policy convergence cannot be established using a non-scoring probe,
the output is POLICY_NOT_ACTIVE / SOURCE_UNSUPPORTED, not a match.

## Registered claims and limits

Horizon = 1 registered binding-patch action, followed by Pod CREATE
decision vector; no other cluster mutation claimed.

The current admission decision vector is equal across both worlds,
yet their lawfully readable namespace label differs. The binding
selector transition makes that distinction relevant to future admission.

Strong B9 baseline:
(store namespace labels + full policy/binding selector/actor + future
mutation semantics), with the SAME V0 information. It should predict both
outcome vectors exactly. No novelty claim based on beating an artificially
current-only B9; current-only omission is merely a diagnostic.

Negative controls:
- both current flux CREATEs admitted while selector == never;
- both current default CREATEs admitted;
- post-patch default CREATE admitted for both;
- WORLD_STANDBY flux remains admitted post-patch;
- wrong native source, inaccessible policy, runtime/Pod-schema failure
  or missing SA must be classified separately.

This experiment does not test a full Kubernetes admission inventory:
other admission controllers may exist and are not silently treated as
the target policy. Registration is LIMITED to the installed, exact
test-only VAP/binding/Pod/namespace scope. Namespaces and cluster episodes
are controlled, not production histories.

## Execution chronology and hard stops

Stage S: freeze sources, independently parse SOURCE JSON, compute predicted
decisions/qualification routes without kubectl/native calls. Archive exact
policy, both binding versions, namespace contexts and prediction SHA256.

Stage N: only after a NEW immutable prescore manifest pins exact source
artifact outer/inner SHA256, code Git blobs and native image/CLI versions,
run two controlled native episodes. Retain negative results as-is.

Scientific success = native source transition (not mock) plus pre/post
decision vectors above and independent mechanism attribution and source
audit. This is a CONTROLLED_NATIVE_A witness, not an R2 FULL PASS without
sufficient B evidence in required family and not H3 advantage over B9.

If admission convergence or selector mutation is not verified natively,
R2_A_NATIVE_NOT_ESTABLISHED. Never reselect labels, action or source
population based on observed native results.
