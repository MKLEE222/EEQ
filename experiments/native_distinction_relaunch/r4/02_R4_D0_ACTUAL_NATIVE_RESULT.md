# R4-D0 Actual Native Result — Controlled Same-Version Authorization Counterexample

Date: 2026-10-09
Evidence class: CONTROLLED_TUF_NATIVE_DEVELOPMENT
Disposition: **R4_D0_NATIVE_VERSION_SUFFICIENCY_KILLED_STRONG_B9_TIE**.
Not R4 P3 measured, not independently novel EEQ method.

## Immutable chronology and source origin

Initial design freeze 00_R4_D0_TUF_AUTHORITY_PRESOURCE_FREEZE.md,
standalone commit 809ede9abd6d70eedc2ab2162b2a92f8f54f963e.

Source-only Ed25519 signature generation, complete source-derived
old/new authority qualification, 2x4 predictions: GitHub Actions
run 37914129494 commit 51aade6f3877ead6872b6ea47f33e63668c4256a.
12/12 synthetic cryptographic tests PASS.
Source-only artifact id 11608811184 / SHA256:
2490380d7424bc7f86216cfeb691ab0c90e8a412d65ff1a3887db3aec135a26d.

Internal frozen source manifest SHA256:
268e9244b57ca7c0a305434be3085d02e4d02d4085bf419bffb6f84045c7736a.
Internal frozen source prediction SHA256:
fa8dd5a40667dea0acd9984d2d5ab0c33ea2148cef314fbc9751df34805d8aa0.
Independent hash-only workflow run 37914513814 verified both pre-native.

Synthetic join-only anti-masking tests: 10/10 PASS, pre-native
Actions run 37914550754.

Final exact code blob/source/protocol manifest:
01_R4_D0_FINAL_PRESCORE_MANIFEST.md at Git commit
8b9f962573b5e440db8988c78c72d78507cbb856.
No D0 native root-update operation was executed before this freeze.

An initial Actions workflow at commit
3bcc1cf090235c7c51647546033c52ab0a984bdf,
run 37914720997, was rejected by GitHub as invalid YAML because a
STEP NAME with a colon was unquoted. That run spawned **ZERO JOBS**,
produced NO native labels, and is infrastructure scheduling failure
ONLY. Its bad YAML is retained in commit history. The fix at
397b9382317f8f99134fa1398dea78e7d053ba8d only quoted the
step title; all prescored sources, native/scorer code blobs, artifact
pins and cases were unchanged.

Successful FIRST native grid:
- Actions run **37914808546**, commit
  397b9382317f8f99134fa1398dea78e7d053ba8d
- Native artifact ID **11609456107**
- Native artifact ZIP SHA256:
  6717ce540a556951dd01f5a9e34a724df17c37564f16e2c034ed75dbb60e745c
- Native oracle: pinned tuf-js@3.0.1 TrustedMetadataStore.updateRoot;
  independent native runner read only original 7 signed source files
  and their SHA256 manifest, NOT SOURCE_PREDICTIONS.json.
- Native raw JSON was written BEFORE the join-only scorer ran.
- Output validates exact expected post-trust ROOT SIGNED BODY AND
  SIGNATURE-SET identity. This is necessary: all candidate root3 signed
  bodies are intentionally IDENTICAL, and matching version only would be
  a false identity check.

## Native matrix: exact eight registered cells

| Starting native signed root | root-3-A (A + NEXT signed) | root-3-B (B + NEXT signed) | root-3-old-only (A signed) | root-3-new-only (NEXT signed) |
|---|---|---|---|---|
| s2a (trusted root version 2, role A) | ACCEPT -> root3A | REJECT -> root2A | REJECT -> root2A | REJECT -> root2A |
| s2b (trusted root version 2, role B) | REJECT -> root2B | ACCEPT -> root3B | REJECT -> root2B | REJECT -> root2B |

Both initial state setups succeeded independently from ONE anchor:
2/2 NATIVE SETUP controls.
Native exact decision plus trusted successor SIGNATURE ENVELOPE IDENTITY:
**8/8**.
Native mismatches: 0; setup failures: 0; unsupported: 0.
Both native contrary-output witnesses hold on the EXACT SAME candidate
source bytes under s2a vs s2b (root3A and root3B).
No source, state, candidate or action was dropped.

The experiment is a direct bounded counterexample to sufficiency of:
  (trusted root VERSION=2, candidate root VERSION=3,
   candidate SOURCE ID).
There are still opposite outcomes at the same projected features.
An oracle-optimal deterministic decoder on that insufficient
representation attains at most **6/8** (development only).

A FULLY INFORMED source- and signature-aware B9 can implement the same
old/new-root verification rules and get **8/8** on EXACT same lawful data.
This is an expected tie, not a deficiency we may hide or circumvent.
The native TUF verification algorithm is standard protocol engineering.

## Scientific disposition and next claims

What is demonstrated:
- Real, cryptographically verified old-root authority differences
  cause a necessary decision distinction even at identical trusted
  and candidate versions and identical candidate source;
- Source-only new v2 program can produce a correct bounded qualified
  transition model before native labels, with eight independent native
  checks; provenance/threshold signer sets are disclosed.

What is **NOT** demonstrated:
- A new algorithm beyond standard TUF old/new root signature semantics;
- Exclusive EEQ advantage over B9 or a conventional quotient;
- A generalized lawful source-to-certificate extractor across ecosystems;
- Reduced domain-specific semantic maintenance effort (future P3);
- Source-unavailable/REFUSE superiority, native transfer to unseen family;
- Any new original v1 G5 semantic cases, G4/G6/G7/G8 closure.

Therefore: R4-D0 COMPLETE WITH LIMITED NEGATIVE-TO-VERSION RESULT.
R4 PRIMARY P3 and general native-method H3 are STILL OPEN.
No old frozen EEQ score, main, G4 protocol or prior holdout was modified.
