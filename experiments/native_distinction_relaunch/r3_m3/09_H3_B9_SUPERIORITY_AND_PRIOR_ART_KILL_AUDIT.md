# H3 Cold-Start Originality Kill Audit After Native M3

Date: 2026-10-10. Disposition: R4_INDEPENDENT_B9_SUPERIORITY_NOT_ESTABLISHED.

## Immutable evidence

- Original M3 V1 native Actions 38027186154: 2 controls, 0 main decisions, blocked by missing collection resourceVersion.
- Versioned V2 used raw Kubernetes API LIST with real per-collection resourceVersion. CI 38027428940 saved 8 native observations, 2 no-binding controls, 3 actual policy/binding mutations, and 4 source inventories. Original scorer FAILED on API-defaulted fields; that original gate remains FAILURE.
- Independent retrospective source-vs-native differences CI 38027634073 revealed only Kubernetes API defaults.
- A separate POST-NATIVE V2B semantic-equivalence freeze (commit 7acdd4c0592492cbe381d38e08dbd5541080726b) preceded any retrospective repair. V2B CI 38027750776: 46 anti-masking tests, narrowly checked 46 defaulted fields across 16 source items, exact frozen scorer reused, retrospective 8/8 source/native, 2/2 controls, 3/3 actual native membership mutations, 4/4 inventories, B9 8/8. No native rescoring or fresh holdout.
- Original two binding source bytes and API identities never changed. A matching third source caused previously ACCEPTed default Pod to be REJECTed; policy without binding did not; deletion restored ACCEPT.

## Indistinguishability ceiling (classic, NOT a novel theorem)

Given qualified observed source evidence O, let W(O) be all lawful completions consistent with O, including unknown additional source membership, and D(w,c) the decision on claim c in world w. If there exist w0,w1 in W(O) with D(w0,c)=ACCEPT and D(w1,c)=REJECT, no deterministic algorithm based solely on O can soundly assert unconditional ACCEPT or REJECT in both worlds. The proof is the standard same-input/opposite-output argument; it is an ordinary certain-answers / possible-world fact.

M3 provides a NATIVE witness that same old source hashes do not establish source membership closure. It does not prove that EEQ has a novel algorithm or can surpass fully informed B9.

## Meaning of superior B9 scientific contribution

If strongest B9 is mathematically defined to include ANY algorithm on the SAME sources and decision contract, it includes a copy of EEQ; strict universal decision expressivity dominance is impossible by construction. Distinct value must be proven in a new, well-defined scientific object, valid new explanation, provable soundness/coverage bound, or independently measured fair construction/maintenance effort. B9 must not be denied any native semantics, old/new source observations, cache, provenance checker, or authoritativeness mechanism available to EEQ.

Main candidate: a contract-relative EVIDENCE VALIDITY FRONTIER over:
 actor/source authority and inventory/freshness scope;
 which evidence is qualified for which claims;
 action-induced requalification and support lineage;
 independently checkable prospective decision/certificate or REFUSE.
The object is not established as theoretically new, and current domain adapters remain handwritten.

## Serious close prior-art attack (must not rebrand)

- Kubernetes LIST->WATCH/Reflector and 410 resync already solve standard resource collection maintenance:
  https://kubernetes.io/docs/reference/using-api/api-concepts/
- OASIS XACML 3.0 effect-specific Indeterminate and possible-world certain answers already study partial/unknown evidence:
  https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-cos01-en.html
- Green et al. PODS 2007 semiring provenance https://doi.org/10.1145/1265530.1265535
- Acar et al. TOPLAS 2006 adaptive computation https://www.cs.cmu.edu/~rwh/papers/afp/toplas06.pdf
- DBToaster incremental view maintenance https://arxiv.org/abs/1207.0137
- Two near-neighbor individual IETF Internet-Drafts (NOT RFCs, not standards, not automatically peer-reviewed):
  I. Schrock, Aug 2026, Authority Documents and Scoped Authority for Agent-Action Evidence:
  https://datatracker.ietf.org/doc/draft-schrock-ep-authority-introduction/03/
  S. Das, Sep 2026, When Valid Authorization Becomes Stale: State and Policy Continuity at the Execution-Finality Boundary:
  https://datatracker.ietf.org/doc/draft-das-state-policy-continuity-finality/
  These directly threaten claims that authority proof, freshness or state-policy continuity alone are novel.
- TUF dual root signatures and Kubernetes VAP rule evaluation are native standards, not EEQ creations.

## Next scientific gates (not yet performed)

C1-WATCH: prove an externally authorized actor can enumerate declared source classes and continue the native LIST version with an event-complete WATCH, including explicit failure on 410/gap/RBAC denial/unmonitored source classes. No global Kubernetes admission C1 from two separate VAP LISTs. Full B9 may use identical list/watch and cached evidence.

P3: freeze prospective changes and fair two-route maintenance tasks, assign independent competent maintainers with randomized/counterbalanced tasks, and choose primary verified adaptation minutes under exactly matched native correctness, safe coverage and source evidence rights. Account for all semantic adapter, tests, source acquisition, proof checker and debugging labor. Without independent maintainers no causal advantage claim. Strong B9 fully equipped; a tie invalidates superiority.

R5: only then preregister a truly untouched new v2 native transfer family, not the old X.509 or in-toto.

STOP/KILL: more 100% accurate native examples with identical B9=100% do not constitute a new method. If the proposed operator reduces to standard certain answers, native policy semantics, LIST/WATCH and incremental provenance with no distinct theory or cost, classify REDUCIBLE_TO_PRIOR_ART + B9_TIE and reposition scientifically.

Final current state: mother problem sharper and experimentally supported in controlled settings; novelty vs B9 NOT ESTABLISHED. Original main/G4/B10 and original G5 count 285 unchanged.
