#!/usr/bin/env python3
"""Pre-native synthetic full-denominator scorer tests; mocks are NEVER native evidence."""
import copy,unittest
from c1_w1_source_only import registered_forecast
from c1_w1_join_only_scorer import join
from test_c1_w1_scoped_evidence_verifier import make_nominal

M,P=registered_forecast()

def mock_raw():
 r=make_nominal()
 r.update({
  "registered_main_native_watch_events":3,
  "registered_full_source_list_snapshots":8,
  "registered_independent_watch_channels":2,
  "registered_native_source_mutations":3,
  "observed_native_watch_events":3,
  "observed_source_list_snapshots":8,
  "observed_native_source_mutations":3,
  "native_validated_scored_pod_decisions":0,
  "historical_g5_new_cases":0,
  "native_errors":[],
 })
 return r

class JoinOnlyW1Prenative(unittest.TestCase):
 def setUp(self):
  self.raw=mock_raw()
  self.manifest=copy.deepcopy(M)
  self.pred=copy.deepcopy(P)
 def score(self):
  return join(self.manifest,self.pred,self.raw)
 def test_01_synthetic_nominal_never_counts_pod_or_global_accept(self):
  s=self.score()
  self.assertEqual(s["captured_native_watch_events"],3)
  self.assertFalse(s["unbounded_realtime_accept_authorized"])
  self.assertFalse(s["method_novelty_established"])
  self.assertEqual(s["native_pod_decisions_scored"],0)
 def test_02_missing_raw_watch_event_denominator_not_filled(self):
  self.raw["watch_events"].pop()
  self.raw["observed_native_watch_events"]=2
  with self.assertRaisesRegex(ValueError,"DENOMINATOR_FAILED"):
   self.score()
 def test_03_false_native_event_of_same_count_refused(self):
  self.raw["watch_events"][1]["event"]["object"]["metadata"]["uid"]="forged"
  with self.assertRaisesRegex(ValueError,"NATIVE_SOURCE_CUSTODY_INVALID"):
   self.score()
 def test_04_original_native_failure_cannot_be_masked(self):
  self.raw["native_errors"].append("WATCH_DISCONNECTED")
  with self.assertRaisesRegex(ValueError,"NATIVE_RAW_CAPTURE_ERROR_RETAINED"):
   self.score()
 def test_05_g5_inflation_rejected(self):
  self.raw["historical_g5_new_cases"]=3
  with self.assertRaisesRegex(ValueError,"DENOMINATOR_FAILED"):
   self.score()
 def test_06_sealed_source_manifest_changed(self):
  self.manifest["new_native_decision_cells"]=8
  with self.assertRaisesRegex(ValueError,"SOURCE_ONLY_PROVENANCE_OR_SCOPE"):
   self.score()
 def test_07_complete_global_admission_claim_never_allowed(self):
  self.raw["global_admission_accept_claimed"]=True
  with self.assertRaisesRegex(ValueError,"NATIVE_SOURCE_CUSTODY_INVALID"):
   self.score()
 def test_08_missing_watched_class_is_not_absence_proof(self):
  self.raw["watches"].pop("binding")
  with self.assertRaisesRegex(ValueError,"NATIVE_SOURCE_CUSTODY_INVALID"):
   self.score()
 def test_09_denied_native_permission_veto(self):
  self.raw["actor"]["authorized_native_permissions"]["binding"]["watch"]=False
  with self.assertRaisesRegex(ValueError,"NATIVE_SOURCE_CUSTODY_INVALID"):
   self.score()
 def test_10_RV_cursor_changed_cannot_be_repaired_posthoc(self):
  self.raw["watches"]["policy"]["resourceVersion"]="different"
  with self.assertRaisesRegex(ValueError,"NATIVE_SOURCE_CUSTODY_INVALID"):
   self.score()

if __name__=="__main__":
 unittest.main(verbosity=2)
