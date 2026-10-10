#!/usr/bin/env python3
"""Preregistered C1 W1 source-only tests. Does not start or read Kubernetes."""
import copy, unittest
from c1_w1_source_only import (
 SOURCES, STAGES, EVENTS, CLASSES, POLICY_API, BINDING_API,
 P0,P3,B0,B3,from_authoritative_sources,registered_forecast
)

class SourceOnlyW1(unittest.TestCase):
 def test_01_six_old_native_sources_exactly_pinned(self):
  docs,m=from_authoritative_sources()
  self.assertEqual(len(docs),6)
  self.assertTrue(all(len(q['sha256'])==64 for q in m['source_files']))
 def test_02_three_preregistered_watch_events(self):
  _,m=registered_forecast()
  self.assertEqual(len(m['watch_events']),3)
  self.assertEqual([(e['class'],e['type'],e['name']) for e in m['watch_events']],[
   ('policy','ADDED',P3),('binding','ADDED',B3),('binding','DELETED',B3)])
 def test_03_four_complete_scoped_source_steps(self):
  _,m=registered_forecast()
  self.assertEqual(len(m['stages']),4)
  self.assertEqual([len(q['expected_binding_names']) for q in m['stages']],[2,2,3,2])
  self.assertEqual([len(q['expected_policy_names']) for q in m['stages']],[1,2,2,2])
 def test_04_original_member_identities_persist_all_stages(self):
  _,m=registered_forecast()
  for s in m['stages']:
   self.assertIn(P0,s['expected_policy_names'])
   for b in B0: self.assertIn(b,s['expected_binding_names'])
 def test_05_third_policy_without_binding_no_added_admission_binding(self):
  _,m=registered_forecast()
  self.assertIn(P3,m['stages'][1]['expected_policy_names'])
  self.assertNotIn(B3,m['stages'][1]['expected_binding_names'])
 def test_06_delete_third_binding_retains_policy(self):
  _,m=registered_forecast()
  self.assertIn(P3,m['stages'][3]['expected_policy_names'])
  self.assertNotIn(B3,m['stages'][3]['expected_binding_names'])
 def test_07_two_independent_unfiltered_collection_endpoints(self):
  self.assertEqual(CLASSES['policy']['path'],POLICY_API)
  self.assertEqual(CLASSES['binding']['path'],BINDING_API)
  self.assertNotEqual(CLASSES['policy']['path'],CLASSES['binding']['path'])
 def test_08_b9_entitled_same_cursor_evidence(self):
  _,m=registered_forecast()
  self.assertTrue(m['fully_informed_b9_entitled_same_tools'])
  self.assertFalse(m['global_admission_accept_certified'])
 def test_09_no_claim_of_cross_kind_atomicity(self):
  _,m=registered_forecast()
  self.assertFalse(m['cross_class_atomic_snapshot_certified'])
 def test_10_zero_native_scoring_cases(self):
  s,m=registered_forecast()
  self.assertEqual(s['new_native_decision_cells'],0)
  self.assertEqual(m['registrations']['native_decisions'],0)
  self.assertEqual(s['main_v1_g5_increment'],0)
 def test_11_exact_snapshot_watch_action_denominators(self):
  _,m=registered_forecast()
  self.assertEqual(m['registrations'],{
   'watch_channels':2,'watch_events':3,'full_list_snapshots':8,
   'native_mutations':3,'native_decisions':0})
 def test_12_model_independent_of_previous_native_labels(self):
  _,m=registered_forecast()
  self.assertTrue(m['source_only'])
  self.assertFalse(m['native_outcomes_read'])
  self.assertNotIn('native_result',m)
 if __name__=='__main__':
  unittest.main(verbosity=2)
