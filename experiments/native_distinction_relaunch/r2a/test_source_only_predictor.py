#!/usr/bin/env python3
"""R2A source-only kill tests: no kubectl, no cluster, no old native labels."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_only_predictor import derive,load

SOURCE_DIR=Path(__file__).resolve().parent/"source"


class R2AKillTests(unittest.TestCase):
    def setUp(self):
        self.data,self.hashes=load(SOURCE_DIR)

    def test_01_exact_current_same_future_split(self):
        r=derive(self.data,self.hashes)
        self.assertEqual(r["case_count"],8)
        self.assertTrue(r["current_decisions_equal"])
        self.assertTrue(r["after_same_mutation_decisions_differ"])
        self.assertEqual(r["native_scored_rows"],0)

    def test_02_strong_b9_allowed_to_tie(self):
        r=derive(self.data,self.hashes)
        self.assertTrue(r["strong_b9_with_full_source_information_correct"])
        self.assertTrue(r["no_novelty_advantage_over_B9_claimed"])

    def test_03_wrong_CEL_fails_closed(self):
        s=copy.deepcopy(self.data)
        s["policy"]["spec"]["validations"][0]["expression"]="true"
        with self.assertRaisesRegex(ValueError,"UNREGISTERED_POLICY_VALIDATION"):
            derive(s,self.hashes)

    def test_04_mutation_not_exact_successor_fails(self):
        s=copy.deepcopy(self.data)
        s["binding_mutation"]["patch_object"]["spec"]["matchResources"]["namespaceSelector"]["matchLabels"]["eeq.r2a/armed"]="standby"
        with self.assertRaisesRegex(ValueError,"FUTURE_BINDING_NOT_EXACT_MUTATION_RESULT"):
            derive(s,self.hashes)

    def test_05_source_qualification_cannot_be_silently_reassigned(self):
        s=copy.deepcopy(self.data)
        s["namespace_standby"]["metadata"]["labels"]["eeq.r2a/armed"]="gate"
        with self.assertRaisesRegex(ValueError,"WORLD_QUALIFICATION_SOURCES_NOT_DISTINCT"):
            derive(s,self.hashes)

    def test_06_nonregistered_selector_fails(self):
        s=copy.deepcopy(self.data)
        s["binding_initial"]["spec"]["matchResources"]["namespaceSelector"]["matchLabels"]["eeq.r2a/armed"]="gate"
        with self.assertRaisesRegex(ValueError,"SELECTOR_MUTATION_NOT_FROZEN"):
            derive(s,self.hashes)

    def test_07_missing_source_aborts(self):
        s=copy.deepcopy(self.data)
        s["namespace_probe"]["metadata"]["labels"].clear()
        with self.assertRaisesRegex(ValueError,"MISSING_INDEPENDENT_ACTIVATION_PROBE"):
            derive(s,self.hashes)

    def test_08_one_test_CEL_and_exact_two_challenges(self):
        r=derive(self.data,self.hashes)
        self.assertEqual(r["fixed_challenges"],["Pod CREATE flux","Pod CREATE default"])
        self.assertEqual(r["registered_horizon"],1)
        self.assertTrue(r["no_native_calls"])
        self.assertEqual(set(row["world"] for row in r["rows"]),
                         {"WORLD_GATE","WORLD_STANDBY"})

    def test_09_mutating_Deny_to_Audit_fails(self):
        s=copy.deepcopy(self.data)
        s["binding_initial"]["spec"]["validationActions"]=["Audit"]
        with self.assertRaisesRegex(ValueError,"POLICY_BINDING_MISMATCH"):
            derive(s,self.hashes)


if __name__=="__main__":
    unittest.main(verbosity=2)
