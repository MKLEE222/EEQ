#!/usr/bin/env python3
"""R3-M1 source-only pre-native tests, no native oracle imported or executed."""
import copy
import json
import unittest
from pathlib import Path
from r3_m1_source_only import (NAMES, ORDERS, PHASES, PROBES, SourceUnavailable,
    Unsupported, build, prediction, source_inputs)

ROOT=Path(__file__).resolve().parent / "sources"
EXPECTED={
("TM","initial","flux"):"REJECT",("TM","initial","default"):"ACCEPT",
("TM","after_first","flux"):"REJECT",("TM","after_first","default"):"ACCEPT",
("TM","after_second","flux"):"ACCEPT",("TM","after_second","default"):"ACCEPT",
("MT","initial","flux"):"REJECT",("MT","initial","default"):"ACCEPT",
("MT","after_first","flux"):"REJECT",("MT","after_first","default"):"ACCEPT",
("MT","after_second","flux"):"ACCEPT",("MT","after_second","default"):"ACCEPT",
}
QUALIFIED={
("TM","initial"):["binding-team.json","binding-mode.json"],
("TM","after_first"):["binding-mode.json"],
("TM","after_second"):[],
("MT","initial"):["binding-team.json","binding-mode.json"],
("MT","after_first"):["binding-team.json"],
("MT","after_second"):[],
}
class R3M1PrenativeTests(unittest.TestCase):
    def setUp(self):
        self.docs,self.manifest=source_inputs(ROOT)

    def test_eight_exact_input_source_documents(self):
        self.assertEqual(set(self.docs),set(NAMES))
        self.assertEqual(len(self.manifest),8)
        self.assertTrue(all(len(r["sha256"])==64 and r["bytes"]>0
                            for r in self.manifest))

    def test_twelve_primary_source_only_predictions(self):
        p=prediction(self.docs)
        got={(r["order"],r["phase"],r["probe"]):r["expected_native"]
             for r in p["registered_cases"]}
        self.assertEqual(got,EXPECTED)
        self.assertFalse(p["native_labels_read"])
        self.assertFalse(p["native_verifier_called"])
        self.assertTrue(p["native_success_not_yet_observed"])
        self.assertEqual(p["native_primary_denominator"],12)
        self.assertEqual(p["native_control_denominator"],12)

    def test_distinct_support_sources_retain_both_binding_ids(self):
        p=prediction(self.docs)
        for r in p["registered_cases"]:
            self.assertEqual(r["qualified_binding_source_ids"],
                QUALIFIED[(r["order"],r["phase"])])

    def test_equal_information_b9_can_compute_every_answer(self):
        # Independent, deliberately simple full-information B9 decision rule
        # uses both matchLabels and the EXACT registered source action prefix.
        bindings={name:self.docs["binding-"+name+".json"]["spec"]["matchResources"][
            "namespaceSelector"]["matchLabels"] for name in ("team","mode")}
        for row in prediction(self.docs)["registered_cases"]:
            relevant=row["source_only_namespace_labels"]
            any_fail=False
            for b in ("team","mode"):
                if all(relevant.get(k)==v for k,v in bindings[b].items()):
                    if row["probe"]=="flux":
                        any_fail=True
            self.assertEqual("REJECT" if any_fail else "ACCEPT",
                             row["expected_native"])

    def test_one_binding_only_ablation_misses_remaining_support(self):
        p=prediction(self.docs)
        missed=0
        for r in p["registered_cases"]:
            if r["phase"]=="after_first" and r["probe"]=="flux":
                removed_binding=r["source_only_action_prefix"][0]
                if not any(name=="binding-"+removed_binding+".json"
                    for name in r["qualified_binding_source_ids"]):
                    missed+=1
        self.assertEqual(missed,2)
        # Deliberately weak ablation: not a legitimate strong B9 baseline.

    def test_source_unavailable_fails_without_native_deny(self):
        d=copy.deepcopy(self.docs)
        del d["binding-mode.json"]
        with self.assertRaises(SourceUnavailable):
            prediction(d)

    def test_param_ref_is_outside_registered_scope(self):
        d=copy.deepcopy(self.docs)
        d["binding-team.json"]["spec"]["paramRef"]={"name":"p"}
        with self.assertRaisesRegex(Unsupported,"UNSUPPORTED_BINDING"):
            prediction(d)

    def test_policy_modified_cel_and_extra_validation_refused(self):
        for kind in ("different_cel","extra_validation"):
            d=copy.deepcopy(self.docs)
            if kind=="different_cel":
                d["policy.json"]["spec"]["validations"][0]["expression"]="true"
            else:
                d["policy.json"]["spec"]["validations"].append(
                    copy.deepcopy(d["policy.json"]["spec"]["validations"][0]))
            with self.assertRaisesRegex(Unsupported,"UNSUPPORTED_POLICY"):
                prediction(d)

    def test_action_precondition_or_unregistered_action_refused(self):
        d=copy.deepcopy(self.docs)
        d["action-mode.json"]["from"]="other"
        with self.assertRaisesRegex(Unsupported,"UNREGISTERED_ACTION"):
            prediction(d)

    def test_production_holdout_and_v1_case_count_unchanged(self):
        m,p=build(ROOT)
        self.assertTrue(m["source_only_before_native"])
        self.assertEqual(m["original_v1_g5_increment"],0)
        self.assertEqual(p["original_v1_g5_increment"],0)
        self.assertTrue(p["strong_b9_given_same_inputs_able_to_tie"])

if __name__=="__main__":
    unittest.main(verbosity=2)
