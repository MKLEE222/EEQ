# R3-M1 prospective controlled Kubernetes two-binding proof-obligation FREEZE

Date: 2026-10-10
Branch: `eeq-r3-multibinding-controlled-20261010`
Parent: `2dbaeb8473e6a520d3817cdbe58c39591536f432`
**State: PRESOURCE / PRENATIVE DESIGN FREEZE. NO SOURCE OR NATIVE LABELS SCORED AT THIS COMMIT.**
Separately versioned R3 controlled development carrier under R0 research charter, **NOT original G4 amendment**.

## Scientific question and non-novelty
Can a label-blind source-to-qualified-continuation model preserve TWO genuinely simultaneously applicable Kubernetes VAP Binding source paths when a sequence of TWO genuine namespace-label updates removes those paths one by one, and output a bounded provenance-aware sufficient state? Even if all native predictions match, Kubernetes binding OR-of-denials and a fully informed B9 should tie. Passing this is scoped mechanism feasibility, NOT method novelty / general R3 closure / R5 holdout.

## Fixed source and native environment
Use eight public non-secret fixture JSON documents created and committed separately **after this design freeze and before any native score**:
`policy.json`, `binding-team.json`, `binding-mode.json`,
`namespace.json`, `pod-flux.json`, `pod-default.json`,
`action-team.json`, `action-mode.json`.
Each raw byte, SHA256, Git blob SHA, predictor blob, native runner blob and scorer blob must be individually pinned in a *subsequent FINAL PRESCORE MANIFEST*, after source-only predictions and tests but BEFORE first native execution.
Kubernetes v1.35.0 on Kind v0.31.0, pinned node image
`kindest/node:v1.35.0@sha256:452d707d4862f52530247495d180205e029056831160e22870e37e3f6c1ac31f`,
`kubectl` 1.35.0 with upstream SHA256, Kind Linux binary SHA256
`eb244cbafcc157dff60cf68693c14c9a75c4e6e6fedaf9cd71c58117cb93e3fa`.
Use two fresh isolated clusters, never a remembered result or existing resource.
Registered actor: dry-run Pod CREATE for serviceAccount flux/default in namespace `eeq-r3`. Exactly one pinned ValidatingAdmissionPolicy with `failurePolicy=Fail`, `Deny` bindings, one CEL predicate `object.spec.serviceAccountName != 'flux'`. No params or other policies or arbitrary CEL are within model scope.
Two differently named native Bindings BOTH pointing to that policy:
- TEAM selector: `r3.team=tenant`;
- MODE selector: `r3.mode=strict`.
Initial real Namespace labels: `r3.team=tenant, r3.mode=strict`.
A proposed source model may not collapse two binding source IDs into one invented source.

## Two preregistered independent native action orders and complete denominator
TM: native UPDATE_NAMESPACE_LABEL `r3.team=external` then `r3.mode=relaxed`.
MT: native UPDATE_NAMESPACE_LABEL `r3.mode=relaxed` then `r3.team=external`.
Each action must be independently reported with unchanged Namespace UID, strictly changed resourceVersion and exact registered label change; no unregistered repair/retry on unexpected result. The native labels/attribution are collected from server-side dry-run Pod CREATE and independently saved before the join-only scorer opens predictions.
Predetermined fixed wait: 10 seconds after both binding setup before scored phase0; 6 seconds after each label update before scored phase1/phase2; no result-conditional waits. Timeout or asynchronous instability is retained as `INFRASTRUCTURE_FAILURE` or `NATIVE_ORACLE_AMBIGUOUS`.

PRE-NATIVE expected source-only 12-cell PRIMARY table:
| Order | Phase | qualified binding sources | flux | default |
|---|---|---|---|---|
| TM | initial | TEAM, MODE | REJECT | ACCEPT |
| TM | after first team change | MODE | REJECT | ACCEPT |
| TM | after second mode change | none | ACCEPT | ACCEPT |
| MT | initial | TEAM, MODE | REJECT | ACCEPT |
| MT | after first mode change | TEAM | REJECT | ACCEPT |
| MT | after second team change | none | ACCEPT | ACCEPT |

Primary denominator **2 orders x 3 phases x 2 registered Pod challenges = 12**. No after-native exclusion, no post-hoc choice of the better order.
Native control denominator, EACH cluster:
- 2 no-binding controls: flux ACCEPT, default ACCEPT.
- 2 isolated TEAM Binding-only controls: flux REJECT, default ACCEPT.
- 2 isolated MODE Binding-only controls: flux REJECT, default ACCEPT.
Thus TOTAL native controls **2 clusters x 6 = 12**; if controls cannot establish independent support, record `R3_M1_INDEPENDENT_BINDING_SUPPORT_NOT_ESTABLISHED` even if primary table matches.
Native verified namespace updates: **2 orders x 2 updates = 4**.
An unrelated native admission failure is `NATIVE_ORACLE_AMBIGUOUS` (not model REJECT), a missing required source is `SOURCE_UNAVAILABLE` (not native REJECT).
Any unsupported feature, unknown additional policy/binding, source mismatch or nonmatching policy observed live must be retained as UNSUPPORTED/MISMATCH, never silently skipped.

## Controls, fair rivals and method-level kill rules
- B0 original complete lawful native inputs/history; B9 full legal source information, separate binding identities, namespace updates and reasonable native parsing; exact straightforward OR-of-denial rule; classical product/quotient alternatives can use same state. B9 should predict all 12; equality is a non-novelty veto, not baseline defeat.
- Selector-blind, one-binding-only and hash-only are intentionally INVALID strong baselines; use them only as mechanistic diagnostic omissions (e.g. losing one support path predicts premature ACCEPT), separately identified.
- Predicted source qualification sets must be saved before any native operation. A native runner may read ONLY `SOURCE_MANIFEST.json` and the eight source files (it must never load `SOURCE_PREDICTIONS.json`); the join-only scorer runs AFTER raw native JSON and hashes are written. Native runner must not import source prediction code.
- Label-blind extractor must not select tasks/cases using previous R2A outcomes; these R3 inputs are newly authored CONTROLLED_NATIVE development fixtures and NOT a fresh external family.
- Hard fail status if action updates fail, native setup doesn't match source, source hash changes, any main cell missing, or any native outcome ambiguous. Record errors and full denominators; do not substitute synthetic results.

## Source-unavailability REFUSE pressure (NOT native REJECT)
A separate source-only preflight with deliberately unavailable TEAM Binding source must return `SOURCE_UNAVAILABLE`/UNSUPPORTED on decisions for which required complete binding inventory cannot be established. Native cannot be scored on an unavailable source and must not be awarded a safety point for refusing everything. The 12 primary native rows use ALL eight valid sources.

## Gate labels regardless of numeric success
Even 12/12 primary matches, 12/12 controls and 4/4 updates mean only `R3_M1_CONTROLLED_NATIVE_TWO_SUPPORT_PATHS_FEASIBLE_B9_TIE`.
They do NOT imply R3 multi-support generality, true cross-family shared extractor, H3 independent value, P3 independent maintainer advantage, original G6/G7/G8 PASS or R5 unseen transfer.
Old G4 `c15b...`, original main, G5=285, G6 disputed global C1, earlier holdouts and old B10 remain untouched.
