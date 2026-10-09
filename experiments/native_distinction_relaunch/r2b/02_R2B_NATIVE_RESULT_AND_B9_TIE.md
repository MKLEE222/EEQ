# R2B-v1 Actual Controlled Native Result — B demonstrated, B9 ties

Date: 2026-10-09
Scientific disposition:
**R2B_CONTROLLED_TUF_CONTRACT_RELATIVE_MERGE_CALIBRATED_B9_TIE**.

This is NOT R2_NATIVE_BIDIRECTIONAL_PASS (A remains open) and NOT
R4_INDEPENDENT_VALUE_SHOWN. No new native holdout or publication-strength
general algorithm claim.

## Prescore chronology (fixed before first R2B native call)

1. Experimental root/targets signing contract and exact test-key derivation
   frozen: 00_R2B_CONTROLLED_NATIVE_PRESOURCE_FREEZE.md,
   commit 2be161c570463f58e3cae526d634e3223e568c72.
2. Deterministic source-only cryptographic fixtures and predictions:
   run 37904757921; commit 1d7bbcb06adb529f2235cc4c9fdbe85c079874ed;
   10/10 source-only tests; 9 public-test signed source documents;
   each source byte-for-byte reproducible across independent same-code runs.
3. Exact frozen source artifact id 11604180918, ZIP SHA256
   e45b07f9e874ca6f96ab2141cce9c1425cc5362ba037f69cf9689bd41ac9fefc.
   - internal SOURCE_MANIFEST.json SHA256:
     a44a328b76a689873dca730f724899fe1c01ffdedd87df5df36b655f070954bc
   - internal SOURCE_PREDICTIONS.json SHA256:
     c090726d0015a155df6dddf758154e189a8adf94e2c16943ddfa0531920f72ca
   - hashes independently re-opened WITHOUT native oracle:
     run 37905117469.
4. Synthetic mismatch-retention scorer tests 9/9, run 37905224575,
   no native verifier invoked.
5. Full 24/126/12 action/trace/qualification grid and exact code blobs
   frozen: 01_R2B_FINAL_NATIVE_PRESCORE_MANIFEST.md,
   commit 7d26f718619966d25867c1875fa9e28ca4e70c41.
6. Native execution only AFTER all above:
   GitHub Actions run 37905398476, commit
   dd7ed422b95cd23972f0a8696c4649d9ac4571a2.
   Artifact id 11603733312, SHA256
   86dadaaf772440708d2aa344f4cbcd607480b8db772434eda06f3c8e8fbb1f15.
   Native client tuf-js@3.0.1 with pinned npm package lock.
   Native checker did NOT read the source-only prediction JSON;
   join-only score was computed after native raw results were saved.

## Native results

Controlled test signing keys are deterministic public TEST-only Ed25519
material, distinct from and unrelated to production credentials.
All controlled states derive via authenticated native root updates
from ONE shared self-signed genesis anchor, not independent trust stories.

Registered evidence states: six:
  {s2a,s2b}, {s3a,s3b}, {s4a,s4b}.
Registered root-update actions: submit-root-3-a, submit-root-3-b,
submit-root-4-a, submit-root-4-b.
Every action and every continuation history was fixed before scoring.

| Native probe | Registered | Exact matches | Error |
|---|---:|---:|---:|
| Root state/action result AND actual native successor identity | 24 | 24 | 0 |
| All registered future action words length 0..2 (6*21) | 126 | 126 | 0 |
| Native top-level targets delegation authorization checks | 12 | 12 | 0 |
| Native setup failures | — | 0 | — |

Native root-update results: 8 ACCEPT, 16 REJECT.
Native targets-role qualification results: 6 QUALIFIED and 6 UNQUALIFIED.
Native checker distinguished candidate metadata identity, not root version
alone, including accepted or rejected branches.

## Genuine but contract-relative B

Native tuf-js verifies that, at every one of three shared-root-role,
shared-version state pairs:
- signed initial root source documents genuinely differ;
- root-role keys and thresholds match, but the authenticated *targets*
  role accepts a different valid signer key in the A and B states;
- native delegate verification accepts targets-A and rejects targets-B
  in branch A and does the reverse in branch B;
- all 21 registered root-update-only action words per branch induce the
  SAME outcome trace (and source-derived transitions match exact native
  successor IDs, with provenance retained).

Therefore under the EXACT frozen ROOT_UPDATE_ONLY J_root contract the
decision quotient legitimately groups:
  {s2a,s2b}, {s3a,s3b}, {s4a,s4b}
and gets 3 decision classes from 6 AUTHENTICATED, noncosmetic sources.

Under J_root + TARGET_ROLE_QUALIFICATION the A and B states MUST NOT be
merged; source identities and their distinct target-authority certificates
are retained for audit. No claim of universal TUF equivalence.

This is **controlled native causal-mechanism feasibility evidence**,
not naturally arising production repetition and not future-separation A.

## Fair strong baseline: a serious negative for unique EEQ novelty

Pre-frozen expert B9, permitted full source/authority information,
may retain ONLY the trusted root version for J_root on this
registered signer/role-fixed carrier:
- B9 native action accuracy 24/24;
- same admissible legal contract, zero unsafe actions;
- a conventional exact Moore quotient of the SAME derived graph also
  gives the same 3 decision classes.

We do NOT beat either. General EEQ-specific advantage is NOT established.
Without a preregistered improvement on source-to-model certification,
multi-family maintenance cost, matched decision coverage or total cost,
this is a standard quotient feasibility demonstration.

## Scope and remaining obligations

- No new original v1 G5 cases; 285 stays 285; no prior G6/G7 or G4 changes.
- TUF controlled Ed25519 fixtures are not production root chain data.
  Historical Bottlerocket production R1 remains separately 56/56 with
  zero nontrivial merges, not replaced by this controlled result.
- R2 A action-induced future distinction is UNOPENED;
  do not fake it by hiding existing targets-role checks.
- Material missing-source/REFUSE native-boundary pressure remains OPEN;
  a source-file absence is SOURCE_UNAVAILABLE, not native REJECT.
- R3 independent multi-support dynamic Kubernetes carrier and R4
  prespecified method-independent benefit vs B9 remain OPEN.
- R5 new untouched family remains UNOPENED.
- Main branch, original G4 protocol, legacy B10 and X.509/in-toto
  holdout evidence unchanged.

**Disposition: R2B_NATIVE_B_ONLY_PASS; R2_COMPLETE=NO; R4_B9_TIE.**
