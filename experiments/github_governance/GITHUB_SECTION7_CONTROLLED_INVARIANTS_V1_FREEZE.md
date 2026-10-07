# GitHub Section-7 controlled invariant controls v1 — freeze before native execution

Protocol parent:
- `parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md` at
  `c15b212ad0c2be3856a03d38802aaffa628aefd1`;
- GitHub native-label rule:
  `experiments/github_governance/GITHUB_NATIVE_ORACLE_PROTOCOL.md`.

Status: **development-family negative-control freeze before controlled native execution**.

This experiment adds one controlled GitHub environment in the same native
family. It does not change the four public-repository production-history
sample, does not make those rows C1-complete, and does not contribute semantic
cases to G5.

## Controlled object

Repository: `MKLEE222/EEQ`.

Base branch: `main`.

A fresh experiment branch is created from the then-current `main` SHA and
adds one inert experiment marker file under
`experiments/github_governance/controlled_section7/`.

One pull request is opened from that experiment branch to `main`.
Throughout all observations:

- base branch and base SHA are unchanged;
- head branch and head SHA are unchanged;
- no commit is added after the first native observation;
- draft state remains false;
- only PR-level descriptive metadata is changed.

## Native oracle

Use the existing GitHub native labels:

- `NATIVE_ADMISSIBLE`: `draft=false`, `mergeable=true`,
  `mergeable_state="clean"`;
- `NATIVE_BLOCKED`: `draft=false`, `mergeable=true`,
  `mergeable_state="blocked"`;
- all other states remain nonscored under the existing protocol.

For each observation, GitHub may be polled up to three times if
`mergeable` is null, matching the frozen native-oracle discipline.

The control compares native labels before and after each perturbation. It does
not require the label to be ACCEPT/clean in advance.

## NC1 — PR body perturbation

Initial title:
`EEQ G6 controlled Section-7 invariant probe`.

Initial body:
`Controlled-native GitHub Section-7 probe. Phase=0.`

Perturbation:
replace only the PR body with
`Controlled-native GitHub Section-7 probe. Phase=1 body-only perturbation.`

Prediction:
the native action is unchanged.

Rationale:
the registered native governance decision is mergeability under branch
governance. PR descriptive body text is not itself a registered support,
qualification, check, review, commit-verification, or branch-governance
predicate. If GitHub nevertheless changes the native action, retain the
mismatch.

## NC2 — PR title perturbation

Starting from the NC1 state, replace only the PR title with
`EEQ G6 controlled Section-7 invariant probe — title perturbation`.

The body, base/head SHA, commits, draft state and all other deliberately
controlled fields remain unchanged.

Prediction:
the native action is unchanged.

Rationale:
the title is a real PR metadata distinction but is not itself a registered
support/qualification predicate in the frozen GitHub adapter contract.
A changed native action is retained as a failed negative control.

## Anti-tuning and cleanup

- Both perturbation strings above are frozen before the test PR exists.
- The experiment does not edit branch rules, reviews, checks, commit
  signatures, or head commits after the first observation.
- The PR is closed after the final observation and is never merged.
- Failure, ambiguity, or API unavailability is retained; no replacement PR is
  substituted after outcomes are observed.
- These controls have `g5_count_effect=0`.
- The public GitHub family-complete C1 disposition remains unchanged.
- The fifth-family holdout remains **UNOPENED**.
