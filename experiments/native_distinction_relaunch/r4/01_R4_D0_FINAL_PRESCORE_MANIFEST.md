# R4-D0 FINAL TUF NATIVE PRESCORE MANIFEST — IMMUTABLE BEFORE ANY NATIVE D0 ACTION

Date: 2026-10-09. Status: FROZEN BEFORE FIRST R4-D0 NATIVE CALL.

## Protocol scope and preexisting facts

Source problem: 00_R4_D0_TUF_AUTHORITY_PRESOURCE_FREEZE.md, Git blob
19344e1913c29d266d1876e812d19d13a5f728d3,
first committed at 809ede9abd6d70eedc2ab2162b2a92f8f54f963e.
It defines 2 valid root-version-2 trusted histories, 4 candidate
root-version-3 updates with the SAME signed payload but different genuine
crypto signer envelopes, exactly 8 cell predictions. The two root2
histories are each cryptographically reachable from the SAME root1 anchor.

This is a TEST OF VERSION-ONLY SUFFICIENCY, not the substantive R4 P3
adaptation advantage. Full-source B9 is permitted every signature/key,
authorization rule and source byte; it is expected to attain 8/8.

## Source generation and source artifact frozen BEFORE native

Independent source-only Actions run 37914129494 at exact commit
51aade6f3877ead6872b6ea47f33e63668c4256a.
All 12/12 source-only semantic/cryptographic kill tests PASS.
Seven unique public-test-only Ed25519 signed TUF source JSON documents,
byte-for-byte repeatable and hashed.

Source-only artifact ID 11608811184, named
eeq-r4-d0-source-only-signed-authority;
exact outer GitHub Actions ZIP SHA256:
2490380d7424bc7f86216cfeb691ab0c90e8a412d65ff1a3887db3aec135a26d.

Source-only manifest (inside ZIP at sources/SOURCE_MANIFEST.json)
SHA256: 268e9244b57ca7c0a305434be3085d02e4d02d4085bf419bffb6f84045c7736a.
Source-only predictions (inside ZIP at sources/SOURCE_PREDICTIONS.json)
SHA256: fa8dd5a40667dea0acd9984d2d5ab0c33ea2148cef314fbc9751df34805d8aa0.

Both internal source SHA256s independently reopened from original artifact
in source-only hash-lock Actions run 37914513814, NO native calls.

Source-only predicted exact 8-cell results:
  s2a,submit-root-3-a         ACCEPT  => root-3-a
  s2a,submit-root-3-b         REJECT  => root-2-a
  s2a,submit-root-3-old-only  REJECT  => root-2-a
  s2a,submit-root-3-new-only  REJECT  => root-2-a
  s2b,submit-root-3-a         REJECT  => root-2-b
  s2b,submit-root-3-b         ACCEPT  => root-3-b
  s2b,submit-root-3-old-only  REJECT  => root-2-b
  s2b,submit-root-3-new-only  REJECT  => root-2-b

All four candidates have IDENTICAL signed root3 body but nonidentical
signed-envelope signer sets. Every cell has independently checked old
and new verifier key ID lists, signer qualification and thresholds.

Actual strong B9 (full source/signing knowledge): 8/8 source-derived
capability. Best version+candidate-only deterministic oracle-optimal
representation upper bound on this registered grid: 6/8; this weaker
ablation is NOT the strong B9. No claim of EEQ unique accuracy.

The join-only scorer anti-masking synthetic tests are 10/10 PASS,
Actions run 37914550754. No tuf-js native verifier was executed in this
unit-test workflow.

## Exact source/verification blobs and environments (MUST abort if changed)

- Pre-source freeze:
  19344e1913c29d266d1876e812d19d13a5f728d3
- Controlled source generator:
  05331a87bc2a04531167fedbb5b554ed91ce6181
- Source-only crypto tests:
  9031f4b121ab8796794fcf5df8adf986a2c7ed5f
- Prior independent OLPC TUF signature checker:
  3ddd6458fe1c71b069e7adf7b21cc839c388265b
- Native-only verifier (NO source prediction file imports):
  dfe9c055de74ce5ba0c5f4c4620227363e82bca3
- Native/source immutable join-only scorer:
  94fb6aaab245287a38d32cccd91d4bdd5c40c15a
- Scorer 10 anti-masking tests:
  13193f3e5d25634f62ece31f6954746739189e76
- tuf-js 3.0.1 pinned npm dependency lock:
  9f9f135f7ff93489c32579aeb90ffb80d0db7e4a
- Original G4 frozen protocol:
  3eeaeeb828d2fcf7ec4487da06489fee3146c920
- Original WFC v1 compiler:
  9a6bff7a2b8db73b86b6952c706852c92b1a4b1d

Node.js 22.16.0, Python3.11, ubuntu-24.04, npm ci on locked tuf-js
node module. NO production source signing keys.

## Stage-II FIRST native execution allowed after THIS manifest's commit

1. Hash-verify original outer source artifact ZIP, manifest, predictions,
   plus each seven original source bytes. Validate registered 2x4 case set.
2. Execute scorer's synthetic test suite again (no native).
3. Install frozen tuf-js dependency tree.
4. Independent native-only script accepts original sources DIRECTORY ONLY,
   not source predictions. Isolate one TUF TrustedMetadataStore for EACH
   initial state and candidate action, starting from shared root1, applying
   valid root2A/root2B and then exactly one frozen root3 candidate. Save
   original native outcomes, error types and the EXACT resulting trusted
   signed-metadata AND signature-envelope identity.
5. Independently verify both shared-root1 native setup paths as separate
   controls, never count failed setup as a method win.
6. Only after the 8 raw native results and 2 setup controls are archived,
   invoke the prescored source/native join-only scorer.
7. Preserve ALL 8 cases, including failures, missing rows and any
   source/verification mismatch, without changing fixtures or scripts.
8. Save native and joined JSON, workflow logs, each SHA256, exact commit,
   original source artifact SHA.

## Required interpretation

If successful: restricted controlled-native VERSION-ONLY representation
is insufficient; source qualification from old/new signatures is necessary;
full-source native B9 matches. Disposition:
R4_D0_NATIVE_VERSION_SUFFICIENCY_KILLED_STRONG_B9_TIE.

If not: retain R4_D0_NATIVE_FAIL_OR_INCOMPLETE with exact error and original
frozen predictions; do not silently patch code or adjust case eligibility.

Even success is *NOT* R4 P3 engineering savings, *NOT* a new generic
source-to-certificate compiler, *NOT* new unseen holdout, *NOT* novel TUF
signature checking and *NOT* improved correctness over fully informed B9.

Main untouched. No prior G4 freeze, original B10 or G5/G6/G7 scores
reinterpreted or modified; G5 original unique semantic count stays 285.
