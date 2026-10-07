# GitHub governance adapter v1 — frozen before validation collection

Status: **FROZEN DEVELOPMENT ADAPTER**
Date: 2026-10-07
Protocol parent: `parityplus/g4/FREEZE_MANIFEST.md` at commit
`c15b212ad0c2be3856a03d38802aaffa628aefd1`.

This adapter is a GitHub **development-family** adapter. GitHub remains ineligible
as the final family-level holdout.

## 1. Anti-leakage boundary (V0)

The adapter reads only:

- `adapter_pr_input.json` (repo, PR number, base/head/test-merge identities,
  author identity/type, timestamp);
- the active effective branch rules returned by
  `GET /repos/{owner}/{repo}/rules/branches/{branch}`;
- submitted reviews;
- calculated repository permission for every reviewer;
- check runs and commit statuses for the PR head and test-merge candidate.

It never opens:

- `native_oracle.json`;
- `native_summary.json`;
- GitHub `mergeable` or `mergeable_state` fields.

Native clean/blocked state is used only after adapter prediction for evaluation.

## 2. Registered action and decision contract (C3)

Registered action: merge the sampled, non-draft, conflict-free pull request into
its sampled base branch at the archived head state.

Adapter decision vocabulary:

- `PREDICT_ADMISSIBLE`
- `PREDICT_BLOCKED`
- `ADAPTER_UNSUPPORTED`

Native evaluation vocabulary remains:

- `NATIVE_ADMISSIBLE`
- `NATIVE_BLOCKED`

Draft, conflict, and native-oracle-ambiguous PRs remain predeclared nonscored
native states.

A supported prediction is correct iff:

- `PREDICT_ADMISSIBLE <-> NATIVE_ADMISSIBLE`, or
- `PREDICT_BLOCKED <-> NATIVE_BLOCKED`.

`ADAPTER_UNSUPPORTED` is retained in the ledger and never counted as a correct
or incorrect native prediction.

## 3. Support coverage (C1)

The active effective-rule endpoint is treated as the authoritative set of
enforced rules for the sampled base branch. The public GitHub contract states
that it returns active applicable rules and omits rulesets in evaluate or
disabled enforcement modes.

v1 supports only cases whose active rule types are drawn from:

- `pull_request`;
- `required_status_checks`;
- `creation` (irrelevant because the registered base ref already exists);
- `deletion` (irrelevant because MERGE_PR does not delete the protected ref);
- `non_fast_forward` (ordinary GitHub merge/squash/rebase updates are not
  registered force-push actions);
- `copilot_code_review` (review scheduling behavior, not itself an approval
  threshold in the registered merge contract).

Any other active effective rule type makes the case
`ADAPTER_UNSUPPORTED`. In particular v1 does not infer:

- `update` / actor-dependent bypass authorization;
- `required_signatures`;
- `required_linear_history`;
- commit/author/committer metadata restriction rules;
- merge queue;
- code scanning / deployment / secret-scanning gates;
- any unknown future rule type.

This is a predeclared support boundary, not an outcome-dependent exclusion.

## 4. Qualification fidelity (C2)

### 4.1 Pull-request approval count

For `required_approving_review_count = k`:

1. take the latest decisive review state per reviewer among
   `APPROVED`, `CHANGES_REQUESTED`, and `DISMISSED`;
2. query GitHub's calculated repository permission for that reviewer;
3. only `write` or `admin` permission counts toward the required approval
   threshold;
4. an unresolved latest `CHANGES_REQUESTED` from such an authorized reviewer
   blocks the case;
5. if the threshold cannot be decided because a potentially relevant reviewer
   permission is unavailable, the case is `ADAPTER_UNSUPPORTED`.

### 4.2 Unsupported review obligations

v1 marks the case `ADAPTER_UNSUPPORTED` if an active PR rule requires any of:

- `dismiss_stale_reviews_on_push=true`;
- `require_last_push_approval=true`;
- `require_code_owner_review=true`;
- `required_review_thread_resolution=true`;
- nonempty `required_reviewers`.

Reason: the frozen v1 evidence contract does not claim to reconstruct the
additional actor, CODEOWNERS/team-membership, merge-base, or thread-resolution
state needed for those obligations.

When `require_extra_approval_for_unattributed_changes=true`, v1 scores only
ordinary human-authored PRs. Bot/Copilot-authored cases are
`ADAPTER_UNSUPPORTED`.

## 5. Required-status-check semantics

For each active `required_status_checks` rule:

- exact required context name is preserved;
- if `integration_id` is specified, a matching check run from that exact
  GitHub App is required;
- required checks are evaluated on the test-merge commit when that commit has
  archived check/status information; otherwise the head commit is used;
- successful check-run conclusions are exactly
  `success`, `neutral`, or `skipped`;
- commit-status state must be `success`;
- if a check run and commit status with the same required name are both
  present, both must pass;
- missing required evidence is blocking, not silently accepted.

`strict_required_status_checks_policy=true` is unsupported in v1 because the
registered evidence contract does not claim an independent base-up-to-date
proof.

## 6. Mechanical post-freeze validation sample

The validation collector is frozen before execution.

Fixed repositories:

- nodejs/node
- microsoft/vscode
- home-assistant/core
- llvm/llvm-project

For each repository:

1. query open PRs sorted by `updated` descending;
2. request the first 50;
3. take positions **26 through 50** (offset 25, count 25);
4. retain every selected PR regardless of outcome;
5. collect adapter evidence and native oracle into physically separate files.

The first 25-per-repository sample used to inspect semantics is not reused as
the validation sample.

## 7. Freeze discipline

After this freeze:

- no adapter rule may be added or changed in response to validation labels;
- no unsupported rule may be promoted to supported after observing its native
  outcome;
- no PR may be removed because it disagrees with the adapter;
- endpoint/source failures remain explicit ledger states;
- any semantic change requires a new adapter version and the v1 validation
  remains attached to v1.

Validation mismatch is therefore an experimental result, not a debugging target
unless the failure is independently attributable to an implementation defect
that violates this frozen document. Such a defect must be recorded explicitly.

## 8. Primary implementation

- `experiments/github_governance/github_adapter_v1.py`
- `experiments/github_governance/collect_validation_sample.py`
- `experiments/github_governance/test_github_adapter_v1.py`

Pre-freeze compile/regression workflow:
`github-adapter-v1-pre-freeze-ci`.
