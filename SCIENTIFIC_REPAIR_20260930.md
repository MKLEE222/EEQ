# Scientific repair ledger — 2026-09-30

## Legacy 4,500-contract evidence

A direct audit of the frozen runner found that the labels
`full-history-oracle`, `wfc-e`, `factored-wfc`,
`backend-given-wfc`, and `wfc-minus-localization` shared the same exact
`MethodView` on all 4,500 contracts.

Revised interpretation:

- the frozen ledgers remain provenance;
- the legacy exact labels are not independent algorithm implementations;
- the 4,500 contracts are used as an information-projection sensitivity study;
- exact contract information is evaluated once as a reference.

Fresh deterministic projection replay reproduces the checked ledgers. Selected
results:

| Projection | Applicable | Selected-action agreement | Complete first-action-set agreement |
| --- | ---: | ---: | ---: |
| current-state observation | 4,500 | 3,060 | 2,988 |
| static value of information | 3,420 | 3,420 | 3,420 |
| exact contract information | 4,500 | 4,500 | 4,500 |

The exact row is a reference, not a separately implemented source-to-state
algorithm.

## Fresh construction validation

### Ordered native study

- 8 constructed source configurations
- 392 executed native traces
- 128 registered decision tasks
- full construction: 128/128 value agreement
- full construction: 128/128 complete optimal first-action-set agreement
- full construction: 128/128 selected-plan native validity
- late acquisition: 128/128 value agreement
- late acquisition: 116/128 complete optimal first-action-set agreement
- adversarial tests: 32/32 pass

### Production-root study

- one pinned, production-authored Sigstore root history
- 15 signed numbered root versions
- 14 adjacent verified updates under an unmodified TUF implementation
- 143 native traces
- 52 registered consumer/cost tasks
- full construction: 52/52 value and complete first-action-set agreement
- late acquisition: 52/52 value agreement
- late acquisition: 13/52 complete first-action-set agreement
- study tests: 40/40 pass

These studies are the manuscript's construction-to-decision validation. They are
bounded studies, not deployment-prevalence estimates.

## Source-admission repair

The repair gate covers the diagnosed SQL and Java acceptance-boundary failures,
including alias arithmetic, swapped aliases, dead migration branches, indirect
helper writes, ambiguous/unresolved calls, recursion, and shadowing.

The public GitHub Actions gate passes 35/35 tests. This is a bounded grammar
repair, not a proof of arbitrary SQL/Java source soundness or of all A1-A5 source
correspondences.

## Prospective selected-case replay

The frozen selector retains five candidate episodes across two of four fixed
repository histories. The independent source/route adjudicator supports the
registered licensing relation in all five.

With the repaired conservative source-admission implementation:

- `licensed-update`: 2
- `unidentified`: 3
- wrong positive emitted certificates: 0
- focused runtime probes passed: 3
- historical build-environment blocks: 2

`unidentified` is conservative abstention, not `withhold`. The revised
manuscript reports this as an admission-coverage result, not a population
accuracy result.

## Manuscript consequence

The first page now states the article's Information Sciences-facing object
directly: an information-state construction problem for sequential decision
support when intervention changes evidence qualification and future corrective
opportunity.

The paper separates:

1. formal finite sufficiency and conditional WFC construction;
2. controlled information-projection sensitivity;
3. bounded native source-to-decision construction validation;
4. conservative source-admission coverage and independent adjudication.

Correct value or one selected policy is not treated as sufficient validation;
the complete optimal first-action set is checked explicitly.
