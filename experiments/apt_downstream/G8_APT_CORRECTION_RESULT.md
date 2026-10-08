# APT G8 downstream native-grid correction result — 2026-10-08

Frozen development task, NOT an unseen holdout.
Run: 37744416039, SUCCESS.
Workflow commit: fe8d759a9ce16747e3a64c7aac0d7e4a34d9bd58.
Artifact: 11535342381 (apt-g8-native-downstream-correction).
ZIP SHA256:
b786fe182c8b7f92b363662d9eee5c348ed0748afcaf3f177d7ac94dccb1d3f8.

Pinned native APT aggregate: 576 executions, 144 semantically distinct
configurations (four Suite/Version zero variants for each template).
Frozen G6 APT representations are used without change. Native histogram on
the 144 semantic cases:
- ACCEPT: 35;
- BLOCK_CONFIRM: 37;
- REJECT_AUTH: 72.

Each of 16 fixed qualified/protected-change contexts has all nine frozen
allowance contracts. All counterfactual successors for contract edits were
looked up in the original native grid. No native action was invented, and
no new native process run was required.

## Exact task-set oracle optimal accuracies (144 cases)

| Task | B0 full lawful | B1 current-only | B8 static view | B9 hand-engineered | B10 frozen generic WFC |
|---|---:|---:|---:|---:|---:|
| SAFE NEXT ACTION SET | 1.0000 | 0.6875 | 0.6875 | 1.0000 | 1.0000 |
| SHORTEST CORRECTION ACTION SEQUENCES | 1.0000 | 0.75694 | 0.75694 | 1.0000 | 1.0000 |
| LEAST-PRIVILEGE FIELD CORRECTION | 1.0000 | 0.74306 | 0.74306 | 1.0000 | 1.0000 |

In all three tasks, B9 and B10 have zero mixed output classes and zero
conflict pairs. B1/B8 mix distinct legal action sets:
- safe-next: 245 conflict pairs, 8 mixed classes;
- shortest: 179 conflict pairs, 7 mixed classes;
- least privilege: 185 conflict pairs, 7 mixed classes.

Full B0-B10/O1-O8 results, applicability and exact semantic outputs are in
the pinned artifact.

## What follows and what does not

Positive:
- A genuinely native-backed counterfactual decision task has been measured;
  not merely a one-shot ACCEPT/REJECT accuracy surrogate.
- Strongly restricted baselines lose critical future-action information.
- The full frozen B10 preserves all registered downstream legal actions.

Critical negative:
- B9 preserves those actions equally well. This APT task demonstrates
  NO incremental oracle discrimination advantage of EEQ/WFC over a
  hand-engineered sufficient state.
- These are within-grid oracle-optimal decoders, NOT held-out learning or
  generalization and NOT minimum-byte encodings.
- APT carrier has a fixed single support source and bounded one-step update;
  it cannot test the hardest source-provenance multi-support claim.
- This alone is not G8 completion because Kubernetes/TUF/GitHub downstream
  tasks, robustness, clean reproduction and broader costs remain incomplete.

Next scientific target: independently sourced, action-conditioned
multi-support histories where deleting a qualified witness changes the
future legal action set, and where an explicitly registered manual baseline
must compete with the generic compiler without post-outcome label leakage.
Do not remove B9 to fabricate superiority.