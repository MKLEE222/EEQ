# R3-M3 V2 FINAL PRESCORE MANIFEST — RAW API INVENTORY EVIDENCE

Date: 2026-10-10. Status: FROZEN PRIOR TO FIRST V2 KIND.
This is an explicitly VERSIONED SOURCE OBSERVATION REPAIR and does not
erase failed V1 run 38027186154 (0/8 scored main cases).
No policy/signature/decision effects were examined in v1 beyond 2
unbound controls, before native list resourceVersion blocker.

Pre-change version protocol:
  04_M3_V2_NATIVE_RAW_API_PRESCORE_FREEZE.md
  blob 2bb92dc8fd7c061df675c1a18cca17cceb66d556.
V1 native failure memo retained blob
  456848778e55504dbd5f6ea7446220a59731f37a.
Original pre-source scientific 8/2/3/4 case freeze blob
  ae756bd87bf2fe52090dab089edb16989ae3e6ed.
All original source and forecast hashes retain prior V1 status.

## Original immutable sources, predictions and SHA

Source-only run 38026874182 PASS 14/14,
artifact 11660256715 SHA256:
d251df798e96eec0d1b4a39dd9b410678657fd025398f26c79cd277ccfd49f0e.
Source manifest SHA256:
d502d56bea25491e83af70c23835488d649cdd481dc15b171211e3385f252b44.
Source-only frozen predictions SHA256:
232f652d841b2871c089e0703c6f79785e051094e006ba01d37444d9a7ccc1a2.
Independent hash validation workflow run 38026960589.
Original whole 8-case source prediction:
  T0 flux REJECT, default ACCEPT;
  T1 flux REJECT, default ACCEPT;
  T2 flux REJECT, default REJECT by NEW third policy;
  T3 flux REJECT, default ACCEPT.
No post-result changes to those cases or source bytes.

Original unchanged source-only model code blob
04a2876c2c7d1bcf7447d617c304174a0432b9f9,
source tests 7001ab6a7aa7121277accc3b4b4d7d77a514c6b6,
original source VAP and Binding third blobs
ae7ab92b2d15f7793ec41232752efc2c30ebf347 and
e2a774ee92c2af6411e1a516e48af4695f096088.
Unchanged join-only FULL B9 scorer blob
8b4a21f8da0cce15791ebf0c0c843f7afa0ac5b5,
original scorer tests blob 69f91dfc6d2c26b96fcbb41aa712ea33a15715cc.

V2 native adapter code blob **105168cf889b13f71326eceef884134d919ebc51**.
V2 raw API parser tests blob **c19779706b62b21af1e98f43a48001efc22c3e00**.
Exact pre-native 34 tests (14 source, 14 scorer, 6 RAW API):
workflow 38027372118, SUCCESS, no new Kind invocation.
Original G4 blob 3eeaeeb828d2fcf7ec4487da06489fee3146c920;
WFC v1 blob 9a6bff7a2b8db73b86b6952c706852c92b1a4b1d.
Original M1 six source files remain SHA-pinned by V1
01_M3_FINAL_NATIVE_PRESCORE_MANIFEST.md.

## V2 native execution fixed interpretation

Versioned one-change observation repair ONLY:
  List all ValidatingAdmissionPolicies via raw Kubernetes API:
  /apis/admissionregistration.k8s.io/v1/validatingadmissionpolicies;
  List all ValidatingAdmissionPolicyBindings via raw Kubernetes API:
  /apis/admissionregistration.k8s.io/v1/validatingadmissionpolicybindings.
Each must respond with original API kind, apiVersion and NONEMPTY
metadata.resourceVersion, preserved as opaque for EVERY snapshot.
No rewriting source model/semantics, no generic formatted kubectl-list.

One new Kind v0.31.0 / v1.35.0 node image pinned by V1 freeze.
Exactly 8 registered Pod server-dry-runs + 2 unbound controls,
3 real API create/binding-create/binding-delete actions and 4 native
whole-VAP-policy and binding LIST snapshots. No case selection.
The final join-only score requires all 8 effects/attributions match,
all 2 controls, 3 actions, 4 inventories with old binding UID/spec
and individual resourceVersions invariant across phases. Strong B9
gets all same LIVE policy/binding source LIST and CEL/selector bytes,
must be 8/8 to establish fair parity. Weak cached-old-only source
ablation anticipated 7/8 is diagnostic, not B9.

If raw LIST still has no valid resourceVersion, retain V2 INFRA_BLOCKED
with 0/8 or partial counted explicitly; NEVER switch to assumed
complete=true or static source inventory. Native raw archived BEFORE
reading predictions; V2 rerun is DEVELOPMENT repair, not unseen test.

Even V2 native 8/8 + B9 tie establishes only source-list-dependent
certificate staleness on a controlled carrier, not fresh continuous
LIST->WATCH witness, universal cross-resource C1, origin proof,
independent P3 cost, or novel general EEQ semantics.
Main/G4/B10/old v1 G5=285, R5 holdout and old results unchanged.
