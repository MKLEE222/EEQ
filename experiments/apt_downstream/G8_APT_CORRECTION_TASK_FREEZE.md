# G8 APT retrospective native counterfactual correction/audit task — freeze

Date: 2026-10-08. Parent G4 protocol Sections 8 and 12:
c15b212ad0c2be3856a03d38802aaffa628aefd1.

Status: POST-NATIVE / PRE-DOWNSTREAM-SCORING DEVELOPMENT FREEZE.
No prospective holdout claim. No further apt-get native run is needed.

## Frozen native evidence and representations

APT exhaustive aggregate:
Actions artifact 11324225958, ZIP SHA256
177fc73578c602834d19d3842a5fb8b6cf9f46155e7d4007a45bb8a1611ff966.
It contains 576 source executions: 144 semantic templates x four
Suite/Version zero-control variants.

Frozen final development matrix:
Actions artifact 11463213360, ZIP SHA256
90f6b9562aa7e76caf1f8c252cf5483dbcca4729b61687a8805a3cd105c81d85.
Use G6_FINAL_285_REPRESENTATIONS.json and only its APT domain rows;
B0-B10/O1-O8 mappings must remain byte-identical to the frozen artifact.

## Frozen task object

Each APT semantic source state has:
- qualified signer flag Q;
- protected metadata changed flags for Origin/Label/Codename;
- registered allowance contract: global override flag G plus allowed fields F.

This finite carrier contains all 9 allowed configurations
(no global+any subset of three protected fields, or global true), for each
of 16 fixed (Q, changed-field-mask) source states.

Registered contract-edit actions (not native accept/reject classes):
- ADD_ALLOW_ORIGIN;
- ADD_ALLOW_LABEL;
- ADD_ALLOW_CODENAME;
- SET_ALLOW_GLOBAL.

An action is available only if it changes the allowance contract, does not
alter Q or protected metadata changes, and does not undo other already
allowed fields. SET_ALLOW_GLOBAL moves to the unique global-true profile.
All actions are semantic edits to the registered allowance contract, not
changes to cryptographic trust; changing Q is deliberately forbidden.

The successor is looked up from the EXACT frozen nine-profile native oracle
grid for the same Q and changed-field-mask; it must exist and be unique.
No successor native outcome may be guessed from an EEQ representation.

## Downstream native-output tasks

Task 1: exact SAFE NEXT ACTION SET = all currently available edits whose
native successor action equals ACCEPT. Report this full set, not an easier
single binary success label.

Task 2: all SHORTEST CORRECTION ACTION SEQUENCES (length <=3 edits) that lead
to native ACCEPT. A currently accepted state has one empty correction word.
If signer qualification is false, changing allowance cannot fix auth:
return no legal correction sequence. The same native grid must prove this,
not a hard-coded label assumption.

Task 3: LEAST-PRIVILEGE CORRECTION, restricted to field-specific
ADD_ALLOW_* actions (never SET_ALLOW_GLOBAL). Return the set of shortest
field-addition subsets that lead to native ACCEPT, with all order
permutations canonicalized to the same subset. This prevents a trivial
global-override action from replacing an actual minimum-permission task.
No correction of trust qualification is permitted.

## Scoring and constraints

Join APT G6 representation rows to aggregate semantic states by
(Q, Origin/Label/Codename changed mask, G, canonical allowed-field set).
Never use scored native outcome or APT case_id to construct representation
equivalence. If any join or successor is missing/ambiguous, FAIL the study.

For EACH frozen B0-B10/O1-O8 representation wherever applicable:
- partition semantic states by exact canonical representation bytes;
- use an oracle-optimal deterministic exact-output decoder for the entire
  SAFE NEXT ACTION SET, and separately for all shortest correction words;
- report mixed classes, conflict pairs, exact-set recovery fraction,
  representation bytes and structural N/A reasons;
- report B0, B1, B8, B9, B10 even if B9 ties or beats B10.

This is finite-grid, within-carrier oracle-optimal recoverability, NOT
independently learned out-of-sample generalization. Results must not be
substituted for G4 single-label scoring or credited to G5.

Primary falsifiers:
- B10 merges states with different lawful next-action sets or correction paths;
- B9/current-only recovers all tasks equally, removing incremental novelty;
- any correction path passes through a missing/invented native case;
- unauthorized source qualification is repaired merely by an allowance edit;
- supposedly irrelevant Suite/Version replication changes downstream results;
- any score excludes a hard case only after observing the output.

No frozen G4 blob, original B10, X.509 or in-toto evidence may change.