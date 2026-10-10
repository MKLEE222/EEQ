#!/usr/bin/env python3
"""R3-M3 immutable JOIN-ONLY scorer and fair registry-aware native B9.

The source predictor and native runner never import one another.
This scorer never changes files or runs kubectl. Native labels are used
solely here after their archive exists.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

PHASES=("T0_OLD_TWO_BINDINGS","T1_THIRD_POLICY_UNBOUND",
        "T2_THIRD_BINDING_ACTIVE","T3_THIRD_BINDING_REMOVED")
PROBES=("flux","default")
OLD=("eeq-r3-binding-mode","eeq-r3-binding-team")
THIRD="eeq-r3-m3-binding-third"
OLD_POLICY="eeq-r3-flux-deny"
THIRD_POLICY="eeq-r3-m3-default-deny"
NAMES=("policy.json","binding-team.json","binding-mode.json",
       "namespace.json","pod-flux.json","pod-default.json",
       "policy-third.json","binding-third.json")


def insist(ok,why):
    if not ok:
        raise ValueError(why)


def uniq(rows,key):
    d={}
    for row in rows:
        k=key(row)
        insist(k not in d,"DUPLICATE_"+str(k))
        d[k]=row
    return d


def native_named(snapshot,what):
    key="binding_items" if what=="binding" else "policy_items"
    return {
        x["name"]:x for x in snapshot[key]
        if x["name"].startswith("eeq-r3-")
    }


def native_B9(snapshot,sa,labels):
    """FULLY INFORMED B9 with all live policy/binding sources.

    Does not consult scored native Pod effects. It can use all matching
    policies, current selectors and CEL on same lawful information.
    Hand-engineered reference, not independent maintainer-time evidence.
    """
    policies=native_named(snapshot,"policy")
    bindings=native_named(snapshot,"binding")
    eligible=[]
    for name,binding in sorted(bindings.items()):
        spec=binding["spec"]
        insist(spec.get("validationActions")==["Deny"],
               "B9_UNSUPPORTED_VALIDATION_ACTION")
        policy_name=spec["policyName"]
        insist(policy_name in policies,"B9_MISSING_POLICY_SOURCE")
        selector=spec.get("matchResources",{}).get(
            "namespaceSelector",{}).get("matchLabels")
        insist(isinstance(selector,dict) and selector,
               "B9_UNSUPPORTED_SELECTOR")
        if not all(labels.get(k)==v for k,v in selector.items()):
            continue
        policy=policies[policy_name]["spec"]
        validations=policy.get("validations",[])
        insist(len(validations)==1,
               "B9_UNSUPPORTED_POLICY_VALIDATION_COUNT")
        expression=validations[0].get("expression")
        if expression=="object.spec.serviceAccountName != 'flux'":
            failing=sa=="flux"
        elif expression=="object.spec.serviceAccountName != 'default'":
            failing=sa=="default"
        else:
            raise ValueError("B9_UNSUPPORTED_POLICY_CEL")
        if failing: eligible.append((name,policy_name))
    return ("REJECT" if eligible else "ACCEPT"),eligible


def check_native_source_spec(item,source):
    """API server can add defaults; require all registered material fields."""
    live=item["spec"]
    original=source["spec"]
    kind=source["kind"]
    if kind=="ValidatingAdmissionPolicy":
        insist(live.get("failurePolicy")==original.get("failurePolicy") and
               live.get("validations")==original.get("validations") and
               live.get("matchConstraints",{}).get("resourceRules")==
               original.get("matchConstraints",{}).get("resourceRules"),
               "NATIVE_VAP_POLICY_SPEC_NOT_MATCHING_FROZEN_SOURCE")
    else:
        insist(live.get("policyName")==original.get("policyName") and
               live.get("validationActions")==original.get("validationActions") and
               live.get("matchResources",{}).get(
                   "namespaceSelector",{}).get("matchLabels")==
               original.get("matchResources",{}).get(
                   "namespaceSelector",{}).get("matchLabels"),
               "NATIVE_VAP_BINDING_SPEC_NOT_MATCHING_FROZEN_SOURCE")


def score(pred,manifest,native,docs):
    insist(pred.get("schema")==
           "eeq-r3-m3-source-only-membership-predictions-v1",
           "INVALID_SOURCE_PREDICTION_SCHEMA")
    insist(manifest.get("schema")=="eeq-r3-m3-source-manifest-v1" and
           manifest.get("source_count")==8,"INVALID_SOURCE_MANIFEST")
    insist(native.get("schema")=="eeq-r3-m3-native-third-membership-v1",
           "INVALID_NATIVE_SCHEMA")
    insist(pred.get("source_only_no_native_labels") is True and
           pred.get("new_native_calls")==0 and
           native.get("source_predictions_read") is False and
           native.get("original_v1_g5_increment")==0,
           "SOURCE_NATIVE_LABEL_LEAK_OR_G5_MUTATION")
    hashes={x["name"]:x["sha256"] for x in manifest["sources"]}
    insist(len(hashes)==len(manifest["sources"])==8 and
           set(hashes)==set(NAMES),"SOURCE_IDENTITY_INCOMPLETE")
    insist(native["source_digest_map"]==hashes,"NATIVE_SOURCE_HASH_MISMATCH")
    for name in NAMES:
        insist(name in docs,"MISSING_SOURCE_DOCUMENT_"+name)
    labels=docs["namespace.json"]["metadata"]["labels"]
    insist(labels=={"r3.team":"tenant","r3.mode":"strict"},
           "REGISTERED_NAMESPACE_CHANGED")

    original=uniq(pred["registered_native_cases"],
                  lambda r:(r["phase"],r["probe"]))
    observed=uniq(native["observed_cases"],
                  lambda r:(r["phase"],r["probe"]))
    cases={(t,p) for t in PHASES for p in PROBES}
    insist(set(original)==set(observed)==cases and
           native["registered_primary_rows"]==8,
           "EIGHT_REGISTERED_NATIVE_CELLS_NOT_COMPLETE")
    ctrls=uniq(native["control_rows"],lambda r:r["probe"])
    insist(set(ctrls)==set(PROBES) and
           native["registered_control_rows"]==2,
           "TWO_NATIVE_NO_BINDING_CONTROLS_MISSING")
    controls=[]
    for who in PROBES:
        r=ctrls[who]
        controls.append({"probe":who,"native":r["native_outcome"],
            "pass":r["native_outcome"]=="ACCEPT" and
            r["native_attribution"]=="ADMITTED" and
            r["source_pod_sha256"]==hashes["pod-"+who+".json"]})
    insist(native["error"] is None and
           native["original_binding_native_ids_unchanged"] is True,
           "NATIVE_STATE_MUTATION_INTEGRITY_FAILURE")
    phases=uniq(native["phase_inventories"],lambda r:r["phase"])
    insist(set(phases)==set(PHASES) and
           native["registered_inventory_snapshots"]==4,
           "FOUR_NATIVE_LIST_SNAPSHOTS_MISSING")
    actions=native["native_membership_actions"]
    insist(len(actions)==native["registered_native_membership_actions"]==3,
           "THREE_REGISTERED_REAL_NATIVE_ACTIONS_MISSING")
    insist([x["action"] for x in actions]==[
        "CREATE_3RD_VAP","CREATE_3RD_BINDING","DELETE_3RD_BINDING"
    ] and all(x["actual_membership_change_verified"] and
              x["command_result"]["returncode"]==0 for x in actions),
           "REAL_THIRD_SOURCE_CREATE_DELETE_ACTIONS_UNVERIFIED")
    expected_p=[
        [OLD_POLICY],
        [OLD_POLICY,THIRD_POLICY],
        [OLD_POLICY,THIRD_POLICY],
        [OLD_POLICY,THIRD_POLICY],
    ]
    expected_b=[
        list(OLD),list(OLD),list(OLD)+[THIRD],list(OLD),
    ]
    inv_records=[]
    old_identity=None
    for i,phase in enumerate(PHASES):
        inv=phases[phase]["native_inventory"]
        policy=native_named(inv,"policy")
        binding=native_named(inv,"binding")
        insist(sorted(policy)==sorted(expected_p[i]) and
               sorted(binding)==sorted(expected_b[i]),
               "NATIVE_MEMBERSHIP_NOT_EQUAL_REGISTERED_PHASE_"+phase)
        insist(bool(inv.get("policy_list_resource_version")) and
               bool(inv.get("binding_list_resource_version")),
               "NATIVE_SOURCE_LIST_RV_MISSING")
        identity={
            name:(binding[name]["uid"],binding[name]["spec_sha256"],
                  binding[name]["resource_version"])
            for name in OLD
        }
        if old_identity is None:old_identity=identity
        insist(identity==old_identity,"ORIGINAL_TWO_BINDINGS_CHANGED")
        for name,item in policy.items():
            expected_file=("policy.json" if name==OLD_POLICY else
                           "policy-third.json")
            check_native_source_spec(item,docs[expected_file])
        for name,item in binding.items():
            expected_file={
                OLD[0]:"binding-mode.json",OLD[1]:"binding-team.json",
                THIRD:"binding-third.json"
            }[name]
            check_native_source_spec(item,docs[expected_file])
        inv_records.append({
            "phase":phase,"policies":sorted(policy),
            "bindings":sorted(binding),
            "policy_list_resourceVersion":
                inv["policy_list_resource_version"],
            "binding_list_resourceVersion":
                inv["binding_list_resource_version"]})
    # List resourceVersion is OPAQUE. Only equality and membership checked.
    insist(inv_records[0]["policy_list_resourceVersion"]!=
           inv_records[1]["policy_list_resourceVersion"] and
           inv_records[1]["binding_list_resourceVersion"]!=
           inv_records[2]["binding_list_resourceVersion"] and
           inv_records[2]["binding_list_resourceVersion"]!=
           inv_records[3]["binding_list_resourceVersion"],
           "LIVE_INVENTORY_RESOURCE_VERSION_NOT_UPDATED")

    checks=[]
    b9_matches=0
    for phase in PHASES:
        inv=phases[phase]["native_inventory"]
        for probe in PROBES:
            source=original[phase,probe]
            actual=observed[phase,probe]
            b9,witness=native_B9(inv,probe,labels)
            if b9==actual["native_outcome"]:
                b9_matches+=1
            eligible=source["source_expected_effect"]
            native_value=actual["native_outcome"]
            expected_attr=("REGISTERED_THIRD_VAP_DENY" if
                eligible=="REJECT" and probe=="default" else
                "REGISTERED_OLD_VAP_DENY" if eligible=="REJECT" else
                "ADMITTED")
            good=(actual["source_pod_sha256"]==
                  hashes["pod-"+probe+".json"] and
                  eligible==native_value and
                  expected_attr==actual["native_attribution"] and
                  b9==eligible and
                  actual["native_exit_code"]==(0 if eligible=="ACCEPT" else 1)
                  )
            checks.append({
                "phase":phase,"probe":probe,
                "frozen_source_prediction":eligible,
                "observed_native":native_value,
                "native_attribution":actual["native_attribution"],
                "fully_informed_B9_decision":b9,
                "B9_support":witness,
                "status":"MATCH" if good else
                "AMBIGUOUS" if native_value=="NATIVE_ORACLE_AMBIGUOUS"
                else "MISMATCH",
            })
    hist=Counter(row["status"] for row in checks)
    valid=(
        hist==Counter({"MATCH":8}) and
        all(x["pass"] for x in controls) and
        b9_matches==8 and
        original["T0_OLD_TWO_BINDINGS","default"]["source_expected_effect"]==
        "ACCEPT" and
        original["T2_THIRD_BINDING_ACTIVE","default"][
            "source_expected_effect"]=="REJECT" and
        original["T3_THIRD_BINDING_REMOVED","default"][
            "source_expected_effect"]=="ACCEPT" and
        native["source_predictions_read"] is False)
    return {
        "schema":"eeq-r3-m3-native-membership-C1-score-v1",
        "all_native_cases":checks,
        "native_unbound_controls":controls,
        "native_inventory_membership_evidence":inv_records,
        "native_real_actions":[{
            "name":a["action"],
            "verified":a["actual_membership_change_verified"],
        } for a in actions],
        "summary":{
            "registered_cases":8,"matched_cases":hist["MATCH"],
            "mismatched_cases":hist["MISMATCH"],
            "ambiguous_cases":hist["AMBIGUOUS"],
            "unbound_controls_total":2,
            "unbound_controls_passed":sum(x["pass"] for x in controls),
            "actual_native_membership_changes":len(actions),
            "native_full_inventory_snapshots":4,
            "old_source_identities_stable":True,
            "cached_positive_default_certificate_invalidated":
                checks[5]["observed_native"]=="REJECT",
            "full_information_B9_native_matches":b9_matches,
            "full_information_B9_total":8,
            "stale_old_only_weak_ablation_source_matches":7,
            "v1_original_g5_increment":0,
            "new_method_unique_advantage":False,
            "global_k8s_C1_supported":False,
            "general_semantic_adapter_proven":False,
            "scientific_status":(
                "R3_M3_CONTROLLED_NATIVE_STALE_ACCEPT_INVENTORY_COLLISION_B9_TIE"
                if valid else "R3_M3_MISMATCH_OR_INADMISSIBLE"
            ),
        },
        "limitations":[
            "New controlled native VAP carrier, not an unseen family",
            "Two separate API resource LIST snapshots are not atomic or continuous watches",
            "Unknown admission webhooks, mutating policies or actor scopes not closed",
            "Classical open-world/possible-world and full-B9 techniques can emulate",
            "No P3 independent maintainer verified adaptation-cost advantage",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pred",required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--native",required=True)
    p.add_argument("--sources",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    pred=json.loads(Path(a.pred).read_text())
    manifest=json.loads(Path(a.manifest).read_text())
    native=json.loads(Path(a.native).read_text())
    docs={name:json.loads((Path(a.sources)/name).read_bytes()) for name in NAMES}
    result=score(pred,manifest,native,docs)
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result["summary"],sort_keys=True))


if __name__=="__main__":
    main()
