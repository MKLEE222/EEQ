# Ordered G7 replacement selection / preflight freeze v1 — in-toto

Date: 2026-10-07

Protocol parent:
`parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md` at
`c15b212ad0c2be3856a03d38802aaffa628aefd1`.

G6 current status:
**PASS after frozen GitHub v2 repair**.

The earlier OpenSSL/X.509 holdout remains valid sealed evidence but is not
counted as the final ordered G7 gate because it was opened before G6 actually
passed. This document selects a previously unopened replacement family after
G6 PASS.

Status: **REPLACEMENT FAMILY SELECTED; NATIVE OUTCOME UNOPENED**.

## Selected unseen family

Native family:
**in-toto supply-chain layout verification**.

Native operation:
`in-toto-verify`.

Pinned native release:
`in-toto v3.1.0`.

Release tag:
`v3.1.0`.

Pinned source commit:
`c82fe5d21aaa61c7f1a213db20a46f10bb3f411a`.

Published wheel:
`in_toto-3.1.0-py3-none-any.whl`.

Published wheel SHA256:
`9a5e73c8e983cdfdfb153760d532893ec0260597c09724ad875ce7950e294a79`.

No `in-toto-verify` invocation may occur until source preflight, case grid,
predictions, adapter mapping and generic-WFC inputs are all frozen.

## Why this family is independent

This native decision system was not used in G0-G6 development and is distinct
from:
- APT release-info/Signed-By continuation;
- Kubernetes admission;
- TUF root update;
- GitHub merge governance;
- the earlier X.509 transfer experiment.

The in-toto decision problem has explicit:
- source/functionary identities;
- owner/functionary cryptographic authentication;
- step-specific authorization and thresholds;
- artifact/material/product claim binding;
- ordered supply-chain step relations;
- inspection/continuation rules governing whether the final product may be
  accepted for downstream use.

It therefore exercises unchanged V0+C1-C3 without requiring a new schema.

## Public source fixtures

Repository:
`in-toto/in-toto`.

Pinned commit:
`c82fe5d21aaa61c7f1a213db20a46f10bb3f411a`.

The official repository's own verification tests use the following demo
fixture family.

| role | path | Git blob |
|---|---|---|
| unsigned layout template | `tests/demo_files/demo.layout.template` | `64ca25099e4b6afcb6710fd9552b7c4e539ce7ba` |
| write-code link | `tests/demo_files/write-code.776a00e2.link` | `1baf159c75e0b4bc408021e34e444c019646e762` |
| package link | `tests/demo_files/package.2f89b927.link` | `e7bde5860ec468c445c9d9bf987663775230e6e8` |
| final package | `tests/demo_files/foo.tar.gz` | `5de7b881306435ec0cef766267d07c4f684ae76c` |
| owner RSA private test key | `tests/pems/rsa_private_unencrypted.pem` | `82406424dc8a606e5a9e4d78f14f913006885ec9` |
| owner RSA public key | `tests/pems/rsa_public.pem` | `02e7bb778798af806c77efe92a3cabe161cd45a6` |
| wrong-owner public key control | `tests/pems/ed25519_public.pem` | `137861a38e86c0c32598ac56d1297e2895e55548` |
| inspection helper | `tests/scripts/tar` | `9cb701375915f0019cdede414f30cf1426aea20d` |

The public test private key is used only to materialize a signed test layout;
it is not a production secret.

## Permitted no-score preflight

Before final case/prediction freeze, a preflight may:
- download the published v3.1.0 wheel and verify the published SHA256;
- fetch only the pinned fixture bytes above and verify Git blob identities;
- install the wheel without invoking verification and record exact transitive
  dependency versions;
- parse layout/link JSON as inert data;
- record step names, authorized key IDs, thresholds, material/product rules,
  inspection command and link signature key IDs;
- create and sign a copy of the public layout template with the pinned public
  test RSA private key;
- create a second signed layout whose `write-code` threshold is 2;
- compute hashes of all generated fixture bytes.

The preflight must not:
- invoke `in-toto-verify`;
- call the verification library entry point;
- observe an ACCEPT/REJECT result for any planned case;
- use a verification exception to tune cases or adapter semantics.

## Planned native cases

The final freeze will instantiate, at minimum:

1. valid signed layout + correct links + final package;
2. correct evidence with wrong owner verification key;
3. tampered write-code link signature;
4. missing package link;
5. modified final `foo.tar.gz` bytes;
6. link with unauthorized/tampered functionary signature identity;
7. owner-signed layout tightening `write-code` threshold from 1 to 2 while
   only one qualifying link exists.

Exact bytes/hashes and predictions are frozen only after the no-score preflight.

## Holdout failure discipline

Any required change to:
- `eeq-adapter-v1` schema;
- V0/C1/C2/C3 semantics;
- generic WFC compiler core,

after native scoring begins is
`HOLDOUT_FAIL_CORE_CHANGE`.

Any native/prediction mismatch is retained as `METHOD_MISMATCH`.

No alternative replacement family may be substituted after observing native
outcomes merely to improve the result.

The in-toto native outcome remains **UNOPENED**.
