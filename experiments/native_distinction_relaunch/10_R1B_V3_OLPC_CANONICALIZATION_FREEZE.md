# R1b-v3 OLPC String Canonicalization Correction — PRE-EXECUTION FREEZE

Date: 2026-10-08. Status: FROZEN BEFORE R1B_V3 SOURCE-CRYPTO RUN.

The old r1b-v1 and r1b-v2 source-only prediction artifacts are preserved
as FAILED KNOWN-POSITIVE CALIBRATIONS; no 56-cell native comparator executed.

Mechanism identified in R1d source-only format diagnostic:
- Run 37799007737, artifact 11558903682,
  outer artifact SHA256:
  86d1769a9585085374c73088294a64bd4a80a0bfba4858ff2093cce2b9104f93
- For all 7 adjacent candidate signed root envelopes, our v1/v2
  JSON.stringify-based canonical signing bytes differed from the pinned
  OLPC Canonical JSON reference: 0/7 equal.
- With reference OLPC bytes, all seven candidate updates have >=2
  independently cryptographically verified unique signer KEYIDs under BOTH
  old and new root roles. Seven candidate pairs have old/new thresholds 2.
- The reference bytes ALSO pass RSA-PSS SHA256 fixed DIGEST salt verification,
  as well as PSS AUTO. Consequently the earlier AUTO-only modification did
  NOT fix the failure; it was not required by this source inventory.

Exact v3 fix is ONE component from ORIGINAL r1b-v1:
- modify source-only canonical JSON serialization of *keys and values* of
  string type to OLPC rules: escape backslash and double quote ONLY,
  retain literal newlines/control characters in signed strings; recursively
  lexical-sort property keys and retain integer-only number handling.
- do not import @tufjs/canonical-json into the v3 extractor;
  that library is a FORMAT REFERENCE used in R1d diagnostic, not the final
  scientific extractor implementation.
- keep original r1b-v1 RSA-PSS DIGEST verifier, key dispatch, threshold
  counting, candidate version and source-pin logic unchanged.
- add frozen unit test using an RSA public PEM containing literal newlines
  and a valid RSA-PSS signature over OLPC canonical bytes; corruption
  and duplicate signatures must still be refused.

The registered state/action grid is UNCHANGED: 8 x 7 = 56 exact pinned
Bottlerocket root candidates. The unchanged historical seven accepted native
adjacent transitions are acknowledged as KNOWN DEVELOPMENT calibration, not
new prospective findings.

No native output label or tuf-js native TrustedMetadataStore is read/executed
in R1b-v3. R1c native full grid is still withheld until the resulting
predictions artifact+code lock+native comparator lock are committed in a
SEPARATE manifest. A source-only 56/56 internal self-test is not R1 PASS.

If v3 predictions still have 0 accepted adjacent trust advances, report
R1B_V3_CALIBRATION_FAILURE; do not rewrite this freeze after seeing the result.
Keep full 56-cell denominator and all adverse statuses.
