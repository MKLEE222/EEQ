#!/usr/bin/env python3
"""R4-E1 F0 emit fully accountable synthetic plan and impossibility witnesses.

No native calls, no developer P3 time, no original G5/G8 scoring.
"""
import argparse,hashlib,json
from pathlib import Path
from collections import Counter

from r4_e1_frontier import frontier
from r4_e1_registry import registry,FROZEN_STATUS_COUNTS,EXPECTATIONS,TOTAL_COST_SUM
from r4_e1_independent_reference import (
 check_frontier_cert,b9_exact_optimum_reference,enumerate_truth
)

def build():
    scenarios=registry()
    scored=[]
    count=Counter()
    for s in scenarios:
        result=frontier(s)
        independent=check_frontier_cert(s,result)
        baseline=b9_exact_optimum_reference(s)
        expected_status,expected_worst=EXPECTATIONS[s["case_id"]]
        if result["status"]!=expected_status or result["read_cost_worst_case"]!=expected_worst:
            raise ValueError("REGISTERED_DISPOSITION_OR_WORST_COST_CHANGED:"+s["case_id"])
        if s["case_id"] in TOTAL_COST_SUM and result["read_cost_over_all_finite_worlds"]!=TOTAL_COST_SUM[s["case_id"]]:
            raise ValueError("FROZEN_TOTAL_COST_CHANGED:"+s["case_id"])
        if independent["sound"] is not True or independent["same_optimal_B9"] is not True:
            raise ValueError("INDEPENDENT_REFERENCE_OR_STRONG_B9_NOT_VERIFIED:"+s["case_id"])
        count[result["status"]]+=1
        scored.append({
          "case_id":s["case_id"],"family":s["family"],
          "program_id":s["program_id"],"source_knowledge":s["observed"],
          "actor_lawful_reads":s["lawful_reads"],
          "finite_registered_completion_count":result["possible_world_count"],
          "frontier":result,
          "independent_oracle":independent,
          "fully_informed_B9_equal_information_optimum":baseline,
          "native_source_read":False,
        })
    if len(scored)!=17 or len({x["case_id"] for x in scored})!=17:
        raise ValueError("FROZEN_PRIMARY_DENOMINATOR_NOT_17")
    if dict(count)!=FROZEN_STATUS_COUNTS:
        raise ValueError("FROZEN_PRIMARY_OUTCOME_HISTOGRAM_CHANGED")
    manifest={
      "schema":"eeq-r4-e1-source-free-frontier-study-summary-v1",
      "evidence_class":"PREREGISTERED_PRE_IMPLEMENTATION_SOURCE_FREE_SYNTHETIC_F0",
      "precode_freeze_git_commit":"7f6b51e6cca6d3b035739a0ab11b33c66aad538e",
      "registered_primary_cases":17,"evaluated_primary_cases":len(scored),
      "outcomes":dict(sorted(count.items())),
      "certainty_case_count":7,
      "uncertain_but_guaranteed_access_resolvable_count":5,
      "actor_access_impossibility_witness_case_count":5,
      "independent_oracle_cases_verified":17,
      "equal_information_B9_eligible_exact_cost_parity":17,
      "full_B9_independent_maintainer_comparison_executed":False,
      "naive_query_all_weak_baseline_is_not_B9":True,
      "two_native_family_qualification_adapters_still_handwritten":True,
      "external_c1_complete_source_inventory_certified":False,
      "global_kubernetes_admission_claims":0,
      "new_native_calls":0,
      "new_original_v1_g5_cases":0,
      "new_g8_cases":0,
      "new_R5_unseen_family_opened":False,
      "method_originality_established":False,
      "independent_b9_value_established":False,
      "scientific_status":"R4_E1_SYNTHETIC_LAWFUL_QUERY_FRONTIER_FEASIBLE_B9_TIE"
    }
    return manifest,scored

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    root=Path(args.out);root.mkdir(parents=True,exist_ok=True)
    manifest,rows=build()
    for name,obj in (
       ("R4_E1_F0_SUMMARY.json",manifest),
       ("R4_E1_F0_ALL_17_ORACLE_VERIFIED_ROWS.json",rows)):
        (root/name).write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n",encoding="utf8")
    with (root/"R4_E1_F0_SHA256.txt").open("w") as f:
        for name in ("R4_E1_F0_SUMMARY.json","R4_E1_F0_ALL_17_ORACLE_VERIFIED_ROWS.json"):
            digest=hashlib.sha256((root/name).read_bytes()).hexdigest()
            f.write(digest+"  "+name+"\n")
    print(json.dumps(manifest,sort_keys=True))

if __name__=="__main__":main()
