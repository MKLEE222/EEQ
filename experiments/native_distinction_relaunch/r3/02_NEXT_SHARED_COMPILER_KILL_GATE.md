# R3 next method candidate — lawful source-to-certificate compiler gate

Date: 2026-10-09
Status: **CANDIDATE RESEARCH CONTRACT, NO NEW GENERIC OPERATOR PASS**.
This plan is prospectively intended for a *new* implementation and testing
stage. It does not retroactively improve the R2-A/R2-B scored results.

## Scientific question to resolve

Can a SINGLE non-domain-specific core construct the correct future
claim/decision distinctions and independently checkable reason certificates
from a lawful source-fact/contract interface, rather than receiving the
native ACCEPT/REJECT outcomes precomputed by each domain interpreter?

The same shared component must be used for TUF and Kubernetes. If all
mechanistic logic lives inside custom adapters and only the JSON format
is common, then R3 has NOT produced an original computational method.

## Provisional minimal machine-readable data model

An input instance must contain:

1. `registered_contract`: claim IDs, actor/authority context, all actions,
   continuation queries, scope/horizon, source and provenance obligations.
2. `source_facts`: stable source IDs/hashes, decision-time visibility,
   claim eligibility, observed vs unavailable status and native source spans.
3. `qualification_relations`: raw verifiable predicates for signed
   authorities, threshold, source/claim binding or policy selector matching;
   *not* final action outcomes.
4. `registered_action_effects`: declared, independently grounded effects
   on source/authority/qualification state with explicit next-state
   references, or `UNSUPPORTED_NATIVE_EFFECT`. The adapter must not
   choose next states by reading scored outcomes.
5. `decision_queries`: registered claims/actions requiring qualified
   support, closed-world prohibition or REFUSE under incomplete sources.
6. `source_proof_hooks`: machine-checkable source byte/digest and native
   predicate verification handles, with a separate native verifier; an
   unverified English explanation is not a proof certificate.

Output:
- explicit `ACCEPT/REJECT/REFUSE/UNSUPPORTED` separated by legality;
- action-conditioned claim-support/qualification dependencies;
- future distinguishing words and contract-relative legal merge witnesses;
- source-anchored evidence certificates and explicit unsupported parts;
- source/preprocess/compiler/codebook/proof/query cost breakdown.

**Permitted specialization boundary:** adapters may parse TUF signed role
metadata and Kubernetes policy/binding/CEL sources into reusable typed facts.
**Not permitted:** adapters output already-scored native action decisions,
hard-code observed R2 result tables, pass future native labels in IDs, or
classify unsupported or missing source values as FALSE by default.

A classic Moore quotient on the same complete graph is a REQUIRED
baseline, not itself EEQ novelty. Source-certified graph *construction*
and valid UNKNOWN boundaries are the candidate added contribution.

## Two competing model explanations (both must be tested)

**EEQ candidate:** lawful source facts + registered contract compiled into
qualified evidence-transition model, certificates, and future quotient.

**Strong B9:** a domain expert receives IDENTICAL readable source/actor
facts, all registered future action semantics, and may construct a
sufficient-state representation with provenance checks and refusals.
The expert is not restricted to current state or deprived of domain
rules. The same canonical source proof verifier may be reused.

Also include full-source B0 ceiling and conventional quotient with the
same graph/observation set. If matched results and matched total costs
are tied, scientific disposition is `B9_TIE_NO_UNIQUE_VALUE`.

## Adversarial mechanism tests to preregister before scoring

- **No-label core test**: static and dynamic trace verifies that generic
  compiler never accesses scored native verdicts or look-up tables.
- **Qualification source mutation**: change TUF targets-role signer binding
  or Kubernetes binding-selector source, preserving other information.
  Certificate validity and decision changes must follow the changed source
  *without any code change*, and be checked by native execution.
- **Unknown source**: intentionally make one material source unavailable;
  REFUSE or UNSUPPORTED must arise with an auditable reason, not a forced
  REJECT or guessed boolean. Report decision coverage as well as mistakes.
- **Bidirectional source distinction**: the same engine must compute a
  future-only separation on Kubernetes A and a noncosmetic contract-relative
  merge on TUF B. Already-scored R2 carriers are development diagnostics,
  not new generalization claims.
- **Foreign-contract probe**: adding a registered targets authorization
  query must split TUF's formerly mergeable anchors; re-run full
  contract-relative equivalence checks without changing the TUF input
  parser.
- **Horizon and action expansion**: expanding the registered future
  challenge family cannot be hidden by backfitting a smaller action set.
  All newly material sources/unknown successors must remain explicit.
- **Codebook/full cost charge**: account for paid source bytes, parsing,
  qualification extraction, state graph, full codebook, certificate,
  verification and decision latency/peak memory, not just class IDs.

## Gate order

C0. Freeze generic grammar, loss/unknown semantics, source byte provenance
    and exact baseline informational parity before any new native outcome.
C1. Synthetic isolated model tests and an independently implemented
    exhaustive trace oracle must pass, including malicious missing fields.
C2. Re-explain archived development TUF/Kubernetes R2 source and native
    evidence WITHOUT domain-specific expected-label lookups.
C3. Freeze NEW source perturbation grids and source/proof predictions prior
    to native verification; do NOT treat C2 historical success as held out.
C4. Select exactly ONE primary R4 advantage P1/P2/P3/P4 before prospective
    new score and timing, with hard safety, coverage and total-cost guards.
C5. Test against fully informed B9 and classical quotient. If no independent
    advantage, retain a bounded positive source-certification result rather
    than inventing new algorithmic originality.

## Falsifying outcomes that end this operator track

- A custom domain adapter must compute every final label: `CORE_BOOKKEEPING_ONLY`.
- Core cannot describe both systems without bespoke terminal-class rules:
  `NO_SHARED_MECHANISM`.
- Qualified-source UNKNOWN coerced into evidence of rejection/permission:
  `UNSOUND_INFORMATION_BOUNDARY`.
- A certificate lacks auditable source provenance or native validity:
  `UNVERIFIED_SOURCE_CERTIFICATE`.
- Classical quotient yields the same classes (expected), and fully
  informed B9 achieves equal cost/coverage/certification:
  `B9_TIE_NO_INDEPENDENT_VALUE`.
- New behavior is established only with previously scored R2 carriers:
  `DEVELOPMENT_ONLY_NOT_PROSPECTIVE_TRANSFER`.

Until all necessary gates pass, **DO NOT** rewrite the main KBS
contribution as a new generic quotient/uncertainty algorithm.
