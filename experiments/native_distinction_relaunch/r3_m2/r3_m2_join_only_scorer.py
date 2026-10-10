#!/usr/bin/env python3
"""R3-M2 retrospective JOIN ONLY: pinned SOURCE-ONLY masks versus OLD native labels.

No Kubernetes calls, no new experiments or G5 cases; never import masked
source-model code or compute results from the archived native labels.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

MASKS=("FULL_CLOSED","TEAM_ONLY_CLOSED","MODE_ONLY_CLOSED",
       "NO_SELECTORS_CLOSED","OPEN_INVENTORY_KNOWN_BINDINGS",
       "POLICY_SOURCE_UNAVAILABLE","POLICY_SOURCE_TAMPERED",
       "BINDING_FRESHNESS_UNPROVEN")
PHASES=("initial","after_first","after_second")
RECOGNIZED={
    "PROVEN_ACCEPT","PROVEN_REJECT",
    "SOURCE_UNAVAILABLE_REFUSE","MODEL_UNSUPPORTED_REFUSE"
}
FROZEN_COUNTS={"PROVEN_ACCEPT":26,"PROVEN_REJECT":14,
               "SOURCE_UNAVAILABLE_REFUSE":24,
               "MODEL_UNSUPPORTED_REFUSE":32}
PER_MASK_CERTS={"FULL_CLOSED":12,"TEAM_ONLY_CLOSED":9,
                "MODE_ONLY_CLOSED":9,"NO_SELECTORS_CLOSED":6,
                "OPEN_INVENTORY_KNOWN_BINDINGS":4,
                "POLICY_SOURCE_UNAVAILABLE":0,
                "POLICY_SOURCE_TAMPERED":0,
                "BINDING_FRESHNESS_UNPROVEN":0}


def require(ok,msg):
    if not ok:
        raise ValueError(msg)


def old_native_index(tm,mt):
    """Every original native record and original 12+12+4 denominator retained."""
    idx={}
    contexts=set()
    total_controls=0
    updates=0
    for order,doc in (("TM",tm),("MT",mt)):
        require(doc.get("schema")=="eeq-r3-m1-native-two-binding-one-order-v1"
                and doc.get("order")==order and doc.get("error") is None and
                doc.get("prediction_json_read") is False and
                doc.get("observed_primary_rows")==6 and
                doc.get("observed_control_rows")==6 and
                doc.get("observed_action_count")==2,
                "ARCHIVED_NATIVE_R3_M1_DENOMINATOR_OR_SCOPE_FAILED:"+order)
        require(doc.get("context") not in contexts and doc.get("context"),
                "OLD_NATIVE_CLUSTER_CONTEXT_NOT_INDEPENDENT")
        contexts.add(doc["context"])
        require(len(doc["observations"])==6 and len(doc["controls"])==6
                and len(doc["native_actions"])==2,
                "ARCHIVED_NATIVE_ROWS_NOT_COMPLETE")
        controls={(r["control"],r["probe"]):r["native"] for r in doc["controls"]}
        require(len(controls)==6,"ARCHIVED_CONTROL_DUPLICATION")
        want={("UNBOUND","flux"):"ACCEPT",("UNBOUND","default"):"ACCEPT",
              ("ONLY_TEAM","flux"):"REJECT",("ONLY_TEAM","default"):"ACCEPT",
              ("ONLY_MODE","flux"):"REJECT",("ONLY_MODE","default"):"ACCEPT"}
        require(controls==want,"ARCHIVED_NATIVE_CONTROL_MISMATCH")
        total_controls+=6
        for row in doc["observations"]:
            phase=row["phase"];probe=row["probe"]
            key=order+"|"+phase+"|"+probe
            require(phase in PHASES and probe in ("flux","default") and
                    key not in idx and row["native"] in ("ACCEPT","REJECT") and
                    row["attribution"] in ("REGISTERED_VAP_DENIAL","ADMITTED"),
                    "ARCHIVED_NATIVE_LABEL_AMBIGUOUS_OR_DUPLICATE:"+key)
            require(row["phase_index"]==PHASES.index(phase),
                    "ARCHIVED_NATIVE_PHASE_INDEX_CHANGED")
            idx[key]=row["native"]
        for a in doc["native_actions"]:
            require(a["native_registered_action_verified"] is True and
                    a["before"]["uid"]==a["after"]["uid"] and
                    a["before"]["resource_version"]!=a["after"]["resource_version"],
                    "ARCHIVED_NAMESPACE_ACTION_NOT_VERIFIED")
            updates+=1
    require(len(idx)==12 and total_controls==12 and updates==4,
            "ARCHIVED_NATIVE_FULL_DENOMINATOR_NOT_COMPLETE")
    return idx


def join(masked,summary,tm,mt):
    native=old_native_index(tm,mt)
    require(summary.get("schema")==
        "eeq-r3-m2-f0-prospective-source-only-masked-development-v1" and
        summary.get("source_only_model_did_not_load_native_labels") is True and
        summary.get("original_native_scored_cases")==12 and
        summary.get("virtual_partial_source_packets")==96 and
        summary.get("safe_decisions")==40 and summary.get("refuses")==56 and
        summary.get("original_g5_increment")==0 and
        summary.get("full_c1_authority_independently_proven") is False,
        "SOURCE_ONLY_SUMMARY_NOT_FROZEN")
    require(isinstance(masked,list) and len(masked)==96,
            "VIRTUAL_MASKED_DENOMINATOR_NOT_96")
    cells={}
    statuses=Counter()
    certified=Counter()
    false_accept=0
    false_reject=0
    native_mismatch=[]
    for row in masked:
        require(isinstance(row,dict),"BAD_MASK_PACKET")
        key=row.get("key")
        mask=row.get("mask_id")
        case=row.get("case_id")
        require(mask in MASKS and case in native and
                key==mask+"|"+case and key not in cells,
                "DUPLICATE_OR_INVALID_MASKED_CASE")
        cells[key]=row
        disp=row.get("disposition")
        require(disp in RECOGNIZED and
                row.get("strong_b9_disposition")==disp and
                row.get("scoped_sound_against_possible_worlds") is True,
                "UNVERIFIED_OR_B9_UNFAIR_MASKED_ROW")
        statuses[disp]+=1
        expected_worlds=(
            ["ACCEPT"] if disp=="PROVEN_ACCEPT"
            else ["REJECT"] if disp=="PROVEN_REJECT"
            else ["ACCEPT","REJECT"])
        require(row.get("possible_world_effects")==expected_worlds,
                "FORGED_POSSIBLE_WORLD_SCOPE")
        if disp in ("PROVEN_ACCEPT","PROVEN_REJECT"):
            certified[mask]+=1
            predicted=("ACCEPT" if disp=="PROVEN_ACCEPT" else "REJECT")
            observed=native[case]
            if predicted!=observed:
                native_mismatch.append({"key":key,"predicted":predicted,
                                        "old_native":observed})
                if predicted=="ACCEPT":
                    false_accept+=1
                else:
                    false_reject+=1
    require(set(cells)=={m+"|"+k for m in MASKS for k in native},
            "VIRTUAL_CROSS_PRODUCT_INCOMPLETE")
    require(dict(statuses)==FROZEN_COUNTS and
            {m:certified[m] for m in MASKS}==PER_MASK_CERTS,
            "SOURCE_ONLY_FROZEN_COVERAGE_CHANGED")
    return {
        "schema":"eeq-r3-m2-f0-retrospective-native-join-result-v1",
        "evidence_class":"RETROSPECTIVE_REUSE_OF_ALREADY_SCORED_R3_M1_NATIVE",
        "original_native_distinct_cases":12,
        "old_native_original_controls":12,"old_native_actions":4,
        "new_native_calls":0,"new_original_g5_cases":0,
        "virtual_masked_packets_registered":96,
        "virtual_masked_packets_scored":96,
        "certified_native_comparisons":40,
        "certified_native_exact_matches":40-len(native_mismatch),
        "certified_native_mismatches":len(native_mismatch),
        "certified_false_accepts":false_accept,
        "certified_false_rejects":false_reject,
        "refused_packets":56,
        "refused_packets_not_relabelled_native_reject":True,
        "certified_coverage":40/96,
        "b9_equal_information_ties":96,
        "b9_independent_maintainer_trial":False,
        "unseen_native_claim":False,
        "world_model_c1_completeness_externally_proven":False,
        "mismatches":native_mismatch,
        "scientific_status":(
            "R3_M2_RETROSPECTIVE_NATIVE_COVERAGE_PROOF_DIAGNOSTIC_B9_TIE"
            if not native_mismatch else
            "R3_M2_PARTIAL_SOURCE_METHOD_MISMATCH_RETAINED"
        ),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-rows",required=True)
    p.add_argument("--source-summary",required=True)
    p.add_argument("--native-tm",required=True)
    p.add_argument("--native-mt",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    load=lambda path:json.loads(Path(path).read_text())
    out=join(load(a.source_rows),load(a.source_summary),
             load(a.native_tm),load(a.native_mt))
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({key:out[key] for key in (
        "original_native_distinct_cases","virtual_masked_packets_scored",
        "certified_native_comparisons","certified_native_exact_matches",
        "refused_packets","b9_equal_information_ties","scientific_status")},
        sort_keys=True))
    if out["certified_native_mismatches"]:
        raise SystemExit("R3_M2_NATIVE_MISMATCH_RETAINED")


if __name__=="__main__":
    main()
