# R2-B FINAL Prescore Manifest: Noncosmetic Signed Targets Authority

Date: 2026-10-09 (UTC+8).
Status: FROZEN BEFORE ANY CONTROLLED R2-B NATIVE TUF ORACLE EXECUTION.

This manifest LOCKS the exact original controlled signed source bytes and
source-only future predictions. No action/claim/prefix/source, native scorer
or strong baseline may be changed after inspecting native outcomes.

## 1. Historical isolation

Parent relaunch branch commit:
0c4fc8d2fec3c88550abd5b24d65cfb9656c72b3.
Original G4 freeze:
c15b212ad0c2be3856a03d38802aaffa628aefd1.
G4 frozen document Git blob:
3eeaeeb828d2fcf7ec4487da06489fee3146c920.

New work is CONTROLLED_NATIVE development, not a production history,
independent transfer holdout, revised original G5 or G6 score. X.509 and
selected in-toto remained untouched.

## 2. Stage-S source-only predictions (committed before any native data)

Protocol/source-generation freeze commit:
266e2aa9bb9e16de900ee319117fbf4fe0d5bd38.

Source-only CI run: 37898538285 at exact Git commit
31bea2410fed394bd66fa0867d38b45d11fb2969.
Result: 8/8 source-only tests PASS, 6 signed public-source files,
14 source-only prefix states (2 anchors × 7 prefixes), a root-update
source-only equivalence claim, and a **predeclared strong B9 tie**.

Source-only artifact: 11601537119 (eeq-r2b-controlled-source-only).
OUTER ZIP SHA256:
ca60eafb405a3ad5617eb409d1c90195909e31dd30c22bbbf25928ea7b4f169a.

Independent pin-only run: 37898667182 (NO native execution).
Inside artifact files:
- R2B_PRE_NATIVE_PREDICTIONS.json:
  SHA256 0ad5e3b462dc43876b3934c48e5cd59c6d06fb8945f10c230290541d84485f2c
- sources/SOURCE_MANIFEST.json:
  SHA256 fea2ea4b47fec6afc75f24f279cadc44399fc7a5e6a4373963a6f30376aefdd2
- sources/anchor_a.root.json:
  SHA256 3b3d1d54688b7ba54998dcc9fc57f6e923d3a87989c8082908ca1f89f4205772
- sources/anchor_b.root.json:
  SHA256 54918e55524626443805e8a58bc023ee95dbbb69f23dd9842fb12cf7e04cbf28
- sources/candidate_2.root.json:
  SHA256 f54ff20687f21117db56896a631e2480b926a79a29761cb0eed12c9c3337052b
- sources/candidate_3.root.json:
  SHA256 5ecff5506e5223d48bb110757a83c0f5527b733396f5e90dd40755e8c5de10a7
- sources/targets_a.targets.json:
  SHA256 35bf1772b974ef20451ed642679c31af203267e88d1c77d6f8758c27503852b8
- sources/targets_b.targets.json:
  SHA256 8d0df11744d31e3d37e17fea6725808f37bb5416128e0d277c56ce0d27c556c1

All controlled test-key derivations are deterministic, public,
non-production and included in frozen source generator. NO production
private keys are used.

## 3. Exact code Git blobs (HARD CI ABORT ON ANY DIFFERENCE)

- Pre-source freeze:
  4baaafcc0f42cb721aa2b9c06327d3f4cf397e28
- Source generator:
  3abcbf481b8789c814d1feeeb1ef05aa355b3864
- Source-only predictor:
  786a04132acbcb39070426b4d504a23abf1fcbee
- Source-only adversarial tests:
  fb952319d25ecf6fb623ed556c72f072f9f18866
- Referenced R1b-v3 source cryptography:
  3ddd6458fe1c71b069e7adf7b21cc839c388265b
- Independent native TUF oracle (NO predictor import):
  bea0ef3b71a94beca7b061418aff0ec038f5d842
- Frozen join-only comparison scorer:
  570e8ca11b0f2d0864c721b80af1b54a8bdc3eca
- Scorer anti-masking tests:
  ed24942155b40023d1d8610dca60205593345d93
- Native tuf-js@3.0.1 package-lock:
  9f9f135f7ff93489c32579aeb90ffb80d0db7e4a

Separate pre-native scorer synthetic kill-loop:
37899022644 FAIL due Python import path, no native execution.
Corrected run: 37899219528 PASS, 10/10 scorer anti-masking tests,
confirming mismatches, wrong successor, bad targets authorization and
missing cases are not silently credited.

## 4. Exact registered controlled native experiment

Environment: Ubuntu 24.04, Node 22.16.0, tuf-js@3.0.1 via pinned npm ci.
Source anchors: A and B, both root version 1, same root-role signing
authority but distinct valid targets-role signer identities.

Registered candidate actions (ORDER FROZEN):
  submit-candidate-2, submit-candidate-3.

Horizon r=2 and all action prefixes:
  [], [2], [3], [2,2], [2,3], [3,2], [3,3].

Expected SOURCE-only outcome claims (not native fact yet):
1. both initial native anchors self-signature valid;
2. targets-A document verifies under root-A, not root-B;
   targets-B verifies under root-B, not root-A;
3. native root-update outcome vector and post-trust-root state match
   the SOURCE PREDICTION for all 14 (anchor,prefix) cells times 2
   challenges = 28 native root-update challenge observations;
4. both anchors' complete registered future root-update observations
   agree at every one of 7 prefixes;
5. root-only contract decision quotient legally merges A and B;
6. strong domain-specific B9 and exact classical quotient do the SAME,
   with no independent EEQ novelty established.

All 28 root-update challenges must be attempted with independent fresh
TrustedMetadataStore instances seeded with the respective frozen anchor.
Separately check 2x2 = 4 role authorization challenges with native
Metadata.verifyDelegate(targets); note this does NOT constitute the
full TUF target-role update with timestamp/snapshot verification.

Store all raw results *before* joining predictions:
- native ACCEPT, REJECT, NATIVE_ERROR, SETUP_FAILURE separately;
- actual post-action signed-root hash/version, not just label;
- authority claim outcome/error class for each signed targets file;
- source SHA, all prefix attempt outcomes, decision times.
Any test failure / unsupported source counts in complete denominator.

IMPORTANT: Some software errors are not native rejections. The native
checker recognizes only BadVersionError and UnsignedMetadataError as
registered root-proposal REJECT; all other native exceptions are
NATIVE_ERROR. No post-hoc exception class relaxation.

## 5. Hard disposition and limits

A 28/28 root-update and 4/4 authority match plus seven complete equal
continuation traces -> CONTROLLED_NATIVE_B_CONFIRMED_B9_TIE.
This is an R2-B proof-of-feasibility **only**. It does not demonstrate
future-only A, a general family theorem, a nontrivial superior algorithm,
minimal representation cost, or a new holdout.

If native mismatches, code behavior, source bytes or qualification differ,
retain B_REJECTED or MODEL_UNSUPPORTED; do NOT rerun source generator
with new keys or change the observation family after seeing outcomes.

No original G4-v1 protocol or scoring artifact is to be altered.
