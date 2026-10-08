# in-toto G7 source-pin discrepancy and pre-native correction v2

Date: 2026-10-08.
Status: PROSPECTIVE SOURCE-INVENTORY CORRECTION, BEFORE NATIVE SCORING.
Original G4 protocol c15b212ad0c2be3856a03d38802aaffa628aefd1
and original in-toto selection freeze remain unchanged.

## Observed blocker (retain failure)

The first intentionally NO-NATIVE-SCORING CI preflight:
GitHub Actions run 37743661121, failed at the wheel digest assertion.
All eight pinned upstream fixtures fetched successfully; the wheel downloaded
from the package index. The verifier was NOT invoked; no native labels or
holdout predictions were generated.

The earlier in-toto selection/preflight document froze the filename
in_toto-3.1.0-py3-none-any.whl with an INCORRECT SHA256:
9a5e73c8e983cdfdfb153760d532893ec0260597c09724ad875ce7950e294a79.

The package publisher's PyPI release JSON:
https://pypi.org/pypi/in-toto/3.1.0/json
explicitly lists the same named wheel with SHA256:
fe8c69a8dae32690d116bb8112e7d6da53bbad3b9a4057ff8d43f1a5a90ee2d4
and size 75177 bytes (upload date 2026-04-25).

This must NOT be treated as an innocuous CI success. Source identity
was misstated in the original selection note.

## Authorized corrective scope

The original selection document and its wrong hash remain intact as an
auditable historical record. This new source-inventory correction explicitly
supersedes ONLY its wheel digest for future PRE-NATIVE source preflight,
using the publisher's identity for the SAME pinned in-toto 3.1.0 wheel.

- No change to selected family, native version or native operation.
- No change to intended G4 V0/C1/C2/C3, core, baselines or scoring.
- No change to upstream pinned test-fixture Git blob identities.
- No change to frozen fifth-family semantic case grid or native labels,
  because neither is yet scored/frozen in this branch.
- No in-toto-verify invocation and no native prediction is authorized
  by this correction.
- If any other pinned Git blob or layout structure fails identity checks,
  retain the failure; do not substitute another fixture without a new
  explicit pre-native inventory correction.

The correction must be committed BEFORE changing the no-score preflight
script and triggering its next workflow run. If a future independent
protocol audit judges changing source identity to be a protocol amendment,
this branch cannot be treated as a clean original-v1 final holdout; keep the
record rather than conceal the possible break.

## Follow-on preflight program

Change the wheel SHA256 expected constant to the official SHA256 above;
leave the exact wheel filename/version fixed. Pin the updated script blob
into the workflow as an execution integrity check. A passing no-score run
will establish wheel/fixture identity and parsed inert structure ONLY.

Scientific status remains: G7 in-toto native outcome UNOPENED; G8 incomplete.
