#!/usr/bin/env python3
"""Pure-synthetic adversarial tests of the join-only scientific scorer."""
import copy
import unittest
from r2b_join_native import all_words, evaluate


ACTIONS=["submit_root3_valid","submit_root3_bad_sig","submit_root2_A_replay"]
FILES=["root1.json","root2_A.json","root2_B.json","root3.json",
       "root3_bad_sig.json","targets_A.json","targets_B.json"]
KEYS={"root_signer":"root_signer_id","targets_A":"A_role",
      "targets_B":"B_role"}


def model_state(s):
    version={"H_A":2,"H_B":2,"H_3":3}[s]
    targets="B_role" if s=="H_B" else "A_role"
    return {"root_version":version,"root_role_keyids":["root_signer_id"],
            "root_role_threshold":1,"targets_role_keyids":[targets],
            "targets_role_threshold":1}


def graph():
    rows=[]
    for state in ("H_A","H_B","H_3"):
        for action in ACTIONS:
            accepts=state!="H_3" and action=="submit_root3_valid"
            next_state="H_3" if accepts else state
            rows.append({
                "state":state,"action":action,
                "expected_effect":"ADVANCE_TRUST_ROOT" if accepts else "KEEP_TRUST_ROOT",
                "expected_next":next_state,
                "candidate_source_sha256":"sha-"+action,
                "trusted_source_sha256":"sha-"+state
            })
    return rows


def pair_fixture():
    rows=graph()
    edges={(x["state"],x["action"]):x for x in rows}
    files={k:{"sha256":"file-sha-"+k,"bytes":101} for k in FILES}
    pred={
        "schema":"eeq-r2b-controlled-source-predictions-v1",
        "native_oracle_called":False,"actions":ACTIONS,"horizon":2,
        "source_files":files,"states":["H_A","H_B","H_3"],
        "key_ids":KEYS,"registered_graph":rows,
        "refinement_classes":[[["H_A","H_B"],["H_3"]]]*3
    }
    trials=[]
    for branch in ("A","B"):
        for word in all_words(ACTIONS):
            state="H_"+branch
            start=model_state(state)
            steps=[]
            for action in word:
                edge=edges[state,action]
                dst=edge["expected_next"]
                steps.append({
                    "action":action,
                    "source_sha256":edge["candidate_source_sha256"],
                    "native_action":"ACCEPT"
                     if edge["expected_effect"]=="ADVANCE_TRUST_ROOT" else "REJECT",
                    "before_native_state":model_state(state),
                    "after_native_state":model_state(dst),
                    "error":None
                })
                state=dst
            trials.append({
                "branch":branch,"action_word":list(word),
                "setup_status":"PASS","setup_error":None,"completed":True,
                "initial_native_state":start,"steps":steps
            })
    native={
        "schema":"eeq-r2b-controlled-tuf-native-oracle-v1",
        "predictor_loaded":False,
        "native_outcomes_generated_independently_from_predictions":True,
        "actions":ACTIONS,"action_horizon":2,
        "source_files":copy.deepcopy(files),
        "native_targets_authorization_cross_check":{
            "A":{"A":{"verified":True},"B":{"verified":False}},
            "B":{"A":{"verified":False},"B":{"verified":True}}
        },
        "trace_results":trials
    }
    return pred,native


class JoinOnlyKillTests(unittest.TestCase):
    def test_correct_diagnostic_is_b9_tie_not_unique_novelty(self):
        p,n=pair_fixture()
        r=evaluate(p,n)
        self.assertEqual(r["scores"]["source_transition_matches"],26)
        self.assertTrue(r["native_targets_authorization_difference_valid"])
        self.assertTrue(r["native_full_future_root_update_trace_equivalence"])
        self.assertTrue(r["strong_b9_also_merges_on_registered_contract"])
        self.assertFalse(r["r4_eeq_unique_advantage_established"])
        self.assertIn("DEV_ONLY_B9_TIE",r["disposition"])

    def test_scoring_mismatch_is_never_discarded(self):
        p,n=pair_fixture()
        row=next(x for x in n["trace_results"]
                 if x["branch"]=="A" and x["action_word"]==[ACTIONS[0]])
        row["steps"][0]["native_action"]="REJECT"
        self.assertGreater(evaluate(p,n)["scores"]["source_transition_mismatches"],0)
        self.assertIn("NOT_ESTABLISHED",evaluate(p,n)["disposition"])

    def test_wrong_native_post_authority_is_mismatch(self):
        p,n=pair_fixture()
        row=next(x for x in n["trace_results"]
                 if x["branch"]=="B" and x["action_word"]==[ACTIONS[0]])
        row["steps"][0]["after_native_state"]["targets_role_keyids"]=["B_role"]
        r=evaluate(p,n)
        self.assertEqual(r["scores"]["source_transition_mismatches"],1)

    def test_setup_failure_is_retained(self):
        p,n=pair_fixture()
        n["trace_results"][0]["setup_status"]="SETUP_FAILURE"
        n["trace_results"][0]["completed"]=False
        r=evaluate(p,n)
        self.assertEqual(r["scores"]["native_setup_failures"],1)
        self.assertNotIn("CONFIRMED",r["disposition"])

    def test_source_file_change_aborts(self):
        p,n=pair_fixture()
        n["source_files"]["root2_B.json"]["sha256"]="wrong"
        with self.assertRaisesRegex(ValueError,"SOURCE_HASH_OR_LENGTH_DRIFT"):
            evaluate(p,n)

    def test_missing_native_trace_aborts(self):
        p,n=pair_fixture()
        n["trace_results"].pop()
        with self.assertRaisesRegex(ValueError,"NATIVE_MISSING_TRACES"):
            evaluate(p,n)

    def test_duplicate_native_trace_aborts(self):
        p,n=pair_fixture()
        n["trace_results"].append(copy.deepcopy(n["trace_results"][0]))
        with self.assertRaisesRegex(ValueError,"DUPLICATE_NATIVE_CASE"):
            evaluate(p,n)

    def test_fake_targets_authority_does_not_count(self):
        p,n=pair_fixture()
        n["native_targets_authorization_cross_check"]["B"]["A"]["verified"]=True
        r=evaluate(p,n)
        self.assertFalse(r["native_targets_authorization_difference_valid"])
        self.assertIn("NOT_ESTABLISHED",r["disposition"])

    def test_missing_graph_action_aborts(self):
        p,n=pair_fixture()
        p["registered_graph"].pop()
        with self.assertRaisesRegex(ValueError,"SOURCE_GRAPH_NOT_3x3"):
            evaluate(p,n)

    def test_changed_action_scope_aborts(self):
        p,n=pair_fixture()
        n["actions"]=ACTIONS[:2]
        with self.assertRaisesRegex(ValueError,"ACTION_ALPHABET_CHANGED"):
            evaluate(p,n)


if __name__=="__main__":
    unittest.main(verbosity=2)
