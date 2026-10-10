# C1-W1 V2B POST-NATIVE documented collection-item TypeMeta inference FREEZE

Date: 2026-10-10. Independent branch `eeq-c1-w1-v2b-postnative-typemeta-copy-20261010`.
Parent forensic-only commit `0738d1b5346a037b1a3ea03a026d0303ea3f35c8`.
**THIS IS RETROSPECTIVE post-native diagnostic; original V1 native workflow run 38029036440 and its scientific gate FAILURE are permanent.** No additional Kubernetes API/native Pod scoring is authorized.

## Immutable evidence chronology

1. W1 V1 pre-native freeze: `01_C1_W1_FINAL_NATIVE_PRESCORE_MANIFEST.md`, commit `0378753912b2b311afd453773259f3668d22f776`, Git blob `b3134f5d537b1178af46f3ef21e36b21bdd30275`.
2. W1 V1 native run **38029036440** from commit `af8ea13452eaec52bed1a343443eeffad3fb53e3`, original result **FAILURE** of strict join scorer `REFUSE_COLLECTION_ITEM_SHAPE`. Native runner collected real 3/3 event messages, 8/8 unfiltered native raw LIST collection replies, two live WATCH channels and 3/3 native source mutations, 0 Pod outcomes.
3. Original raw native archive **11661372658**, ZIP SHA256 `9d2dc931d239f4a269da00038d322c5f795001afec8da22d3b311360740af94d`. Raw file SHA256 is authoritatively recorded in artifact internal `C1_W1_NATIVE_HASH_BEFORE_SOURCE_JOIN.txt`, which must independently verify without modification.
4. Before any shape normalization, the V2 read-only forensic protocol was separately frozen in `v2/00_V1_FAILURE_AND_V2_READONLY_SHAPE_FORENSICS_FREEZE.md` commit `363c485d58c3e330226919060c26acfbd4dd4c00`. Forensic-only CI [38029310544](https://github.com/MKLEE222/EEQ/actions/runs/38029310544) PASSED, 8/8 synthetic forensic tests, archive artifact **11662055398**, ZIP SHA256 `06c692afd8dbe674afd34cd77fe2d121948d1a6c3cff4b3063546351027d4cc2`.
5. Read-only forensic found exactly **16/16** observed native LIST items across **8** collection LIST responses have BOTH `kind` and `apiVersion` ABSENT at the item level. The enclosing collection List `kind` and `apiVersion` are present and correctly typed. No missing item name, UID, resourceVersion or spec; no wrong collection identity observed; 3 WATCH events archived. This cannot itself prove the method; it only identifies the post-native adapter boundary.

## One and ONLY one authorized V2b normalization

Operate on a completely NEW in-memory and serialized COPY of original V1 raw. Never alter original ZIP, original raw, original source-only predictions, original V1 verifier or original V1 scorer.

At exactly eight *original* raw collection LIST objects, for every LIST item:
- First verify raw collection `kind`, `apiVersion`, complete membership, nonempty collection `resourceVersion`, absent/empty `continue` and unfiltered exact native source-class API path.
- If `item.kind` is ABSENT (not present with null/empty/wrong value), infer exactly `ValidatingAdmissionPolicy` from `ValidatingAdmissionPolicyList` OR `ValidatingAdmissionPolicyBinding` from `ValidatingAdmissionPolicyBindingList`. If a present `kind` is wrong, REFUSE.
- If `item.apiVersion` is ABSENT, copy exactly verified collection `admissionregistration.k8s.io/v1`. If present but wrong, REFUSE.
- Before and after, UID/name/item `resourceVersion`, entire `spec`, original source membership and all other bytes/values must be identical; no object IDs invented or removed. The new copy changes ONLY the 32 previously ABSENT TypeMeta entries (16 `kind` + 16 `apiVersion`).
- **WATCH stream events are NEVER edited**, no extra events invented, no stream-gap/410/RBAC normalization; no action, source, timing or collection RV modified. The original V1 strict verifier and join scorer are reused at pinned Git blobs and run on the normalized copy. If they still fail, mark V2b failure (do not widen this version).

Synthetic post-native-shape normalized-copy anti-masking tests must separately reject: present wrong kind, present wrong API version, missing item UID/RV/spec, wrong collection kind, extra/duplicate/omitted items, tampered native WATCH event UID/type, changed old policy/binding semantics, wrong WATCH cursor, watch permission lost, changed denominator and forged global admission proof.

## Native and novelty ceiling

Even a 3/3 event, 8/8 LIST, 2/2 watch and 3/3 action retrospective pass yields ONLY `C1_W1_V2B_RETROSPECTIVE_SCOPED_PREFIX_FEASIBILITY_B9_TIE`.
- Original V1 scientific gate remains **FAILURE**.
- This does not establish cryptographically authenticated source inventory, global Kubernetes admission ACCEPT, atomic cross-kind state, unbounded NOW freshness, native 410 handling, independent B9 superiority, or P3 maintenance advantage.
- Fully informed B9 can use the same raw Kubernetes LIST/WATCH, standard TypeMeta interpretation and the exact same independent verifier.
- Kubernetes Reflector already handles this workflow as native prior art; source prefix correctness is not a novel EEQ operator.

Old original main G4/B10 frozen, G5=285 (increment zero), G6 global C1 disputed, G8 incomplete, fifth family holdout unopened. V1 raw source and fail status preserved forever.
