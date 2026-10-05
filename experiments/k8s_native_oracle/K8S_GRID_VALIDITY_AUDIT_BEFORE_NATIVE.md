# Kubernetes frozen-grid validity audit — before native combinatorial execution

This audit is frozen **after** the semantic prediction file was committed but **before** the combinatorial native grid is executed.

## Frozen inputs

- `K8S_FROZEN_MAPPING.md`
- `K8S_GRID_PREDICTIONS_BEFORE_NATIVE.json`

The prediction file is not edited by this audit.

## Native-schema exclusion rule

Kubernetes defines the container-level `restartPolicy` field on an init container such that, when specified, the only valid value is `Always`. Therefore GCS Fuse grid rows with:

- `sidecar == true`, and
- `restart == "Never"`

are outside the valid native Pod schema. A rejection of such a row cannot be attributed to the target VAP and must not be scored as EEQ/VAP recovery.

These rows are frozen as:

`PREEXCLUDED_NATIVE_SCHEMA_INVALID`

before native combinatorial execution.

## Counts

- Flux frozen rows: 10; all 10 eligible.
- GCS Fuse frozen rows: 20.
- GCS Fuse pre-excluded native-schema-invalid rows: 6.
- GCS Fuse eligible target rows: 14.
- Total eligible native grid: **24**.
- Total pre-excluded rows retained in the ledger: **6**.

## Oracle attribution

For an eligible row:
- `ACCEPT` means kube-apiserver admits the server-side dry-run request.
- `REJECT` counts only when stderr contains the exact target-policy message.
- Any other native rejection is `NATIVE_ORACLE_AMBIGUOUS`, never a pass.

Flux target message:
`pods in tenant namespaces cannot run under the 'flux' ServiceAccount`

GCS Fuse target messages:
- `the native gcsfuse sidecar init container must have restartPolicy:Always.`
- `the native gcsfuse sidecar init container must have env var NATIVE_SIDECAR with value TRUE.`

No row is dropped after observing its native action.
