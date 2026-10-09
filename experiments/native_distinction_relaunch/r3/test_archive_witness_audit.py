#!/usr/bin/env python3
"""Synthetic adversarial R3 archival consistency checks; no native scoring."""
import copy
import unittest
from audit_archived_r2_native import run, b_prefixes


def fixture():
    worlds=("WORLD_GATE","WORLD_STANDBY")
    phases=("CURRENT","AFTER_BINDING_MUTATION")
    sas=("flux","default")
    rows=[]
    for world in worlds:
        for phase in phases:
            for sa in sas:
                decision=("REJECT" if world=="WORLD_GATE" and
                          phase=="AFTER_BINDING_MUTATION" and sa=="flux"
                          else "ACCEPT")
                rows.append({
                    "world":world,"phase":phase,"service_account":sa,
                    "source_only_predicted":decision,"native_observed":decision,
                    "case_status":"MATCH",
                    "native_attribution":"REGISTERED_VAP" if decision=="REJECT" else None
                })
    a={
        "schema":"eeq-r2a-k8s-native-vs-frozen-source-v1",
        "evidence_class":"CONTROLLED_NATIVE_TWO_ISOLATED_CLUSTER_EPISODES",
        "status":"CONTROLLED_NATIVE_A_CONFIRMED_B9_TIE",
        "summary":{
            "frozen_admission_denominator":8,
            "native_admission_matches":8,
            "native_admission_mismatches_or_unavailable":0,
            "episodes_completed":2,"verified_policy_transitions":2,
            "current_decision_vectors_identical":True,
            "future_decision_vectors_diverge_after_same_native_patch":True,
            "source_qualification_distinction_verified":True,
            "strong_b9_tie_predeclared":True,
            "independent_novelty_advantage":False,"full_R2_gate_pass":False,
        },
        "infrastructure_failures":[],
        "case_results":rows,
        "world_summaries":{
            w:{"episode_status":"NATIVE_EPISODE_COMPLETED",
               "policy_transition_supported":True,
               "num_admission_rows":4,
               "num_activation_probes":1}
            for w in worlds
        },
        "witness":{
            "registered_action":"PATCH_BINDING_SELECTOR_TO_GATE",
            "pre_action_flux_gate":"ACCEPT",
            "pre_action_flux_standby":"ACCEPT",
            "post_action_flux_gate":"REJECT",
            "post_action_flux_standby":"ACCEPT",
            "native_binding_resource_mutation_evidence_required":True
        }
    }
    actions=("submit-candidate-2","submit-candidate-3")
    rows=[]
    for initial in ("A","B"):
        for pref in b_prefixes():
            for act in actions:
                effect="ACCEPT" if act==actions[0] and not pref else "REJECT"
                rows.append({
                    "initial_state":initial,
                    "action_prefix":list(pref),"challenge_action":act,
                    "expected":effect,"observed":effect,"status":"MATCH",
                    "prefix_errors":[],
                    "expected_next_canonical_signed_sha256":"sha-"+act+"-"+str(pref),
                    "actual_next_canonical_signed_sha256":"sha-"+act+"-"+str(pref)
                })
    qual={
        ("A","TARGETS_A"):"QUALIFIED",
        ("A","TARGETS_B"):"UNQUALIFIED",
        ("B","TARGETS_A"):"UNQUALIFIED",
        ("B","TARGETS_B"):"QUALIFIED"
    }
    b={
        "schema":"eeq-r2b-pinned-source-vs-independent-native-v1",
        "evidence_class":"CONTROLLED_NATIVE_DEVELOPMENT",
        "status":"CONTROLLED_NATIVE_B_CONFIRMED_B9_TIE",
        "summary":{
            "native_challenge_cells":28,
            "native_root_update_matches":28,
            "native_root_update_nonmatches":0,
            "native_targets_authority_cells":4,
            "native_targets_role_matches":4,
            "native_targets_role_nonmatches":0,
            "registered_initial_states":2,"prefixes_per_state":7,
            "unresolved_prefix_cells":0,
            "complete_future_trace_equivalence":True,
            "strong_b9_tie_predeclared":True,
            "classical_quotient_tie_predeclared":True,
            "novelty_advantage_established":False,
            "R2_A_future_separation_demonstrated":False,
            "R2_FULL_GATE_PASS":False,
        },
        "root_action_comparisons":rows,
        "targets_authority_comparisons":[
            {"initial_state":i,"target_document":t,
             "native_qualified":v,"predicted_qualified":v,"status":"MATCH"}
            for (i,t),v in qual.items()
        ],
        "old_G4_unchanged":True,
        "new_G5_cases":0,
        "no_prospective_holdout_claim":True,
    }
    return a,b


class ArchiveAuditKillTests(unittest.TestCase):
    def test_complete_both_science_limits_kept(self):
        a,b=fixture()
        r=run(a,b)
        self.assertEqual(r["status"],"R2_NATIVE_A_AND_B_CROSS_FAMILY_CONFIRMED")
        self.assertEqual(r["strong_B9"],"B9_TIE_EXPECTED_NOT_MATCHED_COST_BENCHMARK")
        self.assertEqual(r["gate_dispositions"]["R3_unified_label_blind_native_compiler"],
                         "NOT_DEMONSTRATED")
        self.assertEqual((r["A"]["native_denominator"],r["B"]["native_denominator"]),
                         (8,28))
    def test_r2a_missing_case_rejected(self):
        a,b=fixture()
        a["case_results"].pop()
        with self.assertRaisesRegex(ValueError,"R2A_REGISTERED_CASE_SET"):
            run(a,b)
    def test_r2a_duplicate_case_rejected(self):
        a,b=fixture()
        a["case_results"].append(copy.deepcopy(a["case_results"][0]))
        with self.assertRaisesRegex(ValueError,"DUPLICATE_R2A"):
            run(a,b)
    def test_r2a_future_wrong_result_rejected(self):
        a,b=fixture()
        target=next(r for r in a["case_results"] if
                    r["world"]=="WORLD_GATE" and
                    r["phase"]=="AFTER_BINDING_MUTATION" and
                    r["service_account"]=="flux")
        target["native_observed"]="ACCEPT"
        with self.assertRaisesRegex(ValueError,"R2A_MISMATCH"):
            run(a,b)
    def test_r2a_native_mutation_missing_rejected(self):
        a,b=fixture()
        a["world_summaries"]["WORLD_STANDBY"]["policy_transition_supported"]=False
        with self.assertRaisesRegex(ValueError,"R2A_CLUSTER"):
            run(a,b)
    def test_r2a_native_policy_attribution_wrong_rejected(self):
        a,b=fixture()
        target=next(r for r in a["case_results"] if
                    r["native_attribution"]=="REGISTERED_VAP")
        target["native_attribution"]="OTHER_CONTROLLER"
        with self.assertRaisesRegex(ValueError,"R2A_DIVERGENCE_NOT_ATTRIBUTED"):
            run(a,b)
    def test_r2b_missing_prefix_rejected(self):
        a,b=fixture()
        b["root_action_comparisons"].pop()
        with self.assertRaisesRegex(ValueError,"R2B_REGISTERED_NATIVE_CHALLENGE_SET"):
            run(a,b)
    def test_r2b_wrong_source_successor_hash_rejected(self):
        a,b=fixture()
        b["root_action_comparisons"][0]["actual_next_canonical_signed_sha256"]="wrong"
        with self.assertRaisesRegex(ValueError,"R2B_NATIVE_ACTION_OR_NEXT_SOURCE_INVALID"):
            run(a,b)
    def test_r2b_future_different_across_anchors_rejected(self):
        a,b=fixture()
        target=next(r for r in b["root_action_comparisons"] if
                    r["initial_state"]=="B" and not r["action_prefix"])
        target["observed"]="REJECT" if target["observed"]=="ACCEPT" else "ACCEPT"
        target["expected"]=target["observed"]
        with self.assertRaisesRegex(ValueError,"R2B_FUTURE_NATIVE_VECTOR_DIFFERENCE"):
            run(a,b)
    def test_r2b_noncosmetic_targets_contrast_required(self):
        a,b=fixture()
        target=next(r for r in b["targets_authority_comparisons"] if
                    r["initial_state"]=="B" and r["target_document"]=="TARGETS_A")
        target["native_qualified"]="QUALIFIED"
        with self.assertRaisesRegex(ValueError,"R2B_TARGET_QUALIFICATION_PAIR_INVALID"):
            run(a,b)
    def test_r2b_strong_b9_does_not_disappear(self):
        a,b=fixture()
        b["summary"]["strong_b9_tie_predeclared"]=False
        with self.assertRaisesRegex(ValueError,"R2B_UNJUSTIFIED_NOVELTY"):
            run(a,b)
    def test_r2a_full_gate_false_guarded(self):
        a,b=fixture()
        a["summary"]["full_R2_gate_pass"]=True
        with self.assertRaisesRegex(ValueError,"R2A_SCIENCE_B9"):
            run(a,b)


if __name__=="__main__":
    unittest.main(verbosity=2)
