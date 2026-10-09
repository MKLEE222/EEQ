# R2-A Controlled Native Kubernetes Binding-Update Future Distinction — Actual Result

Date: 2026-10-09.
Evidence: CONTROLLED_NATIVE_DEVELOPMENT.
Scientific disposition: **CONTROLLED_NATIVE_A_CONFIRMED_B9_TIE_EXPECTED**.
R2 full generality gate: NOT PASS. R4 independent value: NOT ESTABLISHED.

## Immutable prospective source and test chronology

- Original relaunch R0/G4 protocol unchanged, G5 original 285 cases,
  X.509 and selected in-toto untouched.
- 00_K8S_BINDING_TRANSITION_FREEZE.md first committed
  7411a39943fbed5cb7998df2ad11ec3dcefe0306
  BEFORE exact source and prediction generation.
- Source-only Actions 37900042227: 9/9 tamper/semantic tests pass.
  Source-only artifact 11602065738, outer ZIP SHA256:
  6651d5a42615f1f6656f7dc8892369070dfad0a7be568c2ab4c3f1c759c82dc4
  Immutable R2A_PRE_NATIVE_PREDICTIONS.json inner SHA256:
  a8a504506236853949dc82da4acf35cc90e95349dae58d669028ebc8546d8dc5
- Independent pre-native hash/scorer tests Actions 37900351621:
  9/9 scorer anti-masking tests pass.
- 01_FINAL_PRESCORE_MANIFEST.md first committed
  4c52badcc139231247642a55f49c9b000b72d0f6
  BEFORE any native scoring, locking 8 JSON source blobs, compiler,
  native driver, exact 8 case predictions, node versions, VAP CEL,
  binding patch, attribution, and fair strong B9 allowance.

## Negative attempts retained BEFORE successful native execution

- Native v1 Actions 37900621767 FAILED.
  Archive 11602247238 outer SHA256
  5fee6caafb7f7f27eab8c1d06d45775cbfb79579f9a993388d1176d698575063.
  Kind cluster and actual binding patch succeeded in WORLD_GATE
  (resourceVersion 488 -> 499), but all dry-run Pod names used
  the RFC1123-invalid world_gate token with an underscore. They
  failed input schema before checking registered VAP.
  Native episode became POLICY_MUTATION_ACTIVATION_NOT_VERIFIED.
  The runner inherited shell -e and never started WORLD_STANDBY.
  Failure is **NATIVE_FIXTURE_SCHEMA_INVALID**, not action mismatch.
- Versioned repair: original driver retained unchanged; v2 native
  driver ONLY turns world token underscore into DNS-safe hyphen,
  proven with a separate all-field-invariance test.
  Bash wrapper disables inherited -e during native error capture.
  Details committed beforehand in
  02_NATIVE_V1_FAILURE_AND_SCHEMA_REPAIR_FREEZE.md,
  03_NATIVE_V2_RETRY_CORRECTIONS_FREEZE.md,
  04_V2_FINAL_NATIVE_PRESCORE_MANIFEST.md.
- Native v2 workflow Actions 37901283134 FAILED **before any native
  execution** due the NEW static test's Python sibling module path.
  The original source/decision code did not change.
  Recorded in 05_V2_PRENATIVE_TEST_IMPORT_FAILURE.md.
  v2b wrapper added a PYTHONPATH to this static test only, leaving
  science/predictions/native driver/scorer source Git blobs locked.

## Successful controlled native v2b execution

Actions 37901407490, commit
010d7ffcf7c09c65ac9404876b7101a2d9233bc0,
artifact 11601914837, outer ZIP SHA256:
a0ba962b74c4ed87618248f6555cca9dcca86232fda2606f748ad57bf07f1996.

- Two separate newly created Kubernetes v1.35.0 kind clusters, one
  for WORLD_GATE, one for WORLD_STANDBY; both independently completed.
- Same predeclared policy:
  eeq-r2a-flux-constraint, CEL disallow flux SA, fixed target denial message.
- Same predeclared binding, initial namespaceSelector
  eeq.r2a/armed=never; patch selector to gate in EACH distinct cluster.
- Native source after patch:
  WORLD_GATE resourceVersion 446 -> 457; namespace label gate retained.
  WORLD_STANDBY resourceVersion 452 -> 459; namespace label standby retained.
- Each isolated world used a separate non-scoring gate-labelled activation
  probe. Both registered-policy activation probes passed (2 attempts
  recorded per world).
- EXACT frozen 8 native admission decisions:

| World | Phase | flux Pod CREATE | default Pod CREATE |
|---|---|---|---|
| WORLD_GATE | CURRENT | ACCEPT | ACCEPT |
| WORLD_STANDBY | CURRENT | ACCEPT | ACCEPT |
| WORLD_GATE | AFTER_BINDING_MUTATION | REJECT (registered VAP) | ACCEPT |
| WORLD_STANDBY | AFTER_BINDING_MUTATION | ACCEPT | ACCEPT |

Score: 8/8 native decisions matched source-only predictions;
0 mismatches/unavailable; 2/2 native episodes completed;
2/2 real selector mutations independently verified;
current action vectors identical and futures divergent after SAME
native binding patch; source qualification difference directly observed.

The scoring join was executed ONLY after raw native outputs had been
stored; it does NOT re-run or retrain source-only predictions.

## Scientific conclusion and limitations

This is a valid CONTROLLED_NATIVE_A pair:
two lawful observable contexts, with the same immediate registered
Pod CREATE decision vector, must be distinguished because an
actual later source/qualification binding mutation exposes different
future admissibility. A concrete separation witness is:
  patch binding selector never -> gate; then Pod CREATE flux.
Pre-action both ACCEPT; post-action WORLD_GATE REJECT from exact policy
and WORLD_STANDBY ACCEPT.

A fully informed expert B9 is expressly permitted to retain namespace
labels, binding/policy semantics and future patch. Thus the B9 ability
to predict this same distinction was FROZEN as an EXPECTED TIE.
A matched independent B9 runtime/cost study has NOT yet been executed.
Do NOT label this a measured strict win over B9 or a newly invented
Kubernetes authorization technique.

This experiment is CONTROLLED_NATIVE only; VAP/namespace/Pod action
subset only; one fixed binding selector transition; not complete
Kubernetes admission coverage, not an unseen family, not a general
native state graph extractor. Source-only predictor was a
domain-specific mechanistic implementation rather than a validated
single reusable cross-family EEQ compiler.

The separately confirmed R2-B native TUF noncosmetic legal merge
is in branch eeq-r2b-controlled-authority-20261009,
Actions 37899400973: 28/28 root-update challenges and 4/4
targets-role authorization challenges.
These TWO valid but DIFFERENT family-specific experimental witnesses
DO NOT satisfy R2 generality requirement that each required
development family demonstrate BOTH A and B plus refusal controls.

## Gate disposition at end of this round

- R0: frozen.
- R1 TUF restricted native transition: 56/56, retained from 2026-10-08.
- R2-B TUF controlled signed qualification merger: YES, B9 expected tie.
- R2-A Kubernetes controlled mutation-induced distinction:
  **YES, 8/8 + 2 native mutation sources**, B9 expected tie.
- R2 FULL GENERALITY: NO, cross-family completeness and missing-source
  refusals NOT verified in each required family.
- R3 multi-support native generality: OPEN.
- R4 independent value over B9/classical quotient: OPEN.
- R5 prospective independent transfer: UNOPENED.
- Original G4/G5/G6/G7/G8 v1 scientific gates unchanged.

NEXT PRIORITY: test one common lawful-source/contract/certificate
interface over both native carriers WITHOUT inserting the correct
hand-written domain answers into the generic representation. A fully
informed expert B9 and standard exact quotient must receive identical
information, and independent source/certificate/full-cost advantages
must be preselected and directly measured. Do not claim novelty by
calling the two hand-written native predictors one novel generic method.
