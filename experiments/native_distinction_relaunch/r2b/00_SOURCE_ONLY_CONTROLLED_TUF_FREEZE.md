# R2-B controlled-native TUF qualification contrast — source-only freeze

Date: 2026-10-09
Parent: `0c4fc8d2fec3c88550abd5b24d65cfb9656c72b3`
Status: **BEFORE source generation, native outcome unopened**.
Role: EEQ Native Distinction Necessity, R2-B development experiment. NOT R2-A, not R4, not unseen holdout, not original G4-v1.

## Scientific object and anticipated negative result

We test a **non-cosmetic, claim-relative merge**, not a new minimization algorithm.

The trusted sources `root2_A` and `root2_B` must be valid, separately
signed top-level TUF root metadata, carrying *different* bona fide
`targets`-role authorities, while retaining the same trusted
`root`-role signing authority and threshold.

Under a narrowly frozen ROOT-UPDATE-ONLY contract, they are expected to
make identical decisions and transitions for every registered action word
up to horizon r=2. A strong manual B9 representation containing version,
root-role qualified key IDs, threshold and all candidate signature
checks is **allowed and expected to merge them too**.

The role difference is real only if cross-signature authorization changes:
a signed `targets_A` metadata sample must validate under `root2_A`
and fail under `root2_B`, while `targets_B` does the reverse.
Failing this test is `NO_GENUINE_QUALIFICATION_DIFFERENCE`;
mere different raw JSON or renamed key IDs cannot earn an R2-B result.

For the wider `targets`-qualification/audit contract these two histories
must *not* merge. No claim of universal state equivalence is allowed.

## Frozen deterministic controlled source design

Test-only cryptographic identities generated reproducibly by Ed25519:
`SHA256("EEQ-R2B-TEST-KEYS-V1|" + logical_role)` as a 32-byte
seed, converted to Ed25519 PKCS8. Logical roles:
`root_signer`, `targets_A`, `targets_B`, `snapshot`, `timestamp`.
These are public TEST seeds, NEVER production or secret keys.
Private seed/key material is never included in generated metadata artifacts.
Key IDs = SHA256(OLPC-canonical TUF public Key object) and source bytes
are deterministic OLPC-signed metadata serialized to JSON.

Create five immutable source fixtures:
- `root1.json`: trusted controlled anchor; root, targets(A), snapshot,
  timestamp top-level roles, each threshold 1.
- `root2_A.json`: signed root update to version 2; same root role, targets=A.
- `root2_B.json`: signed root update to version 2; same root role, targets=B.
- `root3.json`: signed candidate update version 3, with same root signing
  authority (choose targets=A before native).
- `root3_bad_sig.json`: single-hex-nibble corruption in version 3
  root envelope signature; all signed metadata otherwise identical.

Also create one `targets_A.json` and one `targets_B.json`, each a
properly signed empty targets metadata with `version=1`, demonstrating
cross-authority authorization differences. Fixed test expiry:
`2035-01-01T00:00:00Z`; `spec_version="1.0.0"`;
`consistent_snapshot=true`; all four required TUF top-level roles present.

Source-only preflight may use Node builtin crypto, independent OLPC string
canonicalization and source bytes. **Do NOT import tuf-js or its models,
call native updateRoot, read earlier native labels or infer outcomes from
native errors.**

## Registered comparison (to be frozen again before native execution)

State histories:
- `H_A`: controlled root1 -> root2_A;
- `H_B`: controlled root1 -> root2_B;
- `H_3`: after a valid root3 update from either history.

Registered action alphabet (EXACTLY, for all states):
1. `submit_root3_valid`;
2. `submit_root3_bad_sig`;
3. `submit_root2_A_replay`.

For root2_A and root2_B source-derived model:
`submit_root3_valid` predicts advance to H_3; bad signature and
root2_A replay predict keep trusted state. From H_3, all registered
proposals predict keep root3. Total graph: 3 states x 3 actions = 9 cells.

Test native BOTH paths independently:
- original trust anchor root1;
- update to root2_A or root2_B;
- enumerate all action words of lengths 0, 1, 2 from the fixed three-action
  alphabet (1 + 3 + 9 = **13 traces per history**);
- replay each trace from a FRESH native store, preserving complete
  action outcomes and exact post-trust-root states at each step;
- count SOURCE_SETUP_FAILURE / native errors separately, never silently
  remove a trace.

**Key equivalence nuance:** H_A and H_B are distinct source histories
whose exact `targets` authority differs. Root-update native states
can remain distinguished by provenance IDs while their *registered
decision quotient* merges. Source lineage cannot be erased from
audit responses unless those audit claims are explicitly out of scope.

## Fair baseline and controls frozen before outcomes

- B0: complete controlled signed root metadata/history, source bytes,
  public keys and action/contract scope.
- Strong B9: exact root-version and qualified root-role signer keys/threshold
  plus version continuity and candidate signature validity; this baseline
  **may discard unrelated targets-role fields** for root-update-only tasks.
- Classical exact future quotient on the same complete registered graph
  (may exactly match EEQ).
- Current-only observation partition, costed separately.
- EEQ candidate: source-qualified compiler + future quotient + a checked
  distinction/merge certificate.
- Required out-of-scope discriminator: native/source targets authority
  cross-check for targets_A/targets_B; controls for tampered root signatures
  and wrong-version replay.
- Missing-source refusal is NOT expected to be decided by native updateRoot
  if the source file is unavailable. Mark SOURCE_UNAVAILABLE / UNSUPPORTED
  separately; no credit for a native REJECT that was never executed.

All methods get identical source and actor/contract information.
Full source/key-generation, parsing, verification, codebook, certificate
and decision costs must be charged before any R4 benefit claim.

## Hard stop criteria

- If source fixture signatures do not independently verify, do not run native.
- If the targets-role difference does not alter qualified targets evidence,
  report `NOT_A_GENUINE_B_PAIR`.
- If the B9 baseline also merges (expected), report `B9_TIE`, not a unique
  EEQ result.
- If native root2_A/B initialization or continued root3 update differs
  from pinned predictions, report `R2_B_NATIVE_MISMATCH`; do not rewrite
  the source set, contract or action alphabet after scoring.
- If a registered continuation action changes a targets-role audit claim,
  that claim is outside the frozen root-update-only equivalence and
  absolutely cannot be conflated with the narrow B result.
- Do not count A-class future divergence as established by this study.
  R2-A still requires a prospective **real action-induced** distinction
  study, likely under Kubernetes policy/binding change.
- Historical R1 root 56/56 and G4 v1 remain unchanged.
- No R2-B native run until the generator Git blob, seven source JSON SHA256,
  source-only prediction JSON SHA256, native scorer code and package-lock
  have been **committed to a separate prescore freeze**.

This source-only experiment has no native outcome denominator yet.
