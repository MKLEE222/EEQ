# EEQ: decision-sufficient information states under endogenous evidence change

Public repair and reproduction workspace for **Endogenous Evidence Qualification:
Decision-Sufficient Information States for Acting Systems**.

## 2026-09-30 repair status

The cold-start review found two claim-bearing execution problems and the revised
paper now treats them explicitly.

1. The frozen 4,500-contract runner used the same exact `MethodView` for several
   algorithm-labelled rows. Those rows are no longer counted as independently
   executed WFC implementations. The 4,500 contracts are used as an
   **information-projection sensitivity study**, with exact contract information
   counted once as a reference.
2. SQL/Java source admission could emit positive certificates outside its
   justified grammar. The repaired admission gate fails closed on the diagnosed
   alias, control-flow, and indirect-write counterexamples. The bounded repair
   suite passes **35/35** locally and in GitHub Actions.

The construction claims are now carried by two fresh source-to-decision reruns:

- ordered native study: **392 traces, 128 tasks, 128/128 complete first-action-set recovery**;
  the late-acquisition restriction preserves every value but matches only
  **116/128** complete optimal first-action sets;
- production-root study: **143 traces, 52 tasks, 52/52 complete recovery**;
  the late-acquisition restriction preserves every value but matches only
  **13/52** complete optimal first-action sets.

The frozen prospective selector retains five adjudicated-positive candidates.
With the repaired conservative adapter, **2 are licensed and 3 are
`unidentified` abstentions**. The independent source/route adjudicator supports
the registered licensing relation in all five candidates. This is reported as a
fixed selected-case **admission-coverage audit**, not a population accuracy
estimate.

See `SCIENTIFIC_REPAIR_20260930.md` for the claim/evidence ledger and
`04_audits/is_cold_review/REPAIR_CONTRACT.md` for the bounded source-admission
contract.

## Engineering gate

```sh
python3 04_audits/is_cold_review/run_revision_checks.py
```

Python 3.10+ and a JDK with `java` and `javac` on PATH are required. The
current CI gate uses only repository code, Python's standard library, SQLite,
and native Java execution; it does not require private local paths or secrets.

## Evidence boundaries

- WFC's exact finite result remains conditional on explicit source
  correspondences A1-A5.
- Certificate re-computation is a consistency check, not an independent semantic
  oracle.
- The 4,500-contract study is not a multi-implementation benchmark.
- Synthetic repair regressions are not a natural cohort or prevalence estimate.
- The prospective 2/5 automatic-admission result is a coverage boundary;
  `unidentified` is not reinterpreted as `withhold`.
- The native studies are bounded constructions, not deployment-prevalence
  estimates.

Publication to this repository was explicitly authorized by the repository
owner.
