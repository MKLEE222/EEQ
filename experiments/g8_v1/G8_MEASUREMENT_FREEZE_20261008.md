# G8-v1 measurement expansion — pre-run audit plan

Date: 2026-10-08

**Development diagnostics only.** Do not change G4-v1 compiler, G5/G6
denominators, historic scores or either X.509/in-toto holdout.

## D1 — dominance / non-vacuity audit

Use exactly these previously frozen, immutable artifacts:

1. 285-case final G6 run `37577515052`, artifact `11463213360`,
   ZIP SHA256
   `90f6b9562aa7e76caf1f8c252cf5483dbcca4729b61687a8805a3cd105c81d85`.
2. GitHub v2 nine-case G6 run `37650255613`, artifact `11495203512`,
   ZIP SHA256
   `381225c9c54153c4950af6f5ba1d60e655cbdb54dfdc53ff23c848a8393f059b`.

Compute for each domain:
- B10 unique classes / N: exact-class injectivity;
- matched applicable B0-B9 and O1-O8 with no worse accuracy and
  lower/equal canonical bytes than B10 (sample-specific dominance);
- number of omissions which actually lose decision discrimination;
- B10 bytes / B0 bytes (only within domain with applicable B0);
- if B10 and every omission are perfect, mark lack of identifiability as
  `NONDIAGNOSTIC_ABLATIONS`, not "proof that omission mechanisms are needed".

No new baseline definitions, no label tuning, no unearned KBS-strength claim.

## D2 — six-axis synthetic compiler cost scaling

Run frozen `compile_wfc_v1.py` unchanged, from Git blob
`9a6bff7a2b8db73b86b6952c706852c92b1a4b1d`.

Create synthetic adapter instances under **eeq-adapter-v1** and independently
vary one factor at a time, fixing the others:

| Axis | Frozen levels | Fixed defaults |
|---|---|---|
| sources | 2, 4, 8, 16, 32 | 8 |
| claims | 1, 2, 4, 8 | 2 |
| actions | 1, 2, 4, 8 | 2 |
| support/qualification density | 0.2, 0.5, 0.8, 1.0 | 0.5 |
| continuation contracts | 1, 2, 4, 8 | 2 |
| successor horizon | 1, 2, 4, 8 | 2 |

Fixed synthetic seed `4108`; no native labels. Each setting:
- 5 warmups, 30 measured `compile_wfc` calls;
- report median/IQR/p95 wall time, process max RSS, traced peak Python
  allocations, canonical serialized output bytes, atom/edge/action counts;
- synthetic generation/preprocessing measured separately, no network fetch;
- direct independent reference compiler for the small-space cases, checking
  canonical output equivalence;
- note that synthesis does **not** provide an independent native-action
  oracle. This closes only the G8 compiler-cost diagnostic, not all G8.

Any failure or poor scaling is retained; no levels are dropped after
observing runtime.

## D3 — downstream correction/audit feasibility

Separately evaluate a declared synthetic finite-state correction task under
the v2 research contract; independently enumerate legal repair action paths.
Compare recovered legal paths using exact quotient vs a current-state-only
ablation. Do not count this as per-native-family downstream G8 evidence.

## G8 status rule

D1/D2/D3 passing never permits `G8 PASS` on its own. The original protocol
also requires applicable 10-category native robustness, per-family
correction/audit where feasible, and clean expanded-suite reproduction.
No old unseen family may be used to tune v2.
