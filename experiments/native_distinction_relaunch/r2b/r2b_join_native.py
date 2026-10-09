#!/usr/bin/env python3
"""R2-B join-only evaluator. Never generates sources or reruns native oracle."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def require(condition, why):
    if not condition:
        raise ValueError(why)


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def vector(a):
    return tuple(a)


def observable_root_only(state):
    if not state:
        return None
    return (state.get("root_version"),
            tuple(state.get("root_role_keyids") or []),
            state.get("root_role_threshold"))


def identity_matches(state, expected, key_ids):
    if not state:
        return False
    expected_versions = {"H_A": 2, "H_B": 2, "H_3": 3}
    expected_targets = {
        "H_A": key_ids["targets_A"],
        "H_B": key_ids["targets_B"],
        "H_3": key_ids["targets_A"],
    }
    return (state.get("root_version") == expected_versions[expected] and
            state.get("targets_role_keyids") == [expected_targets[expected]] and
            state.get("root_role_keyids") == [key_ids["root_signer"]] and
            state.get("root_role_threshold") == 1 and
            state.get("targets_role_threshold") == 1)


def decode_native(effect):
    if effect == "ACCEPT":
        return "ADVANCE_TRUST_ROOT"
    if effect == "REJECT":
        return "KEEP_TRUST_ROOT"
    return "UNSUPPORTED_NATIVE_ACTION"


def all_words(actions):
    return [()] + [(x,) for x in actions] + [
        (x, y) for x in actions for y in actions
    ]


def evaluate(pred, native):
    require(pred["schema"] == "eeq-r2b-controlled-source-predictions-v1",
            "PREDICTIONS_WRONG_SCHEMA")
    require(native["schema"] == "eeq-r2b-controlled-tuf-native-oracle-v1",
            "NATIVE_WRONG_SCHEMA")
    require(pred["native_oracle_called"] is False,
            "NATIVE_CALLED_IN_SOURCE_STAGE")
    require(native["predictor_loaded"] is False, "PREDICTOR_READ_BY_NATIVE")
    require(native["native_outcomes_generated_independently_from_predictions"],
            "NATIVE_PREDICTION_LEAKAGE")
    require(pred["actions"] == native["actions"], "ACTION_ALPHABET_CHANGED")
    require(pred["horizon"] == native["action_horizon"] == 2,
            "FUTURE_HORIZON_CHANGED")
    require(set(pred["source_files"]) == set(native["source_files"]),
            "SOURCE_FILE_SET_CHANGED")
    for filename, p in pred["source_files"].items():
        require(p == native["source_files"][filename],
                "SOURCE_HASH_OR_LENGTH_DRIFT: " + filename)

    actions = pred["actions"]
    required = set(all_words(actions))
    require(len(required) == 13, "REGISTERED_WORD_COUNT_INCORRECT")

    graph = {}
    for edge in pred["registered_graph"]:
        name = (edge["state"], edge["action"])
        require(name not in graph, "DUPLICATE_GRAPH_EDGE")
        graph[name] = edge
    require(len(graph) == 9, "SOURCE_GRAPH_NOT_3x3")
    for s in ["H_A", "H_B", "H_3"]:
        for a in actions:
            require((s, a) in graph, "INCOMPLETE_REGISTERED_GRAPH")

    observed = {}
    for trace in native["trace_results"]:
        branch, word = trace["branch"], tuple(trace["action_word"])
        require(branch in ("A", "B") and word in required,
                "NATIVE_UNREGISTERED_CASE")
        key = (branch, word)
        require(key not in observed, "DUPLICATE_NATIVE_CASE")
        observed[key] = trace
    require(len(observed) == 26, "NATIVE_MISSING_TRACES")
    require(set(observed) == {
        (branch, word) for branch in ("A", "B") for word in required
    }, "NATIVE_TRACE_SET_CHANGED")

    score_rows = []
    statuses = Counter()
    comparable_projections = {"A": {}, "B": {}}
    for branch in ("A", "B"):
        start = "H_" + branch
        for word in all_words(actions):
            o = observed[(branch, word)]
            setup_ok = (o["setup_status"] == "PASS" and o["completed"])
            state = start
            trace_actual_effects = []
            trace_native_post = []
            all_steps_match = setup_ok and len(o["steps"]) == len(word)
            if setup_ok and not identity_matches(o["initial_native_state"], start,
                                                  pred["key_ids"]):
                all_steps_match = False
            for a,step in zip(word, o["steps"]):
                model = graph[(state, a)]
                native_effect = decode_native(step["native_action"])
                trace_actual_effects.append(native_effect)
                trace_native_post.append(observable_root_only(
                    step["after_native_state"]))
                if (step["action"] != a or
                    step["source_sha256"] != model["candidate_source_sha256"] or
                    not identity_matches(step["before_native_state"], state,
                                         pred["key_ids"]) or
                    not identity_matches(step["after_native_state"],
                                         model["expected_next"], pred["key_ids"]) or
                    native_effect != model["expected_effect"]):
                    all_steps_match = False
                state = model["expected_next"]
            status = ("MATCH" if all_steps_match else
                      "NATIVE_SETUP_FAILURE" if not setup_ok else "MISMATCH")
            statuses[status] += 1
            # Compare ACTUAL registered root-decision consequences across
            # histories, excluding out-of-contract targets source identity.
            proj = {
                "effect_path": trace_actual_effects,
                "root_only_initial": observable_root_only(o["initial_native_state"]),
                "root_only_post_path": trace_native_post,
            }
            comparable_projections[branch][word] = proj
            score_rows.append({
                "branch": branch,
                "action_word": list(word),
                "matched_frozen_source_transition": status == "MATCH",
                "comparison_status": status,
                "native_effect_path": trace_actual_effects,
                "expected_effect_path": [
                    graph[(s, a)]["expected_effect"]
                    for s,a in _path_edges(start,word,graph)
                ],
                "native_root_only_trace": proj,
                "native_setup_error": o.get("setup_error"),
                "native_step_errors": [x.get("error") for x in o.get("steps", [])],
            })

    q=native["native_targets_authorization_cross_check"]
    require(set(q) == {"A","B"} and
            all(set(q[x]) == {"A","B"} for x in ("A","B")),
            "NATIVE_TARGETS_PROBE_GRID_INVALID")
    cross_pattern=[q["A"]["A"]["verified"],q["A"]["B"]["verified"],
                   q["B"]["A"]["verified"],q["B"]["B"]["verified"]]
    native_qualifications_genuinely_differ = (
        cross_pattern == [True,False,False,True]
    )
    native_equivalent = all(
        comparable_projections["A"][word] == comparable_projections["B"][word]
        for word in all_words(actions)
    ) and statuses.get("NATIVE_SETUP_FAILURE",0) == 0
    # B9 has the SAME root version/root role and allowed future action
    # validity; it can compute the same partition. This is an equality
    # check, not an unsupported speed/engineering claim.
    strong_b9_tie_on_fixed_contract = native_equivalent

    complete = (statuses.get("MATCH",0) == 26 and
                statuses.get("MISMATCH",0) == 0 and
                native_qualifications_genuinely_differ and
                native_equivalent)
    return {
        "schema":"eeq-r2b-controlled-native-join-result-v1",
        "evidence_class":"CONTROLLED_NATIVE_DEVELOPMENT",
        "old_g4_modified":False,
        "native_contract":"ROOT_UPDATE_ONLY",
        "registered_horizon":2,
        "native_traces_total":26,
        "native_actions":actions,
        "native_targets_authority_cross_verified":q,
        "native_targets_authorization_difference_valid":
            native_qualifications_genuinely_differ,
        "native_full_future_root_update_trace_equivalence":native_equivalent,
        "frozen_source_expected_quotient_classes":
            [len(x) for x in pred["refinement_classes"]],
        "strong_b9_also_merges_on_registered_contract":
            strong_b9_tie_on_fixed_contract,
        "original_full_B0_retains_distinct_sources":True,
        "r2_a_native_future_distinction_established":False,
        "r4_eeq_unique_advantage_established":False,
        "scores":{
            "source_transition_matches":statuses.get("MATCH",0),
            "source_transition_mismatches":statuses.get("MISMATCH",0),
            "native_setup_failures":statuses.get("NATIVE_SETUP_FAILURE",0),
            "matched_cases_denominator":26,
            "total_native_action_steps":
                sum(len(row.get("steps",[])) for row in native["trace_results"])
        },
        "rows":score_rows,
        "disposition": (
            "R2_B_CONTROLLED_NATIVE_NONCOSMETIC_MERGE_CONFIRMED_DEV_ONLY_B9_TIE"
            if complete else "R2_B_NOT_ESTABLISHED_KEEP_ALL_FAILURES"
        ),
        "scope_warning": (
            "Controlled test-only signing and ROOT-UPDATE-ONLY contract; "
            "not production-lawfulness/general TUF equivalence, not R2-A, "
            "not superiority over the strong B9 or classical quotient."
        )
    }


def _path_edges(start,word,graph):
    state = start
    for action in word:
        yield state, action
        state = graph[state, action]["expected_next"]


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pred",required=True)
    p.add_argument("--native",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    result=evaluate(load(args.pred),load(args.native))
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                              encoding="utf-8")
    print(json.dumps({
        **result["scores"],
        "native_targets_authorization_difference_valid":
            result["native_targets_authorization_difference_valid"],
        "native_future_trace_equivalence":
            result["native_full_future_root_update_trace_equivalence"],
        "strong_b9_merges":
            result["strong_b9_also_merges_on_registered_contract"],
        "disposition":result["disposition"]
    },sort_keys=True))


if __name__=="__main__":
    main()
