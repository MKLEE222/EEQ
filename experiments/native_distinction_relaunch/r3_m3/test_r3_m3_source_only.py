#!/usr/bin/env python3
"""Falsification tests for source-only third-source inventory collision."""
import copy
import unittest
from r3_m3_source_only import (
    ALL, OLD, NEW, PHASES, PODS,
    UnsupportedMechanism, build, load, predict,
)


class M3SourceFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources,cls.docs=load(".")

    def test_exact_eight_source_files(self):
        manifest=build(".")[1]
        self.assertEqual(len(manifest["sources"]),8)
        self.assertEqual([x["name"] for x in manifest["sources"]],list(ALL))
        self.assertEqual(len({x["sha256"] for x in manifest["sources"]}),8)

    def test_original_six_inputs_unmodified_in_new_branch(self):
        self.assertEqual(len(OLD),6)
        self.assertEqual(len(NEW),2)
        self.assertTrue(all(x in self.sources for x in OLD))

    def test_fixed_four_phases_and_eight_fully_counted_decisions(self):
        p=predict(self.docs)
        self.assertEqual(
            [x["phase"] for x in p["registered_phases"]],list(PHASES))
        self.assertEqual(len(p["registered_native_cases"]),8)
        self.assertEqual(
            [x["source_expected_effect"] for x in p["registered_native_cases"]],
            ["REJECT","ACCEPT","REJECT","ACCEPT",
             "REJECT","REJECT","REJECT","ACCEPT"])

    def test_before_and_after_third_policy_unbound_identical(self):
        p=predict(self.docs)
        rows=p["registered_native_cases"]
        self.assertEqual([r["source_expected_effect"] for r in rows[:2]],
                         [r["source_expected_effect"] for r in rows[2:4]])

    def test_third_binding_toggles_only_default_and_preserves_flux_deny(self):
        rows=predict(self.docs)["registered_native_cases"]
        self.assertEqual(rows[3]["source_expected_effect"],"ACCEPT")
        self.assertEqual(rows[5]["source_expected_effect"],"REJECT")
        self.assertEqual(rows[7]["source_expected_effect"],"ACCEPT")
        self.assertTrue(all(rows[i]["source_expected_effect"]=="REJECT"
                            for i in (0,2,4,6)))

    def test_qualified_deny_witness_mentions_exact_source(self):
        p=predict(self.docs)
        row=p["registered_native_cases"][5]
        self.assertEqual(len(row["known_qualifying_deny_sources"]),1)
        self.assertEqual(row["known_qualifying_deny_sources"][0]["policy_name"],
                         "eeq-r3-m3-default-deny")
        self.assertEqual(row["known_qualifying_deny_sources"][0]["binding_name"],
                         "eeq-r3-m3-binding-third")

    def test_full_B9_same_source_knowledge_ties_all(self):
        p=predict(self.docs)
        self.assertEqual(p["strong_B9_full_inventory"][
            "expected_native_matches"],8)
        self.assertEqual(p["weak_cached_old_inventory"][
            "source_expected_matches"],7)
        self.assertTrue(p["weak_cached_old_inventory"]["not_strong_B9"])

    def test_unknown_third_CEL_fails_closed(self):
        d=copy.deepcopy(self.docs)
        d["policy-third.json"]["spec"]["validations"][0]["expression"]=(
            "object.metadata.labels['x'] == 'something'")
        with self.assertRaisesRegex(UnsupportedMechanism,
                                    "UNSUPPORTED_OR_UNREGISTERED_POLICY"):
            predict(d)

    def test_new_binding_unknown_matchExpressions_fails_closed(self):
        d=copy.deepcopy(self.docs)
        d["binding-third.json"]["spec"]["matchResources"][
            "namespaceSelector"]["matchExpressions"]=[]
        with self.assertRaisesRegex(UnsupportedMechanism,
                                    "UNSUPPORTED_BINDING_SELECTOR"):
            predict(d)

    def test_unregistered_extra_policy_field_fails_closed(self):
        d=copy.deepcopy(self.docs)
        d["policy-third.json"]["spec"]["auditAnnotations"]=[]
        with self.assertRaisesRegex(UnsupportedMechanism,
                                    "UNSUPPORTED_OR_UNREGISTERED_POLICY"):
            predict(d)

    def test_wrong_third_selector_not_rescued_by_changing_native_case_set(self):
        d=copy.deepcopy(self.docs)
        d["binding-third.json"]["spec"]["matchResources"][
            "namespaceSelector"]["matchLabels"]["r3.team"]="external"
        with self.assertRaisesRegex(UnsupportedMechanism,
                                    "FROZEN_BOUND_SOURCE_SELECTOR_CHANGED"):
            predict(d)

    def test_future_claim_scope_refuses_non_registered_namespace(self):
        d=copy.deepcopy(self.docs)
        d["namespace.json"]["metadata"]["labels"]["r3.mode"]="relaxed"
        with self.assertRaisesRegex(UnsupportedMechanism,
                                    "UNREGISTERED_NAMESPACE"):
            predict(d)

    def test_certification_never_imports_old_native_labels(self):
        p=predict(self.docs)
        self.assertTrue(p["source_only_no_native_labels"])
        self.assertEqual(p["new_native_calls"],0)
        self.assertEqual(p["original_v1_g5_increment"],0)
        self.assertEqual(p["controls"],{
            "unbound_pod_count":2,
            "membership_actions":3,
            "native_inventories":4})

    def test_third_binding_and_policy_source_differ_from_old(self):
        self.assertNotEqual(self.docs["policy.json"]["metadata"]["name"],
                            self.docs["policy-third.json"]["metadata"]["name"])
        self.assertNotEqual(self.docs["binding-team.json"]["spec"]["policyName"],
                            self.docs["binding-third.json"]["spec"]["policyName"])


if __name__=="__main__":
    unittest.main(verbosity=2)
