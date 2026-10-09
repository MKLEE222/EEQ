# R3 read-only cross-family evidence audit — actual result

Date: 2026-10-09
Status: **ARCHIVAL_AUDIT_PASS / COMMON_NATIVE_COMPILER_NOT ESTABLISHED**.
This is not a G4 protocol update, a new prospective transfer score,
a new native result, or an independently verified algorithm improvement.

## Frozen proof inputs and reproducibility

Source/prescore and native artifact IDs/hashes are recorded in
`00_COMMON_WITNESS_ARCHIVE_FREEZE.md` prior to this run.

Read-only Actions `37902762730`, commit
`4dacf865da7e97a4024120a602715dbcf045521d`.
Artifact `11602633432`, outer ZIP SHA256
`6b43af416a7ba8d3a0d510a23df1225e4fa36e2b40ee4154660d2de6e7296f79`.

CI hash-verified **all four** pinned source/native archives, including both
source-only predictions' inner SHA256. Ran 12/12 synthetic anti-masking tests,
then read-only checked the original R2-A and R2-B native joined result JSON.
No Kubernetes cluster, tuf-js native oracle or old predictor was reexecuted.

## Reconciled evidence

| Aspect | Kubernetes R2-A | TUF R2-B |
|---|---|---|
| Native evidence | 2 isolated controlled clusters | Controlled Ed25519 signed root + targets |
| Native scored decisions | 8/8 frozen admission rows | 28/28 frozen root-update rows |
| Native source effects | 2/2 actual binding mutations | 4/4 targets-role authorization checks |
| Counterfactual | CURRENT same; after binding patch future differs | Signed authority genuinely differs; root-update futures equal |
| Distinction necessity | positive controlled A witness | positive controlled B witness |
| B9 effect | can retain source/label/patch and predict equally | can project root role/threshold and merge equally |
| New EEQ advantage | NOT demonstrated | NOT demonstrated |

A: source namespace label gate vs standby affects native admission only
AFTER registered binding selector mutation. Witness: patch
`namespaceSelector never->gate`, then create flux service-account Pod.

B: two valid signed TUF authorities differ in qualified targets-role
signers, 4/4 independently confirmed; root-update-only full registered
horizon 2 equivalence holds at 7 prefixes/anchor, 28/28 native challenges.

Both outcomes come from distinct-domain source-only mechanisms and
separately scored native systems. Neither is a valid new unseen family
for the new operator, and one does not substitute for the other's missing
per-family contrast.

## Core blocker after this verified progress

The source-to-decision interpreters remain domain-specific: TUF RSA/Ed25519
qualified signer and version handling versus Kubernetes CEL selector/binding
mutation. Merely normalizing their completed decisions into a common JSON
envelope is not a novel, domain-independent compiler.

Next: a **label-blind, generic source/contract/certificate** interface
that derives testable predictions from registered qualified source atoms
under explicit native source boundaries. Domain-specific qualification
oracles cannot be smuggled in as already decided ACCEPT/REJECT labels.

If a fully informed expert B9 and an exact classical quotient reproduce
the same certified consequences at equal or better full end-to-end cost,
report B9_TIE/NO_INDEPENDENT_VALUE and stop claiming operator novelty.

## Unchanged gates

R0 charter frozen; R1 TUF restricted 56/56 native; R2 A and B
controlled phenotypes separately supported; R2 original per-family
completeness and missing-source refusal OPEN; R3 common compiler
NOT DEMONSTRATED; R4 independence vs B9/classical quotient NOT SHOWN;
R5 new unseen family UNOPENED.

Original G4-v1, 285-case G5, X.509 and selected in-toto remain unchanged.
Main branch was not written.
