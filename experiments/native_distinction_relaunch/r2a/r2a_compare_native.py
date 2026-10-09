#!/usr/bin/env python3
"""Join frozen source-only R2A predictions and independent native episodes.

Never executes a cluster or predictor; preserves full 8-case denominator,
source-availability failures, policy propagation and unrelated rejections.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

WORLDS=("WORLD_GATE","WORLD_STANDBY")
PHASES=("CURRENT","AFTER_BINDING_MUTATION")
SAS=("flux","default")


def read(p):
    return json.loads(Path(p).read_text(encoding="utf8"))


def check(condition,why):
    if not condition:
        raise ValueError(why)


def compare(pred,episodes):
    check(pred["schema"]=="eeq-r2a-source-only-v1",
          "WRONG_PREDICTION_SCHEMA")
    check(pred["case_count"]==8 and pred["registered_horizon"]==1,
          "FROZEN_DENOMINATOR_CHANGED")
    check(pred["registered_worlds"]==list(WORLDS),
          "REGISTERED_WORLD_CHANGED")
    p={}
    for row in pred["rows"]:
        key=(row["world"],row["phase"],row["service_account"])
        check(key not in p,"DUPLICATE_PREDICTION_ROW")
        p[key]=row
    all_cases={(w,ph,sa) for w in WORLDS for ph in PHASES for sa in SAS}
    check(set(p)==all_cases,"MISSING_OR_NEW_PREDICTION_CASES")
    outcomes={}
    infrastructure=[]
    summaries={}
    for world in WORLDS:
        episode=episodes[world]
        check(episode["schema"]=="eeq-r2a-k8s-native-episode-v1",
              "WRONG_NATIVE_EPISODE_SCHEMA")
        check(episode["world"]==world,"WORLD_ID_DOES_NOT_MATCH_FILE")
        check(episode["source_only_prediction_file_never_read"] is True,
              "ORACLE_NOT_INDEPENDENT")
        if episode.get("status")!="NATIVE_EPISODE_COMPLETED":
            infrastructure.append({"world":world,
                "failure":"NATIVE_EPISODE_NOT_COMPLETED",
                "details":episode.get("error")})
        for name,expected_hash in pred["source_sha256"].items():
            check(episode["source_sha256"].get(name)==expected_hash,
                  "NATIVE_SOURCE_SHA_MISMATCH_"+name)
        before=episode.get("before_native_source",{})
        after=episode.get("after_native_source",{})
        oldsel=before.get("binding_selector")
        newsel=after.get("binding_selector")
        proper=(oldsel=={"eeq.r2a/armed":"never"} and
                newsel=={"eeq.r2a/armed":"gate"} and
                before.get("binding_resourceVersion") and
                after.get("binding_resourceVersion") and
                before["binding_resourceVersion"] !=
                    after["binding_resourceVersion"] and
                episode.get("activation_proven") is True and
                len(episode.get("activation_probe_attempts",[]))>=1)
        if not proper:
            infrastructure.append({"world":world,
                "failure":"ACTUAL_POLICY_MUTATION_SOURCE_OR_ACTIVATION_NOT_PROVED"})
        obs={}
        for row in episode.get("observations",[]):
            key=(row["world"],row["phase"],row["service_account"])
            check(key not in obs,"DUPLICATE_NATIVE_ADMISSION")
            obs[key]=row
        if set(obs)!={(world,ph,sa) for ph in PHASES for sa in SAS}:
            infrastructure.append({"world":world,
                                   "failure":"NATIVE_ADMISSION_DENOMINATOR_INCOMPLETE"})
        outcomes.update(obs)
        summaries[world]={"episode_status":episode.get("status"),
                          "policy_transition_supported":bool(proper),
                          "num_admission_rows":len(obs),
                          "num_activation_probes":len(episode.get("activation_probe_attempts",[]))}
    rows=[]
    for key in [(w,ph,sa) for w in WORLDS for ph in PHASES for sa in SAS]:
        p_row=p[key]
        native=outcomes.get(key)
        actual=native.get("native_outcome") if native else "NOT_OBSERVED"
        attribution=(native.get("native_attribution") if native else None)
        expected=p_row["expected_native"]
        matched=(actual==expected and (
            expected=="ACCEPT" or attribution=="REGISTERED_VAP"))
        rows.append({
            "world":key[0],"phase":key[1],"service_account":key[2],
            "source_only_predicted":expected,"native_observed":actual,
            "native_attribution":attribution,
            "case_status":"MATCH" if matched else "MISMATCH_OR_UNAVAILABLE",
            "native_stdout":native.get("native_stdout") if native else None,
            "native_stderr":native.get("native_stderr") if native else None,
        })
    def vec(w,phase):
        return tuple(outcomes.get((w,phase,sa),{}).get("native_outcome")
                     for sa in SAS)
    curr_equal=vec("WORLD_GATE","CURRENT")==vec("WORLD_STANDBY","CURRENT")
    future_diff=vec("WORLD_GATE","AFTER_BINDING_MUTATION") != \
                vec("WORLD_STANDBY","AFTER_BINDING_MUTATION")
    matched=sum(x["case_status"]=="MATCH" for x in rows)
    valid=(matched==8 and not infrastructure and curr_equal and future_diff)
    return {
      "schema":"eeq-r2a-k8s-native-vs-frozen-source-v1",
      "evidence_class":"CONTROLLED_NATIVE_TWO_ISOLATED_CLUSTER_EPISODES",
      "status":"CONTROLLED_NATIVE_A_CONFIRMED_B9_TIE" if valid
               else "CONTROLLED_NATIVE_A_NOT_ESTABLISHED",
      "summary":{
        "frozen_admission_denominator":8,
        "native_admission_matches":matched,
        "native_admission_mismatches_or_unavailable":8-matched,
        "episodes_completed":sum(s["episode_status"]=="NATIVE_EPISODE_COMPLETED"
                                  for s in summaries.values()),
        "verified_policy_transitions":sum(s["policy_transition_supported"]
                                           for s in summaries.values()),
        "current_decision_vectors_identical":curr_equal,
        "future_decision_vectors_diverge_after_same_native_patch":future_diff,
        "source_qualification_distinction_verified":
            not infrastructure and valid,
        "strong_b9_tie_predeclared":True,
        "independent_novelty_advantage":False,
        "full_R2_gate_pass":False,
      },
      "world_summaries":summaries,
      "infrastructure_failures":infrastructure,
      "case_results":rows,
      "witness":{
        "registered_action":"PATCH_BINDING_SELECTOR_TO_GATE",
        "pre_action_flux_gate":vec("WORLD_GATE","CURRENT")[0],
        "pre_action_flux_standby":vec("WORLD_STANDBY","CURRENT")[0],
        "post_action_flux_gate":vec("WORLD_GATE","AFTER_BINDING_MUTATION")[0],
        "post_action_flux_standby":vec("WORLD_STANDBY","AFTER_BINDING_MUTATION")[0],
        "qualification_source_difference":
            "namespace label eeq.r2a/armed gate versus standby",
        "native_binding_resource_mutation_evidence_required":True,
      },
      "G4_v1_unchanged":True,
      "G5_increment":0
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pred",required=True)
    p.add_argument("--gate",required=True)
    p.add_argument("--standby",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    result=compare(read(a.pred),{
      "WORLD_GATE":read(a.gate),
      "WORLD_STANDBY":read(a.standby),
    })
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                           encoding="utf8")
    print(json.dumps(result["summary"],sort_keys=True))


if __name__=="__main__":
    main()
