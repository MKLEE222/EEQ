# GitHub governance adapter v2 C1-repair freeze

Date: 2026-10-07

Protocol parent:
- `parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md`
- freeze commit `c15b212ad0c2be3856a03d38802aaffa628aefd1`

Status: **PRE-NATIVE V2 FREEZE**.

This is a new development-family adapter instance. It does not overwrite
GitHub adapter v1, the two earlier public samples, or their retained
`C1_COVERAGE_FAILURE`.

## Registered GitHub v2 contract

Native family: GitHub repository-governance mergeability.

Registered action: `MERGE_PR`.

Native vocabulary:
- `NATIVE_ADMISSIBLE`
- `NATIVE_BLOCKED`

Registered actor class:
`ORDINARY_NON_BYPASS_MERGER`.

Bypass-capable actors are outside this v2 registered action contract. This is
consistent with adapter v1's already frozen "ordinary merger" interpretation;
v2 makes the actor class explicit rather than reading hidden bypass lists.

Native label rule is unchanged:
- admissible: non-draft, `mergeable=true`, `mergeable_state=clean`;
- blocked: non-draft, `mergeable=true`, `mergeable_state=blocked`;
- draft/conflict/other states remain retained non-scored states.

## Carrier A — public production blocked carrier

Repository: `home-assistant/core`.
Base branch: `dev`.

Pre-native observability facts used to select this carrier:
- public branch metadata reports `protected=true` but legacy
  `protection.enabled=false`;
- public ruleset `6332198` targets exactly `refs/heads/dev`;
- the public ruleset exposes the pull-request and required-status-check
  parameters;
- GitHub's public `rules/branches/dev` endpoint is required to return all
  active effective rules for the branch.

Frozen pull-request rule parameters:
- required approving review count: 1;
- dismiss stale approvals: false;
- required reviewers: none;
- code-owner review: false;
- last-push approval: false;
- review-thread resolution: false;
- extra approval for unattributed Copilot PRs: true;
- allowed merge method: squash.

Frozen required status checks:
- `code-owner-approval` / integration 97978
- `cla-bot` / integration 97978
- `docs-missing` / integration 97978
- `Collect information & changes data` / integration 15368
- `blocking-label-awaiting-frontend` / integration 97978
- `Check all requirements` / integration 15368
- `Check hassfest` / integration 15368
- `required-labels` / integration 97978

Third-sample selection is mechanical:
1. query open PRs targeting `dev`, sorted by updated descending;
2. exclude PR IDs in the first and second frozen samples;
3. take the first 25 remaining PRs;
4. never select/drop a PR because of mergeability or an adapter prediction.

### Public-row C1 admission rule

A public row is C1-admitted only if:
- base is exactly `dev`;
- branch metadata and effective-rule endpoints are readable;
- legacy `protection.enabled=false`;
- effective rules match the frozen v2 contract;
- reviews endpoint is complete;
- synthetic merge-commit check/status endpoints are complete;
- there are **zero visible APPROVED reviews**.

The zero-approval condition is frozen before the third sample because reviewer
permission is not publicly observable with the available lawful credentials.
With zero approvals, no reviewer-qualification query is required: the frozen
rule requires at least one approval, so the ordinary merger is blocked
regardless of which users would have write permission.

Rows containing one or more APPROVED reviews are retained but preexcluded as
`PREEXCLUDED_UNAVAILABLE_REQUIRED_SOURCE`, because the permission of the
approving reviewer cannot be lawfully established. They are not scored by v2.

Draft/conflict/native-ambiguous rows remain under the frozen native-oracle
taxonomy and are not silently replaced.

For an admitted zero-approval public row, v2 predicts
`NATIVE_BLOCKED`. All effective rule sources and available check/review state
are still preserved in the representation; the prediction is not allowed to
discard them merely because the approval deficit is sufficient.

## Carrier B — controlled admissible carrier

Repository: `MKLEE222/EEQ`.
Base branch: `main`.

Frozen base SHA:
`b5434ab1ad317e5121c88b632806880f903774db`.

Pre-native governance facts:
- repository ruleset list is empty;
- branch metadata reports `protected=false` and
  `protection.enabled=false`;
- therefore the complete registered governance-rule set is empty.

A fresh branch named
`g6-github-v2-admissible-control-20261007` is created from the frozen base and
adds exactly one inert marker file:
`experiments/github_governance/controlled_v2_admissible/marker.txt`.

Frozen PR title:
`EEQ G6 GitHub v2 C1-complete admissible control`.

Frozen PR body:
`Controlled-native GitHub v2 admissible carrier; never merge.`

Before reading native mergeability, v2 predicts
`NATIVE_ADMISSIBLE`, conditional on:
- base SHA still equals the frozen base;
- head has exactly the frozen one-file descendant commit;
- branch/ruleset evidence still shows no effective governance rules;
- draft=false.

The PR is closed after observation and never merged.

## Anti-leakage

The v2 adapter must not read:
- `mergeable`;
- `mergeable_state`;
- native label;
- the validation comparison result.

Third-sample and controlled-carrier predictions are determined by the frozen
rules above before native labels are joined.

## Gate use

A successful v2 result may repair the specific G6 deficiency only if:
- at least one C1-admitted/scored public production row matches
  `NATIVE_BLOCKED`;
- the controlled carrier matches `NATIVE_ADMISSIBLE`;
- no adapter schema or generic WFC core change is required;
- a GitHub B0-B10/O1-O8 matrix can be constructed on the admitted v2 carrier
  without native-label leakage.

Failure or insufficient admitted rows remains a G6 failure. It is not replaced
by a looser claim.

The already executed X.509 holdout is not modified or rerun by this repair.
