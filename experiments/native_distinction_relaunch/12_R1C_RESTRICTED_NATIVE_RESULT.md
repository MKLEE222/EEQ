# R1c — Verified restricted native TUF transition extraction

Date 2026-10-08. Scientific disposition:
**R1_TUF_RESTRICTED_NATIVE_TRANSITION_CALIBRATION_PASS**.
This is NOT overall R1 multi-family/full-domain PASS and NOT R2/H3.

## Exact frozen chronology

R0 charter and R1a source-only source inventory established earlier.
R1b v1 and v2 retain **all 56 KEEP_TRUST_ROOT** known-positive
calibration failures; workflows returned green on structural assumptions
but their science-level disposition is FAIL.

Source-format root cause isolated in R1d run 37799007737:
7/7 independently verifiable old/new signer thresholds using the correct
OLPC canonical JSON serialization, versus 0/7 matching canonical byte
forms from our original JSON.stringify-based implementation.

R1b v3 OLPC fix frozen BEFORE running predictions at commit
c8134fafa28995fa92e2ec23b26497c13b5b9850.
R1b v3 source-only run 37799375569; artifact 11558989924;
outer SHA256 c37f947099c7e7bcbcce0778618123d577395dce4addd0ca291e57d84d6e30b3;
inner JSON SHA256
81b1fd5ff0b7080d33b952d4ae9e890db8e5e4260831899bf773937152f91fed.
8 trust states x 7 fixed candidate actions = 56 source-derived edges:
7 ADVANCE_TRUST_ROOT and 49 KEEP_TRUST_ROOT; 0 unresolved;
14/14 source-crypto unit tests pass, no native action labels read.

Original 56-case native comparator procedure frozen separately at
08_R1C_NATIVE_COMPARATOR_DESIGN_FREEZE.md.
Exact input/artifact and code-binary blobs pinned before native scoring in
11_R1C_FINAL_PRESCORE_MANIFEST.md, commit
d4e4700ba50ffa52c890acaa985ca52003b1189d.

## Native calibration result (new execution)

Workflow Actions 37800115473, commit
de1d08d08d76bd570df6bb0ba3680d49f26cf762.
Artifact 11560197236; outer ZIP SHA256:
be7ef19a6fb6208ab532de58526777e4b9f21e9915034fcbf1d8e89cdc0a32af.

Native oracle: tuf-js@3.0.1 TrustedMetadataStore.updateRoot, Node 22.16.0.
Every (N,M) uses a NEW native store seeded at original production root1,
replays original roots 2..N to reach trust state N and submits original
candidate rootM once. Native score was computed from the frozen independent
source-only prediction artifact, not by rerunning or tuning its extractor.

Observations:
- native ACCEPT: 7; native REJECT: 49;
- source-derived effect AND post-action trust-state match: **56/56**;
- model mismatches: 0;
- native setup failures: 0;
- predictor unsupported: 0;
- scorer synthetic anti-masking unit tests: 6/6 PASS;
- previously known development positives: 7/7 repeated as expected;
- other nonadjacent proposals: **49/49** correct under native semantics;
- G5 count increment: 0, no G4 adjustment.

## What this demonstrates

A legitimate, source-derived, bounded, deterministic root-update model has
been compiled from exact registered public root bytes and RSA-PSS signer
qualification/old-new thresholds, without consulting native decision labels.
All 56 restricted action-state effects were independently checked by
the original native client, including actual successor trust-root state.

This is an empirical **bridge over the earlier 0/294 liftability blocker
FOR THIS NEW R1 TUF ADAPTER ONLY**. It does NOT retroactively make 294 old
adapters total state graphs.

## What remains open

- Native/source extraction is only for 8 pinned root source files and
  7 pinned candidate submit actions; no arbitrary updates, missing remote
  sources, expiry, timestamp/snapshot/targets, or unbounded histories.
- No real noncosmetic **merger** has yet been demonstrated, and no
  preregistered A/B double counterfactual native pair has been scored.
- The production ordered chain contains already-known positive transitions
  and a narrow version-ordered action mechanism; B9 might achieve the same
  task accuracy with considerably less retained state in this fixed carrier.
- C1/C2/C3 correctness shown here does not establish two-family generality.
- The ordinary Moore quotient, fair B9, full cost, coverage/REFUSE and
  robust downstream task comparisons have not yet been run under a new v2
  prospective protocol.

No new unique-algorithm, information compression or KBS-strength claim is
authorized by this result alone.
