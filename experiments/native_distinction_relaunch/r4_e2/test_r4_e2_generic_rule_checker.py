#!/usr/bin/env python3
"""Generic E2 proof AST anti-masking tests, zero domain/native oracle input."""
import copy,unittest
from r4_e2_generic_rule_checker import check_program,verify_registered_pair_sets

D="a"*64
E="b"*64
def a(id_,value,source_refs=None):
 return {"op":"ATOM","id":id_,"value":value,
         "source_refs":source_refs or ["a"],
         "obligation":"REGISTERED_SOURCE_QUALIFIED_PREDICATE"}
def base():
 return {
  "schema":"eeq-r4-e2-native-source-qualified-rule-ir-v1",
  "domain":"TUF_ROOT_UPDATE","case_id":"synthetic_case",
  "registered_contract":"SOURCE_SCOPED_UNIT_DIAGNOSTIC",
  "verified_source_sha256":{"a":D,"b":E},
  "native_labels_read":False,
  "source_closure_is_author_independently_attested":False,
  "evidence_class":"PREVIOUS_NATIVE_DEVELOPMENT_SOURCE_BYTES_NEW_COMPILER",
  "formula":{"op":"AND","children":[
    a("version",True),
    {"op":"THRESHOLD","k":2,"children":[a("k1",True),a("k2",True),a("k3",False)]},
    {"op":"OR","children":[a("s1",False),a("s2",True)]}
  ]}
 }

class GenericE2Checks(unittest.TestCase):
 def setUp(self):self.s=base()
 def status(self):return check_program(self.s)["status"]
 def test_01_boolean_source_rule_exact(self):
  self.assertEqual(self.status(),"QUALIFIED_BOUNDED_RULE_EVALUATED")
  self.assertTrue(check_program(self.s)["scoped_effect_bit"])
 def test_02_threshold_no_fake_extra_signature_credit(self):
  self.s["formula"]["children"][1]["children"][1]["value"]=False
  self.assertFalse(check_program(self.s)["scoped_effect_bit"])
 def test_03_invalid_threshold_is_not_boolean_false(self):
  self.s["formula"]["children"][1]["k"]=4
  self.assertEqual(self.status(),"MODEL_UNSUPPORTED")
 def test_04_duplicate_signature_atom_is_not_counted_twice(self):
  self.s["formula"]["children"][1]["children"][1]["id"]="k1"
  self.assertEqual(self.status(),"MODEL_UNSUPPORTED")
 def test_05_digests_and_native_source_references_mandatory(self):
  self.s["formula"]["children"][1]["children"][1]["source_refs"]=["missing"]
  self.assertEqual(self.status(),"MODEL_UNSUPPORTED")
 def test_06_empty_and_not_vacuously_true(self):
  self.s["formula"]["children"]=[]
  self.assertEqual(self.status(),"MODEL_UNSUPPORTED")
 def test_07_empty_or_not_vacuously_false(self):
  self.s["formula"]["children"][2]["children"]=[]
  self.assertEqual(self.status(),"MODEL_UNSUPPORTED")
 def test_08_non_boolean_unknown_not_mapped_to_false(self):
  self.s["formula"]["children"][0]["value"]="UNKNOWN"
  self.assertEqual(self.status(),"MODEL_UNSUPPORTED")
 def test_09_int_one_not_qualified_boolean(self):
  self.s["formula"]["children"][0]["value"]=1
  self.assertEqual(self.status(),"MODEL_UNSUPPORTED")
 def test_10_false_completed_contract_claim_rejected(self):
  self.s["source_closure_is_author_independently_attested"]=True
  self.assertEqual(self.status(),"MODEL_UNSUPPORTED")
 def test_11_old_native_prediction_ever_read_refused(self):
  self.s["native_labels_read"]=True
  self.assertEqual(self.status(),"MODEL_UNSUPPORTED")
 def test_12_bad_scope_or_source_hash_never_scored(self):
  self.s["registered_contract"]=""
  self.assertEqual(self.status(),"MODEL_UNSUPPORTED")
  self.s=base()
  self.s["verified_source_sha256"]["a"]="forged"
  self.assertEqual(self.status(),"MODEL_UNSUPPORTED")
 def test_13_threshold_nonatom_child_invalid(self):
  self.s["formula"]["children"][1]["children"][0]={
      "op":"OR","children":[a("nested",True)]}
  self.assertEqual(self.status(),"MODEL_UNSUPPORTED")
 def test_14_missing_cross_family_program_rows_not_relabelled(self):
  with self.assertRaisesRegex(Exception,"DENOMINATOR_NOT_8"):
   verify_registered_pair_sets([self.s],[])
 def test_15_unregistered_operator_fails_closed(self):
  self.s["formula"]["op"]="QUANTUM_UNSUPPORTED"
  self.assertEqual(self.status(),"MODEL_UNSUPPORTED")
 def test_16_source_verified_flag_not_true_for_global_K8s_admission(self):
  self.assertFalse(check_program(self.s)["global_k8s_admission_accept_authorized"])

if __name__=="__main__":unittest.main(verbosity=2)
