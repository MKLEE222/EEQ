# K0 actual cold-start source-boundary reduction and trusted-base kill audit

**2026-10-10. Status: NEGATIVE SCIENTIFIC AUDIT ONLY.** Branch `eeq-k0-trusted-boundary-reduction-audit-20261010`; original study parent `0d0d3502dd98a898ad183f02b4a666cb8f9d2794`. Scope and fail categories were locked in `00_K0_REDUCTION_AND_TCB_AUDIT_SCOPE_LOCK.md` at commit `14b7d1b0a8a2d566124593a31f9ff0cecc9d4adc` before this conclusion.

## 0. The decisive cold-start diagnosis

Our scientific bottleneck is NOT `find a source`, `compute sufficient evidence`, `keep source digests`, `verify a Boolean proof`, or `observe changes` separately. Substantial existing theory already handles each. Nor is it the demand that a system establish its OWN externally trusted authorizations/closure from no assumptions—this is impossible under indistinguishable lawful observations.

The missing experimental/theoretical evidence is whether EEQ's **end-to-end construction** of a warranted scoped decision from REAL native contract semantics materially improves something *not already provided by the full conjunction* of (a) query-completeness reasoning, (b) native semantic verification/credential discovery, (c) time-aware trace/cut monitoring, and (d) proof-carrying software with the same APIs, domains, budgets and domain-specific adapters. The current P2 does not substantiate such a residual.

This is a hard result for novelty positioning, not evidence that the underlying EEQ mother question is trivial.

## 1. Scientific semantics — EXACT trust interfaces must be externalized

Fix an externally specified decision contract `J`, an external trusted native-semantic description/interpreter `Sigma` (including the policy action language), and explicit root assumptions `R` including initial anchors, actor rights, source-universe and time/freshness guarantees.

Let `H(E | J,Sigma,R)` be the set of lawful native execution histories consistent with the legitimately observed evidence `E`. Each history includes native source objects and identities, actor-permitted reads, supported action transitions and time/casual ordering; any facts `R` does not prove must remain possible.

A scoped positive warrant for `c` at time `t` exists iff

  `H(E | J,Sigma,R)` is NONEMPTY and for EVERY h in `H(E | J,Sigma,R)`, `D_J(h,t)=TRUE`.

A negative warrant similarly requires all compatible histories to yield FALSE. If mixed, the only grounded status is UNKNOWN/REFUSE, not FALSE. Empty compatible histories are an inconsistent-evidence/error status, NOT vacuous authorization.

This construction is an elementary certain-answer/partial-observation definition, not a new EEQ formalism. It explicitly prevents claiming an unconditionally global Kubernetes ACCEPT from a conditional VAP subset.

Required separate assumptions:
- `J`: Claim and allowed continuation vocabulary are **specified from outside**. An agent cannot infer user values/desired contracts solely from source bytes.
- `Sigma`: Authentic native grammar/semantics of TUF or K8s, including version and trust evaluation. The algorithm cannot infer arbitrary unknown native meanings from bytes alone.
- `R_root`: External trust anchors/issuer authority; a credential cycle cannot establish its own root.
- `R_roster`: Externally supportable source-class/actor coverage and a valid basis for positive absence of additional support. Cannot be created by setting `complete:true`.
- `R_time`: Valid actor observations at target epoch, actual temporal coexistence across relevant sources; no atomic multi-kind snapshot inferred merely from two independently correct LISTs.
- `R_transitions`: Legitimate native action/continuation semantics, including observation actions changing the system.

None of these may be hidden in a Boolean proof leaf. An implementation may TRUST, VERIFY using a trusted primitive, or REFUSE; it cannot simply promote user-provided assertions into guarantees.

## 2. Code-level trusted-base finding: standalone P2 accepts internally consistent UNTRUSTED witnesses

**Precisely scoped statement: a portable/detached checker trust-boundary failure, NOT a new failure of original P2 trusted-source CI.**

Directly inspected original Git blobs, unchanged:
- `r4_e2/r4_e2_generic_rule_checker.py`: `67fa774624e849d9ff31a5234fd4d8162cfb4425` (107 source lines). `check_program` verifies typed `ATOM.value` is bool, `source_refs` name an entry in a dict of 64-hex-character source hashes, unique IDs and rule structure. It does NOT independently open or interpret a TUF/K8s original source, verify signatures or guarantee source scope.
- `r4_e2/p2/p2_independent_original_source_entailment_checker.py`: `b0e5cdb17ab9057aa02a3415e6817d67bb8fd4b6` (66 lines). `verify(program,external)` invokes the above structural checker, then checks that `program.case_id/domain/registered_contract/source_sha256/formula` equal the corresponding fields in caller-provided `external`, and domain-dependent `external` flags are TRUE. It does NOT read, hash or semantically interpret original native source bytes in this function.
- `r4_e2/p2/p2_tuf_independent_native_leaf_witness.js`: `df0ac189dcd293b4a7fb89abc86e83f9016e17fa` (146 lines). The separate trusted generator reuses `sourceFixtures`, original TUF `canon` and Node `crypto.verify`, reconstructing dual-role Ed25519 threshold checks for the fixed development grammar.
- `r4_e2/p2/p2_k8s_independent_source_leaf_witness.py`: `46fda59868e5098a539014a45f11128a479de286` (162 lines). A separate trusted generator declares EIGHT pinned raw file Git blobs, TWO registered policies, THREE Bindings, FOUR AUTHOR-REGISTERED phase rosters, TWO Pod subjects, and a whitelisted regex for exactly one CEL predicate and namespace selector grammar. These are not native complete source-set attestations.
- The original E2 source compilers are separately handwritten `r4_e2_tuf_source_rule_compile.js` Git blob `8ed03d9d8418392d57d8aed7b2afc69ca2267a1f` (149 lines) and `r4_e2_k8s_source_rule_compile.py` Git blob `0488dc542da4429f36f5e697d89f98e5d7cacea3` (197 lines).

**STATIC COUNTEREXAMPLE (NO EXECUTION CLAIM):** take any E2 program with a FALSE old-root signer leaf (or TRUE third-binding CEL-Deny leaf), make a COPY, and flip exactly that `ATOM.value`. Next take the `external` witness, copy it, change the SAME `formula` leaf to match the forged program; keep both copies' `source_sha256` maps, scope and identity equal; keep external flags true. The detached P2 `verify` will see a structurally valid source-referenced program and a matching witness, so it has no route to detect that neither now agrees with original native bytes. It returns the bounded structural `SCOPED_SOURCE_PRIMITIVES_INDEPENDENTLY_RECHECKED` status. This follows directly from its input/branch behavior. If actual `external` is freshly GENERATED and TRUSTED by the source-side P2 CI, the forged `external` violates that pipeline's trust premise and would not arise in that CI. Thus DO NOT relabel old 16/16 P2 SUCCESS as a scientific failure. This is a statement of the **detached verifier's restricted security claim**.

The original P2 Actions [38033392107](https://github.com/MKLEE222/EEQ/actions/runs/38033392107) first generated source-derived witnesses using the pinned trusted generators, and only after that fetched old E2 IR. Its 16/16 matched-source checks and 2/2 P1 forged PROGRAM-only vetoes remain authentic **conditional** source-backed development results.

**Exact trusted-boundary conclusion:** verifying `program == witness` is not the same as checking `native_bytes, trusted_roots, scopes, epoch |= witness`. The current P2 trusted base includes witness generator+original native parser/canonicalizer/crypto rules and externally furnished inventory, not only the 66-line wrapper+107-line generic Boolean checker.

Approximate inspected implementation sizes are IDENTIFICATION diagnostics, not tested engineering cost: 107 generic AST +66 detached check +146 TUF native witness +162 K8s native witness +149 TUF source compiler +197 K8s source compiler = 827 source lines (including blank lines, documentation and glue); these numbers do NOT measure TCB attack surface, minimal implementation, staff hours or comparative advantage. External packages and native API obligations are excluded.

## 3. Two-sided killer of the 'automatically establish minimum necessary completeness' claim

**KILL A — existing tools can construct the boundary under trusted premises.**

Given a FIXED finite native contract `J`, scoped external assumptions `R_root, R_roster, R_time`, and trustworthy source semantics `Sigma`:
1. Use native parser/credential validation to encode admissible source predicates with provenance, actor, role, epoch and action dependencies.
2. Represent source completeness as a set of trusted query/table completeness constraints or a richer claim if the contract requires it. Obtain or REFUSE externally attested completeness; don't manufacture it.
3. Obtain qualified credential chains using goal-directed trust-management search, evaluating authorization predicates over the restricted native scope.
4. Restrict candidate histories to source versions/cross-source cuts compatible with available native trace order and required time claim.
5. Evaluate native decision formula over all candidate histories; the claim is warranted if and only if all agree (certain-answer/monitoring).
6. Construct a native-verifiable proof witness and its condition list using certifying/proof-carrying techniques, retain provenance dependencies and invalidate/recheck affected nodes after native actions by standard incremental view maintenance.

This is an explicit **reduction architecture for finite decidable restricted grammars**. It is NOT a formal correctness proof of an arbitrary real-time/complete Kubernetes evaluator and does not promise polynomial worst-case cost. It is enough to reject 'no other method can achieve a scoped warranted decision once trusted assumptions are supplied'. Fully informed B9 is allowed the exact same source procedures, proof certificates and optimizer. On the same finite task, unrestricted B9 can simply instantiate EEQ itself.

Existing sources:
- Razniewski & Nutt, *Completeness of Queries over Incomplete Databases*, PVLDB 2011, https://www.vldb.org/pvldb/vol4/p749-razniewski.pdf ; both query-completeness inference and weakest completeness conditions appear, with explicit expressive LIMITS (their Theorem 3 shows a projection query can lack a characterization by any set of restricted TC statements under set semantics). Do not weaken full B9 to this restricted TC language when richer completeness logic is lawful.
- Li, Winsborough & Mitchell, *Distributed Credential Chain Discovery in Trust Management*, Journal of Computer Security 2003, https://doi.org/10.3233/JCS-2003-11102 ; goal-directed credential retrieval and a scoped sound/complete credential graph.
- Necula, *Proof-Carrying Code*, POPL 1997, https://doi.org/10.1145/263699.263712 ; certifying compilers and translation validation https://people.eecs.berkeley.edu/~necula/papers.html ; CompCert https://compcert.org/man/manual001.html .
- Green, Karvounarakis & Tannen, *Provenance Semirings*, PODS 2007, https://doi.org/10.1145/1265530.1265535 .
- Original TUF v1.0.36 root continuity and old/new role thresholds, https://theupdateframework.github.io/specification/v1.0.36/ . Kubernetes List-Watch guarantees, https://kubernetes.io/docs/reference/using-api/api-concepts/ .
- Dynamic epistemic action/history semantics and classical distributed consistent cuts apply; see original F0 audit and cited sources. No claim a single cited paper alone supplies ALL native adapters or full pipeline.

**KILL B — without observable qualified premises, EEQ cannot create them either.**

Construct H0 and H1 with identical all-lawful actor observations, same visible source hashes, same known historical actions, but differ in an inaccessible compatible source or its contemporaneous qualification: H0 has no hidden applicable Deny; H1 contains a valid applicable hidden Deny. If there is neither a trusted source-universe completeness certificate nor legal observation/action which separates these histories, then any deterministic or randomized procedure based only on the lawful observation cannot correctly make an always-certain divergent decision in both worlds. The sound response is scoped UNKNOWN/REFUSE.

The issue is **lack of knowledge**, NOT B9 algorithm weakness. Similar indistinguishability with two individually verified policy/binding observations but unknown cross-kind event order prevents asserting their coexistence at the requested time. No amount of structural Boolean certificate recombination resolves missing causal/time observations.

Hence `unconditional independently established globally complete native warrant from finite partial evidence` is impossible; a weaker explicit contractual/authorized boundary is required.

## 4. A THIRD kill: 'the least sufficient boundary' need not be a single unique object

Even under perfect source qualification and a finite monotone contract, a set of **minimal** positive supports need not have a unique LEAST member.

For `c = a OR b`, `{a}` and `{b}` are two incomparable inclusion-minimal sufficient positive support sets. Their intersection is empty (not sufficient); their union is not minimal. Calling either `THE minimum sufficient evidence` without an objective (per-source cost, time, trust, etc.) is mathematically ill-posed.

Worse, let `c_n = AND_i(a_i OR b_i)` with n independent source pairs. There are **2^n** different inclusion-minimal support sets (choose exactly one of each pair). An algorithm explicitly outputting EVERY minimal witness requires Omega(2^n) output size even with trivial native Boolean rules. A symbolic DAG/factored provenance polynomial can be compact; standard provenance semiring and Boolean lineage already investigate this, and FULL B9 can use the same compressed representations. This is an elementary support-antichain/output-size fact, NOT an EEQ lower-bound novelty claim.

For a negative no-Deny claim, additional externally justified source-universe completeness may be needed; Boolean duality across a CLOSED declared roster is not a substitute for an externally proven roster.

**Implication:** before claiming 'minimum proof obligation' choose whether we mean (i) one minimum-cost witness, (ii) an antichain of all inclusion-minimal witnesses, (iii) an intensional/symbolic formula representing them, (iv) a minimum trusted assumption set, or (v) minimum worst-case post-action repair work. They are different optimization problems and can have different cardinality, complexity, validity and baseline results.

## 5. Matrix: where the previous program actually established an obligation

| Obligation | Existing EEQ evidence | What remains EXTERNAL/TRUSTED | Strongest already-known explanation |
| --- | --- | --- | --- |
| Exact contract-relative decision on full finite native state | G4/G5, P2 dev cases | honest registered contract/action vocabulary and native oracle scope | model checking, sufficient state, native semantics |
| Legal evidence-acquisition minimax | E1 17/17 synthetic | source-qualification atoms, legal reads and fixed costs | weighted decision trees + possible worlds |
| Role/signature authenticity | E2/P2 fixed TUF signed-root bytes, 8 development cases | trusted initial anchor, canonicalization/Ed25519 verifier, clock/repository conditions | TUF native specified verification |
| K8s VAP/source predicates | E2/P2 8 old source-only examples | hardcoded two policies, three Bindings, fixed CEL/selector grammar, hand-entered phase membership, real actor rights and live roster | native admission semantics + VAP source interpreter |
| Syntactic shared proof IR | E2 generic AND/OR/THRESHOLD checker | TRUE/FALSE primitive leaf entailment and source authority; no raw source reads | Boolean circuits / provenance / PCC |
| Conditional independent source checking | P2 16/16 old+2/2 P1 attack veto | ORIGINAL SOURCE WITNESS GENERATOR is trusted, not portable detached checker alone | proof-carrying + domain trusted verifier |
| Live source continuity | W1 3 WATCH events+8 LIST; original V1 FAIL and V2b retrospective | per-kind authority, cross-kind cut, real-time fresh interval, global C1 | Kubernetes LIST/WATCH, Reflector and distributed consistency |
| Effect of evidence-seeking actions | F0 6 finite toy cases | real native action/observation semantics | dynamic epistemic planning |
| Cross-domain reusable translation without whole semantic rewrite | NO independent unseen adaption | semantic parser and constructor for every new family; native authoritative interpreter | schema/compiler implementation problem, NOT novel by default |
| Human construction cost vs full B9 | NO independent P3 study | paired developers, fair tools/budgets, preregistered new tasks, scoring | unmeasured |

Status: **REDUCIBLE_WITH_EXTERNAL_TRUST_PREMISES** in bounded finite model; **OBSERVATIONAL_NO_GO_WITHOUT_PREMISES**; **IMPLEMENTATION_TCB_NOT_DETACHED**; **PORTABILITY_ADVANTAGE_NOT_MEASURED**; **NONREDUCIBLE_THEORETICAL_RESIDUAL_NOT_DEMONSTRATED**.

## 6. GO/NO-GO without inflating cases

**NO-GO** for a theoretical claim that EEQ is uniquely able to build a warranted certificate from partial untrusted source bytes, or that a generic logical proof checker implies verified native authority. The first is contradicted by existing logic under assumptions, the second by code audit, and unconditional claim is impossible without some trust premise.

**NO-GO** for 'one minimum necessary source certificate' without defining the order/cost/symbolic interface, because alternative supports form an antichain and can be exponential.

**CONDITIONAL GO** for an independently falsifiable *constructibility* claim: under a stated supported grammar and native authority APIs, can an EEQ-style compiler generate a source-linked proof/decision procedure with materially LESS NEW trusted domain-specific work, certified equivalent correctness, refusal coverage and ongoing maintenance burden than a FULLY INFORMED implementation baseline using identical libs, credentials, source APIs, reflection/cut/provenance and checker code? **No such result is available today.** The study must charge ALL parser/role/selector/CEL/watch/source-closure/clock/permission/proof/canonicalizer/test/debug/setup work. A comparison against a naive hash-only B9 is disallowed.

**CONDITIONAL GO** for a genuinely new mathematical theorem ONLY AFTER someone proves a specific property not preserved by translations into strong provenance/authorization/DEL/consistent-cut theories, with exactly stated input/complexity class and external premises. No theorem is currently demonstrated.

**BLOCK** a new R5 unopened family until v1 holdout discipline permits it. Do not quietly repurpose an in-toto/X.509 previously touched family as untouched v2 transfer.

No main/G4/B10 edits, no new Actions or trials, no new native/synthetic scored cases, original G5=285, original G6 global C1 disputed and G8 unfinished, fifth holdout remains unopened. All prior E1/E2/P1/P2/F0/W1 results and failures remain in their original folders.