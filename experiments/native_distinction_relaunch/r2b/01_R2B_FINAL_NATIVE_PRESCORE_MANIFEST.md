# R2B-v1 FINAL NATIVE PRESCORE MANIFEST — FROZEN BEFORE FIRST NATIVE RUN

Date: 2026-10-09
Study: EEQ native distinction necessity, controlled TUF B contrast.
Scientific scope: ONE controlled TUF family, B-side contract-relative
noncosmetic merges with negative controls. NOT R2 A, NOT R4 novelty,
not G4-v1 protocol amendment or new original G5 cases.

## Chronology and fixed sources

- R2B pre-SOURCE charter Git blob:
  48088bb30fd9ae07f518ccc287118a32c22d6f8b
  (committed at 2be161c570463f58e3cae526d634e3223e568c72)
- Stage I source-only full run 37904757921, commit
  1d7bbcb06adb529f2235cc4c9fdbe85c079874ed.
- Stage I artifact id **11604180918**, name
  eeq-r2b-source-only-frozen-fixtures.
- Exact outer source-only ZIP SHA256:
  e45b07f9e874ca6f96ab2141cce9c1425cc5362ba037f69cf9689bd41ac9fefc
- Independently emitted INTERNAL source manifest SHA256:
  a44a328b76a689873dca730f724899fe1c01ffdedd87df5df36b655f070954bc
- Independently emitted INTERNAL source predictions SHA256:
  c090726d0015a155df6dddf758154e189a8adf94e2c16943ddfa0531920f72ca
- Hash-only workflow run 37905117469, first native not invoked.
- Complete deterministic signed source/source prediction generator tests:
  10/10, all nine sources byte-for-byte reproducible.
- Pre-native join-only scorer anti-masking tests:
  9/9, workflow 37905224575, no native test invoked.

Source-only predicted expectations (frozen on Stage-I run):
  6 reachable trusted-root states from ONE common self-signed trust anchor,
  4 registered original SOURCE candidate actions, 24 one-step rows;
  8 source-crypto derived advances, 16 fixed-root keeps;
  6 * (1+4+16) = 126 registered length-0..2 trajectories;
  12 root-verifies-target-delegation negative controls;
  3 source-only quotient classes:
    {s2a,s2b}; {s3a,s3b}; {s4a,s4b};
  equal-class lawful merged state pairs = 3 (root-update only);
  target-role qualification differentiates a/b in each pair;
  strong fully informed version-only B9 achieves 24/24 in J_root;
  conventional Moore quotient with SAME state graph matches 3 classes.
  No method-specific superiority is anticipated or eligible for this score.

All keys are explicitly PUBLIC TEST-ONLY deterministic Ed25519 seeds
derived in stage-I generator. No production/private secrets or uncontrolled
source/label features. Sources are CONTROLLED_NATIVE, not production history.

## Exact code and dependencies

These Git blob identities MUST be asserted by workflow BEFORE native:
- source generator:
  d3318ad68ddbfe6e4c152257b70aaed1f4c53d8e
- source-only crypto tests:
  1e68525325c13c6e1c20ed8f1ad54167a2765ea2
- pre-source R2B design:
  48088bb30fd9ae07f518ccc287118a32c22d6f8b
- independent native checker, DOES NOT import predictor or read predictions:
  e86ca8aa3a0e1febea4f7931380e419c8343cfa8
- source/native join-only scorer:
  beaacd0257625d5046d8d3b5ead01a456f697fb4
- scorer 9 anti-masking tests:
  1b0e98575e856a706c0cec7b94e77b74bbfcfe18
- pre-existing independent source-only TUF RSA/Ed verification code:
  3ddd6458fe1c71b069e7adf7b21cc839c388265b
- tuf-js@3.0.1 exact package lock:
  9f9f135f7ff93489c32579aeb90ffb80d0db7e4a
- original v1 compiler (MUST NOT MODIFY):
  9a6bff7a2b8db73b86b6952c706852c92b1a4b1d
- original frozen G4 protocol:
  3eeaeeb828d2fcf7ec4487da06489fee3146c920

Runtime: ubuntu-24.04 / Node 22.16.0 / Python 3.11,
npm ci --ignore-scripts from pinned lock, no source code generation or
alteration inside the native job.

## Native procedure already fixed in source-freeze

Stage II restores original source-only artifact and checks ZIP + both
internal SHA256s BEFORE importing/running tuf-js.

The native checker receives ONLY:
  exact nine original signed controlled source blobs
  and their SOURCE_MANIFEST.json;
it must not read SOURCE_PREDICTIONS.json. It reconstructs six reachable
states from root-1-common by branch-specific native updates.

For each (state,action), execute from a newly initialized native root
store. Record result and full signed-root STATE ID, not just root version.
Run all 126 <=2 future action paths with a fresh native store per path.
Use native @tufjs/models Metadata.verifyDelegate for both authentic
targets-a and targets-b metadata under each of the six native root states.
Keep actual native exception classes and setup failures.

Only after native results have been written, invoke the separately frozen
join-only scorer against frozen predictions. Zero missing/duplicate rows
are permitted. Setup errors, MODEL_UNSUPPORTED and refused eligibility
do not count as correct predictions.

The native verifier result is scored as:
- complete exact source/native effect AND successor identity matches on
  all 24 cells;
- all 126 full native future traces match frozen source-derived traces;
- all 12 native targets-role qualification results match, with different
  valid source qualification in A and B branches;
- direct native trajectories of all registered words agree for each of
  the three B pairs; signed sources and targets qualification REALLY differ;
- strong B9 24/24 against same native observations;
- classical full-graph quotient achieves same partition;
- all negative results/mismatches and errors are retained in artifact,
  regardless of job exit code.

## Disposition

If all restricted native checks pass:
  R2B_CONTROLLED_TUF_CONTRACT_RELATIVE_B_FEASIBLE_B9_TIE
  (NOT R2_BIDIRECTIONAL_PASS, NOT R4, NOT paper novelty).
If any material native signature/source/transition/target mismatch:
  R2B_CONTROLLED_NATIVE_FAILURE with fixed denominators.
If setup / infrastructure blocked:
  R2B_NATIVE_SETUP_BLOCKED, do not recode as method success.

A remains unattempted, and controlled fixture results are not new
prospective native transfer. No G4-v1, original G5/G6/G7 or main changes.
