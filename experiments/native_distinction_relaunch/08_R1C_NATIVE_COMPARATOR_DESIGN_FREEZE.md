# R1c native-independent calibration — design frozen, execution NOT authorized yet

Date: 2026-10-08
Status: FROZEN NATIVE-COMPARATOR PROCEDURE / WAITING FOR R1B_V2 SOURCE-ONLY ARTIFACT PIN.

Purpose: evaluate, after exact source-only prediction freeze, the restricted
8-trust-state x 7-pinned-root proposal grid with the previously pinned native
tuf-js@3.0.1 TrustedMetadataStore.updateRoot implementation.

Do NOT create a runnable native scoring workflow until another manifest
commits all of:
- R1b-v2 source-only workflow run, artifact ID and **outer ZIP SHA256**;
- source-only predictions JSON internal SHA256;
- source-only versioned extractor Git blob;
- exact native comparator Git blob;
- pinned native package lock Git blob;
- frozen 8x7 row set with no outcome-based filters;
- explicit declaration that 7 adjacent native outcomes were already seen in
  prior v1 TUF experiments and are NOT prospective independent test cases.

## Independent native procedure

For each of 56 registered (N,M), in deterministic order N=1..8 and M=2..8:
1. Validate all root source bytes against the same pinned inventory.
2. Construct a FRESH tuf-js TrustedMetadataStore initialized with pinned
   production root1 as the declared trust anchor.
3. Replay ordered production updates root2..rootN as setup; preserve any
   setup failure as SETUP_FAILURE and do not convert it into a prediction
   mismatch or native REJECT.
4. Submit the original pinned candidate rootM once using updateRoot.
5. Record native ACCEPT / REJECT / NATIVE_ERROR or SETUP_FAILURE,
   post-action native trusted root version, native exception class/message,
   decision latency, candidate/old source hashes.
6. No change to registered action domain after seeing native outcomes.
7. Only *after* all raw native responses are saved, join by (N,M) to the
   hash-verified R1b-v2 predictor artifact. Never pass native responses
   to the extractor code.

A predicted ADVANCE_TRUST_ROOT requires native ACCEPT and post version M.
A predicted KEEP_TRUST_ROOT requires native REJECT and post version N.
A predicted MODEL_UNSUPPORTED is not scored as a correct native refusal;
retain it with a distinct model failure status and 56-case denominator.

Native setup failures/infrastructure failures also remain separately counted.
A permitted total graph cannot be declared complete if any registered
action/state lacks a verified next-state effect.

Report paired exact matches, mismatches, setup failures, unsupported rows,
native action histogram, and separate old-7/other-49 strata.
Old-7 strata are **development repeatability** only.

No new holdout family, no original G5 increment, no G4 B10 rerun and no
automatic R1_GATE_PASS. Still requires source-derivation correctness,
C1/C2/C3 scope audit, independent transition source proofs, and R2
double-counterfactual challenge before a native-method innovation claim.
