# M3 V2 Raw Native Science Join Failure — PRE-DIAGNOSTIC ADJUDICATION RULES

Date 2026-10-10. This memo is written AFTER v2 original native run
38027428940 FAILED at the frozen join-only scorer. The native run DID
produce an independent, completely registered raw native artifact:
8 Pod observations, 2 no-binding controls, 3 real policy/binding native
membership actions, 4 complete raw policy/binding LISTs, and no runner
setup error. Native had no access to source predictions.

The frozen prescore join failed with:
  ValueError('NATIVE_VAP_POLICY_SPEC_NOT_MATCHING_FROZEN_SOURCE').
That is a MATERIAL protocol gate failure until independently resolved.
The failed v2 verdict is NEVER changed. Any later repair is explicitly
retrospective on the SAME already-observed native labels and is NOT
fresh prescore evidence or new unseen-family validation.

## Exact diagnostic procedure, NO NEW KIND OR KUBECTL CALLS

Read archived raw V2 native JSON from original run artifact. Verify outer
artifact ZIP SHA256 with GitHub artifact digest, frozen source archive ZIP
and both internal manifest/source-prediction hashes. Read ONLY the exact
two original source policy JSON files and the native policy LIST specs
for T0...T3, then independently calculate:
 - all source/live values for registered material fields: policy
   .failurePolicy, .validations, .matchConstraints.resourceRules and
   native API-provided matchPolicy, namespaceSelector, objectSelector,
   params, re/invocation, operations;
 - equality of CEL strings and exact role/resource rules;
 - whether extra fields were API-defaulted, known harmless to the
   registered Pod CREATE contract, or actually change applicability;
 - whether source/digest bindings and origin actor/claim scope match;
 - an explicit complete list of all differences BEFORE authoring
   any revised adjudication function.
Never copy native outcome labels into the prospective source predictor.

## Prespecified disposition

If server-defaulted metadata exists (e.g. default resource rule scope,
matchPolicy), and materiality can be checked independently against
Kubernetes VAP semantics, produce a new *retrospective* V2-A diagnostic
with a narrow separately frozen default-equivalence rule.
Even a successful retrospective 8/8 would mean:
R3_M3_NATIVE_WITNESS_RETROSPECTIVE_JOIN_ONLY_B9_TIE,
not a clean frozen v2 science gate PASS.

If native has ANY unexpected material source difference or no
independently justified default equivalence, retain:
R3_M3_V2_NATIVE_SOURCE_SPEC_DIVERGENCE.
Do NOT ignore it or turn source mismatch into ACCEPT / REJECT credit.

At no point claim old policy cache's no-change is a proof of global
admission C1. Both API LISTs separately observe only their resource
classes at a point in time; they do not prove a continuous, externally
authorized all-admission-mechanisms inventory.

FULLY INFORMED B9 gets identical live API sources and is allowed to
implement exactly any new equivalence rule. There is NO independent
EEQ superiority from this diagnostic.

Original v1 freeze/G5 285/G4/B10/historical holdouts remain unchanged.
