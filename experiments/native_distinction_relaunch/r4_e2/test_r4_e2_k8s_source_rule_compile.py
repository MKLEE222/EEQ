#!/usr/bin/env python3
"""E2 K8s native-source rule AST diagnostics. No kubectl or native label read."""
import copy,unittest,hashlib,json
from r4_e2_k8s_source_rule_compile import (
    pinned_native_docs,compile_case,verify_inputs,PHASES,PINS,Unsupported,
    canonical_object_sha
)
from r4_e2_generic_rule_checker import check_program
from r4_e2_k8s_direct_b9_source_only import direct_b9

EXPECT={
 "K8S|S0_INITIAL|flux":True,"K8S|S0_INITIAL|default":False,
 "K8S|A1_POLICY_ADDED|flux":True,"K8S|A1_POLICY_ADDED|default":False,
 "K8S|A2_BINDING_ADDED|flux":True,"K8S|A2_BINDING_ADDED|default":True,
 "K8S|A3_BINDING_DELETED|flux":True,"K8S|A3_BINDING_DELETED|default":False,
}

def synthetic_requalify(d,key):
    """Explicit synthetic new-source bytes, NEVER an original pinned fixture."""
    canonical=json.dumps(d[key]["obj"],sort_keys=True,separators=(",",":")).encode()
    d[key]["sha256"]=hashlib.sha256(canonical).hexdigest()
    d[key]["canonical_object_sha256"]=canonical_object_sha(d[key]["obj"])


class E2SourceOnlyK8s(unittest.TestCase):
 def setUp(self):self.d=pinned_native_docs()
 def test_01_8_exact_original_native_file_blob_pins(self):
  self.assertEqual(len(self.d),len(PINS))
  self.assertEqual(len(verify_inputs(self.d)),2)
 def test_02_scoped_program_compiler_matches_registered_existing_source_effects(self):
  rows={}
  for phase,_,_ in PHASES:
   for probe in ("flux","default"):
    p=compile_case(self.d,phase,probe)
    rows[p["case_id"]]=check_program(p)
  self.assertEqual(set(rows),set(EXPECT))
  self.assertTrue(all(v["status"]=="QUALIFIED_BOUNDED_RULE_EVALUATED"
                      for v in rows.values()))
  self.assertEqual({k:v["scoped_effect_bit"] for k,v in rows.items()},EXPECT)
 def test_03_separate_handengineered_B9_source_only_reference_ties(self):
  self.assertEqual({r["case_id"]:r["direct_B9_source_only_effect"]
                    for r in direct_b9()},EXPECT)
 def test_04_unbound_third_policy_does_not_create_a_denial(self):
  before=check_program(compile_case(self.d,"S0_INITIAL","default"))
  only_policy=check_program(compile_case(self.d,"A1_POLICY_ADDED","default"))
  self.assertFalse(before["scoped_effect_bit"])
  self.assertFalse(only_policy["scoped_effect_bit"])
 def test_05_new_third_binding_changes_default_without_old_source_mutation(self):
  old=compile_case(self.d,"A1_POLICY_ADDED","default")
  new=compile_case(self.d,"A2_BINDING_ADDED","default")
  self.assertFalse(check_program(old)["scoped_effect_bit"])
  self.assertTrue(check_program(new)["scoped_effect_bit"])
  self.assertEqual(old["verified_source_sha256"]["team_binding"],
                   new["verified_source_sha256"]["team_binding"])
  self.assertEqual(old["verified_source_sha256"]["mode_binding"],
                   new["verified_source_sha256"]["mode_binding"])
 def test_06_binding_deletion_restores_scoped_no_registered_denial(self):
  p=compile_case(self.d,"A3_BINDING_DELETED","default")
  self.assertFalse(check_program(p)["scoped_effect_bit"])
  self.assertFalse(check_program(p)["global_k8s_admission_accept_authorized"])
 def test_07_missing_policy_source_does_not_default_accept(self):
  del self.d["third_policy"]
  with self.assertRaises(Unsupported):compile_case(self.d,"A2_BINDING_ADDED","default")
 def test_08_unregistered_extra_source_must_have_explicit_new_protocol(self):
  self.d["unregistered_fourth_binding"]=copy.deepcopy(self.d["third_binding"])
  with self.assertRaisesRegex(Unsupported,"INVENTORY_UNREGISTERED"):
   compile_case(self.d,"A2_BINDING_ADDED","default")
 def test_09_unregistered_CEL_operation_refused(self):
  p=self.d["flux_policy"]["obj"]["spec"]["validations"][0]
  p["expression"]="object.spec.serviceAccountName.startsWith('flux')"
  synthetic_requalify(self.d,"flux_policy")
  with self.assertRaisesRegex(Unsupported,"UNSUPPORTED_K8S_CEL"):
   compile_case(self.d,"S0_INITIAL","flux")
 def test_10_matchExpressions_not_silently_interpreted_as_no_match(self):
  sel=self.d["team_binding"]["obj"]["spec"]["matchResources"]["namespaceSelector"]
  sel["matchExpressions"]=[{"key":"r3.team","operator":"In","values":["tenant"]}]
  synthetic_requalify(self.d,"team_binding")
  with self.assertRaisesRegex(Unsupported,"UNSUPPORTED_BINDING"):
   compile_case(self.d,"S0_INITIAL","flux")
 def test_11_binding_paramRef_outside_contract(self):
  self.d["third_binding"]["obj"]["spec"]["paramRef"]={"name":"future"}
  synthetic_requalify(self.d,"third_binding")
  with self.assertRaisesRegex(Unsupported,"UNSUPPORTED_BINDING"):
   compile_case(self.d,"A2_BINDING_ADDED","default")
 def test_12_missing_source_identity_cannot_generate_unqualified_certificate(self):
  del self.d["namespace"]["obj"]["metadata"]["name"]
  synthetic_requalify(self.d,"namespace")
  with self.assertRaisesRegex(Unsupported,"NAMESPACE_SOURCE"):
   compile_case(self.d,"S0_INITIAL","flux")
 def test_13_changed_source_object_with_old_source_digest_refused(self):
  self.d["third_binding"]["obj"]["spec"]["policyName"]="other"
  with self.assertRaisesRegex(Unsupported,"SOURCE_RECORD_MALFORMED"):
   compile_case(self.d,"A2_BINDING_ADDED","default")
 def test_14_synthetically_changed_relevant_selector_changes_derived_rule(self):
  self.d["third_binding"]["obj"]["spec"]["matchResources"]["namespaceSelector"]["matchLabels"]["r3.team"]="external"
  synthetic_requalify(self.d,"third_binding")
  p=compile_case(self.d,"A2_BINDING_ADDED","default")
  self.assertFalse(check_program(p)["scoped_effect_bit"])
 def test_15_duplicate_policy_identity_killed(self):
  self.d["third_policy"]["obj"]["metadata"]["name"]="eeq-r3-flux-deny"
  synthetic_requalify(self.d,"third_policy")
  with self.assertRaisesRegex(Unsupported,"DUPLICATE_K8S_POLICY"):
   compile_case(self.d,"A2_BINDING_ADDED","default")
 def test_16_wrong_binding_validation_action_killed(self):
  self.d["third_binding"]["obj"]["spec"]["validationActions"]=["Warn"]
  synthetic_requalify(self.d,"third_binding")
  with self.assertRaisesRegex(Unsupported,"UNSUPPORTED_BINDING"):
   compile_case(self.d,"A2_BINDING_ADDED","default")
 def test_17_scoped_denial_does_not_imply_global_admission_knowledge(self):
  for phase,_,_ in PHASES:
   for probe in ("flux","default"):
    p=compile_case(self.d,phase,probe)
    self.assertFalse(p["source_closure_is_author_independently_attested"])
    self.assertTrue(p["author_registered_phase_membership_not_live_native_list"])
    self.assertFalse(check_program(p)["global_k8s_admission_accept_authorized"])
 def test_18_every_rule_leaf_has_stable_source_sha_for_all_dependencies(self):
  for phase,_,_ in PHASES:
   for probe in ("flux","default"):
    p=compile_case(self.d,phase,probe)
    self.assertEqual(check_program(p)["status"],"QUALIFIED_BOUNDED_RULE_EVALUATED")

if __name__=="__main__":unittest.main(verbosity=2)
