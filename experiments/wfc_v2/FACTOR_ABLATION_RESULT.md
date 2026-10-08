# WFC v2 post-pilot factorization result — 2026-10-08

Run: 37742274735
Job: factorization-ablation
Artifact: 11533569185
Artifact ZIP SHA256:
6e750080b703f69f30fb8d93a0e881fe3fe4567f476ef83b39ab5d4d95526f73
Run commit: 07d4613ff5474f20cbf5bb999e408eeefb108e4e
Optimization design freeze: b60a102eebdab0277abd7d178821f2d8af198735

Stage: post-first-synthetic-pilot DEVELOPMENT only.
Evidence class: SYNTHETIC, zero G5 effect.
G4 frozen B10 and all prior native/holdout results remain unchanged.

## Independent correctness

- 21/21 unit tests PASS.
- All six independently varied synthetic dimensions, 15 configurations:
  factorized and original plain v2 induce exactly the same equivalence classes.
- Additional independent exhaustive 16-state oracle: 120/120 unordered
  state pairs match; the test does not use either quotient to derive the
  expected action-language equivalence.
- Future legal action sets and correction-word preservation PASS on tiny
  counterexamples; missing required evidence still produces refusal.
- Fixed-point detection uses complete deterministic finite transitions and
  does not claim bounded-equivalence at arbitrary horizon without stability.

## Total storage and compilation timing

For each axis-isolated configuration, both variants receive 5 warmups and
30 alternating timed calls within the same runner. Costs include quotient
table + observation dictionary + class codes; no hidden table exclusion.

| Workload | Raw state bytes | Plain v2 bytes | Factorized bytes |
|---|---:|---:|---:|
| Baseline | 42164 | 28185 | 9853 |
| 6 claims | 42164 | 52824 | 18424 |
| 4 contracts | 42164 | 52464 | 17766 |
| r=0 | 42164 | 8491 | 8646 (factorization overhead) |
| r=4 | 42164 | 47879 | 9853 |

Across all 15:
- factorized < plain: 14;
- factorized > plain: 1 (the horizon-0 case);
- factorized > raw: 0, on these explicitly redundant synthetic inputs;
- median ratio factorized / plain: 0.348780857;
- stable partition detected before requested depth: 3 workloads.

Performance is NOT an unqualified win. Baseline median compilation time:
plain 6.718951 ms versus factorized 8.160453 ms. The factorized variant
reduces storage while increasing compile latency for that baseline. The
full per-axis timing, IQR, p95 and exact bytes are retained in the artifact.

## Scientific limitations

1. Four explicit factual replicas per semantic state bucket were planted
   deliberately; real histories need not offer these merges.
2. The synthetic system supplies a complete, trusted transition table;
   deriving such a table from heterogeneous native mechanisms remains the
   most important unsolved compiler problem.
3. Classical finite Moore partition refinement alone is not a sufficient
   originality claim.
4. Lossless future-action sufficiency does not imply optimal serialized bits.
5. There is no native APT/K8s/TUF/GitHub superiority test for v2, and neither
   X.509 nor prospective in-toto was reused to tune this operator.
6. Source retrieval, adapter construction, and real memory/decision latency
   remain unmeasured for this v2 pilot.
7. GitHub v2 frozen G6 matrix remains a scoped v1-operator result; this
   experimental factorization does not improve that result retroactively.

Conclusion: meaningful storage optimization on controlled synthetic
redundancy with retained runtime regression; continuation to native adapters
requires a new protocol version and newly frozen independent evaluation.