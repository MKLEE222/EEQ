#!/usr/bin/env python3
"""C1-W1 source-only frozen event/inventory plan; ZERO native or archived outputs read."""
import argparse, hashlib, json
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
SOURCES={
 "namespace.json":("r3_m1/sources/namespace.json","428f16bc92ac27dec26b87ad24951113cf463922"),
 "policy.json":("r3_m1/sources/policy.json","c22a8134447649d202a49b644ddb8485835c0fc2"),
 "binding-team.json":("r3_m1/sources/binding-team.json","2bc5a5706910196c5cd0631c4034ca3ccdbb890b"),
 "binding-mode.json":("r3_m1/sources/binding-mode.json","357ef4bd582f47e2308f6e640307077bafe47b68"),
 "policy-third.json":("r3_m3/sources/policy-third.json","ae7ab92b2d15f7793ec41232752efc2c30ebf347"),
 "binding-third.json":("r3_m3/sources/binding-third.json","e2a774ee92c2af6411e1a516e48af4695f096088"),
}
POLICY_API="/apis/admissionregistration.k8s.io/v1/validatingadmissionpolicies"
BINDING_API="/apis/admissionregistration.k8s.io/v1/validatingadmissionpolicybindings"
CLASSES={
 "policy":{"path":POLICY_API,"kind":"ValidatingAdmissionPolicyList"},
 "binding":{"path":BINDING_API,"kind":"ValidatingAdmissionPolicyBindingList"}
}
P0="eeq-r3-flux-deny"
P3="eeq-r3-m3-default-deny"
B0=("eeq-r3-binding-team","eeq-r3-binding-mode")
B3="eeq-r3-m3-binding-third"
STAGES=(
 ("S0_INITIAL", (P0,),B0),
 ("A1_POLICY_ADDED", (P0,P3),B0),
 ("A2_BINDING_ADDED", (P0,P3),B0+(B3,)),
 ("A3_BINDING_DELETED", (P0,P3),B0),
)
EVENTS=(
 {"step":"A1_POLICY_ADDED","class":"policy","type":"ADDED","name":P3},
 {"step":"A2_BINDING_ADDED","class":"binding","type":"ADDED","name":B3},
 {"step":"A3_BINDING_DELETED","class":"binding","type":"DELETED","name":B3},
)

def sha256(raw):
    return hashlib.sha256(raw).hexdigest()

def git_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def from_authoritative_sources():
    docs,files={},[]
    for name,(relative,pin) in SOURCES.items():
        raw=(BASE/relative).read_bytes()
        if git_sha(raw)!=pin:
            raise ValueError("SOURCE_GIT_BLOB_PIN_BROKEN:"+name)
        docs[name]=json.loads(raw)
        files.append({"name":name,"relative_repo_path":
             "experiments/native_distinction_relaunch/"+relative,
             "git_blob_sha":pin,"sha256":sha256(raw),"bytes":len(raw)})
    for name,expected in (
        ("policy.json",P0),("policy-third.json",P3),
        ("binding-team.json",B0[0]),("binding-mode.json",B0[1]),
        ("binding-third.json",B3)):
        if docs[name]["metadata"]["name"]!=expected:
            raise ValueError("SOURCE_IDENTITY_INVALID:"+name)
    for name in ("binding-team.json","binding-mode.json"):
        if docs[name]["spec"]["policyName"]!=P0:
            raise ValueError("M1_POLICY_BINDING_MISMATCH:"+name)
    if docs["binding-third.json"]["spec"]["policyName"]!=P3:
        raise ValueError("M3_POLICY_BINDING_MISMATCH")
    if docs["namespace.json"]["metadata"]["name"]!="eeq-r3":
        raise ValueError("M1_NAMESPACE_MISMATCH")
    manifest={
        "schema":"eeq-c1-w1-source-only-manifest-v1",
        "research_class":"CONTROLLED_DEVELOPMENT_WATCH_CURSOR_ONLY",
        "source_files":files,"new_native_decision_cells":0,
        "watched_api_source_classes":CLASSES,
        "source_model_native_observations_read":False,
        "main_v1_g5_increment":0,
    }
    return docs,manifest

def registered_forecast():
    docs,manifest=from_authoritative_sources()
    if len(EVENTS)!=3 or len(STAGES)!=4 or len(SOURCES)!=6:
        raise ValueError("FROZEN_DENOMINATOR_CHANGED")
    return manifest,{
        "schema":"eeq-c1-w1-source-only-forecast-v1",
        "registrations":{"watch_channels":2,"watch_events":3,
                         "full_list_snapshots":8,"native_mutations":3,
                         "native_decisions":0},
        "stages":[{"step":step,"expected_policy_names":sorted(policy),
                  "expected_binding_names":sorted(binding)}
                 for step,policy,binding in STAGES],
        "watch_events":list(EVENTS),
        "actor":"EPHEMERAL_KIND_CURRENT_ADMIN_KUBECONFIG",
        "source_only":True,"native_outcomes_read":False,
        "global_admission_accept_certified":False,
        "cross_class_atomic_snapshot_certified":False,
        "fully_informed_b9_entitled_same_tools":True,
        "scientific_ceiling":"C1_W1_SCOPED_NATIVE_LIST_WATCH_FEASIBILITY_B9_TIE"
    }

def write(out_dir):
    manifest,forecast=registered_forecast()
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    for name,data in (("SOURCE_MANIFEST.json",manifest),("SOURCE_EVENTS_ONLY.json",forecast)):
        (out/name).write_text(json.dumps(data,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    with (out/"SOURCE_SHA256.txt").open("w") as f:
        for name in ("SOURCE_MANIFEST.json","SOURCE_EVENTS_ONLY.json"):
            f.write(sha256((out/name).read_bytes())+"  "+name+"\n")
    print(json.dumps({"state":"C1_W1_SOURCE_ONLY_BEFORE_NATIVE",
        "registered_events":3,"registered_list_snapshots":8,
        "watch_streams":2,"native_scored_decisions":0,"g5_increment":0},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    write(args.out)
