# EEQ parity+ unified experimental protocol — G4 freeze v1

Frozen before main breadth/baseline/scaling experiments and before selection/implementation of the final unseen semantic family. Closing this gate is not a journal-strength assessment.

## 1. Unit and counting
A semantic case is uniquely identified by: family/environment, preregistered pre-action evidence/qualification state, registered action/action-prefix, registered future decision challenge/contract, and native action vocabulary.

Executions differing only by client/server version, machine, retry, seed or clean rerun are one semantic case with multiple robustness executions unless the version changes preregistered native semantics. The same semantic signature in different real environments counts once toward unique semantic cases but separately as environment replication.

Main breadth target: >=250 semantically deduplicated native cases before final holdout scoring.

## 2. Native oracle
Before method scoring each family freezes: native software/version/API, native action classes, raw observation used for the label, attribution rule, polling/retry rule, pre-exclusions, and source/environment provenance.

Only pre-outcome exclusions are allowed:
- PREEXCLUDED_NATIVE_SCHEMA_INVALID
- PREEXCLUDED_OUTSIDE_REGISTERED_CONTRACT
- PREEXCLUDED_UNAVAILABLE_REQUIRED_SOURCE

Rows remain in the ledger. Non-scored states also remain:
- NATIVE_ORACLE_AMBIGUOUS
- INFRASTRUCTURE_FAILURE
- SOURCE_UNAVAILABLE
- NATIVE_VERSION_UNSUPPORTED

## 3. Adapter interface: V0 + C1-C3
Adapters are constructed from documentation, signed/public configuration, native metadata and mechanism semantics, never from scored native decision labels.

**V0 lawful-information boundary**: all exposed fields are legitimately readable/retainable at decision time; no future/native outcome leakage.

**C1 support coverage**: enumerate all compatible support mechanisms within the registered native contract, preserving source identity/provenance where native semantics distinguishes support.

**C2 qualification fidelity**: expose predicates determining whether source/evidence is qualified for the registered claim; do not substitute authentication for authorization unless native semantics equates them.

**C3 transition/objective fidelity**: expose registered actions, action-conditioned successor evidence/qualification state, post-action observations, continuation/allowance predicates, and registered action vocabulary.

C1-C3 quantify over every reachable registered history. There is no separate A5.

Post-freeze change classes:
- ADAPTER_INSTANCE_EXTENSION: family vocabulary mapped into unchanged schema; allowed for development families.
- ADAPTER_SCHEMA_CHANGE: PROTOCOL_BREAK.
- CORE_SEMANTICS_CHANGE: PROTOCOL_BREAK.

## 4. Representation taxonomy
Every applicable representation gets an oracle-optimal deterministic decoder over exact representation-equivalence classes.

- B0 full lawfully available history oracle (upper bound)
- B1 current object/artifact only
- B2 authentication/cryptographic validity only
- B3 authority/authorization only
- B4 provenance/lineage only
- B5 authority + provenance
- B6 retained history without continuation contract
- B7 behavioral/predictive state only
- B8 static selected-information/reduct-inspired state
- B9 protocol-native hand-engineered sufficient state
- B10 EEQ/WFC

NOT_APPLICABLE requires preregistered structural justification.

## 5. Oracle-optimal decoder
For representation R, group cases by exact R(h). For class C and label y let n(C,y) be the number of cases.

best_det_accuracy(R) = sum_C max_y n(C,y) / N.

Report zero-error recoverability, mixed-class count, mixed-case count, label histogram per mixed class, and unordered conflict-pair count. For binary safety views report false accepts/rejects. For multiclass tasks preserve native classes and report full confusion matrix. Ties use lexicographic native-label order.

## 6. Frozen omission matrix
Evaluate wherever structurally applicable:
- O1 no source identity/provenance
- O2 no qualification
- O3 no claim binding
- O4 no continuation history
- O5 no continuation contract
- O6 static action model / suppress action-induced evidence-state change
- O7 one-step/myopic horizon
- O8 partial support coverage / omit one compatible support mechanism

Family-specific omissions may be added before that family's scoring; O1-O8 cannot be removed.

## 7. Negative controls
Each development family preregisters >=2 distinctions/perturbations predicted not to alter native action where structurally possible. A control must change real bytes/metadata/history while preserving the frozen decision-relevant qualification/continuation relation. Failure is retained as a mapping/semantics failure.

## 8. Common metrics
Decision: exact native match, zero-error recoverability, best deterministic baseline accuracy, mixed classes/cases, conflict pairs, FAR/FRR or multiclass confusion.

Representation cost: canonical serialized retained bytes, state cardinality, full-history compression ratio, optional characteristic/conflict graph diagnostics (classical, not novelty).

System cost: compile wall time, decision wall time, peak RSS, atoms/support edges/actions/reachable states, source-fetch/preprocessing time separately.

Downstream: at least one correction/audit continuation task per family where feasible; report exact legal path/action-set recovery and restricted-baseline failure.

## 9. Repetitions/timing
Do not pad deterministic semantics with meaningless repeats. Exhaust finite spaces when feasible. Native async services repeat only according to frozen polling/stability rules. Performance timing: >=5 warmups and >=30 measured operations when resolvable; otherwise batch and report per-operation median, IQR, p95. Version reruns are robustness, not new cases.

## 10. Robustness categories
Applicable families test preregistered perturbations from:
1 client/server version shift
2 stale prior evidence
3 missing noncritical metadata
4 missing decision-critical metadata
5 corrupted/invalid evidence
6 source unavailability
7 authority/key/actor rotation
8 contract tightening
9 contract loosening
10 asynchronous/stale observation or replay

Before native execution predict one: PRESERVE_DECISION / RECOMPILE_THEN_DECIDE / INSUFFICIENT_EVIDENCE_REFUSE.

## 11. Synthetic scaling
Independently vary |sources|, |claims|, |actions|, support/qualification density, |contracts| and horizon r. Exhaust small spaces against an independent oracle; larger spaces use published fixed seeds. Report compiler time, peak RSS, compiled states/edges, representation bytes and decision latency.

## 12. Evidence-class labels
Every environment is exactly one:
- PRODUCTION_HISTORY
- PUBLIC_MAINTAINED_CONFIG_NATIVE_REPLAY
- CONTROLLED_NATIVE
- SYNTHETIC

Never merge these into a single "production" count.

## 13. Final unseen fifth-family holdout
GitHub is ineligible because its semantics were inspected pre-G4.

After this freeze:
1. select a fifth family with legally usable public evidence, native oracle, and source/qualification/continuation relevance;
2. map only through unchanged V0+C1-C3;
3. freeze family adapter and predictions before native scoring;
4. any ADAPTER_SCHEMA_CHANGE or CORE_SEMANTICS_CHANGE => HOLDOUT_FAIL_CORE_CHANGE; family moves to development and another previously unopened family is required;
5. only zero core/schema changes counts as final holdout success.

## 14. Failure taxonomy
METHOD_MISMATCH; BASELINE_MIXED_CLASS; NATIVE_ORACLE_AMBIGUOUS; INFRASTRUCTURE_FAILURE; SOURCE_UNAVAILABLE; NATIVE_VERSION_UNSUPPORTED; PREEXCLUDED_NATIVE_SCHEMA_INVALID; PREEXCLUDED_OUTSIDE_REGISTERED_CONTRACT; PREEXCLUDED_UNAVAILABLE_REQUIRED_SOURCE; V0_VIOLATION; C1_COVERAGE_FAILURE; C2_QUALIFICATION_FAILURE; C3_TRANSITION_OBJECTIVE_FAILURE; PROTOCOL_BREAK_ADAPTER_SCHEMA; PROTOCOL_BREAK_CORE_SEMANTICS; HOLDOUT_FAIL_CORE_CHANGE.

## 15. Amendment rule
After the freeze commit, semantic changes to case definition, V0+C1-C3, core semantics, baseline taxonomy, omissions, scoring, metrics, failure taxonomy or holdout logic create a new protocol version and a PROTOCOL_BREAK ledger entry. Prior results stay attached to their original protocol version; no revision is applied retroactively to improve a score.

Journal-strength reassessment remains blocked until G1-G8 close.
