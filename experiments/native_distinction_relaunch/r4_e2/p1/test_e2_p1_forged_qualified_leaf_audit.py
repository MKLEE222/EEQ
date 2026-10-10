#!/usr/bin/env python3
"""P1 prescore SYNTHETIC proof-leaf forgery adversaries, no E2 archived sources.

These tests demonstrate the type/lineage checker's logical TRUST boundary:
source hash references stay the same even when a Boolean premise is forged.
They are not attempts to authorize global native Kubernetes admission.
"""
import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from r4_e2_generic_rule_checker import check_program
from e2_p1_forged_qualified_leaf_audit import mutate_one,ATTACKS

A="a"*64
B="b"*64
C="c"*64


def leaf(id_,v,refs,obligation):
 return {"op":"ATOM","id":id_,"value":v,
         "source_refs":refs,"obligation":obligation}


def tuf_synthetic():
 return {
  "schema":"eeq-r4-e2-native-source-qualified-rule-ir-v1",
  "domain":"TUF_ROOT_UPDATE","case_id":"fake_tuf",
  "registered_contract":"P1_NONNATIVE_SYNTHETIC_TUF_ROOT_CONTRACT",
  "verified_source_sha256":{"anchor_root":A,"trusted_root":B,"candidate_root":C},
  "native_labels_read":False,
  "evidence_class":"PREVIOUS_NATIVE_DEVELOPMENT_SOURCE_BYTES_NEW_COMPILER",
  "source_closure_is_author_independently_attested":False,
  "formula":{"op":"AND","children":[
    leaf("VERSION_CONTIGUOUS",True,["trusted_root","candidate_root"],
         "TUF_ROOT_VERSION_SUCCESSION_FROM_SOURCE_BYTES"),
    {"op":"THRESHOLD","k":1,"children":[
      leaf("OLD_ROOT:synthetic_key",False,["trusted_root","candidate_root"],
           "OLD_ROOT_REGISTERED_ROLE_UNIQUE_ED25519_SIGNATURE")]},
    {"op":"THRESHOLD","k":1,"children":[
      leaf("NEW_ROOT:synthetic_key",True,["candidate_root"],
           "NEW_ROOT_REGISTERED_ROLE_UNIQUE_ED25519_SIGNATURE")]}
  ]}
 }


def k8s_synthetic():
 return {
  "schema":"eeq-r4-e2-native-source-qualified-rule-ir-v1",
  "domain":"K8S_SCOPED_VAP_DENY","case_id":"fake_k8s",
  "registered_contract":"P1_NONNATIVE_SYNTHETIC_K8S_VAP_CONTRACT",
  "verified_source_sha256":{"namespace":A,"team_binding":B,
        "third_policy":C,"third_binding":A,"default_pod":B},
  "native_labels_read":False,
  "evidence_class":"PREVIOUS_NATIVE_DEVELOPMENT_SOURCE_BYTES_NEW_COMPILER",
  "source_closure_is_author_independently_attested":False,
  "formula":{"op":"OR","children":[
   {"op":"AND","children":[
      leaf("team_selector",True,["namespace","team_binding"],
           "K8S_BINDING_MATCHLABELS_SOURCE_QUALIFIED"),
      leaf("team_cel",False,["default_pod"],
           "K8S_REGISTERED_CEL_NOT_EQUAL_SUBSET")]},
   {"op":"AND","children":[
      leaf("third_selector",True,["namespace","third_binding"],
           "K8S_BINDING_MATCHLABELS_SOURCE_QUALIFIED"),
      leaf("third_cel",True,["third_policy","default_pod"],
           "K8S_REGISTERED_CEL_NOT_EQUAL_SUBSET")]}
  ]}
 }


class P1StandaloneCheckerTrustKill(unittest.TestCase):
 def test_01_two_distinct_scoped_families_frozen(self):
  self.assertEqual(set(ATTACKS),{
   "TUF|s2a|root-3-b","K8S|A2_BINDING_ADDED|default"})
  self.assertEqual({x["family"] for x in ATTACKS.values()},
                   {"TUF_ROOT_UPDATE","K8S_SCOPED_VAP_DENY"})
 def test_02_original_tuf_ir_false(self):
  p=tuf_synthetic()
  r=check_program(p)
  self.assertEqual(r["status"],"QUALIFIED_BOUNDED_RULE_EVALUATED")
  self.assertIs(r["scoped_effect_bit"],False)
 def test_03_tuf_one_wrong_old_role_leaf_changes_generic_effect(self):
  original=tuf_synthetic()
  forged,n=mutate_one(original,"OLD_ROOT")
  self.assertIs(check_program(forged)["scoped_effect_bit"],True)
  self.assertEqual(n["atom_id"],"OLD_ROOT:synthetic_key")
  self.assertEqual(original["verified_source_sha256"],forged["verified_source_sha256"])
  self.assertIs(check_program(original)["scoped_effect_bit"],False)
 def test_04_original_k8s_ir_true_scoped_deny_only(self):
  p=k8s_synthetic()
  r=check_program(p)
  self.assertIs(r["scoped_effect_bit"],True)
  self.assertFalse(r["global_k8s_admission_accept_authorized"])
 def test_05_k8s_one_wrong_cel_leaf_changes_generic_effect(self):
  original=k8s_synthetic()
  forged,n=mutate_one(original,"K8S_THIRD_CEL")
  self.assertIs(check_program(forged)["scoped_effect_bit"],False)
  self.assertEqual(n["atom_id"],"third_cel")
  self.assertEqual(original["verified_source_sha256"],forged["verified_source_sha256"])
  self.assertIs(check_program(original)["scoped_effect_bit"],True)
 def test_06_tuf_false_old_authority_leaf_missing_refuses_attack_target(self):
  p=tuf_synthetic()
  p["formula"]["children"][1]["children"][0]["value"]=True
  with self.assertRaisesRegex(ValueError,"TUF_FALSE_LEAF_NOT_UNIQUE"):
   mutate_one(p,"OLD_ROOT")
 def test_07_multiple_unqualified_tuf_signers_refuses_target_choice(self):
  p=tuf_synthetic()
  p["formula"]["children"][1]["children"].append(
      leaf("OLD_ROOT:extra",False,["trusted_root","candidate_root"],
           "OLD_ROOT_REGISTERED_ROLE_UNIQUE_ED25519_SIGNATURE"))
  with self.assertRaisesRegex(ValueError,"TUF_FALSE_LEAF_NOT_UNIQUE"):
   mutate_one(p,"OLD_ROOT")
 def test_08_no_qualifying_third_cel_refuses_target_choice(self):
  p=k8s_synthetic()
  p["formula"]["children"][1]["children"][1]["value"]=False
  with self.assertRaisesRegex(ValueError,"K8S_THIRD_CEL_LEAF_NOT_UNIQUE"):
   mutate_one(p,"K8S_THIRD_CEL")
 def test_09_two_third_cel_nodes_refuses_target_choice(self):
  p=k8s_synthetic()
  p["formula"]["children"].append({"op":"AND","children":[
     leaf("another_selector",True,["third_binding"],
          "K8S_BINDING_MATCHLABELS_SOURCE_QUALIFIED"),
     leaf("another_cel",True,["third_policy"],
          "K8S_REGISTERED_CEL_NOT_EQUAL_SUBSET")]})
  with self.assertRaisesRegex(ValueError,"K8S_THIRD_CEL_LEAF_NOT_UNIQUE"):
   mutate_one(p,"K8S_THIRD_CEL")
 def test_10_not_a_real_native_or_global_accept_certificate(self):
  for p,role in ((tuf_synthetic(),"OLD_ROOT"),
                 (k8s_synthetic(),"K8S_THIRD_CEL")):
   forged,_=mutate_one(p,role)
   r=check_program(forged)
   self.assertEqual(r["status"],"QUALIFIED_BOUNDED_RULE_EVALUATED")
   self.assertFalse(r["global_k8s_admission_accept_authorized"])
   self.assertFalse(r["native_domain_semantic_compiler_automatically_general"])
   self.assertTrue(r["fully_informed_B9_may_use_same_code"])

if __name__=="__main__":
 unittest.main(verbosity=2)
