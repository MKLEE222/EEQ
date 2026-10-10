#!/usr/bin/env python3
"""V2B retrospective TypeMeta-only COPY anti-masking, entirely synthetic."""
import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from c1_w1_source_only import registered_forecast
from c1_w1_scoped_evidence_verifier import verify
from c1_w1_join_only_scorer import join
from test_c1_w1_join_only_scorer import mock_raw
from c1_w1_v2b_copy_absent_typemeta import clean,RefuseNativeShape

M,F=registered_forecast()

def native_missing_member_typemeta():
 x=mock_raw()
 for checkpoint in x["checkpoints"]:
  for kind in ("policy","binding"):
   for item in checkpoint["collections"][kind]["response"]["items"]:
    del item["kind"]
    del item["apiVersion"]
 return x

class AbsentTypeMetaOnlyCopy(unittest.TestCase):
 def setUp(self):self.x=native_missing_member_typemeta()
 def test_01_exact_16_members_32_absent_fields(self):
  y,info=clean(self.x)
  self.assertEqual((info["native_list_items_typed_on_new_copy"],
                    info["added_absent_item_typemeta_fields"]),(16,32))
  self.assertTrue(info["original_native_raw_unchanged"])
 def test_02_original_frozen_verifier_accepts_only_the_synthetic_copy(self):
  y,_=clean(self.x)
  self.assertEqual(verify(y,F)["status"],
   "C1_W1_SCOPED_NATIVE_LIST_WATCH_FEASIBILITY_B9_TIE")
  self.assertEqual(verify(self.x,F)["status"],"REFUSE_COLLECTION_ITEM_SHAPE")
 def test_03_original_join_scorer_reused_not_revised(self):
  y,_=clean(self.x)
  r=join(M,F,y)
  self.assertEqual(r["captured_native_watch_events"],3)
  self.assertFalse(r["method_novelty_established"])
 def test_04_present_WRONG_kind_is_not_normalized(self):
  self.x["checkpoints"][0]["collections"]["binding"]["response"]["items"][0]["kind"]="Pod"
  with self.assertRaisesRegex(RefuseNativeShape,"TYPEMETA_NOT_ABSENT"):clean(self.x)
 def test_05_present_even_correct_kind_outside_measured_shape(self):
  self.x["checkpoints"][0]["collections"]["policy"]["response"]["items"][0]["kind"]="ValidatingAdmissionPolicy"
  with self.assertRaisesRegex(RefuseNativeShape,"TYPEMETA_NOT_ABSENT"):clean(self.x)
 def test_06_present_wrong_apiVersion_is_not_normalized(self):
  self.x["checkpoints"][0]["collections"]["policy"]["response"]["items"][0]["apiVersion"]="v0"
  with self.assertRaisesRegex(RefuseNativeShape,"TYPEMETA_NOT_ABSENT"):clean(self.x)
 def test_07_missing_uid_fails(self):
  del self.x["checkpoints"][0]["collections"]["policy"]["response"]["items"][0]["metadata"]["uid"]
  with self.assertRaisesRegex(RefuseNativeShape,"IDENTITY_OR_SPEC"):clean(self.x)
 def test_08_missing_object_RV_fails(self):
  del self.x["checkpoints"][0]["collections"]["binding"]["response"]["items"][0]["metadata"]["resourceVersion"]
  with self.assertRaisesRegex(RefuseNativeShape,"IDENTITY_OR_SPEC"):clean(self.x)
 def test_09_missing_domain_source_spec_fails(self):
  del self.x["checkpoints"][0]["collections"]["binding"]["response"]["items"][0]["spec"]
  with self.assertRaisesRegex(RefuseNativeShape,"IDENTITY_OR_SPEC"):clean(self.x)
 def test_10_bad_list_collection_kind_fails(self):
  self.x["checkpoints"][0]["collections"]["policy"]["response"]["kind"]="PolicyListNotRegistered"
  with self.assertRaisesRegex(RefuseNativeShape,"COLLECTION_TYPE"):clean(self.x)
 def test_11_bad_list_collection_apiVersion_fails(self):
  self.x["checkpoints"][0]["collections"]["policy"]["response"]["apiVersion"]="v2"
  with self.assertRaisesRegex(RefuseNativeShape,"COLLECTION_TYPE"):clean(self.x)
 def test_12_filtered_native_list_cannot_be_called_complete(self):
  self.x["checkpoints"][0]["collections"]["binding"]["selector"]="metadata.name=old"
  with self.assertRaisesRegex(RefuseNativeShape,"LIST_SCOPE"):clean(self.x)
 def test_13_wrong_cursor_not_changed_or_masked(self):
  self.x["watches"]["binding"]["resourceVersion"]="tampered"
  y,_=clean(self.x)
  self.assertEqual(verify(y,F)["status"],"REFUSE_LIST_WATCH_CURSOR_MISMATCH")
 def test_14_changed_watch_event_uid_not_patched(self):
  self.x["watch_events"][1]["event"]["object"]["metadata"]["uid"]="stolen"
  y,_=clean(self.x)
  self.assertEqual(verify(y,F)["status"],"REFUSE_WATCH_LIST_OBJECT_IDENTITY_MISMATCH")
 def test_15_truncated_actual_WATCH_denominator_not_patched(self):
  self.x["watch_events"].pop()
  y,_=clean(self.x)
  self.assertEqual(verify(y,F)["status"],"REFUSE_WATCH_EVENT_DENOMINATOR")
 def test_16_duplicate_source_member_id_fails(self):
  p=self.x["checkpoints"][0]["collections"]["binding"]["response"]["items"]
  p.append(copy.deepcopy(p[0]))
  with self.assertRaisesRegex(RefuseNativeShape,"DUPLICATE_MEMBER"):clean(self.x)
 def test_17_missing_bound_source_fails(self):
  self.x["checkpoints"][0]["collections"]["binding"]["response"]["items"].pop()
  with self.assertRaisesRegex(RefuseNativeShape,"INVENTORY_OUT"):clean(self.x)
 def test_18_unregistered_extra_source_fails(self):
  p=self.x["checkpoints"][0]["collections"]["binding"]["response"]["items"]
  q=copy.deepcopy(p[0]);q["metadata"]["name"]="unknown";q["metadata"]["uid"]="new"
  p.append(q)
  with self.assertRaisesRegex(RefuseNativeShape,"INVENTORY_OUT"):clean(self.x)
 def test_19_original_scored_workflow_failure_unchanged(self):
  y,info=clean(self.x)
  self.assertEqual(info["original_V1_native_workflow_scientific_status"],"FAILURE")
 def test_20_action_cannot_be_relabelled(self):
  self.x["mutations"][1]["action"]="DELETE_ANOTHER_SOURCE"
  y,_=clean(self.x)
  self.assertEqual(verify(y,F)["status"],"REFUSE_NATIVE_MUTATION_FAILED")
 def test_21_old_original_binding_spec_changed_refused(self):
  p=self.x["checkpoints"][2]["collections"]["binding"]["response"]["items"][0]
  p["spec"]["policyName"]="changed-authority"
  y,_=clean(self.x)
  self.assertEqual(verify(y,F)["status"],"REFUSE_ORIGINAL_SOURCE_MUTATED")
 def test_22_no_native_decisions_or_H3_sneak_through(self):
  y,info=clean(self.x)
  self.assertEqual(y["native_pod_decision_calls"],0)
  self.assertFalse(info["B9_independent_value"])
  self.assertFalse(info["global_c1_proven"])

if __name__=="__main__":
 unittest.main(verbosity=2)
