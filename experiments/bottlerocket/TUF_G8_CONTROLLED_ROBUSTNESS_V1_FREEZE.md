# TUF G8 prospective controlled robustness v1 — pre-native freeze

Date: 2026-10-08.
Protocol authority: G4 Sections 2, 10, 12, 14 at
c15b212ad0c2be3856a03d38802aaffa628aefd1.
Status: FROZEN TEST DESIGN BEFORE ANY NEW TUF G8 NATIVE CALL.

Native release: tuf-js@3.0.1, TrustedMetadataStore.updateRoot.
Source: Bottlerocket aws-k8s-1.35/x86_64 production roots 1..4,
exact SHA256 from FROZEN_SOURCE_INVENTORY.md.
History setup: production root 1 -> 2 -> 3 with unmodified source bytes;
all setup actions must ACCEPT or the new sample is INFRASTRUCTURE_FAILURE /
NATIVE_VERSION_UNSUPPORTED, never silently repaired.

The root-4 original accepted 3->4 transition is an already-observed
production-history positive and is used only as a reference setup. It is
NOT claimed to be fresh prospective evidence.

New controlled-native perturbations, frozen before scoring:

R3 / MISSING NONCRITICAL TOP-LEVEL METADATA:
- parse original root-4 JSON;
- add a top-level key "eeq_noncritical_observation" whose value is
  "controlled-20261008"; leave both "signed" and "signatures" unchanged;
- force byte SHA inequality; native prediction: ACCEPT;
- G8 forecast: PRESERVE_DECISION.
- If a native schema explicitly forbids additional top-level keys, retain
  REJECT as an adverse result; do not relabel the key as critical afterward.

R4 / MISSING DECISION-CRITICAL SOURCE STATE:
- parse original root-4 JSON;
- set signed.keys to an empty JSON object; retain signed.roles and version;
- force byte SHA inequality; native forecast: REJECT or, if it cannot satisfy
  the native root schema at all, PREEXCLUDED_NATIVE_SCHEMA_INVALID;
- G8 forecast: INSUFFICIENT_EVIDENCE_REFUSE.
- This R4 trial is PREDECLARED UNSCORED for binary native accuracy because
  independent native-schema admissibility of a keys-empty object has not
  been established. The native invocation/error is retained as diagnostic
  evidence only; no post-outcome decision to score or preexclude is allowed.
- A schema-invalid input is NOT counted as a native REJECT or match.

R5 / CRYPTOGRAPHIC CORRUPTION:
- parse original root-4 JSON;
- set signed.version to 5 while keeping the old signatures and other fields;
- force byte SHA inequality; native forecast: REJECT;
- G8 forecast: INSUFFICIENT_EVIDENCE_REFUSE because the signature no longer
  lawfully supports the altered signed claim. Both sequence mismatch and
  signature-invalidity may contribute to native REJECT: no sole-cause
  attribution is authorized without a separate counterfactual.

R10 / STALE REPLAY:
- after reaching trust state root3, submit unmodified production root2;
- native forecast: REJECT due to nonadjacent rollback;
- G8 forecast: INSUFFICIENT_EVIDENCE_REFUSE, not replay acceptance.

R6 / REQUIRED SOURCE UNAVAILABLE:
- do not provide any candidate root-4 bytes to the decision;
- DO NOT call native updateRoot with a fake null candidate;
- expected observation: SOURCE_UNAVAILABLE (not a native REJECT);
- G8 forecast: INSUFFICIENT_EVIDENCE_REFUSE.
- This case remains unscored in any native binary accuracy denominator.

Each R3/R4/R5/R10 uses a FRESH TrustedMetadataStore rooted at root1 with
the identical pre-execution setup 1->2->3; no cross-scenario mutable history.
Every metadata perturbation must change actual bytes; retain SHA256 of
original and perturbed bytes, error class/message, and decision time.

No trial may be replaced after seeing its outcome. No result is attached to
a previous frozen G6 matrix or retroactively credited to Section 7 controls.
These controlled-native G8 oracles are NOT EEQ operator predictions: a later
separately frozen lawful EEQ adapter/decision policy must be evaluated before
method-robustness success can be claimed.

No new G5 semantic cases. No X.509 or in-toto holdout data is used.