# P3-A / P3-B F0: controlled non-scoring falsification registry

Date: 2026-10-09
Research branch: `eeq-p3a-p3b-preflight-20261009`
Parent: `99b29dd1572418765f4d2afa506e9f69eb4fe735`
Status: **DESIGN REGISTRATION BEFORE F0 CODE OR EXECUTION. NOT A P3 EXPERIMENT FREEZE.**

## Authority and preservation

- Original v1 G4 is frozen at `c15b212ad0c2be3856a03d38802aaffa628aefd1`; original G5=285, G6 contested full-scope C1, G7/X.509 7/7 and chronology caveat, G8 incomplete; all remain unchanged.
- R4 C0 16/16 verified certificates are **already scored development reuse**, not independent 16 new native executions.
- P3 primary quantitative effect, unit, recruitment, randomization, threshold, sample size, B9 parity, and prospective native tasks are **not frozen** here. NO P3 native calls, no new score, no new G5 or G8 count, no fifth family opened.
- All cases below are entirely **synthetic diagnostics** of a candidate certificate reuse *guard*, not evidence that domain semantic adapters are complete or cheaper than B9.
- A clean checker PASS, an empty successful test suite, or an author-coded synthetic oracle is not a scientific gate PASS.

## Scientific falsification target

Given a certificate tied to a source/claim/actor/action/horizon scope, old source digests, a declared complete set of claim-relevant source and qualification dependencies, and a fresh independently checked dependency snapshot:

1. Source byte equality **alone must never authorize reuse** when a relevant qualification, authority, or binding premise changes.
2. Changes to **independently certified contract-irrelevant** evidence need not invalidate a scoped decision certificate; audit provenance is not erased.
3. Missing required source is `SOURCE_UNAVAILABLE`, not native `REJECT`; missing proof, unsupported dependency enumeration or changed scope must not be recorded as a native decision.
4. The guard yields **eligibility for reuse only, never native ACCEPT/REJECT**, and its result is conditional on a domain-trusted, **fresh, independently re-enumerated complete dependency closure**. A self-asserted boolean in input JSON is not such verification.

The strongest competing implementation (B9) is fully entitled to the same legal inputs, dependency closure witness, hashing, caching, checker and code. A B9 tie is expected and cannot be hidden. Classical incremental view/provenance systems are first-class prior-art comparators.

## F0 interface and finite cases fixed BEFORE writing executable guard

Fixed synthetic initial contract: `TUF_ROOT_UPDATE_ONLY`; claim `root3_accepted`; actor `registered_tuf_client`; action `UPDATE_ROOT`; horizon 1; initial required source `trusted_root` digest `a`*64; initial required qualification `old_root_authority` digest `b`*64 and status QUALIFIED. Scope and dependency closure fingerprints are canonical SHA256 over exact registered fields and sorted required IDs. Fresh snapshot carries observed source and qualification checks, not native labels.

Four permitted outputs:
- `REUSE_CANDIDATE_CONDITIONAL` — no changed relevant prerequisite under trusted closure recheck; **not** native permission
- `REVERIFY_REQUIRED` — material change under checked closure; obtain new semantics/native evidence
- `SOURCE_UNAVAILABLE` — explicitly unavailable claim-required source/qualification evidence
- `MODEL_UNSUPPORTED` — no trustworthy completeness/scope/observation for a reuse judgment

Registered primary synthetic F0 matrix, **fixed N=20**, not selected by output:

| ID | Registered mutation after snapshot | Expected guard outcome |
| --- | --- | --- |
| F01 | No change | REUSE_CANDIDATE_CONDITIONAL |
| F02 | Unrelated `targets` source bytes change; independently verified closure unchanged | REUSE_CANDIDATE_CONDITIONAL |
| F03 | Required `trusted_root` bytes change | REVERIFY_REQUIRED |
| F04 | Required `old_root_authority` digest changes with IDENTICAL root bytes | REVERIFY_REQUIRED |
| F05 | Unrelated targets-role qualification digest changes, verified closure unchanged | REUSE_CANDIDATE_CONDITIONAL |
| F06 | Required `trusted_root` explicitly unavailable | SOURCE_UNAVAILABLE |
| F07 | Required `old_root_authority` evidence explicitly unavailable | SOURCE_UNAVAILABLE |
| F08 | Fresh complete-closure validation fails | MODEL_UNSUPPORTED |
| F09 | Registered contract changes | MODEL_UNSUPPORTED |
| F10 | Registered action changes | MODEL_UNSUPPORTED |
| F11 | Registered horizon changes | MODEL_UNSUPPORTED |
| F12 | Independently enumerated new required source enters closure | REVERIFY_REQUIRED |
| F13 | Independently enumerated new required qualification enters closure | REVERIFY_REQUIRED |
| F14 | Required source row silently absent (NOT declared unavailable) | MODEL_UNSUPPORTED |
| F15 | Required qualification row silently absent (NOT declared unavailable) | MODEL_UNSUPPORTED |
| F16 | Required qualification becomes UNQUALIFIED | REVERIFY_REQUIRED |
| F17 | Required source is explicitly INVALID | REVERIFY_REQUIRED |
| F18 | Unknown snapshot schema | MODEL_UNSUPPORTED |
| F19 | Trusted closure callback raises/aborts | MODEL_UNSUPPORTED |
| F20 | Malformed required dependency digest | MODEL_UNSUPPORTED |

For F12/F13 the new independently validated dependency list is known; reuse must be prohibited even if old hashes still match. For F02/F05 unrelated data are retained in audit but excluded from the registered decision dependency closure. A domain adapter capable of falsely marking a relevant dependency as irrelevant defeats the guarantee; that is a **hard soundness blocker**, not something this synthetic guard proves away.

## Before native or P3 human evaluation

P3-A must attack: Paige-Tarjan partition refinement; provenance semirings; DBToaster/higher-order incremental view maintenance; existing TUF two-root threshold/signature validation; Kubernetes policy/binding/CEL semantics; domain-native hand-coded B9. Do not claim generic novelty from a certificate envelope, a digest, an invalidation rule or a hash map.

P3-B requires independently audited domain adapters that re-enumerate ALL relevant prerequisites and a matched safe native answer-coverage/refusal study; this F0 register tests ONLY structurally conservative bookkeeping. The current checker cannot independently validate TUF cryptography, Kubernetes admission semantics or a proof that an adapter found every relevant source.

P3-C independent maintainers / randomized paired tasks / fully informed B9 / preregistered sample and statistical threshold remain **NOT AUTHORIZED** until a later versioned preregistration. No switch to P1/P2/P4 after viewing outcomes; those metrics require distinct prospective versions.

### Literature / native spec anchors (precheck, not comprehensive novelty search)
- Paige & Tarjan, *Three Partition Refinement Algorithms*, SIAM J. Comput. 1987, https://doi.org/10.1137/0216062
- Green, Karvounarakis & Tannen, *Provenance Semirings*, PODS 2007, https://doi.org/10.1145/1265530.1265535
- Koch et al., *DBToaster: Higher-order Delta Processing for Dynamic, Frequently Fresh Views*, VLDB J. 2014, https://doi.org/10.1007/s00778-013-0348-4
- TUF root update specification, https://github.com/theupdateframework/specification/blob/master/tuf-spec.md
- Kubernetes ValidatingAdmissionPolicy specification, https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/

## Disposition rules for this isolated probe

F0 scientific status remains `SYNTHETIC_GUARD_DIAGNOSTIC_ONLY` even if all N=20 outcomes match. All failed tests and denominators remain visible. Any change to the registered F01–F20 rows after execution requires a new version and must retain prior failures. No change to original G4, old B10 or scored R4.
