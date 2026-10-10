#!/usr/bin/env python3
"""F0 preregistered six foundational countermodels and adversarial kill suite.

No native API calls, no original EEQ evidence import, no speculative H3 win.
The independent oracle intentionally implements legality/preimage logic anew.
"""
import copy
import unittest
from f0_registry import scenarios,REGISTERED_EXPECTED,DELEGATIONS
from f0_intervention_semantics import (
 analyze_all,analyze_registered,least_anchored_authorities,
 initial_world,transition,lawful_observation,authorized_grant
)
from f0_independent_b9_preimage_oracle import (
 exhaustive_reference,independently_verify,reference_anchored,
 diagnostic_pinned_trust_rotation,diagnostic_positive_local_deny
)

class FrozenFoundationalF0(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.inputs=scenarios()
  cls.result={x["case_id"]:x for x in analyze_all()}

 def test_01_six_fixed_unique_foundational_cases(self):
  self.assertEqual(len(self.inputs),6)
  self.assertEqual(set(self.inputs),set(REGISTERED_EXPECTED))
  self.assertEqual(set(self.result),set(REGISTERED_EXPECTED))

 def test_02_all_frozen_statuses_match_without_posthoc_change(self):
  self.assertEqual({k:v["status"] for k,v in self.result.items()},
                   REGISTERED_EXPECTED)

 def test_03_full_information_lawful_B9_exact_parity_six(self):
  for k,row in self.inputs.items():
   p=independently_verify(self.result[k],row)
   self.assertTrue(p["independent_bruteforce_B9_equal"],k)

 def test_04_I01_static_read_access_denied(self):
  r=self.result["I01"]
  self.assertEqual(r["observation_classes"],1)
  self.assertEqual(len(r["identical_observation_opposite_preimage_pair"]),1)
  self.assertFalse(r["independent_grant_anchor_present"])

 def test_05_I02_only_noninterfering_grant_recovers_pre(self):
  r=self.result["I02"]
  self.assertEqual(r["observation_classes"],2)
  self.assertTrue(r["all_pre_worlds_separated_by_lawful_post_observation"])
  self.assertEqual({w["lawful_observation"]["policy_value"] for w in r["worlds"]},{0,1})

 def test_06_I03_destructive_grant_erases_distinction_permanently(self):
  r=self.result["I03"]
  self.assertEqual(r["observation_classes"],1)
  pair=r["identical_observation_opposite_preimage_pair"]
  self.assertEqual(len(pair),1)
  self.assertTrue(pair[0]["same_complete_successor_state"])
  self.assertEqual([w["after_physical_state"]["policy"] for w in r["worlds"]],[1,1])
  self.assertEqual([w["pre_hidden_effect"] for w in r["worlds"]],[0,1])

 def test_07_I04_post_certain_does_not_infer_pre(self):
  r=self.result["I04"]
  self.assertTrue(r["post_effect_certain_from_action_semantics_not_pre_recovery"])
  self.assertEqual(r["partitions"][0]["possible_contract_effects"],[1])
  self.assertEqual({w["pre_hidden_effect"] for w in r["worlds"]},{0,1})

 def test_08_I05_unanchored_two_credential_cycle_is_not_permission(self):
  self.assertEqual(least_anchored_authorities((),DELEGATIONS),())
  self.assertEqual(reference_anchored(set()),set())
  self.assertEqual(self.result["I05"]["status"],"ROOTLESS_DELEGATION_REFUSE")

 def test_09_I05_external_anchor_makes_actual_grant_lawful(self):
  self.assertEqual(set(least_anchored_authorities(("A",),DELEGATIONS)),{"A","B"})
  self.assertEqual(reference_anchored({"A"}),{"A","B"})
  s=self.inputs["I02"]
  self.assertTrue(authorized_grant(s))
  after=transition(initial_world(0),"GRANT_THEN_READ","PRESERVE",True)
  self.assertEqual(lawful_observation(s,after)["policy_value"],0)

 def test_10_I06_hidden_source_no_global_negative_certificate(self):
  r=self.result["I06"]
  self.assertFalse(r["external_native_source_roster_qualifier_proven"])
  self.assertEqual(len(r["identical_observation_opposite_preimage_pair"]),1)
  self.assertEqual({w["registered_objective_effect"] for w in r["worlds"]},{0,1})
  self.assertFalse(r["global_k8s_admission_claim_authorized"])

 def test_11_positive_qualified_local_deny_robust_to_hidden_extra(self):
  self.assertEqual(diagnostic_positive_local_deny(1,None),"SCOPED_DENY_WITNESSED")
  self.assertEqual(diagnostic_positive_local_deny(1,0),"SCOPED_DENY_WITNESSED")
  self.assertEqual(diagnostic_positive_local_deny(1,1),"SCOPED_DENY_WITNESSED")

 def test_12_negative_visible_deny_absence_never_auto_implies_global_accept(self):
  self.assertEqual(diagnostic_positive_local_deny(0,None),"GLOBAL_NEGATIVE_NOT_PROVEN")
  self.assertEqual(diagnostic_positive_local_deny(0,0),
     "GLOBAL_NO_DENY_CONDITIONAL_ON_EXTERNALLY_CERTIFIED_CLOSURE_ONLY")

 def test_13_current_source_authority_rotates_while_bytes_stable(self):
  r=diagnostic_pinned_trust_rotation()
  self.assertTrue(r["byte_identity_preserved"])
  self.assertTrue(r["before_qualified"])
  self.assertFalse(r["after_current_qualified"])
  self.assertTrue(r["after_historical_epoch0_qualified"])

 def test_14_absent_untrusted_permission_must_refuse_before_read(self):
  with self.assertRaisesRegex(PermissionError,"GRANT_NOT_LAWFULLY_ANCHORED"):
   transition(initial_world(0),"GRANT_THEN_READ","PRESERVE",False)
  row=self.inputs["I02"]
  with self.assertRaisesRegex(PermissionError,"NO_READ_RIGHT"):
   lawful_observation(row,initial_world(1))

 def test_15_unsupported_case_identifier_or_authority_edit_refused(self):
  row=copy.deepcopy(self.inputs["I02"])
  row["rooted_grant"]=False
  self.assertEqual(analyze_registered("I02",row)["status"],"MODEL_UNSUPPORTED")
  self.assertEqual(analyze_registered("I07_NEW_CASE",row)["status"],
                   "MODEL_UNSUPPORTED")

 def test_16_pre_post_objective_mutation_is_not_same_case(self):
  row=copy.deepcopy(self.inputs["I03"])
  row["objective"]="POST"
  self.assertEqual(analyze_registered("I03",row)["status"],"MODEL_UNSUPPORTED")

 def test_17_intervention_mode_change_requires_new_protocol(self):
  row=copy.deepcopy(self.inputs["I03"])
  row["mode"]="PRESERVE"
  self.assertEqual(analyze_registered("I03",row)["status"],"MODEL_UNSUPPORTED")

 def test_18_same_registered_identity_but_new_hidden_source_cannot_be_dropped(self):
  row=copy.deepcopy(self.inputs["I06"])
  row["independently_closed_inventory"]=True
  self.assertEqual(analyze_registered("I06",row)["status"],"MODEL_UNSUPPORTED")

 def test_19_original_G4_and_v1_scores_never_updated_by_model(self):
  for r in self.result.values():
   self.assertEqual(r["new_G5_cases"],0)
   self.assertEqual(r["observed_native_outcomes"],0)
   self.assertFalse(r["method_novelty_established"])

 def test_20_prestate_collision_remains_after_arbitrarily_repeated_passive_reads(self):
  r=self.result["I03"]
  a,b=(r["worlds"][0]["after_physical_state"],
       r["worlds"][1]["after_physical_state"])
  self.assertEqual(a,b)
  for _ in range(10):
   self.assertEqual(lawful_observation(self.inputs["I03"],a),
                    lawful_observation(self.inputs["I03"],b))

 def test_21_unrelated_metadata_change_not_an_observation_of_prebit(self):
  row=self.inputs["I03"]
  s0=initial_world(0);s1=initial_world(1)
  s0["unrelated_note"]="extra";s1["unrelated_note"]="other"
  a0=transition(s0,"GRANT_THEN_READ","OVERWRITE_TRUE",True)
  a1=transition(s1,"GRANT_THEN_READ","OVERWRITE_TRUE",True)
  self.assertEqual(lawful_observation(row,a0),lawful_observation(row,a1))
  self.assertNotEqual(s0["policy"],s1["policy"])

 def test_22_not_a_real_tuf_k8s_or_global_c1_gate(self):
  for r in self.result.values():
   self.assertFalse(r["global_k8s_admission_claim_authorized"])
   self.assertFalse(r["external_native_source_roster_qualifier_proven"])
   self.assertTrue(r["full_B9_gets_same_lawful_observation_model"])
   self.assertEqual(r["evidence_class"],
      "SOURCE_FREE_SYNTHETIC_FOUNDATIONAL_COUNTERMODEL_ONLY")

 def test_23_independent_oracle_kills_fabricated_identifiability(self):
  r=copy.deepcopy(self.result["I03"])
  r["status"]="IDENTIFIABLE_AFTER_NONINTERFERING_INTERVENTION"
  with self.assertRaisesRegex(AssertionError,"DISPOSITION_DISAGREES"):
   independently_verify(r,self.inputs["I03"])

 def test_24_independent_oracle_kills_hidden_source_denominator_mask(self):
  r=copy.deepcopy(self.result["I06"])
  r["observation_classes"]=2
  with self.assertRaisesRegex(AssertionError,"OBSERVATION_DENOMINATOR"):
   independently_verify(r,self.inputs["I06"])

 def test_25_independent_oracle_kills_forged_no_collision_witness(self):
  r=copy.deepcopy(self.result["I03"])
  r["identical_observation_opposite_preimage_pair"]=[]
  with self.assertRaisesRegex(AssertionError,"PREIMAGE_COLLISION"):
   independently_verify(r,self.inputs["I03"])

 def test_26_independent_oracle_kills_forged_post_is_pre(self):
  r=copy.deepcopy(self.result["I04"])
  r["post_effect_certain_from_action_semantics_not_pre_recovery"]=False
  with self.assertRaisesRegex(AssertionError,"POST_CLAIM_CONFUSED"):
   independently_verify(r,self.inputs["I04"])

if __name__=="__main__":
 unittest.main(verbosity=2)
