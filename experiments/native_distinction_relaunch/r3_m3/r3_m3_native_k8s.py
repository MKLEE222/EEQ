#!/usr/bin/env python3
"""R3-M3 NATIVE ONLY: fresh Kubernetes API membership mutation witness.

No source predictor imports, no expected labels, no M2 native data.
Independently reads EXACT pinned 8 source files and their digests.
Records all full per-resource lists, list resourceVersions, actual changes,
and eight server-side Pod CREATE responses, including ambiguous errors.
"""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

NAMES=("policy.json","binding-team.json","binding-mode.json",
       "namespace.json","pod-flux.json","pod-default.json",
       "policy-third.json","binding-third.json")
PHASES=("T0_OLD_TWO_BINDINGS","T1_THIRD_POLICY_UNBOUND",
        "T2_THIRD_BINDING_ACTIVE","T3_THIRD_BINDING_REMOVED")
PROBES=("flux","default")
OLD_BINDINGS=("eeq-r3-binding-team","eeq-r3-binding-mode")
OLD_POLICY="eeq-r3-flux-deny"
NEW_POLICY="eeq-r3-m3-default-deny"
NEW_BINDING="eeq-r3-m3-binding-third"


def hashbytes(b):
    return hashlib.sha256(b).hexdigest()


def js_sha(v):
    return hashbytes(json.dumps(v,sort_keys=True,separators=(',',':')).encode())


def execute(command,check=True):
    t=time.perf_counter_ns()
    r=subprocess.run(list(command),capture_output=True,text=True,timeout=180)
    out={"command":list(command),"returncode":r.returncode,
         "stdout":r.stdout,"stderr":r.stderr,
         "elapsed_ns":time.perf_counter_ns()-t}
    if check and r.returncode:
        raise RuntimeError("K8S_INFRA_FAILURE:"+json.dumps(out))
    return out


def kubectl(*argv,check=True):
    return execute(("kubectl",)+argv,check=check)


def kubejson(*argv):
    out=kubectl(*argv,"-o","json")
    return json.loads(out["stdout"])


def sources(root):
    root=Path(root)
    if (root/"SOURCE_PREDICTIONS.json").exists():
        raise RuntimeError("NATIVE_PREDICTION_FILE_LEAK")
    manifest_raw=(root/"SOURCE_MANIFEST.json").read_bytes()
    manifest=json.loads(manifest_raw)
    if (manifest.get("schema")!="eeq-r3-m3-source-manifest-v1" or
        len(manifest["sources"])!=8 or
        set(x["name"] for x in manifest["sources"])!=set(NAMES)):
        raise RuntimeError("BAD_PINNED_NATIVE_SOURCE_ENVELOPE")
    docs={}
    sha_map={}
    for entry in manifest["sources"]:
        p=root/"sources"/entry["name"]
        raw=p.read_bytes()
        if len(raw)!=entry["bytes"] or hashbytes(raw)!=entry["sha256"]:
            raise RuntimeError("SOURCE_SHA_OR_BYTES_DRIFT_"+entry["name"])
        docs[entry["name"]]=json.loads(raw)
        sha_map[entry["name"]]=entry["sha256"]
    return docs,sha_map,hashbytes(manifest_raw)


def raw_collection(kind):
    """Return an actual Kubernetes API collection, no kubectl List printer.

    LIST metadata.resourceVersion is required and treated as opaque; not
    cross-kind atomicity or continuous WATCH authority.
    """
    endpoints={
        "validatingadmissionpolicies":"ValidatingAdmissionPolicyList",
        "validatingadmissionpolicybindings":"ValidatingAdmissionPolicyBindingList",
    }
    if kind not in endpoints:
        raise RuntimeError("UNREGISTERED_NATIVE_SOURCE_COLLECTION")
    uri="/apis/admissionregistration.k8s.io/v1/"+kind
    response=kubectl("get","--raw",uri)
    obj=json.loads(response["stdout"])
    if (obj.get("apiVersion")!="admissionregistration.k8s.io/v1" or
        obj.get("kind")!=endpoints[kind] or
        not isinstance(obj.get("items"),list) or
        not isinstance(obj.get("metadata",{}).get("resourceVersion"),str) or
        not obj["metadata"]["resourceVersion"]):
        raise RuntimeError("RAW_API_NATIVE_SOURCE_LIST_RV_OR_SHAPE_MISSING_"+kind)
    return obj


def membership_snapshot():
    policies=raw_collection("validatingadmissionpolicies")
    bindings=raw_collection("validatingadmissionpolicybindings")
    def serialize(obj):
        return {
            "name":obj["metadata"]["name"],
            "uid":obj["metadata"]["uid"],
            "resource_version":obj["metadata"]["resourceVersion"],
            "spec_sha256":js_sha(obj["spec"]),
            "spec":obj["spec"],
        }
    return {
        "policy_list_resource_version":
            policies.get("metadata",{}).get("resourceVersion"),
        "binding_list_resource_version":
            bindings.get("metadata",{}).get("resourceVersion"),
        "policy_items":sorted(
            (serialize(x) for x in policies.get("items",[])),
            key=lambda x:x["name"]),
        "binding_items":sorted(
            (serialize(x) for x in bindings.get("items",[])),
            key=lambda x:x["name"]),
        "source_scope":"ENTIRE_NATIVE_VAP_POLICY_AND_BINDING_LIST",
        "not_global_k8s_admission_authority":True,
    }


def ournames(inv,which):
    kind="policy_items" if which=="policies" else "binding_items"
    return sorted(x["name"] for x in inv[kind]
                  if x["name"].startswith("eeq-r3-"))


def check_membership(inv,phase):
    expect_p=[OLD_POLICY]+(
        [NEW_POLICY] if phase!="T0_OLD_TWO_BINDINGS" else [])
    expect_b=list(OLD_BINDINGS)+(
        [NEW_BINDING] if phase=="T2_THIRD_BINDING_ACTIVE" else [])
    got_p=ournames(inv,"policies")
    got_b=ournames(inv,"bindings")
    if got_p!=sorted(expect_p) or got_b!=sorted(expect_b):
        raise RuntimeError(
            "NATIVE_REGISTERED_POLICY_BINDING_INVENTORY_MISMATCH:"
            +json.dumps({"phase":phase,"policies":got_p,
                         "bindings":got_b}))
    if not inv["policy_list_resource_version"] or not (
            inv["binding_list_resource_version"]):
        raise RuntimeError("K8S_NATIVE_LIST_RV_UNAVAILABLE")


def pod(root,who,phase):
    fp=Path(root)/"sources"/("pod-"+who+".json")
    r=kubectl("create","--dry-run=server","-f",str(fp),check=False)
    output=r["stdout"]+"\n"+r["stderr"]
    if r["returncode"]==0:
        outcome="ACCEPT";attribution="ADMITTED"
    elif "EEQ_R3_M3_DEFAULT_SA_DENIED" in output or NEW_POLICY in output:
        outcome="REJECT";attribution="REGISTERED_THIRD_VAP_DENY"
    elif "EEQ_R3_FLUX_SA_DENIED" in output or OLD_POLICY in output:
        outcome="REJECT";attribution="REGISTERED_OLD_VAP_DENY"
    else:
        outcome="NATIVE_ORACLE_AMBIGUOUS";attribution="UNRELATED_DENIAL_OR_INFRA"
    return {"phase":phase,"probe":who,"native_outcome":outcome,
            "native_attribution":attribution,
            "native_exit_code":r["returncode"],
            "native_stdout":r["stdout"],"native_stderr":r["stderr"],
            "source_pod_sha256":hashbytes(fp.read_bytes()),
            "native_elapsed_ns":r["elapsed_ns"]}


def service_accounts():
    r=kubectl("create","serviceaccount","flux",
              "-n","eeq-r3",check=False)
    if r["returncode"] and "AlreadyExists" not in (
            r["stdout"]+r["stderr"]):
        raise RuntimeError("FLUX_SERVICE_ACCOUNT_SETUP_FAILED")
    for _ in range(40):
        r=kubectl("get","serviceaccount","default",
                  "-n","eeq-r3",check=False)
        if r["returncode"]==0:
            return
        time.sleep(0.5)
    raise RuntimeError("DEFAULT_SERVICE_ACCOUNT_SETUP_FAILED")


def do_native_action(root,action):
    before=membership_snapshot()
    commands={
        "CREATE_3RD_VAP":
            ("kubectl","apply","-f",str(Path(root)/"sources"/"policy-third.json")),
        "CREATE_3RD_BINDING":
            ("kubectl","apply","-f",str(Path(root)/"sources"/"binding-third.json")),
        "DELETE_3RD_BINDING":
            ("kubectl","delete","-f",str(Path(root)/"sources"/"binding-third.json")),
    }
    if action not in commands:
        raise RuntimeError("UNREGISTERED_NATIVE_MEMBERSHIP_ACTION")
    result=execute(commands[action],check=False)
    after=membership_snapshot()
    if action=="CREATE_3RD_VAP":
        good=(
            NEW_POLICY not in ournames(before,"policies") and
            NEW_POLICY in ournames(after,"policies") and
            ournames(before,"bindings")==ournames(after,"bindings") and
            before["policy_list_resource_version"]!=
                after["policy_list_resource_version"])
    elif action=="CREATE_3RD_BINDING":
        good=(
            NEW_BINDING not in ournames(before,"bindings") and
            NEW_BINDING in ournames(after,"bindings") and
            before["binding_list_resource_version"]!=
                after["binding_list_resource_version"])
    else:
        good=(
            NEW_BINDING in ournames(before,"bindings") and
            NEW_BINDING not in ournames(after,"bindings") and
            before["binding_list_resource_version"]!=
                after["binding_list_resource_version"])
    return {
        "action":action,"command_result":result,
        "before_inventory":before,"after_inventory":after,
        "actual_membership_change_verified":bool(good and
                                              result["returncode"]==0),
    }


def old_identity(inv):
    return {
        x["name"]:(x["uid"],x["spec_sha256"],x["resource_version"])
        for x in inv["binding_items"] if x["name"] in OLD_BINDINGS
    }


def run(root):
    docs,sha_map,manifest_hash=sources(root)
    context=kubectl("config","current-context")["stdout"].strip()
    result={
        "schema":"eeq-r3-m3-native-third-membership-v1",
        "scientific_evidence_class":"CONTROLLED_NATIVE_DEVELOPMENT",
        "native_context":context,
        "source_manifest_sha256":manifest_hash,
        "source_digest_map":sha_map,
        "source_predictions_read":False,
        "control_rows":[],"observed_cases":[],
        "phase_inventories":[],"native_membership_actions":[],
        "error":None,"registered_primary_rows":8,
        "registered_control_rows":2,
        "registered_native_membership_actions":3,
        "registered_inventory_snapshots":4,
        "original_v1_g5_increment":0,
    }
    try:
        kubectl("apply","-f",str(Path(root)/"sources"/"namespace.json"))
        service_accounts()
        ns=kubejson("get","namespace","eeq-r3")
        if ns["metadata"]["labels"].get("r3.team")!="tenant" or (
            ns["metadata"]["labels"].get("r3.mode")!="strict"):
            raise RuntimeError("NATIVE_NAMESPACE_SOURCE_SETUP_MISMATCH")
        pre=membership_snapshot()
        if any(n.startswith("eeq-r3-") for n in
               ournames(pre,"policies")+ournames(pre,"bindings")):
            raise RuntimeError("FRESH_CLUSTER_PREEXISTING_TARGET_SOURCES")
        result["control_rows"]=[pod(root,who,"NO_BINDINGS")
                                for who in ("flux","default")]

        for name in ("policy.json","binding-team.json","binding-mode.json"):
            kubectl("apply","-f",str(Path(root)/"sources"/name))
        time.sleep(10) # Freeze: no retry or case-dependent settle.
        for i,phase in enumerate(PHASES):
            if i:
                change=do_native_action(root,(
                    "CREATE_3RD_VAP","CREATE_3RD_BINDING",
                    "DELETE_3RD_BINDING")[i-1])
                result["native_membership_actions"].append(change)
                if not change["actual_membership_change_verified"]:
                    raise RuntimeError("NATIVE_REAL_ACTION_UNVERIFIED_"+phase)
                time.sleep(8) # Fixed registration, no outcome-dependent retry.
            native_inventory=membership_snapshot()
            check_membership(native_inventory,phase)
            result["phase_inventories"].append({
                "phase":phase,"native_inventory":native_inventory})
            result["observed_cases"] += [pod(root,who,phase)
                                         for who in PROBES]
        # Check the two ORIGINAL binding objects never changed in any phase.
        identities=[old_identity(x["native_inventory"])
                    for x in result["phase_inventories"]]
        if len(identities)!=4 or not all(x==identities[0]
                                        for x in identities):
            raise RuntimeError("OLD_BINDING_NATIVE_IDENTITY_CHANGED")
        result["original_binding_native_ids_unchanged"]=True
    except Exception as e:
        result["error"]=repr(e)
    result["observed_primary_rows"]=len(result["observed_cases"])
    result["observed_controls"]=len(result["control_rows"])
    result["observed_native_membership_actions"]=len(
        result["native_membership_actions"])
    result["observed_native_inventories"]=len(result["phase_inventories"])
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-capsule",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    data=run(a.source_capsule)
    Path(a.out).write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "native_observed_cases":data["observed_primary_rows"],
        "controls":data["observed_controls"],
        "mutations":data["observed_native_membership_actions"],
        "inventories":data["observed_native_inventories"],
        "error":data["error"],"source_predictions_read":False
    },sort_keys=True))
    if data["error"]:
        raise SystemExit("R3_M3_NATIVE_FAILURE_RAW_ARCHIVED")


if __name__=="__main__":
    main()
