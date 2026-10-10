# M3 V2B Retrospective API Default-Equivalence Normalization Freeze

Date: 2026-10-10. Existing V2 run 38027428940 is irrevocably
completed/FAILURE at its original frozen scorer. The original 8 raw
native observations ARE NOW KNOWN from immutable forensic audit
38027634073 and thus no new evaluation is blinded by source predictions.

V2B's scope: DATA-PRESERVING NORMALIZATION AND REJOIN DIAGNOSTIC ONLY,
on exact V2 source and native archives, NEVER a new Kind or TUF verifier.

## BEFORE V2B code: exact allowed Kubernetes server-added defaults

Original source JSON omitted fields. Native original spec adds ONLY:
For ValidatingAdmissionPolicy spec.matchConstraints:
 - matchPolicy = "Equivalent"
 - namespaceSelector = {}
 - objectSelector = {}
 - resourceRules[i].scope = "*"
For ValidatingAdmissionPolicyBinding spec.matchResources:
 - matchPolicy = "Equivalent"
 - objectSelector = {}.

These values and only these paths are the allowed default-equivalent
native additions. Official Kubernetes admissionregistration/v1 API
documents Equivalent as the default policy matching strategy, empty
label selectors as selecting all, and wildcard scope as the rule default.
See https://kubernetes.io/docs/reference/kubernetes-api/definitions/match-resources-v1-admissionregistration/
and https://kubernetes.io/docs/reference/kubernetes-api/admissionregistration/validating-admission-policy-v1/

The normalizer MUST:
- independently reopen the original native V2 artifact id 11661085822
  ZIP SHA256 10b93b315194c2be6733222a87e28d1f568bb551fb970f8ea7f8833367f3253c;
- reopen original source stage1 artifact id 11660256715 ZIP SHA256
  d251df798e96eec0d1b4a39dd9b410678657fd025398f26c79cd277ccfd49f0e;
- verify original source manifest digest
  d502d56bea25491e83af70c23835488d649cdd481dc15b171211e3385f252b44
  and original prediction digest
  232f652d841b2871c089e0703c6f79785e051094e006ba01d37444d9a7ccc1a2;
- read original native raw and hash it BEFORE making a copy;
- ensure exact all observed native policy/binding spec differences
  belong to the SIX allowed default values, no other field changed;
- normalize ONLY the certified defaulted live spec in a new
  RETROSPECTIVE_COPY.json; never overwrite original native raw artifact;
- preserve raw Pod native decisions, all 8 case IDs, 2 controls,
  3 native actions, 4 snapshots, object UIDs, object/list
  resourceVersions and source hashes EXACTLY;
- call original frozen join-only scorer unchanged
  (blob 8b4a21f8da0cce15791ebf0c0c843f7afa0ac5b5)
  on ONLY the default-normalized *copy* and the old sealed predictions;
- include original vs copied SHA, every normalization path,
  predicate asserted, full source/native score and strong B9 results.

Required synthetic anti-masking tests:
 unknown additional key/value, wrong default value, altered original
 CEL, selector, policyName or source matchRule must FAIL; dropping
 any original native Pod case or inventory phase must FAIL.
 An old ACCEPT that becomes native REJECT due the new third binding
 must remain a REJECT, never re-labelled by normalizer.

An equivalence-normalized original scorer 8/8 under V2B means ONLY
 "retrospectively corroborated controlled native inventory contrast,
  B9 tied" and original V2 remains scored FAILURE, not modified.
No native calls, new holdout, prospective V2 success or R4 P3 novelty.
G4/B10/main and original G5 285 unchanged.
