# Prospective v2 native-state liftability audit — freeze

Date: 2026-10-08

Goal: find whether the *existing frozen v1 adapter instances* already provide
the finite total action-successor graph that the quotient-v2 candidate needs.

This is a **read-only structural audit**, not native decision scoring.
Input immutable 285-case G6 adapter archives and GitHub v2 adapter archive
from the two pinned G6 matrix artifacts in
`experiments/g8_v1/G8_MEASUREMENT_FREEZE_20261008.md`.

Admission criteria for a direct native lift into finite quotient-v2:

1. Registered action alphabet is finite/nonempty.
2. Every action has an explicit deterministic next-state target **semantic ID**
   for every audited case, with closure inside the same registered domain.
3. Complete, lawful source/qualification/claim-binding predicates and the
   continuation contract are present before labels.
4. Unknown successor/source conditions lead to a refusal/unsupported
   disposition, never fabricated transitions.
5. Native outcome labels are never read to construct the graph.

No symbolic per-action attribute (e.g., 'restart=Always') may be silently
interpreted as a next-state ID. A failure says the **v2 extractor is missing**,
not that the frozen G4-v1 case or adapter is invalid.

Expected disposition: preserve whatever actual coverage emerges, including
`C3_TOTAL_GRAPH_NOT_AVAILABLE` or missing source bindings. Do not relax
criteria after seeing the count.
