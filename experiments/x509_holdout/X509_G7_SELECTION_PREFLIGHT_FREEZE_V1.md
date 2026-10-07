# G7 fifth-family selection + source preflight freeze v1

Date: 2026-10-07

Protocol parent:
`parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md` at
`c15b212ad0c2be3856a03d38802aaffa628aefd1`.

G5 disposition:
`experiments/common_evaluation/G5_BREADTH_AUDIT_20261007.md`.

G6 disposition:
`experiments/common_evaluation/G6_GATE_DISPOSITION_20261007.md`.

Status: **G7 family selected; native outcome scoring remains unopened**.

## Selected unseen fifth family

Native family:
**OpenSSL X.509 certification-path validation**.

Native operation to be frozen after environment preflight:
`openssl verify` / OpenSSL X.509 path validation.

This family was not used in G0-G6 development, is semantically distinct from
APT release-info, Kubernetes admission, TUF root update, and GitHub merge
governance, and exposes independent source/trust, qualification, claim-binding
and verification-contract distinctions.

No `openssl verify` command may be executed before:
1. the exact native OpenSSL version is recorded;
2. source bytes and hashes are pinned;
3. the holdout case grid and expected native actions are frozen;
4. the X.509 adapter instance mapping to unchanged V0+C1-C3 is frozen;
5. the generic-WFC invocation is frozen.

## Public source

Repository:
`chromium/badssl.com`.

Pinned repository commit:
`bfc80f7c2bf0873e2fdc9ba79f38a5afd93570fb`.

Pinned tree:
`1d3ab2d9ec5f608c544af3e2d0d26360584fa7e9`.

Evidence license:
Apache-2.0 repository.

Pinned source files inspected before selection:

| role | path | Git blob |
|---|---|---|
| normal public chain | `certs/sets/prod/pregen/chain/wildcard-rsa2048.pem` | `63db88a8ed36d3ffb462e2124b203a44dba4c853` |
| expired public chain | `certs/sets/prod/pregen/chain/wildcard-expired.pem` | `14107878cfaef7eb728a020afa7bc6f13ba4efca` |
| self-signed public cert | `certs/sets/prod/pregen/chain/wildcard-self-signed.pem` | `60cc7ab76918a1c0fefdeb3192c2c1100c423d54` |
| incomplete public chain | `certs/sets/prod/pregen/chain/wildcard-incomplete-chain.pem` | `68acede9d6344162950edcc8c1a6e8be2d576bc7` |

The normal chain contains the BadSSL wildcard leaf followed by a DigiCert
intermediate. The holdout design will use only pinned certificate bytes; it
will not depend on the runner's mutable system CA store.

## Preflight scope

A source/environment preflight is permitted before the final holdout freeze.
It may:

- print `openssl version -a`;
- download only the pinned files above from the pinned commit;
- verify Git blob identity and compute SHA256/byte size;
- count/split PEM certificates;
- inspect certificate metadata using `openssl x509 -noout`:
  subject, issuer, serial, dates, SAN, basic constraints, key usage, EKU and
  purpose metadata;
- record the runner image metadata.

It must **not**:

- run `openssl verify`;
- call X509 path-validation APIs;
- observe a native ACCEPT/REJECT label for any planned holdout case;
- tune the family, source files or case grid using verification outcomes.

## Planned trust model

The normal-chain intermediate will be evaluated as an explicit experiment
trust anchor using OpenSSL's native `-partial_chain` behavior. This prevents
system trust-store drift while preserving native path-building/validation
semantics.

A later final freeze will choose exact verification time(s), hostname(s),
purpose and trust-source variants solely from the pinned metadata and OpenSSL
documentation, before any native validation outcome is observed.

## Holdout discipline

Any required change to:
- the G4 adapter schema,
- V0/C1/C2/C3 semantics,
- generic WFC compiler core,

after this family is scored yields `HOLDOUT_FAIL_CORE_CHANGE`. The family
then moves to development and another previously unopened family is required.

The fifth-family native outcome remains **UNOPENED** at this preflight stage.
