#!/usr/bin/env python3
import json, subprocess, sys, time, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRED = ROOT / "experiments/k8s_native_oracle/K8S_GRID_PREDICTIONS_BEFORE_NATIVE.json"
MAP = ROOT / "experiments/k8s_native_oracle/K8S_FROZEN_MAPPING.md"
AUDIT = ROOT / "experiments/k8s_native_oracle/K8S_GRID_VALIDITY_AUDIT_BEFORE_NATIVE.md"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "grid-results")
OUT.mkdir(parents=True, exist_ok=True)

FLUX_MSG = "pods in tenant namespaces cannot run under the 'flux' ServiceAccount"
GCS_MSGS = [
    "the native gcsfuse sidecar init container must have restartPolicy:Always.",
    "the native gcsfuse sidecar init container must have env var NATIVE_SIDECAR with value TRUE.",
]

def run(cmd, check=True):
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode != 0:
        sys.stderr.write("$ " + " ".join(cmd) + "\n")
        sys.stderr.write(p.stdout)
        sys.stderr.write(p.stderr)
        raise SystemExit(p.returncode)
    return p

def k(*args, check=True):
    return run(["kubectl", *args], check=check)

def ensure_ns(name, tenant=False):
    k("create", "namespace", name)
    for sa in ["flux", "other"]:
        k("create", "serviceaccount", sa, "-n", name)
    for _ in range(40):
        if k("get", "serviceaccount", "default", "-n", name, check=False).returncode == 0:
            break
        time.sleep(0.25)
    else:
        raise RuntimeError(f"default serviceaccount not observed in {name}")
    if tenant:
        k("label", "namespace", name, "toolkit.fluxcd.io/tenant=yes")

def pod_yaml(name, ns, sa, annotation=None, sidecar=False, restart="NA", env="NA"):
    lines = [
        "apiVersion: v1",
        "kind: Pod",
        "metadata:",
        f"  name: {name}",
        f"  namespace: {ns}",
    ]
    if annotation:
        lines += ["  annotations:", '    gke-gcsfuse/volumes: "true"']
    lines += [
        "spec:",
        "  restartPolicy: Never",
        f"  serviceAccountName: {sa}",
    ]
    if sidecar:
        lines += [
            "  initContainers:",
            "    - name: gke-gcsfuse-sidecar",
            "      image: registry.k8s.io/pause:3.10",
        ]
        if restart not in ("NA", "absent"):
            lines.append(f"      restartPolicy: {restart}")
        if env not in ("NA", "absent"):
            lines += [
                "      env:",
                "        - name: NATIVE_SIDECAR",
                f'          value: "{env}"',
            ]
    lines += [
        "  containers:",
        "    - name: app",
        "      image: registry.k8s.io/pause:3.10",
    ]
    return "\n".join(lines) + "\n"

def execute_yaml(case_id, yaml_text, target_msgs):
    path = OUT / f"{case_id}.yaml"
    path.write_text(yaml_text, encoding="utf-8")
    p = k("create", "--dry-run=server", "-f", str(path), check=False)
    (OUT / f"{case_id}.stdout").write_text(p.stdout, encoding="utf-8")
    (OUT / f"{case_id}.stderr").write_text(p.stderr, encoding="utf-8")
    if p.returncode == 0:
        return "ACCEPT", "ADMITTED"
    if any(msg in p.stderr for msg in target_msgs):
        return "REJECT", "TARGET_POLICY"
    return "REJECT", "NATIVE_ORACLE_AMBIGUOUS"

def execute_update(case_id, ns, name, target_msgs):
    p = k(
        "patch", "pod", name, "-n", ns,
        "--type=merge",
        "-p", '{"metadata":{"annotations":{"eeq-grid-update":"1"}}}',
        "--dry-run=server", "-o", "yaml",
        check=False,
    )
    (OUT / f"{case_id}.stdout").write_text(p.stdout, encoding="utf-8")
    (OUT / f"{case_id}.stderr").write_text(p.stderr, encoding="utf-8")
    if p.returncode == 0:
        return "ACCEPT", "ADMITTED"
    if any(msg in p.stderr for msg in target_msgs):
        return "REJECT", "TARGET_POLICY"
    return "REJECT", "NATIVE_ORACLE_AMBIGUOUS"

# Verify target native policies are present.
k("get", "validatingadmissionpolicy", "flux-tenant-pods")
k("get", "validatingadmissionpolicybinding", "flux-tenant-pods")
k("get", "validatingadmissionpolicy", "gcsfuse-sidecar-validator.csi.storage.gke.io")
k("get", "validatingadmissionpolicybinding", "gcsfuse-sidecar-validator-binding.csi.storage.gke.io")

# Persist frozen-input hashes used by this run.
with (OUT / "FROZEN_INPUT_SHA256SUMS.txt").open("w", encoding="utf-8") as fh:
    for p in [MAP, PRED, AUDIT]:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        fh.write(f"{h}  {p.relative_to(ROOT)}\n")

preds = json.loads(PRED.read_text(encoding="utf-8"))

# Flux CREATE namespaces.
ensure_ns("eeq-grid-c0", tenant=False)
ensure_ns("eeq-grid-c1", tenant=True)

# Flux UPDATE namespaces: create baseline pods before enabling tenant qualification.
ensure_ns("eeq-grid-u0", tenant=False)
ensure_ns("eeq-grid-u1", tenant=False)
for tenant, ns in [(False, "eeq-grid-u0"), (True, "eeq-grid-u1")]:
    for sa in ["flux", "default"]:
        name = f"flux-update-t{int(tenant)}-{sa}"
        path = OUT / f"baseline-{name}.yaml"
        path.write_text(pod_yaml(name, ns, sa), encoding="utf-8")
        k("create", "-f", str(path))
k("label", "namespace", "eeq-grid-u1", "toolkit.fluxcd.io/tenant=yes")

# GCS grid namespace.
ensure_ns("eeq-gcs-grid", tenant=False)

rows = []
mismatches = 0
ambiguous = 0
eligible = 0
preexcluded = 0

for i, row in enumerate(preds, start=1):
    family = row["family"]
    expected = row["expected"]
    case_id = f"{i:02d}-{family}"
    params = json.dumps({k:v for k,v in row.items() if k not in ("family","expected")}, sort_keys=True, separators=(",",":"))

    if family == "gcsfuse" and row.get("sidecar") is True and row.get("restart") == "Never":
        rows.append([case_id, family, params, expected, "NOT_RUN", "PREEXCLUDED_NATIVE_SCHEMA_INVALID", "PREEXCLUDED"])
        preexcluded += 1
        continue

    eligible += 1
    if family == "flux":
        tenant = bool(row["tenant_label"])
        sa = row["service_account"]
        op = row["operation"]
        if op == "CREATE":
            ns = "eeq-grid-c1" if tenant else "eeq-grid-c0"
            name = f"flux-create-t{int(tenant)}-{sa}"
            observed, attribution = execute_yaml(case_id, pod_yaml(name, ns, sa), [FLUX_MSG])
        elif op == "UPDATE":
            ns = "eeq-grid-u1" if tenant else "eeq-grid-u0"
            name = f"flux-update-t{int(tenant)}-{sa}"
            observed, attribution = execute_update(case_id, ns, name, [FLUX_MSG])
        else:
            raise RuntimeError(f"unknown Flux operation {op}")
    elif family == "gcsfuse":
        name = f"gcs-{i:02d}"
        observed, attribution = execute_yaml(
            case_id,
            pod_yaml(
                name, "eeq-gcs-grid", "default",
                annotation=bool(row["annotation"]),
                sidecar=bool(row["sidecar"]),
                restart=row["restart"],
                env=row["env"],
            ),
            GCS_MSGS,
        )
    else:
        raise RuntimeError(f"unknown family {family}")

    if attribution == "NATIVE_ORACLE_AMBIGUOUS":
        status = "AMBIGUOUS"
        ambiguous += 1
    elif observed == expected:
        status = "PASS"
    else:
        status = "MISMATCH"
        mismatches += 1
    rows.append([case_id, family, params, expected, observed, attribution, status])

with (OUT / "grid_results.tsv").open("w", encoding="utf-8") as fh:
    fh.write("case\tfamily\tparams\texpected\tobserved\tattribution\tstatus\n")
    for r in rows:
        fh.write("\t".join(map(str, r)) + "\n")

summary = {
    "frozen_rows": len(preds),
    "eligible_rows": eligible,
    "preexcluded_native_schema_invalid": preexcluded,
    "mismatches": mismatches,
    "ambiguous_eligible_rows": ambiguous,
    "passes": sum(1 for r in rows if r[-1] == "PASS"),
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(summary, sort_keys=True))
print((OUT / "grid_results.tsv").read_text(encoding="utf-8"))

if mismatches or ambiguous:
    raise SystemExit(1)
