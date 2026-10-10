# R3-M2 F0 actual partial-evidence result: conditional safety, B9 tie, C1 unresolved

Date: 2026-10-10
Disposition: **R3_M2_RETROSPECTIVE_NATIVE_COVERAGE_PROOF_DIAGNOSTIC_B9_TIE**.
Research branch: `eeq-r3-m2-partial-knowledge-20261010`.
Scientific evidence class: `RETROSPECTIVE_REUSE_OF_ALREADY_SCORED_R3_M1_NATIVE`.
**Do not describe these as 96 native cases, unseen validation or new algorithm superiority.**

## Execution chain

1. M2 F0 pre-implementation frozen 8 masks x 12 old native cells: commit `1059b7eaa8d2b95cd3050e4e7ad625b764702ca7`. Original G4, G5=285, old B10 and holdouts unchanged.
2. First M2 source-only CI `38025708847` FAILED: a missing-required-source list was mistakenly placed inside a positive proof `witness`. It is now a distinct `missing_dependencies` diagnostic with empty positive witness. FAILURE KEPT.
3. Source-only CI [38025746868](https://github.com/MKLEE222/EEQ/actions/runs/38025746868) SUCCESS, **22/22** tests. 96 source-only masks, all fixed denominators and independent bounded possible-world proof oracle. Artifact [11660039350](https://github.com/MKLEE222/EEQ/actions/runs/38025746868/artifacts/11660039350), ZIP SHA256 `44250176d9af43b7763d2e6c9a6e7cef600e61c0f1dde5d8bb66cba93501480b`; `F0_SUMMARY.json` SHA256 `cbbd4a985f4ff1bff7bca52ddf908f9fc581129e7c57f55488db250dcc73125d`; masked 96 predictions JSON SHA256 `96f0eebce842c6220477a931035bfc81ea0a34bbb214f4e9d7cfe8e853af91b4`. Source-only candidate used NO native decision labels.
4. Retrospective scorer code synthetic anti-masking SUCCESS CI `38025861913`, **36/36 tests** (22 source / 14 scorer). NO actual native artifact loaded at that stage.
5. Final retrospective-join rule + exact source, model, code, scorer and archived native SHA freeze: `01_R3_M2_F0_FINAL_RETROSPECTIVE_JOIN_FREEZE.md`, commit `c4f42ea703b71dca510585077f411e64a4ed3ddb`. PRE-join freeze, but R3-M1 native truth was already known from a separate prior study and therefore is **not an independent/honest holdout**.
6. Retrospective join run [38025921406](https://github.com/MKLEE222/EEQ/actions/runs/38025921406), commit `02d2d88b1b296d5bb12721d8f5a425ff3f48cbb5` SUCCESS. Pipeline downloaded/verified sealed F0 source-only artifact FIRST, ran all 36 synthetic tests, only THEN fetched the immutable earlier native R3-M1 artifact `11657391628` and compared. No Kubernetes calls.
7. Final M2 join archive [11659719962](https://github.com/MKLEE222/EEQ/actions/runs/38025921406/artifacts/11659719962), ZIP SHA256 `cd236ab123f79787d9084df7478f25ba372e02c9ca7cf90c8dc3ad763ae6328e`. Independently downloaded & rehashed `R3_M2_RETROSPECTIVE_NATIVE_JOIN.json`, SHA256 `9ef428ee907fe434aba675fe863b204fcf7821cc8def933b81486d03c6564351`.

## Exact fixed denominator / disposition

| Evidence mask | Eligible proven decisions | Refuse | Mechanism |
| --- | ---: | ---: | --- |
| FULL_CLOSED | 12 | 0 | two registered selectors known under closed authored envelope |
| TEAM_ONLY_CLOSED | 9 | 3 | TEAM qualified denial or default passes the single known CEL |
| MODE_ONLY_CLOSED | 9 | 3 | MODE qualified denial or default passes |
| NO_SELECTORS_CLOSED | 6 | 6 | default accepted under *assumed complete same-policy inventory* |
| OPEN_INVENTORY_KNOWN_BINDINGS | 4 | 8 | positive Deny witness survives unknown *additional* policies; no ACCEPT allowed |
| POLICY_SOURCE_UNAVAILABLE | 0 | 12 | SOURCE_UNAVAILABLE_REFUSE |
| POLICY_SOURCE_TAMPERED | 0 | 12 | MODEL_UNSUPPORTED_REFUSE |
| BINDING_FRESHNESS_UNPROVEN | 0 | 12 | MODEL_UNSUPPORTED_REFUSE |
| **Total (virtual)** | **40** | **56** | **96 old-native-case/mask comparisons, only 12 distinct archived native cases** |

Overall: 26 `PROVEN_ACCEPT`, 14 `PROVEN_REJECT`, 24 `SOURCE_UNAVAILABLE_REFUSE`, 32 `MODEL_UNSUPPORTED_REFUSE`. Bounded conditional safety oracle: **0/40 unsound certified effects** across the registered completion model. Against reused original native observations: **40/40** verified certified decision matches, 0 false accepts, 0 false rejects; 56 refusals are **not** relabeled as correct native denials. Selective safe-coverage 40/96 = 41.67%, versus always-REFUSE 0/96.

STRONG B9 with IDENTICAL partially visible sources and admissible common-policy/inventory assumptions: **96/96 same proof/refusal decisions**. It may use the same ordinary 3-valued inference and cached dependencies. No baseline superiority. The deliberately weak missing-as-false ablation emits unsound certificates on 20/96 packets under the possible-world oracle; these are logical unsoundness, NOT 20 observed native errors nor a win over legitimate B9.

## Real scientific gain

The narrow positive mechanism is selective evidence sufficiency:
- One **fresh, independently qualified Deny source** is a sufficient negative witness in additive Deny semantics even when another source or an extra source is unknown.
- Positive ACCEPT needs all potentially applicable Deny support *accounted for* (or a valid uniform proof of their predicates passing) and a trusted complete contract scope. Under the registered SAME-POLICY envelope, missing selector bytes do not prevent accepting the `default` Pod, because this exact CEL succeeds regardless of selector.
- Missing sources are different from native REJECT. Absent qualification never silently becomes false or decision-safe.
- The proof basis is **ordinary partial-information possible-world logic**, not a novel theorem, EEQ general semantics, or an independent method advantage.

## Two hard blockers remain central

1. **Authenticated, fresh C1 inventory & source-qualification closure**. The authored two-Binding envelope is a research-contract assumption. A *third previously unobserved binding/policy* could deny a `default` Pod despite both known bindings being harmless; old certificates must NOT claim global ACCEPT if a complete live list cannot be proven. The fixture validates only the original specified VAP and registered two bindings; it does not establish a full authoritative inventory of all Kubernetes admission mechanisms. This prevents global native decision correctness or universal certificate reuse claims.
2. **Method originality under strong prior art**. OASIS XACML 3.0 defines `Indeterminate{D,P,DP}` for missing information, Libkin (2016) formalizes certain answers over possible worlds, Kubernetes documents multiple binding conjunction, and provenance/incremental view maintenance are directly relevant. B9 matches all 96 conditional inference results. No new EEQ-specific algorithm benefit is established.

Additional gate discipline: G4 `c15b212...` unchanged; G5 285; original G6 global C1 disputed; X.509 earlier 7/7 valid with chronology caveat; G8 NOT complete; R5 new unseen not opened; P3 independent maintainer study still DESIGN ONLY.

## Next authorized attack, NOT yet executed/scored

Design a separately preregistered controlled-native adversarial C1 test where a new, previously unobserved **third VAP/policy/binding** is added after a cached two-binding inventory snapshot. Test an otherwise accepted default Pod before/after adding the third rejecting policy. Determine what actual Kubernetes API/list version/inventory evidence is required to revoke invalid old ACCEPT certificates; a known and still qualified independent Deny may remain provable without a complete inventory. Include positive and negative controls and a fully informed B9. This would be a new controlled developer case, NOT a holdout and NOT proof of novelty. No R3-M2 scores may be revised from that result.

**Current allowed claim:** scoped, conditionally sound partial-evidence discrimination on reused controlled-native development labels with complete B9 parity; external C1/generalization/novelty NOT ESTABLISHED.
