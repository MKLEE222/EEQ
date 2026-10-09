# R4-D0 / TUF Same-Version, Different-Lawful-Authority — PRE-SOURCE FREEZE

Date: 2026-10-09
Status: FROZEN BEFORE SOURCE FIXTURE GENERATION OR NATIVE SCORING.
Parent research branch eeq-r2a-k8s-dynamic-20261009 at
6433d48d5d5b50aeda9bae94ff16380798a37886.

## Scientific objective (diagnostic, not R4 superiority test)

R2B controlled TUF root-update used one common root signing role at each
root version. On its narrowly registered candidate set, a sufficient B9
could retain trusted root VERSION only and achieve 24/24. We now attempt
to falsify that dataset-specific sufficiency, NOT a fully informed B9.

A genuine signed cryptographic contrast under exactly the SAME candidate:
old trusted root version=2 in both branches, but different qualified
root-authority signing key:
  History H_A: root1-common -> root2-a; root2-a root role = A.
  History H_B: root1-common -> root2-b; root2-b root role = B.
Both transitions must be genuinely accepted by independent native
tuf-js (old root1 authority plus new root2 authority).
Common genesis root1 role = ANCHOR.

Root3 candidates are ALL version 3 with the SAME *signed root3 body*
(root role = NEXT) but distinct actually cryptographic signature envelopes:
  C_A: signatures {A, NEXT};
  C_B: signatures {B, NEXT};
  C_OLD_ONLY: signatures {A} (new-root NEXT qualification missing);
  C_NEW_ONLY: signatures {NEXT} (old-root qualification missing).

All root1/2/3 signed sources use native TUF root metadata:
  _type="root", spec_version="1.0.31",
  expires="2036-01-01T00:00:00Z",
  consistent_snapshot=true,
  role snapshot, targets, timestamp keyids and threshold=1,
  root-role threshold=1, genuine TUF public signing keys/IDs.
No production signing credentials, no secret third-party source.

Reproducible TEST-ONLY Ed25519 private keys:
  private seed = SHA256(UTF8("EEQ_R4_TUF_AUTHORITY_V1_TEST_ONLY/" + label))
  with labels EXACTLY:
  ANCHOR, ROOT_A, ROOT_B, ROOT_NEXT, TARGETS, SNAPSHOT, TIMESTAMP.
The deterministic keys are PUBLIC TEST MATERIAL, forbidden for production.
Sign the OLPC canonical signed-body bytes using Node Ed25519 crypto,
not tuf-js. KeyID = SHA256(OLPC canonical public TUF key object).

Seven immutable JSON source documents after generation:
  root-1-common.json,
  root-2-a.json, root-2-b.json,
  root-3-a.json, root-3-b.json,
  root-3-old-only.json, root-3-new-only.json.
All candidate root3 files have EQUAL canonical SIGNED-body hash; their
source bytes/signature envelopes differ. No metadata-version confound.

## Registered action/state grid, full denominator, predictions

States EXACTLY {s2a, s2b}. Actions EXACTLY:
 {submit-root-3-a, submit-root-3-b,
  submit-root-3-old-only, submit-root-3-new-only}.
Full 2x4 = 8-cell grid.

Pre-native source-derived expected native results:
  s2a / cA         -> ACCEPT / trusted root3-a;
  s2a / cB         -> REJECT / remain trusted root2-a;
  s2a / cOLD_ONLY  -> REJECT / remain trusted root2-a;
  s2a / cNEW_ONLY  -> REJECT / remain trusted root2-a;

  s2b / cA         -> REJECT / remain trusted root2-b;
  s2b / cB         -> ACCEPT / trusted root3-b;
  s2b / cOLD_ONLY  -> REJECT / remain trusted root2-b;
  s2b / cNEW_ONLY  -> REJECT / remain trusted root2-b.

Old/new signer qualification must be tracked SEPARATELY, each
cryptographically verified with DISTINCT authorized role keyids,
not syntactically counted envelope keyids. All eight must be source-only
derivable, with 0 UNKNOWN for the registered signed sources.
Native verifier exact allowed API:
  tuf-js@3.0.1 TrustedMetadataStore.updateRoot,
  fresh store seeded at common root1 then root2-A/B installed by native,
  followed by EXACTLY ONE registered candidate per reset.
Native observations record old version, old signed root source identity,
candidate source SHA, ACCEPT/REJECT, post-action FULL signed-root identity,
native exception class and independent setup failures.

Minimum positive existence obligations:
 - both lawful branch setups actually succeed in native tuf-js;
 - cA accepted ONLY from H_A, cB accepted ONLY from H_B;
 - C_OLD_ONLY and C_NEW_ONLY both rejected by native under both states;
 - all 8 native labels AND actual post-state identity match the
   PRE-FROZEN source-only predictions; 0 omitted/censored rows.
 - root2 variants have distinct authenticated root signing keyids even
   though version and non-root fixed keys match.
 - each candidate has valid new-root signature as designated (except
   OLD_ONLY), and old-root authority is properly checked.
A failure is retained, never repaired by post-score changing fixtures.

## Fair strongest baseline and no-op control

**FULL-SOURCE B9** is allowed to read all registered source metadata,
old-root/new-root signing keyids, both thresholds and all valid signature
bytes, and to reproduce the standard updateRoot rules before native labels.
It should match 8/8 if the fixture instantiates correctly.
Conventional native verifier is the oracle, not a blinded baseline.

A deliberately insufficient VERSION-ONLY ablation sees only trusted
version=2 and candidate version=3 PLUS unchanged candidate identity.
Its optimal deterministic per-action majority decision scores at most
6/8 on the four actions, because cA and cB each have opposite results
under identical versions + candidate identity. DO NOT label it "B9".
The simplistic always-accept-when-version-contiguous rule gets 2/8;
the BEST version+candidate identity oracle gets 6/8. Report both if
possible, but only FULL-SOURCE B9 counts for originality.

The contrast is a DATASET/PREDICATE SUFFICIENCY counterexample,
not a general mathematical novelty proof and not R4 primary metric.

## Research chronology and science-gate rules

1. Freeze this file on NEW BRANCH, with exact action set and pre-native
   semantic expectations BEFORE the source fixture generator exists.
2. Implement independent source-only deterministic generator/extractor
   using Node crypto, NO tuf-js and NO scored native output labels.
3. Source-only CI signs exactly seven files, verifies exact source hashes,
   prints SHA256 and prediction JSON, rejects source-generation errors.
4. Freeze source-artifact outer SHA256, internal source and prediction
   SHA256, exact code blob SHAs, tuf-js package-lock blob SHA in a NEW
   prescore manifest before any native update.
5. Only THEN invoke independent tuf-js native challenger and a join-only
   scorer, with all eight registered native results and both setup paths.
6. Synthetic anti-masking tests verify that signature corruption,
   missing rows, incorrect successor identity, source drift and
   unsupported keys cannot be counted as correct.

Even perfect 8/8 controlled native calibration:
  R4_D0_LAWFUL_SOURCE_QUALIFICATION_NECESSARY;
  R4_PRIMARY_P3_NOT_YET_SCORED;
  R4_INDEPENDENT_VALUE_NOT_PROVEN; FULL_B9_TIE.

## Actual future R4 evaluation (separate frozen protocol required)

We tentatively prioritize P3: independent, domain-specific adaptation
and certificate maintenance effort under exact matched correctness,
legal-source access and safety. No primary P3 evaluation is authorized
from this D0 protocol; independently freeze task population,
maintainers/time budgets, semantic-delta conditions, certificate-checker
requirements, strongest B9, classical methods, end-to-end costs and
failure disposition before running P3. If well-equipped B9 ties P3,
record NO_INDEPENDENT_VALUE; never downgrade B9.

Other gates still open: missing-source SOURCE_UNAVAILABLE/REFUSE
calibration; generic adapter generation; independent family transfer.
No original G4, G5/G6/G7, v1 B10, main, or holdout changes.
