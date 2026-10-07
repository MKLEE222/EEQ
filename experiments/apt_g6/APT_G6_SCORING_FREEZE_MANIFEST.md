# APT G6 baseline-scoring freeze manifest

Protocol parent:
- G4 commit: c15b212ad0c2be3856a03d38802aaffa628aefd1

Representation mapping frozen before baseline scoring:
- APT_G6_REPRESENTATION_FREEZE.md
  - blob: aaba8d7c13e42663838d01cb96621a73248d9052
- build_representations.py
  - blob: b6e2ba806bc6faa30e852671bc923758056761fa

Common evaluator implementation repaired to match already-frozen G4 scoring:
- evaluate_representations.py
  - blob: ec55d0266f5143139d2f16e5491400cf0acbd51c
- test_evaluator.py
  - blob: 49772c89dee90f702281f01045b6c5daacf032d0

Implementation repair note:
- prior implementation used a hand-written default tie order;
- G4 requires lexicographic native-label tie breaking;
- repaired implementation now defaults to lexicographic order and emits the
  G4-required zero-error flag, mixed-case count, mixed-class label histograms,
  and confusion matrix.
This is an implementation-conformance repair, not a protocol amendment.

Pre-score CI:
- run id: 37562742356
- head: c4a558ab55f8c51dd90e6b28c3365a511efe7a6e
- conclusion: success
- artifact id: 11457610330
- artifact digest:
  sha256:30017154cddaec1828f624f9ae1d93166ca15c5cd50850ce184e7c40c2ea922b

Frozen native source reused for scoring:
- APT exhaustive run: 37258974581
- head: c6de51b2af3a7cc3abe479fa37157fab36ec3457
- aggregate artifact id: 11324225958
- aggregate artifact digest:
  sha256:177fc73578c602834d19d3842a5fb8b6cf9f46155e7d4007a45bb8a1611ff966
- native configurations: 576
- frozen core semantic templates: 144
- native mismatches against preregistered APT mechanism mapping: 0

No representation definition or scoring rule may be changed in response to the
baseline scores produced after this manifest.
