#!/usr/bin/env python3
"""R3-M1 NATIVE ONLY: two real binding sources and two ordered namespace updates.

NEVER imports source predictor, sees SOURCE_PREDICTIONS.json or consults
expected native labels. All 12 main observations and 12 controls are kept
even if an experiment fails. It runs on one FRESH Kind cluster per order.
"""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

NAMES=("policy.json","binding-team.json","binding-mode.json","namespace.json",
       "pod-flux.json","pod-default.json","action-team.json","action-mode.json")
ORDERS={"TM":("team","mode"),"MT":("mode","team")}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def call(argv,check=True):
    start=time.perf_counter_ns()
    done=subprocess.run(list(argv),capture_output=True,text=True,timeout=180)
    row={"command":list(argv),"exit_code":done.returncode,
         "stdout":done.stdout,"stderr":done.stderr,
         "elapsed_ns":time.perf_counter_ns()-start}
    if check and done.returncode:
        raise RuntimeError("NATIVE_INFRA_FAILURE:"+json.dumps(row))
    return row


def kube(*args,check=True):
    return call(("kubectl",)+args,check=check)


def kube_json(*args):
    return json.loads(kube(*args,"-o","json")["stdout"])


def read_bundle(root):
    root=Path(root)
    if (root/"SOURCE_PREDICTIONS.json").exists():
        raise RuntimeError("NATIVE_FORBIDDEN_PREDICTIONS_PRESENT")
    manifest_bytes=(root/"SOURCE_MANIFEST.json").read_bytes()
    m=json.loads(manifest_bytes)
    if m.get("schema")!="eeq-r3-m1-source-manifest-v1":
        raise RuntimeError("BAD_REGISTERED_SOURCE_MANIFEST")
    rows=m.get("sources")
    if not isinstance(rows,list) or len(rows)!=8 or set(
        x.get("name") for x in rows)!=set(NAMES):
        raise RuntimeError("SOURCE_INVENTORY_MISMATCH")
    docs={}
    for row in rows:
        name=row["name"]
        raw=(root/"sources"/name).read_bytes()
        if len(raw)!=row["bytes"] or sha(raw)!=row["sha256"]:
            raise RuntimeError("SOURCE_HASH_MISMATCH:"+name)
        docs[name]=json.loads(raw)
    return docs,sha(manifest_bytes)


def namespace():
    o=kube_json("get","namespace","eeq-r3")
    m=o["metadata"]
    return {"uid":m["uid"],"resource_version":m["resourceVersion"],
            "labels":dict(m.get("labels",{}))}


def inventory():
    out=kube_json("get","validatingadmissionpolicybindings")
    return sorted({
        x["metadata"]["name"]:x["spec"]["matchResources"]["namespaceSelector"]["matchLabels"]
        for x in out.get("items",[])
        if x["metadata"]["name"].startswith("eeq-r3-binding-")
    }.items())


def probe(root,pod,phase):
    r=kube("create","--dry-run=server","-f",
           str(Path(root)/"sources"/("pod-"+pod+".json")),check=False)
    output=r["stdout"]+"\n"+r["stderr"]
    if r["exit_code"]==0:
        observed="ACCEPT"
        attribution="ADMITTED"
    elif ("EEQ_R3_FLUX_SA_DENIED" in output or
          "eeq-r3-flux-deny" in output):
        observed="REJECT"
        attribution="REGISTERED_VAP_DENIAL"
    else:
        observed="NATIVE_ORACLE_AMBIGUOUS"
        attribution="UNRELATED_OR_AMBIGUOUS_FAILURE"
    return {"phase":phase,"probe":pod,"native":observed,
            "attribution":attribution,"exit_code":r["exit_code"],
            "stdout":r["stdout"],"stderr":r["stderr"],
            "pod_sha256":sha((Path(root)/"sources"/("pod-"+pod+".json")).read_bytes()),
            "decision_elapsed_ns":r["elapsed_ns"]}


def probes(root,phase):
    return [probe(root,p,phase) for p in ("flux","default")]


def ensure_sa():
    result=kube("create","serviceaccount","flux","-n","eeq-r3",check=False)
    if result["exit_code"] and "AlreadyExists" not in (
            result["stdout"]+result["stderr"]):
        raise RuntimeError("FLUX_SA_NATIVE_SETUP_FAILURE")
    for i in range(40):
        r=kube("get","serviceaccount","default","-n","eeq-r3",check=False)
        if r["exit_code"]==0:
            return
        time.sleep(0.5)
    raise RuntimeError("DEFAULT_SA_NATIVE_SETUP_FAILURE")


def registered_match(docs,actual_bindings):
    expected={
        "eeq-r3-binding-"+name:docs["binding-"+name+".json"]["spec"]["matchResources"][
            "namespaceSelector"]["matchLabels"]
        for name in ("team","mode")
    }
    got=dict(actual_bindings)
    if got!=expected:
        raise RuntimeError("NATIVE_BINDING_SOURCE_MISMATCH:"+repr((got,expected)))


def action(root,docs,key):
    item=docs["action-"+key+".json"]
    before=namespace()
    command=item["full_command"]
    if command!=["kubectl","label","namespace","eeq-r3",
                 "r3."+key+"="+item["to"],"--overwrite"]:
        raise RuntimeError("UNREGISTERED_NATIVE_ACTION")
    changed=call(command,check=False)
    after=namespace()
    valid=(changed["exit_code"]==0 and before["uid"]==after["uid"] and
           before["resource_version"]!=after["resource_version"] and
           before["labels"].get(item["key"])==item["from"] and
           after["labels"].get(item["key"])==item["to"] and
           all(before["labels"].get(k)==v for k,v in after["labels"].items()
               if k!=item["key"]))
    return {"action":key,"command":changed,"before":before,
            "after":after,"native_registered_action_verified":valid}


def run(root,order):
    if order not in ORDERS:
        raise RuntimeError("UNREGISTERED_ACTION_ORDER")
    docs,mhash=read_bundle(root)
    ctx=kube("config","current-context")["stdout"].strip()
    out={"schema":"eeq-r3-m1-native-two-binding-one-order-v1",
         "order":order,"context":ctx,"source_manifest_sha256":mhash,
         "prediction_json_read":False,
         "controls":[],"observations":[],"native_actions":[],
         "original_v1_g5_increment":0,
         "error":None}
    try:
        kube("apply","-f",str(Path(root)/"sources"/"namespace.json"))
        ensure_sa()
        initial=namespace()
        if any(initial["labels"].get(k)!=v for k,v in
               docs["namespace.json"]["metadata"]["labels"].items()):
            raise RuntimeError("NATIVE_INITIAL_NAMESPACE_MISMATCH")
        out["initial_namespace"]=initial
        # Exactly two pre-policy/binding unbound controls.
        if inventory():
            raise RuntimeError("FRESH_CLUSTER_HAS_REGISTERED_BINDING")
        out["controls"] += [dict(p,control="UNBOUND") for p in probes(root,"unbound")]
        kube("apply","-f",str(Path(root)/"sources"/"policy.json"))
        policy=kube_json("get","validatingadmissionpolicy","eeq-r3-flux-deny")
        if policy["spec"]["validations"]!=docs["policy.json"]["spec"]["validations"]:
            raise RuntimeError("NATIVE_POLICY_CEL_MISMATCH")
        for key in ("team","mode"):
            kube("apply","-f",str(Path(root)/"sources"/("binding-"+key+".json")))
            expected="eeq-r3-binding-"+key
            if [name for name,selector in inventory()]!=[expected]:
                raise RuntimeError("ISOLATION_CONTROL_BINDING_INVENTORY_MISMATCH")
            time.sleep(10.0)  # frozen fixed setup stabilization
            out["controls"] += [dict(p,control="ONLY_"+key.upper())
                                for p in probes(root,"isolated_"+key)]
            kube("delete","-f",str(Path(root)/"sources"/("binding-"+key+".json")))
            if inventory():
                raise RuntimeError("ISOLATED_BINDING_DELETION_NOT_VISIBLE")
            time.sleep(10.0)  # frozen fixed isolation stabilization

        for key in ("team","mode"):
            kube("apply","-f",str(Path(root)/"sources"/("binding-"+key+".json")))
        both=inventory()
        registered_match(docs,both)
        out["observed_registered_bindings"]=both
        time.sleep(10.0)  # frozen fixed before phase0
        out["observations"] += [dict(p,phase_index=0,namespace=namespace(),
                                     native_binding_inventory=inventory())
                                for p in probes(root,"initial")]
        for phase,key in enumerate(ORDERS[order],start=1):
            registered=action(root,docs,key)
            out["native_actions"].append(registered)
            if not registered["native_registered_action_verified"]:
                raise RuntimeError("NATIVE_ACTION_VIOLATED_FROZEN_PRECONDITION:"+key)
            time.sleep(6.0)  # fixed pre-registered, not outcome-driven
            out["observations"] += [dict(p,phase_index=phase,
                                         namespace=namespace(),
                                         native_binding_inventory=inventory())
                    for p in probes(root,("after_first" if phase==1 else "after_second"))]
    except Exception as exc:
        out["error"]=repr(exc)
    out["registered_primary_rows"]=6
    out["observed_primary_rows"]=len(out["observations"])
    out["registered_control_rows"]=6
    out["observed_control_rows"]=len(out["controls"])
    out["registered_action_count"]=2
    out["observed_action_count"]=len(out["native_actions"])
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-bundle",required=True)
    ap.add_argument("--order",choices=tuple(ORDERS),required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    result=run(a.source_bundle,a.order)
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                           encoding="utf-8")
    print(json.dumps({"order":a.order,"main":result["observed_primary_rows"],
        "controls":result["observed_control_rows"],
        "updates":result["observed_action_count"],
        "error":result["error"],"native_predictions_read":False},sort_keys=True))
    if result["error"] is not None:
        raise SystemExit("R3_M1_NATIVE_EXECUTION_FAILURE_RETAINED_IN_RAW")


if __name__=="__main__":
    main()
