#!/usr/bin/env python3
"""V2B strict post-native normalization adversarial tests (NO native API)."""
import copy
import unittest
from r3_m3_v2b_default_only_copy import normalize_spec
from r3_m3_source_only import load

DOCS=load(".")[1]
P=DOCS["policy.json"]["spec"]
B=DOCS["binding-team.json"]["spec"]


def defaults_policy():
    native=copy.deepcopy(P)
    match=native["matchConstraints"]
    match["matchPolicy"]="Equivalent"
    match["namespaceSelector"]={}
    match["objectSelector"]={}
    for row in match["resourceRules"]:row["scope"]="*"
    return native


def defaults_binding():
    native=copy.deepcopy(B)
    match=native["matchResources"]
    match["matchPolicy"]="Equivalent"
    match["objectSelector"]={}
    return native


class OnlyDocumentedDefaultsTests(unittest.TestCase):
    def test_policy_exact_normalization_reversible(self):
        edited,removed=normalize_spec(P,defaults_policy(),"policy")
        self.assertEqual(edited,P)
        self.assertEqual(set(removed),{
            "matchConstraints.matchPolicy",
            "matchConstraints.namespaceSelector",
            "matchConstraints.objectSelector",
            "matchConstraints.resourceRules[0].scope"
        })

    def test_binding_exact_normalization_reversible(self):
        edited,removed=normalize_spec(B,defaults_binding(),"binding")
        self.assertEqual(edited,B)
        self.assertEqual(set(removed),{
            "matchResources.matchPolicy",
            "matchResources.objectSelector",
        })

    def test_original_unchanged_spec_has_no_changes(self):
        edited,removed=normalize_spec(P,P,"policy")
        self.assertEqual(edited,P)
        self.assertEqual(removed,[])

    def test_native_explicit_exact_mode_is_not_an_equivalent_default(self):
        v=defaults_policy()
        v["matchConstraints"]["matchPolicy"]="Exact"
        with self.assertRaisesRegex(ValueError,"UNRECOGNIZED_OR_MATERIAL_SERVER_DEFAULT"):
            normalize_spec(P,v,"policy")

    def test_nonempty_native_namespace_selector_is_material(self):
        v=defaults_policy()
        v["matchConstraints"]["namespaceSelector"]={
            "matchLabels":{"r3.team":"external"}}
        with self.assertRaisesRegex(ValueError,"UNRECOGNIZED_OR_MATERIAL_SERVER_DEFAULT"):
            normalize_spec(P,v,"policy")

    def test_native_object_selector_nonempty_cannot_be_erased(self):
        v=defaults_binding()
        v["matchResources"]["objectSelector"]={"matchLabels":{"allow":"true"}}
        with self.assertRaisesRegex(ValueError,"UNRECOGNIZED_OR_MATERIAL_SERVER_DEFAULT"):
            normalize_spec(B,v,"binding")

    def test_native_rule_scope_cluster_only_is_material(self):
        v=defaults_policy()
        v["matchConstraints"]["resourceRules"][0]["scope"]="Cluster"
        with self.assertRaisesRegex(ValueError,"UNKNOWN_POLICY_SCOPE_DEFAULT"):
            normalize_spec(P,v,"policy")

    def test_changed_native_policy_cel_is_material(self):
        v=defaults_policy()
        v["validations"][0]["expression"]="true"
        with self.assertRaisesRegex(ValueError,"SOURCE_VS_NATIVE_MATERIAL_SPEC_DRIFT"):
            normalize_spec(P,v,"policy")

    def test_native_added_param_kind_is_material(self):
        v=defaults_policy()
        v["paramKind"]={"apiVersion":"v1","kind":"ConfigMap"}
        with self.assertRaisesRegex(ValueError,"SOURCE_VS_NATIVE_MATERIAL_SPEC_DRIFT"):
            normalize_spec(P,v,"policy")

    def test_native_binding_policy_name_is_material(self):
        v=defaults_binding()
        v["policyName"]="some-other-policy"
        with self.assertRaisesRegex(ValueError,"SOURCE_VS_NATIVE_MATERIAL_SPEC_DRIFT"):
            normalize_spec(B,v,"binding")

    def test_native_binding_selector_is_material(self):
        v=defaults_binding()
        v["matchResources"]["namespaceSelector"]["matchLabels"]["r3.team"]="other"
        with self.assertRaisesRegex(ValueError,"SOURCE_VS_NATIVE_MATERIAL_SPEC_DRIFT"):
            normalize_spec(B,v,"binding")

    def test_native_duplicate_resource_rule_is_material(self):
        v=defaults_policy()
        v["matchConstraints"]["resourceRules"].append(
            copy.deepcopy(v["matchConstraints"]["resourceRules"][0]))
        with self.assertRaisesRegex(ValueError,"NATIVE_POLICY_RULE_SCOPE_OR_LENGTH_DRIFT"):
            normalize_spec(P,v,"policy")


if __name__=="__main__":
    unittest.main(verbosity=2)
