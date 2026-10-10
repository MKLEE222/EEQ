#!/usr/bin/env python3
"""F1 source-backed DEV audit; old R2A native results are test-only, never model features."""
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from p3b_dependency_reuse_guard import check as f0_guard
from p3b_f1_k8s_source_closure import (
    SOURCES, SCOPE, ModelUnsupported, SourceUnavailable, audit,
    changed_registered_reads, evaluate_from_sources, original_docs,
    parse_registered,
)

# FROZEN PRIOR R2A NATIVE DEVELOPMENT OUTCOMES, run 37906692298.
# These values are NOT imported or read by the F1 source-only implementation.
ARCHIVED_NATIVE={
    ("a","current","flux"):"REJECT",
    ("a","current","default"):"ACCEPT",
    ("b","current","flux"):"REJECT",
    ("b","current","default"):"ACCEPT",
    ("a","after_native_label_update","flux"):"REJECT",
    ("a","after_native_label_update","default"):"ACCEPT",
    ("b","after_native_label_update","flux"):"ACCEPT",
    ("b","after_native_label_update","default"):"ACCEPT",
}
FROZEN_PAIRS={
    ("a","flux"):"REUSE_DECISION_ONLY",
    ("a","default"):"REUSE_DECISION_ONLY",
    ("b","flux"):"REVERIFY_REQUIRED",
    ("b","default"):"REVERIFY_REQUIRED",
}


def fair_b9(docs):
    """Hand-engineered strong B9 with the same lawful data and a reasonable read-set."""
    selector, prior, updated, sas=parse_registered(docs)
    result={}
    decisions={}
    for branch in ("a","b"):
        required_fields=set(selector[branch].keys())
        changed=any(prior.get(k)!=updated.get(k) for k in required_fields)
        for probe in ("flux","default"):
            result[(branch,probe)]=(
                "REVERIFY_REQUIRED" if changed else "REUSE_DECISION_ONLY")
            for phase,ns in (("current",prior),
                             ("after_native_label_update",updated)):
                matches=all(ns.get(k)==value
                            for k,value in selector[branch].items())
                decisions[(branch,phase,probe)]=(
                    "REJECT" if matches and sas[probe]=="flux" else "ACCEPT")
    return result,decisions


def sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,
        separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


class F1SourceBackedPreregisteredTests(unittest.TestCase):
    def setUp(self):
        self.docs=original_docs()

    def test_01_original_git_blobs_verified(self):
        self.assertEqual(len(self.docs),7)
        self.assertTrue(all(x in self.docs for x in
            ("policy.json","binding-b.json","namespace-before.json")))

    def test_02_all_eight_source_only_decisions_match_archived_development(self):
        v=audit(self.docs)
        self.assertEqual(v["status"],"SOURCE_BACKED_READ_SET_DERIVED")
        self.assertTrue(v["source_only_no_native_labels_read"])
        self.assertEqual(v["native_calls_in_this_audit"],0)
        self.assertEqual(v["new_g5_cases"],0)
        self.assertFalse(v["p3_independent_advantage"])
        rows={(r["branch"],r["phase"],r["probe"]):r["source_only_expected"]
              for r in v["source_only_rows"]}
        self.assertEqual(len(rows),8)
        self.assertEqual(rows,ARCHIVED_NATIVE)

    def test_03_all_four_pair_verdicts_frozen(self):
        v=audit(self.docs)
        pair={(p["branch"],p["probe"]):p for p in v["pairs"]}
        self.assertEqual(len(pair),4)
        self.assertEqual({k:p["reuse_disposition"] for k,p in pair.items()},
                         FROZEN_PAIRS)
        self.assertIn("namespace.labels:r2a.mode",pair[("b","flux")]["read_set"])
        self.assertNotIn("namespace.labels:r2a.mode",pair[("a","flux")]["read_set"])
        self.assertTrue(all(p["requires_new_provenance_for_native_revision"]
                            and p["conditional_on_actual_registered_native_update"]
                            for p in pair.values()))
        # "REUSE" is deliberately never treated as native permission.
        self.assertFalse(any(p["reuse_disposition"] in ("ACCEPT","REJECT")
                             for p in pair.values()))

    def test_04_no_unsafe_reuse_and_one_conservative_extra_revalidation(self):
        pair={(p["branch"],p["probe"]):p["reuse_disposition"]
              for p in audit(self.docs)["pairs"]}
        unchanged=0
        needed=0
        unnecessary=0
        for (branch,probe),verdict in pair.items():
            native_same=(ARCHIVED_NATIVE[(branch,"current",probe)]==
                ARCHIVED_NATIVE[(branch,"after_native_label_update",probe)])
            if native_same:
                unchanged+=1
            if verdict=="REUSE_DECISION_ONLY":
                self.assertTrue(native_same)
            else:
                if native_same: unnecessary+=1
                else: needed+=1
        self.assertEqual((unchanged,needed,unnecessary),(3,1,1))

    def test_05_fully_informed_b9_ties_all_eight_and_all_four(self):
        pairs,decisions=fair_b9(self.docs)
        self.assertEqual(pairs,FROZEN_PAIRS)
        self.assertEqual(decisions,ARCHIVED_NATIVE)
        self.assertEqual(
            pairs,
            {(p["branch"],p["probe"]):p["reuse_disposition"]
             for p in audit(self.docs)["pairs"]})

    def test_06_bad_F0_completeness_callback_carries_false_reuse(self):
        """KILL: a caller claiming complete:true without namespace mode breaks F0 premise."""
        source={n:{"digest":sha(self.docs[n]),"status":"AVAILABLE"}
                for n in ("policy.json","binding-b.json","pod-flux.json")}
        base={"schema":"eeq-p3b-dependency-snapshot-f0","scope":{
            "contract":"R2A_K8S_REGISTERED_VAP_DYNAMIC_POD_CREATE",
            "claim":"flux_pod_admissible","actor":"registered_client",
            "action":"NAMESPACE_LABEL_UPDATE","horizon":1},
            "closure":{"sources":list(source),
                       "qualifications":["policy_and_binding_qualified"]},
            "sources":source,"qualifications":{
                "policy_and_binding_qualified":{"digest":"e"*64,
                                                 "status":"QUALIFIED"}}}
        # Same source/qualification projection across the label-changing native action:
        projected_after=copy.deepcopy(base)
        def dishonest_auditor(_):
            return {**base["closure"],"complete":True}
        self.assertEqual(f0_guard(base,projected_after,dishonest_auditor),
                         "REUSE_CANDIDATE_CONDITIONAL")
        self.assertNotEqual(
            ARCHIVED_NATIVE[("b","current","flux")],
            ARCHIVED_NATIVE[("b","after_native_label_update","flux")])
        candidate=next(p for p in audit(self.docs)["pairs"] if
                       p["branch"]=="b" and p["probe"]=="flux")
        self.assertEqual(candidate["reuse_disposition"],"REVERIFY_REQUIRED")

    def test_07_missing_source_is_unavailable_not_native_reject(self):
        for key in ("namespace-before.json","update-namespace-label.json"):
            d=copy.deepcopy(self.docs)
            del d[key]
            self.assertEqual(audit(d)["status"],"SOURCE_UNAVAILABLE")

    def test_08_match_expressions_fails_closed(self):
        d=copy.deepcopy(self.docs)
        selector=d["binding-b.json"]["spec"]["matchResources"]["namespaceSelector"]
        del selector["matchLabels"]
        selector["matchExpressions"]=[{"key":"r2a.mode","operator":"In",
                                      "values":["strict"]}]
        self.assertEqual(audit(d)["status"],"MODEL_UNSUPPORTED")

    def test_09_param_sources_not_silently_dropped(self):
        d=copy.deepcopy(self.docs)
        d["binding-a.json"]["spec"]["paramRef"]={"name":"test"}
        self.assertEqual(audit(d)["status"],"MODEL_UNSUPPORTED")
        d=copy.deepcopy(self.docs)
        d["policy.json"]["spec"]["paramKind"]={"apiVersion":"v1","kind":"ConfigMap"}
        self.assertEqual(audit(d)["status"],"MODEL_UNSUPPORTED")

    def test_10_cel_policy_enforcement_and_extra_validation_vetoes(self):
        for f in ("expression","failurePolicy","validationActions","matchConstraints"):
            d=copy.deepcopy(self.docs)
            if f=="expression":
                d["policy.json"]["spec"]["validations"][0]["expression"]=(
                    "object.spec.serviceAccountName == 'flux'")
            elif f=="failurePolicy":
                d["policy.json"]["spec"]["failurePolicy"]="Ignore"
            elif f=="validationActions":
                d["binding-a.json"]["spec"]["validationActions"]=["Audit"]
            else:
                d["policy.json"]["spec"]["matchConstraints"]={"resourceRules":[]}
            self.assertEqual(audit(d)["status"],"MODEL_UNSUPPORTED")
        d=copy.deepcopy(self.docs)
        d["policy.json"]["spec"]["validations"].append(
            copy.deepcopy(d["policy.json"]["spec"]["validations"][0]))
        self.assertEqual(audit(d)["status"],"MODEL_UNSUPPORTED")

    def test_11_unrelated_namespace_evidence_is_not_decision_dependency(self):
        d=copy.deepcopy(self.docs)
        d["namespace-before.json"]["metadata"]["labels"]["r2a.unrelated"]="x"
        d["namespace-before.json"]["metadata"]["annotations"]={"owner":"audit"}
        self.assertEqual(
            {(p["branch"],p["probe"]):p["reuse_disposition"]
             for p in audit(d)["pairs"]}, FROZEN_PAIRS)

    def test_12_synthetic_team_delta_affects_both_static_read_sets(self):
        selectors,before,after,_=parse_registered(self.docs)
        synthetic=before.copy()
        synthetic["r2a.team"]="other"
        changed=changed_registered_reads(selectors,before,synthetic)
        self.assertIn("r2a.team",changed["a"])
        self.assertIn("r2a.team",changed["b"])
        # This is NOT the frozen native update; it is only a structural read-set test.

    def test_13_added_selector_key_is_read_even_if_label_absent(self):
        d=copy.deepcopy(self.docs)
        sel=d["binding-b.json"]["spec"]["matchResources"]["namespaceSelector"]["matchLabels"]
        sel["r2a.region"]="west"
        r=audit(d)
        self.assertEqual(r["status"],"SOURCE_BACKED_READ_SET_DERIVED")
        pair=next(x for x in r["pairs"] if x["branch"]=="b" and x["probe"]=="flux")
        self.assertIn("namespace.labels:r2a.region",pair["read_set"])
        rows={(x["branch"],x["phase"],x["probe"]):x["source_only_expected"]
              for x in r["source_only_rows"]}
        self.assertEqual(rows[("b","current","flux")],"ACCEPT")

    def test_14_original_source_pin_tamper_cannot_be_reclassified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in self.docs:
                shutil.copyfile(SOURCES / name,root/name)
            path=root/"binding-b.json"
            path.write_bytes(path.read_bytes()+b" ")
            with self.assertRaisesRegex(ModelUnsupported,"ORIGINAL_SOURCE_PIN_CHANGED"):
                original_docs(root)

    def test_15_changed_contract_actor_action_horizon_are_unsupported(self):
        for field,val in (("contract","DIFFERENT"),("actor","DIFFERENT"),
                          ("action","OTHER_ACTION"),("horizon",3)):
            scope=copy.deepcopy(SCOPE)
            scope[field]=val
            self.assertEqual(audit(self.docs,scope=scope)["status"],
                             "MODEL_UNSUPPORTED")

    def test_16_missing_registered_label_is_observed_absence_not_missing_source(self):
        d=copy.deepcopy(self.docs)
        del d["namespace-before.json"]["metadata"]["labels"]["r2a.team"]
        self.assertEqual(audit(d)["status"],"SOURCE_BACKED_READ_SET_DERIVED")
        self.assertTrue(all(
            r["source_only_expected"]=="ACCEPT"
            for r in audit(d)["source_only_rows"]))


if __name__=="__main__":
    unittest.main(verbosity=2)
