#!/usr/bin/env python3
"""R4 E1 F0: prescored synthetic 17-row correctness and adversarial kill suite.

No native source bytes, no TUF crypto client, no Kubernetes credential or
already scored native oracle used. Compares exact fully informed B9-eligible
enumeration and *all* finite legal worlds.
"""
import copy,unittest
from collections import Counter
from r4_e1_registry import (
 registry,immutable_case,registered_input_check,FROZEN_STATUS_COUNTS,
 EXPECTATIONS,TOTAL_COST_SUM
)
from r4_e1_frontier import frontier,possible_worlds
from r4_e1_independent_reference import check_frontier_cert,b9_exact_optimum_reference


class FrozenR4E1Study(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=registry()
  cls.results=[frontier(x) for x in cls.s]
  cls.byid={x["case_id"]:x for x in cls.results}

 def test_01_exact_17_synthetic_case_denominator(self):
  self.assertEqual(len(self.s),17)
  self.assertEqual(len({s["case_id"] for s in self.s}),17)
  self.assertEqual({s["case_id"] for s in self.s},set(EXPECTATIONS))

 def test_02_exact_predeclared_disposition_distribution(self):
  self.assertEqual(dict(Counter(r["status"] for r in self.results)),
                   FROZEN_STATUS_COUNTS)

 def test_03_every_registered_scoped_disposition_matches_freeze(self):
  for case_id,(status,worst) in EXPECTATIONS.items():
   r=self.byid[case_id]
   self.assertEqual(r["status"],status,case_id)
   self.assertEqual(r["read_cost_worst_case"],worst,case_id)

 def test_04_exhaustive_reference_independent_oracle_all_17(self):
  proof=[check_frontier_cert(s,frontier(s)) for s in self.s]
  self.assertTrue(all(x["sound"] and x["same_optimal_B9"] for x in proof))
  self.assertEqual(len(proof),17)

 def test_05_strong_b9_same_information_same_exact_cost_all_17(self):
  for s in self.s:
   ours=frontier(s)
   b9=b9_exact_optimum_reference(s)
   self.assertEqual(ours["read_cost_worst_case"],b9["worst"])
   self.assertEqual(ours["read_cost_over_all_finite_worlds"],b9["total"])

 def test_06_three_preregistered_uniform_world_cost_sums(self):
  for name,want in TOTAL_COST_SUM.items():
   self.assertEqual(self.byid[name]["read_cost_over_all_finite_worlds"],
                    want,name)

 def test_07_old_authority_unavailable_is_not_false(self):
  r=self.byid["T01"]
  self.assertEqual(r["status"],"IMPOSSIBLE_UNDER_ACTOR_ACCESS")
  pair=r["inaccessible_distinction_pair"]
  self.assertNotEqual(pair[0]["old"],pair[1]["old"])
  self.assertEqual(pair[0]["new"],pair[1]["new"])

 def test_08_definitively_unsatisfied_TUF_role_suffices_for_reject(self):
  r=self.byid["T02"]
  self.assertEqual(r["status"],"CERTAIN_FALSE")
  self.assertEqual(r["scoped_effect"],"REJECT_ROOT_UPDATE")

 def test_09_TUF_same_signed_bytes_cannot_override_changed_old_authority(self):
  self.assertEqual(self.byid["T06"]["scoped_effect"],"AUTHORIZED_ROOT_UPDATE")
  self.assertEqual(self.byid["T07"]["scoped_effect"],"REJECT_ROOT_UPDATE")
  self.assertEqual(self.byid["T07"]["read_cost_worst_case"],0)

 def test_10_contract_irrelevant_targets_change_does_not_change_root_effect(self):
  self.assertEqual(self.byid["T06"]["scoped_effect"],
                   self.byid["T08"]["scoped_effect"])

 def test_11_k8s_positive_deny_witness_survives_unobserved_other_binding(self):
  r=self.byid["K02"]
  self.assertEqual(r["status"],"CERTAIN_TRUE")
  self.assertEqual(r.get("scoped_effect"),"SCOPED_VAP_DENY")
  self.assertEqual(r["possible_world_count"],2)

 def test_12_missing_access_to_only_remaining_binding_forbids_accept(self):
  r=self.byid["K03"]
  self.assertEqual(r["status"],"IMPOSSIBLE_UNDER_ACTOR_ACCESS")
  self.assertEqual(set(r["world_effects"]),{0,1})

 def test_13_unobserved_third_binding_invalidates_old_two_binding_no_deny(self):
  self.assertEqual(self.byid["K04"]["status"],"IMPOSSIBLE_UNDER_ACTOR_ACCESS")
  self.assertEqual(self.byid["K05"]["status"],"IMPOSSIBLE_UNDER_ACTOR_ACCESS")

 def test_14_closed_default_no_deny_is_not_global_admission_accept(self):
  r=self.byid["K06"]
  self.assertEqual(r["status"],"CERTAIN_FALSE")
  self.assertEqual(r["scoped_effect"],"NO_REGISTERED_VAP_DENY")
  self.assertFalse(r["global_k8s_admission_authorized"])
  self.assertFalse(r["external_source_inventory_completeness_proven"])

 def test_15_third_matching_deny_positive_survives_extra_uncertain_source(self):
  self.assertEqual(self.byid["K07"]["status"],"CERTAIN_TRUE")
  self.assertEqual(self.byid["K07"]["scoped_effect"],"SCOPED_VAP_DENY")

 def test_16_E1_never_self_attests_source_authorization(self):
  for r in self.results:
   self.assertFalse(r["external_source_inventory_completeness_proven"])
   self.assertTrue(r["conditional_on_external_source_qualification"])
   self.assertFalse(r["independent_method_advantage_over_full_B9"])
   self.assertEqual(r["native_calls"],0)
   self.assertEqual(r["original_g5_new_cases"],0)

 def test_17_scope_actor_permission_change_is_not_a_scored_new_case(self):
  for key,value in (
   ("registered_scope","OTHER_CLAIM"),("registered_actor","FORGED_ADMIN"),
   ("lawful_reads",["mode"]),("read_costs",{"team":0,"mode":0})):
   s=copy.deepcopy(immutable_case("K03"))
   s[key]=value
   self.assertEqual(frontier(s)["status"],"MODEL_UNSUPPORTED",key)

 def test_18_unknown_cannot_be_silently_cast_to_false(self):
  s=copy.deepcopy(immutable_case("K05"))
  s["observed"]["additional"]=0
  self.assertEqual(frontier(s)["status"],"MODEL_UNSUPPORTED")
  self.assertEqual(frontier(immutable_case("K05"))["status"],
                   "IMPOSSIBLE_UNDER_ACTOR_ACCESS")

 def test_19_forge_complete_true_does_not_authorize_accept(self):
  s=copy.deepcopy(immutable_case("K05"))
  s["caller_claimed_complete"]=True
  self.assertEqual(frontier(s)["status"],"MODEL_UNSUPPORTED")

 def test_20_missing_duplicate_or_extra_atom_is_invalid(self):
  s=copy.deepcopy(immutable_case("K01"))
  s["atoms"]=["team","team"]
  self.assertEqual(frontier(s)["status"],"MODEL_UNSUPPORTED")
  s=copy.deepcopy(immutable_case("K01"))
  s["atoms"].append("other")
  self.assertEqual(frontier(s)["status"],"MODEL_UNSUPPORTED")
  s=copy.deepcopy(immutable_case("K01"))
  s["atoms"].pop()
  self.assertEqual(frontier(s)["status"],"MODEL_UNSUPPORTED")

 def test_21_fake_certain_certificate_is_killed_by_independent_oracle(self):
  s=immutable_case("K03")
  cert=frontier(s)
  cert["status"]="CERTAIN_FALSE"
  cert["read_cost_worst_case"]=0
  cert["read_cost_over_all_finite_worlds"]=0
  with self.assertRaisesRegex(AssertionError,"FALSE_EVIDENCE_CERTAINTY"):
   check_frontier_cert(s,cert)

 def test_22_impossible_world_pair_forgery_killed(self):
  s=immutable_case("T01")
  cert=frontier(s)
  cert["inaccessible_distinction_pair"][1]["new"]=0
  with self.assertRaises(AssertionError):
   check_frontier_cert(s,cert)

 def test_23_truncated_adaptive_plan_does_not_certify_all_worlds(self):
  s=immutable_case("T04")
  cert=frontier(s)
  cert["adaptive_plan"]={"effect":0}
  with self.assertRaisesRegex(AssertionError,"PLAN_MISCLASSIFIES"):
   check_frontier_cert(s,cert)

 def test_24_cost_not_computed_from_single_favorable_world(self):
  s=immutable_case("K09")
  cert=frontier(s)
  cert["read_cost_over_all_finite_worlds"]=1
  with self.assertRaisesRegex(AssertionError,"COST_DENOMINATOR"):
   check_frontier_cert(s,cert)

 def test_25_bruteforce_strong_B9_beats_expensive_first_plan(self):
  s=immutable_case("K09")
  cert=frontier(s)
  cert["adaptive_plan"]={
   "ask":"additional","read_cost":3,
   "if_true":{"effect":1},
   "if_false":{"ask":"third","read_cost":1,
               "if_true":{"effect":1},"if_false":{"effect":0}}
  }
  cert["read_cost_worst_case"]=4
  cert["read_cost_over_all_finite_worlds"]=14
  with self.assertRaisesRegex(AssertionError,"NOT_STRONG_B9_EQUAL_INFORMATION_OPTIMAL"):
   check_frontier_cert(s,cert)

 def test_26_no_legal_query_read_after_preidentified_effect(self):
  self.assertEqual(self.byid["K02"]["adaptive_plan"],{"effect":1})
  self.assertEqual(self.byid["T02"]["adaptive_plan"],{"effect":0})

 def test_27_no_unseen_family_or_synthetic_as_native_score(self):
  self.assertTrue(all(s["native_source_bytes_read"] is False for s in self.s))
  self.assertTrue(all(s["native_actor_rbac_proven"] is False for s in self.s))
  self.assertTrue(all(r["research_class"].endswith("DEVELOPMENT_ONLY")
                      for r in self.results))

 def test_28_unknown_readable_access_is_only_hypothetical(self):
  for s in self.s:
   self.assertFalse(s["externally_attested_authority"])
   self.assertEqual(set(s["lawful_reads"])-set(s["atoms"]),set())

if __name__=="__main__":
 unittest.main(verbosity=2)
