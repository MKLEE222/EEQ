#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRED = ROOT / "experiments/k8s_5spot/PREDICTIONS_BEFORE_NATIVE.json"
MAP = ROOT / "experiments/k8s_5spot/FROZEN_MAPPING.md"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "k8s-5spot-results")
OUT.mkdir(parents=True, exist_ok=True)
LOGS = OUT / "logs"
LOGS.mkdir(exist_ok=True)

UPSTREAM_COMMIT = "4d14866b5b0b9de5b4b6bb6e264303e22b5cfd98"
POLICY_BLOB = "a8dc90c393d7355c7633c6f5be2e37aa0639e244"
BINDING_BLOB = "54c4bfc4a74da27b19d4eec1211026039706f3ad"
BASE = f"https://raw.githubusercontent.com/finos/5-spot/{UPSTREAM_COMMIT}/deploy/admission"
POLICY_URL = BASE + "/agent-pod-security-policy.yaml"
BINDING_URL = BASE + "/agent-pod-security-binding.yaml"
TARGET_POLICY = "5spot-agent-pod-security"
TARGET_MESSAGES = [
    "hostPID in 5spot-system is restricted to the 5-Spot node agents",
    "hostNetwork is not permitted in 5spot-system",
    "hostIPC is not permitted in 5spot-system",
    "privileged containers in 5spot-system are restricted to the kata config agent",
    "privileged containers must keep readOnlyRootFilesystem: true",
    "hostPath volumes in 5spot-system are restricted to the 5-Spot node agents",
    "the kata config agent may only mount hostPath '/'",
    "the reclaim agent may only mount hostPath '/proc' and '/etc/machine-id'",
    "added Linux capabilities in 5spot-system are restricted to NET_ADMIN",
    "explicitly running as root",
    "5-Spot agent pods must set pod-level seccompProfile.type: RuntimeDefault",
    "ephemeral (debug) containers in 5spot-system may not be privileged",
]

def run(cmd, check=True, input_text=None):
    p = subprocess.run(cmd, text=True, input=input_text,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode != 0:
        sys.stderr.write("$ " + " ".join(cmd) + "\n" + p.stdout + p.stderr)
        raise SystemExit(p.returncode)
    return p

def k(*args, check=True, input_text=None):
    return run(["kubectl", *args], check=check, input_text=input_text)

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def fetch_exact(url, path, expected_blob):
    with urllib.request.urlopen(url, timeout=120) as r:
        path.write_bytes(r.read())
    observed = run(["git", "hash-object", str(path)]).stdout.strip()
    if observed != expected_blob:
        raise SystemExit(f"upstream blob mismatch for {path.name}: {observed} != {expected_blob}")
    return observed

def pod_yaml(row):
    profile = row["profile"]
    lines = [
        "apiVersion: v1",
        "kind: Pod",
        "metadata:",
        f"  name: {row['id']}",
        f"  namespace: {row['namespace']}",
        "spec:",
        f"  serviceAccountName: {row['service_account']}",
        "  restartPolicy: Never",
        "  securityContext:",
        "    seccompProfile:",
        "      type: RuntimeDefault",
    ]
    if profile == "host_network":
        lines += ["  hostNetwork: true"]
    elif profile == "host_ipc":
        lines += ["  hostIPC: true"]
    elif profile == "host_pid":
        lines += ["  hostPID: true"]
    elif profile == "run_as_root":
        lines += ["    runAsUser: 0"]
    if profile in {"hostpath_root", "hostpath_proc"}:
        hp = "/" if profile == "hostpath_root" else "/proc"
        lines += [
            "  volumes:",
            "    - name: hp",
            "      hostPath:",
            f"        path: {hp}",
        ]
    lines += [
        "  containers:",
        "    - name: c",
        "      image: registry.k8s.io/pause:3.10",
        "      securityContext:",
        "        readOnlyRootFilesystem: true",
    ]
    if profile in {"privileged_ro", "privileged_rw"}:
        lines += ["        privileged: true"]
        if profile == "privileged_rw":
            # Override the safe-base mitigation for this profile.
            lines[-2] = "        readOnlyRootFilesystem: false"
    elif profile in {"cap_net_admin", "cap_sys_admin"}:
        cap = "NET_ADMIN" if profile == "cap_net_admin" else "SYS_ADMIN"
        lines += [
            "        capabilities:",
            "          add:",
            f'            - "{cap}"',
        ]
    return "\n".join(lines) + "\n"

def execute(case_id, yaml_text, phase):
    pth = OUT / f"{case_id}.{phase}.yaml"
    pth.write_text(yaml_text, encoding="utf-8")
    p = k("create", "--dry-run=server", "-f", str(pth), check=False)
    (LOGS / f"{case_id}.{phase}.stdout").write_text(p.stdout, encoding="utf-8")
    (LOGS / f"{case_id}.{phase}.stderr").write_text(p.stderr, encoding="utf-8")
    return p

def classify(p):
    if p.returncode == 0:
        return "ACCEPT", "ADMITTED"
    joined = p.stdout + "\n" + p.stderr
    if TARGET_POLICY in joined or any(msg in joined for msg in TARGET_MESSAGES):
        return "REJECT", "TARGET_POLICY"
    return "REJECT", "NATIVE_ORACLE_AMBIGUOUS"

def ensure_environment():
    for ns in ("5spot-system", "eeq-5spot-unscoped"):
        p = k("create", "namespace", ns, check=False)
        if p.returncode != 0 and "AlreadyExists" not in (p.stdout + p.stderr):
            raise SystemExit(p.stdout + p.stderr)
    for sa in ("5spot-kata-config-agent", "5spot-reclaim-agent"):
        p = k("create", "serviceaccount", sa, "-n", "5spot-system", check=False)
        if p.returncode != 0 and "AlreadyExists" not in (p.stdout + p.stderr):
            raise SystemExit(p.stdout + p.stderr)
    labels = {}
    for ns in ("5spot-system", "eeq-5spot-unscoped"):
        p = k("get", "namespace", ns, "-o", "json")
        obj = json.loads(p.stdout)
        labels[ns] = obj.get("metadata", {}).get("labels", {})
    if labels["5spot-system"].get("kubernetes.io/metadata.name") != "5spot-system":
        raise SystemExit("native namespace label missing for 5spot-system")
    if labels["eeq-5spot-unscoped"].get("kubernetes.io/metadata.name") == "5spot-system":
        raise SystemExit("unscoped namespace unexpectedly matches target selector")
    (OUT / "namespace_labels.json").write_text(json.dumps(labels, indent=2, sort_keys=True)+"\n")

def main():
    preds = json.loads(PRED.read_text(encoding="utf-8"))
    if preds.get("semantic_cases") != 38 or len(preds.get("rows", [])) != 38:
        raise SystemExit("frozen prediction grid must contain 38 cases")

    policy = OUT / "upstream-agent-pod-security-policy.yaml"
    binding = OUT / "upstream-agent-pod-security-binding.yaml"
    observed_policy = fetch_exact(POLICY_URL, policy, POLICY_BLOB)
    observed_binding = fetch_exact(BINDING_URL, binding, BINDING_BLOB)
    (OUT / "UPSTREAM_IDENTITY.json").write_text(json.dumps({
        "repository": "finos/5-spot",
        "commit": UPSTREAM_COMMIT,
        "policy_blob_expected": POLICY_BLOB,
        "policy_blob_observed": observed_policy,
        "binding_blob_expected": BINDING_BLOB,
        "binding_blob_observed": observed_binding,
        "policy_url": POLICY_URL,
        "binding_url": BINDING_URL,
    }, indent=2, sort_keys=True)+"\n")

    (OUT / "FROZEN_INPUT_SHA256SUMS.txt").write_text(
        f"{sha256(MAP)}  experiments/k8s_5spot/FROZEN_MAPPING.md\n"
        f"{sha256(PRED)}  experiments/k8s_5spot/PREDICTIONS_BEFORE_NATIVE.json\n",
        encoding="utf-8",
    )

    ensure_environment()

    # Pre-scoring native schema/precondition audit with target VAP absent.
    eligible = []
    preexcluded = []
    for row in preds["rows"]:
        p = execute(row["id"], pod_yaml(row), "precheck")
        if p.returncode == 0:
            eligible.append(row)
        else:
            preexcluded.append({
                **row,
                "status": "PREEXCLUDED_NATIVE_SCHEMA_INVALID",
                "precheck_rc": p.returncode,
                "precheck_stdout_sha256": sha256(LOGS / f"{row['id']}.precheck.stdout"),
                "precheck_stderr_sha256": sha256(LOGS / f"{row['id']}.precheck.stderr"),
            })

    (OUT / "precheck.json").write_text(json.dumps({
        "frozen_rows": len(preds["rows"]),
        "eligible_before_policy": len(eligible),
        "preexcluded": preexcluded,
    }, indent=2, sort_keys=True)+"\n")

    k("apply", "-f", str(policy))
    k("apply", "-f", str(binding))
    k("get", "validatingadmissionpolicy", TARGET_POLICY, "-o", "yaml")
    k("get", "validatingadmissionpolicybinding", "5spot-agent-pod-security-binding", "-o", "yaml")

    # Wait until the exact target policy is active.
    probe = {
        "id": "activation-probe",
        "scope": "scoped",
        "namespace": "5spot-system",
        "service_account": "default",
        "identity": "default",
        "profile": "host_network",
        "expected": "REJECT",
    }
    activated = False
    attempts = 0
    for attempts in range(1, 61):
        p = execute(probe["id"], pod_yaml(probe), "activation")
        observed, attr = classify(p)
        if observed == "REJECT" and attr == "TARGET_POLICY":
            activated = True
            break
        time.sleep(0.5)
    (OUT / "activation.json").write_text(json.dumps({
        "attempts": attempts, "activated": activated,
    }, indent=2)+"\n")
    if not activated:
        raise SystemExit("5-Spot VAP did not activate with attributable rejection")

    results = []
    mismatches = 0
    ambiguous = 0
    for row in eligible:
        t0 = time.perf_counter_ns()
        p = execute(row["id"], pod_yaml(row), "score")
        t1 = time.perf_counter_ns()
        observed, attr = classify(p)
        if attr == "NATIVE_ORACLE_AMBIGUOUS":
            status = "NATIVE_ORACLE_AMBIGUOUS"
            ambiguous += 1
        elif observed == row["expected"]:
            status = "PASS"
        else:
            status = "MISMATCH"
            mismatches += 1
        results.append({
            **row,
            "observed": observed,
            "attribution": attr,
            "status": status,
            "native_rc": p.returncode,
            "decision_ns": t1 - t0,
            "stdout_sha256": sha256(LOGS / f"{row['id']}.score.stdout"),
            "stderr_sha256": sha256(LOGS / f"{row['id']}.score.stderr"),
        })

    all_rows = results + preexcluded
    (OUT / "grid_results.json").write_text(json.dumps(all_rows, indent=2, sort_keys=True)+"\n")
    summary = {
        "frozen_rows": len(preds["rows"]),
        "eligible_rows": len(results),
        "preexcluded_native_schema_invalid": len(preexcluded),
        "passes": sum(r["status"] == "PASS" for r in results),
        "mismatches": mismatches,
        "ambiguous_eligible_rows": ambiguous,
        "native_action_counts": {
            a: sum(r.get("observed") == a for r in results)
            for a in ("ACCEPT", "REJECT")
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n")
    print(json.dumps(summary, sort_keys=True))

    entries=[]
    for p in sorted(OUT.rglob("*")):
        if p.is_file() and p.name != "SHA256SUMS.txt":
            entries.append(f"{sha256(p)}  {p.relative_to(OUT)}")
    (OUT / "SHA256SUMS.txt").write_text("\n".join(entries)+"\n", encoding="utf-8")

    if mismatches or ambiguous:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
