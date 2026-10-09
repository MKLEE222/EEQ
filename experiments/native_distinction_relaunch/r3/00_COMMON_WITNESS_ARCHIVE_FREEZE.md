# R3 common witness interface — archival audit freeze

Date: 2026-10-09
Status: **BEFORE INTEGRATION AUDIT EXECUTION**. READ-ONLY DEVELOPMENT EVIDENCE.
Parent: `353c6e46d887e09e293a1a5fbb20c9d3f4970d92`.
Original G4-v1 and original compiler are never changed.

## Exact immutable inputs

1. Kubernetes R2-A, two native kind v1.35 worlds:
   - Actions `37901407490`, commit `010d7ffcf7c09c65ac9404876b7101a2d9233bc0`
   - artifact `11601914837`
   - outer ZIP SHA256
     `a0ba962b74c4ed87618248f6555cca9dcca86232fda2606f748ad57bf07f1996`
   - inner expected native joined result:
     `R2A_NATIVE_JOIN_RESULT.json`
   - source-only preregistered predictions archive `11602065738`,
     outer SHA256
     `6651d5a42615f1f6656f7dc8892369070dfad0a7be568c2ab4c3f1c759c82dc4`
     and inner prediction SHA256
     `a8a504506236853949dc82da4acf35cc90e95349dae58d669028ebc8546d8dc5`.
   - v1 native fixture schema failure and v2 pre-native import failure
     remain recorded; v2b is the successful corrected native run.
2. TUF R2-B, test-only controlled root+targets authorization:
   - Actions `37899400973`, commit
     `9d5fccb5110ac5388f71169d9055e249279b77c7`
   - artifact `11601504071`
   - outer ZIP SHA256
     `caf59ac91e8cf7b325b5f3c88b42fbb38f359d155e3df4664a0c189798c01de9`
   - inner expected native joined result:
     `R2B_NATIVE_JOIN_RESULT.json`
   - source-only signed fixture archive `11601537119`,
     outer SHA256
     `ca60eafb405a3ad5617eb409d1c90195909e31dd30c22bbbf25928ea7b4f169a`
     and inner prediction SHA256
     `0ad5e3b462dc43876b3934c48e5cd59c6d06fb8945f10c230290541d84485f2c`.

No new native cluster, signer, verifier, scoring or prospective prediction
may run as part of this audit. Do not change the returned observations.

## Common minimum witness envelope

Both cases are projected, **retrospectively**, into the following common
audit fields:

`evidence_class`, `family`, `registered_contract`,
`registered_action_family`, `horizon`, `source_artifact_sha256`,
`native_artifact_sha256`, `native_denominator`,
`native_matches`, `native_mismatches`, `mechanism_source_transition`,
`distinction_kind`, `witness`, `refusal_coverage_status`,
`matched_strong_b9_status`, `algorithm_novelty_status`.

This is an audit **envelope**; a common filename/JSON schema is not a
new domain-independent method. The verifier has NO TUF signing engine
and NO Kubernetes CEL engine. In particular it cannot independently
certify the correctness of source-to-rule interpretation merely by
checking a pre-existing score JSON.

### A witness — Kubernetes (known native controlled result)

Require every one of eight frozen admission rows (two worlds, two phases,
two SAs). Both currently equal (ACCEPT/ACCEPT); after the SAME actual
native binding mutation, the gate world becomes (REJECT/ACCEPT), standby
remains (ACCEPT/ACCEPT). Exact registered native attribution, two
isolate-cluster successes, resourceVersion/selector transitions required
by original join evaluator, and 8/8 prior scored matches.

Witness: mutate binding selector from `never` to `gate`, then CREATE
Pod with serviceAccountName=`flux` (gate REJECT, standby ACCEPT).

### B witness — TUF (known controlled result)

Require 14 exact (anchor,prefix) pairs and 28 native root-update
challenges under the *two-action* full registered alphabet through depth
2; 4/4 `targets` role signature qualification checks with reversed
authorized signer capabilities. Full future root-update observations
must match between two valid signed trust anchors. Same contracted
root-only decision future; different `targets` evidence authorization.

Each result must retain explicit `strong_b9_tie_predeclared` and
`classical_quotient_tie_predeclared` flags; this is NOT a strict
algorithm superiority experiment.

## Adversarial audit conditions

- Any missing, duplicated, incorrect or unregistered native case -> FAIL.
- Any source/native archive digest mismatch -> abort; no re-run native.
- Any mismatched native action, missing actual binding patch evidence,
  missing native targets qualification check, or nonzero mismatch -> FAIL.
- Strong B9 **expected** to be able to reproduce both outcomes, but there
  is no independently run matched B9 time/cost study. Output
  `B9_TIE_EXPECTED_NOT_MATCHED_COST_BENCHMARK`, not `EEQ_BETTER`.
- A and B belong to TWO different families: DO NOT mark original R2
  BOTH-A-AND-B-PER-FAMILY gate PASS. Retain missing refusal / unknown
  coverage and multi-support family proof.
- Retrospective harmonization cannot count as independent prospective
  transfer, leakage-free general compiler validation or native source
  completeness.
- No claim that a JSON envelope certifies cryptographic root authority
  or cluster admission mechanism independently.
- Run a synthetic anti-masking test in which a scored row or witness is
  removed, and ensure the audit rejects it.

## Required scientific disposition

If both archived traces pass: `R2_NATIVE_A_AND_B_CROSS_FAMILY_CONFIRMED`
with flags `R2_FULL_GENERALITY_OPEN`, `R3_COMMON_COMPILER_UNPROVEN`,
`R4_STRONG_B9_ADVANTAGE_UNPROVEN`, `R5_UNOPENED`.

This step identifies common information requirements and narrows the next
research question. It is **not** the next general algorithm by itself.
