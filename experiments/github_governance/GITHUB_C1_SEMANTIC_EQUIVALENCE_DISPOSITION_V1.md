# GitHub governance C1 / semantic-equivalence disposition v1

Protocol parent: `parityplus/g4/FREEZE_MANIFEST.md` at
`c15b212ad0c2be3856a03d38802aaffa628aefd1`.

Development evidence parent:
- frozen GitHub adapter v1 / second-sample protocol in
  `experiments/github_governance/ADAPTER_V1_AND_SECOND_SAMPLE_FREEZE.md`;
- second mechanical sample Actions run `37562674312`, artifact
  `11458025511`;
- v2 observability diagnostic Actions run `37566674618`, artifact
  `11458039987`, SHA256
  `4686dcdcbccf0a31487ff896581aef6a09872dbafc6cdaccbc9dbe2dab819005`.

Status: **negative C1 closure for family-complete parity under the frozen
public-evidence model**.

This document does not alter the G4 schema, does not relabel any PR, does not
change the frozen v1 adapter, does not make GitHub G5-count eligible, and does
not open a third GitHub sample or the fifth-family holdout.

## What the diagnostic established

The frozen second sample contains 100 PRs. The v2 diagnostic performed no
adapter scoring and opened no new sample. It found:

- synthetic/test merge commit SHA present for 98/100 rows;
- merge-commit check-runs readable for 98/100 rows;
- merge-commit combined status readable for 98/100 rows;
- issue timeline readable for 100/100 rows;
- 428 `committed` timeline events, but 0 expose a GitHub push actor;
- 11 distinct base-branch protection keys were queried through the classic
  branch-protection endpoint and all 11 returned HTTP 403.

These observations improve attribution for required checks but do not supply
all effective merge-rule predicates registered by adapter v1.

## Frozen C1 requirement

The existing G4 adapter schema requires C1 support coverage for the registered
claims. The GitHub v1 freeze further requires preservation of all effective
merge-rule sources and parameters, including unresolved legacy
branch-protection and bypass/actor predicates when they are relevant.

Therefore the following are forbidden:

1. interpreting 403 or absent actor data as predicate=false;
2. dropping an unresolved predicate because the v1 sufficient-blocker rule
   does not need it;
3. redefining the registered GitHub claim after native outcomes are known;
4. making a PR count-eligible merely because its native label is scorable or
   because the conservative adapter prediction matches.

## Disposition

Under the frozen public-evidence model, **family-complete C1 is not
established**. GitHub therefore remains ineligible for:

- a family-level parity claim;
- contribution to the G5 semantic-case threshold;
- a complete B0-B10/O1-O8 family matrix interpreted as native-governance
  equivalence.

This is a coverage limitation, not a mismatch result.

The frozen positive result remains valid at its narrower claim boundary:
across the two mechanical samples, 64 scored sufficient-blocker predictions
matched the native blocked label, with zero observed mismatches. Those rows
show evidence for a conservative sufficient-blocker procedure, not complete
GitHub governance equivalence.

## Semantic-equivalence rule for diagnostic analysis only

For reproducible analysis of the GitHub development family, two rows are
diagnostically equivalent only when their lawful, pre-label observable state
agrees after removing identifiers that do not change the registered decision
problem.

The canonical diagnostic signature retains:

- normalized effective public merge-rule mechanisms and parameters;
- required review predicates and visible latest-review states;
- required check identities together with synthetic-merge-commit observations
  when readable;
- commit-signature verification predicates;
- explicit unresolved-predicate set;
- registered action `MERGE_PR`;
- continuation contract `BRANCH_GOVERNANCE_CONTINUATION`;
- declared native action vocabulary.

It excludes:

- PR number and PR URL;
- repository-local mutable request identifiers that do not alter governance
  semantics;
- sampling order and timestamps used only for provenance;
- native `mergeable`, `mergeable_state`, native label, adapter prediction,
  and any post-hoc expected label.

Because unresolved-predicate identity is retained, rows with different
coverage gaps are never collapsed into the same diagnostic class.

**This diagnostic equivalence rule does not make any GitHub row
`g4_count_eligible=true`.** Count eligibility remains false unless a future,
pre-scoring protocol version lawfully closes the missing native-governance
predicates. Such a version would require a new adapter freeze and a fresh
mechanical validation sample; it cannot retroactively upgrade v1.

## Research consequence

GitHub is retained as a development-family stress test showing the distinction

[
\text{sufficient evidence for a blocker claim}
\not\Rightarrow
\text{sufficient evidence for complete governance equivalence}.
]

This negative result is consistent with the EEQ research question: evidence
qualification is claim-relative, and missing lawful support must reduce the
permitted conclusion rather than be silently imputed.

The fifth-family holdout remains **UNOPENED**.
