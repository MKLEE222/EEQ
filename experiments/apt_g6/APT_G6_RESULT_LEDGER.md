# APT G6 result ledger

Status: completed family-level B0-B10/O1-O8 scoring under G4.
This ledger is not a journal-strength assessment and does not close G6 globally.

Native source:
- exhaustive run: 37258974581
- 576 native configurations
- 144 core semantic templates
- zero-effect Suite/Version controls: four variants per template
- native mechanism mismatches: 0

Scoring run:
- workflow: apt-g6-baseline-scoring
- run id: 37562855844
- head: a8c1626f279420a499c9d86f4f67c33180ad9309
- conclusion: success
- artifact id: 11456589641
- artifact digest:
  sha256:4a51e997a60d1cb3128a616259591631f22d52c202ddf5df9af9a78daa36577b

Native action counts over the 144 deduplicated core templates:
- ACCEPT: 35
- BLOCK_CONFIRM: 37
- REJECT_AUTH: 72

## Representation results

| ID | n | classes | mixed classes | conflict pairs | best deterministic accuracy |
|---|---:|---:|---:|---:|---:|
| B0 | 144 | 144 | 0 | 0 | 1.000000 |
| B1 | 144 | 16 | 7 | 128 | 0.840278 |
| B2 | 144 | 2 | 1 | 1295 | 0.756944 |
| B3 | 144 | 2 | 1 | 1295 | 0.756944 |
| B4 | 144 | 2 | 1 | 1295 | 0.756944 |
| B5 | 144 | 2 | 1 | 1295 | 0.756944 |
| B6 | 144 | 16 | 7 | 128 | 0.840278 |
| B7 | 0 | 0 | 0 | 0 | N/A |
| B8 | 144 | 16 | 7 | 128 | 0.840278 |
| B9 | 144 | 144 | 0 | 0 | 1.000000 |
| B10 | 144 | 16 | 0 | 0 | 1.000000 |

B7 is structurally NOT_APPLICABLE according to the pre-score freeze.

## Omission results

| ID | n | classes | mixed classes | conflict pairs | best deterministic accuracy |
|---|---:|---:|---:|---:|---:|
| O1 | 144 | 16 | 0 | 0 | 1.000000 |
| O2 | 144 | 16 | 0 | 0 | 1.000000 |
| O3 | 144 | 40 | 3 | 54 | 0.937500 |
| O4 | 144 | 18 | 7 | 91 | 0.868056 |
| O5 | 144 | 16 | 7 | 128 | 0.840278 |
| O6 | 0 | 0 | 0 | 0 | N/A |
| O7 | 0 | 0 | 0 | 0 | N/A |
| O8 | 0 | 0 | 0 | 0 | N/A |

O6/O7/O8 are structurally NOT_APPLICABLE according to the frozen APT mapping.

## Protocol notes

- B0/B9/B10 are zero-error under the frozen multiclass native labels.
- O1 and O2 are empirically non-identifying in this controlled carrier, as
  preregistered: signer provenance and qualification are one-to-one here, and
  raw source identity is redundant after qualification/obligation compilation.
- O3/O4/O5 produce mixed representation classes.
- No representation definition was changed after scores were observed.
- Common evaluator used G4 lexicographic native-label tie breaking and emitted
  confusion matrices plus mixed-class label histograms.
