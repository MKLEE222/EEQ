# R3-M3 C1 SOURCE-INVENTORY ADVERSARY — PRE-SOURCE/PRE-NATIVE FREEZE

Date: 2026-10-10 (Asia/Shanghai).
Status: REGISTRY FROZEN BEFORE M3 SOURCE GENERATOR, NEW THIRD POLICY/BINDING
SOURCE BYTES, OR NEW NATIVE KUBERNETES RESULTS.
Base: eeq-r3-m2-partial-knowledge-20261010 @
7bd0e92dbbdd3cd462fc3ca5880c9402e36c1ba3.
Prior unrelated R4-C0 cross-family certificates 16/16 DEV (GitHub Actions
37915644281) are referenced as already scored, NOT reproduced here.

## Scientific mother problem and strongest originality attack

M2 retrospective 96 partial-information mask predictions showed
40 conditionally sound decisions, 56 REFUSE, zero bounded-world false
accepts, and full B9 parity. Its positive ACCEPT witness depends on
a *researcher-authored, supposedly complete fresh support inventory*.
A third previously unobserved policy/binding may invalidate an ACCEPT
without changing any of the TWO previously cached policy/binding bytes.

M3 aims to kill the proposition:
 "unchanged hashes of all previously known valid decision-support
 sources imply a previously ACCEPT decision is still safe."
Construct and score ONE native external-inventory change with unchanged
cached sources, and pressure the ability to *detect/revalidate* the
formerly absent additional source.

Do NOT claim the result as a novel incremental/provenance algorithm.
Full B9 gets the complete lawful source and membership history, and may
use list/watch and conditional certificates like EEQ. D0 and M2 do
not score new method advantage; only this scientific prerequisite.

## Existing immutable source inputs

Reuse EXACT historical M1 source files, all unchanged, from:
  experiments/native_distinction_relaunch/r3_m1/sources/policy.json
  experiments/native_distinction_relaunch/r3_m1/sources/binding-team.json
  experiments/native_distinction_relaunch/r3_m1/sources/binding-mode.json
  experiments/native_distinction_relaunch/r3_m1/sources/namespace.json
  experiments/native_distinction_relaunch/r3_m1/sources/pod-flux.json
  experiments/native_distinction_relaunch/r3_m1/sources/pod-default.json.
Never use old native labels or historical M2 model predictions when
generating new source-only M3 labels.

EXACT new third source files, to be committed AFTER this freeze:
  experiments/native_distinction_relaunch/r3_m3/sources/policy-third.json
  experiments/native_distinction_relaunch/r3_m3/sources/binding-third.json.

Third policy metadata.name = eeq-r3-m3-default-deny;
  admissionregistration.k8s.io/v1 ValidatingAdmissionPolicy,
  failurePolicy Fail, matchConstraints Pod CREATE core/v1,
  ONE validation CEL:
  object.spec.serviceAccountName != 'default'
  message=EEQ_R3_M3_DEFAULT_SA_DENIED; reason=Forbidden.
Third binding metadata.name=eeq-r3-m3-binding-third,
  admissionregistration.k8s.io/v1 ValidatingAdmissionPolicyBinding,
  policyName=eeq-r3-m3-default-deny, validationActions=[Deny],
  matchResources.namespaceSelector.matchLabels={'r3.team':'tenant'}.

Existing policy rejects flux; its two bindings select labels
r3.team=tenant and r3.mode=strict; source namespace eeq-r3 initially
has these two labels, so flux REJECT and default ACCEPT before M3.

NO other VAP/binding is intentionally added. Real clusters may still
have unrelated admission mechanisms; all claims are scoped only to the
registered VAP / binding deny effects. No evidence of global Kubernetes
admission mechanism completeness or external authoritative closure.

## Prospective native phases, exact observations and mutations

ONE clean kind v0.31.0 Kubernetes v1.35.0 cluster using frozen
kindest/node:v1.35.0@sha256:
452d707d4862f52530247495d180205e029056831160e22870e37e3f6c1ac31f.
kubectl v1.35.0, Ubuntu 24.04, Python 3.11.
No other cluster from old scored M1, no production credentials.

BEFORE scoring, create namespace and serviceAccounts, check no M3 source
objects; two unbound Pod server-dry-run CREATE controls:
 flux=ACCEPT, default=ACCEPT. They are NOT primary rows.

Apply M1 original policy and BOTH M1 bindings; fixed 10-second
activation. Then for each of FOUR phases, take a fresh native
LIST of all ValidatingAdmissionPolicy AND all
ValidatingAdmissionPolicyBinding objects (unfiltered namespaces),
including list metadata.resourceVersion, each item's name, UID,
resourceVersion and full policy/binding spec hash. Record original
two binding individual UID/spec unchanged across all four phases;
do not parse or compare resourceVersion as numeric (opaque string).

Exactly four phase names (each with EXACT TWO Pod probes):
  T0_OLD_TWO_BINDINGS: old policy + TEAM & MODE bindings;
  T1_THIRD_POLICY_UNBOUND: native API CREATE third policy, NO third
    binding yet; old 2 bindings unchanged;
  T2_THIRD_BINDING_ACTIVE: native API CREATE third binding to third
    policy, selector matches namespace; old 2 bindings unchanged;
  T3_THIRD_BINDING_REMOVED: native API DELETE ONLY third binding;
    policy remains installed, old 2 bindings unchanged.

Native action set EXACT:
 - CREATE_3RD_VAP (source policy-third.json) exactly once;
 - CREATE_3RD_BINDING (source binding-third.json) exactly once;
 - DELETE_3RD_BINDING exactly once.
Use separate CLI API requests; verify each actual CREATE/DELETE
inventory membership change by native LIST; record operation exit code.
Fixed 10 seconds after original setup and 8 seconds after each of the
three subsequent membership mutation actions. NO outcome-dependent retry.

Two original IDENTICAL byte-for-byte Pod sources for each phase:
  P_flux (serviceAccountName='flux');
  P_default (serviceAccountName='default').
Only server-side dry-run CREATE, no Pod persisted.

SOURCE-ONLY labels frozen BEFORE first cluster:
  T0: flux REJECT by original VAP; default ACCEPT;
  T1: flux REJECT by original VAP; default ACCEPT;
  T2: flux REJECT by original VAP; default REJECT by THIRD VAP;
  T3: flux REJECT by original VAP; default ACCEPT.
Full denominator: 4 phases x 2 Pod probes = EXACT **8** primary native
observations; PLUS 2 no-binding controls and 3 membership mutation
certificates, 4 full native policy/binding inventory snapshots.
No missing/failed case may be silently censored.

Reject credit requires the registered policy's exact identifiable error:
  flux: EEQ_R3_FLUX_SA_DENIED / eeq-r3-flux-deny
  default: EEQ_R3_M3_DEFAULT_SA_DENIED / eeq-r3-m3-default-deny.
Unrelated native errors are AMBIGUOUS, not REJECT.

## Primary mechanism pressure / predeclared comparisons

- Cached original source-digest set remains exactly the same for
  old VAP + both original bindings + namespace + Pod sources;
  after T2 additional effective source membership changes, and previously
  cached scoped ACCEPT(default) is no longer supportable.
- A source-only old-two-source/inventory-ignoring ablation predicts
  7/8 across registered native phases; must be called WEAK diagnostic.
- An independently allowed and *fully informed* B9 with both original
  and new VAP/binding sources, native LIST snapshots, real actions
  and source-scoped CEL/selector semantics can obtain 8/8, matched
  safe decision coverage and same invalidation decision.
- Scoped registry-aware EEQ candidate also should score 8/8, but no
  independent superiority if B9 ties.
- The new third policy ALONE, without binding, is inert for the probes.
- Deleting third binding restores positive default Pod admission,
  with the third policy still present.
- A known currently qualified original flux DENY witness remains
  sound across all phases under additive deny semantics.
- Old (two-binding) ACCEPT certificate must be invalidated or REFUSE
  after third binding is added until additional source is evaluated.
  Source bytes alone cannot prove nonexistence of new support sources.

## Inventory authorization, temporal validity and C1 restrictions

The LIST metadata.resourceVersion is an *API-server authenticated,
readable collection snapshot under current client privileges*, but:
- it is not a signed global completeness proof across all Kubernetes
  admission types or arbitrary future times;
- separate VAP-policy and VAP-binding LIST calls are NOT claimed as
  an atomic cross-resource snapshot;
- a finite before/after LIST pair is NOT continuous watch custody;
- a LIST from a different actor with restricted RBAC is not globally
  conclusive, and watch compaction/410 breaks continuity;
- no full G4 C1 for all future actions is established.

Unless freshness/authority and exclusion of other admissible denial
sources are independently established for the specific bounded contract,
ACCEPT is conditional or REFUSE. Preserve any surprising native
timing/propagation observation as a scientific failure, never retry to
achieve preferred decisions.

## Stage boundaries and scoring chronology

1. Commit this PRE-SOURCE freeze first.
2. Commit exactly two M3 source files plus whitelisted source-only
   decision and inventory-membership model. NO native label imports.
3. Run source-only tests and retain SHA256 source manifest + predicted
   complete 8 rows in a frozen Actions artifact.
4. Independently reopen the source artifact and lock both outer ZIP
   and manifest/prediction SHA256 plus exact native/scorer code Git blobs
   in a *final prescore manifest* before FIRST new Kind creation.
5. Native runner must receive only original source files and
   manifest, not predictor outputs; save RAW observations, all list
   snapshots and 3 real action certificates before join scoring.
6. Join-only scorer matches all 8 raw cases, controls, inventory
   membership/UID/spec, both denial attributions and source hashes.
7. Publish negative, infra, ambiguous statuses with full denominator;
   do not modify any frozen source or method code to rescue results.

Synthesize no new original G5 score; G5=285 frozen, G4/B10/holdouts
unchanged. Native controlled carrier is DEVELOPMENT only.

If all passes:
  R3_M3_CONTROLLED_NATIVE_STALE_ACCEPT_INVENTORY_COLLISION_B9_TIE,
  *NOT* C1_GLOBAL_COMPLETE, *NOT* EEQ_NEW_ALGORITHM,
  *NOT* R4_P3_ADVANTAGE.

Novelty reduction threats MUST remain:
possible-world certain answers, XACML Indeterminate,
database provenance, incremental maintenance and standard list/watch.
If B9 or these known techniques can simulate, score B9_TIE. No
"until success" outcome-driven protocol changes are allowed.
