# G5 breadth audit — conservative completion count

Date: 2026-10-07

Protocol authority:
- original parity+ completion line: 4 native families; >=8 independent
  environments; >=6 production histories; >=250 deduplicated semantic
  transitions/cases;
- G4 case/counting discipline:
  `parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md` at
  `c15b212ad0c2be3856a03d38802aaffa628aefd1`.

This audit intentionally uses conservative denominators. Software-version
replications never create new environments or semantic cases. Public maintained
configuration replay is not counted as a production history.

## Counting rules

### Native family

A native family is a distinct native decision system with its own native
oracle/action semantics. Method success is not required for a family to exist;
a retained C1/C2/C3 failure remains evidence about that native family.

### Independent environment

An independent environment is a distinct source/contract execution context.
A mere client/server version rerun of the same source/contract context is not a
new environment.

### Production history

A production history is an independently maintained public historical stream
or time/version-ordered native source. Controlled-native grids and
`PUBLIC_MAINTAINED_CONFIG_NATIVE_REPLAY` are excluded from this denominator.

## Native families: 4 — PASS

1. APT release-info / Signed-By continuation.
2. Kubernetes admission-policy decision.
3. TUF root-update trust continuation.
4. GitHub repository-governance mergeability.

GitHub is retained as a native family even though family-complete C1 parity is
not established. Its C1 limitation belongs to G6/method coverage; it does not
erase the native oracle or production-history evidence.

## Independent environments: 12 — PASS

No version replication is counted separately.

### APT — 3

1. `apt-3.0.3-exhaustive` controlled native finite carrier.
2. Debian stable signed production-snapshot replay.
3. Ubuntu noble-updates signed production-snapshot replay.

The Debian/Ubuntu replay workflow completed both jobs successfully in Actions
run `37256382052`.

### Kubernetes — 4

4. Flux public VAP/binding from `fluxcd/flux2-multi-tenancy`.
5. GCS Fuse public VAP from `GoogleCloudPlatform/gcs-fuse-csi-driver`.
6. Volcano public VAP from `volcano-sh/volcano`.
7. 5-Spot public VAP/binding from `finos/5-spot`.

Kubernetes v1.34.3 and v1.35.0 executions of the same 5-Spot source/contract
count as robustness/version replication, not two environments.

### TUF — 1

8. Bottlerocket `aws-k8s-1.35/x86_64` production root history, roots 1..8.

### GitHub governance — 4

9. `nodejs/node`.
10. `microsoft/vscode`.
11. `home-assistant/core`.
12. `llvm/llvm-project`.

The two mechanical samples are replications/sampling waves inside these four
environments, not eight environments.

## Public production histories: 7 — PASS

The conservative production-history denominator is:

1. Debian stable signed snapshot sequence used by APT production replay.
2. Ubuntu noble-updates signed snapshot sequence used by APT production replay.
3. Bottlerocket production root sequence 1..8.
4. `nodejs/node` public PR/governance history.
5. `microsoft/vscode` public PR/governance history.
6. `home-assistant/core` public PR/governance history.
7. `llvm/llvm-project` public PR/governance history.

Excluded deliberately:
- APT exhaustive controlled grid;
- Flux/GCS Fuse/Volcano/5-Spot public maintained configuration replay;
- software-version replication;
- retry/polling/sampling-wave multiplicity.

## Deduplicated semantic native cases: 285 — PASS

G5 artifact:
- workflow run `37565829286`;
- artifact `11458960196`;
- ZIP SHA256
  `687ee21b30c53aa8b78d888060099211f56ca7a86e5d7341e0d65ed0bce4b265`.

Unique scored semantic cases:

- APT: 144;
- K8s Flux: 10;
- K8s GCS Fuse: 14;
- K8s Volcano: 72;
- K8s 5-Spot: 38;
- TUF Bottlerocket root: 7;
- total: **285**.

GitHub contributes zero semantic cases to this denominator because its frozen
v1 family-complete C1 coverage/equivalence requirement is not closed.

## G5 disposition

[
4\;\text{native families},\quad
12\;\text{independent environments},\quad
7\;\text{production histories},\quad
285\;\text{deduplicated semantic cases}.
]

Therefore **G5 breadth = PASS** under the conservative counting rules above.

This does not close G6 and does not authorize a journal-strength conclusion.
The fifth-family holdout remains unopened until G6 closes.
