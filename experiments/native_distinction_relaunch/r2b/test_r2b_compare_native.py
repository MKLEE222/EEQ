#!/usr/bin/env python3
"""Synthetic join-only kill tests; no real/native verifier invoked here."""
import copy
import itertools
import unittest
from r2b_compare_native import compare

ACTS = ("submit-candidate-2", "submit-candidate-3")
FILES = ("A", "B", "C2", "C3", "TARGETS_A", "TARGETS_B")
RAW = {s: "raw_"+s for s in FILES}
CAN = {s: "signed_"+s for s in FILES}


def go(state, action):
    if state in ("A", "B") and action == ACTS[0]:
        return "ACCEPT", "C2"
    if state == "C2" and action == ACTS[1]:
        return "ACCEPT", "C3"
    return "REJECT", state


def all_paths():
    return [(), *((x,) for x in ACTS),
            *((x, y) for x in ACTS for y in ACTS)]


def fake():
    manifest = {
        "schema": "eeq-r2b-controlled-sources-v1",
        "files": [{"sha256": RAW[x], "signed_canonical_sha256": CAN[x]}
                  for x in FILES]
    }
    prediction = {
        "schema": "eeq-r2b-source-only-predictions-v1",
        "registered_actions": list(ACTS), "horizon": 2,
        "targets_role_qualification": {
            "A": {"TARGETS_A": {"qualified": True},
                  "TARGETS_B": {"qualified": False}},
            "B": {"TARGETS_A": {"qualified": False},
                  "TARGETS_B": {"qualified": True}}
        }, "rows": []
    }
    native = {
        "schema": "eeq-r2b-independent-native-tuf-v1",
        "fixed_actions": list(ACTS), "fixed_horizon": 2,
        "source_only_predictions_never_read": True,
        "rows": [], "target_authorizations": []
    }
    for initial in ("A", "B"):
        for prefix in all_paths():
            state = initial
            prefix_expected = []
            prefix_actual = []
            for action in prefix:
                outcome, nextstate = go(state, action)
                prefix_expected.append({
                    "action": action,
                    "effect": "ADVANCE_TRUST_ROOT" if outcome == "ACCEPT"
                              else "KEEP_TRUST_ROOT"})
                prefix_actual.append({
                    "action": action, "native_outcome": outcome
                })
                state = nextstate
            expected_cont = []
            actual_cont = []
            for action in ACTS:
                outcome, nextstate = go(state, action)
                expected_cont.append({
                    "action": action,
                    "effect": "ADVANCE_TRUST_ROOT" if outcome == "ACCEPT"
                              else "KEEP_TRUST_ROOT",
                    "to_source_sha256": RAW[nextstate]
                })
                actual_cont.append({
                    "action": action, "replay_setup_ok": True,
                    "native_decision": {
                        "native_outcome": outcome,
                        "after": {"canonical_signed_sha256": CAN[nextstate]},
                        "decision_ns": 100
                    }
                })
            prediction["rows"].append({
                "initial_state": initial, "prefix": list(prefix),
                "prefix_effects": prefix_expected,
                "state_after_prefix_source_sha256": RAW[state],
                "continuation": expected_cont
            })
            native["rows"].append({
                "initial_state": initial, "prefix": list(prefix),
                "prefix_trace": prefix_actual,
                "post_prefix_state": {"canonical_signed_sha256": CAN[state]},
                "setup_error": None, "prefix_completed": True,
                "challenges": actual_cont
            })
        for doc in ("TARGETS_A", "TARGETS_B"):
            native["target_authorizations"].append({
                "initial_state": initial,
                "target_document": doc,
                "native_role_authority_status":
                    "QUALIFIED" if (initial, doc) in
                    (("A", "TARGETS_A"), ("B", "TARGETS_B")) else "UNQUALIFIED"
            })
    return prediction, native, manifest


class FrozenScorerTests(unittest.TestCase):
    def test_01_perfect_synthetic_trace(self):
        p, n, m = fake()
        result = compare(p, n, m)
        self.assertEqual(result["summary"]["native_root_update_matches"], 28)
        self.assertEqual(result["summary"]["native_targets_role_matches"], 4)
        self.assertEqual(result["status"],
                         "CONTROLLED_NATIVE_B_CONFIRMED_B9_TIE")
        self.assertFalse(result["summary"]["novelty_advantage_established"])

    def test_02_wrong_outcome_is_retained(self):
        p, n, m = fake()
        n["rows"][0]["challenges"][0]["native_decision"]["native_outcome"] = "REJECT"
        result = compare(p, n, m)
        self.assertEqual(result["summary"]["native_root_update_nonmatches"], 1)
        self.assertNotEqual(result["status"],
                            "CONTROLLED_NATIVE_B_CONFIRMED_B9_TIE")

    def test_03_wrong_next_state_is_retained(self):
        p, n, m = fake()
        n["rows"][0]["challenges"][0]["native_decision"]["after"]["canonical_signed_sha256"] = "WRONG"
        result = compare(p, n, m)
        self.assertEqual(result["summary"]["native_root_update_nonmatches"], 1)

    def test_04_setup_failure_is_not_credited(self):
        p, n, m = fake()
        n["rows"][0]["prefix_completed"] = False
        result = compare(p, n, m)
        self.assertGreater(result["summary"]["unresolved_prefix_cells"], 0)
        self.assertNotEqual(result["status"],
                            "CONTROLLED_NATIVE_B_CONFIRMED_B9_TIE")

    def test_05_target_authority_failure_is_not_hidden(self):
        p, n, m = fake()
        n["target_authorizations"][0]["native_role_authority_status"] = "UNQUALIFIED"
        result = compare(p, n, m)
        self.assertEqual(result["summary"]["native_targets_role_nonmatches"], 1)

    def test_06_case_dropped_is_fatal(self):
        p, n, m = fake()
        n["rows"].pop()
        with self.assertRaisesRegex(ValueError, "UNREGISTERED_OR_MISSING_PREFIX"):
            compare(p, n, m)

    def test_07_extra_case_is_fatal(self):
        p, n, m = fake()
        n["rows"].append(copy.deepcopy(n["rows"][0]))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_PREFIX_ROW"):
            compare(p, n, m)

    def test_08_incorrect_native_horizon_is_fatal(self):
        p, n, m = fake()
        n["fixed_horizon"] = 1
        with self.assertRaisesRegex(ValueError, "FROZEN_HORIZON_CHANGED"):
            compare(p, n, m)

    def test_09_source_manifest_sha_drift_fails(self):
        p, n, m = fake()
        m["files"][0]["sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "UNPINNED_POST_PREFIX_SOURCE"):
            compare(p, n, m)

    def test_10_B9_tie_must_remain_visible(self):
        p, n, m = fake()
        result = compare(p, n, m)
        self.assertTrue(result["summary"]["strong_b9_tie_predeclared"])
        self.assertTrue(result["summary"]["classical_quotient_tie_predeclared"])
        self.assertFalse(result["summary"]["R2_FULL_GATE_PASS"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
