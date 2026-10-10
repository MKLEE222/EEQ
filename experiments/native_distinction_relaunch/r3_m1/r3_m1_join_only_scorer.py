#!/usr/bin/env python3
"""R3-M1 JOIN-ONLY scorer. Runs only after both native raw JSON files are saved.

It never executes kubectl, simulates native outcomes, drops failures or changes
frozen source-only predictions. Synthetic unit tests are not native evidence.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ORDERS={"TM":("team","mode"),"MT":("mode","team")}
PHASES=("initial","after_first","after_second")


def require(ok,reason):
    if not ok: raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def score(manifest,pred,tm,mt,manifest_raw=None):
    require(manifest.get("schema")=="eeq-r3-m1-source-manifest-v1" and
            len(manifest.get("sources",[]))==8,
            "SCORER_INVALID_SOURCE_MANIFEST")
    require(pred.get("schema")=="eeq-r3-m1-source-only-predictions-v1" and
            pred.get("native_labels_read") is False and
            pred.get("native_verifier_called") is False and
            pred.get("native_primary_denominator")==12 and
            pred.get("native_control_denominator")==12 and
            pred.get("native_action_updates")==4,
            "SCORER_INVALID_PREREGISTERED_PREDICTIONS")
    expected_rows={}
    for row in pred["registered_cases"]:
        case=(row["order"],row["phase"],row["probe"])
        require(case not in expected_rows,"DUPLICATE_SOURCE_PREDICTION")
        require(case[0] in ORDERS and case[1] in PHASES and
                case[2] in ("flux","default") and
                row["expected_native"] in ("ACCEPT","REJECT"),
                "SOURCE_PREDICTION_OUT_OF_SCOPE")
        expected_rows[case]=row
    expected_ids={(o,ph,p) for o in ORDERS for ph in PHASES
                  for p in ("flux","default")}
    require(set(expected_rows)==expected_ids,"SOURCE_PRIMARY_DENOMINATOR_NOT_12")
    raw_map={"TM":tm,"MT":mt}
    contexts=[]
    all_results=[]
    all_controls=[]
    all_actions=[]
    for order,raw in raw_map.items():
        require(raw.get("schema")=="eeq-r3-m1-native-two-binding-one-order-v1"
            and raw.get("order")==order and raw.get("prediction_json_read") is False
            and raw.get("error") is None and
            raw.get("registered_primary_rows")==6 and
            raw.get("observed_primary_rows")==6 and
            raw.get("registered_control_rows")==6 and
            raw.get("observed_control_rows")==6 and
            raw.get("registered_action_count")==2 and
            raw.get("observed_action_count")==2,
            "NATIVE_RUN_FAILURE_OR_COUNT:"+order)
        if manifest_raw is not None:
            require(raw["source_manifest_sha256"]==digest(manifest_raw),
                    "NATIVE_SOURCE_MANIFEST_HASH_MISMATCH:"+order)
        contexts.append(raw.get("context"))
        binding_map=dict(raw.get("observed_registered_bindings",[]))
        require(set(binding_map)=={"eeq-r3-binding-team","eeq-r3-binding-mode"},
                "NATIVE_BOTH_BINDINGS_NOT_INSTALLED:"+order)
        require(binding_map["eeq-r3-binding-team"]=={"r3.team":"tenant"} and
                binding_map["eeq-r3-binding-mode"]=={"r3.mode":"strict"},
                "NATIVE_BINDING_SELECTOR_OUT_OF_SCOPE:"+order)
        controls=raw["controls"]
        require(len(controls)==6,"NATIVE_CONTROL_DENOMINATOR:"+order)
        observed_keys=set()
        for c in controls:
            key=(c["control"],c["probe"])
            require(key not in observed_keys,"DUPLICATE_NATIVE_CONTROL:"+order)
            observed_keys.add(key)
            grp={"UNBOUND":"unbound","ONLY_TEAM":"only_team",
                 "ONLY_MODE":"only_mode"}.get(c["control"])
            require(grp is not None and c["probe"] in ("flux","default"),
                    "UNREGISTERED_NATIVE_CONTROL:"+order)
            want=pred["per_cluster_frozen_controls"][grp][c["probe"]]
            require(c.get("native") in ("ACCEPT","REJECT") and
                    c.get("native")==want,
                    "NATIVE_CONTROL_MISMATCH_OR_AMBIGUOUS:"+order)
            all_controls.append((order,key))
        require(len(observed_keys)==6,"MISSING_NATIVE_CONTROL:"+order)

        seen=set()
        for row in raw["observations"]:
            case=(order,row.get("phase"),row.get("probe"))
            require(case in expected_rows and case not in seen,
                    "MISSING_OR_DUPLICATE_NATIVE_MAIN:"+order)
            seen.add(case)
            exp=expected_rows[case]
            observed=row.get("native")
            require(observed in ("ACCEPT","REJECT"),
                    "NATIVE_ORACLE_AMBIGUOUS_NO_CREDIT:"+str(case))
            labels=row.get("namespace",{}).get("labels",{})
            require(labels.get("r3.team")==exp["source_only_namespace_labels"]["r3.team"]
                    and labels.get("r3.mode")==exp["source_only_namespace_labels"]["r3.mode"],
                    "NATIVE_NAMESPACE_DIFFERS_FROM_REGISTERED_ACTION:"+str(case))
            actual_bindings=dict(row.get("native_binding_inventory",[]))
            require(actual_bindings==binding_map,
                    "NATIVE_REGISTERED_BINDING_INVENTORY_CHANGED:"+str(case))
            qualified=sorted("binding-"+key+".json" for key in ("team","mode")
                if all(labels.get(k)==v for k,v in
                       binding_map["eeq-r3-binding-"+key].items()))
            require(qualified==sorted(exp["qualified_binding_source_ids"]),
                    "NATIVE_SOURCE_SUPPORT_QUALIFICATION_MISMATCH:"+str(case))
            all_results.append({
                "order":order,"phase":row["phase"],"probe":row["probe"],
                "expected_native":exp["expected_native"],
                "observed_native":observed,
                "match":observed==exp["expected_native"],
                "native_qualified_binding_sources":qualified,
            })
        require(seen=={i for i in expected_ids if i[0]==order},
                "NATIVE_MAIN_DENOMINATOR_NOT_SIX:"+order)
        actions=raw["native_actions"]
        require([a.get("action") for a in actions]==list(ORDERS[order]),
                "NATIVE_ACTION_ORDER_NOT_FROZEN:"+order)
        for a in actions:
            before=a.get("before",{})
            after=a.get("after",{})
            key="r3."+a["action"]
            expected_to={"r3.team":"external","r3.mode":"relaxed"}[key]
            expected_from={"r3.team":"tenant","r3.mode":"strict"}[key]
            require(a.get("native_registered_action_verified") is True and
                    a.get("command",{}).get("exit_code")==0 and
                    before.get("uid")==after.get("uid") and
                    before.get("resource_version")!=after.get("resource_version") and
                    before.get("labels",{}).get(key)==expected_from and
                    after.get("labels",{}).get(key)==expected_to,
                    "NATIVE_ACTION_NOT_VERIFIED:"+order+":"+key)
            all_actions.append((order,key))
    require(len(set(contexts))==2 and all(contexts),
            "NATIVE_TWO_ORDERS_NOT_IN_INDEPENDENT_CONTEXTS")
    require(len(all_results)==12 and len(all_controls)==12 and len(all_actions)==4,
            "NATIVE_GLOBAL_DENOMINATOR_REDUCED")
    correct=sum(r["match"] for r in all_results)
    statuses=Counter(r["observed_native"] for r in all_results)
    return {
        "schema":"eeq-r3-m1-controlled-multibinding-join-result-v1",
        "evidence_class":"CONTROLLED_NATIVE_DEVELOPMENT",
        "registered_primary":12,"observed_primary":len(all_results),
        "exact_source_to_native_matches":correct,
        "mismatches":12-correct,
        "native_label_histogram":dict(sorted(statuses.items())),
        "native_isolation_controls_passed":len(all_controls),
        "native_isolation_controls_registered":12,
        "native_namespace_actions_verified":len(all_actions),
        "native_namespace_actions_registered":4,
        "strong_b9_equal_information_reference_can_tie":True,
        "independent_human_b9_evaluation":False,
        "new_original_v1_g5_cases":0,
        "p3_independent_value_established":False,
        "new_general_multi_support_compiler_established":False,
        "per_case":all_results,
        "scientific_status":(
            "R3_M1_CONTROLLED_NATIVE_TWO_SUPPORT_PATHS_FEASIBLE_B9_TIE"
            if correct==12 else "R3_M1_NATIVE_MODEL_MISMATCH_RETAINED"
        ),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--predictions",required=True)
    p.add_argument("--native-tm",required=True)
    p.add_argument("--native-mt",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    raw=Path(a.manifest).read_bytes()
    out=score(json.loads(raw),json.loads(Path(a.predictions).read_text()),
              json.loads(Path(a.native_tm).read_text()),
              json.loads(Path(a.native_mt).read_text()),raw)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:out[k] for k in ("registered_primary",
         "exact_source_to_native_matches","mismatches",
         "native_isolation_controls_passed","native_namespace_actions_verified",
         "scientific_status")},sort_keys=True))
    if out["mismatches"]:
        raise SystemExit("R3_M1_NATIVE_MISMATCH_RETAINED")


if __name__=="__main__":
    main()
