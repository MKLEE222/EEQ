# R1b-v2 negative calibration result and R1d crypto format diagnosis freeze

Date 2026-10-08.
Status: R1B_V2_RETAINED_FAILURE / R1D DIAGNOSTIC ONLY.
No first-56-cell native comparator has run under either v1 or v2.

## R1b-v2 result

Run 37798557365, code commit
56b5f7bfb9defee6a221b24b7f208ea902ef5353.
Thirteen synthetic cryptographic unit tests passed, including a variable RSA
PSS salt-length regression, and the eight pinned roots were hash-verified.

All 56 source-derived proposal rows still reported KEEP_TRUST_ROOT, including
the seven previously archived positive production-adjacent transitions.
Therefore **R1b-v2 did not repair the known-development calibration failure**.
Do not report 56/56 success, do not launch R1c native comparison, and do not
reinterpret source-only predictions as native ground truth.

Changing DIGEST to AUTO was a plausible but INSUFFICIENT single-component fix.

## R1d frozen diagnostic hypotheses (not scoring)

Inspect the exact ORIGINAL signed JSON from the pinned source bytes;
compare our independent canonical serializer to the OLPC canonical-json
implementation already pinned transitively by tuf-js@3.0.1.

D1: canonical signed JSON mismatch: equality of byte length, SHA256, first
mismatch offset / escaped snippets. This is a format-compliance check, NOT
a native root-update decision.

D2: verify the same syntactically matching RSA-PSS signatures against
(i) independently canonicalized raw-signed metadata,
(ii) reference OLPC-canonicalized raw-signed metadata,
with SHA256 and padding PSS; retain counts for AUTO, DIGEST and Node's
undefined digest algorithm. Do not change source bytes or required keys.

D3: report old/new role keyid intersection with candidate signature keyids,
signature hexadecimal length and key public encoding. Do not output raw
private keys, perform key recovery, or read archived native verdicts.

D4: if the raw reference canonical bytes are identical but NO signature
verifies, report UNRESOLVED_CRYPTO_INTEROPERABILITY. No native comparison,
no false-positive graph completeness, no opportunistic key/scheme substitution.

The diagnostic may import pinned @tufjs/canonical-json as a FORMAT REFERENCE
only; it MUST NOT call TrustedMetadataStore.updateRoot or read any earlier
native label. Distinguish this from independent final method evaluation.
Fixed source inventory / action grid still 8x7, G5 count effect 0.

Only after a mechanistically grounded result may an R1b-v3 extractor be
separately frozen and implemented. The earlier v1/v2 scripts, tests, runs
and artifacts stay immutable.
