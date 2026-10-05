# Kubernetes development-family mapping — frozen before combinatorial native grid

Scope: exact public VAP semantics already promoted at G4 freeze.
This is a **development-family mapping**, not the final GitHub holdout adapter.
Native action labels from the forthcoming combinatorial grid are not used below.

## Common action classes
- `ACCEPT`: native API-server dry-run admits the registered request.
- `REJECT`: native API-server dry-run rejects the request because the target VAP returns Deny.

Other rejection mechanisms are oracle contamination and classified `NATIVE_ORACLE_AMBIGUOUS` rather than target labels.

## Flux (`fluxcd/flux2-multi-tenancy`)

Source predicate, read directly from the public VAP/binding:

- policy resource scope: Pod CREATE/UPDATE;
- binding qualification: namespace has label key `toolkit.fluxcd.io/tenant` (value arbitrary);
- validation: `object.spec.serviceAccountName != 'flux'`;
- action: Deny/Audit, so failed validation is native `REJECT`.

Frozen decision semantics for the registered grid:

`REJECT iff operation in {CREATE,UPDATE} AND tenant-label-present AND serviceAccountName == 'flux'; otherwise ACCEPT.`

C1: single installed Flux VAP/binding is the complete target mechanism for registered cases; unrelated native admission failures are excluded by exact denial-message attribution.
C2: binding qualification is the namespace-label selector; the claim is whether the submitted Pod is permitted to run under the `flux` ServiceAccount in a tenant namespace.
C3: registered request action is CREATE/UPDATE; post-action observation is native admit/reject. Namespace-label removal is an explicit action that changes policy applicability without changing Pod bytes.

Predicted zero controls:
- non-tenant namespace + `flux` SA => ACCEPT;
- tenant namespace + any SA other than literal `flux` => ACCEPT.

## Google Cloud GCS Fuse CSI (`GoogleCloudPlatform/gcs-fuse-csi-driver`)

Pinned public policy semantics:

- resource scope: Pod CREATE;
- match condition 1: annotation `gke-gcsfuse/volumes == "true"`;
- match condition 2: init container named `gke-gcsfuse-sidecar` exists;
- validation 1: that sidecar has `restartPolicy == "Always"`;
- validation 2: its env contains `NATIVE_SIDECAR=TRUE`;
- action: Deny.

Frozen decision semantics for the registered grid:

`ACCEPT if annotation is absent OR sidecar is absent.`
Otherwise `ACCEPT iff restartPolicy == Always AND NATIVE_SIDECAR == TRUE`; else `REJECT`.

C1: the installed GCS Fuse VAP/binding is the complete target mechanism for the generated dry-run Pods; target rejection must match one of the two source policy messages.
C2: applicability/qualification is established jointly by the repository annotation and presence of the named native sidecar; an invalid-looking unscoped Pod is a negative control, not a qualified target.
C3: registered action is Pod CREATE; native admit/reject is observed by server-side dry-run.

Predicted zero controls:
- annotation absent => ACCEPT regardless of the sidecar validation fields;
- target annotation present but named sidecar absent => ACCEPT because the second match condition is false.

## No output leakage

The combinatorial-grid expected labels are generated only from the frozen predicates above. Grid prediction file and this mapping are SHA256-hashed before the native grid workflow is added or run.
