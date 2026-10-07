# G7 X.509 holdout adapter freeze v1

Protocol parent:
`parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md` at
`c15b212ad0c2be3856a03d38802aaffa628aefd1`.

Generic compiler parent:
`experiments/common_evaluation/GENERIC_WFC_V1_FREEZE.md` at
`062be7f533977d45e879a8026a3034913d1a6a57`.

Source metadata:
`experiments/x509_holdout/X509_HOLDOUT_SOURCE_METADATA_V1.json`.

Case grid:
`experiments/x509_holdout/X509_HOLDOUT_CASES_V1.json`.

Predictions:
`experiments/x509_holdout/X509_HOLDOUT_PREDICTIONS_BEFORE_NATIVE_V1.json`.

Status: **adapter semantics frozen before any X.509 native holdout scoring**.

## Native contract

Family: OpenSSL X.509 certification-path validation.

Native version:
`OpenSSL 3.0.13 30 Jan 2024` on `ubuntu-24.04`.

Registered action:
`VERIFY_X509_TLS_SERVER`.

Native vocabulary:
`ACCEPT/REJECT`.

Every case disables the default CA path/store. An explicit CA file is supplied
only when the frozen case specifies a trust source. `auth_level=0` is part of
the registered contract so the holdout tests path/trust/claim/time semantics,
not changing cryptographic-strength policy.

## V0 lawful-information boundary

The adapter may read only:

- pinned badssl source identity and SHA256/fingerprint metadata;
- target subject/issuer/SAN/basicConstraints and preflight purpose metadata;
- trust-source subject/issuer/basicConstraints and pinned identity;
- frozen hostname, verification time, purpose, auth level and trust-selection
  parameters.

It may not read:

- `openssl verify` exit code/stdout/stderr;
- any expected label from the separate prediction file;
- a post-hoc native error class;
- reviewer-only annotation.

## C1 support coverage

Registered claim:
`x509-server-identity-valid`.

Support atoms:
- target leaf certificate;
- selected explicit trust source, or an explicit missing-trust placeholder.

The adapter retains each source identity, provenance path, SHA256 fingerprint
and compatibility status. Missing or wrong trust is represented, not silently
dropped.

## C2 qualification fidelity

Frozen qualification predicates include:

- hostname appears in the target SAN set;
- verification time is within the target validity interval;
- requested purpose is compatible with the target's preflight purpose metadata;
- trust source is present;
- trust source equals the registered Superfish root;
- trust source is CA-qualified;
- target issuer DN matches selected trust-source subject DN.

Authentication/source-integrity predicates include whether target and selected
trust bytes are pinned to the preflight inventory.

These predicates are derived from source metadata and case parameters only.
They are not inferred from native verification outcomes.

Claim binding retains:
- target fingerprint;
- hostname;
- purpose;
- attime;
- selected trust-source fingerprint/identity.

## C3 transition/objective fidelity

Action:
`VERIFY_X509_TLS_SERVER`.

This carrier is a complete one-step validation horizon. The transition object
retains the target certificate identity and the verification context. There are
no post-action observations available to the pre-decision adapter.

Continuation contract:
- permit the TLS-server identity claim only under the registered target,
  hostname, purpose, attime, trust-source selection and auth-level context;
- default trust path/store remain disabled;
- native action vocabulary is `ACCEPT/REJECT`.

## Generic compilation

The adapter output must conform to unchanged `eeq-adapter-v1`.
It is fed directly to the already frozen domain-agnostic
`compile_wfc_v1.py::compile_wfc(adapter)`.

No X.509 family branch is permitted in the generic compiler.

If this mapping cannot be represented without changing the adapter schema or
generic compiler core, G7 disposition is
`HOLDOUT_FAIL_CORE_CHANGE`.

The fifth-family native outcomes remain **UNOPENED** at this freeze.
