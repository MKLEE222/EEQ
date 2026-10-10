# A1 formal algorithm pressure — counterexample-guided preservation vs optimized incumbent

STATUS: **RESEARCH CANDIDATE / NOT A NOVEL ALGORITHM RESULT / NOT EXECUTED.** Date: 2026-10-10. This is an exact bounded-task REDUCTION and future algorithm kill protocol design, not a scored experiment.

## I. Exact underlying finite combinatorial problem

The original 2026-09-22 IS reconstruction treats a finite source-state/alternative family. To avoid collapsing alternatives illegitimately, define a finite nonempty set of **qualified source-world pairs** `U={(m,x)}`. Native/destructive action program `m` maps old input x to a legally observed post-action output `O(m,x)` (include source-alternative identifier in O **ONLY IF legitimately observable**), while the historical claim is `C(m,x)`. Each PRE-action snapshot query `q_i(x)` is lawful, fixed/nonadaptive, and has a declared nonnegative cost `w_i`.

For an archive subset R, a single COMMON decoder exists exactly when:
  for all u,v in U,
    O(u)==O(v) and q_i(u)==q_i(v) for all i in R  => C(u)==C(v).

The quantification includes **cross-alternative pairs** m != m'. Only checking each m separately is not enough when decoder does not learn m.

Let `P={ {u,v} : O(u)=O(v) AND C(u)!=C(v) }` and `Sep(u,v)={i : q_i(u)!=q_i(v)}`.

Then the minimum-cost fixed retention problem on explicit finite U is EXACTLY

`min sum_i w_i z_i subject to sum_{i in Sep(u,v)} z_i >= 1 for ALL {u,v} in P; z_i in {0,1}`.

**Proof:** If a collision pair is not separated, it has exactly the same observable (post-output, retained-query) tuple but different historical claims, so no common decoder can be sound on both. Conversely, if every such pair is separated by at least one selected pre-query, grouping states by (post-output, q_R) produces singleton historical-claim classes, defining a deterministic common decoder. Costs are additive, so minimum-cost retention equals minimum weighted hitting set. If some Sep(u,v)=empty, the selected menu cannot ever suffice and refusal is mandatory.

This yields a clean exact **positive AND negative certificate** requirement, and immediately **kills novelty claims** that just rebrand set cover, static feature/key selection or ordinary view determinacy. It does NOT cover adaptive pre-action queries, stochastic costs or arbitrary unbounded native language without further proof.

## II. Strong generic optimization baseline the candidate MUST beat

**EAGER-EXACT:** enumerate all qualified native/source pairs (or an equivalent symbolic relation), group by post-output, construct every differing-claim conflict clause, solve EXACT weighted MaxSAT/MILP/branch-and-bound using known techniques. Direct original 2026-09-22 compiler is a small bounded member of this class and compared only to 2^7 exhaustive SQLite, not published strong optimization solvers.

**GENERIC-LAZY-EXACT / CEGAR baseline** (this is NOT an invented EEQ algorithm):
1. Initialize witness clauses `L:=empty`.
2. Compute an exactly minimum-cost archive `R` that hits all clauses in L, using the same exact solver/cost/time budget as the candidate. Cost serves as a lower bound on the final optimum.
3. Call an independent source-program two-run verifier/separation oracle:
   `FindViolatingPair(R) = find qualified u,v with O(u)=O(v), C(u)!=C(v), all selected q_i(u)=q_i(v)`.
4. If none exists, R is globally sound; since R was min-cost over the weaker set L, its feasible cost also proves global optimum. Certification additionally demands independent native-semantics test for the no-witness/UNSAT result, and a verifier-checkable optimizer lower-bound certificate. Do NOT claim a generic solver's PASS is independent unless all obligations are backed by native semantics or trusted checker.
5. If a pair is found and `Sep(u,v)=empty`, report `INFEASIBLE_UNDER_LEGAL_QUERY_MENU` with source-bound two-world witness.
6. Else append clause `OR_{i in Sep(u,v)} z_i`; repeat. Each discovered clause excludes the current R. Finite convergence holds, but worst-case can be exponential; independent explanation of any improvement is mandatory.

The baseline is precisely *implicit hitting set / counterexample-guided constraint generation* (known algorithms), and may exploit native SMT encodings, source grammar constraints, cached equations, indexed output fibers, provenance, source-level equality hashing and incremental solver state. **If our 'new' method does only these steps, it is NOT new.**

A standalone 'fast' result against naive eager enumeration without comparing such incumbent is an insufficient algorithm paper.

## III. What COULD be a nontrivial computational mechanism — hypothesis, not implementation

Try to derive a **SOURCE-PROGRAM-SPECIALIZED separation procedure** that:
- computes a correct cross-alternative collision certificate directly from native program syntax, without constructing all possible old worlds or pretending native program variants are observed;
- preserves actor legality, typed pre-query semantics and exact original post-output equality;
- exploits provable structural restrictions of the native transformations (e.g. local writes, bounded dependency width, versioned predicate scopes) to bound the *number/size* of instantiated constraints or the oracle search complexity, with a REAL proof;
- supports source-program deltas without rebuilding all closed-world certificates when authority/action semantics are demonstrably unchanged, while emitting refusal on uncertified cases;
- beats optimized same-information generic symbolic CEGAR or known IVM on relevant and *independent native* workloads, not by omitting native witness derivation or codebook/translation costs.

If generic CEGAR/SMT/IVM achieves identical complexity and correctness after identical domain-specific frontend work, report `NO_INDEPENDENT_ALGORITHM_MECHANISM` and stop chasing this kernel.

## IV. Nontrivial hard tests needed BEFORE performance claims (prospective, not executed)

1. **Scale query menu, not only state count**: original old query menu had 7 candidates (only 128 subsets); use independently authored 16/32/64+ available pre-action queries and genuine support alternatives. Evaluate exact optimality only when an independent exact oracle has certified bound; timeouts are censored not counted as correctness wins.
2. **CROSS-SOURCE common decoder**: two each-individually-determinable modes but no common decoder without extra snapshots. Source identity cannot be revealed post-action except when lawful. If per-mode optimization declares cost zero, it's WRONG.
3. **HARD contradictory witness**: an observed same-output/different-claim pair that NO authorized query separates must lead to infeasible/refusal; do not insert an illegal query.
4. **EASY/no retention**: source transformation already preserves claim. Over-retention is a counterexample to optimality.
5. **MANY redundant pairs**: group millions of duplicate output/claim signatures to test legitimate oracle factorization without weighting raw execution count as independent natural cases.
6. **ADVERSARIAL worst case**: source alternatives and query results engineered so generic lazy constraint generation needs many iterations or timed-out solver calls. Preserve all timeouts and failed denominators; no claim of universal speedup.
7. **REAL native source semantics**: start with original pinned SQL subset but progress to a VERSIONED independent SQL grammar including joins/conditional update/schema migration or another independently maintained native executor; trust assumptions explicit. Query validation, native execution/compilation cost fully charged.
8. **Same optimizers and native tools**: implementations of eager exact, generic lazy exact, incumbent view-determinacy/query rewriting and, for changed source families, provenance/DBSP-style IVM all receive identical legal source bytes, raw programs, cost menu, actor/access, CPU/wall/memory allowance, reuse and checker.
9. **NATIVE label-blind pre-registration**: freeze source program grammar, permitted post-action observations, old hidden claim, pre-query menu/costs, source-alternative distribution, expected result classification, tie policy and system versions before any authoritative outcome test.
10. **Unseen generalization**: verify outside hand-authored two-integer single-row SQL; do not recycle the old v1 fifth holdout or relabel old 396 source-runtime cases as fresh.

For any timing: >=5 warmups, >=30 measured operations where resolvable, median/IQR/p95 with peak RSS, witness/constraint counts, solver search states and source preprocessing charged. Zero correctness discrepancy and exact certificate coverage are first-class constraints, not post-hoc filter.

## V. The actual A1 gate

**GO to A2 ALGORITHM ENGINEERING** only if one can state a formally checkable proposition of the form: `For registered native sublanguage L and source-coupling parameter k, our source-to-conflict oracle has bound B(...) whereas best direct generic exact baselines require/empirically perform substantially more work under matched conditions`, and that difference survives peer-reviewed prior-art scrutiny and a small independent feasibility audit. The bound can be parameterized or output-sensitive, but cannot be a renamed basic hashing/indexing/BDD operation.

**NO-GO** if all proposed gains are only from (a) hitting set instead of exhaustive 128 subsets, (b) lazy CEGAR instead of eager all-pairs enumeration, (c) maintaining an ordinary dependency graph, (d) letting EEQ see hidden source alternatives denied to full B9, (e) count inflation, (f) moving handwritten semantic interpretation outside measured work.

**Current finding: NOT YET GO.** This document is a transparent algorithmic map and strongest-baseline kill framework, not a novel algorithm's construction/execution.

Existing protocol: main `b5434ab1ad317e5121c88b632806880f903774db`; G4 blob `3eeaeeb828d2fcf7ec4487da06489fee3146c920`; B10 blob `9a6bff7a2b8db73b86b6952c706852c92b1a4b1d`; v1 G5=285; original G6 global C1 disputed; G8 incomplete; v1 fifth family holdout unopened. Zero new scored semantic cases in A1.