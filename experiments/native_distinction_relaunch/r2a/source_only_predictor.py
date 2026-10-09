#!/usr/bin/env python3
"""R2-A VAP/binding source-only prediction. NO kubectl, native API or labels."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

FILES=("policy","binding_initial","binding_after","namespace_gate",
       "namespace_standby","namespace_probe","binding_mutation","challenges")
EXPECTED_CEL="object.spec.serviceAccountName != 'flux'"
LABEL="eeq.r2a/armed"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def merge(target,patch):
    if not isinstance(patch,dict):
        return copy.deepcopy(patch)
    result=copy.deepcopy(target) if isinstance(target,dict) else {}
    for k,v in patch.items():
        if v is None:
            result.pop(k,None)
        else:
            result[k]=merge(result.get(k),v)
    return result


def derive(sources,raw_sha):
    pol=sources["policy"]
    initial=sources["binding_initial"]
    future=sources["binding_after"]
    patch=sources["binding_mutation"]
    ch=sources["challenges"]
    require(pol.get("kind")=="ValidatingAdmissionPolicy" and
            pol["metadata"]["name"]=="eeq-r2a-flux-constraint",
            "WRONG_POLICY_KIND_OR_ID")
    spec=pol["spec"]
    require(spec["failurePolicy"]=="Fail" and
            len(spec["validations"])==1 and
            spec["validations"][0]["expression"]==EXPECTED_CEL and
            spec["validations"][0]["message"]=="EEQ_R2A_REGISTERED_FLUX_DENIAL",
            "UNREGISTERED_POLICY_VALIDATION")
    rr=spec["matchConstraints"]["resourceRules"]
    require(rr==[{"apiGroups":[""],"apiVersions":["v1"],
                  "operations":["CREATE"],"resources":["pods"]}],
            "POLICY_RESOURCES_NOT_REGISTERED")
    for b in (initial,future):
        require(b["kind"]=="ValidatingAdmissionPolicyBinding" and
                b["metadata"]["name"]=="eeq-r2a-flux-binding" and
                b["spec"]["policyName"]=="eeq-r2a-flux-constraint" and
                b["spec"]["validationActions"]==["Deny"],
                "POLICY_BINDING_MISMATCH")
    require(patch.get("resource_name")=="eeq-r2a-flux-binding" and
            patch.get("patch_type")=="merge",
            "MUTATION_TARGET_NOT_REGISTERED")
    require(merge(initial,patch["patch_object"])==future,
            "FUTURE_BINDING_NOT_EXACT_MUTATION_RESULT")
    def selector(b):
        return b["spec"]["matchResources"]["namespaceSelector"]["matchLabels"]
    require(selector(initial)=={LABEL:"never"} and
            selector(future)=={LABEL:"gate"},
            "SELECTOR_MUTATION_NOT_FROZEN")

    require(ch.get("service_accounts")==["flux","default"] and
            ch.get("horizon_binding_patch_actions")==1 and
            ch.get("operation")=="Pod CREATE" and
            ch.get("target_policy_name")=="eeq-r2a-flux-constraint",
            "REQUEST_SCOPE_NOT_FROZEN")
    worlds={"WORLD_GATE":sources["namespace_gate"],
            "WORLD_STANDBY":sources["namespace_standby"]}
    require(
      worlds["WORLD_GATE"]["metadata"]["labels"].get(LABEL)=="gate"
      and worlds["WORLD_STANDBY"]["metadata"]["labels"].get(LABEL)=="standby",
      "WORLD_QUALIFICATION_SOURCES_NOT_DISTINCT")
    for name,obj in worlds.items():
        require(obj["kind"]=="Namespace" and
                obj["metadata"]["name"].startswith("eeq-r2a-"),
                "UNREGISTERED_WORLD_NAMESPACE")
    require(sources["namespace_probe"]["metadata"]["labels"].get(LABEL)=="gate",
            "MISSING_INDEPENDENT_ACTIVATION_PROBE")

    rows=[]
    for world,namespace in worlds.items():
        labels=namespace["metadata"]["labels"]
        for phase,b in (("CURRENT",initial),("AFTER_BINDING_MUTATION",future)):
            matched=all(labels.get(k)==v for k,v in selector(b).items())
            for sa in ch["service_accounts"]:
                status="REJECT" if matched and sa=="flux" else "ACCEPT"
                rows.append({
                    "world":world,"namespace":namespace["metadata"]["name"],
                    "phase":phase,"action":"Pod CREATE",
                    "service_account":sa,
                    "qualified_binding_applies":matched,
                    "expected_native":status,
                    "mechanism":"eeq-r2a-flux-constraint"
                })
    def v(world,phase):
        return tuple(x["expected_native"] for x in rows
                     if x["world"]==world and x["phase"]==phase)
    initial_same=v("WORLD_GATE","CURRENT")==v("WORLD_STANDBY","CURRENT")
    future_diff=v("WORLD_GATE","AFTER_BINDING_MUTATION")!=v(
        "WORLD_STANDBY","AFTER_BINDING_MUTATION")
    require(initial_same and future_diff,"FROZEN_A_CONTRAST_INCONSISTENT")
    require(v("WORLD_GATE","CURRENT")==("ACCEPT","ACCEPT"),"WRONG_CURRENT_GATE")
    require(v("WORLD_STANDBY","CURRENT")==("ACCEPT","ACCEPT"),"WRONG_CURRENT_STANDBY")
    require(v("WORLD_GATE","AFTER_BINDING_MUTATION")==("REJECT","ACCEPT"),
            "WRONG_FUTURE_GATE")
    require(v("WORLD_STANDBY","AFTER_BINDING_MUTATION")==("ACCEPT","ACCEPT"),
            "WRONG_FUTURE_STANDBY")
    return {
        "schema":"eeq-r2a-source-only-v1",
        "evidence_class":"CONTROLLED_SOURCE_ONLY_DEVELOPMENT",
        "source_sha256":raw_sha,
        "target_policy":"eeq-r2a-flux-constraint",
        "registered_worlds":list(worlds),
        "future_mutation":"PATCH_BINDING_SELECTOR_TO_GATE",
        "fixed_challenges":["Pod CREATE flux","Pod CREATE default"],
        "registered_horizon":1,
        "case_count":len(rows),
        "rows":rows,
        "current_decisions_equal":initial_same,
        "after_same_mutation_decisions_differ":future_diff,
        "strong_b9_with_full_source_information_correct":True,
        "no_novelty_advantage_over_B9_claimed":True,
        "no_native_calls":True,
        "native_scored_rows":0,
        "G4_v1_unchanged":True
    }


def load(directory):
    sources={}
    hashes={}
    for name in FILES:
        data=(Path(directory)/(name+".json")).read_bytes()
        sources[name]=json.loads(data)
        hashes[name]=hashlib.sha256(data).hexdigest()
    return sources,hashes


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    sources,hashes=load(args.source_dir)
    answer=derive(sources,hashes)
    Path(args.out).write_text(json.dumps(answer,indent=2,sort_keys=True)+"\n",
                              encoding="utf-8")
    print(json.dumps({
        "cases":answer["case_count"],
        "current_equal":answer["current_decisions_equal"],
        "future_different":answer["after_same_mutation_decisions_differ"],
        "native_scored":answer["native_scored_rows"],
        "strong_b9_tie":answer["strong_b9_with_full_source_information_correct"],
    },sort_keys=True))


if __name__=="__main__":
    main()
