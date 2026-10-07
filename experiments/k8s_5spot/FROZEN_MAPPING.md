# Kubernetes 5-Spot development carrier — frozen semantic mapping

Protocol parent: `parityplus/g4/FREEZE_MANIFEST.md` at commit
`c15b212ad0c2be3856a03d38802aaffa628aefd1`.

Status: development-family adapter-instance extension. This does not alter the
G4 schema, V0+C1-C3 interface, case definition, scoring, failure taxonomy, or
fifth-family holdout. The fifth-family holdout remains unopened.

## Public maintained source

Repository: `finos/5-spot`

Pinned upstream commit:
`4d14866b5b0b9de5b4b6bb6e264303e22b5cfd98`

Policy:
`deploy/admission/agent-pod-security-policy.yaml`

Git blob SHA:
`a8dc90c393d7355c7633c6f5be2e37aa0639e244`

Binding:
`deploy/admission/agent-pod-security-binding.yaml`

Git blob SHA:
`54c4bfc4a74da27b19d4eec1211026039706f3ad`

Evidence class:
`PUBLIC_MAINTAINED_CONFIG_NATIVE_REPLAY`.

The native runner must download the exact two upstream files at the pinned
commit and verify their Git blob SHA values before applying them.

## Registered native contract

The public binding scopes the policy to namespace label
`kubernetes.io/metadata.name=5spot-system` and enforces `Deny`.

The registered action is Pod `CREATE`. The native action vocabulary is
`ACCEPT/REJECT`.

The registered identities are:

- `default`
- `5spot-kata-config-agent`
- `5spot-reclaim-agent`

The two agent service accounts are created only to instantiate the public
policy's documented identities; their names come directly from the pinned
policy.

Every test Pod uses a safe common base:
- one `registry.k8s.io/pause:3.10` container;
- pod-level `seccompProfile.type=RuntimeDefault`;
- container `readOnlyRootFilesystem=true`;
- no risky field unless the registered profile below adds it.

This base is selected before native execution to avoid unrelated validation
failures and to satisfy the public policy's mandatory agent seccomp mitigation.

## Frozen scoped semantic grid

For the `5spot-system` namespace, cross the three registered identities with
the following eleven profiles:

1. `baseline`: no risky field.
2. `host_network`: `hostNetwork=true`.
3. `host_ipc`: `hostIPC=true`.
4. `host_pid`: `hostPID=true`.
5. `privileged_ro`: container `privileged=true`, retain
   `readOnlyRootFilesystem=true`.
6. `privileged_rw`: container `privileged=true`,
   `readOnlyRootFilesystem=false`.
7. `hostpath_root`: hostPath `/`.
8. `hostpath_proc`: hostPath `/proc`.
9. `cap_net_admin`: add Linux capability `NET_ADMIN`.
10. `cap_sys_admin`: add Linux capability `SYS_ADMIN`.
11. `run_as_root`: pod-level `runAsUser=0`.

This yields 33 scoped semantic cases.

Frozen expected actions in `5spot-system`:

| profile | default | kata agent | reclaim agent |
|---|---|---|---|
| baseline | ACCEPT | ACCEPT | ACCEPT |
| host_network | REJECT | REJECT | REJECT |
| host_ipc | REJECT | REJECT | REJECT |
| host_pid | REJECT | ACCEPT | ACCEPT |
| privileged_ro | REJECT | ACCEPT | REJECT |
| privileged_rw | REJECT | REJECT | REJECT |
| hostpath_root | REJECT | ACCEPT | REJECT |
| hostpath_proc | REJECT | REJECT | ACCEPT |
| cap_net_admin | REJECT | REJECT | ACCEPT |
| cap_sys_admin | REJECT | REJECT | REJECT |
| run_as_root | REJECT | ACCEPT | ACCEPT |

## Frozen scope negative controls

Create an additional namespace `eeq-5spot-unscoped`, which does not satisfy
the binding's namespace selector. With the `default` service account, the
following five profiles are explicit scope controls and are all predicted
`ACCEPT`:

- baseline
- host_network
- privileged_rw
- hostpath_root
- cap_sys_admin

These cases verify that changing a policy-readable object field outside the
qualified binding scope does not create a decision-relevant rejection.

Total frozen semantic cases:

[
33 + 5 = 38.
]

Kubernetes-version replications are executions only and never increase the
semantic-case count.

## V0 + C1-C3

V0: only the pinned public policy/binding, submitted Pod fields, namespace
labels, registered service-account identities, and native kube-apiserver
response are used. Native outcome labels are not adapter inputs.

C1 support coverage: within this carrier, the exact pinned
`5spot-agent-pod-security` VAP and binding are the registered target support.
A rejection is scored as target-policy REJECT only when the native API response
attributes the denial to this exact policy; any other rejection is
`NATIVE_ORACLE_AMBIGUOUS`.

C2 qualification fidelity: namespace binding scope and service-account identity
are explicit qualification dimensions. The unscoped namespace is a negative
qualification control.

C3 transition/objective fidelity: action is Pod CREATE; continuation horizon is
one admission step; the submitted Pod carries the registered security posture;
native vocabulary is ACCEPT/REJECT.

## Exclusion and failure discipline

No case may be deleted after native execution begins.

A case that is invalid under native Kubernetes schema is retained as
`PREEXCLUDED_NATIVE_SCHEMA_INVALID` only if the invalidity is detected before
scoring for that native version. A non-target admission rejection is
`NATIVE_ORACLE_AMBIGUOUS`, not a method mismatch. Infrastructure/source
failures remain nonscored under the G4 taxonomy.

No prediction file or mapping may be edited after native execution begins.
