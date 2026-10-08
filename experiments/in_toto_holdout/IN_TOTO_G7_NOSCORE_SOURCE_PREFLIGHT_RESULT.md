# in-toto prospective source-only preflight result — 2026-10-08

This is NOT native holdout scoring and NOT a G7 final-pass result.

## Original no-score integrity failure retained

- First run 37743661121 failed correctly on SHA256 mismatch.
- Original selection document expected wheel SHA256:
  9a5e73c8e983cdfdfb153760d532893ec0260597c09724ad875ce7950e294a79.
- PyPI published in-toto 3.1.0 wheel has SHA256:
  fe8c69a8dae32690d116bb8112e7d6da53bbad3b9a4057ff8d43f1a5a90ee2d4.
- The source-pin discrepancy was recorded BEFORE any corrective code edit in
  IN_TOTO_G7_SOURCE_PIN_CORRECTION_V2.md at commit
  6946bd18fe179720aabcbd77b93b6089fa40a3a6.
- The original erroneous selection note remains unchanged. This is not a
  disguised source replacement after outcome inspection.

## Corrected pre-native source-only run

GitHub Actions run 37744948626, SUCCESS.
Workflow commit cb6be5ddbf30028d6d22e9cba9b0424abe221118.
Artifact 11534994976, name in-toto-g7-no-score-source-preflight.
Artifact ZIP SHA256
3ac7a24d6f3f75b39ce4a970a1a0c2485a1e6e24d59a24b9bf52601a0d9c6ff2.

Verified:
- exact published wheel filename/version/digest;
- all 8 pinned upstream Git blob SHA1 identities at commit
  c82fe5d21aaa61c7f1a213db20a46f10bb3f411a;
- inert JSON layout/link shape with 2 declared steps and 1 inspection;
- no wheel installation or signing was performed in this source-only run;
- NO in-toto-verify call or imported native verification routine;
- no native labels, native predictions, or holdout scoring.

## Boundaries

In-toto is still a PROSPECTIVE UNOPENED FAMILY; it has not passed G7.
The next legitimate work is to version/freeze exact case bytes, complete
lawful V0+C1-C3 adapter/registered continuation semantics, and freeze all
predictions BEFORE the first native call. Whether it is needed as a
replacement for the valid earlier X.509 transfer experiment remains under
the independent original-protocol gate chronology audit.

Do not call this preflight success a fifth-family generalization test.