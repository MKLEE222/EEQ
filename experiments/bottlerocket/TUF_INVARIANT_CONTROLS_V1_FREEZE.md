# TUF Section-7 invariant controls v1 — freeze before native execution

Protocol parent: `parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md` at
`c15b212ad0c2be3856a03d38802aaffa628aefd1`.

Status: **development-family negative-control freeze before native execution**.

These controls exist specifically for Section 7 of the frozen protocol:
each perturbation changes real bytes/metadata/history while preserving the
registered decision-relevant qualification/continuation relation and is
predicted **not** to alter the native action.

The earlier `TUF_NEGATIVE_CONTROLS_V1` replay/unsigned/tamper tests are useful
adversarial/robustness tests but do not satisfy this Section-7 invariance
definition because they intentionally induce native rejection.

## Native oracle

- family: TUF / Bottlerocket production root chain
- native library: `tuf-js@3.0.1`
- native operation: `TrustedMetadataStore.updateRoot`
- registered action vocabulary: `ACCEPT/REJECT`
- source inventory: frozen Bottlerocket roots 1..8
- evidence class: `CONTROLLED_NATIVE` for the perturbed bytes, anchored to
  production-authored root metadata.

## NC1 — JSON serialization perturbation

History: trusted production root 1 -> candidate production root 2.

Perturbation:
- parse the exact frozen root-2 JSON;
- re-encode the identical JSON value as compact UTF-8 JSON;
- require perturbed bytes SHA256 != original bytes SHA256;
- require parsed JSON value equality with the production root.

Prediction: **ACCEPT**.

Rationale: TUF signature verification authenticates the canonical signed
payload; changing outer JSON serialization whitespace/layout must not change
the root-transition qualification or continuation relation.

## NC2 — signature-array order perturbation

History: trusted production root 1 -> production root 2 (unmodified setup),
then candidate production root 3.

Perturbation:
- parse the exact frozen root-3 JSON;
- require at least two top-level signatures;
- reverse only the top-level `signatures` array;
- leave the complete `signed` object unchanged;
- require perturbed bytes SHA256 != original bytes SHA256;
- require parsed `signed` value equality with the production root.

Prediction: **ACCEPT**.

Rationale: signature ordering is not a qualification distinction. The same
authorized signatures over the identical signed payload remain available.

## Failure discipline

- A byte-equality precondition failure is retained as
  `PREEXCLUDED_OUTSIDE_REGISTERED_CONTRACT`; it is not silently replaced by
  another perturbation.
- A native REJECT for either admitted control is retained as a mapping/semantics
  failure.
- No alternative control is substituted after observing a native result.
- These controls add **zero** G5 semantic cases.
- They do not alter the frozen generic compiler, case definition, or final
  fifth-family holdout.

The fifth-family holdout remains **UNOPENED**.
