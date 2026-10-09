#!/usr/bin/env python3
"""R2B immutable join-only scorer: independently frozen SOURCE vs tuf-js NATIVE.

No fixture generation, extractor, crypto, or native library imported here.
Errors/missing cases/UNKNOWN never count as matches; B9 has full native info.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

STATES = ("s2a", "s2b", "s3a", "s3b", "s4a", "s4b")
ACTIONS = ("submit-root-3-a", "submit-root-3-b",
           "submit-root-4-a", "submit-root-4-b")


def require(v, message):
    if not v:
        raise ValueError(message)


def unique(records, key):
    result = {}
    for record in records:
        k = key(record)
        require(k not in result, "DUPLICATE_CASE_" + str(k))
        result[k] = record
    return result


def action_words():
    return [()] + [(a,) for a in ACTIONS] + [
        (a, b) for a in ACTIONS for b in ACTIONS
    ]


def compare(pred, native, manifest):
    require(pred.get("schema") == "eeq-r2b-source-predictions-v1",
            "UNFROZEN_PREDICTOR_SCHEMA")
    require(native.get("schema") == "eeq-r2b-native-tuf-controlled-grid-v1",
            "UNFROZEN_NATIVE_SCHEMA")
    require(manifest.get("schema") == "eeq-r2b-source-manifest-v1",
            "BAD_SOURCE_MANIFEST")
    require(native.get("predictions_json_read") is False,
            "NATIVE_ORACLE_READ_PREDICTIONS")
    require(pred.get("native_outcomes_read") is False,
            "EXTRACTOR_READ_NATIVE_LABEL")
    require(native.get("original_g5_increment") == 0, "G5_TAMPER")
    require(tuple(native["registered_states"]) == STATES, "STATE_REGISTRATION_CHANGED")
    require(tuple(native["registered_actions"]) == ACTIONS, "ACTION_REGISTRATION_CHANGED")
    require(native["registered_horizon"] == 2, "HORIZON_CHANGED")
    source_hashes = {x["name"]: x["sha256"] for x in manifest["sources"]}
    require(source_hashes == native["source_digests"], "SOURCE_HASH_MISMATCH")
    require(len(source_hashes) == 9, "SOURCE_MANIFEST_NOT_COMPLETE")
    expected_states = {x["state"]: x for x in pred["states"]}
    actions = {x["action"]: x for x in pred["actions"]}
    require(set(expected_states) == set(STATES) and set(actions) == set(ACTIONS),
            "PREDICTION_REGISTRATION_CHANGED")

    ps = unique(pred["predictions"], lambda r: (r["from_state"], r["action"]))
    ns = unique(native["one_step"], lambda r: (r["from_state"], r["action"]))
    cells = {(s, a) for s in STATES for a in ACTIONS}
    require(set(ps) == cells and set(ns) == cells, "INCOMPLETE_NATIVE_24_GRID")
    row_checks = []
    for s in STATES:
        for a in ACTIONS:
            expected, observed = ps[s, a], ns[s, a]
            if observed.get("setup_error"):
                status = "SETUP_FAILURE"
            elif expected["effect"] == "MODEL_UNSUPPORTED":
                status = "UNSUPPORTED_PREDICTOR"
            else:
                should_accept = expected["effect"] == "ADVANCE_TRUST_ROOT"
                effect = "ACCEPT" if should_accept else "REJECT"
                valid = (
                    observed.get("effect") == effect
                    and observed.get("native_after_state") == expected["to_state"]
                    and observed.get("initial_source_sha256") ==
                    expected["from_source_sha256"]
                    and observed.get("candidate_sha256") ==
                    expected["candidate_source_sha256"]
                )
                status = "MATCH" if valid else "MISMATCH"
            row_checks.append({
                "from_state": s, "action": a,
                "source_effect": expected["effect"],
                "source_to_state": expected["to_state"],
                "native_effect": observed.get("effect", observed.get("native_effect")),
                "native_to_state": observed.get("native_after_state"),
                "native_error": observed.get("error"),
                "setup_error": observed.get("setup_error"),
                "status": status,
            })

    words = action_words()
    require(len(words) == 21, "WRONG_TRACE_SET")
    nt = unique(native["action_traces"], lambda x: (
        x["from_state"], tuple(x["word"])))
    expected_traces = {(s, word) for s in STATES for word in words}
    require(set(nt) == expected_traces, "INCOMPLETE_NATIVE_126_TRACES")
    trace_checks = []
    native_trace_outputs = {}
    for s in STATES:
        for word in words:
            observed = nt[s, word]
            end = s
            expected_effects = []
            expected_states_seq = []
            for action in word:
                e = ps[end, action]
                expected_effects.append(
                    "ACCEPT" if e["effect"] == "ADVANCE_TRUST_ROOT" else
                    "REJECT" if e["effect"] == "KEEP_TRUST_ROOT" else
                    "MODEL_UNSUPPORTED"
                )
                end = e["to_state"] if e["to_state"] is not None else end
                expected_states_seq.append(end)
            native_events = observed["events"]
            observed_effects = [event["effect"] for event in native_events]
            observed_states = [event["native_after_state"] for event in native_events]
            valid = (not observed.get("setup_error") and
                     observed_effects == expected_effects and
                     observed_states == expected_states_seq and
                     observed.get("terminal_native_state") == end)
            status = "MATCH" if valid else (
                "SETUP_FAILURE" if observed.get("setup_error") else "MISMATCH"
            )
            native_trace_outputs[s, word] = tuple(observed_effects) if valid else None
            trace_checks.append({
                "from_state": s, "action_word": list(word),
                "expected_effects": expected_effects,
                "native_effects": observed_effects,
                "expected_terminal_state": end,
                "native_terminal_state": observed.get("terminal_native_state"),
                "status": status,
            })

    pc = unique(pred["qualifications"], lambda x: (
        x["state"], x["targets_source_name"]))
    nc = unique(native["target_controls"], lambda x: (
        x["from_state"], x["target_source_name"]))
    control_cases = {(s, "targets-" + t + ".json") for s in STATES for t in "ab"}
    require(set(pc) == control_cases and set(nc) == control_cases,
            "INCOMPLETE_TARGET_12_NEGATIVE_CONTROLS")
    controls = []
    for s in STATES:
        for t in "ab":
            target = "targets-" + t + ".json"
            p, n = pc[s, target], nc[s, target]
            good = (not n.get("setup_error") and
                    p["status"] == n["native_qualification"] and
                    p["targets_sha256"] == n.get("target_source_sha256"))
            controls.append({
                "state": s, "targets_source": target,
                "predicted_status": p["status"],
                "native_status": n["native_qualification"],
                "native_error": n.get("error"),
                "status": "MATCH" if good else "MISMATCH",
            })

    # Native observed action effect traces only. Full registered action
    # alphabet, 21 words per state. Do not collapse sources or target roles.
    native_equiv = []
    for version in (2, 3, 4):
        left, right = ("s" + str(version) + "a", "s" + str(version) + "b")
        equal = all(native_trace_outputs[left, w] is not None and
                    native_trace_outputs[left, w] == native_trace_outputs[right, w]
                    for w in words)
        native_equiv.append({
            "states": [left, right],
            "same_all_native_root_update_outcome_traces": equal,
            "exhaustive_word_count": len(words),
            "distinct_signed_root_sources":
                expected_states[left]["source_sha256"] !=
                expected_states[right]["source_sha256"],
            "targets_authorization_differs":
                expected_states[left]["targets_role_keyids"] !=
                expected_states[right]["targets_role_keyids"],
            "qualifier_control_proves_difference":
                nc[left, "targets-a.json"]["native_qualification"] == "QUALIFIED"
                and nc[right, "targets-a.json"]["native_qualification"] ==
                "UNQUALIFIED"
                and nc[left, "targets-b.json"]["native_qualification"] ==
                "UNQUALIFIED"
                and nc[right, "targets-b.json"]["native_qualification"] ==
                "QUALIFIED",
        })

    # A strong expert native-state baseline is allowed the complete root
    # and targets role information. For this restricted root-update contract,
    # root version + fixed candidate version is already sufficient.
    b9_matches = 0
    for item in row_checks:
        expected_accept = int(item["action"].split("-")[2]) == (
            int(item["from_state"][1]) + 1
        )
        predicted_effect = "ACCEPT" if expected_accept else "REJECT"
        if item["native_effect"] == predicted_effect:
            b9_matches += 1
    c = Counter(item["status"] for item in row_checks)
    t = Counter(item["status"] for item in trace_checks)
    d = Counter(item["status"] for item in controls)
    full_b_pairs = sum(
        all(row[k] for k in (
            "same_all_native_root_update_outcome_traces",
            "distinct_signed_root_sources",
            "targets_authorization_differs",
            "qualifier_control_proves_difference",
        )) for row in native_equiv
    )
    valid = (c == Counter({"MATCH": 24}) and
             t == Counter({"MATCH": 126}) and
             d == Counter({"MATCH": 12}) and
             full_b_pairs == 3 and b9_matches == 24)
    summary = {
        "one_step_registered": 24, "one_step_matches": c["MATCH"],
        "one_step_mismatches": c["MISMATCH"],
        "one_step_setup_failures": c["SETUP_FAILURE"],
        "traces_registered": 126, "trace_matches": t["MATCH"],
        "trace_mismatches": t["MISMATCH"],
        "targets_controls_registered": 12,
        "targets_controls_matches": d["MATCH"],
        "noncosmetic_native_b_pairs_verified": full_b_pairs,
        "strong_b9_native_matches": b9_matches,
        "strong_b9_native_total": 24,
        "classical_quotient_source_classes":
            pred["quotient"]["horizons"][2]["class_count"],
        "evidence_class": "CONTROLLED_NATIVE_DEVELOPMENT",
        "r2b_status": (
            "CONTROLLED_TUF_B_CONTRACT_RELATIVE_MERGE_CALIBRATED_B9_TIE"
            if valid else "R2B_NATIVE_MISMATCH_OR_INCOMPLETE"
        ),
        "r2_a_established": False, "r4_unique_advantage_established": False,
        "original_g5_increment": 0,
    }
    return {
        "schema": "eeq-r2b-joined-source-vs-native-result-v1",
        "status": summary["r2b_status"],
        "one_step_checks": row_checks,
        "all_126_native_trace_checks": trace_checks,
        "targets_qualification_negative_controls": controls,
        "native_b_pairs": native_equiv,
        "summary": summary,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-pred", required=True)
    parser.add_argument("--native", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    p = json.loads(Path(args.source_pred).read_text(encoding="utf-8"))
    n = json.loads(Path(args.native).read_text(encoding="utf-8"))
    m = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result = compare(p, n, m)
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True)+"\n",
                              encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
