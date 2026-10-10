#!/usr/bin/env python3
"""Emit deterministic R3-M2 F0 SOURCE-ONLY virtual evidence scores, not native."""
import argparse
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path
from r3_m2_partial_source import MASKS,candidate,registered_mask_packet_rows,registered_rows
from r3_m2_possible_world_oracle import possible_native_vap_effects,strongest_b9_with_equal_partial_inputs

EXPECTED={
  "PROVEN_ACCEPT":26,"PROVEN_REJECT":14,
  "SOURCE_UNAVAILABLE_REFUSE":24,"MODEL_UNSUPPORTED_REFUSE":32
}
EXPECTED_COVERAGE={
 "FULL_CLOSED":12,"TEAM_ONLY_CLOSED":9,"MODE_ONLY_CLOSED":9,
 "NO_SELECTORS_CLOSED":6,"OPEN_INVENTORY_KNOWN_BINDINGS":4,
 "POLICY_SOURCE_UNAVAILABLE":0,"POLICY_SOURCE_TAMPERED":0,
 "BINDING_FRESHNESS_UNPROVEN":0,
}


def build():
    packets=registered_mask_packet_rows()
    rows=[]
    summary_counts=Counter()
    per_mask=defaultdict(Counter)
    bad=[]
    oracle_disagreements=[]
    b9_disagreements=[]
    weak_unsound=0
    for packet in packets:
        result=candidate(packet)
        possible=possible_native_vap_effects(packet)
        fair_b9=strongest_b9_with_equal_partial_inputs(packet)
        disp=result["disposition"]
        summary_counts[disp]+=1
        per_mask[packet["mask_id"]][disp]+=1
        sound=(("PROVEN_ACCEPT"==disp and possible==frozenset(("ACCEPT",))) or
               ("PROVEN_REJECT"==disp and possible==frozenset(("REJECT",))) or
               (disp.endswith("REFUSE") and possible==frozenset(("ACCEPT","REJECT"))))
        if not sound:
            oracle_disagreements.append(packet["mask_id"]+"|"+packet["case_id"])
        if disp!=fair_b9:
            b9_disagreements.append(packet["mask_id"]+"|"+packet["case_id"])
        if disp in ("PROVEN_REJECT","PROVEN_ACCEPT") and not result["witness"]:
            bad.append(packet["mask_id"]+"|"+packet["case_id"])
        # Deliberately weak ablation: missing/not-yet-discovered support ignored.
        # Only measure logical unsoundness, not empirical native errors.
        if packet["policy"]["state"]=="AVAILABLE" and packet[
                "binding_provenance"]["individual_bindings_fresh_in_scoped_native_archive"]:
            active=any(slot["selector_status"]=="AVAILABLE" and
                       all(packet["namespace_labels"].get(k)==v
                           for k,v in slot["selector"].items())
                       for slot in packet["binding_slots"])
            weak="REJECT" if packet["pod"]["serviceAccountName"]=="flux" and active else "ACCEPT"
            if weak not in possible or len(possible)!=1:
                weak_unsound+=1
        rows.append({
            "key":packet["mask_id"]+"|"+packet["case_id"],
            "mask_id":packet["mask_id"],"case_id":packet["case_id"],
            "disposition":disp,"reason":result["reason"],
            "witness":result["witness"],"possible_world_effects":sorted(possible),
            "strong_b9_disposition":fair_b9,
            "scoped_sound_against_possible_worlds":sound,
        })
    if len(rows)!=96 or len({r["key"] for r in rows})!=96:
        raise ValueError("MASKED_PRIMARY_DENOMINATOR_NOT_96")
    if dict(summary_counts)!=EXPECTED:
        raise ValueError("MASKED_OUTCOME_HISTOGRAM_CHANGED:"+repr(summary_counts))
    coverage={m:sum(per_mask[m][x] for x in ("PROVEN_ACCEPT","PROVEN_REJECT")) for m in MASKS}
    if coverage!=EXPECTED_COVERAGE:
        raise ValueError("MASKED_COVERAGE_HISTOGRAM_CHANGED:"+repr(coverage))
    if oracle_disagreements or b9_disagreements or bad:
        raise ValueError("INVALID_PARTIAL_EVIDENCE_PROOF_OR_STRONG_B9_TIE")
    if weak_unsound!=20:
        raise ValueError("WEAK_ABLATION_UNSOUND_COUNT_CHANGED:"+str(weak_unsound))
    return {
        "schema":"eeq-r3-m2-f0-prospective-source-only-masked-development-v1",
        "evidence_class":"POST_NATIVE_REUSE_OF_ALREADY_SCORED_CONTROLLED_DEVELOPMENT",
        "original_native_scored_cases":12,
        "virtual_partial_source_packets":96,
        "new_native_calls":0,"original_g5_increment":0,
        "source_only_model_did_not_load_native_labels":True,
        "outcome_histogram":dict(sorted(summary_counts.items())),
        "safe_decisions":40,"refuses":56,
        "safe_coverage_ratio":40/96,
        "unsound_certifications_against_bounded_possible_worlds":0,
        "strong_equal_information_b9_ties":96,
        "weak_missing_as_false_ablation_unsound_proof_packets":weak_unsound,
        "per_mask_coverage":coverage,
        "full_c1_authority_independently_proven":False,
        "global_kubernetes_admission_proven":False,
        "p3_human_advantage_established":False,
        "scientific_status":"R3_M2_SOURCE_ONLY_PARTIAL_EVIDENCE_DIAGNOSTIC_B9_TIE",
    },rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    summary,rows=build()
    root=Path(args.out);root.mkdir(parents=True,exist_ok=True)
    for name,obj in (("F0_SUMMARY.json",summary),("F0_MASKED_96_SOURCE_ONLY.json",rows)):
        (root/name).write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    with (root/"SOURCE_ONLY_SHA256.txt").open("w") as dest:
        for name in ("F0_SUMMARY.json","F0_MASKED_96_SOURCE_ONLY.json"):
            h=hashlib.sha256((root/name).read_bytes()).hexdigest()
            dest.write(h+"  "+name+"\n")
    print(json.dumps(summary,sort_keys=True))


if __name__=="__main__":
    main()
