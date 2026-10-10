# A1 two hard algorithmic no-go reductions — exact retention complexity and local-update instability

**2026-10-10. MATHEMATICAL ARGUMENT ONLY; no code executed, no performance result, no novel theorem claimed.** Applies to the finite fixed-price query-selection objective in A1 `01_...`.

## No-go 1 — weighted set cover embeds even with two-world post-output fibers

Given any weighted set-cover instance with universe E={e1,...,en}, sets S1,...,Sk and nonnegative weights wi, construct **two pre-worlds** u_j^0 and u_j^1 for each element e_j. Native post-output `O(u_j^0)=O(u_j^1)=j`; outputs for different j are different. Historical claim `C(u_j^b)=b`. Pre-snapshot query qi is boolean: `qi(u_j^0)=0` and `qi(u_j^1)=1` exactly if e_j∈Si, otherwise qi(u_j^1)=0.

The only same-post-output but different-claim collisions are pairs {u_j^0,u_j^1}. A query qi separates pair j iff Si contains e_j. Thus a query set R makes the historical claim recoverable iff {Si:i∈R} covers E. Optimal archive weight equals optimal weighted set-cover cost. If an element is not covered by any S_i, that pair has no legal distinguishing query and the preservation task is impossible for the declared menu.

**Consequence:** General minimum-weight exact preservation is NP-hard, even with zero source-alternative ambiguity, Boolean queries/claims, and at most two relevant worlds per post-output. There can be no unconditional polynomial exact solver promise unless P=NP. The result is an elementary reduction, NOT a new scientific theorem.

## No-go 2 — one semantic source change can create quadratic numbers of explicit conflicts

Let n worlds labeled claim TRUE and n labeled claim FALSE. At epoch0 the lawful post-output includes a distinct identity of each world, so there are no same-output cross-claim collisions. At epoch1 a SINGLE externally qualified regime bit changes the interpretation of outputs from 'distinct per world' to 'the same constant for all worlds' (for example, an abstract global trust/identity projection; this is NOT a TUF or Kubernetes native execution claim). Then n*n conflict pairs appear. A procedure that explicitly materializes all `P` pairs must change Omega(n^2) rows even though the source event count is one.

**Consequence:** A guarantee of update work proportional only to number of changed native events is unsound for explicit conflict-pair materialization unless the grammar excludes global effects or output is symbolic. Source-locality assumptions must themselves be attested and not inferred from a small event count.

## No-go 3 — one new constraint may force global replacement of the optimal archive

Set n>=2. Candidate qA has cost n-1/2 and covers original constraints e1,...,en. Individual qB_i have cost 1 each and cover their respective e_i. Initially unique cheapest solution is {qA} of cost n-1/2, because all {qB_1,...,qB_n} cost n, and any mix including qA costs more. Add ONE additional constraint e0, covered ONLY by qB_1. Now qA alone is invalid; qA+qB_1 costs n+1/2, whereas selecting every B_i costs n and satisfies every old+new constraint. The unique optimal solution switches from one archive query to n unrelated queries upon adding ONE source-induced obligation.

**Consequence:** Even when change in a compact obligation hypergraph is ONE clause, the exact optimal archive set may change globally. Index-based incremental conflict maintenance need not imply an equally local exact optimization update. Measure objective changes, optimizer work and policy churn independently; no blanket 'locality theorem' without extra structure.

## What remains worth searching for

- A **fully specified source-program class** L in which the native semantic witness generator can exploit independence/dependency treewidth, limited writable footprint, bounded alternatives or source-conditioned output support to produce certified counterexamples and optimize snapshots with proved FPT, approximation or output-sensitive guarantees **beyond** generic MaxSAT/CEGAR/IVM using the SAME structure.
- A new **cost/coverage tradeoff** under meaningful native destructive procedures that makes such specialization empirically useful at >=16/32/64 available queries, not just 7.
- A specific native continuation/source-certification dependency whose special structure invalidates common direct approaches but can be handled by a genuinely new decomposition, with a strict no-leak pre-score protocol.

If no such property survives a strongest prior-art attack and truly independent native oracle, **do not rebrand ordinary weighted set cover, modular decomposition, symbolic pair generation or lazy clauses as EEQ novelty.**

All original main/G4/B10/G5/G6/G8/holdout unchanged; 0 new scored cases.