#!/usr/bin/env python3
"""Synthetic anti-masking tests for the R2A scorer. NO kubectl or native calls."""
import copy
import json
import sys
import unittest
from pathlib import Path
from r2a_join_only_scorer import score

PRED = None
MANIFEST = None


def make_branch(branch):
    sources = {x["name"]: x["sha256"] for x in MANIFEST["sources"]}
    cells = [r for r in PRED["registered_cases"] if r["branch"] == branch]
    def probe(r):
        value=r["expected_native"]
        return {
            "probe":r["probe"],"phase":r["phase"],"native":value,
            "native_attribution":
                "REGISTERED_VAP_DENY" if value=="REJECT" else "ADMITTED",
            "pod_source_sha256":sources["pod-"+r["probe"]+".json"],
            "exit_code":1 if value=="REJECT" else 0,
        }
    before_labels={"r2a.team":"tenant","r2a.mode":"strict"}
    after_labels={"r2a.team":"tenant","r2a.mode":"relaxed"}
    return {
        "schema":"eeq-r2a-native-k8s-dynamic-branch-v1",
        "branch":branch,
        "native_cluster_context":"kind-eeq-r2a-"+branch,
        "native_predictions_file_read":False,
        "source_digest_map":sources,
        "source_binding_selector":PRED["binding_selectors"][branch],
        "native_observed_binding_selector":PRED["binding_selectors"][branch],
        "native_namespace_action_verified":True,
        "native_current_namespace":{
            "uid":"namespace-"+branch,
            "resource_version":"101","labels":before_labels},
        "native_post_action_namespace":{
            "uid":"namespace-"+branch,
            "resource_version":"102","labels":after_labels},
        "namespace_label_action_command":{
            "exit_code":0,"command":PRED["registered_native_action"]},
        "unbound_controls":[{
            "probe":p,"phase":"unbound","native":"ACCEPT",
            "native_attribution":"ADMITTED",
            "pod_source_sha256":sources["pod-"+p+".json"],
            "exit_code":0,
        } for p in ("flux","default")],
        "current_probes":[probe(r) for r in cells if r["phase"]=="current"],
        "future_probes":[probe(r) for r in cells if r["phase"]==
                         "after_native_label_update"],
    }


def twin():
    return {"a":make_branch("a"),"b":make_branch("b")}


class R2AScorerTests(unittest.TestCase):
    def test_clean_synthetic_oracle_scoring_not_real_native_evidence(self):
        s=score(PRED,MANIFEST,twin())["summary"]
        self.assertEqual(s["native_cases_match"],8)
        self.assertEqual(s["unbound_native_controls_match"],4)
        self.assertTrue(s["native_action_induced_a_witness_verified"])
        self.assertEqual(s["strong_b9_native_matches"],8)

    def test_future_native_disagreement_is_never_hidden(self):
        t=twin()
        t["b"]["future_probes"][0]["native"]="REJECT"
        t["b"]["future_probes"][0]["native_attribution"]="REGISTERED_VAP_DENY"
        s=score(PRED,MANIFEST,t)["summary"]
        self.assertEqual(s["native_cases_match"],7)
        self.assertFalse(s["native_action_induced_a_witness_verified"])

    def test_current_mismatch_kills_A(self):
        t=twin()
        t["b"]["current_probes"][0]["native"]="ACCEPT"
        t["b"]["current_probes"][0]["native_attribution"]="ADMITTED"
        s=score(PRED,MANIFEST,t)["summary"]
        self.assertFalse(s["native_present_decisions_identical"])
        self.assertFalse(s["native_action_induced_a_witness_verified"])

    def test_native_source_drift_aborts(self):
        t=twin()
        t["a"]["source_digest_map"]["binding-a.json"]="tamper"
        with self.assertRaisesRegex(ValueError,"NATIVE_SOURCE_HASH_MISMATCH"):
            score(PRED,MANIFEST,t)

    def test_native_action_without_real_resource_version_change_aborts(self):
        t=twin()
        t["a"]["native_post_action_namespace"]["resource_version"]="101"
        with self.assertRaisesRegex(ValueError,"NATIVE_NAMESPACE_REVISION"):
            score(PRED,MANIFEST,t)

    def test_native_missing_registered_probe_aborts(self):
        t=twin()
        t["a"]["current_probes"].pop()
        with self.assertRaisesRegex(ValueError,"MISSING_NATIVE_CASE"):
            score(PRED,MANIFEST,t)

    def test_unrelated_admission_denial_cannot_claim_target_rejection(self):
        t=twin()
        t["a"]["current_probes"][0]["native"]="REJECT"
        t["a"]["current_probes"][0]["native_attribution"]="UNRELATED_REJECTION"
        s=score(PRED,MANIFEST,t)["summary"]
        self.assertEqual(s["native_cases_match"],7)
        self.assertFalse(s["native_action_induced_a_witness_verified"])

    def test_native_unbound_controls_must_be_admissible(self):
        t=twin()
        t["a"]["unbound_controls"][0]["native"]="NATIVE_ORACLE_AMBIGUOUS"
        s=score(PRED,MANIFEST,t)["summary"]
        self.assertEqual(s["unbound_native_controls_match"],3)
        self.assertFalse(s["native_action_induced_a_witness_verified"])

    def test_two_native_branches_require_separate_clusters(self):
        t=twin()
        t["b"]["native_cluster_context"]=t["a"]["native_cluster_context"]
        with self.assertRaisesRegex(ValueError,"NON_INDEPENDENT_NATIVE_KIND"):
            score(PRED,MANIFEST,t)


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: test_r2a_join_only_scorer.py PRED_JSON MANIFEST_JSON")
    PRED=json.loads(Path(sys.argv[1]).read_text())
    MANIFEST=json.loads(Path(sys.argv[2]).read_text())
    unittest.main(argv=[sys.argv[0]],verbosity=2)
