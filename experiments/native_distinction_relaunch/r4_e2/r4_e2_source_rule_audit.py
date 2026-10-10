#!/usr/bin/env python3
"""E2 source-derived native-rule compilation differential audit (development only).

Generically checks 16 TUF/K8s rule IR programs against separate native-source
B9 direct source-only reference, NEVER archived native oracle labels.
"""
import argparse,hashlib,json
from pathlib import Path
from collections import Counter
from r4_e2_generic_rule_checker import (
 check_program,verify_registered_pair_sets
)

EXPECTED_TUF={
 "TUF|s2a|root-3-a":True,"TUF|s2a|root-3-b":False,
 "TUF|s2a|root-3-old-only":False,"TUF|s2a|root-3-new-only":False,
 "TUF|s2b|root-3-a":False,"TUF|s2b|root-3-b":True,
 "TUF|s2b|root-3-old-only":False,"TUF|s2b|root-3-new-only":False,
}
EXPECTED_K8S={
 "K8S|S0_INITIAL|flux":True,"K8S|S0_INITIAL|default":False,
 "K8S|A1_POLICY_ADDED|flux":True,"K8S|A1_POLICY_ADDED|default":False,
 "K8S|A2_BINDING_ADDED|flux":True,"K8S|A2_BINDING_ADDED|default":True,
 "K8S|A3_BINDING_DELETED|flux":True,"K8S|A3_BINDING_DELETED|default":False,
}

def fail(cond,why):
 if not cond:raise ValueError(why)

def evaluate(tuf,k8s,tuf_b9,k8s_b9):
 checked=verify_registered_pair_sets(tuf,k8s)
 expected={**EXPECTED_TUF,**EXPECTED_K8S}
 fail(set(checked)==set(expected),"E2_CROSS_DOMAIN_SOURCE_CASE_DENOMINATOR")
 refs=tuf_b9+k8s_b9
 fail(len(refs)==16 and len({x["case_id"] for x in refs})==16,
      "E2_B9_REFERENCE_DENOMINATOR")
 truth={r["case_id"]:r["direct_B9_source_only_effect"] for r in refs}
 fail(set(truth)==set(expected),"E2_SOURCE_B9_REFERENCE_SCOPE")
 fail(all(type(v) is bool for v in truth.values()),"E2_B9_NOT_BOOLEAN")
 fail(all(truth[k]==expected[k] for k in expected),
      "E2_DIRECT_NATIVE_SOURCE_GRAMMAR_REFERENCE_CHANGED")
 matched=[]
 for key in expected:
  got=checked[key]
  fail(got["scoped_effect_bit"]==truth[key],
       "E2_COMMON_IR_NOT_EQUIVALENT_TO_DIRECT_SOURCE_ONLY_B9:"+key)
  fail(got["status"]=="QUALIFIED_BOUNDED_RULE_EVALUATED",
       "E2_GENERIC_CHECKER_FAILED")
  fail(got["global_k8s_admission_accept_authorized"] is False,
       "E2_UNSOUND_GLOBAL_K8S_ACCEPT")
  matched.append({"case_id":key,"family":got["domain"],
                  "generic_source_rule_effect":got["scoped_effect_bit"],
                  "independent_source_only_B9_effect":truth[key],
                  "proof_atoms":got["checked_proof_atoms"],
                  "source_closure_externally_proven":False,
                  "already_scored_native_labels_read":False})
 counter=Counter(q["family"] for q in matched)
 fail(counter=={"TUF_ROOT_UPDATE":8,"K8S_SCOPED_VAP_DENY":8},
      "E2_DOMAIN_COVERAGE_INCOMPLETE")
 return {
  "schema":"eeq-r4-e2-source-derived-rule-compiler-dev-result-v1",
  "evidence_class":"NEW_SOURCE_ONLY_COMPILER_ON_ALREADY_SCORED_NATIVE_DEVELOPMENT_INPUT",
  "tuf_source_qualified_programs":8,
  "k8s_source_qualified_programs":8,
  "cross_family_common_rule_programs":16,
  "all_verified_with_generic_AND_OR_THRESHOLD":16,
  "matched_direct_B9_source_semantics":len(matched),
  "source_only_true_effects":sum(bool(x["generic_source_rule_effect"]) for x in matched),
  "source_only_false_effects":sum(not x["generic_source_rule_effect"] for x in matched),
  "new_native_calls":0,
  "previous_native_outcomes_reused_as_unseen":0,
  "original_v1_G5_increment":0,
  "original_G8_increment":0,
  "source_roster_externally_proven_complete":False,
  "domain_semantic_source_parsers_still_handwritten":True,
  "independent_human_B9_adaptation_test_run":False,
  "full_B9_may_adopt_generic_rule_checker":True,
  "R4_H3_independent_value_established":False,
  "general_source_to_decision_compiler_proven":False,
  "scientific_status":"R4_E2_BOUNDED_SOURCE_TO_RULE_COMPILER_DEV_FEASIBLE_B9_TIE",
  "rows":matched,
 }

def run():
 p=argparse.ArgumentParser()
 for k in ("tuf-programs","k8s-programs","tuf-b9","k8s-b9","out"):
  p.add_argument("--"+k,required=True)
 a=p.parse_args()
 load=lambda f:json.loads(Path(f).read_text())
 result=evaluate(load(a.tuf_programs),load(a.k8s_programs),
                 load(a.tuf_b9),load(a.k8s_b9))
 Path(a.out).write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf8")
 print(json.dumps({k:result[k] for k in (
   "cross_family_common_rule_programs",
   "matched_direct_B9_source_semantics",
   "source_only_true_effects","source_only_false_effects",
   "general_source_to_decision_compiler_proven","scientific_status"
 )},sort_keys=True))

if __name__=="__main__":run()
