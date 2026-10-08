# WFC v2 first controlled synthetic pilot — frozen result note

Run: 37741290233
GitHub Actions job: scientific-kill-tests
Artifact: 11533693798 (eeq-wfc-v2-synthetic-kill-suite)
Artifact SHA256: 754069d50c6cad6a2fc97343dd9483c21d3d4a4a96302f257208921852d68b6b
Run commit: 280a0e9653cf21cbaefcd3cabb21d86e711608bd

This note reports the original PLAIN v2 candidate, before later shared-table
factorization optimization. The original CI artifact and code SHA manifest
remain the authoritative source. Nothing is native-scored here.

## Logical correctness

- 15 prospective unit tests passed.
- Independent brute-force action-word oracle: 120/120 unordered state pairs
  on a separate 16-state synthetic system, PASS.
- Tiny seven-state constructive mechanism: current-only decision-equivalence
  recovers the exact safe-action set on 5/7 states; lawful bounded quotient
  recovers it on 7/7.
- A provenance-audit contract splits source-distinct justifications that a
  decision-only contract legitimately merges.
- Missing required support inputs are refused; the compiler explicitly rejects
  native-outcome injection keys.

## Six-axis performance and measured storage

15 configurations, one changed axis at a time, fixed seed 20261008.
Each configuration uses 5 warmups and 30 measured compiles.
The synthetic generator intentionally contains four irrelevant history/byte
replicas per semantic transition bucket, making the compression opportunity
visible rather than pretending the carrier is natural production history.

Examples (total quotient table PLUS per-state codes versus raw state bytes):

| Workload | Raw bytes | Plain v2 encoded bytes | Encoded / raw |
|---|---:|---:|---:|
| Baseline (8 sources, 3 claims, 3 actions, 2 contracts, r=2) | 42164 | 28185 | 0.668 |
| 20 sources | 83420 | 28014 | 0.336 |
| 6 claims | 42164 | 52824 | 1.253 (regression) |
| 4 contracts | 42164 | 52464 | 1.244 (regression) |
| r=4 | 42164 | 47879 | 1.136 (regression) |

The baseline median compiler execution on the GitHub runner was 4.172 ms
and the Python process high-water RSS at that point was 19,372 KiB.
This is NOT isolated compilation RSS or native source-fetch/adapter time.
Other timing statistics are preserved in the original artifact.

## Scientifically important negative findings

1. The operator does NOT uniformly compress. Multiple contracts, claims and
   horizons can make the encoded representation larger than raw states.
2. The scaling experiment creates known nuisance metadata and duplicate
   histories; it demonstrates implementation behavior under controlled
   redundancy, not naturally observed compression.
3. The correct quotient theorem is standard finite-state partition refinement.
   Merely implementing it is not evidence of novel mathematical theory.
4. No generality claim follows for APT/Kubernetes/TUF/GitHub, or the sealed
   X.509/in-toto cases, until a new protocol version and independently frozen
   lawful adapters are developed.
5. Neither v1 G4 B10 nor any prior native score is changed.

## Follow-on

A strictly post-pilot factorization hypothesis was separately frozen before
implementation. That experiment must compare its equivalence relation to
the original v2 and its total costs on ALL 15 configurations, reporting
regressions as well as improvements.