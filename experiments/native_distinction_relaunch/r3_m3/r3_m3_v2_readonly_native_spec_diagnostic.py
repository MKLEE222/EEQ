#!/usr/bin/env python3
"""M3 V2 POST-NATIVE FORENSICS ONLY. No Kubernetes / no re-scoring.

Compare original SHA-frozen policy/binding JSON to raw API LIST objects,
show all structural differences and all exact archived primary observations.
Does NOT modify model, native, or scorer.
"""
import argparse
import hashlib
import json
from pathlib import Path

def sha(b):
    return hashlib.sha256(b).hexdigest()

def differences(source,live,prefix=""):
    if isinstance(source,dict) and isinstance(live,dict):
        out=[]
        for key in sorted(set(source)|set(live)):
            sub=prefix+"."+key if prefix else key
            if key not in source:
                out.append({"path":sub,"kind":"NATIVE_ONLY","native":live[key]})
            elif key not in live:
                out.append({"path":sub,"kind":"SOURCE_ONLY","source":source[key]})
            else:
                out+=differences(source[key],live[key],sub)
        return out
    if isinstance(source,list) and isinstance(live,list):
        out=[]
        if len(source)!=len(live):
            out.append({"path":prefix+".length",
                "source":len(source),"native":len(live),"kind":"LENGTH_DIFFERENT"})
        for i,(a,b) in enumerate(zip(source,live)):
            out+=differences(a,b,prefix+"["+str(i)+"]")
        return out
    return [] if source==live else [{
        "path":prefix,"kind":"VALUE_DIFFERENT","source":source,"native":live
    }]

def analyze(native,manifest,sources):
    assert native["schema"]=="eeq-r3-m3-native-third-membership-v1"
    assert native["source_predictions_read"] is False
    assert native["registered_primary_rows"]==8
    assert native["observed_primary_rows"]==8
    assert len(native["phase_inventories"])==4
    assert len(native["native_membership_actions"])==3
    assert len(native["control_rows"])==2
    rows=manifest["sources"]
    assert len(rows)==8
    docs={}
    for item in rows:
        raw=(sources/item["name"]).read_bytes()
        assert sha(raw)==item["sha256"] and len(raw)==item["bytes"]
        docs[item["name"]]=json.loads(raw)
    names={
        "eeq-r3-flux-deny":"policy.json",
        "eeq-r3-m3-default-deny":"policy-third.json",
        "eeq-r3-binding-team":"binding-team.json",
        "eeq-r3-binding-mode":"binding-mode.json",
        "eeq-r3-m3-binding-third":"binding-third.json"
    }
    diagnostics={}
    for phase in native["phase_inventories"]:
        p=phase["phase"]
        snapshot=phase["native_inventory"]
        entries=[]
        for collection in ("policy_items","binding_items"):
            for x in snapshot[collection]:
                f=names.get(x["name"])
                if not f:
                    continue
                delta=differences(docs[f]["spec"],x["spec"],"spec")
                entries.append({
                    "kind":collection,
                    "native_object":x["name"],
                    "original_source_file":f,
                    "uid":x["uid"],
                    "native_resource_version":x["resource_version"],
                    "spec_delta_count":len(delta),
                    "spec_deltas":delta
                })
        diagnostics[p]={
            "policy_list_rv":snapshot["policy_list_resource_version"],
            "binding_list_rv":snapshot["binding_list_resource_version"],
            "objects":entries
        }
    return {
        "schema":"eeq-r3-m3-v2-retrospective-source-default-diagnostic-v1",
        "raw_source_manifest_sha256":sha(json.dumps(manifest,sort_keys=True).encode()),
        "native_error":native["error"],
        "native_did_not_read_predictions":True,
        "phase_differences":diagnostics,
        "native_main_observations":[{
            "phase":x["phase"],"probe":x["probe"],
            "native_outcome":x["native_outcome"],
            "native_attribution":x["native_attribution"],
            "native_exit_code":x["native_exit_code"],
        } for x in native["observed_cases"]],
        "unbound_controls":[{
            "probe":x["probe"],"outcome":x["native_outcome"]
        } for x in native["control_rows"]],
        "native_membership_actions":[{
            "action":x["action"],
            "verified":x["actual_membership_change_verified"],
        } for x in native["native_membership_actions"]],
        "new_native_calls":0,
        "scientific_status":"FORENSIC_DIAGNOSTIC_NOT_PRESCORED_SUCCESS"
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--native",required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--sources",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    payload=analyze(json.loads(Path(a.native).read_text()),
                    json.loads(Path(a.manifest).read_text()),
                    Path(a.sources))
    Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    first=next(iter(payload["phase_differences"].values()))
    print(json.dumps({
        "native_error":payload["native_error"],
        "cases":payload["native_main_observations"],
        "controls":payload["unbound_controls"],
        "actions":payload["native_membership_actions"],
        "first_phase_source_vs_native_deltas":{
            item["native_object"]:item["spec_deltas"] for item in first["objects"]
        },
        "later_source_vs_native_delta_counts":{
            phase:{item["native_object"]:item["spec_delta_count"]
                   for item in entry["objects"]}
            for phase,entry in payload["phase_differences"].items()
        },
        "status":payload["scientific_status"]
    },sort_keys=True))

if __name__=="__main__":
    main()
