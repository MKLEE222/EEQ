# E2-P1 actual result: native-source hashes do not entail qualified Boolean leaves

Date: 2026-10-10.
Scientific status: E2_P1_GENERIC_CHECKER_NOT_STANDALONE_NATIVE_SEMANTIC_VERIFIER.
Evidence class: POST-SOURCE-ONLY synthetic attack on OLD already-scored E2 IR. No new native/Kubernetes calls, no extra G5.

## Original E2 remains unchanged
- Original E2: Actions 38032779592, SUCCESS 46 tests and 16/16 native-SOURCE-ONLY development IR/B9 matches. Artifact 11662422247 SHA256 a7609ac01eacb667282ef4fe02331c38b0913369358602b0e35cc041d3217fd5.
- P1 two attacks PRE-REGISTERED in 00_P1_POST_E2_SOURCE_LEAF_FORGERY_FREEZE.md commit 7b5b03dd95a3f62d63138d205e42dc804741ec28, before attacker code.
- First P1 CI 38033018972 FAILED on Python import syntax prior to opening old E2 archive; this remains an infrastructure/implementation failure. V1 narrow syntax correction was frozen separately at 4b2321f507aa8bd47f7924d7a43c23b1a000b1d4 before changing the code; no attack selection or success condition changed.
- P1 successful CI 38033101279 commit c69704895c2ddfd0016160ef90103e7b374f97f4: 10/10 fake-unit source qualification attack checks, then verified untouched E2 ZIP/SHA and executed exactly two registered postsource attacks.
- P1 artifact 11662757411, ZIP SHA256 60a33019bab1fb70887aed8da240ae5138e0024649c337c916ee47fa695f0145. Source bytes modified: zero. Original old E2 scored IR modified: zero. New native calls: zero.

## Two preregistered independently checked falsifications

1. TUF case TUF|s2a|root-3-b: original full source B9 says root update REJECT due missing qualified old-root signature. On a COPY of identical IR/source-digest map, FALSE old-root signer leaf was flipped TRUE. The exact E2 generic checker accepted the altered program as structurally valid and inferred WRONG authorized update TRUE.
2. K8s case K8S|A2_BINDING_ADDED|default: original source-only B9 says registered scoped VAP Deny TRUE. On a COPY of identical IR/source-digest map, exactly one third-binding TRUE CEL failure leaf was flipped FALSE. The generic checker accepted structurally valid program and inferred WRONG scoped VAP Deny FALSE.

Both original standalone checker results were false with respect to independently source-derived B9 but syntactically verified. This does NOT imply actual Kubernetes global admission ACCEPT: scoped no-registered-VAP-denial is not global API permission. The complete E2 original source-only compiler plus direct B9 cross-check was correct on its old 16 development samples, not falsified here.

## Scientific inference

Source SHA256 references plus an AND/OR/THRESHOLD AST prove at most lineage and Boolean bookkeeping, NOT that source bytes entail a cryptographic signature or Kubernetes selector/CEL qualification. The missing trusted base is independent primitive semantic checking of ALL emitted proof leaves, including old/new source/actor and inventory authorization, freshness and claim contract.

A next P2 must tie each leaf to a directly checkable primitive over immutable original source bytes (TUF Ed25519 and root-role thresholds; K8s exactly registered VAP+Binding CEL/selector with authoritative class membership). Missing or unqualified live source -> REFUSE, not fallback to the author-supplied Boolean. An updated primitive witness checker is itself standard proof-carrying-data/authorization prior art; fully informed B9 has all the same tools and may copy its code. Only a separate non-reducible science claim or independently staffed prospective P3 full-cost comparison could establish new H3 value. Current H3 remains NOT ESTABLISHED.

Main b5434ab1ad317e5121c88b632806880f903774db, original G4 c15b212ad0c2be3856a03d38802aaffa628aefd1 and blob 3eeaeeb828d2fcf7ec4487da06489fee3146c920, old B10 blob 9a6bff7a2b8db73b86b6952c706852c92b1a4b1d, G5=285, G6 full C1 disputed, G8 open, fifth family sealed holdout untouched, old W1 V1 failure retained.
