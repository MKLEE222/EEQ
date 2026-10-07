# GitHub governance native-oracle protocol — frozen before development-family sampling

## Scope

This protocol defines only the **native observation and exclusion rule** for GitHub repository-governance cases.
It does **not** define an EEQ adapter and does not map GitHub rules to EEQ fields.

GitHub is a development family, not the final family-level holdout.

## Fixed development environments

The first development sample uses four independently maintained public repositories whose active repository rulesets are publicly readable:

- nodejs/node
- microsoft/vscode
- home-assistant/core
- llvm/llvm-project

No repository is added or removed after labels are observed in this first sample.

## Mechanical PR sampling

For each repository:

1. query open pull requests sorted by `updated` descending;
2. take the first 25 returned by the API;
3. archive the exact PR JSON, active repository ruleset list/details, combined commit status, check-runs, reviews, and requested reviewers when available;
4. archive timestamp, base ref, head SHA, and all raw JSON used by the collector.

No PR is selected or dropped because of its native outcome.

## Native decision label

The primary native oracle is GitHub's PR `mergeable_state`, conditioned on the PR being conflict-free according to `mergeable=true`.

Eligible labels:

- `NATIVE_ADMISSIBLE`: `draft=false`, `mergeable=true`, `mergeable_state="clean"`.
- `NATIVE_BLOCKED`: `draft=false`, `mergeable=true`, `mergeable_state="blocked"`.

Predeclared non-scored states retained in the ledger:

- `DRAFT`: `draft=true`.
- `CONFLICT`: `mergeable=false`.
- `NATIVE_ORACLE_AMBIGUOUS`: `mergeable=null` or a mergeable_state other than `clean` or `blocked`.

The collector may poll a PR up to three times when `mergeable` is null to allow GitHub to compute mergeability. It must retain the final raw response and poll count.

## Attribution data

Attribution data is archived but is not used to change the native label:

- active rulesets and rule parameters;
- combined commit status;
- check-runs;
- submitted reviews;
- requested reviewers;
- base/head refs and SHAs.

If an endpoint is unavailable, the failure is recorded explicitly. Missing attribution never silently changes the native label.

## Anti-leakage

- Expected EEQ labels are not generated in this branch.
- No GitHub-to-EEQ adapter is authored before G4.
- This development sample may inform feasibility and omission-test design only.
- Because GitHub semantics have already been inspected, GitHub is permanently ineligible as the final family-level holdout.

## Reproducibility

Every raw response is stored, and the output directory receives a SHA256 manifest.
