# EEQ/WFC v2 research freeze: lawful action-conditioned quotient

Status: ALTERNATIVE OPERATOR RESEARCH, protocol-v2 candidate; NOT an amendment to G4.
Frozen parent: G4 at c15b212ad0c2be3856a03d38802aaffa628aefd1.
Research branch: eeq-wfc-v2-quotient-research-20261008.
Evaluation evidence class: SYNTHETIC unless separately qualified by a native oracle.

## Scientific defect in v1 motivating this branch

The frozen v1 compiler copies ordered claim-support, qualification and
transition/continuation frontiers into canonical JSON. Canonicalization alone
does not compute a contract-relative sufficient quotient: the six development
domains produced 285 classes for 285 semantic cases. In GitHub v2, all nine
cases have distinct B10 representations, B10 is on average larger than B0,
and every omission/baseline preserves native-label accuracy. The v1 label
leakage audits establish lawful construction, not necessity, compression or
minimality.

This branch retains all v1 results and treats the following as an independent
hypothesis, subject to disproof.

## Candidate primitive

A complete, finite, documented native-system abstraction consists of:
- states S containing lawful source, qualification and claim-binding data;
- a registered, ordered action alphabet A;
- a total deterministic action successor function delta: S x A -> S;
- a finite family of continuation/audit contracts J;
- an observation function O_J(s) computed from visible qualified support and
  contract requirements, never from scored native labels.

An observed claim yields ALLOW, DENY or REFUSE. REFUSE is mandatory when
required support/qualification facts are unavailable; it is not DENY.
A contract may additionally demand the qualified supporting source identities
as an audit output, making provenance distinctions claim-relative.

For a fixed horizon r, define:

Q_0(s) := O_J(s)
Q_(k+1)(s) := ( O_J(s), [ class_k(delta(s,a)) for a in ordered A ] )

where class_k is the canonical quotient-class ID at depth k. Only complete
lawful registered states are admitted. Absent transition/contract/source
coverage causes an explicit refusal or failure; missing predicates are never
silently imputed.

The finite-horizon observation equivalence is:
s ~_(J,r) t iff O_J(delta*(s,w)) = O_J(delta*(t,w))
for every action word w of length <= r.

The output is layered: after one action the remaining legal horizon is r-1.
A depth-r class is NOT claimed to support arbitrary unbounded updates.

## Precisely limited correctness claim

Under complete finite deterministic transition and observable-contract
assumptions, class_r(s) = class_r(t) iff s ~_(J,r) t. Proof: induction on r.
Therefore the quotient has the fewest distinguishable states among exact
deterministic encodings preserving all those bounded future observations.
This is a standard finite-state/Moore-style partition-refinement principle,
NOT an invented minimization theorem and NOT a minimum-bit encoding claim.

The candidate research contribution is the lawful construction of O_J from
C1 support/source identity, C2 qualification and claim binding, and C3
action-conditioned continuation, with explicit epistemic refusal and
claim-relative provenance obligations. It requires separate empirical
evidence that this object is useful and not merely renamed automata theory.

## Research falsifiers

1. A pair merged by Q_r differs for some registered action word length <= r.
2. A pair split by Q_r has identical independent oracle traces to r.
3. A legal action is not representable at the appropriate remaining horizon.
4. Differentially unknown/qualified support is coerced into false.
5. Dropping provenance changes an audit contract result without splitting.
6. A scorer/native label changes a compiled quotient or its certificates.
7. Total encoding cost (class IDs plus shared quotient table) or compile/RSS
   costs erase all benefit under realistic reuse; report such losses.
8. Current-only and hand-engineered baselines match or outperform the method;
   preserve those results instead of claiming superiority.
9. The experiment needs changed frozen G4 case/scoring semantics to succeed.

## Required pre-declared tests

- Tiny constructive witness: equal current decisions, unequal safe future actions.
- Irrelevant byte/provenance perturbations under non-audit contract must merge.
- A provenance-audit contract must split source-distinct explanations.
- Unavailable decision-critical qualification must yield REFUSE.
- Independent brute-force action-word oracle on small finite spaces.
- Shortest distinguishing action-word certificate and exact layer transitions.
- Native-label poison/permutation invariance (compiler never sees native labels).
- Synthetic six-axis variation: sources, claims, actions, support density,
  contracts and horizon; fixed published seeds and axis-isolated changes.
- Compiler time with >=5 warmups and >=30 measured calls where possible.
- Peak RSS, compiled class count, serialized full state bytes, quotient-table
  bytes, per-state code bytes, and amortized total state bytes.
- Separate source-fetch/adapter-construction cost when eventually integrated.
- Downstream exact legal action-set and bounded correction-path recovery.
- Reject incomplete C1/C2/C3, missing actions and missing transitions.

Synthetic studies NEVER count toward the G5 native-case threshold.
This operator is not substituted for G4 B10 or retrospectively scored on the
X.509 and prospective in-toto holdout families. An actual cross-family
replacement requires a new protocol version and fresh, previously unopened
testing after freezing all new operator choices.

## Current stage

Design freeze only. No v2 scientific success claimed until independent
tests/CI/artifacts have been executed and inspected.