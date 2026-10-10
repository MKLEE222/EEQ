#!/usr/bin/env python3
"""Synthetic R3-M2 scorer kill tests; not new or independently scored native."""
import copy
import unittest

from r3_m2_f0_emit import build
from r3_m2_join_only_scorer import join

SUMMARY, MASKED = build()
PHASES=("initial","after_first","after_second")


def synthetic_native(order):
    controls=[]
    for group in ("UNBOUND","ONLY_TEAM","ONLY_MODE"):
        for probe in ("flux","default"):
            native=("REJECT" if group!="UNBOUND" and probe=="flux"
                    else "ACCEPT")
            controls.append({"control":group,"probe":probe,"native":native})
    observations=[]
    for step,phase in enumerate(PHASES):
        for pod in ("flux","default"):
            effect=("REJECT" if pod=="flux" and step<2 else "ACCEPT")
            observations.append({
                "phase":phase,"phase_index":step,"probe":pod,
                "native":effect,
                "attribution":("REGISTERED_VAP_DENIAL" if effect=="REJECT"
                               else "ADMITTED"),
            })
    actions=[]
    for step in range(2):
        actions.append({
            "native_registered_action_verified":True,
            "before":{"uid":"synthetic-"+order,"resource_version":str(step+100)},
            "after":{"uid":"synthetic-"+order,"resource_version":str(step+101)},
        })
    return {
        "schema":"eeq-r3-m1-native-two-binding-one-order-v1",
        "order":order, "context":"synthetic-test-"+order,
        "error":None,"prediction_json_read":False,
        "observed_primary_rows":6,"observed_control_rows":6,
        "observed_action_count":2,"controls":controls,
        "observations":observations,"native_actions":actions,
    }


class R3M2JoinOnlyKillTests(unittest.TestCase):
    def setUp(self):
        self.summary=copy.deepcopy(SUMMARY)
        self.masked=copy.deepcopy(MASKED)
        self.tm=synthetic_native("TM")
        self.mt=synthetic_native("MT")

    def score(self):
        return join(self.masked,self.summary,self.tm,self.mt)

    def test_01_synthetic_nominal_does_not_count_new_native(self):
        r=self.score()
        self.assertEqual((r["original_native_distinct_cases"],
                          r["virtual_masked_packets_scored"]), (12,96))
        self.assertEqual(r["certified_native_exact_matches"],40)
        self.assertEqual(r["refused_packets"],56)
        self.assertEqual(r["new_native_calls"],0)

    def test_02_masked_row_missing_aborts(self):
        self.masked.pop()
        with self.assertRaisesRegex(ValueError,"DENOMINATOR"):
            self.score()

    def test_03_same_case_duplicate_does_not_inflate_accuracy(self):
        self.masked[-1]=copy.deepcopy(self.masked[0])
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            self.score()

    def test_04_wrong_certified_native_label_is_retained_not_hidden(self):
        for row in self.tm["observations"]:
            if row["phase"]=="initial" and row["probe"]=="flux":
                row["native"]="ACCEPT"
                row["attribution"]="ADMITTED"
        r=self.score()
        self.assertGreater(r["certified_native_mismatches"],0)
        self.assertEqual(r["virtual_masked_packets_scored"],96)
        self.assertEqual(r["scientific_status"],
                         "R3_M2_PARTIAL_SOURCE_METHOD_MISMATCH_RETAINED")

    def test_05_ambiguous_native_is_never_credited(self):
        self.tm["observations"][0]["native"]="NATIVE_ORACLE_AMBIGUOUS"
        with self.assertRaisesRegex(ValueError,"AMBIGUOUS"):
            self.score()

    def test_06_missing_original_native_row_aborts(self):
        self.tm["observations"].pop()
        with self.assertRaisesRegex(ValueError,"NOT_COMPLETE"):
            self.score()

    def test_07_missing_controls_in_old_native_aborts(self):
        self.mt["controls"].pop()
        with self.assertRaisesRegex(ValueError,"NOT_COMPLETE"):
            self.score()

    def test_08_original_action_not_verified_aborts(self):
        self.tm["native_actions"][0]["native_registered_action_verified"]=False
        with self.assertRaisesRegex(ValueError,"ACTION_NOT_VERIFIED"):
            self.score()

    def test_09_proof_disposition_cannot_be_tampered(self):
        self.masked[0]["disposition"]="PROVEN_ACCEPT"
        with self.assertRaisesRegex(ValueError,
             "UNVERIFIED_OR_B9_UNFAIR|FORGED_POSSIBLE_WORLD"):
            self.score()

    def test_10_refuse_cannot_be_relabelled_native_reject(self):
        i=next(i for i,x in enumerate(self.masked) if x["disposition"].endswith("REFUSE"))
        self.masked[i]["disposition"]="PROVEN_REJECT"
        with self.assertRaisesRegex(ValueError,
             "UNVERIFIED_OR_B9_UNFAIR|FORGED_POSSIBLE_WORLD"):
            self.score()

    def test_11_claim_of_external_authority_cannot_be_inserted(self):
        self.summary["full_c1_authority_independently_proven"]=True
        with self.assertRaisesRegex(ValueError,"SUMMARY_NOT_FROZEN"):
            self.score()

    def test_12_native_main_case_duplicate_aborts(self):
        self.mt["observations"][-1]=copy.deepcopy(self.mt["observations"][0])
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            self.score()

    def test_13_two_native_contexts_mandatory(self):
        self.mt["context"]=self.tm["context"]
        with self.assertRaisesRegex(ValueError,"CONTEXT_NOT_INDEPENDENT"):
            self.score()

    def test_14_scoped_native_denial_attribution_mandatory(self):
        self.tm["observations"][0]["attribution"]="UNRELATED_POLICY"
        with self.assertRaisesRegex(ValueError,"AMBIGUOUS"):
            self.score()


if __name__=="__main__":
    unittest.main(verbosity=2)
