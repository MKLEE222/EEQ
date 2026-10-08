# R2–R4 — Native Bidirectional Counterfactuals and Fair Strong-B9 Challenge

Date: 2026-10-08
Status: DESIGN FREEZE ONLY. EXACT NATIVE FIXTURES / PREDICTIONS NOT YET FROZEN.
Do not execute new native R2–R4 scoring from this document alone.

## 1. One fixed comparison unit

A comparison unit is a pair of lawful evidence histories (h_i,h_j) with:
- a registered source/claim/authority/actor scope;
- native decision-time accessible information V0;
- exactly the same registered current challenge family J_0 and future family J;
- a frozen action alphabet A and horizon r (initial native candidate r<=2);
- an independent native oracle implementation/version;
- case eligibility and native-preexclusion decided BEFORE native outcomes;
- evidence class PRODUCTION_HISTORY or CONTROLLED_NATIVE;
- unique semantic signature, not counted twice for version/seed/retry;
- exact source bytes, SHA manifests, permitted contract edits and fixture hashes.

The R2 experiment cannot be scored until exact units and pre-outcome
predictions are frozen in a versioned experiment manifest.

## 2. Contrast A: future *necessary* distinction

Admit a predeclared pair only if:
- all presently registered decisions/action sets for h_i,h_j agree;
- the two histories have distinct lawful source, qualification or history
  features not fabricated from outcome labels;
- there exists a preregistered native-executable future action word w
  (length 1..r) such that native continuation decisions differ;
- the selected method retains the distinction and emits a verifiable
  (claim, action word, initial source proof, future difference) certificate.

Native verification must execute both paths from independent controlled
initial states. Reading a scripted model's predictions as native labels is
forbidden. If oracle responses are ambiguous, mark native-ambiguous, not a
positive split.

Key diagnostic: a current-only view merges these states incorrectly;
B9 may also keep them apart. That is not an EEQ win over B9.

## 3. Contrast B: lawful *erasable* distinction

Admit a pair only if:
- h_i,h_j differ in bona fide lawful source identity, qualified support
  graph, valid lineage or evidence history. Pure whitespace, JSON key order,
  Suite/Version and other unregistered cosmetic bytes do not count;
- the contract J and action set A were frozen independently of the chosen
  pair's outcomes;
- direct native verification shows the SAME complete decision/continuation
  trace for EVERY registered action word of lengths 0..r;
- the extractor preserves audit/provenance obligations even if the
  *decision quotient* merges these histories.
- no unknown/unexecuted relevant successor is silently skipped.

For a small native carrier, enumerate |A|^0+...+|A|^r words; otherwise
record INCOMPLETE_COUNTERFACTUAL_COVERAGE and do not count the B pair.
Report the contract-relative nature of the merge. If a registered audit
claim explicitly asks which source supports the decision, two different
source-provenance states may be *not* equivalent.

Decision quotient state count below the number of real lawful evidence
states is necessary but not sufficient; full cost can still increase.

## 4. Required third pressure: unknown source / refusal

Predeclare one material missing/expired/unqualified or unavailable
source path that prevents a qualified decision. It must yield a
native-justified unknown/refusal or explicit model-unsupported boundary.
No solver earns a point for refusing EVERYTHING.

Measure both:
- unsafe decisions / false permissions;
- safely answered fraction (coverage) at the SAME eligibility and
  rejection/abstention accounting.

Source-fetch failure is SOURCE_UNAVAILABLE, not a native REJECT.
Policy/source inapplicability is not silently recoded as REFUSE.

## 5. Strong baseline matrix (no straw men)

B0: all lawfully available evidence / native full-history ceiling.
B9: a domain-expert, native-mechanism-derived sufficient state, frozen
BEFORE outcome scoring. It may include every legally readable source,
qualification, action, continuation and history rule that the EEQ
extractor may use. It may be nonminimal; optimize it fairly if a reasonable
engineering simplification exists.
Old B10-v1: retained, never retrospectively redefined.
Moore/classical quotient: strongest direct partition-refinement baseline
on the SAME model graph with the SAME registered observation challenges
and horizon. Its decision partition may match the new quotient EXACTLY;
that is an expected tie, not a failure of the classical method.
A state-engineering-only baseline: expert source/claim-aware information
representation WITHOUT automated extractor certificate, if pre-frozen.
Original frozen B0-B10/O1-O8: maintain applicability/NA accounting if
comparison is published as v1 experiment; a new v2 taxonomy must be
versioned separately, not changed retrospectively.

Do not remove B9 after observing a tie. Do not give B9 only current
snapshots while giving EEQ future contracts. Both may implement full native
future mechanics and even choose a source-qualification-aware state.

## 6. Evaluation without a mathematically impossible target

If B9's exact task optimum is 1.0, new method cannot attain >1.0 on
that identical task. In that event there is NO claimed accuracy advantage.

Do not change metric after observing performance. The exact R4 experiment
freeze must choose its PRIMARY contrast *before scoring*, from:

P1: safer/higher native decision coverage at fixed zero verified false-
    permission threshold, including abstentions and excluded cases;
P2: lower TOTAL measured end-to-end cost at matched exact decisions,
    including lawful evidence retrieval, preprocessing, extractor,
    codebook, certificate and query time;
P3: lower domain-specific semantic adaptation workload under an audited
    identical-input and identical-feature-budget setup, with predetermined
    maintainers/tasks and contemporaneous changes (code size alone cannot
    prove developer-time savings);
P4: independently checkable provenance/qualification or refusal certificates
    that B9 under its frozen contract cannot produce at the same cost/coverage.

P1–P4 are CANDIDATES, not a menu of post-hoc winning claims. R4 must select
exactly one primary family-level metric (and all hard guardrails) BEFORE
the new native comparison. Other metrics are secondary and fully reported.
If B9 or conventional quotient matches the primary plus guardrails:
B9_TIE, no EEQ-specific superiority claimed.

Mandatory hard guardrails:
- exact native continuation match (no fabricated next states);
- sound qualified-source certificates for every accepted claim;
- no increase in false permissions or unreported refusals;
- identical registered action/contract horizon and lawful data;
- full costs, paired seeds, confidence/variance when timing matters;
- hold-out family adaptation performed before labels;
- native success denominators shown by evidence class.

## 7. Fairness audit before execution

An independent reader should answer YES to all:
[ ] Baselines saw the same legally readable source and actor fields.
[ ] B9 is allowed to carry the full future-contract and provenance state.
[ ] No baseline is designed from the very native outcomes it predicts.
[ ] Method extractor did not read future native outcome labels.
[ ] All registered successor histories are tested or explicitly unsupported.
[ ] The distinction A and B hypotheses were frozen before native execution.
[ ] No representational cost omits its dictionary/proof/evidence acquisition.
[ ] Exact task-set recovery (not just action accuracy) is scored.
[ ] The strongest relevant B9 result is retained even when it ties EEQ.
[ ] Synthetic redundancy and cosmetic changes are not scored as B contrasts.
[ ] Any cross-family generalization is tested on a NEW, untouched family.

If any required item is NO, the result is a bounded diagnostic, not H3 PASS.

## 8. Predeclared overall stop line

A genuine general native-method claim requires:
- lawful outcome-blind transition-model extraction on >=2 independent
  development native families under preregistered registered scope;
- at least one native-verified A pair and one noncosmetic, exhaustively
  native-verified B pair in EACH required development family, or the failed
  family's outcome remains an explicit limitation and generality is
  NOT asserted;
- at least one preregistered refusal/unsupported evidence test in each;
- a complete matched B9 and classical-quotient baseline comparison;
- strict improvement on the PRESELECTED primary P1/P2/P3/P4 metric without
  breaching safety/proof guardrails;
- subsequent new-family transfer governed by a separately frozen protocol.

Any failing condition yields a limited or negative result, never a
retroactive narrowing of "general native method".

## 9. Why TUF then Kubernetes (not because of labels)

TUF is a first development feasibility carrier: its root update procedure
requires authorization using key thresholds in the OLD trusted root and
the NEW candidate root, with version continuity. Official normative
reference: https://theupdateframework.github.io/specification/v1.0.36/.
Constructible source/key/qualification transitions should be investigated
before claiming any useful equivalent states. If TUF cannot yield B, report
that limitation; do not count root JSON reserialization as B.

Kubernetes is a candidate for multi-support continuation: registered
policy, binding and parameter sources may be independently scoped, and
multiple matching binding/parameter combinations are evaluated.
Official reference:
https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/.
This motivates a NATIVE policy/binding-update history, not a synthetic
"one policy at a time" simplification of a multi-binding decision.

Neither family is a v2 holdout. Both are development systems already studied
under v1. The specific R2/R3 carrier and contrast grids remain subject to
independent PRE-NATIVE freezing and admissibility review.

## 10. Interpretation

Full A/B satisfaction demonstrates decision-relative distinctions on
native history; classical quotient still may reproduce the same partition.
H3 is about the lawful **source-to-certifiable-transition-model** workflow,
not a new name for an old minimization algorithm.
