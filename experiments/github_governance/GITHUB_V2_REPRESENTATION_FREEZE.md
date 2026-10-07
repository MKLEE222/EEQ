# GitHub v2 representation / G6 matrix freeze

Date: 2026-10-07

Protocol parent:
`parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md` at
`c15b212ad0c2be3856a03d38802aaffa628aefd1`.

GitHub v2 pre-native contract:
`experiments/github_governance/GITHUB_V2_C1_REPAIR_FINAL_FREEZE.md` at
`c4f5defe530bae4cb134f49b0df07cd106cd3685`.

Status: **development post-native / pre-matrix representation freeze**.

The third-sample native labels have been collected. This mapping is therefore
not a holdout and is not claimed to have been frozen before native outcomes.
Its scientific role is G6 development-family baseline/omission evaluation.

The representation builder is forbidden to branch on native labels. Semantic
signatures and all B0-B10/O1-O8 representations are constructed solely from
the already frozen v2 adapter state and the controlled-carrier governance
state. Native labels are attached only after representation construction.

## Matrix population

Include:
- every third-sample row with adapter status
  `PREDICTED_C1_COMPLETE` and a scored frozen native label;
- the frozen controlled admissible carrier in
  `GITHUB_V2_CONTROLLED_ADMISSIBLE_RESULT.json`.

Do not include:
- rows preexcluded for unavailable approving-reviewer permission;
- drafts, conflicts or native-oracle ambiguous rows.

PR number, head SHA and synthetic merge-commit SHA are retained for provenance
outside semantic equivalence but do not create semantic cases.

Semantic equivalence retains:
- registered actor class;
- legacy-protection state;
- complete effective rule types/parameters;
- ruleset source class but not mutable PR identifier;
- review-state histogram and visible approval count;
- merge-check observations without timestamps;
- commit-verification verified/reason sequence;
- registered action, continuation contract and native vocabulary.

If two executions map to the same semantic signature but have different native
labels, matrix construction fails and records a semantic-equivalence conflict.

## Frozen eeq-adapter-v1 mapping for generic B10

Registered claim:
`github-ordinary-merge-admissible`.

Support items:
1. effective governance policy;
2. pull-request review evidence;
3. synthetic-merge-commit check/status evidence;
4. commit-verification evidence.

C1 preserves source identity/provenance and all effective rule parameters.

C2 preserves, separately:
- authentication/commit-verification observations;
- review-count qualification;
- required-check qualification;
- actor-class qualification;
- claim binding to the repository/base governance context.

C3:
- action: `MERGE_PR`;
- actor class: `ORDINARY_NON_BYPASS_MERGER`;
- successor: target branch advances to the merge result;
- continuation: the branch-governance contract remains in force after merge;
- native vocabulary remains
  `NATIVE_ADMISSIBLE/NATIVE_BLOCKED`.

The unchanged generic compiler at
`062be7f533977d45e879a8026a3034913d1a6a57` must compile B10. No GitHub
branch may be added to the generic compiler.

## Frozen baseline mapping

All 19 frozen IDs are materialized.

- B0: full lawful normalized v2 governance/evidence state.
- B1: current PR evidence only: review-state histogram, merge-check
  observations and commit-verification observations; no governance rule
  source/contract.
- B2: authentication/cryptographic-validity state only: commit-verification
  observations and whether signature qualification is required.
- B3: authority/authorization only: registered actor class and effective
  governance rule types/parameters, without source provenance.
- B4: provenance/lineage only: repository/base and ruleset-source identity,
  without qualification observations.
- B5: authority + provenance.
- B6: retained rule/evidence state with the continuation contract removed.
- B7: behavioral/predictive state only, expressed as mechanism quantities
  (required vs observed approvals, required-check unsatisfied/unknown counts);
  it must not copy a native or expected label.
- B8: static selected-information state: legacy-protection state, actor class,
  approval requirement/observation and required-check qualification summary.
- B9: protocol-native hand-engineered sufficient state: B8 plus full effective
  merge-rule parameters and signature-requirement state.
- B10: unchanged generic EEQ/WFC compiler output from the frozen adapter map.

## Frozen omissions

- O1: remove repository/base/ruleset source identity while retaining rule
  parameters and qualification state.
- O2: remove review/check/signature qualification observations while retaining
  source/provenance and the registered governance contract.
- O3: remove claim-binding context (repository/base/actor binding) while
  retaining source and qualification evidence.
- O4: remove retained review/commit history; keep current governance rule and
  current check-qualification summary.
- O5: remove the branch-governance continuation contract.
- O6: suppress the action-conditioned branch-head successor relation.
- O7: retain only the immediate merge decision and omit the post-merge
  governance horizon.
- O8: omit the pull-request review support item and its observed review
  evidence while retaining the remaining compatible support mechanisms.

No omission is declared structurally N/A for this v2 carrier.

## Matrix success criterion

The strict G4 evaluator is used unchanged with
`NATIVE_ADMISSIBLE` as the accept label.

G6 repair requires at minimum:
- nine unique semantic cases are expected from the currently frozen evidence,
  but construction must recompute this rather than hard-code PR IDs;
- both native labels present;
- all 19 IDs present on every row;
- generic B10: zero mixed classes, zero conflict pairs, accuracy 1.0;
- label-permutation / no-label audit confirms all representations and adapters
  are invariant to replacing native labels after construction.

Passing this matrix does not erase the broader v1 four-repository C1
observability limitation. It closes only the frozen v2 registered ordinary
non-bypass contract used for G6 repair.
