# R1a Actual Result — Immutable Production Root Authority-Descriptor Preflight

Date: 2026-10-08
Status: R1A_SOURCE_STRUCTURE_PREFLIGHT_PASS, NOT NATIVE EXTRACTOR PASS.

Freeze document:
experiments/native_distinction_relaunch/03_TUF_SOURCE_ONLY_PREFLIGHT_FREEZE.md
Commit frozen before source-only run: 818bdb0267ed940f79f07e92e57837b3fa97cfba.

Execution:
- GitHub Actions run: 37765321520
- Workflow commit: 1ac5ea5f0b408cb59f5697a2d7e9389eef9fbeb7
- Artifact: 11543717893 (eeq-r1a-tuf-source-only-preflight)
- Artifact ZIP SHA256:
  fe4f993aa26e27d5834127cc0a67f32a6f8353d8e1f22a7bee6a1c2e5abee346
- Conclusion: SUCCESS

Result as printed by source-only extractor:
- immutable source root files: 8/8;
- candidate adjacent transitions: 7 (roots 1->2 through 7->8);
- root-role authority descriptor changes (keyid set OR threshold): **7/7**;
- TUF native verifier invoked: FALSE;
- cryptographic signatures checked: FALSE;
- prior native outcome labels read: FALSE;
- method scored rows: 0; G5 count increment: 0;
- R1 status: PREFLIGHT_SOURCE_STRUCTURE_ONLY.

This observation establishes only that authority descriptions DIFFER along
all seven candidate edges. The archived JSON artifact contains per-root
keyids/threshold and per-transition additions/removals/intersections and
syntactic signature-envelope overlaps. A syntactically present signature is
not proof of cryptographic validity.

## Next scientific obligation, not yet passed

Freeze an executable *label-blind* root-update transition extractor which:
1. derives the authorized old and new signer qualification predicates from
   the exact source bytes and documented native semantics;
2. exposes old/new threshold checks without consulting prior scored labels;
3. encodes version and source availability boundaries and source identities;
4. returns UNSUPPORTED / UNKNOWN rather than fabricating a deterministic
   successor if an input or signature/effect is unresolved;
5. identifies complete finite action-state closures **before** claiming
   contract-relative quotient results;
6. supplies independently native-verifiable future distinction words;
7. admits real noncosmetic merging only relative to a frozen future contract.

No A/B native pair has been scored. No native method performance or
superiority over B9 has been shown. R1_NATIVE_EXTRACTOR_FEASIBLE is OPEN.

TUF may serve development feasibility, not the new prospective unseen family.
Original G4, v1 B10, X.509/in-toto and all G5/G6/G7 prior scores unchanged.
