# GitHub adapter v1 freeze manifest

Protocol parent:
- G4 freeze commit: c15b212ad0c2be3856a03d38802aaffa628aefd1

Frozen adapter artifacts:
- GITHUB_ADAPTER_V1_FREEZE.md
  - Git blob: a65be129b905c413a93e0fbd6c5b8e3d44247e3e
- github_adapter_v1.py
  - Git blob: e94bb76e6d8c5d8b579de5ceb333a272a6f09768
- collect_validation_sample.py
  - Git blob: 025b088d47fbe701b6a94aedcb81fda9c84f3633
- test_github_adapter_v1.py
  - Git blob: b56bc7d842675b9948287412b4e1c7960f158a7b

Pre-freeze implementation check:
- workflow: github-adapter-v1-pre-freeze-ci
- run id: 37561823486
- head commit: 62b340dc2bc020b48104ba994554791a9baa644b
- conclusion: success
- artifact id: 11456862811
- artifact digest:
  sha256:c74a413b30b370046fa98eec9e73ff772871f7be1c34464cb73c711dc8c2a7c9

Development evidence used to define the support boundary:
- enriched first sample run: 37270160203
- enriched first sample head:
  9c661d899b57bbcd0cb694aa1c2936c627ac9199
- enriched artifact id: 11327648114
- enriched artifact digest:
  sha256:851ac6dce9070be3947010d9e889b4043fc2b58eb5343cb7939e5cac32a50541
- label-blind policy input audit run: 37561291293
- audit head: 436bfa17b7b9b54c1880f261dcafdc3cae024e0b
- audit artifact id: 11456662319
- audit artifact digest:
  sha256:8b7335d74eeb6d6ae4975814b8f836f76589fdcdbede67334986ad8d1beeb7d5

Freeze rule:
No validation sample may be collected before this manifest is committed.
No adapter/collector semantic change is permitted after this manifest commit
without creating a new adapter version. Execution-only workflow plumbing may
be added later provided it invokes the frozen blobs above without modifying
their semantics.
