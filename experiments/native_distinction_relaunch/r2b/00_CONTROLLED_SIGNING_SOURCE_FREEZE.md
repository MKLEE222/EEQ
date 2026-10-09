# EEQ R2-B: Controlled Real-Authority Distinction — Source-Only Freeze

Date: 2026-10-09 (Asia/Shanghai).
Parent R1 snapshot: 0c4fc8d2fec3c88550abd5b24d65cfb9656c72b3.
Status: PRE-FIXTURE-GENERATION FREEZE. NO R2-B NATIVE ORACLE RESULT YET.
Evidence class on future execution: CONTROLLED_NATIVE_DEVELOPMENT.

## Science question, contract and danger of triviality

Can *genuinely different authorized evidence* be merged without losing any
future decisions for a specifically registered **root-update-only** TUF
continuation contract?

The changed evidence is NOT decorative:
two valid signed root-v1 trust anchors have identical (root-role key set,
root threshold, version), but **different authorized TARGETS signing keys**.
They entail different capabilities to verify target-role signed metadata.
The distinction MUST be retained if the contract asks about targets.

For this R2-B experiment only, the registered decision contract concerns
**TrustedMetadataStore.updateRoot** with a finite, fixed action alphabet,
not target-file integrity or source-provenance identity.

We pre-register a **strong B9 tie**: a competent hand-engineered sufficient
state containing (root version, root-role signing key set and threshold)
and the candidate signatures is allowed to merge these two initial roots.
A classical exact Moore quotient has exactly the same legal action graph
and contract. This experiment cannot, by itself, demonstrate EEQ's
superiority to either baseline.

## Exact source construction — controlled valid Ed25519 signing

Generate from deterministic PUBLICLY KNOWN test-only seeds using
  seed(role) = SHA256(UTF8("EEQ-R2B-20261009-DEVELOPMENT-ONLY::" + role)).
Use Node 22.16.0 builtin crypto with an Ed25519 PKCS#8 private key wrapper
around that 32-byte seed. This is NOT private production key material and
must never be used to sign a real production update.

Five disjoint role-key labels are frozen:
- "ROOT_SHARED"
- "TARGETS_A"
- "TARGETS_B"
- "SNAPSHOT_SHARED"
- "TIMESTAMP_SHARED"

Derive each keyid from sha256(TUF-OLPC-canonical(public key object)).
Public key object uses the exact Ed25519 TUF key schema:
  {keytype:"ed25519", scheme:"ed25519", keyval:{public:<64-hex>}}.
All role thresholds = 1, and a single root-signing key is shared.
JSON signed bytes are TUF OLPC canonical JSON (sort object keys, escape
backslash and double quote; preserve literal newlines).
All controlled metadata expiries = 2035-01-01T00:00:00Z (fixed frozen
scope, NOT full timestamp/snapshot/targets update coverage).
Specification version 1.0.0; consistent_snapshot = true.

Produce exact source-file roles:
- anchor_a.root.json: root v1, root role ROOT_SHARED, targets TARGETS_A;
- anchor_b.root.json: root v1, root role ROOT_SHARED, targets TARGETS_B;
- candidate_2.root.json: root v2, root role ROOT_SHARED, targets TARGETS_A;
- candidate_3.root.json: root v3, root role ROOT_SHARED, targets TARGETS_B.

All four are individually cryptographically signed by ROOT_SHARED.
Produce two targets metadata envelopes (version 1, same harmless artifact
descriptor) separately signed with TARGETS_A and TARGETS_B, respectively.
Each is authentic under only its matching initial anchor, absent any
compromise. These target-role envelopes are *capability witnesses*, not
root-update decisions.

No generation-time native result, native library import, prior native
label, production signing key or network token may enter source generation.

## Registered future-decision graph, frozen independently of outcome

Initial native states: ROOT_A and ROOT_B.
Proposal action alphabet, in exact order:
  submit-candidate-2, submit-candidate-3.

Future action-prefix horizon r = 2; exhaustive words:
  empty, [2], [3], [2,2], [2,3], [3,2], [3,3].
No action may be removed after observing native results.

Source-only extractor:
- for each initial anchor and each prefix, derive the lawful trust root
  by *cryptographically checking* the candidate's old and new root-role
  signing threshold, plus exactly one-step version continuity;
- accepted action -> candidate becomes the trusted root;
- rejected action -> unchanged trust root;
- unresolved signature, unknown algorithm or invalid source ->
  MODEL_UNSUPPORTED (not a fabricated next state);
- for every prefix state, derive the two next-action eligibility decisions
  as the registered continuation observation vector.

Expected source-only hypothesis **before native calls**:
1. both initial anchors are VALID signed sources;
2. their root-role (version, authorized signing keys, threshold) is equal;
3. their targets-role authorized signing key IDs differ;
4. a targets-A signed document verifies using ROOT_A authority but NOT
   ROOT_B, with the opposite relationship for targets-B;
5. both initial anchors have the SAME full root-update action observation
   vectors at every registered future path of length <=2;
6. contract-relative quotient MERGES ROOT_A and ROOT_B while distinct
   authorized targets-role evidence remains separately retained for audit.

These are mechanistic hypotheses. If source-only check fails, retain its
failure. Native verification has not yet been performed at this freeze.

## Source-only then native chronology

**Stage S (source only):**
- commit this freeze BEFORE generating files/predictions;
- execute generator and independent local-crypto evidence/continuation
  assertions in GitHub Actions; NO tuf-js import or call;
- archive exact source bytes, signed targets witnesses and full source-only
  decision/prefix prediction ledger;
- externally pin BOTH artifact outer SHA256 and inner JSON/source SHA256.

**Stage N (later, separately frozen):**
- first commit an immutable prescore manifest containing the Stage-S
  run/artifact hashes, exact generator/script blobs, native verifier script
  blobs, tuf-js@3.0.1 package-lock blob and all word/claim IDs;
- run native root verification independently: fresh TrustedMetadataStore
  seeded with either pre-signed root-A or root-B for each action prefix,
  then native continuation challenges with separate new isolated stores;
- *also* use native role signature verification to check that targets-A
  is qualified by root-A but not root-B, and vice versa;
- join AFTER raw native observations are recorded against pinned predictions;
- zero observed outcome-dependent exclusions. Report and retain native
  setup failures, errors, source/hash drift, and all mismatches.

## Hard adversarial controls and interpretation

C1. If native signed root anchors cannot be independently self-verified,
    the carrier is INADMISSIBLE and no quotient success is claimed.
C2. If the targets-role authority contrast cannot be independently
    confirmed using real signed target metadata, mark
    NONCOSMETIC_QUALIFICATION_NOT_ESTABLISHED.
C3. If root-only action traces differ across A/B at any frozen prefix,
    record ILLEGAL_B_MERGE; do not shrink action scope post-score.
C4. If B9 and classical quotient produce the same merge or accuracy,
    report B9_TIE. This is the EXPECTED control, not a disappointment
    to be suppressed.
C5. If full cost (source evidence, codebook, certificate/verification)
    overwhelms benefit, do not claim a compression advantage.
C6. This is a controlled native feasibility pair, **not** a natural
    production B pair, an A future divergence, an unseen holdout, or a
    general-purpose trustworthy evidence compressor.
C7. No old G4-v1 protocol, case ledger, code or holdout may be modified.

## R2-A scope warning

On fixed-proposal root-update machines where every rejected update leaves
the trust root unchanged and every accepted update replaces it with the
same fixed candidate root, states that agree on ALL immediate action
outcomes cannot become separable by future strings over that same alphabet.
This is an elementary deterministic-transition induction, not an EEQ
novel theorem. The result does not cover external source publication,
key exposure, asynchronous events or other action families.

Therefore do NOT force the current TUF carrier to provide an R2-A example:
prospective real Kubernetes policy/binding update is a separate task.

Disposition after Stage S: SOURCE_ONLY_FEASIBLE or SOURCE_ONLY_FAIL.
Disposition after Stage N: CONTROLLED_NATIVE_B_CONFIRMED / B_REJECTED, with
B9_TIE recorded whenever warranted. Neither entails full R2 PASS.
