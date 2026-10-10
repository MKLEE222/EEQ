# F0 — ENDOGENOUS EVIDENCE: PRE-IMPLEMENTATION FOUNDATIONAL KILL FREEZE

Date: 2026-10-10. Branch: `eeq-f0-endogenous-evidence-interventions-20261010`. Parent: `faa6a87c390d20a8c9421d058b3e8bd36d6adf12`.
**STATUS: FROZEN BEFORE NEW CODE AND SCORING. ALL LOGICAL CARRIERS SYNTHETIC; ZERO NEW TUF, KUBERNETES, G5, G8, P3, OR HOLDOUT SCORING.**

## Hypothesis reset / reason for NOT building P3 or another verifier

P2 showed 16/16 domain-specific primitive leaf assertions can be reconstructed, and two P1 forgeries vetoed, yet strong B9 can copy everything. H3 originality NOT ESTABLISHED. Going further down requires identifying the **scientific object**: an observer's effort to obtain admissible evidence is itself a potentially state-changing **action**, rather than a read-only database query. Evidence observed after such an action may cease to identify the PRE-action contract; it might also invalidate earlier certificates by changing trust/authorization or source coverage.

Candidate object for REJECTION/RECOMPOSITION: **intervention-conditioned justifiability**, not a proposed novel algorithm. Does a qualified post-action observation warrant a claim about the pre-action state? Does an authorized action that changes future read rights permit an identification formerly impossible under fixed observations? Can any algorithm deduce an unobserved denial's absence without an independently authorized and closed source roster?

## Formal finite model: fully known TRANSITION laws, partially hidden world

Each toy world has pre-state bit p in {0,1} for the scoped effect; actor initially cannot read it, `list_allowed=False`. An authorization action `GRANT_READ`, allowed only if actor's grant right is anchored in a declared trusted root/authorization, changes `list_allowed` to True and the observation epoch from 0 to 1. It has one of two *pre-registered* modes:

- `PRESERVE`: `post.p = pre.p`.
- `OVERWRITE_TRUE`: `post.p = 1`, irrespective of `pre.p`.

After grant, `READ_POLICY` returns the POST bit and observation epoch 1. Before grant, no lawful read of p. The exact native API semantic validity of such a grant/policy combination is NOT claimed: this is an **abstract logical countermodel** to the assumption that evidence acquisition is read-only. The effects of GRANT are known to the claimant; knowing the action model is NOT observing the hidden pre-bit.

Let (F_a) be deterministic action transition, (O) lawful observation and (f) the PRE or POST contract:
[
K_f(o,a) = {f(s): s\in W_{pre},\; O(F_a(s))=o}.
]
One may issue a certain pre-claim only when (|K_f(o,a)|=1) AND the relied-upon authority/source-coverage premises are separately trusted. If two pre-worlds produce identical complete legal post-action observations but disagree on (f_{pre}), the pre-claim cannot be reconstructed by any post-only deterministic decoder. This is simply **noninjectivity/possible-world certain answers**, NOT a new theorem.

### Frozen SIX foundational falsifiers, before code

| ID | Worlds/authority | Claim | Frozen expected outcome |
| -- | -- | -- | -- |
| I01 STATIC-NO-READ | pre p=0 vs p=1, no anchored GRANT, actor cannot READ | PRE.p | UNIDENTIFIABLE: pair indistinguishable under legal observation |
| I02 ANCHORED-NONINTERFERING | same two worlds, rooted GRANT, `PRESERVE`, GRANT then READ | PRE.p | IDENTIFIABLE at epoch1: observed 0 vs 1 separates worlds, 1 lawful intervention |
| I03 ANCHORED-DESTRUCTIVE | same two worlds, rooted GRANT, `OVERWRITE_TRUE`, GRANT then READ | PRE.p | UNIDENTIFIABLE even after lawful GRANT: both postbit1, same observation and same successor; opposite PRE p |
| I04 POST-ONLY | same I03 pair, rooted GRANT, `OVERWRITE_TRUE`, GRANT then READ | POST.p | CERTAIN_TRUE=1; MUST NOT be relabelled a successful PRE inference |
| I05 ROOTLESS-DELEGATION | two source credentials `A<-B`, `B<-A` but no rooted authorizer; graph positive least fixed point | authorization to GRANT/READ | REFUSE (rootless cycle does not make own authority); with anchor A, A/B become qualified and I02 GRANT becomes lawful |
| I06 SOURCE-CLOSURE | visible Deny source=0, hidden additional Deny x=0 vs x=1, no authority to enumerate hidden source class or prove completeness | GLOBAL-NO-DENY | UNIDENTIFIABLE; no global ACCEPT, but a verified positive VISIBLE Deny=1 implies scoped Deny with either hidden x |

Additional two fixed diagnostic controls **NOT new primary cases**: (i) same payload/proof bytes, issuer A qualified under pinned anchor A at epoch0, trust rotates to B at epoch1: CURRENT qualification false while historical epoch0 claim may still be valid; (ii) an unrelated audit field changes without modifying pre/post p or authorization: PRE claim remains unchanged, without implying proof freshness can be carried over. These control truth-support separation and irrelevant-change invariance.

### Full B9 and alternative theoretical reduction MUST be scored

- **Fully informed B9** gets the *same lawful observations, grant semantics, source/authority roots, action history, contract and all proof tools*, never the hidden prebit for free. It may use exhaustive preimage reasoning and compute the same six outcomes. If it ties, report TIE.
- Naive fixed passive-query E1 is a **restricted diagnostic** and may fail I02; this is NOT a real advantage over full B9.
- An exhaustive independent oracle must compare all pre/post worlds, legal observations, preimage claim constancy and root reachability. It must independently verify I01–I06, and whether the I03 two states actually converge after the action.
- Must refuse self-authorized cyclic credentials; missing list permission must never be interpreted as `visible_sources=[]` being complete.
- Candidate program must NEVER import or read results from the original P2/E2 source scorers. Tests cannot turn a post-action inference into a pre-action inference.

## Strongest known reductive prior art (FIRST-CLASS originality veto)

1. Dynamic epistemic logic already formalizes model-transforming actions: https://plato.stanford.edu/entries/dynamic-epistemic/
2. Bucheli, Kuznets, Studer 2014, *Realizing public announcements by justifications*, `https://doi.org/10.1016/j.jcss.2014.04.001`: updating explicit justifications is established theory.
3. Becker & Nanz, *A Logic for State-Modifying Authorization Policies*, 2007/2010 `https://www.microsoft.com/en-us/research/publication/a-logic-for-state-modifying-authorization-policies/`: requests modifying the authorization state and reasoning about sequences already known.
4. Libkin 2016, *Certain answers as objects and knowledge* `https://doi.org/10.1016/j.artint.2015.11.004`: preimage/set-of-world certainty belongs to incomplete-information reasoning.
5. Why/why-not provenance for negation: `https://arxiv.org/abs/1701.05699`; source dependence and negative explanations not automatically novel.
6. Trust management delegation least-fixed-point semantics and trusted anchors are standard; no new novelty from rejecting cycles.
7. Fully informed hand-engineered B9 may copy every state-changing action planner, knowledge-state filter, proof witness and comparator.
8. Classical observational equivalence, labelled transition systems and knowledge-game theory may encode ALL F0. If a faithful translation exists, label `REDUCIBLE_TO_DYNAMIC_EPISTEMIC_LOGIC_AND_INCOMPLETE_INFORMATION`, **not a novel EEQ operator**.

## Failure, science gate and original program discipline

F0 GOAL: falsify the previous simplifying premise `EVIDENCE_ACQUISITION_IS_PASSIVE` and expose the action/preimage authority boundary with exact finite witnesses. Even SIX/SIX positive conclusions mean **F0_FOUNDATIONAL_SEPARATION_DEV_ONLY_B9_TIE**, never H3 superiority.

F0 FAIL: one expected disposition wrong, false access authorization, an action-rewritten preclaim misreported as resolved, a rootless trust cycle accepted, incomplete negative source treated as global ACCEPT, original source/Protocol edit, or even one hidden state leaked to a model-observation method.

If current literature/strong B9 fully models the result, retain exact `REDUCIBLE_TO_PRIOR_ART`; advance original research only with a prospective target beyond mere problem recoding: source authority acquired from native provenance with independently justified noninterference/prestate recoverability OR impossibility explicitly grounded in native APIs, matched B9 and an independent new property not already proved by epistemic/dynamic justification logic.

Original immutable main `b5434ab1ad317e5121c88b632806880f903774db`, G4 authority commit `c15b212ad0c2be3856a03d38802aaffa628aefd1`, blob `3eeaeeb828d2fcf7ec4487da06489fee3146c920`, legacy B10 blob `9a6bff7a2b8db73b86b6952c706852c92b1a4b1d`, old G5=285, global G6 C1 disputed, G8 incomplete, fifth family sealed holdout unopened; original W1 V1 native gate FAILURE retained and W1 V2b RETROSPECTIVE only.