# Quotient v2 — ten-category robustness kill grid (synthetic development)

Date: 2026-10-08
Status: **pre-execution registered v2 scenarios**.

Scope: `experiments/quotient_v2/test_finite_contract_quotient_v2.py::fixture`,
starting state `A`, contract `contractA`, decision action `inspect`.
The unperturbed state is ACCEPT.

For authority rotation scenarios only, the baseline contract additionally
restricts support to sourceA. This is frozen before executing the perturbation.

| G4 category | Perturbation | Pre-declared response | Expected after-state |
|---|---|---|---|
| 1 client/server version shift | change only decorative version metadata | PRESERVE_DECISION | ACCEPT |
| 2 stale prior evidence | revoke A's qualified flag | RECOMPILE_THEN_DECIDE | REJECT |
| 3 missing noncritical metadata | remove A's decorative annotation | PRESERVE_DECISION | ACCEPT |
| 4 missing decision-critical metadata | set A authorization predicate to unknown | INSUFFICIENT_EVIDENCE_REFUSE | REFUSE |
| 5 corrupted/invalid evidence | set A authentication predicate false | RECOMPILE_THEN_DECIDE | REJECT |
| 6 source unavailability | remove A support + inventory incomplete | INSUFFICIENT_EVIDENCE_REFUSE | REFUSE |
| 7 authority/key/actor rotation | change A sourceA to unauthorized sourceB under sourceA-restricted contract | RECOMPILE_THEN_DECIDE | REJECT |
| 8 contract tightening | raise qualified-source threshold from 1 to 2 | RECOMPILE_THEN_DECIDE | REJECT |
| 9 contract loosening | relative to threshold-2 baseline, lower to 1 | RECOMPILE_THEN_DECIDE | ACCEPT |
| 10 async/stale/replay observation | quarantine A's qualification as unknown | INSUFFICIENT_EVIDENCE_REFUSE | REFUSE |

Acceptance:
1. All before/after decisions are independently recalculated by the direct
   trace oracle (not read from adapter/native labels).
2. Recompiled quotient agrees with exhaustive trace oracle at horizon 1.
3. No scenario is silently replaced after result observation.
4. Every category emits a status and a logical response classification;
   model limitations and ambiguous predictions remain visible.
5. This is a **SYNTHETIC stress study**, not completion of the original G8
   cross-family native robustness obligation.

No previous holdout (X.509 or in-toto) is used for scenario selection.
