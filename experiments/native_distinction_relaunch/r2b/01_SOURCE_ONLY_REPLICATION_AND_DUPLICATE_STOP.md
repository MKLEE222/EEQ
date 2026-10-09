# R2-B independent source-only replication — stop native duplication

Date: 2026-10-09
Status: **SOURCE_ONLY_PASS / NATIVE_NOT_RUN / DO_NOT_CLAIM_FRESH_R2_B**.

## This branch's own execution

- Source-only preregistration:
  `00_SOURCE_ONLY_CONTROLLED_TUF_FREEZE.md`, committed BEFORE generated sources.
- Signed-source run: Actions `37901727074`, artifact `11602832697`,
  outer ZIP SHA256
  `f2f64d29461b0fdd286c5df8b525cd91356082f690b840a33432e92b30964b30`.
- 10/10 unit tests; seven publicly reproducible **test-key only** signed
  sources, three registered states, three actions and nine source-derived
  action edges. Complete action traces up to horizon 2: 13 per initial
  history. Source-derived quotient classes at horizons 0,1,2: 2,2,2.
- Genuine targets signer authority contrast from source crypto:
  A: targets_A true / targets_B false;
  B: targets_A false / targets_B true.
- Independent NO-NATIVE pin-only run: Actions `37902177542`,
  artifact `11602464585`, ZIP SHA256
  `36768f9105bc979a3275735ceb18ce63eac73615a7bda6745968472ab8110c2d`.
  R2B source-only prediction inner SHA256:
  `1187f6cf5664e947400cd6ff91f050ba62563f84ab7e68baf3cf7145f6dc8cb3`.
  Scorer anti-masking: 10/10 pure synthetic tests.
- This branch's native oracle implementation was PREPARED but never
  executed; there is NO R2-B native score from this source set.

## Discovery and evidence precedence

A separate branch `eeq-r2b-controlled-authority-20261009` had already
performed an equivalent *scientific intervention* under its own frozen
fixtures and its own valid pre-native chronology:
- native Actions `37899400973`, artifact `11601504071`,
  SHA256
  `caf59ac91e8cf7b325b5f3c88b42fbb38f359d155e3df4664a0c189798c01de9`;
- original study 28/28 root-update and 4/4 targets-role qualification,
  controlled signed-authority difference and full registered futures;
- B9/classical quotient expected TIE; no EEQ-independent benefit;
- older source and prescore manifest remain the authoritative first
  native R2-B evidence.

This branch MUST NOT pretend to be the first prospective native R2-B test.
Its independent source-only signed fixture is diagnostic replication
and can be retained for development, but a new native run here would
largely duplicate an already-observed phenomenon, not add an unseen
scientific mechanism.

## Scientifically useful consequence

The cross-family progression already contains:
- native Kubernetes R2-A (Actions 37901407490): controlled current
  equivalence, future separation after a real binding source update;
- native TUF R2-B (Actions 37899400973): controlled noncosmetic,
  contract-relative merging with a strong B9 tie.

Neither a common future-qualified compiler nor R4 independent superiority
is yet demonstrated. We stop duplicate native work and move to a
read-only evidence interface audit in a separate R3 branch,
`eeq-r3-common-certificate-audit-20261009`.

The original G4-v1 and main stay unchanged. The source-only artifact and
negative/positive history remain immutable.
