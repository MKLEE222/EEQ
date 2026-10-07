# Generic G4 adapter -> WFC compiler v1 — freeze before scoring

Protocol parent:
`parityplus/g4/FREEZE_MANIFEST.md` at
`c15b212ad0c2be3856a03d38802aaffa628aefd1`.

Adapter schema parent:
`parityplus/g4/adapter_schema_v1.json`.

Status: **development compiler freeze before any 285-case generic-compiler
score is inspected**.

This freeze does not alter G4, does not open the fifth-family holdout, and does
not claim global minimal coding, minimum bits, a new graph-coloring result, or
a generic quotient theorem.

## Separation boundary

Family-specific native semantics end at the adapter boundary.

- `emit_adapter_v1.py` maps the already registered APT and Kubernetes
  development carriers into the frozen `eeq-adapter-v1` C1/C2/C3 interface.
- `emit_tuf_adapter_v1.js` maps the Bottlerocket production root carrier into
  the same interface. It recomputes cryptographic qualification witnesses from
  the frozen root bytes with `@tufjs/models@3.0.1`; it must not infer signer
  qualification from the native ACCEPT label.
- `compile_wfc_v1.py::compile_wfc()` is the generic compiler. No
  family/domain identifier is passed to this function and no family/domain
  branch is permitted inside it.

The native action label is joined to an evaluation row only after the adapter
or compiled representation has been constructed.

## Frozen compiler object

For each registered claim, the compiler retains the declared compatible
support routes together with:

- source identity and provenance;
- authentication predicates;
- native qualification predicates;
- support-to-claim binding.

This is the **qualified support frontier**.

The compiler also retains:

- registered action vocabulary;
- action-conditioned successor relation;
- post-action observations;
- continuation contract;
- native action vocabulary.

This is the **transition/continuation frontier**.

The B10 representation is the canonical pair:

[
(	ext{qualified support frontier}, 	ext{transition/continuation frontier}).
]

Canonicalization sorts claims, support routes, qualification/authentication
atoms, and claim-binding atoms without using a scored native outcome.

## Lawful-information audit

The compiler recursively rejects the G4 forbidden fields:

- `scored_native_outcome`;
- `post_hoc_expected_label`;
- `reviewer_only_annotation`;
- `future_information_unavailable_at_decision_time`.

The scoring workflow must additionally perform a label-permutation leakage
test: change evaluation labels after adapter construction, recompile, and
verify that every compiled B10 representation is byte-identical.

## Scope of the claim

This compiler is a semantic compilation layer from frozen native adapter
semantics to a canonical future-decision frontier.

It **does not** claim:

- the globally smallest representation;
- the minimum number of retained fields or bits;
- uniqueness among all sufficient representations;
- novelty of generic quotienting, bisimulation, reducts, or zero-error coding.

The only question scored in this development run is whether the same frozen,
domain-agnostic compiler preserves the registered future-decision distinctions
on every currently closed development carrier.

## Freeze discipline

Any post-score change to:

- `emit_adapter_v1.py`;
- `emit_tuf_adapter_v1.js`;
- `compile_wfc_v1.py`;
- this freeze document,

creates a new compiler version. Results from v1 remain attached to this frozen
version.

The fifth-family holdout remains `UNOPENED`.
