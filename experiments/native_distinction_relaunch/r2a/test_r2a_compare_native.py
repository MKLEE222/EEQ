#!/usr/bin/env python3
"""Pre-native synthetic scorer anti-masking tests for R2A only."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from r2a_compare_native import compare


def fake():
    worlds=("WORLD_GATE","WORLD_STANDBY")
    phases=("CURRENT","AFTER_BINDING_MUTATION")
    sas=("flux","default")
    hashes={"policy":"shaP","binding_initial":"shaB0",
            "binding_after":"shaB1","namespace_gate":"shaNG",
            "namespace_standby":"shaNS","namespace_probe":"shaNP",
            "binding_mutation":"shaM","challenges":"shaC"}
    pred={
        "schema":"eeq-r2a-source-only-v1",
        "case_count":8,
        "registered_horizon":1,
        "registered_worlds":list(worlds),
        "source_sha256":hashes,
        "rows":[]
    }
    episodes={}
    for world in worlds:
        e={
          "schema":"eeq-r2a-k8s-native-episode-v1",
          "world":world,
          "source_only_prediction_file_never_read":True,
          "source_sha256":hashes.copy(),
          "status":"NATIVE_EPISODE_COMPLETED",
          "before_native_source":{
            "binding_selector":{"eeq.r2a/armed":"never"},
            "binding_resourceVersion":"100",
          },
          "after_native_source":{
            "binding_selector":{"eeq.r2a/armed":"gate"},
            "binding_resourceVersion":"101",
          },
          "activation_proven":True,
          "activation_probe_attempts":[{"attempt":1,"native_outcome":"REJECT"}],
          "observations":[]
        }
        for phase in phases:
            for sa in sas:
                expected=("REJECT" if world=="WORLD_GATE" and
                          phase=="AFTER_BINDING_MUTATION" and sa=="flux"
                          else "ACCEPT")
                pred["rows"].append({
                  "world":world,"phase":phase,
                  "service_account":sa,"expected_native":expected
                })
                e["observations"].append({
                  "world":world,"phase":phase,
                  "service_account":sa,
                  "native_outcome":expected,
                  "native_attribution":"REGISTERED_VAP" if expected=="REJECT"
                                       else "NATIVE_ADMITTED",
                  "native_stdout":"","native_stderr":""
                })
        episodes[world]=e
    return pred,episodes


class NativeComparatorKillTests(unittest.TestCase):
    def test_01_exact_8_native_trace(self):
        pred,episodes=fake()
        p=compare(pred,episodes)
        self.assertEqual(p["status"],"CONTROLLED_NATIVE_A_CONFIRMED_B9_TIE")
        self.assertEqual(p["summary"]["native_admission_matches"],8)
        self.assertTrue(p["summary"]["future_decision_vectors_diverge_after_same_native_patch"])
        self.assertFalse(p["summary"]["independent_novelty_advantage"])

    def test_02_one_wrong_native_decision_survives(self):
        pred,episodes=fake()
        episodes["WORLD_GATE"]["observations"][2]["native_outcome"]="ACCEPT"
        o=compare(pred,episodes)
        self.assertEqual(o["summary"]["native_admission_mismatches_or_unavailable"],1)
        self.assertNotEqual(o["status"],"CONTROLLED_NATIVE_A_CONFIRMED_B9_TIE")

    def test_03_wrong_denial_attribution_not_a_match(self):
        pred,episodes=fake()
        episodes["WORLD_GATE"]["observations"][2]["native_attribution"]="OTHER_NATIVE_ERROR"
        o=compare(pred,episodes)
        self.assertEqual(o["summary"]["native_admission_matches"],7)

    def test_04_source_binding_patch_missing_is_not_credited(self):
        pred,episodes=fake()
        episodes["WORLD_STANDBY"]["after_native_source"]["binding_selector"]={
            "eeq.r2a/armed":"never"}
        o=compare(pred,episodes)
        self.assertEqual(o["summary"]["verified_policy_transitions"],1)
        self.assertNotEqual(o["status"],"CONTROLLED_NATIVE_A_CONFIRMED_B9_TIE")

    def test_05_activation_probe_not_confirmed_is_not_credited(self):
        pred,episodes=fake()
        episodes["WORLD_GATE"]["activation_proven"]=False
        o=compare(pred,episodes)
        self.assertEqual(o["summary"]["verified_policy_transitions"],1)

    def test_06_native_source_hash_drift_is_fatal(self):
        pred,episodes=fake()
        episodes["WORLD_STANDBY"]["source_sha256"]["binding_after"]="WRONG"
        with self.assertRaisesRegex(ValueError,"NATIVE_SOURCE_SHA_MISMATCH"):
            compare(pred,episodes)

    def test_07_native_missing_one_case_retained(self):
        pred,episodes=fake()
        episodes["WORLD_GATE"]["observations"].pop()
        o=compare(pred,episodes)
        self.assertEqual(o["summary"]["native_admission_mismatches_or_unavailable"],1)
        self.assertNotEqual(o["status"],"CONTROLLED_NATIVE_A_CONFIRMED_B9_TIE")

    def test_08_extra_native_case_rejected(self):
        pred,episodes=fake()
        episodes["WORLD_GATE"]["observations"].append(
            copy.deepcopy(episodes["WORLD_GATE"]["observations"][0]))
        with self.assertRaisesRegex(ValueError,"DUPLICATE_NATIVE_ADMISSION"):
            compare(pred,episodes)

    def test_09_strong_B9_tie_remains_explicit(self):
        pred,episodes=fake()
        o=compare(pred,episodes)
        self.assertTrue(o["summary"]["strong_b9_tie_predeclared"])
        self.assertFalse(o["summary"]["full_R2_gate_pass"])


if __name__=="__main__":
    unittest.main(verbosity=2)
