# 5-Spot G4 representation adapter v1 — development freeze

Protocol parent: `c15b212ad0c2be3856a03d38802aaffa628aefd1`.

Carrier semantic freeze:
`2e2bc28ff52678b0a6fc0ba75f851134fb123d55`.

Native evidence run:
`37565593683`.

Status: **development post-native / pre-matrix freeze**. This mapping is
frozen before any B0–B10/O1–O8 score for the 5-Spot carrier is inspected.
It is not holdout evidence and does not change G4.

The representation builder may read the mechanically deduplicated semantic
signature only. It must not branch on `native_action`.

## Applicable representations

- B0: full registered semantic state.
- B1: current Pod object view: namespace, service account and security posture.
  The namespace name is retained because it is part of the submitted object;
  no hidden binding label is injected.
- B3: policy/authorization qualification: binding scope and service-account
  identity.
- B6: retained request state without a future continuation contract.
- B7: frozen public-policy mechanism forecast.
- B8: static derived view of binding applicability, agent identity and security
  predicates.
- B9: protocol-native hand-engineered sufficient state: binding applicability,
  agent identity and registered security profile.
- B10: EEQ/WFC adapter-state pilot consisting of qualified policy scope,
  claim-bound identity/security posture, and registered CREATE action.

B10 remains an adapter-state pilot; the generic EEQ/WFC compiler is not yet
integrated.

## Frozen omissions

- O2 no qualification: retain only the submitted security posture; drop both
  binding-scope qualification and service-account exemption identity.
- O3 no claim binding: retain binding scope and service-account qualification,
  but remove the security posture to which the decision applies.

## Frozen non-applicability

B2 is not applicable because the registered carrier has no authentication or
cryptographic-validity distinction.

B4/B5 are not applicable because there is one pinned public policy source and
no registered provenance alternatives.

O1 is not applicable for the same single-source reason.

O4/O5/O6/O7 are not applicable because this is the complete registered
one-step admission horizon; there is no prior continuation history, future
continuation contract, or later action-induced evidence transition.

O8 is not applicable because exactly one registered matching VAP/binding
support mechanism is in scope.

No NA cell may be replaced with an invented numeric result merely to make the
matrix dense.

The fifth-family holdout remains unopened.
