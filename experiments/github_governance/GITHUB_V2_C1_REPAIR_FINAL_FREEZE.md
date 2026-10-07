# GitHub v2 C1 repair — final pre-native manifest

Date: 2026-10-07

Status: **FINAL PRE-NATIVE FREEZE**.

Protocol parent:
- `parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md`
- commit `c15b212ad0c2be3856a03d38802aaffa628aefd1`

This manifest freezes the GitHub v2 repair implementation before:
- any third-sample native mergeability observation is joined to adapter output;
- any new controlled admissible PR native mergeability is observed.

## Frozen files

| role | path | Git blob |
|---|---|---|
| semantic contract | `experiments/github_governance/GITHUB_V2_C1_REPAIR_FREEZE.md` | `6aa399cbad08b2bdf80975abef70221ca01dfa33` |
| fresh-sample collector | `experiments/github_governance/collect_v2_third_sample.py` | `eb363b92c7751ac0ec856a42df3fc52cdc9db7f8` |
| adapter v2 | `experiments/github_governance/adapter_v2.py` | `6a5f326f34301850d4728df49c070d979638f157` |

Implementation commits:
- collector: `df9aa10e5b11aab39eba090a209218c4182acf12`
- adapter: `9d1e357cac7872439f0299194c8a0961f8fa8761`

## Frozen prior-sample exclusions

First-sample IDs:
`experiments/github_governance/FIRST_SAMPLE_IDS.json`.

Second sample:
- Actions run `37562674312`
- artifact `11458025511`
- outer ZIP SHA256
  `6c37a1c0766158be8f1224877d014a5911ae0c937a98a080482a9508435beb83`

The third sample must exclude PR IDs from both earlier samples before selecting
the first 25 open `home-assistant/core` PRs targeting `dev` sorted by
`updated desc`.

## Frozen public carrier

Repository: `home-assistant/core`.
Base: `dev`.
Ruleset identity: `6332198`.
Registered actor class: `ORDINARY_NON_BYPASS_MERGER`.

Public rows with one or more visible APPROVED reviews are preexcluded as
`PREEXCLUDED_UNAVAILABLE_REQUIRED_SOURCE` because approving-reviewer
repository permission is not observable with the lawful available credentials.

Rows with zero visible approvals are C1-admitted only when:
- legacy branch protection is proven disabled;
- the complete active effective-rule set is readable and matches the frozen
  v2 contract;
- review, merge-commit check/status and commit-chain evidence are complete.

For such rows the pre-native v2 prediction is `NATIVE_BLOCKED`.

## Frozen controlled admissible carrier

Repository: `MKLEE222/EEQ`.
Base: `main`.
Frozen base SHA:
`b5434ab1ad317e5121c88b632806880f903774db`.

Pre-native governance state:
- repository ruleset list: empty;
- branch protection: disabled.

Frozen branch:
`g6-github-v2-admissible-control-20261007`.

Frozen marker path:
`experiments/github_governance/controlled_v2_admissible/marker.txt`.

Frozen marker bytes:

`EEQ GitHub v2 C1-complete admissible control.\nNever merge this branch.\n`

Frozen PR title:
`EEQ G6 GitHub v2 C1-complete admissible control`.

Frozen PR body:
`Controlled-native GitHub v2 admissible carrier; never merge.`

Prediction before native mergeability observation:
`NATIVE_ADMISSIBLE`, conditional on the frozen base remaining unchanged and
governance state remaining empty.

The PR is closed after observation and never merged.

## Anti-leakage and success rule

`adapt_public_row()` must contain no access to `mergeable`,
`mergeable_state` or `native_label`.

A successful repair requires:
1. fresh third sample created by the frozen mechanical rule;
2. at least one C1-admitted/scored public production row;
3. zero mismatches among all C1-admitted/scored public rows;
4. controlled carrier predicted and observed `NATIVE_ADMISSIBLE`;
5. no adapter-schema or generic-core change;
6. subsequent GitHub B0-B10/O1-O8 representation freeze/scoring without
   native-label leakage.

Until all six hold, G6 remains **NOT PASS**.
