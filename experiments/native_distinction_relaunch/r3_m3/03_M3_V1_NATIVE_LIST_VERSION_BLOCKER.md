# R3-M3 v1 first native attempt — SOURCE-LIST VERSION EVIDENCE BLOCKED

Date: 2026-10-10. SCIENTIFIC STATUS: R3_M3_V1_NATIVE_NOT_SCORED.
Original registered 8 main cases / 2 controls / 3 membership changes /
4 policy+binding source LIST snapshots. NO core task label
or denominator has been modified.

## Immutable execution

Native CI first run:
https://github.com/MKLEE222/EEQ/actions/runs/38027186154
commit 8f9b483bcf1dda639882d3a91e2d656efd83f562.
Status: completed FAILURE.
Artifact 11660312314, ZIP SHA256
d2980423aa1ebd89a6ad705ce388920d5aedbfa4f468a05d0a1d4f147c136d9c.

Initial source-only 14/14 PASS, complete eight foreseen source labels,
SHA-verified original source-only artifact 11660256715.
Prenative synthetic scorer+source 28/28 PASS on run 38027088628.
A preceding test fixture SHA-alias test run 38027049226 failed;
fixed BEFORE this native run with no experimental source/model
changes and retained in chronology.

The first actual Kind native runner established fresh Kind and
two no-binding Pod controls (2 observed controls), but failed in
the FIRST policy/binding LIST version assertion:
  RuntimeError('K8S_NATIVE_LIST_RV_UNAVAILABLE').
The runner recorded:
  controls=2, inventories=0, mutations=0, primary cases=0,
  source_predictions_read=false.

Do not claim 0/8 scientific correctness. This is an inability to
establish the preregistered metadata.resourceVersion from the
kubectl get ValidatingAdmissionPolicies -o json LIST path,
not a native policy decision mismatch. It also does NOT verify the
third binding causal contrast; none of 8 new native Pod labels scored.

## Mechanism blocker

The precise source-closure claim REQUIRES a native-supported list
freshness interface. Merely counting binding names, preserving earlier
policy source hashes, or writing complete=true cannot substitute.
metadata.resourceVersion is an opaque version; absence is a hard
evidence block. An API raw LIST endpoint MAY expose collection RV
even when kubectl's formatted generic GET does not, but that is
untested until an independently versioned repair CI.

V1 remains frozen and failed; no reclassification, no post-hoc
case dropping. For V2 create a DIFFERENT experimental version with
a PRE-RUN freeze and explicitly changed native source observation
method: kubectl get --raw /apis/admissionregistration.k8s.io/v1/
validatingadmissionpolicies and analogous
validatingadmissionpolicybindings, requiring each LIST's real
metadata.resourceVersion. Keep all original eight source-predicted
decisions, original source bytes/hashes, frozen actors, three native
mutations, four snapshots and independent full B9 the SAME.

If even raw source inventory lacks a valid resourceVersion, fail closed
again and do not call C1 complete.

Reference Kubernetes API LIST/WATCH contracts:
https://kubernetes.io/docs/reference/using-api/api-concepts/
Source resourceVersions are client-opaque and no cross-resource
atomic snapshot is claimed.

Original EEQ main G4/B10/G5 285 untouched. No R4 P3 uniqueness
established. Native M3 V1 science classification INFRA_EVIDENCE_BLOCKED.
