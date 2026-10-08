# R1b — TUF Source-Derived Root-Update Transition Extractor Freeze

Date: 2026-10-08
Status: SOURCE-CRYPTO PREDICTION DESIGN FROZEN BEFORE FIRST NEW 56-CELL NATIVE GRID.
Parent R0 charter at 00_REFOUNDING_CHARTER.md; R1a source inventory frozen earlier.

## Scope and authority

This is DEVELOPMENT feasibility on previously studied Bottlerocket roots, NOT
a new unseen native family, new G5 cases, or a G4-v1 protocol modification.
Old native TUF adjacent updates 1->2, ..., 7->8 are already known; do not
report the seven repeated successes as fresh prospective evidence.

Pinned sources and source boundary: 1.root.json ... 8.root.json of
aws-k8s-1.35/x86_64 at immutable exact SHA/byte lengths in
experiments/bottlerocket/FROZEN_SOURCE_INVENTORY.md.
Never substitute root 9 or a different environment if any source fails.

Normative update obligation: TUF specification v1.0.36 root-update step:
https://theupdateframework.github.io/specification/v1.0.36/
- the candidate must have signed.version = trusted version + 1;
- old trusted root key role threshold and new candidate root key role
  threshold must EACH be met by cryptographically verified unique KEYIDs;
- each distinct keyid contributes at most once to a role threshold.
TUF keyids are declared authoritative identifiers associated with keys in
signed.keys, not evidence of cryptographic validity by themselves.

## A frozen finite development domain

States S = {trusted-root-1, ..., trusted-root-8}.
Actions A = {submit-root-2, ..., submit-root-8}.
Exactly 8 x 7 = **56** state/action cells, including 7 adjacent
state-matching proposals and 49 nonadjacent proposals.

For each (trusted-root-N, submit-root-M):
- both files come only from verified pinned root inventory;
- source-only extractor independently canonically serializes candidate
  signed metadata as TUF-compatible Canonical JSON (not RFC 8785 JCS);
- verifies signature bytes using public keys from the OLD trusted root
  role and the NEW candidate root role;
- computes old/new signer *unique keyid* counts vs their thresholds;
- checks exact version continuity;
- if signatures, algorithm and sources are resolvable and both thresholds
  plus version hold: declared model transition is trusted-root-M;
- if resolved candidate is invalid or nonadjacent: declared transition is
  a trust-root-N self loop ("attempt refused, trusted root unchanged");
- if required source, crypto scheme, key encoding or qualification is
  unsupported/unknown: MODEL_UNSUPPORTED, with no fabricated transition.
- initial trusted root-1 is a preselected *trusted anchor*, not inferred
  by retrospective native actions.

The finite model is complete ONLY for this registered 8x7 action domain,
not all arbitrary root bytes, expiry handling, timestamp/snapshot/targets,
repository network failure, or all native TUF environments.

## Supported cryptographic schemes at this frozen stage

Only:
- Ed25519 raw public key (hex) -> DER/SPKI, Ed25519 verify;
- ecdsa-sha2-nistp256 key PEM/SPKI with SHA-256, DER signature;
- rsassa-pss-sha256 PEM/SPKI with SHA-256 and PSS saltLen=SHA256 digest.

Unsupported or badly encoded keys do NOT count as a failed signature;
classify MODEL_UNSUPPORTED. Invalid well-formed signature bytes and
insufficient cryptographically verified unique keyids count as false when
the scheme is explicitly supported.

No tuf-js imports, no native oracle outcomes, and no action-label fields
are allowed in the independent extractor code. Only Node built-in crypto,
JSON and pinned public root bytes. The exact key/scheme distribution is
reported, not assumed.

## Two-stage execution chronology

R1b stage I — source-derived predictions ONLY:
1. Check pinned source integrity and the frozen action grid;
2. extract all 56 statuses and predicted destinations without native calls;
3. issue machine-readable validity certificates: signature overlap, old/new
   verified signer IDs, thresholds, canonical signed hash, source SHA;
4. archive predictions and artifact hash. Independently test crypto
   implementation on synthetic signed fixtures, duplicate signatures,
   tampering, nonadjacent roots and unsupported mechanisms.

R1c stage II — independent native calibration:
1. FURTHER FREEZE the exact stage-I predictions artifact ID, ZIP SHA256,
   script Git blobs, native \`tuf-js@3.0.1\` package lock and grid before any
   56-cell native run;
2. for each starting trusted root N, create an isolated
   TrustedMetadataStore initially anchored by production root1, replay
   root2..N as setup, then propose original source root M;
3. retain both native ACCEPT/REJECT/ERROR and post-action trusted-root
   version, timing, error class; no silent retry/replacement based on labels;
4. score **only** states with the frozen prediction status in the valid
   comparable domain; failures of native setup or unsupported mechanisms
   remain independently documented and never converted into a match;
5. compare exact per-cell status and state destination to pre-native
   predictions, retain mismatches and all 56 cells as denominator.

Source-only stage I is NOT a native success and does not establish the
noncosmetic merge / future separation required for R2.
A no-op update is NOT a claim that unknown candidate bytes are safe.

## Tests that kill this direction

- Root source bytes/size/hash differ: abort with SOURCE_PIN_MISMATCH.
- Unresolvable crypto and candidate cannot be classified: MODEL_UNSUPPORTED.
- A duplicate signature-keyid counts >1: reject implementation.
- Reversed/current-only/new-only threshold verification fails to reject
  adversarial fixture: reject implementation.
- Predictions use previous native outcomes or tuf-js: reject implementation.
- R1c native disagrees with any otherwise supported registered cell:
  R1_EXTRACTOR_MISMATCH; do not alter the frozen predictions.
- Any accepted candidate without a corresponding closed state in S:
  C3_GRAPH_NOT_CLOSED, not an invented new state.
- If the complete 56-cell graph is not derivable, R1 remains OPEN.

## Further scope limits after a successful 56-cell calibration

Even a 56/56 match would show a correctly extracted **restricted TUF root
transition graph**, not a native quotient advantage or generality.
R2 still needs prospective noncosmetic A/B counterfactuals and matched
strong B9 + classical quotient comparison. If no genuine B pair exists in
this source inventory, retain that negative finding; do not rescue it
using whitespace/key ordering.
