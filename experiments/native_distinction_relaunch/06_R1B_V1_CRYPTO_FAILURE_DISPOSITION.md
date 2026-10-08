# R1b source-only v1: retained negative result and crypto-format disposition

Date: 2026-10-08.

The original R1b source-only prediction experiment was frozen at commit
dae99fcd716ed5ae9ad391ee1df8229a7aa6c899 (protocol statement).
The crypto extractor implementation was subsequently committed at
4d037bd20097e163090d62c34480d57d3536b31e.

Actions run 37798000427, artifact 11559432145,
ZIP SHA256 9d07cf524bb46f76fc34dcc13420eb76e26c2068532addc8f89414357448e605.
Software run SUCCESS, 12/12 synthetic unit tests PASS.

Source-derived grid result: eight states, seven actions, 56 rows.
ALL 56 rows were assigned KEEP_TRUST_ROOT, zero ADVANCE_TRUST_ROOT,
complete_registered_graph flagged TRUE; key type/scheme inventory:
rsa/rsassa-pss-sha256.

**Scientific status = V1_EXTRACTOR_REJECTED_DUE_TO_KNOWN_POSITIVE_CALIBRATION_FAILURE.**
The seven prior archived native production-adjacent transitions root1->root2
through root7->root8 were already observed ACCEPT by the native tuf-js chain.
A model that predicts KEEP_TRUST_ROOT on all seven is inconsistent with these
known development calibration facts. DO NOT count 56 rows as successful
transition prediction or R1 gate closure.

Likely root cause from independent code audit (not yet confirmed on source
bytes): crypto.verify('sha256',...,RSA-PSS saltLength=RSA_PSS_SALTLEN_DIGEST)
rejects otherwise valid signatures using a longer PSS salt. The public
reference implementation theupdateframework/tuf-js
packages/models/src/utils/key.ts supplies RSA_PSS padding WITHOUT forcing
saltLength, and Node crypto defaults to PSS AUTO for verify. This is a
mechanistic code/format issue, not a reason to remove adverse rows.

The source-only R1b v1 artifact remains immutable. No native grid run has
been performed under its 56 predictions. A v2 candidate MUST be
pre-frozen with its own code version and source-only execution before any
independent native calibration run.

No modification to G4-v1, G5, old frozen B10, X.509, in-toto, main or
historical native labels.
