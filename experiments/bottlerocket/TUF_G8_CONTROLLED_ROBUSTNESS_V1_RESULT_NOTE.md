# TUF G8 prospective controlled native observations — 2026-10-08

Native reference run: 37743183698, SUCCESS.
Workflow commit: 45419f8fbc0439712dda99f0d6c2f13a83a39d30.
Artifact: 11535215610, tuf-g8-prospective-native-robustness.
Artifact ZIP SHA256:
68de71bcc36ca8ff853056ae8d63ea82e75b449a996cd4dd90cce300c47fc466.

Frozen TUF G8 scenario transformations and forecasts were committed before
the workflow/native call. Source Bottlerocket roots 1..4 were verified
against original inventory SHA256s. Native tuf-js@3.0.1 was pinned.
Every scenario started with independent root 1->2->3 trust setup.

## Outcome by frozen denominator

| Scenario | Native prediction | Native observation | Scored? | Context |
|---|---|---|---|---|
| R3 unsigned outer observation | ACCEPT | ACCEPT | YES | signed payload and signatures unchanged |
| R4 empty signed key map | none (diagnostic) | REJECT / UnsignedMetadataError | NO | predeclared unscored because native schema admissibility lacked independent certification |
| R5 signed version 4->5 without resigning | REJECT | REJECT / UnsignedMetadataError | YES | cannot uniquely attribute rejection to invalid signature versus sequence check |
| R10 root2 replay into trusted root3 | REJECT | REJECT / UnsignedMetadataError | YES | stale prior source |
| R6 absent root4 bytes | none | SOURCE_UNAVAILABLE; native NOT CALLED | NO | not a native REJECT |

Frozen scoreboard: 5 scenarios, 3 native-scored, 3/3 matched, zero observed
native prediction mismatches, two predeclared unscored. R4 remains unscored
even though the resulting call rejected: no post-outcome eligibility change.

## Scientific boundary

This is **native-oracle calibration evidence** on CONTROLLED_NATIVE
perturbations, NOT a score for the EEQ/WFC v1 or v2 method:
- Section 10 predicted method dispositions were predeclared (PRESERVE,
  RECOMPILE, REFUSE), but no EEQ adapter decision was scored here.
- The native exceptions do not independently identify all underlying
  cryptographic or policy causes.
- No missing source was imputed to a native reject.
- No native case was added to G5 and no previous sample was retroactively
  relabeled as prospective G8.
- The fifth-family X.509 and prospective in-toto sources were untouched.

G8 ten-category robustness, downstream native tasks and clean reproduction
all remain OPEN.