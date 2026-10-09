# R2A-v1 — K8s Native Dynamic Binding-Qualification Split: PRE-SOURCE FREEZE

Date: 2026-10-09
Evidence class: CONTROLLED_NATIVE_DYNAMIC_KUBERNETES.
Research status: PRE-SOURCE, PRE-NATIVE, NO RESULT.
Base contains independent TUF R2B verified B-only result, which remains
separate from this Kubernetes A-only development experiment.

## Scientific question and exact A contrast

Can two genuine Kubernetes ValidatingAdmissionPolicyBinding configurations
produce IDENTICAL registered current Pod admission decisions, but DIFFERENT
registered admission decisions after the SAME lawful native namespace-label
update?

The distinguishing lawful evidence is the namespace-selector qualification
predicate in the binding. The native ACTION is a real API-server namespace
label change, not a synthetic successor pointer or a separately selected
static admission record.

All current/future claim scope is explicitly registered before looking at
native outcomes. This is not a general K8s all-actions equivalence test.
It is a strictly registered current Pod-CREATE decision family (two Pod
requests) and one future namespace UPDATE followed by the same two Pod
requests.

## Fixed native environments

Primary: kind v0.31.0, binary SHA256
eb244cbafcc157dff60cf68693c14c9a75c4e6e6fedaf9cd71c58117cb93e3fa.
Kubernetes v1.35.0, node image
kindest/node:v1.35.0@sha256:452d707d4862f52530247495d180205e029056831160e22870e37e3f6c1ac31f.
kubectl client from matching v1.35.0 release; SHA checksum validated from
official dl.k8s.io v1.35.0 release endpoint before installation.
Runner: ubuntu-24.04, Python 3.11, no custom admission webhook/controller.

Branch H_A and H_B MUST be executed in TWO CLEAN kind clusters, in
deterministic A-then-B order, with identical kube-server binaries, same
namespace name, same Pod bytes and same label-update action. No binding
carryover or cross-branch cluster state.

## Exact source policy and two alternative binding histories

One Kubernetes admissionregistration.k8s.io/v1
ValidatingAdmissionPolicy:
  name: eeq-r2a-flux-deny
  failurePolicy: Fail
  matchConstraints: Pod CREATE, core/v1
  validation CEL: object.spec.serviceAccountName != 'flux'
  message: EEQ_R2A_FLUX_SA_DENIED
  reason: Forbidden.

Only one ValidatingAdmissionPolicyBinding installed per native cluster:
  name eeq-r2a-binding-a (H_A), or eeq-r2a-binding-b (H_B);
  policyName eeq-r2a-flux-deny;
  validationActions = [Deny];
  matchResources.namespaceSelector.matchLabels:
    H_A = {'r2a.team': 'tenant'}
    H_B = {'r2a.team': 'tenant', 'r2a.mode': 'strict'}.

Common namespace JSON source:
  name=eeq-r2a,
  labels BEFORE: r2a.team=tenant, r2a.mode=strict;
  labels AFTER:  r2a.team=tenant, r2a.mode=relaxed.

The registered future action for EACH branch is exactly:
  kubectl label namespace eeq-r2a r2a.mode=relaxed --overwrite
executed ONCE after current Pod probes; show native namespace
resourceVersion and labels before/after. No Pod is actually persisted.

Two registered server-side dry-run Pod CREATE probes:
  P_flux: serviceAccountName='flux'
  P_default: serviceAccountName='default'
with identical immutable safe Pod objects across H_A/H_B and before/after.
Create native service accounts flux and default (default automatic or
explicitly confirmed) before probes, avoiding unrelated admission failures.

## Pre-native source-derived predictions (all eight main native rows)

At CURRENT namespace labels (strict):
 H_A P_flux = REJECT, H_A P_default = ACCEPT.
 H_B P_flux = REJECT, H_B P_default = ACCEPT.
--> both histories have identical COMPLETE registered current decision vector.

After actual label action (relaxed):
 H_A P_flux = REJECT, H_A P_default = ACCEPT.
 H_B P_flux = ACCEPT, H_B P_default = ACCEPT.
--> H_A and H_B diverge on P_flux; this is the intended future
separating witness (UPDATE_NAMESPACE_LABEL, then P_flux CREATE).

The pre-score source-only extractor must read the literal JSON policy,
binding and namespace bytes, compile only a REGISTERED whitelist of CEL
syntax, selector conjunction, Pod CREATE scope and Deny; if any material
mechanism unsupported, output MODEL_UNSUPPORTED, not fabricated labels.
Compute successor namespace source labels by the frozen update command.
Native labels never become extractor inputs.

Additional independent controls (not counted in main eight):
  no VAP/BINDING installed -> both registered Pod CREATE probes ACCEPT
  in each clean cluster (4 native controls total).
These confirm other active admission controls are not responsible for the
critical scoped REJECT. Native target rejection must be attributed by
exact message/policy name; unrelated failures are
NATIVE_ORACLE_AMBIGUOUS and not scored as matched REJECT.

## Scoring units, oracle separation and constraints

Primary experimental domain: two binding histories x two phases
(before, after native namespace action) x two Pod probes = **8** main
native result rows, all counted. Plus **4** unbound native controls
and **2** actual native label updates (one per independent cluster).

Do not collapse repeated probes, change namespace/probe names, or
postselect successful timing windows. After creating policy/binding,
wait a fixed registered 10 seconds; before/after actions each sampled
ONCE. Native source resourceVersion and bindings must be preserved.

Record source SHA256/bytes for every policy, binding, Pod, namespace
source and transition descriptor. The source-only predictions artifact
outer ZIP and inner manifest/prediction SHA256, source generator Git
blobs, native runner and join-only scorer Git blobs MUST be frozen in
a SECOND manifest before first kind cluster creation.

Use source-only strong B9 that sees FULL two selectors, actual labels,
pod serviceAccountName and policy predicate; it is allowed to obtain
8/8. Also compare a deliberately *insufficient* label-only baseline
as a mechanism diagnostic, not as the strong B9. A success under these
conditions is an R2A NATIVE NECESSARY DISTINCTION, not proof of EEQ novelty.

## Native and future-subject boundaries

- Namespace update must be genuinely carried out by Kubernetes API.
- Future challenge is native Pod server-dry-run CREATE; not stored Pod.
- A pair differs in real binding selector semantics, even if current
  output vector coincides. No claim of equivalence under other cluster
  operations or unlimited future steps.
- One policy/binding, one namespace/label action, two registered Pod
  challenges. C1/C2/C3 completeness limited to this registered carrier.
- All synthetic inference work is SOURCE-ONLY and all native labels are
  produced after prediction freeze.
- No original G4, G5, B10, or prior historical holdout scores affected.

## Kill and interpretation

No native current-equivalence -> A_CURRENT_EQUIVALENCE_FAILURE.
No verified native namespace state mutation -> A_NO_REAL_TRANSITION.
No native future divergence with attributable target policy -> A_SPLIT_FAILURE.
Any input/config/actor ambiguity -> A_INADMISSIBLE_OR_AMBIGUOUS.
An otherwise correctly predicted A pair does not establish superiority:
strong B9 and a classical state/source-aware model can represent the
same binding selector and should be allowed to do so.

Even if this A experiment passes, R2 global bidirectional claim requires
the actual scope/family caveats: TUF B was a different controlled native
system, not A and B in EACH family. Cross-family mechanism generality
requires separate replication, new protocols and R4 advantage evidence.
