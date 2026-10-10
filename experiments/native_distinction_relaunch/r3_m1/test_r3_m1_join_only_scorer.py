#!/usr/bin/env python3
"""BEFORE-NATIVE synthetic anti-masking tests; generated native rows are FAKE, never evidence."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from r3_m1_source_only import build
from r3_m1_join_only_scorer import score

ROOT=Path(__file__).resolve().parent/"sources"
M,P=build(ROOT)
MRAW=(json.dumps(M,sort_keys=True,indent=2)+"\n").encode()
MHASH=hashlib.sha256(MRAW).hexdigest()
BINDINGS=[["eeq-r3-binding-mode",{"r3.mode":"strict"}],
          ["eeq-r3-binding-team",{"r3.team":"tenant"}]]

def native(order):
    rows=[r for r in P["registered_cases"] if r["order"]==order]
    controls=[]
    for name,grp in (("UNBOUND","unbound"),("ONLY_TEAM","only_team"),
                     ("ONLY_MODE","only_mode")):
        for p in ("flux","default"):
            controls.append({"control":name,"probe":p,
                             "native":P["per_cluster_frozen_controls"][grp][p]})
    phases=("initial","after_first","after_second")
    obs=[]
    for r in rows:
        i=phases.index(r["phase"])
        obs.append({"phase":r["phase"],"probe":r["probe"],
                    "native":r["expected_native"],"native_binding_inventory":copy.deepcopy(BINDINGS),
                    "namespace":{"uid":"native-"+order,"resource_version":str(100+i),
                                 "labels":r["source_only_namespace_labels"]}})
    acts=[]
    prefix=("team","mode") if order=="TM" else ("mode","team")
    for i,key in enumerate(prefix):
        before=next(r for r in rows if r["phase"]==phases[i])["source_only_namespace_labels"]
        after=next(r for r in rows if r["phase"]==phases[i+1])["source_only_namespace_labels"]
        acts.append({
            "action":key,"command":{"exit_code":0},
            "before":{"uid":"native-"+order,"resource_version":str(100+i),"labels":before},
            "after":{"uid":"native-"+order,"resource_version":str(101+i),"labels":after},
            "native_registered_action_verified":True,
        })
    return {"schema":"eeq-r3-m1-native-two-binding-one-order-v1",
            "order":order,"context":"kind-eeq-r3-"+order,
            "source_manifest_sha256":MHASH,"prediction_json_read":False,
            "error":None,"registered_primary_rows":6,"observed_primary_rows":6,
            "registered_control_rows":6,"observed_control_rows":6,
            "registered_action_count":2,"observed_action_count":2,
            "observed_registered_bindings":copy.deepcopy(BINDINGS),
            "controls":controls,"observations":obs,"native_actions":acts}

class SyntheticScorerKillTests(unittest.TestCase):
    def setUp(self):
        self.tm=native("TM")
        self.mt=native("MT")
    def run_score(self):
        return score(M,P,self.tm,self.mt,MRAW)
    def test_nominal_synthetic_12_12_is_not_native_proof(self):
        v=self.run_score()
        self.assertEqual(v["exact_source_to_native_matches"],12)
        self.assertEqual(v["native_isolation_controls_passed"],12)
        self.assertEqual(v["native_namespace_actions_verified"],4)
        self.assertFalse(v["p3_independent_value_established"])
        self.assertEqual(v["new_original_v1_g5_cases"],0)
    def test_one_wrong_native_row_retains_mismatch_in_full_denominator(self):
        self.tm["observations"][0]["native"]="ACCEPT"
        v=self.run_score()
        self.assertEqual(v["registered_primary"],12)
        self.assertEqual(v["mismatches"],1)
        self.assertEqual(v["scientific_status"],"R3_M1_NATIVE_MODEL_MISMATCH_RETAINED")
    def test_missing_primary_row_not_converted_to_success(self):
        self.tm["observations"].pop()
        with self.assertRaisesRegex(ValueError,"NATIVE_RUN_FAILURE_OR_COUNT|NATIVE_MAIN"):
            self.run_score()
    def test_ambiguous_native_outcome_never_counts(self):
        self.mt["observations"][2]["native"]="NATIVE_ORACLE_AMBIGUOUS"
        with self.assertRaisesRegex(ValueError,"NATIVE_ORACLE_AMBIGUOUS"):
            self.run_score()
    def test_unbound_control_dropped_never_counts(self):
        self.tm["controls"].pop()
        with self.assertRaisesRegex(ValueError,"NATIVE_RUN_FAILURE_OR_COUNT|NATIVE_CONTROL"):
            self.run_score()
    def test_renamed_or_duplicate_control_veto(self):
        self.tm["controls"][0]["control"]="OTHER"
        with self.assertRaisesRegex(ValueError,"UNREGISTERED_NATIVE_CONTROL"):
            self.run_score()
    def test_control_wrong_result_veto(self):
        self.tm["controls"][0]["native"]="REJECT"
        with self.assertRaisesRegex(ValueError,"NATIVE_CONTROL_MISMATCH"):
            self.run_score()
    def test_both_binding_inventory_source_mismatch_veto(self):
        self.mt["observed_registered_bindings"].pop()
        with self.assertRaisesRegex(ValueError,"NATIVE_BOTH_BINDINGS_NOT_INSTALLED"):
            self.run_score()
    def test_action_without_real_revision_change_veto(self):
        self.tm["native_actions"][1]["after"]["resource_version"]=(
            self.tm["native_actions"][1]["before"]["resource_version"])
        with self.assertRaisesRegex(ValueError,"NATIVE_ACTION_NOT_VERIFIED"):
            self.run_score()
    def test_native_prediction_read_flag_veto(self):
        self.tm["prediction_json_read"]=True
        with self.assertRaisesRegex(ValueError,"NATIVE_RUN_FAILURE_OR_COUNT"):
            self.run_score()
    def test_native_source_hash_mismatch_veto(self):
        self.tm["source_manifest_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"NATIVE_SOURCE_MANIFEST_HASH_MISMATCH"):
            self.run_score()
    def test_separate_clusters_mandatory(self):
        self.mt["context"]=self.tm["context"]
        with self.assertRaisesRegex(ValueError,"INDEPENDENT_CONTEXTS"):
            self.run_score()
    def test_future_namespace_label_is_not_fabricated(self):
        self.tm["observations"][-1]["namespace"]["labels"]["r3.mode"]="strict"
        with self.assertRaisesRegex(ValueError,"NATIVE_NAMESPACE_DIFFERS"):
            self.run_score()
    def test_source_binding_qualification_pair_is_checked(self):
        self.tm["observations"][0]["native_binding_inventory"][0][1]["r3.mode"]="relaxed"
        with self.assertRaisesRegex(ValueError,"NATIVE_REGISTERED_BINDING_INVENTORY_CHANGED"):
            self.run_score()
    def test_native_infrastructure_failure_retained(self):
        self.mt["error"]="KUBECTL_FAILED"
        with self.assertRaisesRegex(ValueError,"NATIVE_RUN_FAILURE_OR_COUNT"):
            self.run_score()

if __name__=="__main__":
    unittest.main(verbosity=2)
