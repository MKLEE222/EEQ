# EEQ R2-B Controlled-Native Qualified Distinction — Actual Result

Date: 2026-10-09.
Evidence class: CONTROLLED_NATIVE_DEVELOPMENT.
Disposition: **CONTROLLED_NATIVE_B_CONFIRMED_B9_TIE**.
Full R2 = OPEN; R4 independent innovation = NOT SHOWN.

## Immutable chronology

- New experimental branch:
  eeq-r2b-controlled-authority-20261009, parent
  0c4fc8d2fec3c88550abd5b24d65cfb9656c72b3.
- Pre-generation source/contract freeze:
  00_CONTROLLED_SIGNING_SOURCE_FREEZE.md,
  first committed 266e2aa9bb9e16de900ee319117fbf4fe0d5bd38.
- Source-only Actions 37898538285, commit
  31bea2410fed394bd66fa0867d38b45d11fb2969, 8/8 tests pass.
- Signed source/predictions artifact 11601537119, OUTER ZIP SHA256:
  ca60eafb405a3ad5617eb409d1c90195909e31dd30c22bbbf25928ea7b4f169a.
- Source-only predicted trace SHA256:
  0ad5e3b462dc43876b3934c48e5cd59c6d06fb8945f10c230290541d84485f2c.
  Source manifest SHA256:
  fea2ea4b47fec6afc75f24f279cadc44399fc7a5e6a4373963a6f30376aefdd2.
  These were pinned independently before native in Actions 37898667182.
- Scorer anti-masking test first failed due Python import path
  (Actions 37899022644), before any native execution; corrected
  scorer test import and passed all 10/10 cases at Actions 37899219528.
- FULL pre-native manifest 02_FINAL_PRESCORE_MANIFEST.md committed
  b0291691fa052467dc08920841790ac27841649e, BEFORE first R2-B
  native run. It pins artifact outer/inner hashes, all six signed source
  hashes, generator code, independent native code, evaluator code, original
  G4 freeze and tuf-js@3.0.1 package-lock Git blobs.
- Independent native Actions 37899400973 at commit
  9d5fccb5110ac5388f71169d9055e249279b77c7.
  Native evidence artifact 11601504071, outer ZIP SHA256:
  caf59ac91e8cf7b325b5f3c88b42fbb38f359d155e3df4664a0c189798c01de9.

## What was ACTUALLY tested

Two valid controlled Ed25519-signed TUF root version-1 anchors A and B:
same root signing keyid, version and root signature threshold; DIFFERENT
trusted **targets-role** authorized key identity.

Both anchors are self-verified by native tuf-js@3.0.1 constructor.

The contract was preregistered **root update only**. Candidate actions:
submit-candidate-2, submit-candidate-3.
For each A/B source and each prefix length 0,1,2, exhaustive
7 registered action words:
[],[2],[3],[2,2],[2,3],[3,2],[3,3].

For each prefix, an isolated native store was used to evaluate both
potential next root updates. Native root-update challenge observations:
**28/28 matched SOURCE-ONLY frozen predictions**,
including cryptographically qualified versions/actual next trusted
signed-root hashes; 0 mismatches, 0 unresolved prefixes, and exact complete
contract-relative continuation equivalence at all 7 registered prefixes.

Native challenge histogram: 12 ACCEPT, 16 REJECT.

Separately, 2 anchors x 2 independently signed targets metadata envelopes
were checked via **native Metadata.verifyDelegate(targets)**:
4/4 qualification predictions matched, 2 QUALIFIED and 2 UNQUALIFIED.
These witnesses substantiate genuinely DIFFERENT authorized evidence.
This was a targets-role SIGNATURE AUTHORIZATION check, **not a full
TUF targets-update pipeline** with timestamp and snapshot.

The identity difference is therefore materially relevant to a registered
TARGETS authority claim but irrelevant to the narrower ROOT-UPDATE
continuation contract. If the claim family includes targets authorization,
the two states MUST NOT be merged; this result is strictly
CLAIM-RELATIVE.

No native production private keys: all controlled signing seed derivations
are PUBLIC, deterministic and tagged TEST-ONLY. Do not use these keys for
production.

## Fair baseline and independent novelty veto

A strong expert baseline B9 is allowed to keep root version, trusted root
role keys/threshold and candidate signature/qualification information.
It can LEGALLY merge anchors A and B for the root-update-only contract,
just like the source-derived quotient.

A classical Moore quotient given the same lawful transition graph also
makes the same merge. Both were predeclared in the prescore manifest,
not added post hoc.

Therefore, this is a **valid controlled noncosmetic B witness** and an
explicit **STRONG_B9_TIE**, with no EEQ-specific advantage or compression
cost benefit established. Codebook/source retrieval/signing/verification
costs have NOT been compared under R4.

## R2-A obstruction

01_FIXED_PROPOSAL_R2A_NO_GO.md records a simple deterministic structural
lemma: fixed-candidate root-update operations with accept-to-common-source
or reject-self-loop behavior cannot produce "same all current actions,
different future registered action trace" within that same fixed alphabet.
This restriction is NOT a theorem about Kubernetes or TUF generally.
The old production 8-state/7-action carrier also has 8 singleton classes
at r=0..2.

Thus R2-A should move to an actually evolving multi-source admission
policy/binding system, prospectively frozen and natively executed, not a
fictitious TUF action or post-hoc changed contract.

## Gate accounting (strict)

R0_CHARTER: complete.
R1_TUF_RESTRICTED_NATIVE_EXTRACTOR: 56/56 prior native pass, unchanged.
R2_B_CONTROLLED_NATIVE: PASS (this run).
R2_A_NATIVE_FUTURE_SEPARATION: **NOT STARTED**.
R2_FULL_BIDIRECTIONAL: **NOT PASS**.
R3_MULTISOURCE_NATIVE_TRANSFER: OPEN.
R4_STRONG_BASELINE_INDEPENDENT_VALUE: **NOT SHOWN / B9_TIE ON B**.
R5_NEW_UNSEEN_FAMILY: UNOPENED.

No v1 G4/G5/G6/G7/G8 claim changed. Historical G5 stays 285.
Main branch not modified. X.509 and selected in-toto untouched.

### Most important conclusion

The problem's **representation-relative necessity** of evidence distinctions
is now empirically supported in a signed native controlled system:
valid, noncosmetically different authority sources can be collapsed for
one registered future claim family but not for another.

The experiment does **not** yet show EEQ uniquely achieves this beyond
fair expert sufficient-state design. Continue only toward an independent
native construction/certificate or boundary advantage; do not use B alone
as the primary algorithmic novelty claim.
