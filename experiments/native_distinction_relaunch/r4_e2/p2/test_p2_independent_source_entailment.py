#!/usr/bin/env python3
"""P2 synthetic fail-closed trusted leaf witness tests, no E2 archived labels."""
import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "p1"))
from test_e2_p1_forged_qualified_leaf_audit import tuf_synthetic,k8s_synthetic
from e2_p1_forged_qualified_leaf_audit import mutate_one
from p2_independent_original_source_entailment_checker import verify

def witness(program):
 w={
  "case_id":program["case_id"],"domain":program["domain"],
  "registered_contract":program["registered_contract"],
  "verified_source_sha256":copy.deepcopy(program["verified_source_sha256"]),
  "formula":copy.deepcopy(program["formula"])
 }
 if program["domain"]=="TUF_ROOT_UPDATE":
  w["original_source_only_setup_proven_by_new_primitive_verifier"]=True
  w["E2_candidate_IR_or_B9_output_never_read"]=True
 else:
  w["old_native_decisions_never_read"]=True
  w["authored_membership_NOT_a_live_authorized_list"]=True
 return w

class P2NegativePrimitiveRecheckTests(unittest.TestCase):
 def test_01_scoped_synthetic_TUF_valid_external_entailment(self):
  p=tuf_synthetic();r=verify(p,witness(p))
  self.assertEqual(r["status"],"SCOPED_SOURCE_PRIMITIVES_INDEPENDENTLY_RECHECKED")
  self.assertIs(r["scoped_effect_bit"],False)
 def test_02_TUF_old_role_forgery_is_rejected_as_not_entailed(self):
  p=tuf_synthetic();w=witness(p);forged,_=mutate_one(p,"OLD_ROOT")
  r=verify(forged,w)
  self.assertEqual(r["status"],"REFUSE_SOURCE_ENTAILMENT")
  self.assertFalse(r["global_k8s_admission_accept_authorized"])
 def test_03_scoped_synthetic_K8s_valid_entailment(self):
  p=k8s_synthetic();r=verify(p,witness(p))
  self.assertEqual(r["status"],"SCOPED_SOURCE_PRIMITIVES_INDEPENDENTLY_RECHECKED")
  self.assertIs(r["scoped_effect_bit"],True)
 def test_04_K8s_third_CEL_false_forgery_refused(self):
  p=k8s_synthetic();w=witness(p);forged,_=mutate_one(p,"K8S_THIRD_CEL")
  self.assertEqual(verify(forged,w)["status"],"REFUSE_SOURCE_ENTAILMENT")
 def test_05_mutated_source_sha_map_cannot_inherit_semantic_witness(self):
  p=tuf_synthetic();w=witness(p)
  p["verified_source_sha256"]["trusted_root"]="e"*64
  self.assertEqual(verify(p,w)["status"],"REFUSE_SOURCE_ENTAILMENT")
 def test_06_forged_native_case_id_cannot_use_old_witness(self):
  p=k8s_synthetic();w=witness(p)
  p["case_id"]="falsified_reference"
  self.assertEqual(verify(p,w)["status"],"REFUSE_SCOPE_OR_NATIVE_LEAKAGE")
 def test_07_wrong_formula_operator_not_entailed_even_with_same_atoms(self):
  p=tuf_synthetic();w=witness(p)
  p["formula"]["op"]="OR"
  self.assertEqual(verify(p,w)["status"],"REFUSE_SOURCE_ENTAILMENT")
 def test_08_threshold_changed_not_entailed(self):
  p=tuf_synthetic();w=witness(p)
  p["formula"]["children"][1]["k"]=0
  self.assertEqual(verify(p,w)["status"],"MODEL_UNSUPPORTED")
  p=tuf_synthetic();w=witness(p)
  p["formula"]["children"][1]["children"].append(copy.deepcopy(
        p["formula"]["children"][1]["children"][0]))
  p["formula"]["children"][1]["children"][-1]["id"]="new_label"
  self.assertEqual(verify(p,w)["status"],"REFUSE_SOURCE_ENTAILMENT")
 def test_09_unknown_qualified_premise_not_silently_false(self):
  p=k8s_synthetic();w=witness(p)
  p["formula"]["children"][1]["children"][1]["value"]=None
  self.assertEqual(verify(p,w)["status"],"MODEL_UNSUPPORTED")
 def test_10_tampered_independent_native_witness_sources_fail_closed(self):
  p=tuf_synthetic();w=witness(p)
  w["verified_source_sha256"]["candidate_root"]="0"*64
  self.assertEqual(verify(p,w)["status"],"REFUSE_SOURCE_ENTAILMENT")
 def test_11_unverified_TUF_common_anchor_cannot_be_silent(self):
  p=tuf_synthetic();w=witness(p)
  w["original_source_only_setup_proven_by_new_primitive_verifier"]=False
  self.assertEqual(verify(p,w)["status"],"REFUSE_SOURCE_ENTAILMENT")
 def test_12_wrong_K8s_claimed_membership_class_not_allowed(self):
  p=k8s_synthetic();w=witness(p)
  w["authored_membership_NOT_a_live_authorized_list"]=False
  self.assertEqual(verify(p,w)["status"],"REFUSE_SOURCE_ENTAILMENT")
 def test_13_false_old_native_label_blinding_veto(self):
  p=k8s_synthetic();w=witness(p)
  p["native_labels_read"]=True
  self.assertEqual(verify(p,w)["status"],"MODEL_UNSUPPORTED")
 def test_14_cross_family_witness_swap_refused(self):
  p=tuf_synthetic();w=witness(k8s_synthetic())
  self.assertEqual(verify(p,w)["status"],"MODEL_UNSUPPORTED")
 def test_15_absent_witness_refused(self):
  self.assertEqual(verify(tuf_synthetic(),None)["status"],"MODEL_UNSUPPORTED")
 def test_16_global_native_admission_and_independent_B9_not_claimed(self):
  for program in (tuf_synthetic(),k8s_synthetic()):
   r=verify(program,witness(program))
   self.assertFalse(r["global_k8s_admission_accept_authorized"])
   self.assertFalse(r["live_source_roster_completeness_proven"])
   self.assertFalse(r["independent_B9_advantage_proven"])
   self.assertTrue(r["domain_native_semantics_still_handwritten"])
 def test_17_missing_registered_source_lineage_refused(self):
  p=k8s_synthetic();w=witness(p)
  p["formula"]["children"][1]["children"][1]["source_refs"]=["unlisted"]
  self.assertEqual(verify(p,w)["status"],"MODEL_UNSUPPORTED")
 def test_18_source_schema_and_contract_bound(self):
  p=tuf_synthetic();w=witness(p)
  p["registered_contract"]="not_the_source_contract"
  self.assertEqual(verify(p,w)["status"],"REFUSE_SCOPE_OR_NATIVE_LEAKAGE")

if __name__=="__main__":unittest.main(verbosity=2)
