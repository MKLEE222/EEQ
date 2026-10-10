#!/usr/bin/env python3
"""P1 post-E2 archival-only qualified-leaf forgery, not new native scoring.

One flipped Boolean semantic predicate suffices to fool E2's structural
checker while source hashes are unchanged. This is a trustworthy-base
audit, NOT a procedure for creating externally accepted admission rights.
"""
import argparse,copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from r4_e2_generic_rule_checker import check_program

ATTACKS={
 "TUF|s2a|root-3-b":{
    "family":"TUF_ROOT_UPDATE",
    "original":False,"after":True,
    "role":"OLD_ROOT","source_program":"TUF"
 },
 "K8S|A2_BINDING_ADDED|default":{
    "family":"K8S_SCOPED_VAP_DENY",
    "original":True,"after":False,
    "role":"K8S_THIRD_CEL","source_program":"K8S"
 }
}

def get_map(rows):
 if len(rows)!=8 or len({x["case_id"] for x in rows})!=8:
  raise ValueError("E2_ORIGINAL_SOURCE_DENOMINATOR_INCOMPLETE")
 return {x["case_id"]:x for x in rows}

def mutate_one(program,role):
 forged=copy.deepcopy(program)
 if role=="OLD_ROOT":
  old=forged["formula"]["children"][1]
  if old.get("op")!="THRESHOLD":
   raise ValueError("TUF_OLD_ROOT_GATE_UNEXPECTED")
  candidates=[x for x in old["children"]
              if x.get("obligation")=="OLD_ROOT_REGISTERED_ROLE_UNIQUE_ED25519_SIGNATURE"
              and x.get("value") is False]
  if len(candidates)!=1:
   raise ValueError("TUF_FALSE_LEAF_NOT_UNIQUE")
  chosen=candidates[0]
  chosen["value"]=True
 elif role=="K8S_THIRD_CEL":
  matches=[]
  for branch in forged["formula"]["children"]:
   for leaf in branch["children"]:
    if (leaf["obligation"]=="K8S_REGISTERED_CEL_NOT_EQUAL_SUBSET"
        and "third_policy" in leaf["source_refs"]
        and leaf["value"] is True):
     matches.append(leaf)
  if len(matches)!=1:
   raise ValueError("K8S_THIRD_CEL_LEAF_NOT_UNIQUE")
  chosen=matches[0]
  chosen["value"]=False
 else:raise ValueError("P1_ROLE_UNREGISTERED")
 # Strictly prove exactly the ONE modified value; no other source/identity
 # or scope is changed. Canonical program copy reparses unchanged after undo.
 restored=copy.deepcopy(forged)
 if role=="OLD_ROOT":
  restored["formula"]["children"][1]["children"][0]["value"]=False
 else:
  for branch in restored["formula"]["children"]:
   for leaf in branch["children"]:
    if ("third_policy" in leaf.get("source_refs",[]) and
        leaf.get("obligation")=="K8S_REGISTERED_CEL_NOT_EQUAL_SUBSET"):
      leaf["value"]=True
 if restored!=program:
  raise ValueError("UNREGISTERED_SEMANTIC_FORGERY_CHANGED_ANOTHER_FIELD")
 return forged,{"role":role,"atom_id":chosen["id"]}

def audit(program_tuf,program_k8s,b9_tuf,b9_k8s):
 orig={**get_map(program_tuf),**get_map(program_k8s)}
 baseline={**get_map(b9_tuf),**get_map(b9_k8s)}
 if len(orig)!=16 or len(baseline)!=16 or set(orig)!=set(baseline):
  raise ValueError("E2_ORIGINAL_16_REFERENCE_SET_NOT_SAME")
 rows=[]
 for key,register in ATTACKS.items():
  original=orig[key]
  b9=baseline[key]["direct_B9_source_only_effect"]
  original_verdict=check_program(original)
  if (original_verdict["status"]!="QUALIFIED_BOUNDED_RULE_EVALUATED"
     or original_verdict["scoped_effect_bit"]!=b9
     or original_verdict["scoped_effect_bit"]!=register["original"]):
   raise ValueError("P1_ORIGINAL_E2_SOURCE_EVIDENCE_NOT_VALIDATED:"+key)
  forged,change=mutate_one(original,register["role"])
  verifier=check_program(forged)
  if (verifier["status"]!="QUALIFIED_BOUNDED_RULE_EVALUATED"
      or verifier["scoped_effect_bit"]!=register["after"]
      or verifier["scoped_effect_bit"]==b9):
   raise ValueError("P1_FORGERY_DID_NOT_ISOLATE_GENERIC_CHECKER_GAP:"+key)
  if original["verified_source_sha256"]!=forged["verified_source_sha256"]:
   raise ValueError("P1_SOURCE_HASH_MUTATED")
  rows.append({
    "case_id":key,"family":register["family"],
    "original_source_only_B9_effect":b9,
    "unmodified_common_checker_effect":original_verdict["scoped_effect_bit"],
    "forged_leaf_checker_status":verifier["status"],
    "forged_leaf_checker_effect":verifier["scoped_effect_bit"],
    "forged_atom":change,"total_semantic_leaf_values_changed":1,
    "source_hashes_identical":True,
    "raw_native_source_bytes_modified":False,
    "original_E2_scored_primary_row_changed":False,
    "global_k8s_admission_accept_claimed":False,
  })
 if len(rows)!=2:raise ValueError("P1_TWO_ATTACK_DENOMINATOR_NOT_COMPLETE")
 return {
    "schema":"eeq-r4-e2-p1-postsource-leaf-self-assertion-attack-v1",
    "evidence_class":"POST_SOURCE_ONLY_SYNTHETIC_ATTACK_ON_ARCHIVED_RULE_IR",
    "original_E2_source_only_run":38032779592,
    "original_E2_source_only_run_remains_success":True,
    "target_original_E2_scientific_scope":"BOUNDED_SOURCE_TO_RULE_COMPILER_DEV_B9_TIE",
    "registered_attacks":2,"executed_attacks":len(rows),
    "standalone_generic_structural_checker_semantically_fooled":len(rows),
    "fully_informed_direct_source_B9_catches_both_mismatches":True,
    "raw_source_byte_edits":0,
    "original_E2_certificates_rewritten":0,
    "new_native_calls":0,"original_G5_increment":0,
    "method_independent_value_established":False,
    "standalone_independently_checked_native_authorization_proven":False,
    "scientific_status":"E2_P1_GENERIC_CHECKER_NOT_STANDALONE_NATIVE_SEMANTIC_VERIFIER",
    "attacks":rows
 }

def main():
 p=argparse.ArgumentParser()
 for item in ("tuf","k8s","tuf-b9","k8s-b9","out"):
  p.add_argument("--"+item,required=True)
 a=p.parse_args()
 load=lambda f:json.loads(Path(f).read_text())
 out=audit(load(a.tuf),load(a.k8s),load(a.tuf_b9),load(a.k8s_b9))
 Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:out[k] for k in (
    "registered_attacks","standalone_generic_structural_checker_semantically_fooled",
    "raw_source_byte_edits","scientific_status"
 )},sort_keys=True))

if __name__=="__main__":main()
