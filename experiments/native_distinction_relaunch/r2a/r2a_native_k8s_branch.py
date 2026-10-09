#!/usr/bin/env python3
"""R2A NATIVE ONLY: one dynamic branch in one fresh, pinned Kind cluster.

Does NOT import/inspect SOURCE_PREDICTIONS or any expected native outcomes.
All Kubernetes API effects and server-side dry-run decisions are recorded.
The caller must create a FRESH Kind cluster for each branch beforehand.
"""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def call(argv, check=True):
    started = time.perf_counter_ns()
    completed = subprocess.run(
        list(argv), capture_output=True, text=True, timeout=150,
    )
    result = {
        "command": list(argv), "exit_code": completed.returncode,
        "stdout": completed.stdout, "stderr": completed.stderr,
        "elapsed_ns": time.perf_counter_ns()-started,
    }
    if check and completed.returncode != 0:
        raise RuntimeError("K8S_INFRA_COMMAND_FAILED " + json.dumps(result))
    return result


def kubectl(*args, check=True):
    return call(("kubectl",) + args, check=check)


def read_kube_json(*args):
    r = kubectl(*args, "-o", "json")
    return json.loads(r["stdout"])


def load_sources(bundle):
    root = Path(bundle)
    manifest = json.loads((root / "SOURCE_MANIFEST.json").read_text())
    if manifest.get("schema") != "eeq-r2a-k8s-source-manifest-v1":
        raise RuntimeError("BAD_NATIVE_SOURCE_MANIFEST")
    if len(manifest["sources"]) != 7:
        raise RuntimeError("MISSING_REGISTERED_SOURCE")
    docs = {}
    for row in manifest["sources"]:
        raw = (root / "sources" / row["name"]).read_bytes()
        if len(raw) != row["bytes"] or sha(raw) != row["sha256"]:
            raise RuntimeError("SOURCE_PIN_MISMATCH " + row["name"])
        docs[row["name"]] = json.loads(raw)
    return docs, manifest


def assert_source_equivalent(observed, expected, branch):
    if observed["spec"]["policyName"] != expected["spec"]["policyName"]:
        raise RuntimeError("BINDING_POLICY_IDENTITY_MISMATCH_" + branch)
    actual_labels = observed["spec"]["matchResources"][
        "namespaceSelector"]["matchLabels"]
    expected_labels = expected["spec"]["matchResources"][
        "namespaceSelector"]["matchLabels"]
    if actual_labels != expected_labels:
        raise RuntimeError("NATIVE_BINDING_SELECTOR_MISMATCH_" + branch)


def ensure_service_accounts():
    # These steps establish the lawful native precondition; they are
    # never counted as outcome evidence and are independent of the VAP.
    account = kubectl("create", "serviceaccount", "flux",
                      "-n", "eeq-r2a", check=False)
    if account["exit_code"] != 0 and "AlreadyExists" not in (
            account["stdout"] + account["stderr"]):
        raise RuntimeError("COULD_NOT_CREATE_FLUX_SERVICEACCOUNT")
    for i in range(40):
        default = kubectl("get", "sa", "default", "-n", "eeq-r2a", check=False)
        if default["exit_code"] == 0:
            return
        time.sleep(0.5)
    raise RuntimeError("NATIVE_DEFAULT_SERVICEACCOUNT_MISSING")


def read_namespace():
    v = read_kube_json("get", "namespace", "eeq-r2a")
    return {
        "resource_version": v["metadata"]["resourceVersion"],
        "labels": dict(v["metadata"].get("labels", {})),
        "uid": v["metadata"]["uid"],
    }


def pod_probe(bundle, probe, phase):
    filename = "pod-" + probe + ".json"
    path = Path(bundle) / "sources" / filename
    r = kubectl("create", "--dry-run=server", "-f", str(path), check=False)
    output = r["stdout"] + "\n" + r["stderr"]
    if r["exit_code"] == 0:
        native = "ACCEPT"
        attributable = "ADMITTED"
    elif ("EEQ_R2A_FLUX_SA_DENIED" in output or
          "eeq-r2a-flux-deny" in output):
        native = "REJECT"
        attributable = "REGISTERED_VAP_DENY"
    else:
        native = "NATIVE_ORACLE_AMBIGUOUS"
        attributable = "UNRELATED_REJECTION"
    return {
        "probe": probe, "phase": phase,
        "native": native, "native_attribution": attributable,
        "exit_code": r["exit_code"], "stdout": r["stdout"],
        "stderr": r["stderr"], "decision_ns": r["elapsed_ns"],
        "pod_source_sha256": sha(path.read_bytes()),
    }


def run_branch(bundle, branch):
    if branch not in ("a", "b"):
        raise RuntimeError("UNREGISTERED_NATIVE_BRANCH")
    docs, manifest = load_sources(bundle)
    ns = docs["namespace-before.json"]
    expected_policy = docs["policy.json"]
    expected_binding = docs["binding-" + branch + ".json"]
    action = docs["update-namespace-label.json"]

    # Source files are original frozen bytes; never rewrite JSON or labels.
    ns_path = Path(bundle) / "sources" / "namespace-before.json"
    policy_path = Path(bundle) / "sources" / "policy.json"
    binding_path = Path(bundle) / "sources" / ("binding-" + branch + ".json")
    kubectl("apply", "-f", str(ns_path))
    ensure_service_accounts()
    init_ns = read_namespace()
    for k, v in ns["metadata"]["labels"].items():
        if init_ns["labels"].get(k) != v:
            raise RuntimeError("NAMESPACE_SETUP_LABEL_MISMATCH")
    # Four native unbound controls are separate from the eight main rows.
    unbound = [pod_probe(bundle, p, "unbound") for p in ("flux", "default")]

    kubectl("apply", "-f", str(policy_path))
    kubectl("apply", "-f", str(binding_path))
    policy = read_kube_json("get", "validatingadmissionpolicy",
                            "eeq-r2a-flux-deny")
    binding = read_kube_json("get", "validatingadmissionpolicybinding",
                             "eeq-r2a-binding-" + branch)
    assert_source_equivalent(binding, expected_binding, branch)
    if policy["spec"]["validations"][0]["expression"] != (
            expected_policy["spec"]["validations"][0]["expression"]):
        raise RuntimeError("NATIVE_POLICY_CEL_MISMATCH")
    time.sleep(10.0)  # Freeze: fixed wait, never outcome-dependent retry.
    before_ns = read_namespace()
    current = [pod_probe(bundle, p, "current") for p in ("flux", "default")]

    # EXACT registered native API state-changing action, ONCE.
    registered = action["full_command"]
    if registered != [
            "kubectl", "label", "namespace", "eeq-r2a",
            "r2a.mode=relaxed", "--overwrite"]:
        raise RuntimeError("UNREGISTERED_NAMESPACE_ACTION")
    change = call(registered, check=False)
    after_ns = read_namespace()
    legal_mutation = (
        change["exit_code"] == 0 and
        before_ns["uid"] == after_ns["uid"] and
        before_ns["resource_version"] != after_ns["resource_version"] and
        before_ns["labels"].get("r2a.mode") == "strict" and
        after_ns["labels"].get("r2a.mode") == "relaxed" and
        before_ns["labels"].get("r2a.team") ==
        after_ns["labels"].get("r2a.team") == "tenant"
    )
    # Never replace the update, never retry until the desired labels appear.
    future = ([pod_probe(bundle, p, "after_native_label_update")
               for p in ("flux", "default")] if legal_mutation else [])
    result = {
        "schema": "eeq-r2a-native-k8s-dynamic-branch-v1",
        "branch": branch,
        "native_cluster_context": kubectl("config", "current-context")["stdout"].strip(),
        "source_manifest_sha256": sha(
            (Path(bundle)/"SOURCE_MANIFEST.json").read_bytes()),
        "source_digest_map": {
            item["name"]:item["sha256"] for item in manifest["sources"]},
        "native_predictions_file_read": False,
        "source_binding_selector": expected_binding["spec"]["matchResources"][
            "namespaceSelector"]["matchLabels"],
        "native_observed_binding_selector": binding["spec"]["matchResources"][
            "namespaceSelector"]["matchLabels"],
        "native_policy_observed_name": policy["metadata"]["name"],
        "native_initial_namespace": init_ns,
        "native_current_namespace": before_ns,
        "native_post_action_namespace": after_ns,
        "namespace_label_action_command": change,
        "native_namespace_action_verified": legal_mutation,
        "unbound_controls": unbound,
        "current_probes": current,
        "future_probes": future,
        "expected_registered_main_rows": 4,
        "actual_registered_main_rows": len(current)+len(future),
        "g5_increment": 0,
    }
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bundle", required=True)
    p.add_argument("--branch", choices=("a", "b"), required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    result = run_branch(a.bundle, a.branch)
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                           encoding="utf-8")
    print(json.dumps({
        "branch": a.branch,
        "unbound_controls":len(result["unbound_controls"]),
        "current":len(result["current_probes"]),
        "future":len(result["future_probes"]),
        "actual_native_namespace_label_action":
            result["native_namespace_action_verified"],
        "current_native":[x["native"] for x in result["current_probes"]],
        "future_native":[x["native"] for x in result["future_probes"]],
    },sort_keys=True))


if __name__ == "__main__":
    main()
