#!/usr/bin/env python3
"""Pure source-only R2A kill tests, no cluster or native labels."""
import copy
import sys
import unittest

from r2a_source_predictor import (
    UnsupportedMechanism, build, predict, source_inputs,
)

SOURCE_DIR = None


class R2ASourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs, cls.manifest = source_inputs(SOURCE_DIR)

    def test_registered_exhaustive_eight_rows_and_full_two_phase_pair(self):
        m = predict(self.docs)
        self.assertEqual(len(m["registered_cases"]), 8)
        self.assertTrue(m["current_decisions_equal"])
        self.assertTrue(m["future_decisions_differ"])
        self.assertEqual(m["current_complete_decision_vectors"]["a"],
                         m["current_complete_decision_vectors"]["b"])
        self.assertEqual(m["post_action_decision_vectors"]["a"],
                         ("REJECT", "ACCEPT"))
        self.assertEqual(m["post_action_decision_vectors"]["b"],
                         ("ACCEPT", "ACCEPT"))

    def test_twin_histories_have_distinct_native_binding_selectors(self):
        m = predict(self.docs)
        self.assertNotEqual(m["binding_selectors"]["a"],
                            m["binding_selectors"]["b"])
        self.assertEqual(m["binding_selectors"]["a"],
                         {"r2a.team": "tenant"})
        self.assertEqual(m["binding_selectors"]["b"],
                         {"r2a.team": "tenant", "r2a.mode": "strict"})

    def test_action_changes_source_state_not_native_outcome(self):
        m = predict(self.docs)
        self.assertEqual(m["namespace_labels_before"]["r2a.mode"], "strict")
        self.assertEqual(
            m["namespace_labels_after_source_derived"]["r2a.mode"], "relaxed")
        self.assertEqual(m["registered_native_action"], [
            "kubectl", "label", "namespace", "eeq-r2a",
            "r2a.mode=relaxed", "--overwrite"])
        self.assertTrue(m["native_verifier_not_invoked"])

    def test_full_b9_ties_but_selector_blind_ablation_fails(self):
        m = predict(self.docs)
        self.assertEqual(m["strong_b9"]["predicted_native_matches"], 8)
        self.assertEqual(m["insufficient_selector_blind_ablation"][
            "matched_source_predictions"], 7)

    def test_weaker_binding_makes_preregistered_split_disappear_and_fails(self):
        docs = copy.deepcopy(self.docs)
        docs["binding-b.json"]["spec"]["matchResources"][
            "namespaceSelector"]["matchLabels"].pop("r2a.mode")
        with self.assertRaisesRegex(
            UnsupportedMechanism, "FROZEN_A_PREDICTION_NOT_INSTANTIATED"):
            predict(docs)

    def test_cel_grammar_extension_fails_closed(self):
        docs = copy.deepcopy(self.docs)
        docs["policy.json"]["spec"]["validations"][0]["expression"] = (
            "object.spec.serviceAccountName != 'flux' && true")
        with self.assertRaisesRegex(
            UnsupportedMechanism, "UNSUPPORTED_CEL_PREDICATE"):
            predict(docs)

    def test_binding_match_expressions_are_not_guessed(self):
        docs = copy.deepcopy(self.docs)
        docs["binding-a.json"]["spec"]["matchResources"][
            "namespaceSelector"]["matchExpressions"] = []
        with self.assertRaisesRegex(
            UnsupportedMechanism, "UNSUPPORTED_NAMESPACE_SELECTOR"):
            predict(docs)

    def test_unregistered_native_action_fails_closed(self):
        docs = copy.deepcopy(self.docs)
        docs["update-namespace-label.json"]["to"] = "unscoped"
        with self.assertRaisesRegex(
            UnsupportedMechanism, "UNSUPPORTED_NATIVE_NAMESPACE_TRANSITION"):
            predict(docs)

    def test_read_source_manifest_exactly_seven_files(self):
        m, p = build(SOURCE_DIR)
        self.assertEqual(len(m["sources"]), 7)
        self.assertEqual(len(set(x["sha256"] for x in m["sources"])), 7)
        self.assertEqual(p["g5_increment"], 0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: test_r2a_source_predictor.py SOURCE_DIR")
    SOURCE_DIR = sys.argv[1]
    unittest.main(argv=[sys.argv[0]], verbosity=2)
