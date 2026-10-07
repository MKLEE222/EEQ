# G7 X.509 final holdout freeze manifest v1

Date: 2026-10-07

Status: **FINAL PRE-NATIVE FREEZE**.

No `openssl verify` or `X509_verify_cert` outcome for the seven frozen
holdout cases has been observed before this manifest.

Protocol parent:
- G4 freeze: `c15b212ad0c2be3856a03d38802aaffa628aefd1`;
- adapter schema blob:
  `5b25e074f26f1c0b02ec4aa65c32ff9bccf51631`.

Generic compiler:
- freeze commit:
  `062be7f533977d45e879a8026a3034913d1a6a57`;
- `compile_wfc_v1.py` blob:
  `9a6bff7a2b8db73b86b6952c706852c92b1a4b1d`.

No core/schema change is permitted for this holdout.

## No-score preflight

Actions run:
`37578749376`.

Artifact:
- id `11463732099`;
- SHA256
  `501db4374062cf5b11f1f1ae321e853327a9326fc481cfa80506ed16bb75bb91`.

Native environment frozen from preflight:
- runner: `ubuntu-24.04`;
- OpenSSL:
  `OpenSSL 3.0.13 30 Jan 2024`;
- library:
  `OpenSSL 3.0.13 30 Jan 2024`.

The preflight contained no native verification command. It inspected only
source hashes and certificate metadata.

## Frozen public source

Repository:
`chromium/badssl.com`.

Commit:
`bfc80f7c2bf0873e2fdc9ba79f38a5afd93570fb`.

Primary target:
- `certs/sets/prod/pregen/chain/subdomain-superfish.pem`;
- Git blob `41539e568d11b339e1a1fd2fa1a5a7c7a16a2c18`;
- SHA256 `9269c7d678af5a6eaace9a749c738c3b3880faaa880c7653779b0ca516adf1b4`.

Registered trust anchor:
- `certs/src/crt/ca-superfish.crt`;
- Git blob `7e0f08e2f5fa59f0b7aed14cde51398edd420ed8`;
- SHA256 `247e12a507df1b1205d34a34b1d1568fdf982b5a106e4b6546c974615b8c6989`.

Wrong-trust control source:
- `certs/sets/prod/pregen/chain/wildcard-self-signed.pem`;
- Git blob `60cc7ab76918a1c0fefdeb3192c2c1100c423d54`;
- SHA256 `990c242d02a15d5a384d2625b4c1942e861ba5f18eaebd58116b85fbb5b49096`.

Preflight metadata establishes:
- target SAN: `superfish.badssl.com`;
- target basicConstraints: `CA:FALSE`;
- target validity: 2018-05-16 through 2020-05-15 UTC;
- target SSL-server purpose: Yes;
- target Time-Stamp-signing purpose: No;
- registered root is self-issued/self-signed by metadata;
- registered root basicConstraints: `CA:TRUE`;
- registered root SSL-server-CA purpose: Yes;
- registered root validity spans the valid target test time.

## Frozen semantic cases

Case-grid blob:
`9c03e76839445d0bffba7fa01fc1be4e57807f93`.

Seven cases:

1. valid contract;
2. wrong hostname;
3. expired verification time;
4. not-yet-valid verification time;
5. missing trust source with all default trust disabled;
6. wrong explicit trust source;
7. incompatible `timestampsign` purpose.

Common valid reference time:
`2019-06-01T00:00:00Z` / Unix `1559347200`.

Registered action:
`VERIFY_X509_TLS_SERVER`.

Native vocabulary:
`ACCEPT/REJECT`.

`auth_level=0` is frozen for every case to isolate the registered
path/trust/claim/time/purpose semantics from algorithm-strength policy.

## Frozen predictions

Prediction blob:
`01924a6aa8364289e4b7bfbb271656f1e5b33345`.

Predicted actions:
- h1 valid contract: ACCEPT;
- h2 wrong hostname: REJECT;
- h3 expired time: REJECT;
- h4 not-yet-valid: REJECT;
- h5 missing trust: REJECT;
- h6 wrong trust: REJECT;
- h7 wrong purpose: REJECT.

Predictions were derived from pinned source metadata and OpenSSL verification
semantics before native scoring.

## Frozen adapter

Adapter-semantics document blob:
`96f360737d4406182428fd847e3662f0a72b2749`.

Adapter implementation:
- `experiments/x509_holdout/emit_x509_adapter_v1.py`;
- blob `83406ada9b4551691e67473db15106dc42a62b07`.

Source metadata blob:
`9b462beb7b3438ab28f39a0c4f1b22df820ae201`.

The emitter reads only source metadata and the case grid. It does not read the
prediction file or native outcomes.

## Native scoring order

The G7 scoring workflow must enforce:

1. exact source/hash and OpenSSL-version checks;
2. static no-label adapter audit;
3. emit all seven adapters;
4. compile and save all seven generic B10 representations **before**
   `openssl verify`;
5. execute exactly the seven frozen native commands;
6. join native labels only after step 5;
7. compile again and prove each B10 representation equals the pre-native one;
8. compare native labels with the frozen prediction file;
9. retain every mismatch/error.

## Success/failure disposition

`G7_HOLDOUT_SUCCESS` requires:
- zero adapter-schema/core changes;
- seven admitted/scored native cases;
- seven frozen predictions match native actions;
- pre-native/post-native B10 identity;
- generic B10 has no mixed native-label class.

Any prediction mismatch is retained as `METHOD_MISMATCH`; G7 does not receive
a clean success.

Any required adapter-schema or generic-core change is
`HOLDOUT_FAIL_CORE_CHANGE`.

Version/source mismatch is retained under the existing native failure taxonomy
and does not silently substitute another environment.

Only after this manifest may native X.509 holdout scoring begin.
