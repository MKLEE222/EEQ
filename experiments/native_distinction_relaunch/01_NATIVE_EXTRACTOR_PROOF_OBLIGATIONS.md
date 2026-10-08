# R1 — Label-Blind Native Transition Extractor: Proof Obligations

Date: 2026-10-08
Status: REQUIREMENTS FREEZE / SPECIFICATION ONLY.
No native outcome is scored; no new extractor implementation is certified.

## 1. Input, output and authority boundary

Input (all obtainable at decision time):
- pinned native software, native oracle interface and immutable source bytes;
- source inventory with identity, provenance, acquisition success/failure and
  explicit COMPLETE / PARTIAL / UNAVAILABLE coverage status;
- registered claim family J, actor/authority context, action alphabet A,
  continuation/allowance contracts and finite horizon r;
- native mechanism specification sufficient to derive next evidence states
  from each registered action without looking up target native labels.

Output:
- normalized lawful evidence state s, including source identity,
  authentication, authorization, qualification and claim bindings;
- each action's source and authority effects, including successor evidence
  state, continuation predicates, or explicit UNSUPPORTED outcome;
- the registered finite reachable domain, its completeness status and a
  machine-checkable provenance map back to exact source bytes/rules;
- a source/transition/claim coverage certificate with unresolved obligations;
- an interface for a SEPARATE native oracle to test case actions later.

The extractor must never consume:
native_action, native_label, expected_native_action, oracle verdict,
mergeable_state, final verification status, or outcome-derived case selection.

Do not use names alone for leakage avoidance: static dependency inspection
plus a negative perturbation test must check that changing native outcomes
cannot change any extracted state/edge/predicate.

## 2. Validity of a complete finite abstraction

The current quotient-v2 implementation assumes a total deterministic finite
transition system. A native lift is admitted only when an explicit mapping

  T(s,a) = s'

is derived for every registered reachable state s and registered action a,
with a source/rule certificate, and all s' remain inside the registered
finite state universe.

Important failure cases:
- only having action-parameter objects or symbolic successor descriptions
  is NOT a total next-semantic-state-ID graph;
- the system has asynchronous/multiple possible successors -> do NOT choose
  one silently; record NONDETERMINISTIC_NATIVE_SEMANTICS, or construct a
  separately preregistered set-valued semantics with new correctness proof;
- native sources are partial/unreadable -> no graph completeness claim;
- source state after action is unknown -> UNSUPPORTED_TRANSITION,
  not deterministic REFUSE or arbitrary REJECT;
- post-action evidence visibility may differ from present visibility;
  the pre-native extractor cannot peek at later observations.
- stored source IDs can legitimately differ even when decisions are
  equivalent; graph compilation must preserve identity for audit challenges.

Only the **registered domain** can be claimed complete. Do not claim
completeness for an entire unbounded platform based on a finite carrier.

## 3. Independent obligations

C0 / Lawfulness:
Each feature has a source pointer, timestamp/validity boundary and
decision-time availability explanation. No future info or scored verdicts.

C1 / Coverage:
All mechanisms compatible with each registered claim must either be
enumerated or explicitly unresolved. Negative evidence about a source is
not inferred from lack of API access; permission failure is UNKNOWN.

C2 / Qualification:
For every support path, source authentication, authorization, expiration,
revocation, relevant identity, actor qualification and claim binding are
distinct fields unless the native semantics demonstrably equates them.
A qualified witness has an explicit chain to its original source rule.

C3 / Transition:
Each registered action has a declared precondition, lawful source/authority
transformation, successor-state pointer(s), and continuation task. If there
are unregistered effects relevant to future registered decisions, mark C3
UNSUPPORTED; do not ignore them. Total closure is separately audited.

C4 / Decision conservativeness:
Use three distinct outcomes at evaluation boundaries:
  ACCEPT: registered native claim is independently established;
  REJECT: available, complete registered evidence establishes prohibition
          under the frozen mechanism;
  REFUSE: insufficient or unknown evidence prevents either conclusion.
Additionally use a META-status, UNSUPPORTED_MODEL, when the contract or
transition semantics itself is not covered. This is not an ordinary
native action label.

C5 / Soundness:
Exact separation certificates include starting source identities,
registered contract, action word (length <= r), intermediate source changes,
and two distinct future native outcomes. Certificates are checked by native
execution on independent histories, not by reading the model's own label.

C6 / Merge legality:
For contract family J and horizon r, an equivalence-class merge must preserve
the **complete registered decision/continuation trace**, not just the
present native action. Every distinct class pair requires a separating
trace inside the finite model; selected nontrivial pairs also require
native validation. A quotient/minimum-state result is RELATIVE TO J,r,
not universal across all possible future claims.

C7 / Auditing and costs:
The provenance map and legality certificate have measured bytes and
verification time. Codebook/table, class assignment IDs and retained
source evidence are all charged. Source fetch, parsing, normalization,
native calls, compilation, lookup and RSS are disaggregated.

## 4. TUF R1 candidate — development feasibility only

Known pinned reference:
- source inventory: experiments/bottlerocket/FROZEN_SOURCE_INVENTORY.md;
- public Bottlerocket roots 1..8 (aws-k8s-1.35/x86_64);
- native operation previously studied: tuf-js@3.0.1
  TrustedMetadataStore.updateRoot;
- public historical root1->root8 successful chain plus separately frozen
  controlled-native corruption/replay calibrations.

These are KNOWN development data, not a new holdout and not fresh native
predictions. R1 may use their public bytes and documented mechanism to
test whether the extraction contract can be met without consulting
archived native labels.

Before any fresh R2 native invocation, a DIFFERENT experiment freeze must
pin, at minimum:
1. native binary/package hash and dependency lock;
2. exact root inputs or deterministic, auditable controlled signing
   procedure, including source/provenance class;
3. registered trust source and root-key role threshold semantics;
4. accepted action vocabulary, signed/unsigned metadata and qualifications;
5. exact reachable native histories and time constraints;
6. C1/C2/C3 model generator source-code Git blob;
7. pre-score challenges, paired trajectories, exclusion semantics and
   predicted native responses;
8. B9 design, cost rule and leakage audit;
9. independent verifier interface and declared repetitions.

Important TUF limit: root1..8 are all accepted production transitions.
They are evidence of a real native trust chain, not yet a proof of A/B
bidirectional native contrasts or multi-source generalization.

## 5. Kubernetes R3 candidate — no automatic enrollment

Native evolution of policies/bindings and admission history might support
multi-source, actor, and claim-specific continuation. It is admissible only
when the registered actions genuinely evolve policy/binding state, and the
next native observable source state is lawfully captured. A static Pod
admission grid with altered attributes is not, by itself, a general
policy-transition graph.

If the policy admission semantics / cluster API version/identity are not
fully captured, classify R3_UNSUPPORTED, not "N/A passed".

## 6. Anti-shortcuts that invalidate the evidence

- Manually scripting a desired seven-state graph and calling it native.
- Filling missing source rules by reading past oracle verdicts.
- Replacing unavailable approved reviewer permissions by FALSE.
- Treating every native error as clean REJECT.
- Counting cosmetic re-serialization as semantic quotient compression.
- Comparing quotient IDs without paying for the transition codebook.
- Giving B9 less provenance or weaker future action semantics than B10.
- Training the decoder on the exact native outputs whose fidelity is claimed
  as prospective generalization.
- Modifying G4 or reopening previously observed X.509/in-toto as a v2 holdout.

## 7. Kill gate and exit artifact

R1 can advance to R2 only with:
- an output-independent extractor implementation pinned by Git blob;
- at least one native registered carrier with a complete, finite action graph
  and the exact claimed source inventory/qualification fields, OR a precisely
  bounded partial model whose unsupported transitions explicitly prevent
  whole-graph quotient claims;
- a direct source/transition audit against the documented native mechanism,
  performed without native outcome labels;
- a self-contained counterexample test detecting unknown/incomplete effects;
- an explicit no-leakage audit.

Current status: R1_SPEC_ONLY; ALL proof obligations OPEN.
