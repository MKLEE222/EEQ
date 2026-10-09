# R4-C0 Cross-Family Qualified-Transition Certificate — DEVELOPMENT PRERUN FREEZE

Date: 2026-10-09
Status: C0 DESIGN FROZEN BEFORE C0 IMPLEMENTATION OR C0 RUN.
Not original R4-P3 adaptation-performance pre-registration.

## Core scientific question

Can a common, independently readable SOURCE-QUALIFICATION-ACTION-OUTCOME
certificate contract cover two already validated native-system contrasts,
WITHOUT pretending their lawful semantic adapters are interchangeable?

The goal is a software interface feasibility pressure test. It may show
common certificate accounting, fail-closed semantics and source identity
validation. It does NOT demonstrate a generic extractor, novelty beyond
provenance/verification literature, or a cost win against strong B9.

## Preselected, PREVIOUSLY SCORED DEVELOPMENT evidence

TUF R4-D0 controlled source/native evidence:
- source-only artifact 11608811184; ZIP SHA256
  2490380d7424bc7f86216cfeb691ab0c90e8a412d65ff1a3887db3aec135a26d
- source manifest SHA256
  268e9244b57ca7c0a305434be3085d02e4d02d4085bf419bffb6f84045c7736a
- source predictions SHA256
  fa8dd5a40667dea0acd9984d2d5ab0c33ea2148cef314fbc9751df34805d8aa0
- native artifact 11609456107; ZIP SHA256
  6717ce540a556951dd01f5a9e34a724df17c37564f16e2c034ed75dbb60e745c
- 2 old-root states x 4 candidate root updates = 8 cases,
  2 native anchor setup controls. Source verification of old/new root
  cryptographic signer threshold MUST be REAL, never inferred from labels.

Kubernetes R2A controlled development source/native evidence:
- source-only artifact 11604865804; ZIP SHA256
  84704d3e070bcc20543278c76166fedcdff2a73dcbe9762b7a2236c954a7a00e
- source manifest SHA256
  c9a5b954d3b3e93ebbe9e55fc1a26885dbcef6e241cc6c0c93af2159f8cb0efa
- source predictions SHA256
  c5a8050790648afe6d28c4c444ec0b256d1cca56e40b5404e4b24c55810765e1
- native artifact 11604423996; ZIP SHA256
  1d644a8e98497d097a4b3b4e4354180bfff5bea144ccf89c2790b34bd43fc70c
- 2 binding histories x 2 phases x 2 native dry-run Pod probes = 8
  decisions, plus 4 unbound controls and 2 real namespace label updates.

These sources were already examined in previous development workflows.
The new C0 run is a **POST-NATIVE REUSE/INTEGRATION DIAGNOSTIC**.
It is NOT NEW independent validation or unseen-family transfer.

## Minimal common certificate interface

For each registered native decision emit exactly one immutable certificate:
  schema = eeq-r4-qualified-transition-certificate-v0
  domain = tuf_root_update | k8s_admission
  contract_id = explicit family+allowed action/claim scope string
  case_id = deterministic state/action label or binding/phase/pod label
  sources = nonempty {role_or_reference: original_SOURCE_SHA256}
  original_state = original source-scoped identity
  qualified_obligations = list of typed, domain-verified premises
  action = exact registered action name
  outcome = ACCEPT | REJECT | MODEL_UNSUPPORTED | SOURCE_UNAVAILABLE
  native_observation = independently archived native ACCEPT or REJECT
  successor_state = source-derived scoped successor state/label identity
  native_successor = observed native full state, if defined by contract
  checker_outcome = VERIFIED | MISMATCH | UNSUPPORTED
  verifier_domain = source-rule/signature verifier adapter name/version
  provenance = source artifact ID + native artifact ID (non-secret IDs)

The common *structural* checker MAY:
- reject missing/hash-invalid source documents and duplicate/missing case IDs;
- check typed certificate completeness, cohort scope and denominator;
- reject invalid decision/UNKNOWN conflation, unsupported-as-match;
- compare native outcome and successor to source-derived claim;
- enforce explicit source/actor/claim/action scopes;
- count whether raw evidence was present, checked and full coverage retained.

It MUST NOT pretend to verify domain cryptography or native selector
semantics from a generic JSON shape alone.

## Required domain-specific proof adapters, independently replayed

TUF adapter: verify original signed root JSON source SHA256 and Ed25519
signatures over TUF OLPC canonical signed bytes with authorized keyIDs,
OLD and NEW role threshold and exact next-version condition. Source-derived
effect and source identity checked against independently recorded native
root decision and full signer-envelope successor ID. Use existing verified
TUF crypto primitives, NOT the v1 R4-D0 source predictor's output labels.

Kubernetes adapter: independently read exact frozen VAP CEL predicate
(for ONE whitelisted grammar), binding namespaceSelector.matchLabels,
Pod serviceAccountName, source namespace labels and action
UPDATE_NAMESPACE_LABEL; recompute qualified policy applicability and
expected source decision for both phases. Verify recorded native
resourceVersion and labels actually changed; verify target-policy denial
attribution, the 4 unbound controls and independent two cluster contexts.
No arbitrary CEL parsing or fabricated native successor states.

All already scored native evidence remains immutable. If either adapter
cannot validate its source signature/selector or exact native row, return
UNSUPPORTED/MISMATCH; do not skip the corresponding certificate or change
its denominator.

## Fixed denominators, scope, and negative controls

C0 main certificate rows: 8 TUF + 8 Kubernetes = **16**.
Native setup controls: 2 TUF.
Native unbound controls: 4 Kubernetes.
Native action resourceVersion proofs: 2 Kubernetes.
Every source SHA must match its original frozen artifact.
No new native API or TUF verifier call is permitted in C0 integration:
it rechecks from immutable evidence and compares archived native results.

C0 synthetic mutations must fail:
- missing signed source file, changed source hash;
- TUF old/new root cryptographic signature tamper;
- TUF incorrect full signer-envelope successor;
- Kubernetes selector/source label change without re-freeze;
- missing/bad namespace resourceVersion update;
- native ambiguous unrelated admission denial;
- missing source/cell and treating unsupported as ACCEPT.

These are required test intentions; actual tests/results must be reported
honestly and a missing test is NOT a pass.

## Novelty veto and fail-closed boundary

Standard signature verification, attribute/predicate checking, typed proof
records, provenance and incremental dependency tracking are prior art.

C0 successful 16/16 envelope checks means ONLY:
  C0_COMMON_CERTIFICATE_INTERFACE_FEASIBLE_ON_PREVIOUS_DEVELOPMENT.
It does not mean 2 native families share one lawful state extractor:
adapters remain explicit domain-trusted code. A strong B9 may use the SAME
certificate interface and all lawful information. Any claimed advantage
must await new primary P3 (domain adaptation effort) with independent task
assignments, full cost accounting, uncertainty and B9 parity guardrails.

No original EEQ G4/B10 or G5/G6/G7 history changed; no new original G5
cases. Keep main unchanged. All C0 failures and mismatches retained.
