# Scientific repair ledger — 2026-09-30

## Claim architecture after bottom-up repair

The manuscript now separates four obligations instead of asking one benchmark to
support all of them:

| Obligation | Evidence | Result |
| --- | --- | --- |
| Information necessity | frozen EEQBench projections | restricted states lose decisions; exact contract information is one reference |
| Finite WFC realization | four separately implemented finite execution paths | 4,500/4,500 agreement on feasibility, value, and complete first-action sets |
| Bounded source construction | frozen raw-SQL compiler vs exhaustive native SQLite | 396/396 optimum, certificate, and source-semantic agreement |
| Native source-to-decision recovery | ordered-native and production-root reruns | 128/128 and 52/52 complete first-action-set recovery |

This is intentionally stronger than the pre-audit presentation: each claim is
paired with an execution boundary and oracle that actually tests that claim.

## Legacy 4,500-contract evidence

A direct audit found that the legacy labels `full-history-oracle`, `wfc-e`,
`factored-wfc`, `backend-given-wfc`, and
`wfc-minus-localization` shared the same exact `MethodView` on all 4,500
contracts. The frozen ledgers remain provenance, but these labels are not counted
as independent implementations.

The manuscript-bearing interpretation is an **information-projection sensitivity
study**. Exact contract information is evaluated once as a reference. Selected
projection results remain:

| Projection | Applicable | Selected-action agreement | Complete first-action-set agreement |
| --- | ---: | ---: | ---: |
| current-state observation | 4,500 | 3,060 | 2,988 |
| static value of information | 3,420 | 3,420 | 3,420 |
| exact contract information | 4,500 | 4,500 | 4,500 |

## Finite WFC realization

A new deterministic post-audit benchmark generates 4,500 explicit finite tasks
over the registered stress axes. Task records contain compatible atoms,
stage-indexed query signatures, legal action masks, immediate costs,
observation labels, successor atoms, and a finite horizon. They do not serialize
a value, optimal action, policy, or implementation label.

Four execution paths are compared:

1. full-support recursive policy enumeration;
2. explicit WFC-E query-cell/frontier construction plus support recursion;
3. an independently coded integer-bitset WFC recursion;
4. a generic minimax backend that receives only value-free compiled topology
   (supports, legal actions, costs, observations, successors).

The solver modules do not import one another. Fresh result:
**4,500/4,500 four-way agreement**, zero mismatches, **223 tied-optimum tasks**,
and **1,702 horizon-infeasible tasks**. This is deterministic implementation
validation, not a natural-system generalization experiment.

## Frozen raw-SQL source compiler

A separately frozen 22 September protocol was recovered byte-for-byte from the
prior reproduction package. Input consists of finite possible inputs, raw
`CREATE TABLE ... AS SELECT ...; DROP TABLE input;` programs in a declared
integer grammar, a registered historical claim, candidate pre-action snapshot
queries, and query costs. Inputs contain no correct preservation action,
preservation label, collision pair, decoder answer, or oracle value.

The compiler statically constructs cross-claim collision constraints and solves
the minimum-cost preservation problem. The independent oracle uses in-memory
SQLite execution and exhaustive search over all `2^7 = 128` candidate snapshot
subsets; it does not call the compiler parser/interpreter/conflict routine.

Fresh rerun:

- 396 contracts: 288 known-source + 108 source-ambiguous;
- 396/396 exhaustive-SQLite optimum agreement;
- 396/396 independently replayed sound certificates;
- 396/396 compiler/SQLite source-semantic agreement;
- 19,488 source-world executions;
- 162 zero-retention optima;
- 216 source-refinement checks with 0 violations;
- 12/12 adverse/unit tests pass.

This validates only the declared bounded SQL frontend and finite preservation
specialization.

## Native source-to-decision reruns

### Ordered native study

- 8 constructed source configurations;
- 392 executed native traces;
- 128 registered decision tasks;
- full construction: 128/128 value agreement;
- full construction: 128/128 complete optimal first-action-set agreement;
- full construction: 128/128 selected-plan native validity;
- late acquisition: 128/128 value agreement but only 116/128 complete
  first-action-set agreement;
- adversarial tests: 32/32 pass.

### Production-root study

- one pinned, production-authored Sigstore root history;
- 15 signed numbered root versions and 14 adjacent verified updates under an
  unmodified TUF implementation;
- 143 native traces and 52 registered consumer/cost tasks;
- full construction: 52/52 value and complete first-action-set agreement;
- late acquisition: 52/52 value agreement but only 13/52 complete
  first-action-set agreement;
- study tests: 40/40 pass.

These bounded studies show why value-only validation is insufficient: a
representation can preserve the optimum value while introducing unsupported
optimal first actions.

## Source-admission repair and selected-case coverage

The repaired SQL/Java admission gate covers the diagnosed alias,
control-flow, and indirect-write failures and passes 35/35 bounded regressions in
GitHub Actions. This remains a grammar-boundary repair, not a proof of arbitrary
source soundness or all A1-A5 correspondences.

The frozen repository selector retains five adjudicated-positive candidates.
With the conservative repaired adapter:

- `licensed-update`: 2;
- `unidentified`: 3;
- wrong positive emitted certificates: 0;
- focused runtime probes passed: 3;
- historical build-environment blocks: 2.

`unidentified` is abstention, not `withhold`. This track is reported as
admission coverage rather than population accuracy.

## Manuscript consequence

The first page now presents EEQ as an Information Sciences information-state
construction problem for sequential decision support. The frozen projection
study establishes information sensitivity; finite WFC realization establishes
algorithm identity on explicit contracts; raw-SQL/SQLite establishes bounded
source construction without answer labels; and R2/R3 establish bounded native
source-to-decision recovery.

Correct value or one selected policy is not treated as sufficient validation;
the complete optimal first-action set is checked explicitly.
