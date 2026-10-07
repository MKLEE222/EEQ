# Kubernetes Volcano development-environment mapping — frozen before native execution

Protocol parent: parityplus/g4/FREEZE_MANIFEST.md at commit c15b212ad0c2be3856a03d38802aaffa628aefd1.

This is an ADAPTER_INSTANCE_EXTENSION under the frozen V0+C1-C3 schema. It does not change the schema or core semantics.

## Public source

- Repository: volcano-sh/volcano
- Pinned repository commit: e0905bab6fe49b5df2948edb001703c523525784
- Path: installer/helm/chart/volcano/policy/pods-validating.yaml
- Git blob SHA: 435232ea78684f2406a0b20e577ef8ffd8dd12aa
- Evidence class: PUBLIC_MAINTAINED_CONFIG_NATIVE_REPLAY

The native workflow must download this exact path at the pinned commit and verify that `git hash-object` of the downloaded bytes equals the blob SHA above before applying it.

## Frozen native semantics

The source ValidatingAdmissionPolicy applies to Pod CREATE requests.

Let:
- `V`: `spec.schedulerName == "volcano"`;
- `m`: annotation `volcano.sh/jdb-min-available`, if present;
- `x`: annotation `volcano.sh/jdb-max-unavailable`, if present.

For a non-Volcano Pod (`V=false`) every registered row is predicted ACCEPT because every validation is guarded by `!variables.volcanoScheduler`.

For a Volcano Pod:
1. if both annotations are present => REJECT ("not allow configure multiple annotations at same time");
2. if only `m` is present, ACCEPT iff it is either a positive decimal integer or a percentage from 1% through 99%;
3. if only `x` is present, the same value predicate applies;
4. if neither is present => ACCEPT.

Registered annotation states are:
- absent
- `1` (valid integer)
- `25%` (valid percentage)
- `0` (invalid zero)
- `100%` (invalid percentage boundary)
- `abc` (invalid lexical form)

Registered scheduler states:
- `volcano`
- `default-scheduler`

This yields 2 x 6 x 6 = **72 preregistered semantic cases**. All values are legal Kubernetes annotation strings and no case is pre-excluded by construction.

## V0 + C1-C3

V0: only the public policy bytes, submitted Pod fields, and native kube-apiserver response are used. Native outcome labels are not adapter inputs.

C1 support coverage: within the registered contract, the single installed Volcano Pod VAP/binding is the complete target mechanism. A rejection is scored as target-policy REJECT only if stderr contains one of the exact Volcano policy messages; any other native rejection is NATIVE_ORACLE_AMBIGUOUS.

C2 qualification fidelity: policy applicability is the registered Pod CREATE resource scope plus scheduler qualification `schedulerName == "volcano"`. Non-Volcano scheduler rows are explicit negative controls.

C3 transition/objective fidelity: action is Pod CREATE; continuation horizon is one step; native action vocabulary is ACCEPT/REJECT. The submitted object contains the two registered annotations and scheduler state.

## Frozen negative controls

- non-Volcano scheduler with otherwise invalid annotation values => ACCEPT;
- Volcano scheduler with neither annotation => ACCEPT;
- valid single min/max annotation => ACCEPT.

No prediction file may be edited after native execution begins.
