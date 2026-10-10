#!/usr/bin/env python3
"""Synthetic R3-M3 scorer anti-masking tests; never calls Kubernetes."""
import copy
import json
import unittest
from r3_m3_source_only import build, load
from r3_m3_join_only_scorer import (
    PHASES,PROBES,OLD,OLD_POLICY,THIRD,THIRD_POLICY,score,
)

SOURCES,MANIFEST,PRED=build(".")
DOCS=load(".")[1]
HASHES={x["name"]:x["sha256"] for x in MANIFEST["sources"]}


def mock_native():
    policy_source={
        OLD_POLICY:DOCS["policy.json"],
        THIRD_POLICY:DOCS["policy-third.json"],
    }
    binding_source={
        "eeq-r3-binding-mode":DOCS["binding-mode.json"],
        "eeq-r3-binding-team":DOCS["binding-team.json"],
        THIRD:DOCS["binding-third.json"],
    }
    phases=[]
    for i,p in enumerate(PHASES):
        policies=[OLD_POLICY]+([THIRD_POLICY] if i>0 else [])
        bindings=list(OLD)+([THIRD] if i==2 else [])
        snapshot={
            "policy_list_resource_version":("100" if i==0 else "110"),
            "binding_list_resource_version":("200","200","220","240")[i],
            "policy_items":[{"name":x,"uid":"POLICY_UID_"+x,
                             "spec_sha256":"s_"+x,
                             "resource_version":"8",
                             "spec":copy.deepcopy(policy_source[x]["spec"])} for x in policies],
            "binding_items":[{"name":x,"uid":"BINDING_UID_"+x,
                              "spec_sha256":"s_"+x,
                              "resource_version":"9",
                              "spec":copy.deepcopy(binding_source[x]["spec"])} for x in bindings],
        }
        phases.append({"phase":p,"native_inventory":snapshot})
    expected={(row["phase"],row["probe"]):row
              for row in PRED["registered_native_cases"]}
    rows=[]
    for phase in PHASES:
        for probe in PROBES:
            value=expected[phase,probe]["source_expected_effect"]
            attributed=("REGISTERED_THIRD_VAP_DENY" if
                value=="REJECT" and probe=="default" else
                "REGISTERED_OLD_VAP_DENY" if value=="REJECT" else "ADMITTED")
            rows.append({
                "phase":phase,"probe":probe,
                "native_outcome":value,"native_attribution":attributed,
                "native_exit_code":1 if value=="REJECT" else 0,
                "source_pod_sha256":HASHES["pod-"+probe+".json"],
            })
    controls=[{
        "phase":"NO_BINDINGS","probe":x,"native_outcome":"ACCEPT",
        "native_attribution":"ADMITTED",
        "native_exit_code":0,
        "source_pod_sha256":HASHES["pod-"+x+".json"],
    } for x in PROBES]
    actions=[{
        "action":action,"actual_membership_change_verified":True,
        "command_result":{"returncode":0},
    } for action in PRED["registered_native_actions"]]
    return {
        "schema":"eeq-r3-m3-native-third-membership-v1",
        "source_predictions_read":False,
        "source_digest_map":HASHES,
        "registered_primary_rows":8,
        "registered_control_rows":2,
        "registered_native_membership_actions":3,
        "registered_inventory_snapshots":4,
        "observed_cases":rows,"control_rows":controls,
        "phase_inventories":phases,
        "native_membership_actions":actions,
        "original_binding_native_ids_unchanged":True,
        "original_v1_g5_increment":0,
        "error":None,
    }


class M3ScorerKillTests(unittest.TestCase):
    def test_nominal_mock_is_not_real_native_evidence(self):
        s=score(PRED,MANIFEST,mock_native(),DOCS)["summary"]
        self.assertEqual(s["matched_cases"],8)
        self.assertEqual(s["unbound_controls_passed"],2)
        self.assertEqual(s["full_information_B9_native_matches"],8)
        self.assertFalse(s["new_method_unique_advantage"])

    def test_missing_native_primary_aborts(self):
        d=mock_native();d["observed_cases"].pop()
        with self.assertRaisesRegex(ValueError,"EIGHT_REGISTERED_NATIVE_CELLS"):
            score(PRED,MANIFEST,d,DOCS)

    def test_duplicate_native_primary_aborts(self):
        d=mock_native();d["observed_cases"].append(d["observed_cases"][0])
        with self.assertRaisesRegex(ValueError,"DUPLICATE_"):
            score(PRED,MANIFEST,d,DOCS)

    def test_rejected_default_in_T2_must_be_attributed_to_new_VAP(self):
        d=mock_native();d["observed_cases"][5]["native_attribution"]=(
            "REGISTERED_OLD_VAP_DENY")
        s=score(PRED,MANIFEST,d,DOCS)["summary"]
        self.assertEqual(s["matched_cases"],7)

    def test_old_cached_default_ACCEPT_cannot_hide_new_native_rejection(self):
        d=mock_native()
        d["observed_cases"][5]["native_outcome"]="ACCEPT"
        d["observed_cases"][5]["native_attribution"]="ADMITTED"
        d["observed_cases"][5]["native_exit_code"]=0
        s=score(PRED,MANIFEST,d,DOCS)["summary"]
        self.assertEqual(s["matched_cases"],7)

    def test_missing_native_policy_membership_aborts(self):
        d=mock_native()
        d["phase_inventories"][2]["native_inventory"]["policy_items"].pop()
        with self.assertRaisesRegex(ValueError,"NATIVE_MEMBERSHIP"):
            score(PRED,MANIFEST,d,DOCS)

    def test_missing_native_binding_membership_aborts(self):
        d=mock_native()
        d["phase_inventories"][2]["native_inventory"]["binding_items"].pop()
        with self.assertRaisesRegex(ValueError,"NATIVE_MEMBERSHIP"):
            score(PRED,MANIFEST,d,DOCS)

    def test_forged_no_resource_version_change_aborts(self):
        d=mock_native()
        d["phase_inventories"][2]["native_inventory"][
            "binding_list_resource_version"]="200"
        with self.assertRaisesRegex(ValueError,
                                    "LIVE_INVENTORY_RESOURCE_VERSION"):
            score(PRED,MANIFEST,d,DOCS)

    def test_source_digest_drift_aborts_before_join(self):
        d=mock_native();d["source_digest_map"]["binding-third.json"]="tamper"
        with self.assertRaisesRegex(ValueError,"NATIVE_SOURCE_HASH_MISMATCH"):
            score(PRED,MANIFEST,d,DOCS)

    def test_native_policy_spec_wrong_aborts(self):
        d=mock_native()
        d["phase_inventories"][2]["native_inventory"][
            "policy_items"][1]["spec"]["validations"][0]["expression"]="true"
        with self.assertRaisesRegex(ValueError,"NATIVE_VAP_POLICY_SPEC"):
            score(PRED,MANIFEST,d,DOCS)

    def test_missing_native_action_aborts(self):
        d=mock_native();d["native_membership_actions"].pop()
        with self.assertRaisesRegex(ValueError,
                                    "THREE_REGISTERED_REAL_NATIVE_ACTIONS"):
            score(PRED,MANIFEST,d,DOCS)

    def test_live_original_two_binding_identity_change_aborts(self):
        d=mock_native()
        d["phase_inventories"][2]["native_inventory"]["binding_items"][0][
            "uid"]="different"
        with self.assertRaisesRegex(ValueError,"ORIGINAL_TWO_BINDINGS_CHANGED"):
            score(PRED,MANIFEST,d,DOCS)

    def test_unbound_control_failure_not_masked(self):
        d=mock_native();d["control_rows"][1]["native_outcome"]="REJECT"
        s=score(PRED,MANIFEST,d,DOCS)["summary"]
        self.assertEqual(s["unbound_controls_passed"],1)
        self.assertEqual(s["scientific_status"],"R3_M3_MISMATCH_OR_INADMISSIBLE")

    def test_ambiguous_native_error_not_counted_as_reject(self):
        d=mock_native()
        d["observed_cases"][0]["native_outcome"]="NATIVE_ORACLE_AMBIGUOUS"
        s=score(PRED,MANIFEST,d,DOCS)["summary"]
        self.assertEqual(s["ambiguous_cases"],1)
        self.assertEqual(s["matched_cases"],7)


if __name__=="__main__":
    unittest.main(verbosity=2)
