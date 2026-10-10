#!/usr/bin/env python3
"""P2 source-backed primitive proof adversary audit — ZERO new native work.

Replays 16 old E2 source-only programs only AFTER separate TUF and K8s
original-source primitive witness generators emit their new leaf entailment
trees. Tests the TWO old P1 attacks without touching archived E2 source IR.
"""
import argparse,hashlib,json,sys
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"p1"))
from e2_p1_forged_qualified_leaf_audit import mutate_one,ATTACKS
from p2_independent_original_source_entailment_checker import verify
from r4_e2_generic_rule_checker import check_program

WANT_BY_FAMILY={"TUF_ROOT_UPDATE":8,"K8S_SCOPED_VAP_DENY":8}

def index(rows,what):
 if not isinstance(rows,list) or len(rows)!=8:
  raise ValueError("P2_DENOMINATOR_MISSING:"+what)
 keys=[r.get("case_id") for r in rows]
 if len(set(keys))!=8 or any(not isinstance(k,str) for k in keys):
  raise ValueError("P2_DUPLICATE_OR_BAD_CASE_ID:"+what)
 return {r["case_id"]:r for r in rows}

def demand(cond,why):
 if not cond:raise ValueError(why)

def evaluate(tuf_prog,k8s_prog,tuf_witness,k8s_witness,tuf_b9,k8s_b9):
 p={**index(tuf_prog,"TUF_PROGRAM"),**index(k8s_prog,"K8S_PROGRAM")}
 w={**index(tuf_witness,"TUF_WITNESS"),**index(k8s_witness,"K8S_WITNESS")}
 b={**index(tuf_b9,"TUF_B9"),**index(k8s_b9,"K8S_B9")}
 demand(len(p)==len(w)==len(b)==16 and set(p)==set(w)==set(b),
        "P2_16_ORIGINAL_DEVELOPMENT_PROGRAMS_NOT_COMPLETE")
 outcomes=Counter()
 rows=[]
 for caseid in sorted(p):
  original=p[caseid]
  witness=w[caseid]
  strong=b[caseid]["direct_B9_source_only_effect"]
  domain=original["domain"]
  demand(domain in WANT_BY_FAMILY,"P2_UNSUPPORTED_SOURCE_FAMILY")
  original_struct=check_program(original)
  demand(original_struct["status"]=="QUALIFIED_BOUNDED_RULE_EVALUATED" and
         original_struct["scoped_effect_bit"]==strong,
         "P2_ORIGINAL_E2_SOURCE_ONLY_B9_DISAGREEMENT:"+caseid)
  verdict=verify(original,witness)
  demand(verdict["status"]=="SCOPED_SOURCE_PRIMITIVES_INDEPENDENTLY_RECHECKED" and
         verdict["scoped_effect_bit"]==strong,
         "P2_ORIGINAL_SOURCE_PRIMITIVE_RECHECK_FAIL:"+caseid+"="+repr(verdict))
  outcomes[domain]+=1
  rows.append({
    "case_id":caseid,"domain":domain,
    "original_E2_source_only_effect":original_struct["scoped_effect_bit"],
    "independently_checked_original_source_effect":verdict["scoped_effect_bit"],
    "fully_informed_B9_source_only_effect":strong,
    "native_oracle_outcomes_read":False,
    "original_E2_program_modified":False,
    "externally_complete_native_roster_certified":False,
    "new_original_g5_increment":0})
 demand(dict(outcomes)==WANT_BY_FAMILY,"P2_SOURCE_SEMANTIC_DOMAIN_DENOMINATOR")
 attacks=[]
 for caseid,registered in ATTACKS.items():
  orig=p[caseid]
  native_leaf_ref=w[caseid]
  forged,changed=mutate_one(orig,registered["role"])
  structural=check_program(forged)
  rebuilt=verify(forged,native_leaf_ref)
  demand(structural["status"]=="QUALIFIED_BOUNDED_RULE_EVALUATED" and
         structural["scoped_effect_bit"]==registered["after"] and
         structural["scoped_effect_bit"]!=b[caseid]["direct_B9_source_only_effect"],
         "P2_EXPECTED_ORIGINAL_STRUCTURAL_BYPASS_NOT_REPRODUCED:"+caseid)
  demand(rebuilt["status"]=="REFUSE_SOURCE_ENTAILMENT" and
         rebuilt["reason"]=="P2_PRIMITIVE_LEAF_OR_RULE_NOT_IMPLIED_BY_NATIVE_SOURCE_BYTES",
         "P2_INDEPENDENT_PRIMITIVE_VETO_FAILED:"+caseid)
  demand(orig["verified_source_sha256"]==forged["verified_source_sha256"],
         "P2_ORIGINAL_SOURCE_HASH_DIFFERENT")
  attacks.append({
    "case_id":caseid,"forged_atom":changed["atom_id"],
    "source_hashes_preserved":True,
    "original_generic_structural_checker_accepts_forged_claim":True,
    "new_original_source_native_primitive_verifier_rejects":True,
    "reason":rebuilt["reason"],"scoped_not_global_native_effect":True
  })
 demand(len(attacks)==2,"P2_FORGED_LEAF_FIXED_DENOMINATOR_NOT_TWO")
 return {
    "schema":"eeq-r4-e2-p2-independent-native-primitive-evidence-result-v1",
    "evidence_class":"RETROSPECTIVE_SOURCE_ONLY_OLD_NATIVE_DEVELOPMENT_WITH_NEW_PRIMITIVE_CHECKER",
    "original_E2_source_only_run_id":38032779592,
    "original_P1_attack_run_id":38033101279,
    "registered_old_source_programs":16,"independently_rechecked_old_source_programs":16,
    "tuf_checked_source_programs":8,"k8s_checked_source_programs":8,
    "original_e2_direct_B9_source_only_ties":16,
    "registered_P1_forged_leaves":2,
    "original_structural_checker_accepted_P1_forged_leaves":2,
    "new_trusted_primitive_entailment_checker_rejected_P1_forged_leaves":2,
    "new_native_calls":0,
    "new_v1_g5_cases":0,
    "new_g8_cases":0,
    "source_inventory_complete_external_native_authority_proven":False,
    "source_parsers_handwritten_per_family":True,
    "global_k8s_admission_accept_certified":False,
    "fully_informed_B9_can_copy_source_witness_verifier":True,
    "independent_B9_value_proven":False,
    "method_originality_established":False,
    "scientific_status":"R4_E2_P2_BOUNDED_INDEPENDENT_PRIMITIVE_CHECKER_DEV_B9_TIE",
    "attacks":attacks,
    "old_program_rows":rows,
 }

def main():
 ap=argparse.ArgumentParser()
 for key in ("tuf","k8s","tuf-witness","k8s-witness","tuf-b9","k8s-b9","out"):
  ap.add_argument("--"+key,required=True)
 a=ap.parse_args()
 load=lambda fname:json.loads(Path(fname).read_text())
 result=evaluate(load(a.tuf),load(a.k8s),load(a.tuf_witness),
                 load(a.k8s_witness),load(a.tuf_b9),load(a.k8s_b9))
 Path(a.out).write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
 print(json.dumps({k:result[k] for k in (
    "independently_rechecked_old_source_programs",
    "new_trusted_primitive_entailment_checker_rejected_P1_forged_leaves",
    "fully_informed_B9_can_copy_source_witness_verifier","independent_B9_value_proven",
    "scientific_status")},sort_keys=True))
if __name__=="__main__":main()
