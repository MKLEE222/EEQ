# Quotient-v2 prior-art and novelty veto — cold-start note

Date: 2026-10-08

## Prior art that must NOT be claimed as new

1. Paige and Tarjan, *Three Partition Refinement Algorithms*,
   SIAM Journal on Computing 16(6), 973-989 (1987):
   https://doi.org/10.1137/0216062.
   Coarsest partition refinement is classical. The Python refinement loop in
   `finite_contract_quotient_v2.py` is an intentionally simple baseline
   implementation, not a new asymptotically efficient algorithm.
2. Classical Myhill-Nerode distinguishability and automaton minimization.
   Equality of future observations as a criterion for merging states is not
   novel. The finite-horizon equivalence used here is a straightforward
   contract-labelled specialization, not a novel minimization theorem.
3. Three-valued abstraction/refinement and may/must semantics have extensive
   prior art. Example: *Generalized abstraction-refinement for game-based CTL
   lifted model checking* (2020), TCS:
   https://www.sciencedirect.com/science/article/pii/S0304397520303522.
   The existence of an UNKNOWN/REFUSE third value cannot be claimed novel.

## Candidate contribution that remains to be proven

- A **lawful, claim-relative evidence compiler** from real source
  qualification, source/claim bindings and action-conditioned continuation to
  a quotient over specified future claims.
- A certificate-producing soundness boundary: if source support is partial,
  the representation must explicitly limit the claims that can still be made.
- A contract-specific distinction-preservation test that succeeds on real
  native systems beyond hand-authored adapters and requires neither the
  native outcome label nor a manually selected state key.
- Measurable improvement in legal downstream correction/audit path recovery
  and *fully charged* representation costs, relative to B0-B9, O1-O8,
  traditional partition refinement and hand-engineered native states.

## Evidence still missing

The current v2 implementation assumes that a lawful finite transition system
and monotone threshold contract have already been specified. It does **not**
infer complete C1 support graphs or C3 successor relation from open-ended
native code. It is therefore not yet a cross-family method.

A valid prospective experiment must:
1. freeze a native-specific V0/C1/C2/C3 *input compiler* before outcomes;
2. test against at least one realistic source-availability/refusal case and
   one action-induced distinction that affects native continuation;
3. show a nontrivial quotient (classes < semantic states), zero mixed classes,
   and a discriminative baseline omission under native action variation;
4. charge codebook, evidence acquisition, preprocessing, and decision cost;
5. run on a genuinely untouched transfer family after a v2 protocol freeze.
   The already seen X.509 and selected in-toto families are not valid v2
   unseen holdouts.

If none of these conditions can be met, disposition is
`V2_FINITE_ONLY` or `V2_REJECT`; the classical partition minimizer by itself
does not elevate a paper.
