# EEQ R4-E1 — lawful evidence acquisition frontier: PRE-CODE falsification freeze

Date: 2026-10-10. Research branch: eeq-r4-e1-epistemic-query-frontier-20261010.
Parent: C1-W1 V2b audit commit 2548287116e2ee72d309c4191d4309eab6c55a21.
**Status: PRE-IMPLEMENTATION / SOURCE-FREE SYNTHETIC F0. This is NOT a prospective native score or P3 human experiment.**

## Why this experiment differs from another B9 100%-accuracy grid

The mother problem asks which lawful original-source observations can still support a claim after actions, and which future decisions remain justified. A hand-engineered B9 already attains exact effects on earlier complete-information TUF/Kubernetes development carriers; more correct/incorrect rows do not establish unique value.

Candidate new *research object*, not assumed novelty: an **actor-authorized evidence acquisition frontier**. An agent given incomplete, qualified observations must either (i) issue an effect-certain proof, (ii) compute the least required lawful observation questions that can always resolve the effect, or (iii) return a checkable pair of legal source worlds indistinguishable under all accessible questions but yielding opposite contract effects. Its output is a source-read/proof obligation, NEVER global permission or a new native observation. This tests whether EEQ can reformulate the science around the cost and possibility of becoming justified, instead of pointwise decision accuracy.

The operational success criterion of F0 is only a **nontrivial executable, independently oracle-checked lower-bound witness and cross-domain query-plan interface**, not strict accuracy improvement over fully informed B9. An unrestricted full B9 with equal actor/source/algorithm access can copy the plan. If it does, score B9_TIE / NO_INDEPENDENT_VALUE. Do not hide this mathematical ceiling or call implementation a new theorem.

## Source/authority model and hard science limits

Two **manually specified** finite contract grammars:
- `TUF_ROOT2_TO_ROOT3`: binary proposition TRUE means root update authorized under a trusted fully qualified and complete *old/new role signer-set* interface. Effect = OLD_ROOT_THRESHOLD_SATISFIED AND NEW_ROOT_THRESHOLD_SATISFIED. Native TUF requires BOTH old-root and new-root threshold signatures, sequential root version, valid canonical signature bytes, expiry, etc. These are ASSUMED VERIFIED by hypothetical native adapter here, NOT reverified by the generic kernel. FALSE is scoped root update rejection under that complete interface; UNKNOWN is not FALSE.
- `K8S_REGISTERED_VAP_DENY`: TRUE means there exists a qualified additive Deny witness from two registered bindings for a flux Pod (`TEAM_MATCH OR MODE_MATCH`) or, for a default Pod, from the third matching default-deny Binding or a possibly unobserved additional qualified Deny source (`THIRD_DEFAULT_BINDING_MATCH OR ADDITIONAL_SCOPED_DENY`). FALSE means **NO DENY IN THE DECLARED COMPLETE VAP CONTRACT**, NOT global Kubernetes Pod ACCEPT; a source-authorization/closed-inventory claim is a hypothetical external prerequisite, never proved by fixture syntax.

All registered atom outcomes are Boolean *post-authority-qualified native predicates*; E1 does not implement TUF signatures or K8s CEL and may NOT infer these from signature bytes, old list hashes, a fake `complete=true`, or native output labels. A hidden new policy can be represented by ADDITIONAL_SCOPED_DENY UNKNOWN; no permission to retrieve means a negative decision may be impossible. A known qualified additive DENY remains positive even while further source classes may be undiscovered. The difference between qualified observed FALSE and source UNAVAILABLE is mandatory.

"Accessible" is a hypothetical actor permission for a native query to reveal an **authoritative Boolean qualification**; no synthetic assertion establishes actual RBAC, TUF trust continuity or cross-collection atomicity. All direct tests are development synthetic; old R4-D0 TUF and R3-M3 Kubernetes native data are prior *motivation*, never read by this source-only optimizer. If an external adapter lies about completeness or loses a watch, no sound global claim follows.

## Fixed query-planning formalism and proof obligations (before code)

Let finite possible worlds W be all {0,1} assignments for UNKNOWN atoms consistent with currently qualified observations. Each allowed observation action reads **one registered unknown atom** at nonnegative integer fixed cost. NO unauthorized atom may be requested. For each world w, contract effect D(w) evaluated from the complete registered Boolean formula.

- `CERTAIN_TRUE / CERTAIN_FALSE` iff every w in W has the same effect. Evidence certificate stores supporting scope and complete registered universe assumption.
- If effects vary, algorithm may produce an adaptive plan. A plan is `GUARANTEED_RESOLVABLE` iff for EVERY possible response branch the downstream leaf effect is constant. Reject algorithms that silently report a partial plan as guaranteed.
- Minimize **worst-case total authorized evidence-acquisition cost**, not runtime, then break ties by total cost summed across all equally weighted finite worlds (explicit *mathematical diagnostic*, not an empirical probability distribution), then lexicographic atom ID. All atoms have independent stable read costs: `old,new,TEAM,MODE,THIRD=1`; `ADDITIONAL=3`. Exhaustive query-all is a WEAK diagnostic, not strong B9.
- A `NOT_RESOLVABLE` outcome MUST include two complete lawful Boolean worlds with (a) opposite scoped effects, (b) identical current known observations, and (c) identical answers for ALL lawful readable UNKNOWN atoms. These are independent-checkable **epistemic impossibility witnesses**.
- An externally lost/unqualified source is `NOT_OBSERVED_OR_NO_AUTHORITY` and cannot be converted to Boolean false. No global Kubernetes admission guarantee.
- Comparator: strong B9 is allowed identical source bits, permissions, costs, worlds, fully optimized search, generic DSL/certificate and witness oracle. The primary fair result expected is EXACT B9 parity on all 17 registered cells, not an EEQ win.

## Immutable F0 matrix — exactly 17 scenarios, including negative controls

Each atom is T (verified true), F (verified false), or ? (unobserved). Set of lawful read actions is frozen. Costs as above.

| id | contract | current | lawful unanswered reads | expected now | future decision resolvability |
| --- | --- | --- | --- | --- | --- |
| T01 | TUF AND(old,new) | old=?,new=T | none | UNCERTAIN | NO: must return 2-world access indistinguishability |
| T02 | TUF | old=F,new=? | none | CERTAIN_FALSE | ALREADY CERTAIN (old threshold conclusively failed, assumes complete old root roster) |
| T03 | TUF | old=T,new=? | new | UNCERTAIN | YES: 1 read, worst cost 1 |
| T04 | TUF | old=?,new=? | old,new | UNCERTAIN | YES: minimax cost 2; uniform-world total read cost 6/4 |
| T05 | TUF | old=?,new=? | none | UNCERTAIN | NO: 2-world witness |
| T06 | TUF | old=T,new=T | none | CERTAIN_TRUE | ALREADY CERTAIN |
| T07 | TUF | old=F,new=T (same signed candidate body, rotated authority) | none | CERTAIN_FALSE | ALREADY CERTAIN; old source bytes not sole qualification |
| T08 | TUF | old=T,new=T (targets-only irrelevant change) | none | CERTAIN_TRUE | ALREADY CERTAIN; contract-relative |
| K01 | K8s flux OR(TEAM,MODE) | TEAM=?,MODE=? | TEAM,MODE | UNCERTAIN | YES: minimax 2; uniform-world total 6/4 |
| K02 | K8s flux | TEAM=T,MODE=? | none | CERTAIN_TRUE = scoped DENY | ALREADY CERTAIN |
| K03 | K8s flux | TEAM=F,MODE=? | none | UNCERTAIN | NO: 2-world witness |
| K04 | K8s default OR(THIRD,ADDITIONAL) | THIRD=?,ADDITIONAL=F | none | UNCERTAIN | NO: 2-world witness |
| K05 | K8s default | THIRD=F,ADDITIONAL=? | none | UNCERTAIN | NO: 2-world witness (source inventory not proven closed) |
| K06 | K8s default | THIRD=F,ADDITIONAL=F | none | CERTAIN_FALSE = no scoped VAP Deny | ALREADY CERTAIN, but ONLY under authored complete scope premise |
| K07 | K8s default | THIRD=T,ADDITIONAL=? | none | CERTAIN_TRUE = scoped DENY | ALREADY CERTAIN |
| K08 | K8s default | THIRD=?,ADDITIONAL=F | THIRD | UNCERTAIN | YES: 1 read, worst cost 1 |
| K09 | K8s default | THIRD=?,ADDITIONAL=? | THIRD,ADDITIONAL | UNCERTAIN | YES: minimax cost 4, sum of costs across 4 worlds = 10 (2.5 per equally weighted completion), prioritizing cheap THIRD |

Expected fixed categories: 7 already certain; 5 uncertain but guaranteed resolvable; 5 uncertain and proven unresolvable with a concrete indistinguishable pair. No replacement, no pruning, no rerun to chase a desired histogram; if implementation disagrees, record failure.

## F0 tests and serious novelty veto

Independently constructed reference oracle must enumerate truth assignments and verify all 17 scenario effect sets; independently inspect each impossible-world pair; verify the complete adaptive plan on ALL legal worlds, not only one selected native label. Kill tests: fake closure, permission escalation, truncated query plan, missing/duplicate atom, UNKNOWN treated as F, query known atom, dishonest expensive source made free, post-action same bytes authority change, irrelevant-target invalidation, scope changed, two worlds with different accessible answers falsely called indistinguishable, and nonminimal worst-case queries.

Known immediate reduction threats: active diagnosis / decision-tree complexity; database certain answers over incomplete worlds; work on why/why-not provenance including Datalog negation (Bogaerts et al. KR 2026, https://proceedings.kr.org/2026/19/); incremental provenance sketches (Li et al. EDBT 2026, https://arxiv.org/abs/2505.20683); provenance semiring/monus, XACML 3.0, TUF spec, Kubernetes LIST/WATCH+Reflector, standard fully informed B9. This F0 is not original just because source queries are called a frontier.

Scientific status if all source-only tests pass: `R4_E1_SYNTHETIC_LAWFUL_QUERY_FRONTIER_FEASIBLE_B9_TIE`. H3/P3 remain OPEN, no independent cost claim, no new native observations, no original G5 increment, fifth family unopened. Original main b5434ab1ad317e5121c88b632806880f903774db; G4 at c15b212ad0c2be3856a03d38802aaffa628aefd1, blob 3eeaeeb828d2fcf7ec4487da06489fee3146c920; B10 blob 9a6bff7a2b8db73b86b6952c706852c92b1a4b1d; v1 G5=285, G6 global C1 disputed and G8 incomplete.
