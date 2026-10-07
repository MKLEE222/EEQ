# Bottlerocket TUF representation adapter v1 — development freeze

Protocol parent: `parityplus/g4/FREEZE_MANIFEST.md` at commit
`c15b212ad0c2be3856a03d38802aaffa628aefd1`.

Status: **development post-native / pre-matrix freeze**.

This adapter instance is frozen after the production root chain was natively
verified and before any Bottlerocket B0–B10 / O1–O8 matrix is scored. It is not
presented as a pre-native preregistration and is not holdout evidence. The
representation builder may read only the frozen root bytes 1..8, the frozen G4
case ledger, and `@tufjs/models@3.0.1` cryptographic verification semantics. It
must not branch on `native_action`, a native decision field, or any matrix
score while constructing a representation.

The final fifth-family holdout remains unopened.

## Registered semantic carrier

Environment: Bottlerocket public updater metadata,
`aws-k8s-1.35/x86_64`.

Production-authored roots 1..8 are pinned by
`experiments/bottlerocket/FROZEN_SOURCE_INVENTORY.md`. The seven registered
actions are adjacent root updates 1→2 through 7→8. Root 9 returning HTTP 403 is
a source boundary, not a native rejection.

Registered action: `ROOT_UPDATE`.

Future contract: `TUF_ROOT_CHAIN_CONTINUATION`.

Native action vocabulary: `ACCEPT / REJECT`.

The lawful root-transition state contains:

- previous trusted root version, root-role threshold, root-role key IDs and
  signed-byte identity;
- candidate root version, root-role threshold, root-role key IDs, signatures,
  signed-byte identity and consistent-snapshot flag;
- signatures on the candidate that cryptographically verify under the previous
  trusted root role;
- signatures on the candidate that cryptographically verify under the
  candidate root role itself;
- version adjacency and the candidate root role that becomes the next trust
  anchor.

The two distinct qualification obligations are retained: authorization by the
currently trusted root and candidate self-authorization. Their conjunction with
version adjacency is the protocol-native sufficient state for the registered
root transition.

## Frozen B0–B10 mapping

- **B0 full lawful history oracle**: previous root, candidate root,
  cryptographic qualification witnesses, continuation state and structural
  delta.
- **B1 current artifact only**: candidate root only, including its signatures
  and byte identity; previous trust is omitted.
- **B2 crypto validity only**: counts/booleans for valid previous-root and
  candidate-root signature support, without provenance/history payloads.
- **B3 authority/authorization only**: previous and candidate root-role
  thresholds/key IDs, without signature observations or lineage.
- **B4 provenance/lineage only**: from/to versions and pinned signed-byte
  identities.
- **B5 authority + provenance**: B3 and B4 together.
- **B6 retained history without continuation contract**: previous/candidate
  root state and valid signer identities, but no explicit next-trust contract.
- **B7 behavioral/predictive state**: coarse transition features only
  (key-rotation counts, threshold change, signature count, version gap).
- **B8 static view/reduct-inspired**: candidate-root summary only.
- **B9 protocol-native hand-engineered sufficient state**:
  previous-root authorization, candidate self-authorization, version adjacency.
- **B10 EEQ/WFC adapter-state pilot**: qualified support for both authorization
  obligations, candidate claim binding by signed-byte identity, and
  continuation contract identifying the next trust anchor.

B10 remains an adapter-state pilot; this freeze does not claim that the generic
EEQ/WFC compiler is integrated.

## Frozen O1–O8 omissions

- **O1 no source identity/provenance**: remove signed-byte hashes and explicit
  lineage identities while retaining qualification and trust-role structure.
- **O2 no qualification**: retain versions, authority sets and candidate
  signatures but remove cryptographic-validity/qualification witnesses.
- **O3 no claim binding**: retain qualified signer identities and continuation
  state but remove the candidate signed-byte binding.
- **O4 no continuation history**: remove previous trusted-root state; retain
  candidate self-qualification and candidate identity.
- **O5 no continuation contract**: retain both root states and qualification
  witnesses but omit the explicit next-trust/adjacency contract.
- **O6 static action model**: candidate-only state; suppress the transition from
  the currently trusted root.
- **O7 one-step/myopic horizon**: retain current authorization and version
  adjacency but omit candidate self-authorization / next-trust qualification.
- **O8 partial support coverage**: retain only previous-root authorization
  support; omit candidate self-authorization support.

## Interpretation limit

All seven production transitions in this Bottlerocket carrier have the same
native label, `ACCEPT`. Therefore the Bottlerocket matrix can audit
representation construction, applicability and byte cost, but **cannot provide
within-carrier discrimination evidence** for baseline accuracy or omission
failure. No zero-error superiority claim may be inferred from seven all-positive
rows.

Any change to this mapping after its freeze commit requires a new TUF
representation-adapter version. Native root-chain results remain attached to
their original artifact and are never rewritten.
