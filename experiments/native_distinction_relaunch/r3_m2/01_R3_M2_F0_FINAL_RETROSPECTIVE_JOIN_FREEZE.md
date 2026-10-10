# R3-M2 F0 FINAL RETROSPECTIVE-JOIN FREEZE — 2026-10-10

Status: **FROZEN BEFORE R3-M2 ARCHIVED-NATIVE JOIN**, but the underlying R3-M1 native outcomes were already PUBLIC/KNOWN before this F0 design. This is a RETROSPECTIVE DEVELOPMENT REUSE study; no new native labels or prospective unseen holdout will be claimed.

## Source, protocol and code authority
- Original v1 G4 authority `c15b212ad0c2be3856a03d38802aaffa628aefd1`, blob `3eeaeeb828d2fcf7ec4487da06489fee3146c920`. Original generic B10 blob `9a6bff7a2b8db73b86b6952c706852c92b1a4b1d`; G5=285; original main `b5434ab1ad317e5121c88b632806880f903774db`. All unchanged.
- Registered F0 eight-mask/96-cell freeze commit `1059b7eaa8d2b95cd3050e4e7ad625b764702ca7`, blob `1815d67c9f42153cb7ab10dcf3c1948170dcccb7`.
- Exactly the original eight R3-M1 source JSONs and two distinct native-cluster histories (TM/MT); no reclassification of old samples; no new original G5 case.
- R3-M2 source-only candidate `r3_m2_partial_source.py` Git blob `9a299ba11bd370712a1254563c78efb8d7808c7b`.
- Independent bounded completion oracle `r3_m2_possible_world_oracle.py` Git blob `f58d83f2c70bff395d77a2a2cb39d51706b1eb10`.
- Source-only 22 fixed tests `test_r3_m2_f0.py` blob `8b034cbef41e07c80144696f8e22a56bd50930c8`.
- Deterministic source-only emitter `r3_m2_f0_emit.py` blob `3d455309bfbbd1adb48ac4e615631cadcd2c6e70`.
- Retrospective JOIN ONLY scorer `r3_m2_join_only_scorer.py` blob `11b89defe8aac3978bd5e988f920c16a3ac69c77`.
- Scorer 14 synthetic anti-masking tests `test_r3_m2_join_only_scorer.py` blob `0de2bb8e242c7ba1a2bb4abc9a47d5b72fafadf7`.

## F0 sealed outputs completed BEFORE retrospective join
First successful source-only F0 CI: [38025746868](https://github.com/MKLEE222/EEQ/actions/runs/38025746868), SOURCE-ONLY artifact **11660039350**, ZIP SHA256:
`44250176d9af43b7763d2e6c9a6e7cef600e61c0f1dde5d8bb66cba93501480b`.
Two independently verified artifact-internal JSON SHA256:
- `F0_SUMMARY.json`: `cbbd4a985f4ff1bff7bca52ddf908f9fc581129e7c57f55488db250dcc73125d`;
- `F0_MASKED_96_SOURCE_ONLY.json`: `96f0eebce842c6220477a931035bfc81ea0a34bbb214f4e9d7cfe8e853af91b4`.
This artifact is authoritative source-only scoring input. Subsequent CI reruns MUST reproduce those deterministic digests but cannot replace its original source-only evidence with a post-native optimized output.

First F0 CI `38025708847` FAILED because SOURCE_UNAVAILABLE diagnostics were incorrectly stored in a positive witness field; repaired in `8acc40196e894de9f5bd1ec002d9605894fda71d`; 22/22 tests then passed, including exact source-only 96 packet counts, independent completion proof, equal-information B9, and anti-masking. Failure preserved, no old original cases changed.

Join-scoring code tested prospectively AGAINST **synthetic native data only** (14 tests; 22 source tests), successful run [38025861913](https://github.com/MKLEE222/EEQ/actions/runs/38025861913). No R3-M1 native archive loaded in this pre-join check.

## Archived actual native evidence, NEVER opened by F0 candidate
- R3-M1 native run [38018392189](https://github.com/MKLEE222/EEQ/actions/runs/38018392189)
- Artifact ID **11657391628**, ZIP SHA256 `b5a26de574de9978c53cdea6dd0e65887b264a46eb2c3ad8583c0df079cb4b1d`.
- `R3_M1_RAW_NATIVE_TM.json` SHA256 `0ec43c391e194c16bad41e4383349f90ecc3f7b40e501badc737bf513104dc20`.
- `R3_M1_RAW_NATIVE_MT.json` SHA256 `d1bf43bd91d4b4d1f9c5d2b4772028263d74fb2a7b3f6e182a1c084e84aced6b`.
- `R3_M1_NATIVE_JOIN_SCORE.json` SHA256 `6dbf1a82bf12cda30e6d3a59caff86a2db6f68168e65e6b9a95a45858821a816`.
- Original native independent-context denominator: 2 Kind clusters, 12 primary Pod observations, 12 unbound/isolated-Binding controls, 4 real namespace label updates. All inputs old CONTROLLED_NATIVE from authored dev fixture. Native dry-run outcomes were known before R3-M2 preregistration.

## Fixed retrospective evaluation, no success-rule shifting
- All 8 mask types x all 12 original native cells = 96 VIRTUAL PROJECTIONS, NOT independent 96 native executions.
- Source-only F0 fixed histogram: 26 PROVEN_ACCEPT, 14 PROVEN_REJECT, 24 SOURCE_UNAVAILABLE_REFUSE, 32 MODEL_UNSUPPORTED_REFUSE. Coverage **40/96**.
- Compare every one of the 40 certified ACCEPT/REJECT to the appropriate archived native outcome; preserve all 56 refusals as refusals, NEVER count as correct native REJECT. Expected archived-cell agreement, as a retrospective check only: 40/40; any mismatch retained and run fails. 12 original native source cases never re-counted.
- Independent bounded possible-world obligations (96/96), equal-information fair strong B9 (96/96 same disposition) must also stay pinned. Weak missing-as-false invalid ablation produces 20 *logically unsound* packets; NOT a strong baseline defeat.
- An all-REFUSE method obtains 0 safe decision coverage; paired native coverage is mandatory. No claim that 40/96 is generalizable. Hard C1 external, live completeness and scope authority remain UNPROVEN.

## Blocking originality and authority issues (pre-join veto)
- Kubernetes VAP officially evaluates EVERY matching policy, binding and parameter, and a Deny validation failure denies the admission request; no new semantics invented: https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/
- OASIS XACML 3.0 formally distinguishes Indeterminate{D}/{P}/{DP}, attribute missingness and policy combining; partial-information policy decisions are existing art: https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-cos01-en.html
- Libkin, *Certain answers as objects and knowledge*, Artificial Intelligence (2016), formalizes all-completion/possible-world certainty under open/closed assumptions: https://doi.org/10.1016/j.artint.2015.11.004
- Paige–Tarjan refinement, provenance semirings, self-adjusting computation, DBToaster/incremental views, standard native B9 remain serious reduction threats.
- The F0 `PROVEN_ACCEPT` is CONDITIONAL on a frozen authored membership envelope. `caller_claimed_complete=true` is NOT a reliable external certification; real C1 must be established separately via source authorization and freshness. Open-world cases allow safe denials but NEVER global ACCEPT in this model. No theorem of generality or method novelty follows.

The only possible PASS label after this retrospective comparison is **R3_M2_RETROSPECTIVE_NATIVE_COVERAGE_PROOF_DIAGNOSTIC_B9_TIE**. No new R3 generality, original G6/G8, R5 transfer or P3 independently measured improvement can be awarded. Negative outcomes stay as such.
