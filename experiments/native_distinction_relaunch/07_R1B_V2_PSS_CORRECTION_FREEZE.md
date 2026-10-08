# R1b v2 RSA-PSS Salt-Length Mechanism Correction — Pre-Execution Freeze

Date: 2026-10-08. Status: FROZEN BEFORE THE R1B_V2 SOURCE-ONLY RUN.

This fixes a mechanistically identified verification-parameter error in the
separately versioned source-only v1 extractor; it does NOT overwrite v1
predictions, change the registered 8x7 source/action grid, or import any
native verdict into the extractor.

## Correction (ONE semantic component)

Original line in r1b-v1:
  crypto.verify('sha256', signedBytes,
    { key: rsaKey, padding: RSA_PKCS1_PSS_PADDING,
      saltLength: RSA_PSS_SALTLEN_DIGEST }, signature)

New v2:
  crypto.verify('sha256', signedBytes,
    { key: rsaKey, padding: RSA_PKCS1_PSS_PADDING,
      saltLength: RSA_PSS_SALTLEN_AUTO }, signature)

The change permits cryptographically valid RSA-PSS SHA256 signatures with
different supported salt lengths during verification. It does not weaken
signature byte validation, SHA256/MGF1 requirements, root-source hashes,
key authorization, unique signer counting, or old/new role thresholds.
The operation is still RSA-PSS signature VERIFY with a public key.

Reason: Node's documented PSS verify AUTO discovers the signature salt
length, whereas DIGEST fixes it to the SHA256 digest length. Reference
tuf-js source packages/models/src/utils/key.ts specifies RSA-PSS padding,
without a fixed PSS verify salt length. That public implementation detail
informed this pre-native algorithm audit, NOT any new 56-cell native labels.

A dedicated synthetic unit test must first sign a valid RSA-PSS SHA256
message using MAX_SIGN salt length and verify it with the new AUTO code.
A second test must alter the signed bytes and show INVALID; old/new
dual-threshold and duplicate signatures still have to hold.

All R1b v1 source inputs unchanged:
- Bottlerocket pinned roots 1..8;
- eight registered trusted-root states;
- submit-root-2 through submit-root-8 (56 cells);
- state update iff exact N+1, old and new root signer thresholds sufficient;
- unknown cryptographic evidence -> MODEL_UNSUPPORTED;
- invalid/known insufficient evidence -> KEEP_TRUST_ROOT.

Outputs remain SOURCE-DERIVED DEVELOPMENT PREDICTIONS, never native outcomes.
If all seven adjacent proposals still fail independent cryptography, retain
R1B_V2_CRYPTO_CALIBRATION_FAILURE; do not adjust a second component in-place.

Even if seven correct predicted advances emerge, do NOT call R1 PASS.
A subsequent stage must bind the exact source-only artifact SHA, v2 script
Git blob and native package lock BEFORE isolated tuf-js grid scoring.
Old seven adjacent native results are existing development calibration, not
fresh holdout evidence. Future R2 A/B still requires independent freeze.
