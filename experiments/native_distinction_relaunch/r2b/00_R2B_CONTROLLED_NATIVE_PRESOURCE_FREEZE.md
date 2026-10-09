# R2B-v1 — Controlled Native TUF Role-Qualification Contrast: PRE-SOURCE FREEZE

Date: 2026-10-09
Parent EEQ research: eeq-native-distinction-relaunch-20261008 at
0c4fc8d2fec3c88550abd5b24d65cfb9656c72b3.
Status: R2B DESIGN FREEZE ONLY. NO CONTROLLED SOURCE BYTES GENERATED;
NO NATIVE R2B ORACLE RESULTS OBSERVED.

## Scientific purpose and non-novelty warning

Test B side ONLY: bona fide differences in AUTHENTICATED TUF 'targets' role
authorization may be lawfully coalesced for a PREDECLARED 'root-update only'
continuation contract while they MUST be distinguished for a target-role
qualification claim.

This does NOT test action-induced future separation A. No broad R2 PASS
without separately frozen A and source/refusal pressure. No expectation of
independent advantage over an informed B9 or a classical Moore quotient.
This is deliberately designed as a falsification attempt under strong B9.

The prior 8-production-roots/7-actions R1e negative result (8 singleton
classes, 0 merges) is retained unchanged. These newly signed test sources
are CONTROLLED_NATIVE, never production history or new holdout.

## All fixture generation decisions locked BEFORE source bytes exist

Only fixed, public, dedicated test keys (NOT production root signing keys):
Ed25519 private seed = SHA256(UTF8("EEQ_R2B_CONTROLLED_PUBLIC_TEST_ONLY_V1/" + label)).
Labels EXACTLY: ROOT, TARGET_A, TARGET_B, SNAPSHOT, TIMESTAMP.
Use Node built-in crypto PKCS8 ed25519 seed -> public SPKI, hex public material.
Keys are deliberately reproducible, PUBLIC TEST MATERIAL; never use for
production or security deployment. Sign using Node crypto.sign(null, OLPC
canonical signed JSON bytes, Ed25519 privateKey).
Key ID = SHA256(UTF8(OLPC canonical JSON of the public TUF key object)).
No external test datasets, random seeds, or hidden private credentials.

Source root documents, ALL to be produced exactly once under pinned
source-generator code:
- root-1-common.json, common self-signed trust genesis anchor;
- root-2-a.json, root-2-b.json;
- root-3-a.json, root-3-b.json;
- root-4-a.json, root-4-b.json;
- targets-a.json, targets-b.json.

All root signed metadata:
- _type=root; spec_version=1.0.31;
- expires=2036-01-01T00:00:00Z;
- one shared ROOT Ed25519 key / threshold=1 in role root;
- snapshot and timestamp have one fixed distinct key and threshold=1 each;
- for variant A: targets role contains TARGET_A key / threshold=1;
  for variant B: targets role contains TARGET_B key / threshold=1;
- root-1-common uses TARGET_A as genesis target role;
- signed metadata version is integer 1,2,3,4 as named;
- consistent_snapshot=true;
- each root is correctly self-signed by shared root key;
- the role-authority difference is REAL (valid authenticated target key
  qualification), not JSON serialization, whitespace or source version.
- each targets source (_type=targets, spec_version=1.0.31, version=1,
  expires=2036-01-01T00:00:00Z, targets={}) is signed only by its own
  TARGET_A or TARGET_B private test key respectively.

## Registered native state histories and action grammar

A single common trusted anchor root-1-common exists.

Start states (all reachable by native root updates from common anchor):
  s2a = root1-common -> root2-a
  s2b = root1-common -> root2-b
  s3a = root1-common -> root2-a -> root3-a
  s3b = root1-common -> root2-b -> root3-b
  s4a = root1-common -> root2-a -> root3-a -> root4-a
  s4b = root1-common -> root2-b -> root3-b -> root4-b.

Registered root-update actions EXACTLY:
  submit-root-3-a, submit-root-3-b,
  submit-root-4-a, submit-root-4-b.
No post-result action filtering or horizon changes.

Root-update-only decision contract J_root:
- output per action = ACCEPT and successor trust root, or REJECT and
  unchanged trust root;
- action sequences of length 0,1,2 from EVERY registered starting state,
  independently reset native store before each sequence;
- two histories may merge for J_root only if ALL their action-word
  output traces length <=2 are equal under these exact actions, and
  the quotient retains provenance separately for auditing.
- note J_root deliberately EXCLUDES targets delegation decisions;
  do not claim equivalence for the entire TUF system.

Distinct targets-role qualification negative control J_targets:
For every one of the six states, independently test both targets-a.json
and targets-b.json under tif-js root.verifyDelegate("targets", targetMd).
(Expected 6 positive + 6 negative in 12 checks, with A/B state suffix
selecting the valid target signer.) If the native library does not expose
a lawful delegate verification with this source format, mark CONTROL_BLOCKED
rather than silently declaring a real authorization difference.
For the combined contract J_root+J_targets, A/B root histories must NOT
be claimed equivalent at each version.

## Source-derived *before-native* predictions

The independent source-only generator MUST:
- include exact SHA256/byte length of all nine source fixtures;
- verify cryptographic root and targets signatures with Node built-ins,
  no tuf-js imports and no previous native labels;
- compile 6 states x 4 fixed root-update actions = 24 cells;
- expectation 8 advances (from version2 submit version3 candidates,
  or version3 submit version4 candidates), 16 retains;
- C3: all successor states within the six registered states;
- exact source-derived entire 0..2 action-word trace partition: expect 3
  classes {s2a,s2b},{s3a,s3b},{s4a,s4b}, i.e. 3 noncosmetic valid merges
  from 6 evidence states (relative to J_root);
- source-derived TARGET_A/TARGET_B qualifier difference: expected 12
  control checks, exactly one valid target signer per state;
- expert B9 version-only, with full knowledge of this registered native
  root signer/actions/contract, has 24/24 SOURCE predicted matches;
- classical standard quotient on the SAME derived graph is expected to
  produce the SAME three classes as the candidate, NO novelty advantage.

All expectations are pre-declared before source generation. If they fail
source-crypto checks, retain SOURCE_PILOT_FAILURE, do not silently alter
keys, roles, action set or horizon to rescue results.

## Two-stage scored execution rule

STAGE I source-only:
- commit generator/extractor and tests AFTER this freeze;
- one GitHub Actions job builds the nine signed source fixtures, hashes them,
  saves source-only 24 predictions and full trace partition;
- DO NOT install or import tuf-js in stage I.
- pin stage-I artifact ZIP digest, internal source manifest / predictions
  SHA256s, exact source generator and tests Git blob SHA in a SECOND freeze.

STAGE II native-only (not before STAGE I freeze):
- use pinned tuf-js@3.0.1 from locked package-lock;
- restore exact original controlled signed fixtures and independently
  recheck their hashes against the frozen manifest;
- native verifier receives source fixtures ONLY, not source predictions;
- run native initialization from common anchor then frozen setup
  paths for six states; abort/record if a setup path is invalid;
- execute all 24 one-step cells with fresh native store, recording
  ACCEPT/REJECT and precise next trusted root source identity and version;
- execute all registered 0..2 root-update action-word traces from each
  start state (6*(1+4+16)=126 total paths); no skipped or collapsed paths;
- verify all 12 target-delegation negative-control checks in native library,
  including post-source role qualification distinction;
- AFTER raw native evidence archived, join with frozen predictions without
  changing any source or action registration;
- report completeness, mismatches, native setup failures, ambiguity
  separately, with absolute 24/126/12 denominators.

A native-root version match ALONE is insufficient to validate successor
identity; root signed-source SHA/branch must also match.

## Strong baseline and interpretation

B9 allowed exact current trusted root version and all signer/role inputs,
plus full native root-update rules. Version-only is a permissible compressed
sufficient representation *for J_root* and must be tested; do not weaken it.
Classical Moore quotient gets SAME complete source-derived transition graph
and all actions. Equality is a valid control, not an EEQ win.

Even if everything matches:
- label R2B_CONTROLLED_NATIVE_CONTRACT_RELATIVE_MERGE_FEASIBLE;
- A remains UNOPENED, R3/R4/R5 remain UNOPENED;
- no general TUF compression, no performance/novelty victory, no new
  production-history or original G5 increment.
- state-origin audit and J_targets MUST still separate the evidence states.

Failures: unknown source -> SOURCE_UNAVAILABLE, not REJECT;
crypto unsupported -> MODEL_UNSUPPORTED, not native false;
native disagreement -> NATIVE_MISMATCH with frozen unedited predictions;
target qualifier fails to separate variants -> B_NONCOSMETIC_NOT_DEMONSTRATED.

Changes from this protocol require new version and new untouched fixtures
AFTER recording this one's result; never overwrite the negative finding.
