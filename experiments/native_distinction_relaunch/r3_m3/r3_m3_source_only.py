#!/usr/bin/env python3
"""M3 source-only: prospective third-binding membership contrast.

Never loads native observations nor previous M1/M2 predictions.
Extracts from eight pinned JSON Kubernetes policy/binding/namespace/Pod
sources plus three predeclared source-membership events.
Fail-closed on unregistered CEL, actors, selector syntax or policy scope.
"""
import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path

OLD = ("policy.json", "binding-team.json", "binding-mode.json",
       "namespace.json", "pod-flux.json", "pod-default.json")
NEW = ("policy-third.json", "binding-third.json")
ALL = OLD + NEW
PHASES = ("T0_OLD_TWO_BINDINGS","T1_THIRD_POLICY_UNBOUND",
          "T2_THIRD_BINDING_ACTIVE","T3_THIRD_BINDING_REMOVED")
PODS = ("flux","default")
OLD_POLICY="eeq-r3-flux-deny"
THIRD_POLICY="eeq-r3-m3-default-deny"
OLD_BINDINGS=("eeq-r3-binding-team","eeq-r3-binding-mode")
THIRD_BINDING="eeq-r3-m3-binding-third"
SOURCE_SUBDIR="experiments/native_distinction_relaunch/r3_m1/sources"
THIRD_SUBDIR="experiments/native_distinction_relaunch/r3_m3/sources"


class UnsupportedMechanism(Exception):
    pass


def refuse(reason):
    raise UnsupportedMechanism(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(repo_root):
    root=Path(repo_root)
    sources={}
    for name in OLD:
        sources[name]=(root/SOURCE_SUBDIR/name).read_bytes()
    for name in NEW:
        sources[name]=(root/THIRD_SUBDIR/name).read_bytes()
    docs={name:json.loads(raw) for name,raw in sources.items()}
    return sources,docs


def policy_definition(policy,name,blocked):
    spec=policy.get("spec",{})
    expected_rule={
        "apiGroups":[""],"apiVersions":["v1"],
        "operations":["CREATE"],"resources":["pods"],
    }
    if (policy.get("kind")!="ValidatingAdmissionPolicy" or
        policy.get("apiVersion")!="admissionregistration.k8s.io/v1" or
        policy.get("metadata",{}).get("name")!=name or
        set(spec)!= {"failurePolicy","matchConstraints","validations"} or
        spec["failurePolicy"]!="Fail" or
        spec["matchConstraints"]!={"resourceRules":[expected_rule]} or
        spec["validations"]!=[{
            "expression":"object.spec.serviceAccountName != '"+blocked+"'",
            "message":("EEQ_R3_FLUX_SA_DENIED" if blocked=="flux" else
                       "EEQ_R3_M3_DEFAULT_SA_DENIED"),
            "reason":"Forbidden",
        }]):
        refuse("UNSUPPORTED_OR_UNREGISTERED_POLICY_"+name)
    return {"name":name,"blocked_sa":blocked}


def binding_definition(binding,name,policy):
    spec=binding.get("spec",{})
    if (binding.get("kind")!="ValidatingAdmissionPolicyBinding" or
        binding.get("apiVersion")!="admissionregistration.k8s.io/v1" or
        binding.get("metadata",{}).get("name")!=name or
        set(spec)!={"policyName","validationActions","matchResources"} or
        spec["policyName"]!=policy or
        spec["validationActions"]!=["Deny"]):
        refuse("UNSUPPORTED_OR_UNREGISTERED_BINDING_"+name)
    match=spec["matchResources"]
    if (set(match)!={"namespaceSelector"} or
        set(match["namespaceSelector"])!={"matchLabels"}):
        refuse("UNSUPPORTED_BINDING_SELECTOR_"+name)
    labels=match["namespaceSelector"]["matchLabels"]
    if (not isinstance(labels,dict) or not labels or
        not all(isinstance(k,str) and isinstance(v,str) for k,v in
                labels.items())):
        refuse("MALFORMED_BINDING_SELECTOR_"+name)
    expected={
        "eeq-r3-binding-team":{"r3.team":"tenant"},
        "eeq-r3-binding-mode":{"r3.mode":"strict"},
        THIRD_BINDING:{"r3.team":"tenant"},
    }
    if labels!=expected[name]:
        refuse("FROZEN_BOUND_SOURCE_SELECTOR_CHANGED_"+name)
    return {"name":name,"policy":policy,"selector":labels}


def extract(docs):
    policies={
        OLD_POLICY:policy_definition(docs["policy.json"],OLD_POLICY,"flux"),
        THIRD_POLICY:policy_definition(docs["policy-third.json"],
                                       THIRD_POLICY,"default"),
    }
    bindings={
        OLD_BINDINGS[0]:binding_definition(docs["binding-team.json"],
                                           OLD_BINDINGS[0],OLD_POLICY),
        OLD_BINDINGS[1]:binding_definition(docs["binding-mode.json"],
                                           OLD_BINDINGS[1],OLD_POLICY),
        THIRD_BINDING:binding_definition(docs["binding-third.json"],
                                         THIRD_BINDING,THIRD_POLICY),
    }
    namespace=docs["namespace.json"]
    labels=namespace.get("metadata",{}).get("labels")
    if (namespace.get("apiVersion")!="v1" or
        namespace.get("kind")!="Namespace" or
        namespace["metadata"].get("name")!="eeq-r3" or
        labels!={"r3.team":"tenant","r3.mode":"strict"}):
        refuse("UNREGISTERED_NAMESPACE")
    for who in PODS:
        pod=docs["pod-"+who+".json"]
        if (pod.get("apiVersion")!="v1" or pod.get("kind")!="Pod" or
            pod.get("metadata",{}).get("name")!="eeq-r3-"+who+"-probe" or
            pod["metadata"].get("namespace")!="eeq-r3" or
            pod.get("spec",{}).get("serviceAccountName")!=who or
            not pod.get("spec",{}).get("containers")):
            refuse("UNREGISTERED_POD_"+who)
    return policies,bindings,labels


def phases():
    return [
        {"phase":PHASES[0],"policies":[OLD_POLICY],
         "bindings":list(OLD_BINDINGS),"last_native_action":"SETUP_OLD_TWO_BINDINGS"},
        {"phase":PHASES[1],"policies":[OLD_POLICY,THIRD_POLICY],
         "bindings":list(OLD_BINDINGS),"last_native_action":"CREATE_3RD_VAP"},
        {"phase":PHASES[2],"policies":[OLD_POLICY,THIRD_POLICY],
         "bindings":list(OLD_BINDINGS)+[THIRD_BINDING],
         "last_native_action":"CREATE_3RD_BINDING"},
        {"phase":PHASES[3],"policies":[OLD_POLICY,THIRD_POLICY],
         "bindings":list(OLD_BINDINGS),
         "last_native_action":"DELETE_3RD_BINDING"},
    ]


def decision(policies,bindings,labels,phase,who):
    active=[]
    for name in phase["bindings"]:
        binder=bindings[name]
        if binder["policy"] not in phase["policies"]:
            refuse("BINDING_HAS_NO_REGISTERED_POLICY")
        if all(labels.get(k)==v for k,v in binder["selector"].items()):
            if policies[binder["policy"]]["blocked_sa"]==who:
                active.append({"binding_name":name,"policy_name":binder["policy"],
                               "predicate_false":True})
    return ("REJECT" if active else "ACCEPT"),active


def predict(docs):
    policies,bindings,labels=extract(docs)
    phase_list=phases()
    rows=[]
    for entry in phase_list:
        for who in PODS:
            result,witness=decision(policies,bindings,labels,entry,who)
            rows.append({"phase":entry["phase"],"probe":who,
                "source_expected_effect":result,
                "known_qualifying_deny_sources":witness,
                "current_registered_binding_names":entry["bindings"],
                "current_registered_policy_names":entry["policies"]})
    if (len(rows)!=8 or
        [r["source_expected_effect"] for r in rows]!=[
            "REJECT","ACCEPT","REJECT","ACCEPT",
            "REJECT","REJECT","REJECT","ACCEPT"]):
        refuse("FROZEN_EXPECTED_CONTRAST_NOT_INSTANTIATED")
    old_model=lambda who:"REJECT" if who=="flux" else "ACCEPT"
    weak=sum(r["source_expected_effect"]==old_model(r["probe"]) for r in rows)
    if weak!=7: refuse("MISSING_INVENTORY_GROWTH_COLLISION")
    return {
        "schema":"eeq-r3-m3-source-only-membership-predictions-v1",
        "evidence_class":"CONTROLLED_NATIVE_DEVELOPMENT",
        "source_only_no_native_labels":True,
        "new_native_calls":0,
        "observed_labels_read":False,
        "registered_phases":phase_list,
        "registered_native_actions":["CREATE_3RD_VAP",
            "CREATE_3RD_BINDING","DELETE_3RD_BINDING"],
        "registered_native_cases":rows,
        "original_old_binding_sources_remain_unchanged":True,
        "old_accept_default_invalidated_in_T2":True,
        "third_policy_without_binding_is_inert":True,
        "third_binding_deletion_restores_default":True,
        "strong_B9_full_inventory":{
            "expected_native_matches":8,"registered":8,
            "same_sources_as_candidate":True,
            "allowed_standard_list_watch_and_rule_evaluation":True},
        "weak_cached_old_inventory":{
            "source_expected_matches":weak,"registered":8,
            "not_strong_B9":True},
        "controls":{"unbound_pod_count":2,
                    "membership_actions":3,
                    "native_inventories":4},
        "original_v1_g5_increment":0,
        "limits":["Only registered VAP policy/binding effects",
                  "Not universal Kubernetes admission acceptance",
                  "Native list snapshots not a continuous watch",
                  "Independent B9 can use full registry and same semantics"],
    }


def build(repo_root):
    sources,docs=load(repo_root)
    model=predict(docs)
    manifest={
        "schema":"eeq-r3-m3-source-manifest-v1",
        "source_count":len(sources),
        "sources":[{"name":name,"bytes":len(sources[name]),
                    "sha256":sha(sources[name])} for name in ALL],
        "native_calls":0,"native_labels_read":False,
        "evidence_class":"CONTROLLED_NATIVE_DEVELOPMENT",
        "original_v1_g5_increment":0,
    }
    return sources,manifest,model


def write(repo_root,out_dir):
    sources,manifest,pred=build(repo_root)
    root=Path(out_dir)
    (root/"sources").mkdir(parents=True,exist_ok=True)
    for name,raw in sources.items():
        (root/"sources"/name).write_bytes(raw)
    (root/"SOURCE_MANIFEST.json").write_text(
        json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    (root/"SOURCE_PREDICTIONS.json").write_text(
        json.dumps(pred,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "source_files":len(sources),
        "scored_predictions":len(pred["registered_native_cases"]),
        "native_predicted_reject":sum(r["source_expected_effect"]=="REJECT"
                                      for r in pred["registered_native_cases"]),
        "native_predicted_accept":sum(r["source_expected_effect"]=="ACCEPT"
                                      for r in pred["registered_native_cases"]),
        "full_B9_source_expected":pred["strong_B9_full_inventory"][
            "expected_native_matches"],
        "old_inventory_weak_ablation":pred["weak_cached_old_inventory"][
            "source_expected_matches"],
        "new_native_calls":0},sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",default=".")
    p.add_argument("--out",required=True)
    a=p.parse_args()
    write(a.repo_root,a.out)


if __name__=="__main__":
    main()
