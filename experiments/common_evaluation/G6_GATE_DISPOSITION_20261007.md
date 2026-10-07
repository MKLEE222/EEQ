# G6 gate disposition — baselines, omissions and negative controls

Date: 2026-10-07

Protocol authority:
- G4 freeze commit `c15b212ad0c2be3856a03d38802aaffa628aefd1`;
- original gate ordering: G0-G4 prerequisites -> G5 breadth -> G6
  baselines/omissions/negative controls -> G7 unseen fifth-family holdout -> G8
  scaling/robustness/downstream/clean reproduction.

Status: **G6 DISPOSITIONED WITH RETAINED GITHUB C1 COVERAGE FAILURE — NOT PASS**.

This document records that the preregistered development-family baseline,
omission and negative-control obligations were executed or explicitly
dispositioned. It is an execution/disposition record, not a clean gate pass.

Because the intended GitHub development family still lacks family-complete C1
support coverage under the lawful public-evidence model, G6 must not be
reported as PASS/CLOSED in the scientific gate sense.

## Final 285-case B0-B10 / O1-O8 matrix

Actions run: `37577515052`.

Artifact:
- id: `11463213360`;
- name: `g6-final-285-generic-wfc-matrix`;
- ZIP SHA256:
  `90f6b9562aa7e76caf1f8c252cf5483dbcca4729b61687a8805a3cd105c81d85`.

The run reconstructs historical frozen family-specific B0-B9/O1-O8 mappings
from their original pinned commits/blobs, and replaces only B10 with the same
frozen domain-agnostic generic WFC v1 compiler at
`062be7f533977d45e879a8026a3034913d1a6a57`.

All 285 G5 semantic cases are present exactly once. The strict evaluator
requires all 19 frozen IDs on every row; structural N/A cells require reasons.

Generic B10 results:

| Domain | n | B10 classes | mixed classes | conflict pairs | best deterministic accuracy |
|---|---:|---:|---:|---:|---:|
| APT releaseinfo | 144 | 144 | 0 | 0 | 1.000000 |
| K8s 5-Spot | 38 | 38 | 0 | 0 | 1.000000 |
| K8s Flux | 10 | 10 | 0 | 0 | 1.000000 |
| K8s GCS Fuse | 14 | 14 | 0 | 0 | 1.000000 |
| K8s Volcano | 72 | 72 | 0 | 0 | 1.000000 |
| TUF Bottlerocket root | 7 | 7 | 0 | 0 | 1.000000 |

The TUF carrier remains all-ACCEPT and therefore cannot provide within-carrier
discrimination evidence; its matrix is construction/applicability/cost evidence.

## Baseline and omission coverage

The frozen taxonomy contains B0-B10 and O1-O8.

- APT: all 19 IDs are represented; B7 and O6/O7/O8 are structurally N/A under
  the frozen carrier.
- Kubernetes Flux/GCS Fuse/Volcano/5-Spot: all 19 IDs are represented; IDs that
  require unavailable authentication/provenance/longer-horizon/multi-support
  structure remain structural N/A with frozen reasons.
- TUF: all 19 IDs are applicable and constructed under the frozen TUF
  representation mapping.
- GitHub: a family-complete 19-column matrix is **not fabricated** because
  frozen v1 C1 support coverage is incomplete under the lawful public-evidence
  model.

Thus the protocol's approximately ten baseline families and eight omission
ablations are covered wherever structurally applicable; structural N/A remains
a valid result rather than being replaced by invented numeric cells.

## Negative controls

### APT — PASS

Frozen distinctions: Suite and Version.

The exhaustive native artifact contains 576 configurations for 144 semantic
templates, four Suite/Version variants per template. All 144 templates contain
all four variants and all four native actions agree within every template.

### Kubernetes — PASS

5-Spot provides five explicit unscoped binding controls:
baseline, host_network, privileged_rw, hostpath_root and cap_sys_admin.

All five are native `ACCEPT` in the frozen semantic ledger. The complete
5-Spot grid also reproduced with zero mismatches on Kubernetes v1.34.3 and
v1.35.0 in Actions run `37565593683`.

Flux/GCS Fuse/Volcano additionally contain frozen policy-scope zero controls,
but they are not needed to inflate the per-family minimum.

### TUF — PASS

Section-7 invariant-control freeze:
`6c4c664ef102f9b47fafe16941921f649d9b3c44`.

Actions run `37576522839`:
- compact JSON reserialization of production root 2: ACCEPT -> ACCEPT;
- top-level signature-array reordering of production root 3: ACCEPT -> ACCEPT.

Result: 2/2 matched, 0 mismatches, real bytes changed, G5 count effect zero.

The older replay/unsigned/tamper rejection tests remain robustness/adversarial
evidence and are not relabeled as Section-7 controls.

### GitHub — PASS for Section-7 controlled invariants

Control freeze:
`5a4148b56e8296627186fec13bc0af7b76da46bb`.

Controlled-native PR:
`MKLEE222/EEQ#2`, never merged and closed after observation.

Fixed base/head:
- base `main@b5434ab1ad317e5121c88b632806880f903774db`;
- head
  `g6-github-section7-controlled-20261007@01e4529881733787b47709a29b50641a71461ab9`.

Native observations:
1. initial: `mergeable=true, mergeable_state=clean`;
2. body-only metadata perturbation: still `clean`;
3. title-only metadata perturbation: still `clean`.

Both preregistered controls therefore preserve
`NATIVE_ADMISSIBLE`: 2/2 matched, 0 mismatches.

These controls do not repair the separate public-production C1 limitation.

## Retained GitHub limitation

Across the two public GitHub mechanical samples:
- 146 rows have scorable native labels;
- 64 conservative sufficient-blocker predictions are scorable;
- all 64 matched;
- family-complete C1 is not established because required public governance
  predicates remain unavailable or unresolved.

Therefore:

[
\text{GitHub sufficient-blocker evidence}
\neq
\text{GitHub family-complete governance equivalence}.
]

This is retained as `C1_COVERAGE_FAILURE`, not converted into a method success
and not used to make GitHub G5-count eligible.

## G6 disposition

- frozen baseline taxonomy: covered;
- O1-O8 omissions: evaluated wherever structurally applicable;
- generic WFC B10: integrated across all 285 closed G5 cases;
- >=2 negative controls per development family: satisfied;
- known method/coverage failures: retained rather than hidden.

Therefore the G6 experimental work is **DISPOSITIONED**, but the overall gate
status is:

[
\boxed{\texttt{G6 NOT PASS}}
]

The blocking condition is the retained GitHub
`C1_COVERAGE_FAILURE`: a family-complete GitHub governance representation and
full baseline/omission interpretation are not lawfully established.

A sealed X.509 holdout was subsequently executed after these G6 experimental
obligations had been dispositioned. Its 7/7 native result remains valid as a
separately frozen holdout result, but it must not be narrated as
`G6 PASS -> G7 PASS`, and it does not retroactively repair this G6 failure.

No journal-strength/KBS conclusion is authorized by this disposition alone.
