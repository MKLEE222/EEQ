# APT exhaustive G6 representation mapping — frozen before baseline scoring

Parent protocol: G4 commit `c15b212ad0c2be3856a03d38802aaffa628aefd1`.

Native carrier: the frozen APT 3.0.3 exhaustive carrier.
Scored baseline denominator: the **144 core semantic templates**, one representative
per template. The four Suite/Version variants remain negative-control executions and
must not inflate the representation denominator.

The builder may read native actions only after this mapping is committed.

## Native semantic inputs

- source/signature lineage: signer A or B;
- configured qualification: whether the current InRelease is accepted by the
  configured Signed-By binding;
- protected continuation distinctions: changes to Origin, Label, Codename;
- continuation contract: global release-info allowance or the subset of
  field-specific allowances;
- Suite and Version: frozen zero-effect controls for this decision contract.

## B0-B10

B0 full history oracle:
- signer lineage;
- qualification;
- fixed pre-update metadata and current metadata;
- exact continuation contract.
This is the lawful upper-bound representation.

B1 current artifact only:
- current signer lineage;
- current Origin/Label/Codename values;
- no pre-update history and no continuation contract.

B2 authentication/cryptographic validity only:
- signature acceptance under the configured Signed-By trust boundary.
In this APT carrier the native trust configuration makes this coincide with
the binary qualification predicate. We retain the baseline even though it
collapses to B3 here.

B3 authority/authorization only:
- configured qualification predicate only.

B4 provenance/lineage only:
- signer lineage A/B only.

B5 authority + provenance:
- signer lineage plus qualification.

B6 retained history without continuation contract:
- signer lineage, qualification, and exact protected-change vector;
- continuation allowance contract removed.

B7 behavioral/predictive state:
- NOT_APPLICABLE.
The finite carrier defines no independent behavioral predictor or learned
state. Inventing one after seeing the carrier would not be a legitimate
baseline.

B8 static selected-information/reduct-inspired state:
- qualification plus the exact protected-change vector;
- fixed independently of the per-case continuation contract.
For this family B8 intentionally resembles B6 minus raw lineage; generic
baseline names need not produce distinct states in every family.

B9 protocol-native hand-engineered sufficient state:
- exact frozen native-decoder inputs:
  qualification, protected-change vector, allow-global, allow-fields.

B10 EEQ/WFC:
- signer lineage;
- qualification;
- compiled unresolved continuation obligations:
  the set of changed protected fields not discharged by the registered
  continuation contract.
This compilation is computed from semantic inputs, never from native labels.

## O1-O8

O1 no source identity/provenance:
- B10 without signer lineage; qualification and compiled obligations remain.
A zero effect is allowed and would mean raw identity is redundant after lawful
qualification compilation for this carrier.

O2 no qualification:
- B10 without the qualification bit while retaining signer provenance and
  compiled obligations.
Because signer and qualification are one-to-one in this controlled carrier,
O2 may be empirically non-identifying here; that limitation must be reported,
not repaired post hoc.

O3 no claim binding:
- retain qualification, number of protected fields changed, allow-global, and
  number of field-specific allowances, but erase which allowance belongs to
  which protected claim.

O4 no continuation history:
- signer lineage, qualification, and continuation contract;
- protected-change history removed.

O5 no continuation contract:
- signer lineage, qualification, and protected-change history;
- continuation allowances removed.

O6 static action model:
- NOT_APPLICABLE to this one registered update action; there is no alternate
  action-conditioned successor model in the exhaustive APT carrier.

O7 one-step/myopic:
- NOT_APPLICABLE because the registered APT carrier itself has a one-transition
  horizon. A fabricated longer horizon would change the frozen case contract.

O8 partial support coverage:
- NOT_APPLICABLE: this carrier has one configured Signed-By support binding,
  not multiple compatible support mechanisms from which one can be omitted.

## Negative controls

Suite changed/unchanged and Version changed/unchanged remain the two frozen
zero-effect distinctions. For each of the 144 core templates, all four native
variants must agree before that template is admitted to the 144-case baseline
ledger.

## Scoring

All applicable representations use the frozen common oracle-optimal
deterministic decoder. Native multiclass labels are preserved:
REJECT_AUTH / BLOCK_CONFIRM / ACCEPT.

No representation mapping may be changed in response to baseline scores.
