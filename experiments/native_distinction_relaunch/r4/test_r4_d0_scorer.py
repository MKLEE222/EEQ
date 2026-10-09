#!/usr/bin/env python3
"""Synthetic scorer adversarial tests. No real native client or TUF labels."""
import json
import sys
import unittest
from pathlib import Path
from r4_d0_join_only_scorer import STATES, ACTIONS, compare

PRED = MANIFEST = None


def fake_native():
    states={x["state"]:x for x in PRED["states"]}
    sources={x["name"]:x["sha256"] for x in MANIFEST["sources"]}
    expected={(x["state"],x["action"]):x for x in PRED["predictions"]}
    action_data={x["action"]:x for x in PRED["candidates"]}
    setups=[]
    rows=[]
    for s in STATES:
        f=states[s]["source_file"]
        setups.append({
            "state":s,"result":"PASS",
            "native_source_name":f,
            "setup_source_sha256":sources[f],
            "native_version":2,
            "native_metadata_identity":"ID:"+f,
        })
        for a in ACTIONS:
            e=expected[s,a]
            post=e["expected_post_source_file"]
            rows.append({
                "state":s,"action":a,
                "state_setup_source":f,
                "candidate_source":action_data[a]["source_file"],
                "state_source_sha256":sources[f],
                "candidate_source_sha256":
                    sources[action_data[a]["source_file"]],
                "native_outcome":e["native_expected"],
                "initial_native_source":f,
                "post_native_source":post,
                "initial_metadata_identity":"ID:"+f,
                "post_metadata_identity":"ID:"+post,
                "initial_native_version":2,
                "post_native_version":3 if e["native_expected"]=="ACCEPT" else 2,
                "setup_error":None,"candidate_error":None,
            })
    return {
        "schema":"eeq-r4-d0-tuf-native-auth-contrast-v1",
        "source_predictions_read":False,
        "registered_cells":8,
        "states":list(STATES),"actions":list(ACTIONS),
        "setup_controls":setups,"native_rows":rows,
        "original_g5_increment":0,
    }


class R4D0ComparatorTests(unittest.TestCase):
    def test_clean_mock_is_not_native_evidence(self):
        s=compare(PRED,MANIFEST,fake_native())["summary"]
        self.assertEqual(s["exact_native_cell_matches"],8)
        self.assertEqual(s["successful_native_setups"],2)
        self.assertEqual(s["best_version_candidate_only_oracle_decoder_matches"],6)
        self.assertTrue(s["same_candidate_opposite_result_A"])
        self.assertTrue(s["same_candidate_opposite_result_B"])

    def test_incorrect_native_outcome_retained(self):
        n=fake_native()
        n["native_rows"][0]["native_outcome"]="REJECT"
        s=compare(PRED,MANIFEST,n)["summary"]
        self.assertEqual(s["exact_native_cell_matches"],7)
        self.assertEqual(s["native_mismatches"],1)
        self.assertEqual(s["scientific_status"],"R4_D0_NATIVE_FAIL_OR_INCOMPLETE")

    def test_same_version_does_not_mask_bad_native_successor(self):
        n=fake_native()
        n["native_rows"][0]["post_native_source"]="root-3-b.json"
        s=compare(PRED,MANIFEST,n)["summary"]
        self.assertEqual(s["native_mismatches"],1)

    def test_bad_signature_envelope_identity_is_not_a_correct_post_state(self):
        n=fake_native()
        n["native_rows"][0]["post_metadata_identity"]=(
            n["native_rows"][0]["initial_metadata_identity"])
        s=compare(PRED,MANIFEST,n)["summary"]
        self.assertEqual(s["native_mismatches"],1)

    def test_missing_cell_aborts(self):
        n=fake_native()
        n["native_rows"].pop()
        with self.assertRaisesRegex(ValueError,"NATIVE_GRID_CASES_MISSING"):
            compare(PRED,MANIFEST,n)

    def test_duplicate_cell_aborts(self):
        n=fake_native()
        n["native_rows"].append(n["native_rows"][0].copy())
        with self.assertRaisesRegex(ValueError,"DUPLICATE_ROW"):
            compare(PRED,MANIFEST,n)

    def test_source_hash_drift_aborts(self):
        n=fake_native()
        n["native_rows"][0]["candidate_source_sha256"]="malicious"
        with self.assertRaisesRegex(ValueError,"NATIVE_SOURCE_FILE_HASH"):
            compare(PRED,MANIFEST,n)

    def test_unverified_common_anchor_setup_is_not_success(self):
        n=fake_native()
        n["setup_controls"][0]["result"]="FAIL"
        s=compare(PRED,MANIFEST,n)["summary"]
        self.assertEqual(s["successful_native_setups"],1)
        self.assertEqual(s["scientific_status"],"R4_D0_NATIVE_FAIL_OR_INCOMPLETE")

    def test_unknown_material_cannot_count_as_a_correct_native_refusal(self):
        n=fake_native()
        p=json.loads(json.dumps(PRED))
        p["predictions"][0]["native_expected"]="MODEL_UNSUPPORTED"
        s=compare(p,MANIFEST,n)["summary"]
        self.assertEqual(s["exact_native_cell_matches"],7)
        self.assertEqual(s["native_unknown_prediction"],1)

    def test_native_setup_failure_is_never_match(self):
        n=fake_native()
        n["native_rows"][0]["setup_error"]={"class":"InfrastructureFailure"}
        n["native_rows"][0]["native_outcome"]="SETUP_FAILURE"
        s=compare(PRED,MANIFEST,n)["summary"]
        self.assertEqual(s["native_setup_failures"],1)
        self.assertEqual(s["scientific_status"],"R4_D0_NATIVE_FAIL_OR_INCOMPLETE")


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: test_r4_d0_scorer.py PRED_JSON SOURCE_MANIFEST_JSON")
    PRED=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    MANIFEST=json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    unittest.main(argv=[sys.argv[0]],verbosity=2)
