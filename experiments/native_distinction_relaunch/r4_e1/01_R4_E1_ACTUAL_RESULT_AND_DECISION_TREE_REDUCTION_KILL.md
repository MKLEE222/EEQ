# R4-E1 F0 ACTUAL RESULT and formal reduction kill audit

Date: 2026-10-10. Branch eeq-r4-e1-epistemic-query-frontier-20261010.
Status **R4_E1_SYNTHETIC_LAWFUL_QUERY_FRONTIER_FEASIBLE_B9_TIE**.
This audit is POST-F0-SOURCE-ONLY scoring, not an amendment of the preregistered 17 scenarios or metric.

## Evidence actually executed

1. Frozen BEFORE implementation: `00_R4_E1_PRESOURCE_SYNTHETIC_QUERY_FRONTIER_FREEZE.md`, commit `7f6b51e6cca6d3b035739a0ab11b33c66aad538e`, Git blob `e02dd912699215c9849bdb28196c8a4b7b60b40f`.
2. First E1 complete suite CI [38032262890](https://github.com/MKLEE222/EEQ/actions/runs/38032262890), code commit `b3abcbac9a5727dfae79dbfc94453b42b4d6cf9c`, **SUCCESS 28/28** independent source-free synthetic tests.
3. Artifact [11663005869](https://github.com/MKLEE222/EEQ/actions/runs/38032262890/artifacts/11663005869), ZIP SHA256 `10017ac4f360d0e41ede392ec07061827a3a444a05442983bd4e8efc72724757`. Contains deterministic E1 summary and ALL 17 full plans, finite possible worlds, actor-access two-world impossibility certificates, full B9-equivalent optimum, and SHA256 manifest.
4. Registered 17 scenarios: **7 CERTAIN (4 true+3 false)**, **5 GUARANTEED_RESOLVABLE** with exact optimal legal adaptive read plan, **5 IMPOSSIBLE_UNDER_ACTOR_ACCESS** with concrete worlds of opposite scoped effect and identical all-lawful-read answers. All 17 checked against a separately implemented truth-table reference, all reads/branch leaves audited across every finite world, and every plan cost compared to a complete exhaustive B9-eligible decision-tree optimizer. **17/17 fair fully informed B9 optimum parity**. K09 cheap THIRD then expensive ADDITIONAL cost: worst 4, mathematical uniform-possible-world sum 10 over four worlds, versus a deliberately weak static query-all sum 16; this is NOT a win over optimized B9.
5. Entire experiment is SOURCE-FREE SYNTHETIC development. TUF old/new threshold qualifications and K8s Binding/Policy scope completeness are **hand-authored assumptions** in two restricted Boolean grammars; cryptography, native K8s actor RBAC, source-class completeness and native output are NOT independently verified here. Zero new native calls, zero P3 maintainers, zero original G5/G8 cases, no R5 transfer.

## Exact reduction, i.e. why this STILL DOES NOT create unique method novelty

For a finite registered contract f over Boolean source-qualification atoms S, qualified observations fix a partial assignment o, actor-authorized source reads form A subset S and per-source costs c. For any world completion w consistent with o, the scoped effect is f(w).

1. A safe immediately CERTAIN effect exists exactly when f is constant on the set W(o).
2. If uncertain, a guaranteed lawful adaptive evidence-acquisition plan is EXACTLY a deterministic decision tree over currently unknown variables in A with constant-effect leaves for all completions. Minimum worst-cost and total cost are classical **weighted decision-tree optimization** on f restricted by o and A.
3. No such plan exists iff two worlds w0,w1 in W(o) agree on the projection to ALL A but f(w0) differs from f(w1). Necessity: every allowed query returns the same values in those worlds, hence identical leaf but required opposite results. Sufficiency: query every remaining A atom and resolve if no equivalence class contains opposing effects. These are elementary observation-equivalence/monitorability facts, NOT new EEQ theorems.
4. The equal-information FULL B9 is legally entitled to precisely the same oracle, query tree, inference, source access, and witness checker. It ties by construction as independently tested. A weaker B9 that always queries all available atoms is only an ablation, not the scientific comparator.

**Formal disposition for the finite F0 kernel**: `REDUCIBLE_TO_WEIGHTED_DECISION_TREE_AND_POSSIBLE_WORLDS` and `FULL_B9_TIE`; E1 provides a nontrivial **auditable problem diagnostic**, NOT non-reducible H3 originality or unconditional global ACCEPT soundness.

Close-prior-art audit supported by:
- Benasher & Newman (1995), Decision Trees with Boolean Threshold Queries, JCSS, https://doi.org/10.1006/jcss.1995.1085
- Buhrman & de Wolf (2002), Complexity measures and decision tree complexity survey, https://doi.org/10.1016/S0304-3975(01)00144-X
- Ferrando & Cardoso (2025), Towards partial monitoring: Never too early to give in, https://doi.org/10.1016/j.scico.2024.103220
- Ciccone, Dagnino & Ferrando (2026), Ain't No Stopping Us Monitoring Now, ACM TOSEM, https://doi.org/10.1145/3744241
- Cimatti et al. (2026), Exploiting Assumptions for Effective Monitoring of Real-Time Properties under Partial Observability, https://doi.org/10.1007/s10270-026-01394-6
- Bogaerts et al. (2026), Why(-Not)-Provenance for Datalog with Negation, KR 2026, https://doi.org/10.24963/kr.2026/19
- Li et al. (2026), In-memory Incremental Maintenance of Provenance Sketches, https://arxiv.org/abs/2505.20683
- Native TUF dual root signature thresholds: https://theupdateframework.github.io/specification/v1.0.36/
- Kubernetes per-kind LIST/WATCH and 410: https://kubernetes.io/docs/reference/using-api/api-concepts/

## Surviving distinct research object and new test that could actually kill or support it

E1 identifies an *important gap that cannot be filled by another synthetic decision-tree study*: the source-qualification bits are assumed rather than **constructed from independently authorized native source procedures**. In real TUF, the authority witness is a cryptographically verified predecessor/root role and both old/new signer thresholds. In Kubernetes, a source set requires actual actor permissions, collection LIST/WATCH custody and explicit bounded scope; two distinct resource classes are not an atomic global admission truth.

Candidate H3 opportunity: a **contract-to-lawful-evidence-procedure compiler** that synthesizes, from actual native source and authority rules rather than handwritten Boolean statuses, an executable scoped observation/refusal interface AND an independently checked provenance/qualification proof across TUF and K8s. This is only a candidate, and still threatened by monitor synthesis, XACML, provenance and strong B9. The F1 hard falsifier is: if it needs a manually asserted complete-dependency callback, hard-coded expected native decisions or a new domain-specific handwritten policy adapter of comparable complexity to fair B9, mark `COMPILER_NOT_INDEPENDENTLY_ESTABLISHED`. A common JSON certificate format, a copy of client-go Reflector or a generic AND/OR library does NOT pass.

H3 requires at least one **independently validated** positive property against full B9 and nearest prior art: a demonstrably more transferable/source-derived authority compiler with independently quantified human adaptation cost at matched native safety/coverage (P3 independent maintainers and prescoring REQUIRED), OR a new non-reducible theoretical result formally distinguished from decision-tree and monitorability literature. In absence of either, retain `B9_TIE / R4_INDEPENDENT_VALUE_NOT_ESTABLISHED`.

No unqualified external current ACCEPT, no X.509/in-toto v2 unseen reuse, no main/G4/B10 modification, no original G5 counter change. Original main `b5434ab1ad317e5121c88b632806880f903774db`, original G4 authority `c15b212ad0c2be3856a03d38802aaffa628aefd1`, G5=285, historical G6 global C1 disputed and G8 incomplete.
