# EEQ Quotient-Frontier v2: development-only mechanism candidate

Date: 2026-10-08

Branch: `kbs-parityplus-quotient-v2-g8-20261008`.
Parent: `5392d76d19cd5cd75d7aedd3f6080ac81d542cd6`.

**Status: NEW CANDIDATE / NOT G4-v1-COMPATIBLE / NOT SCORED ON A HOLDOUT.**

This is NOT an amendment to the frozen G4 protocol at
`c15b212ad0c2be3856a03d38802aaffa628aefd1`. Do not replace
`compile_wfc_v1.py`, its existing adapter emitters, case ledgers, or scores.

## Scientific failure pressure from v1

Frozen v1 emits a canonical qualified-support/transition *frontier*, but
does not actually quotient decision-equivalent states. In the G6 285-case
matrix each B10 class is a singleton, so zero mixed classes alone do not show
compression. In the Github-v2 nine-case matrix B10 also makes nine classes;
B10's mean serialized size (5199.33 B) exceeds B0's (3857.33 B), while all
O1-O8 retain 1.0 oracle-optimal accuracy on that carrier.

Therefore 'zero errors' is not an adequate v2 success criterion. The research
target is contract-relative distinction necessity, including lawful merges
*and* independently checkable separation witnesses.

## Finite-state research object (explicitly restricted)

Let a finite, deterministic registered evidence-state machine be
`M=(S,A,T,E,C)`, where:

- `S` consists of lawfully observed source/qualification/binding states;
- `A` is the complete registered action alphabet;
- `T:S x A -> S` is the **declared**, total, deterministic action-conditioned
  evidence-state successor model; it is *not learned from native outcomes*;
- `E(s,c,a) in {ACCEPT,REJECT,REFUSE}` is a decision for claim/contract `c`
  computed from declared, monotone threshold support semantics;
- `C` is the registered family of future decision challenges.

The explicit REFUSE outcome separates lack of qualification evidence from
evidence that qualification is false. Missing/unreadable support is not
silently imputed as false.

This is initially a **finite-state theorem/experiment**, not a claim that
arbitrary native histories can be automatically abstracted into a complete
finite model. Native-family extraction and C1-C3 closure remain open work.

### Future equivalence at depth r

At depth `r >= 0`, two states are equivalent when *every* registered
sequence of up to r transitions leads to the same complete vector of
registered claim/action decisions:

```
s ≡_(C,r) t
iff for every u in A^{<=r} and (c,a) in C x A,
    E(T*(s,u), c, a) = E(T*(t,u), c, a).
```

The compiled operator uses a Moore-style partition refinement:

- `P_0(s) = [(c,a,E(s,c,a))]_(c,a)`;
- `P_(k+1)(s) = (P_0(s), [(a, [T(s,a)]_(P_k))]_(a))`.

Equal `P_r` implies and is implied by the stated finite-horizon equivalence.
The coarsest legal quotient for this **specified observation family and
horizon** is exactly the set of its equivalence classes.

This fact and the partition-refinement technique are standard automata
theory, **not claimed as a novel algorithmic primitive**. The candidate
scientific contribution is claim-qualified evidence semantics, lawful
V0+C1-C3 instantiation, REFUSE boundary, contract-relative quotienting,
separation certificates, and empirical downstream benefit.

### Separation witnesses

For each non-equivalent pair (small-space audit only), produce an action
sequence of length <=r, a claim and a decision action whose observed decisions
differ. Witnesses must be verified by an independently implemented direct
trace oracle. A missing witness for unequal classes is a correctness failure.

### Legal compression conditions

For a proposed abstraction `q:S->Q`, compression is legal for depth r iff
no two states in one q-class have different registered decision traces of
length <=r. In the stable/unbounded case, output agreement and
action-successor congruence give the usual bisimulation-style test.

This is a model-relative iff, **not** global minimum-bit coding, and not
native-domain completeness without a lawful, closed source inventory.

## Anti-leakage and failure conditions

- No native outcome labels, post-hoc labels or old holdout case data may enter
  the operator or its synthetic generator.
- No scientific conclusion from a synthetic oracle is presented as native
  parity.
- Native C1 coverage is independently audited; synthetic full inventories are
  not a surrogate for public GitHub permissions.
- A frozen v1 fifth-family result (X.509) and the already selected in-toto
  family are **off-limits as v2 tuning or evaluation data**.
- Operator-v2 is a new core-semantics candidate. Under G4-v1 it would be a
  `PROTOCOL_BREAK_CORE_SEMANTICS`; any native v2 evaluation therefore needs
  a new protocol version with new preregistration and a *fresh unopened*
  transfer family.

## Pre-registered kill tests

1. **Independent exhaustiveness**: for small finite models, compare the
   partition against direct enumeration of every action trace <=r.
2. **Minimality**: each pair of distinct quotient classes has a checked
   separating trace; every merged pair has none.
3. **Horizon sensitivity**: states equal now but diverging after a registered
   action merge at r=0 and separate at r>=1.
4. **Evidence vs qualification**: authenticated-but-unauthorized evidence
   cannot count as qualified; unknown evidence must REFUSE when material.
5. **Invariance**: irrelevant cosmetic metadata changes do not split classes.
6. **Contract tightening/loosening**: recompute decisions/quotient; do not
   reuse stale proof certificates across changed contracts.
7. **No trivial compression claim**: report number of distinct quotient
   states, representation bytes INCLUDING codebook/table amortization, and
   source acquisition time separately; do not compare a free class ID against
   paid full-history evidence.
8. **Moore baseline**: compare exact quotient output against conventional
   deterministic partition refinement; if all advantage vanishes, no novelty
   is claimed for the underlying minimizer.
9. **Formal model limit**: if a native adapter cannot enumerate admissible
   actions/successors/qualification predicates without future labels, mark it
   `C1/C3_UNSUPPORTED`, not a success.
10. **Scalability**: vary sources/claims/actions/density/contracts/horizon
    independently with fixed seeds and report median/IQR/p95 over 5 warmups
    and 30 measured calls where measurable, peak memory and codebook bytes.

## Workstream separation

- **A, original parity+ v1:** existing G4 unchanged; remedy gate-document
  contradictions; continue G8 robustness, synthetic scaling, downstream
  correction/audit and clean reproduction without touching G7 outcomes.
- **B, v2 research:** finite contract quotient, independent oracle,
  counterfactual tests, witness certificates, baseline cost tradeoffs, then
  native-instance feasibility; re-freeze before any new native score.
- **C, manuscript:** do not claim minimized evidence states, general
  state-space inference, or KBS strength until workstream B has native evidence
  and A meets the original completion line.

## Required disposition

`RETAIN_V1_ONLY`, `V2_FINITE_ONLY`, `V2_ADVANCE_TO_NATIVE_PROSPECTIVE`,
or `V2_REJECT`, determined by the registered kill tests, not by whether a
workflow completed green.
