# R4-E2 PRE-CODE source-derived obligation compiler — registered development scope

Date: 2026-10-10. Branch eeq-r4-e2-source-rule-compiler-20261010.
Parent R4-E1 @ f999ffd1384a23fb9d920aac1a8ca5ab1386986a, E1 source-free run 38032262890.
**STATUS: PRE-IMPLEMENTATION. NO NEW NATIVE TEST, NO P3 HUMAN STUDY, NO UNSEEN TRANSFER.**

## Why E1's 17/17 success is not enough

E1 finite legal-query frontier and impossible-world witnesses are *exactly reducible* to a restricted weighted Boolean decision tree plus partial-information equivalence classes. Fully informed same-access B9 ties 17/17. In particular, E1 receives source-qualification TRUE/FALSE as an AUTHOR-supplied input. That is precisely what EEQ must stop assuming to demonstrate a native scientific contribution.

E2 first pressure: can a small label-blind, source-backed compiler infer *qualified proof obligation structure* from the actual TUF root-role metadata / signatures and the actual Kubernetes ValidatingAdmissionPolicy+Binding selector / CEL grammar, and emit a SAME generic typed AND/OR/THRESHOLD rule IR checked without domain-specific expected answer tables?

This must NOT be presented as a universal generic semantics compiler. Native domain parsers and original crypto verification routines remain essential, standard existing techniques, and FULL B9 is permitted to reuse all code, inputs and the same IR. A correct 16/16 source-side result is feasibility only. One measured failure of allowed source parsing/authority must abort, not silently default to false/ACCEPT.

## Frozen input/native provenance, old cases ONLY

TUF: EXACT pinned deterministic TEST source generator `experiments/native_distinction_relaunch/r4/r4_d0_tuf_sources.js` Git blob `05331a87bc2a04531167fedbb5b554ed91ce6181`, associated old R1b-v3 cryptographic helper and established TUF spec v1.0.36. Generate seven public Ed25519 signed root source envelopes from `sourceFixtures()` only, and two root2 states x four same-signed-payload root3 candidate envelopes. Compiler must never import `build().predictions`, native `tuf-js` outcome or archived pre-scored label. Verify candidate canonical signed bytes under actual keys; old root role must satisfy old authorized keys+threshold, new root role must satisfy new authorized keys+threshold; exact version succession also required. Root2 setup from a common anchor must be cryptographically source-verified, not assumed simply because version=2.

Kubernetes: EXACT old source JSON bytes (M1):
- r3_m1/sources/policy.json blob c22a8134447649d202a49b644ddb8485835c0fc2
- r3_m1/sources/binding-team.json blob 2bc5a5706910196c5cd0631c4034ca3ccdbb890b
- r3_m1/sources/binding-mode.json blob 357ef4bd582f47e2308f6e640307077bafe47b68
- r3_m1/sources/namespace.json blob 428f16bc92ac27dec26b87ad24951113cf463922
- r3_m1/sources/pod-flux.json & pod-default.json pinned via exact current Git blobs before F2 first run.
And M3 third sources:
- r3_m3/sources/policy-third.json blob ae7ab92b2d15f7793ec41232752efc2c30ebf347
- r3_m3/sources/binding-third.json blob e2a774ee92c2af6411e1a516e48af4695f096088.

Phase membership grammar is the ORIGINAL already-scored R3-M3 authored protocol: T0 old two bindings; T1 third policy without third binding; T2 third binding added; T3 third binding removed (third policy remains). This is NOT a fresh authoritative native LIST closure or prospective data. Within each phase, compile OR across all *explicit registered active bindings* of AND(selector match for fixed namespace, registered exact CEL failure for fixed Pod) by parsing native source bytes. Must independently reject unregistered CEL grammar, matchExpressions/params, missing policy source, wrong policyName, undocumented binding action, duplicate/missing identity, source tampering or extra unregistered Bindings.

## Generic IR as F2 implementation target

A typed evidence rule AST:
- ATOM(status true/false, source_id and source SHA256 identity, authority/qualification predicate, scope);
- AND(children), OR(children);
- THRESHOLD(k, children) for both TUF old/new independently authorized signer roles.
- Shared checker NEVER contains string matches for TUF/Kubernetes policy names, source key labels, or registered expected outcome lists. Empty AND/OR, empty threshold list, k outside 1..len children, nonboolean atom and duplicate proof ID all refuse. Refusals distinguish missing SOURCE_UNAVAILABLE from unsupported semantics.
- Every emitted leaf needs native-source lineage and source material digest; the emitter must not populate leaf bool from previously scored native/prediction labels.
- The generic interpreter should compute only `TUF_ROOT_UPDATE_AUTHORIZED / REJECT` and `K8S_SCOPED_VAP_DENY / NO_REGISTERED_VAP_DENY`, NEVER GLOBAL_K8S_ADMISSION_ACCEPT.
- New source unauthorized/missing/not pinned => explicit REFUSE, never silently assumed absent.
- Scope/actor and original source-set closure assumed by this controlled contract are recorded as UNPROVEN externally; the IR does not become a signed native authority certificate.

## Fixed DEVELOPMENT-REUSE cross product, no case selection

TUF exactly 2 trusted roots x4 candidate source envelopes = **8** source-only rows. Expected authorized root update TRUE for exactly (s2a,root-3-a) and (s2b,root-3-b), FALSE for the other **6**. These native outcomes were ALREADY scored as R4-D0; F2 compiler must not access those old labels to construct its input.

K8s exactly 4 registered phases x2 Pod probes = **8** source-only rows. Registered scoped VAP Deny:
- T0 flux TRUE, default FALSE;
- T1 flux TRUE, default FALSE;
- T2 flux TRUE, default TRUE;
- T3 flux TRUE, default FALSE.
Previously native observed in R3-M3, original V2 gate FAILED and V2b calibration is retrospective. These F2 rows are NOT a prospective native oracle.

Total 16 source-side compiler outputs. Primary science gate is **rule-source extraction + lineage completeness + failure on unsupported authority/grammar**, not numerical accuracy. A generic verifier must independently recompute Boolean AST semantics; direct domain-specific source-only B9 reference must get all 16 with equal access. Exact equality, no group pruning or changed denominator.

## Fixed adversarial source mutations prior to scoring

TUF: wrong signer key cannot become verified; duplicate signature keyID cannot inflate threshold; root-version-only shortcut must fail on same-version different old authorized signer; expired/untrusted root invalidates; absent candidate signature source must REFUSE if source bytes unavailable; unrelated targets changes must not affect ROOT-only claimed dependencies.
K8s: unauthorized third Binding must invalidate former negative (no Deny) scoped certificate; standalone third policy without Binding has no Deny; missing policy/binding source, wrong CEL grammar, additional matchExpressions/parameter sources, changed selector key, malformed object identity or altered source Git blob must not be silently accepted; a complete source roster CANNOT be established just by author `complete:true`.

## Fairness, prior art, abort

Source-only parser B9 may use identical complete root metadata, Ed25519 verifier, Kubernetes CEL subset, selector engine and same AST/generic code. All source-specific code including grammar and manifest construction MUST be counted toward complexity; cannot show implementation cost advantage absent independent prospective P3 maintainers. Compositional AND/OR/THRESHOLD rule evaluation, K8s native interpretation, TUF role signature threshold verification and ordinary provenance are already known; E2 common IR is not novel on its own.

If a Boolean atom remains author-populated rather than derived from actual supported native source bytes OR authenticated role qualification, mark `E2_COMPILER_NOT_ESTABLISHED`. If a static authored phase membership is treated as a global complete native list, mark `SOURCE_AUTHORITY_OVERCLAIM`. If all 16 source-only rows pass, maximum status `R4_E2_BOUNDED_SOURCE_TO_RULE_COMPILER_DEV_FEASIBLE_B9_TIE`.

No new original main G4/B10 edits; original G5=285, G6 global C1 disputed, G8 open and fifth-family holdout unopened. No old native result is used as fresh transfer.
