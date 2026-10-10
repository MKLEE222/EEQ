# R4-E2-P1 POST-SOURCE audit freeze: qualified-leaf self-assertion attack

2026-10-10. Separate branch eeq-r4-e2-p1-qualified-leaf-forgery-20261010 from original scored source-only E2 `b1ce28715b0a1eb86e007d68d701486c974e7780`.
**POST-E2-source-only-RESULT adversarial probe**. Does NOT revise 16/16 originally checked source compiler results, no new native calls and no new original G5 cases.

## Precisely targeted scientific question

E2's generic AND/OR/THRESHOLD checker verifies source SHA256 *references*, leaf types and declared obligations, but does not independently re-open original native signed root or Policy/Binding JSON and check whether leaf Boolean claims are actually implied by them. Does a byte-identical source-attached certificate containing a falsified leaf predicate pass generic structural verification and contradict independently source-evaluated B9?

Two registered ATTACKS, fixed before making the adversary:
- P1-TUF: original E2 case `TUF|s2a|root-3-b`, registered TUF source-only B9 FALSE (ROOT UPDATE REJECT); original candidate root3-b lacks root2-a old-root authorized signature while its new-role signature is valid. Flip **exactly one FALSE old-root signer leaf to TRUE** on an IN-MEMORY COPY of the frozen E2 IR, keep candidate_root/trusted_root/anchor_root hashes, signed root bytes and every other leaf unchanged. Expect original E2 common checker to structurally ACCEPT/compute an incorrect TRUE effect, whereas independent pre-existing direct B9 result remains FALSE. Falsifying a cryptographic leaf demonstrates that hashes as REFERENCES are not proof the byte contents entail the leaf.
- P1-K8S: original E2 case `K8S|A2_BINDING_ADDED|default`, registered K8s source-only B9 TRUE (SCOPED VAP Deny). The only third policy/Binding supplies this default-Pod denial. Flip **exactly one TRUE third-binding CEL-failure leaf to FALSE** on a COPY while leaving actual old/third policy and Binding source digests, selector leaves, source roster and all original bytes unchanged. Expect original generic common checker to structurally ACCEPT/compute FALSE (no registered Deny), contradict direct B9 TRUE. This does NOT establish actual API admission ACCEPT, which E2 never certifies.

Primary denominator EXACT **2 postscore adversarial IR copies** and **0 new source/native cases**. Every attack must compare original E2 unmodified IR effect to frozen independent B9 reference before mutation; require exactly one changed Boolean field, no SHA/source-ref/actor/contract changes, and no original E2 artifact edit. If expected attack doesn't work, record a NEGATIVE falsification, not rewrite primary E2.

## Inputs pinned before adversarial execution

Original E2 Actions [38032779592](https://github.com/MKLEE222/EEQ/actions/runs/38032779592) SUCCESS, 12 Node TUF tests +34 Python K8s/generic tests, 16 generated IRs and independent direct-source B9 parity. Original artifact ID **11662422247**, outer ZIP SHA256 `a7609ac01eacb667282ef4fe02331c38b0913369358602b0e35cc041d3217fd5`. Exact original generated program and reference filenames:
`E2_TUF_8_SOURCE_RULE_PROGRAMS.json`, `E2_TUF_8_FULL_B9_SOURCE_REFERENCE.json`, `E2_K8S_8_SOURCE_RULE_PROGRAMS.json`, `E2_K8S_8_FULL_B9_SOURCE_REFERENCE.json`.
Original common structural checker source Git blob SHA `67fa774624e849d9ff31a5234fd4d8162cfb4425`. All other source/contract inputs of E2 unchanged. Avoid reading previously scored native labels or predicting any new native outcomes.

## Expected logic and scientific consequence

If P1-TUF and P1-K8s attacks both succeed, **E2_GENERIC_CHECKER_NOT_STANDALONE_SEMANTIC_VERIFIER**; at most the complete E2 workflow with separate native-source evaluation is checked. New unique EEQ capability may not be claimed from typed AST sharing. Next method improvement needs a trusted **independent primitive proof checker** that can reverify cryptographic authority/threshold against original raw bytes, and Kubernetes native actor/source/selector/CEL obligations against live appropriately scoped evidence OR an explicit trusted native attestation. These are domain-specific; B9 can use them equally, and existing proof-carrying authorization / proof-carrying data prior art remains serious.

If a bit-flipped proof is accepted as a global native admission right, that is a **scientific safety failure**, not a successful EEQ result. Original E2 only says scoped VAP Deny / no registered Deny and does not authorize global ACCEPT.

No original main/G4/B10/old G5 changes. Original G5=285, G6 C1 disputed, G8 open, fifth holdout unopened; original W1 V1 FAILURE and V2b retrospective calibration also untouched.
