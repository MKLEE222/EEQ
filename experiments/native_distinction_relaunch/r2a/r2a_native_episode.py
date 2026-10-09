#!/usr/bin/env python3
"""Independent native R2-A cluster episode. NO source-only predictor imported.

Each episode must run inside its OWN freshly created pinned kind cluster.
Returns raw native API observations, binding state and mutation evidence.
"""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

POLICY="eeq-r2a-flux-constraint"
BINDING="eeq-r2a-flux-binding"
SA=("flux","default")
PHASES=("CURRENT","AFTER_BINDING_MUTATION")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def kubectl(*args,stdin=None):
    cmd=["kubectl",*map(str,args)]
    out=subprocess.run(cmd,input=stdin,text=True,
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return {"command":cmd,"returncode":out.returncode,
            "stdout":out.stdout,"stderr":out.stderr}


def necessary(p,context):
    if p["returncode"]:
        raise RuntimeError(context+": "+(p["stderr"] or p["stdout"]))
    return p


def classify(p):
    if p["returncode"]==0:
        return "ACCEPT","NATIVE_ADMITTED"
    diagnostic=p["stdout"]+"\n"+p["stderr"]
    if POLICY in diagnostic and "EEQ_R2A_REGISTERED_FLUX_DENIAL" in diagnostic:
        return "REJECT","REGISTERED_VAP"
    return "NATIVE_ORACLE_AMBIGUOUS","OTHER_NATIVE_ERROR"


def pod_template(namespace,sa,phase,world):
    return {
        "apiVersion":"v1","kind":"Pod",
        "metadata":{"name":"eeq-r2a-"+world.lower()+"-"+
                    phase.lower().replace("_","-")+"-"+sa,
                    "namespace":namespace},
        "spec":{"serviceAccountName":sa,"restartPolicy":"Never",
                "containers":[{"name":"c","image":"registry.k8s.io/pause:3.10"}]}
    }


def observe_pod(ns,sa,phase,world):
    p=kubectl("create","--dry-run=server","-f","-",
              stdin=json.dumps(pod_template(ns,sa,phase,world)))
    outcome,attribution=classify(p)
    return {"world":world,"phase":phase,"service_account":sa,
            "native_outcome":outcome,"native_attribution":attribution,
            "native_returncode":p["returncode"],
            "native_stdout":p["stdout"],"native_stderr":p["stderr"],
            "request_sha256":sha(json.dumps(pod_template(ns,sa,phase,world),
                                            sort_keys=True).encode())}


def get(kind,name):
    p=necessary(kubectl("get",kind,name,"-o","json"),"GET_"+kind+"_"+name)
    return json.loads(p["stdout"])


def selector(binding):
    return (binding["spec"]["matchResources"]["namespaceSelector"]
            ["matchLabels"])


def create_sa(ns):
    r=kubectl("create","serviceaccount","flux","-n",ns)
    if r["returncode"] and "AlreadyExists" not in r["stderr"]:
        raise RuntimeError("FLUX_SA_CREATE:"+r["stderr"])
    for _ in range(30):
        check=kubectl("get","serviceaccount","default","-n",ns)
        if check["returncode"]==0:
            return
        time.sleep(.25)
    raise RuntimeError("DEFAULT_SERVICE_ACCOUNT_NOT_OBSERVABLE")


def run(source_dir,world,out_dir):
    source=Path(source_dir)
    output=Path(out_dir)
    output.mkdir(parents=True,exist_ok=True)
    base_names={
        "WORLD_GATE":"namespace_gate",
        "WORLD_STANDBY":"namespace_standby",
    }
    if world not in base_names:
        raise ValueError("UNREGISTERED_WORLD")
    paths=["policy","binding_initial","binding_after",
           "namespace_gate","namespace_standby","namespace_probe",
           "binding_mutation","challenges"]
    source_hashes={}
    for name in paths:
        source_hashes[name]=sha((source/(name+".json")).read_bytes())
    challenge=json.loads((source/"challenges.json").read_text())
    mutation=json.loads((source/"binding_mutation.json").read_text())
    namespace=json.loads((source/(base_names[world]+".json")).read_text())
    probe=json.loads((source/"namespace_probe.json").read_text())
    world_ns=namespace["metadata"]["name"]
    probe_ns=probe["metadata"]["name"]
    expected_before={"eeq.r2a/armed":"never"}
    expected_after={"eeq.r2a/armed":"gate"}
    record={
        "schema":"eeq-r2a-k8s-native-episode-v1",
        "world":world,
        "evidence_class":"CONTROLLED_NATIVE_INDEPENDENT_KIND_CLUSTER",
        "source_sha256":source_hashes,
        "native_oracle":"Kubernetes v1.35.0 API server server-side dry-run admission",
        "source_only_prediction_file_never_read":True,
        "observations":[],
        "activation_probe_attempts":[],
        "patch_result":None,
        "status":"IN_PROGRESS",
    }
    try:
        necessary(kubectl("apply","-f",source/(base_names[world]+".json")),
                  "CREATE_WORLD_NAMESPACE")
        necessary(kubectl("apply","-f",source/"namespace_probe.json"),
                  "CREATE_PROBE_NAMESPACE")
        create_sa(world_ns)
        create_sa(probe_ns)
        necessary(kubectl("apply","-f",source/"policy.json"),"INSTALL_REGISTERED_VAP")
        necessary(kubectl("apply","-f",source/"binding_initial.json"),
                  "INSTALL_REGISTERED_BINDING")
        before_binding=get("validatingadmissionpolicybinding",BINDING)
        before_policy=get("validatingadmissionpolicy",POLICY)
        before_world=get("namespace",world_ns)
        record["before_native_source"]={
            "binding_resourceVersion":before_binding["metadata"].get("resourceVersion"),
            "binding_selector":selector(before_binding),
            "namespace_labels":before_world["metadata"].get("labels",{}),
            "policy_generation":before_policy["metadata"].get("generation"),
            "policy_resourceVersion":before_policy["metadata"].get("resourceVersion"),
        }
        if selector(before_binding)!=expected_before:
            raise RuntimeError("INITIAL_BINDING_SOURCE_UNEXPECTED")
        for sa in SA:
            record["observations"].append(observe_pod(
                world_ns,sa,"CURRENT",world))

        # The very same patch JSON is executed in each isolated cluster.
        patch=mutation["patch_object"]
        p=kubectl("patch","validatingadmissionpolicybinding",BINDING,
                  "--type=merge","-p",json.dumps(patch,separators=(",",":")))
        record["patch_result"]=p
        necessary(p,"ACTUAL_NATIVE_BINDING_MUTATION_FAILURE")
        after_binding=get("validatingadmissionpolicybinding",BINDING)
        after_world=get("namespace",world_ns)
        record["after_native_source"]={
            "binding_resourceVersion":after_binding["metadata"].get("resourceVersion"),
            "binding_selector":selector(after_binding),
            "namespace_labels":after_world["metadata"].get("labels",{}),
        }
        if selector(after_binding)!=expected_after:
            raise RuntimeError("MUTATED_BINDING_NOT_OBSERVED")
        if (record["before_native_source"]["binding_resourceVersion"]==
            record["after_native_source"]["binding_resourceVersion"]):
            raise RuntimeError("NO_NATIVE_RESOURCE_VERSION_CHANGE")

        # Prove mutation has reached policy enforcement using a separate
        # preregistered namespace, NEVER by observing the target score rows.
        activated=False
        for attempt in range(1,61):
            probe_result=observe_pod(probe_ns,"flux","ACTIVATION_PROBE",world)
            record["activation_probe_attempts"].append({
                "attempt":attempt,
                "native_outcome":probe_result["native_outcome"],
                "native_attribution":probe_result["native_attribution"],
                "native_returncode":probe_result["native_returncode"],
            })
            if (probe_result["native_outcome"]=="REJECT" and
                probe_result["native_attribution"]=="REGISTERED_VAP"):
                activated=True
                break
            time.sleep(.5)
        record["activation_proven"]=activated
        if not activated:
            raise RuntimeError("POLICY_MUTATION_ACTIVATION_NOT_VERIFIED")

        for sa in SA:
            record["observations"].append(observe_pod(
                world_ns,sa,"AFTER_BINDING_MUTATION",world))
        record["status"]="NATIVE_EPISODE_COMPLETED"
    except Exception as exc:
        record["status"]="NATIVE_EPISODE_ERROR"
        record["error"]=str(exc)

    result_path=output/("R2A_NATIVE_"+world+".json")
    result_path.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n",
                           encoding="utf-8")
    print(json.dumps({
        "world":world,"status":record["status"],
        "observations":len(record["observations"]),
        "activation_proven":record.get("activation_proven",False),
        "error":record.get("error")},sort_keys=True))
    if record["status"]!="NATIVE_EPISODE_COMPLETED":
        raise SystemExit(2)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",required=True)
    p.add_argument("--world",choices=("WORLD_GATE","WORLD_STANDBY"),
                   required=True)
    p.add_argument("--out-dir",required=True)
    a=p.parse_args()
    run(a.source_dir,a.world,a.out_dir)


if __name__=="__main__":
    main()
