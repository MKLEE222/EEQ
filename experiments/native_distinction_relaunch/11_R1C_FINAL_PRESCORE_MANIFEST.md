# R1c FINAL 56-cell independent native calibration manifest — PRE-NATIVE FREEZE

Date: 2026-10-08
Status: **FROZEN BEFORE ANY R1C NATIVE 8x7 CALIBRATION GRID EXECUTION**.

This is the first prospective FULL 56-cell native grid with the NEW R1b-v3
extractor, although its seven adjacent accepted transition labels were known
from earlier development and are not fresh held-out evidence.

## Unmodified G4, v1 and parent boundaries

Original G4 protocol commit:
c15b212ad0c2be3856a03d38802aaffa628aefd1.
Original v1 generic compiler blob:
9a6bff7a2b8db73b86b6952c706852c92b1a4b1d.
No G4/G5/G6/G7 or historical TUF result changes.
X.509 and selected in-toto family never used for this new extractor.

## Frozen source-derived predictions (NO native calls)

Source-crypto execution: Actions 37799375569 at Git commit
2fb36c489ce1109272658f87f78b1a600c5f7aa2.
Artifact ID: 11558989924, name
eeq-r1b-v3-source-crypto-transition-grid.
Exact **outer artifact ZIP SHA256**:
c37f947099c7e7bcbcce0778618123d577395dce4addd0ca291e57d84d6e30b3.
Exact **inner prediction file SHA256**:
81b1fd5ff0b7080d33b952d4ae9e890db8e5e4260831899bf773937152f91fed.
The inner hash was independently printed without native execution in
Actions 37799763720.

Filename: TUF_R1B_V3_SOURCE_CRYPTO_PREDICTIONS.json.
Frozen hypothesis on all registered 56 cells:
- seven old-trusted-root-N -> submit-root-(N+1) source-derived advances;
- 49 nonadjacent root proposals keep trusted root unchanged;
- zero model unsupported under this source/action registration;
- 8 trusted-root states, 7 proposal actions, exact 56-case domain;
- source hashes pinned to FROZEN_SOURCE_INVENTORY.md.

As of this freeze, no R1c native 56-case grid run has occurred.

## Exact code blobs, not merely filenames

- R1b-v3 source-only extractor:
  3ddd6458fe1c71b069e7adf7b21cc839c388265b
- R1b-v3 synthetic crypto regression tests:
  5327aa134d4fa8527638d24ef7fb8daf6d4e64fc
- R1c native comparator, no prediction import:
  203bfcd94ff12ac9e9ef9a86150e0e2726f40636
- R1c join-only scorer:
  bce66baf147c5ee3f352de2f9882e9bd3b9d491a
- R1c synthetic anti-masking scorer tests:
  091a6a89af503cfdc099112c9fbf3869607563bb
- Pinned tuf-js@3.0.1 native package-lock:
  9f9f135f7ff93489c32579aeb90ffb80d0db7e4a
- Exact eight root source inventory:
  791edfa06c6e0ce7b95cd1b2a31db46d756feb03
- Original R1c design freeze:
  eaeff09fc85d4ad241cab2d8f4e6b9378d59e430

A workflow differing in any above Git blob must abort or count as a NEW
versioned experiment. This final manifest itself is never rewritten after
native outcomes.

## Native challenge and scoring (frozen)

Native oracle: tuf-js@3.0.1 TrustedMetadataStore.updateRoot.
Runtime node 22.16.0, ubuntu-24.04, npm ci on the pinned package-lock.

For every N in 1..8 and M in 2..8, always run a FRESH native store from
predeclared trusted root1, replay 2..N setup, submit the pinned candidate rootM
once, capture post trusted version and error class, including all 56 cells.

Expected pairing:
- frozen ADVANCE_TRUST_ROOT -> native ACCEPT and post-state root M;
- frozen KEEP_TRUST_ROOT -> native REJECT and post-state root N;
- frozen MODEL_UNSUPPORTED -> never counted correct merely for REFUSE;
- native SETUP_FAILURE -> infrastructure/source failure, not method success.

Preserve the entire 56 denominator regardless of outcome. Stratify seven
previously known adjacent production updates and 49 other proposals.
No post-score exclusion, action replacement, new root source or result tuning.

A successful all-match full grid is only
**R1_TUF_RESTRICTED_NATIVE_TRANSITION_CALIBRATION**:
one source-derived finite registered native root-update graph, NOT R2
noncosmetic merging, NOT a universal TUF source graph, NOT H3 advantage over
strong B9 and NOT a new holdout.

An observed native mismatch is **R1C_NATIVE_MISMATCH**, and must be retained;
the frozen R1b-v3 predictions cannot be retroactively modified.
