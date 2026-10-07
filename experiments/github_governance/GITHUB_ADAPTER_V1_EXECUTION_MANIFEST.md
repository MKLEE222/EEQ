# GitHub adapter v1 validation execution manifest

Adapter freeze commit:
- 635b602ac6921cc43d5c83c7f7397003b0e4eb2a

Frozen semantic blobs (re-verified after execution scorer work):
- github_adapter_v1.py
  - e94bb76e6d8c5d8b579de5ceb333a272a6f09768
- collect_validation_sample.py
  - 025b088d47fbe701b6a94aedcb81fda9c84f3633
- GITHUB_ADAPTER_V1_FREEZE_MANIFEST.md
  - 506e2695a954d7c20f8affbd7f83b33942c7f750

Execution/scoring blobs fixed before validation collection:
- evaluate_validation_v1.py
  - f9a3172034eeab6f34df9a36933a9b343b64d960
- test_evaluate_validation_v1.py
  - 287522540cac1e3d168e9ecc8224d1b478b6fba1

Execution regression:
- workflow: github-validation-execution-ci
- run id: 37562154880
- head: 445f44e7a4606d695b8b6bf0ea50cd06f6f18726
- conclusion: success
- frozen-adapter synthetic tests: success
- semantic-dedup scorer synthetic tests: success

Rule:
The validation workflow added after this manifest may only invoke the frozen
collector, adapter, and scorer blobs above. No semantic edit is permitted after
native validation labels are collected.
