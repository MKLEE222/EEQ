# EEQ: decision-sufficient information states under endogenous evidence change

Public repair and reproduction workspace for **Endogenous Evidence Qualification:
Decision-Sufficient Information States for Acting Systems**.

## 2026-09-30 bottom-up repair status

The cold-start audit found that the frozen 4,500-contract runner reused one exact
`MethodView` under several algorithm labels. The manuscript no longer treats
those labels as independent implementations. That frozen study now has one job:
measure decision loss under restricted information projections.

The constructive claim is rebuilt as separate obligations with separate checks:

1. **Finite WFC realization.** A post-audit benchmark supplies 4,500 explicit
   finite transition tasks with no values, optimal actions, policies, or solver
   labels. Full-support enumeration, explicit WFC-E, an independently coded
   bitset WFC, and a generic minimax backend over value-free compiled topology
   agree on feasibility, value, and the complete optimal first-action set on
   **4,500/4,500** tasks, including **223** tied-optimum tasks and **1,702**
   horizon-infeasible tasks.
2. **Bounded source construction.** A separately frozen raw-SQL compiler study
   was recovered byte-for-byte and rerun. Compiler input contains raw source
   programs, finite supports, claims, candidate snapshots, and costs but no
   preservation labels, collision pairs, decoder answers, or oracle values.
   The compiler matches exhaustive native SQLite on **396/396** contracts,
   with **396/396** independently replayed certificates and **19,488**
   source-world executions.
3. **Native source-to-decision construction.** The ordered-native study reruns
   **392 traces / 128 tasks** with **128/128** complete first-action-set
   recovery. The production-root study reruns **143 traces / 52 tasks** with
   **52/52** complete recovery. Late-acquisition restrictions preserve every
   optimal value while matching only **116/128** and **13/52** complete optimal
   first-action sets, respectively.

Separately, the repaired SQL/Java source-admission gate passes **35/35** bounded
regressions locally and in GitHub Actions. The frozen prospective selector keeps
five adjudicated-positive candidates; the conservative repaired adapter licenses
two and returns three as `unidentified` abstentions. This is an
admission-coverage boundary, not a population accuracy estimate.

See `SCIENTIFIC_REPAIR_20260930.md` for the claim/evidence ledger and
`04_audits/is_cold_review/REPAIR_CONTRACT.md` for the bounded source-admission
contract.

## Engineering gate

```sh
python3 04_audits/is_cold_review/run_revision_checks.py
```

Python 3.10+ and a JDK with `java` and `javac` on PATH are required. The
current CI gate uses repository code, Python's standard library, SQLite, and
native Java execution; it does not require private local paths or secrets.

## Evidence boundaries

- WFC exactness remains conditional on explicit source correspondences A1-A5.
- The finite four-way realization check validates an explicit finite algorithm
  contract; it does not prove native source adequacy.
- The recovered raw-SQL result is limited to its declared finite integer SQL
  grammar; it is not unrestricted SQL analysis.
- Certificate re-computation is a consistency check, not an independent semantic
  oracle.
- The frozen 4,500 projection study is not a multi-implementation benchmark.
- Synthetic repair cases are not a natural cohort or prevalence estimate.
- The prospective 2/5 automatic-admission result is a coverage boundary;
  `unidentified` is not reinterpreted as `withhold`.
- The native studies are bounded constructions, not deployment-prevalence
  estimates.

Publication to this repository was explicitly authorized by the repository
owner.
