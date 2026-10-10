# R3-M3 V2 PRE-RUN CHANGE FREEZE — API RAW LIST INSTEAD OF FORMATTED KUBECTL LIST

Date: 2026-10-10.
New independent development branch after failed M3 v1 native run:
eeq-r3-m3-v2-raw-api-inventory-20261010.
Parent M3 v1 blocked artifact:
https://github.com/MKLEE222/EEQ/actions/runs/38027186154
and immutable disposition 03_M3_V1_NATIVE_LIST_VERSION_BLOCKER.md.

This is a prospectively frozen V2 repair, NOT rewriting failed V1 and
NOT a newly unseen holdout. V1 had 2 unbound controls, ZERO registered
primary Pod decisions, ZERO mutation actions and ZERO complete inventory
snapshots; no M3 primary decision labels were learned.

## Exact one authorized modification

Change only the source-inventory API collection reader inside
r3_m3_native_k8s.py:
  OLD: kubectl get validatingadmissionpolicies -o json;
       kubectl get validatingadmissionpolicybindings -o json.
  NEW: kubectl get --raw
       /apis/admissionregistration.k8s.io/v1/validatingadmissionpolicies;
       kubectl get --raw
       /apis/admissionregistration.k8s.io/v1/validatingadmissionpolicybindings.

Parse exact original JSON raw response; require metadata.resourceVersion
for BOTH complete native resource-list endpoints at all four phases.
Verify resource list .kind and .apiVersion are appropriate policy and
binding lists. Record and preserve list version opaque identity with
original entire policy/binding spec and item identity fields as before.
Use no previously observed policy outcomes or post-hoc labels.
The native source-only module, registered eight source JSON documents,
native four phases, three actions, two Pod probes, two controls, original
all eight source predictions and fair full-information B9 remain unchanged.
The V1 source artifact SHA256 d251df798e96eec0d1b4a39dd9b410678657fd025398f26c79cd277ccfd49f0e
is the ONLY eligible V2 prediction/source artifact.

A correctly exposed RAW LIST metadata resourceVersion is NOT proof of
global/continuous C1. Every LIST is scoped to one Kubernetes API source
class and point-in-time. No cross-resource atomicity or uninterrupted
watch from the snapshot is assumed. No numerical ordering of RV.
If RAW LIST lacks metadata.resourceVersion, FAIL CLOSED again.

## No-score and scientific gate chronology

1. Commit THIS protocol before changing any code or running a new cluster.
2. Change only the native source LIST reader, add small pre-native synthetic
   tests for raw list parser; preserve prior runtime/scorer/source semantics.
3. Re-run source-only 14 tests, scorer anti-masking 14 tests, new raw API
   parser tests, and assert unchanged SHA/artifact before Kind.
4. Pin EXACT native V2 modified code blob and all unaffected code blobs
   and original source artifact ZIP + internal manifest/prediction hashes
   in a new V2 final manifest before first V2 Kind.
5. Run same ONE clean Kind v1.35.0 cluster from scratch; 8 Pod native
   decisions, two controls, 3 membership changes, 4 full policy+binding
   raw API LIST source inventories. Archive raw before joining the
   frozen predictions.
6. All failed setups and ambiguous results kept with fixed denominator.
7. Full B9 receives same entire native policy/binding inventory and
   original source/actor contract. Its 8/8 tie if achieved is a serious
   negative for unique EEQ method advantage.

Potential outcome only:
R3_M3_V2_CONTROLLED_NATIVE_STALE_ACCEPT_INVENTORY_COLLISION_B9_TIE.
Never claim global G6/C1 closure, no novelty vs native list/watch,
possible-world inference or strong B9, no independent engineering
adaptation cost reduction.

Do NOT modify original v1 main, frozen G4, B10, 285-case G5, prior
holdouts, archived M1/M2 or failed V1 artifact. This is an explicit
infrastructure evidence acquisition repair, not scientific retuning.
