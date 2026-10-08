#!/usr/bin/env python3
"""Falsification-first tests for a candidate v2 operator.

A PASS demonstrates only correctness on declared SYNTHETIC finite systems.
It does not turn synthetic data into native-family evidence or G5 counts.
"""
import copy
import json
import unittest
from collections import Counter, defaultdict

from lawful_quotient import (
    EvidenceRefusal, REFUSAL, canon, compile_quotient,
    distinction_witness, independent_equivalence_check,
    legal_next_actions, correction_words, observable, safe_compile,
    validate_spec, quotient_downstream_check,
)
from synthetic_systems import generate_system, toy_system

def clone(obj):
    return copy.deepcopy(obj)

def current_only_safe_action_accuracy(spec):
    states={s["id"]:s for s in spec["states"]}
    groups=defaultdict(Counter)
    for sid, state in states.items():
        key=canon(observable(spec,state))
        safe=tuple(legal_next_actions(spec,sid,"continuation","release"))
        groups[key][safe]+=1
    return sum(max(counts.values()) for counts in groups.values())/len(states)

class LawfulQuotientTest(unittest.TestCase):
    def test_current_outcome_collapses_but_future_actions_split(self):
        spec=toy_system()
        q0=compile_quotient(spec,0)
        q1=compile_quotient(spec,1)
        self.assertEqual(q0["class_count"],3)
        self.assertEqual(q1["class_count"],5)
        self.assertEqual(q0["states_to_final_class"]["s0"],
                         q0["states_to_final_class"]["s2"])
        self.assertNotEqual(q1["states_to_final_class"]["s0"],
                            q1["states_to_final_class"]["s2"])
        self.assertEqual(q1["states_to_final_class"]["s0"],
                         q1["states_to_final_class"]["s1"])
        self.assertEqual(q1["states_to_final_class"]["s3"],
                         q1["states_to_final_class"]["s6"])
        self.assertEqual(independent_equivalence_check(spec,1,q1)["status"],"PASS")

    def test_shortest_future_distinction_certificate(self):
        spec=toy_system()
        witness=distinction_witness(spec,"s0","s2",1)
        self.assertEqual(witness["length"],1)
        self.assertEqual(witness["actions"],["revoke_A"])
        self.assertIsNone(distinction_witness(spec,"s0","s1",3))

    def test_unknown_authentication_or_authorization_refuses(self):
        spec=toy_system()
        state=next(s for s in spec["states"] if s["id"]=="s5")
        self.assertEqual(observable(spec,state)[0]["verdict"],"REFUSE")
        state["qualification"]["A"]["authenticated"]=False
        self.assertEqual(observable(spec,state)[0]["verdict"],"DENY")

    def test_audit_provenance_is_claim_relative(self):
        unaudited=toy_system(audit=False)
        audited=toy_system(audit=True)
        q0=compile_quotient(unaudited,0)
        qa=compile_quotient(audited,0)
        self.assertEqual(q0["states_to_final_class"]["s0"],
                         q0["states_to_final_class"]["s2"])
        self.assertNotEqual(qa["states_to_final_class"]["s0"],
                            qa["states_to_final_class"]["s2"])
        self.assertEqual(qa["states_to_final_class"]["s0"],
                         qa["states_to_final_class"]["s1"])

    def test_missing_critical_governance_refuses_without_false(self):
        spec=toy_system()
        spec["c1_complete"]=False
        self.assertEqual(safe_compile(spec,1)["status"],REFUSAL)
        self.assertEqual(safe_compile(spec,1)["reason"],"c1_complete_not_proven")

    def test_incomplete_c2_and_c3_are_not_implicitly_completed(self):
        for name in ("c2_complete","c3_complete","decision_time_visible"):
            spec=toy_system()
            spec[name]=False
            self.assertEqual(safe_compile(spec,1)["status"],REFUSAL)
        spec=toy_system()
        del spec["states"][0]["qualification"]["A"]
        self.assertEqual(safe_compile(spec,1)["reason"],"incomplete_c1_source_state")
        spec=toy_system()
        del spec["states"][0]["transitions"]["revoke_A"]
        self.assertEqual(safe_compile(spec,1)["reason"],"incomplete_c3_action_relation")

    def test_native_outcome_injection_rejected_at_v0(self):
        for key in ("native_action","native_label","mergeable_state",
                    "post_hoc_expected_label","scored_native_outcome"):
            spec=toy_system()
            spec["states"][0]["irrelevant_metadata"][key]="POISON"
            self.assertEqual(safe_compile(spec,1)["status"],REFUSAL)
            self.assertEqual(safe_compile(spec,1)["reason"],"forbidden_native_outcome_field")

    def test_true_finite_horizon_layer_semantics(self):
        spec=toy_system()
        for horizon in range(4):
            q=compile_quotient(spec,horizon)
            independent=independent_equivalence_check(spec,horizon,q)
            self.assertEqual(independent["status"],"PASS",independent)
            self.assertEqual(independent["pairs_compared"],21)
            for k in range(1,horizon+1):
                prev=q["state_to_class_by_depth"][k-1]
                curr=q["state_to_class_by_depth"][k]
                states={s["id"]:s for s in spec["states"]}
                per_class=defaultdict(list)
                for sid,cid in curr.items():
                    per_class[cid].append(sid)
                for members in per_class.values():
                    successors={
                        tuple(prev[states[s]["transitions"][a]]
                              for a in sorted(spec["actions"]))
                        for s in members
                    }
                    self.assertEqual(len(successors),1)

    def test_downstream_safe_actions_not_recoverable_from_current_label(self):
        spec=toy_system()
        q=compile_quotient(spec,1)
        self.assertIn("revoke_B",legal_next_actions(spec,"s0","continuation","release"))
        self.assertNotIn("revoke_A",legal_next_actions(spec,"s0","continuation","release"))
        self.assertIn("revoke_A",legal_next_actions(spec,"s2","continuation","release"))
        self.assertNotIn("revoke_B",legal_next_actions(spec,"s2","continuation","release"))
        self.assertEqual(quotient_downstream_check(spec,q,"continuation","release")["status"],"PASS")
        self.assertLess(current_only_safe_action_accuracy(spec),1.0)

    def test_correction_path_legality(self):
        spec=toy_system()
        self.assertEqual(correction_words(spec,"s3","continuation","release",0),[])
        paths=correction_words(spec,"s3","continuation","release",1)
        self.assertEqual(paths,[["restore_A"]])
        q=compile_quotient(spec,2)
        self.assertEqual(quotient_downstream_check(spec,q,"continuation","release")["status"],"PASS")

    def test_synthetic_exhaustive_independent_oracle(self):
        for seed in (20261008,20261009,20261010):
            spec=generate_system(sources=5,claims=2,actions=2,
                                 density=.4,contracts=2,state_count=16,seed=seed)
            for horizon in (0,1,2):
                q=compile_quotient(spec,horizon)
                result=independent_equivalence_check(spec,horizon,q)
                self.assertEqual(result["status"],"PASS",result)
                self.assertEqual(result["pairs_compared"],120)

    def test_generated_redundancy_is_explicit_and_mergeable(self):
        spec=generate_system(state_count=64)
        q=compile_quotient(spec,2)
        self.assertLessEqual(q["class_count"],16)
        self.assertEqual(q["states_to_final_class"]["s000"],
                         q["states_to_final_class"]["s016"])
        self.assertEqual(q["states_to_final_class"]["s016"],
                         q["states_to_final_class"]["s032"])

    def test_determinism_is_byte_stable(self):
        spec=generate_system(state_count=32)
        self.assertEqual(canon(compile_quotient(spec,2)),
                         canon(compile_quotient(clone(spec),2)))

    def test_invalid_spec_or_horizon_does_not_score(self):
        spec=toy_system()
        spec["sources"][0]["identity_provenance_available"]=False
        self.assertEqual(safe_compile(spec,1)["status"],REFUSAL)
        with self.assertRaises(ValueError):
            compile_quotient(toy_system(),-1)

    def test_no_minimum_byte_claim(self):
        q=compile_quotient(toy_system(),2)
        self.assertIn("quotient_table_bytes",q["cost"])
        self.assertIn("amortized_bytes_per_state",q["cost"])
        self.assertIn("class_count_minimality_not_bit_minimality",q["limitations"])

if __name__ == "__main__":
    unittest.main()
