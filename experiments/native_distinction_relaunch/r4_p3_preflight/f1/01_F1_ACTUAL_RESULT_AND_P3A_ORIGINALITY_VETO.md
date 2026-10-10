# F1 actual execution & preliminary P3-A originality veto — 2026-10-10

Authority: F1 preregistration `00_F1_SOURCE_BACKED_K8S_FREEZE.md` at commit `d6336500d229610b3d875efbc28e0a7b26261a56`.
Implementation before first F1 CI: `091b628e5e36bd7d5f41d2ee0006c086dbd73baf`.
Original v1 G4 at `c15b212ad0c2be3856a03d38802aaffa628aefd1` unchanged.
**Disposition: F1_SCOPED_SOURCE_BACKED_DEV_DIAGNOSTIC_ONLY; B9 TIE; NO P3 INDEPENDENT VALUE.**

## Reproducible execution and provenance

- First F1 CI: https://github.com/MKLEE222/EEQ/actions/runs/38017684517
- Run ID `38017684517`, job `114111513699`, result **SUCCESS**.
- All **16/16** F1 unit tests pass, including source-blob pinning, 8 archived source-only/native matches, fixed 4-pair reuse contrast, missing-source/unsupported feature tests, original fixture tamper and F0 invalid-completeness counterexample.
- Deterministic audit artifact: `11656528198`, `eeq-p3b-f1-source-backed-dev-audit`. Inside audit JSON SHA256 from Actions stdout:
  `4dd0249b024750e132bc87eb7378e52bc78df6e8aca3bee11b061df3641415ea`.
- Original K8s source bytes: 7 Git blob SHA1 pins in the preregistration; native outcomes are old independent R2A results (run `37906692298`, artifact `11604423996`) and **not an unseen evaluation**.
- F1 native API calls: **0**. New v1 G5 scored cases: **0**. New G8 cases: **0**. R4 P3 author-time trials: **0**. No old artifact or original main changed.

## Frozen F1 decision-reuse result

| Binding / Pod | Relevant namespace reads | F1 source-backed verdict | Prior native decision | Hand-engineered B9 |
|---|---|---|---|---|
| A / flux | team | REUSE_DECISION_ONLY | REJECT -> REJECT | SAME |
| A / default | team | REUSE_DECISION_ONLY | ACCEPT -> ACCEPT | SAME |
| B / flux | team, mode | REVERIFY_REQUIRED | REJECT -> ACCEPT | SAME |
| B / default | team, mode | REVERIFY_REQUIRED | ACCEPT -> ACCEPT | SAME |

- 2/4 decisions conditionally reusable, 2/4 conservatively reverified.
- 0 unsafe reuse against **archived development labels**; 1 extra revalidation B/default. No superiority over equal-information B9 (4/4 parity in a hand-engineered reference implementation, **not** an independent external-maintainer study).
- The old F0 guard accepts a dishonestly self-asserted `complete:true` closure that omits namespace mode; under this **violated premise** it yields false reuse for native B/flux. This does NOT falsify F0's explicitly conditional safety statement; it demonstrates why completeness cannot be self-attested.
- The F1 source-backed parser derives selector reads from all keys in the frozen `namespaceSelector.matchLabels` dictionary, with strict refusal on `matchExpressions`, `paramRef`, unregistered CEL/multiple rules. This prevents THAT omitted-mode example in the fixed single-binding grammar.
- F1 only yields a **reuse candidate** conditional on the original native action actually happening; it neither authorizes native ACCEPT nor allows an old signed source/provenance certificate to be replayed unchanged after a namespace revision.

## Narrow conditional invariant (existing dependency-locality reasoning)

Let `S_b` be the registered `matchLabels` keys of Binding b and `L,L'` two *fully observed* namespace label maps. For the fixed single Binding, registered VAP and Pod source in F1,

`D_b(L,p)=REJECT iff (p.serviceAccountName='flux' and for every k in S_b: L[k]=binding[k])`.

If `L|S_b=L'|S_b`, all clauses of that fixed predicate are unchanged and therefore `D_b(L,p)=D_b(L',p)`. This is a straightforward program dependency property **NOT A NEW THEOREM**. Native validity of the assumptions, source authenticity, other admission mechanisms, action success and completeness outside this whitelist remain unproved.

**Indistinguishability veto**: When two lawful histories have the same retained projection yet different registered future native decisions, no deterministic decoder of only that projection can be correct on both. This ordinary information-theoretic observation rules out a hash-only fix and motivates either source enrichment or REFUSE; it does not itself create novel EEQ algebra.

## Preliminary close-prior-art threats: do NOT claim novelty

| Threat | Directly relevant work | F1 / R4 reduction risk | Current verdict |
|---|---|---|---|
| Decision partition refinement | Paige & Tarjan (1987), classic automaton/finite-trace minimization | R2B legal merges and future-state quotient are classical | KNOWN / no operator novelty |
| Data and proof lineage | Green, Karvounarakis & Tannen, *Provenance Semirings* (PODS 2007) | Typed source/provenance circuits and support qualification records not unique | STRONG THREAT |
| Program dependency update | Acar, Blelloch & Harper, *Adaptive Functional Programming* (TOPLAS 2006) and later self-adjusting computation | Dependency read-set tracking and change propagation, including changing branches, is existing technique | STRONG THREAT / F1 NOT NOVEL |
| Higher-order incremental maintenance | Ahmad, Kennedy, Koch, Nikolic, *DBToaster* (arXiv 1207.0137; later VLDB J.) | Avoiding unnecessary recompilation via deltas and cached dependencies is existing technique | STRONG THREAT |
| Native trust qualification | TUF Specification §5.3 root updates | Old+new thresholds, root version succession, expiration and signature authorization are native TUF obligations | STANDARD, NOT EEQ NOVEL |
| Native Kubernetes policy/selector qualification | Kubernetes Validating Admission Policy + Binding docs | matchLabels, multiple bindings, params, CEL, namespaceSelector all already specified | STANDARD, NOT EEQ NOVEL |
| Fully informed engineering baseline | B9 same source, scope, cache, native library and certificate interface | F1 hand-engineered B9 produces the exact same read-set decisions; no human cost evidence | **B9 TIE** |

Sources for follow-up adversarial prior-art review:
- Paige/Tarjan https://doi.org/10.1137/0216062
- Green et al. https://doi.org/10.1145/1265530.1265535
- Acar et al. https://www.cs.cmu.edu/~rwh/papers/afp/toplas06.pdf
- DBToaster https://arxiv.org/abs/1207.0137
- TUF https://theupdateframework.github.io/specification/v1.0.36/
- K8s https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/

This is a targeted **veto audit**, NOT an exhaustive systematic prior-art survey. A strong mathematical/source-theoretic novelty claim is currently unsupported.

## Next scientific gates and abort conditions

**P3-A remains open**: decide whether any reusable qualification extractor/certificate verifier contributes more than recognized provenance + self-adjusting dependency maintenance + hand-engineered B9. Do not call paperwork or a shared JSON certificate a new semantics compiler.

**P3-B remains open beyond F1**: independently derive and check a complete read-set under changing policy/binding/params, multiple simultaneously matching bindings and authenticated native source transitions. Current F1 expressly refuses these and cannot claim C1 all-reachable histories. The crucial adversarial challenge is **missing or unqualified source vs a native DENY**, with matched safe native coverage, not an all-REFUSE solution.

**P3-C is unopened**: freeze maintainer cohort, comparable tasks, randomization/counterbalancing, exact complete B9 engineering freedoms, primary pair-wise verified minutes, native-safety guardrails, exclusions, sample size, stopping rule, confidence/variance and preregistered success threshold before any scoring. If B9 ties on full correctness/coverage and workload, retain `STRONG_BASELINE_TIE`.

**R5 unseen new-family transfer is unopened.** Historical X.509 and prospective in-toto are not fresh v2 transfer families. Original G6 global C1 gate contested; original G8 incomplete. Any migration of original v1 classifications requires a new version, never rewriting G4.

### Scientific interpretation

F1 has made an explicit safety premise executable and identified a concrete omitted-dependency witness, but is at present reducible to **ordinary restricted rule evaluation and static data-dependency tracking**. That is a serious originality limit rather than a result to advertise as a breakthrough.

Final research state: **R4_INDEPENDENT_VALUE_NOT_ESTABLISHED**.
