# R3-M2 F0 preregistration: partial source observability with witnessed decisions

Date: 2026-10-10
Branch: `eeq-r3-m2-partial-knowledge-20261010`
Parent: R3-M1 controlled-native result `e30ad36c0f3dbcfdbdc02ef69a9e363e8b97c97a`.
**STATUS: BEFORE R3-M2 IMPLEMENTATION; RETROSPECTIVE DEVELOPMENT LABELS; NOT NATIVE/P3/HOLDOUT SCORING.**

## Parent and hard freeze

Authoritative original parity+ G4 remains commit `c15b212ad0c2be3856a03d38802aaffa628aefd1`, G5 285 cases; original main `b5434ab1ad317e5121c88b632806880f903774db`. Old B10, G4, G7 X.509/in-toto, fifth-family holdout untouched. Original G6 global C1 scope remains disputed; G8 remains open. R3-M1 first native evidence: [run 38018392189](https://github.com/MKLEE222/EEQ/actions/runs/38018392189), artifact `11657391628`, 12/12 source-only vs native, 12/12 isolated Binding controls, 4/4 state changes, fair B9 tie. R3-M2 REUSES those **already scored** 12 native cells; it must never call Kubernetes for its development diagnostics or call them unseen.

## Scientific question, witness limits and target statuses

For a fixed registered K8s ValidatingAdmissionPolicy with `failurePolicy=Fail`, known CEL `serviceAccountName != 'flux'`, `Deny`, and **at most two registered, individually identifiable Binding support paths**, can a partial-evidence engine produce decision *certificates* for:
- `PROVEN_REJECT`: one fresh, qualified, known Binding whose known policy CEL is violated proves a denial, irrespective of other missing support sources. Under additive Deny semantics this proof remains sound even if the set of OTHER bindings is not closed.
- `PROVEN_ACCEPT`: ONLY if every effective Binding in the *complete, fresh* registered inventory is known to target that validated policy, all instances of its CEL pass or their selectors are proven inapplicable, and the model excludes any unobserved policy/webhook/admission cause. In the restricted single-policy contract, a `default` Pod passes irrespective of missing selector metadata, provided a complete inventory and trusted common policy-binding envelope is independently available.
- `SOURCE_UNAVAILABLE_REFUSE`: some needed original source unavailable and neither side provable.
- `MODEL_UNSUPPORTED_REFUSE`: contract/authority/inventory freshness unproven, malformed or tampered; not a native REJECT.

**WARNING**: This prototype uses an explicitly declared *authored registered inventory envelope* from the previously pinned controlled-native carrier, with individual Binding ID/policyName/validationAction and source-scoped freshness from previously archived native observations. It does NOT authenticate a fresh external/production membership certificate or prove C1 completeness for changing policies/bindings/webhooks. No binary ACCEPT/REJECT is emitted when evidence insufficient. It certifies **bounded scoped VAP policy effect only**, never global Kubernetes API admission.

## Immutable fixture and source/label boundary

All source-only inputs are the unchanged 8 R3-M1 JSON files at `experiments/native_distinction_relaunch/r3_m1/sources/`. Source-only prediction code may call prior `r3_m1_source_only.validate` for grammar, obtain namespace and action paths from source JSON, then construct masks; it MUST NOT load `R3_M1_RAW_NATIVE_*.json`, previous join score or `expected_native` fields from sealed predictions. Independent test/scorer may consult exactly the 12 fixed old native outcomes, never to choose cases or construct candidate outputs.

The fixed R3-M1 **two orders x three phases x two Pod probes = 12** cells remain one development carrier. Every registered mask applies to **every** cell; no row selection, no change to denominator or original G5.

## Prospective F0 mask registry — EXACT 8 x 12 = 96 tested virtual packets

Source masks (each is an EVIDENCE PROJECTION / controlled fault injection, NOT a new Kubernetes state or physical Binding deletion):
1. `FULL_CLOSED`: both Binding selectors visible, common-policy envelope + fresh closed inventory proof assumed; 12/12 decision certificates.
2. `TEAM_ONLY_CLOSED`: TEAM selector visible, MODE selector intentionally unavailable; fresh inventory/envelope still attests both IDs/common policy. Exactly 9 decision certificates, 3 refuses.
3. `MODE_ONLY_CLOSED`: MODE visible, TEAM selector unavailable; exactly 9 decisions, 3 refuses.
4. `NO_SELECTORS_CLOSED`: both selectors unavailable but complete fresh inventory and known same policy available; exactly 6 decisions (the `default` probes), 6 refuses (all `flux`).
5. `OPEN_INVENTORY_KNOWN_BINDINGS`: both registered source Binding records known/fresh, but extra unobserved bindings or policies POSSIBLE, so closed-world inventory cannot be asserted; exactly 4 `PROVEN_REJECT` on current/first-phase `flux` evidence, 8 refuses. NO `PROVEN_ACCEPT`.
6. `POLICY_SOURCE_UNAVAILABLE`: policy validation bytes are unavailable; exactly 0 decisions and 12 `SOURCE_UNAVAILABLE_REFUSE`.
7. `POLICY_SOURCE_TAMPERED`: policy authenticity/digest invalid; exactly 0 decisions and 12 `MODEL_UNSUPPORTED_REFUSE`.
8. `BINDING_FRESHNESS_UNPROVEN`: both Binding identities/selector bodies may have changed since certified snapshot, so neither a source-specific denial nor complete acceptance may be inferred; exactly 0 decisions and 12 `MODEL_UNSUPPORTED_REFUSE`.

**Totals frozen before code:** 96 evidence packets; 40 sound decision candidates (12+9+9+6+4), 56 refusals. Native base has 12 previously scored results; each is reused eight times as retrospective fault-injection truth comparison, thus **96 virtual observations, NOT 96 native cases**. Every certified decision must match archived native AND an independent bounded possible-world enumerator. Measure soundness over **all consistent completions** (not just archived labels); target 0 unsound decisions, 40/96 coverage; always-REFUSE has 0/96 coverage. A selective rule must not be rewarded solely for 0 false accepts.

### Independent finite oracle
Oracle enumerates every boolean applicability of each unavailable selector. If the set is not closed, add a possible extra native vetoing policy which may or may not reject; if policy unavailable/tampered/freshness unknown, enumerate both effects. `PROVEN_REJECT` iff ALL worlds reject; `PROVEN_ACCEPT` iff ALL worlds accept; otherwise REFUSE with the corresponding reason. This bounded enumeration is a PROOF OBLIGATION, not a new semantics theorem.

## Fair strong baseline and kill design

A fully informed B9 with EXACT SAME partially visible source projection, envelope, admissible masks and computation privileges may use the same 3-valued evidence lattice, caching and possible-world oracle; it is expected to tie **40/96 safe decisions** with identical false-positive/false-negative rate. A complete-information B9 on unmasked native inputs can recover 12/12, but comparing it against masked EEQ is unfair. `missing-as-false`, `assume absent Binding` and `default accept when no known veto` are explicitly WEAK UNSOUND diagnostic ablations only; never relabel as B9.

Fixed anti-masking tests must kill: wrong/missing packet, incomplete case/mask denominators, duplicate case, unknown selectors interpreted as nonmatch, unknown-policy default ACCEPT, known denial incorrectly refused, unclosed inventory ACCEPT, stale known Binding reused as source denial, corrupted source silently treated as unavailable, deliberate native-label leakage, missing support path, false audit hash/inventory assertion. A forged `complete:true` supplied by caller MUST NOT elevate the actual soundness guarantee.

## Novelty and scientific blocker

This is **three-valued monotone proof search / possible-world reasoning**, a known technique, and likely reducible to database provenance, partial-information semantics, incremental maintenance, and ordinary hand-coded B9. Even perfect F0 results establish at most `R3_M2_CONTROLLED_DEV_PARTIAL_EVIDENCE_SOUNDNESS_DIAGNOSTIC_B9_TIE`.

Hard remaining issue: proving the *actual fresh completeness/authorization* of support source inventory and excluded mechanisms across all reachable native histories. As long as membership is assumed by the authored fixture, no universal ACCEPT safety or independent cross-family certificate construction claim is authorized. No P3 human cost advantage, no R5 new family, no G6/G8 clean PASS.
