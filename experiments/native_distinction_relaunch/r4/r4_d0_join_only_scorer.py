#!/usr/bin/env python3
"""R4-D0 fixed join-only eight-cell scorer; no TUF native/extractor calls.

Intentionally preserves all source/native mismatches. Validity of a
post-state is checked by the native signer's signature-envelope identity,
not just root version or candidate signed-body hash.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

STATES = ("s2a", "s2b")
ACTIONS = (
    "submit-root-3-a", "submit-root-3-b",
    "submit-root-3-old-only", "submit-root-3-new-only",
)


def require(cond, why):
    if not cond:
        raise ValueError(why)


def unique(rows, key):
    result = {}
    for row in rows:
        k = key(row)
        require(k not in result, "DUPLICATE_ROW_" + str(k))
        result[k] = row
    return result


def compare(pred, manifest, native):
    require(pred.get("schema") == "eeq-r4-d0-source-only-prediction-v1",
            "SOURCE_PREDICTION_SCHEMA_MISMATCH")
    require(manifest.get("schema") == "eeq-r4-d0-source-manifest-v1",
            "SOURCE_MANIFEST_SCHEMA_MISMATCH")
    require(native.get("schema") == "eeq-r4-d0-tuf-native-auth-contrast-v1",
            "NATIVE_RESULT_SCHEMA_MISMATCH")
    require(pred["native_outcomes_read"] is False and
            pred["native_oracle_invoked"] is False and
            native["source_predictions_read"] is False,
            "PREDICTION_NATIVE_LABEL_CONTAMINATION")
    require(pred["original_g5_increment"] == 0 and
            native["original_g5_increment"] == 0,
            "ORIGINAL_G5_PROTOCOL_TAMPER")
    sources = {x["name"]: x["sha256"] for x in manifest["sources"]}
    require(len(sources) == len(manifest["sources"]) == 7,
            "SOURCE_MANIFEST_INCOMPLETE")
    ps = unique(pred["predictions"], lambda x: (x["state"], x["action"]))
    ns = unique(native["native_rows"], lambda x: (x["state"], x["action"]))
    expected = {(s, a) for s in STATES for a in ACTIONS}
    require(set(ps) == expected and set(ns) == expected and
            native["registered_cells"] == 8, "NATIVE_GRID_CASES_MISSING")
    require(tuple(native["states"]) == STATES and
            tuple(native["actions"]) == ACTIONS, "NATIVE_GRID_REORDERED")
    setups = unique(native["setup_controls"], lambda x: x["state"])
    require(set(setups) == set(STATES), "NATIVE_SETUP_CONTROLS_MISSING")
    srcstates = unique(pred["states"], lambda x: x["state"])
    actions = unique(pred["candidates"], lambda x: x["action"])
    require(set(srcstates) == set(STATES) and set(actions) == set(ACTIONS),
            "REGISTERED_PREDICTION_SCOPE_CHANGED")

    setup_checks = []
    for state in STATES:
        n = setups[state]
        expected_file = srcstates[state]["source_file"]
        good = (n.get("result") == "PASS" and
                n.get("native_source_name") == expected_file and
                n.get("setup_source_sha256") == sources[expected_file] and
                n.get("native_version") == 2 and
                bool(n.get("native_metadata_identity")))
        setup_checks.append({
            "state": state, "native_source": n.get("native_source_name"),
            "native_error": n.get("error"),
            "status": "MATCH" if good else "SETUP_FAILURE",
        })

    cases = []
    for state in STATES:
        for action in ACTIONS:
            p, n = ps[state, action], ns[state, action]
            sfile = srcstates[state]["source_file"]
            afile = actions[action]["source_file"]
            correct_source = (
                p["initial_source_sha256"] == sources[sfile] ==
                    n["state_source_sha256"] and
                p["candidate_source_sha256"] == sources[afile] ==
                    n["candidate_source_sha256"] and
                n["state_setup_source"] == sfile and
                n["candidate_source"] == afile
            )
            require(correct_source, "NATIVE_SOURCE_FILE_HASH_MISMATCH_" +
                    state + "_" + action)
            expected_native = p["native_expected"]
            if n.get("setup_error") or n.get("native_outcome") == "SETUP_FAILURE":
                status = "SETUP_FAILURE"
            elif expected_native == "MODEL_UNSUPPORTED":
                status = "PREDICTOR_UNSUPPORTED"
            elif expected_native not in ("ACCEPT", "REJECT"):
                status = "BAD_PREDICTION_LABEL"
            else:
                expected_post_version = (
                    3 if expected_native == "ACCEPT" else 2
                )
                correct = (
                    n.get("native_outcome") == expected_native and
                    n.get("initial_native_source") == sfile and
                    n.get("initial_native_version") == 2 and
                    n.get("post_native_source") ==
                        p["expected_post_source_file"] and
                    n.get("post_native_version") == expected_post_version and
                    bool(n.get("initial_metadata_identity")) and
                    bool(n.get("post_metadata_identity")) and
                    ((n["initial_metadata_identity"] !=
                      n["post_metadata_identity"]) ==
                     (expected_native == "ACCEPT"))
                )
                status = "MATCH" if correct else "MISMATCH"
            cases.append({
                "state": state, "action": action,
                "expected_native": expected_native,
                "native_outcome": n.get("native_outcome"),
                "expected_post_source_file": p["expected_post_source_file"],
                "native_post_source_file": n.get("post_native_source"),
                "old_role_verified_signer_keyids":
                    p["old_authority"]["verified_unique_keyids"],
                "new_role_verified_signer_keyids":
                    p["new_authority"]["verified_unique_keyids"],
                "native_error": n.get("candidate_error"),
                "native_setup_error": n.get("setup_error"),
                "status": status,
            })

    hist = Counter(x["status"] for x in cases)
    sc = Counter(x["status"] for x in setup_checks)
    witness_a = (ps["s2a","submit-root-3-a"]["native_expected"] == "ACCEPT" and
                 ps["s2b","submit-root-3-a"]["native_expected"] == "REJECT" and
                 ns["s2a","submit-root-3-a"]["native_outcome"] == "ACCEPT" and
                 ns["s2b","submit-root-3-a"]["native_outcome"] == "REJECT")
    witness_b = (ps["s2a","submit-root-3-b"]["native_expected"] == "REJECT" and
                 ps["s2b","submit-root-3-b"]["native_expected"] == "ACCEPT" and
                 ns["s2a","submit-root-3-b"]["native_outcome"] == "REJECT" and
                 ns["s2b","submit-root-3-b"]["native_outcome"] == "ACCEPT")
    same_version_different_auth = (
        srcstates["s2a"]["root_version"] ==
        srcstates["s2b"]["root_version"] == 2 and
        srcstates["s2a"]["root_keyids"] !=
        srcstates["s2b"]["root_keyids"]
    )
    same_candidate_source_across_states = all(
        ps["s2a", action]["candidate_source_sha256"] ==
        ps["s2b", action]["candidate_source_sha256"] for action in ACTIONS
    )
    same_signed_body_all_candidates = len({
        actions[a]["signed_source_sha256"] for a in ACTIONS
    }) == 1
    for row in cases:
        require(row["old_role_verified_signer_keyids"] is not None and
                row["new_role_verified_signer_keyids"] is not None,
                "MISSING_CRYPTOGRAPHIC_SIGNER_PROOF")

    # Optimal VERSION + candidate-ID decoder, not the fully informed B9:
    # its maximum accuracy is computed post-native for diagnostic only.
    decoder_upper_bound = 0
    for action in ACTIONS:
        values = [ns[state, action].get("native_outcome") for state in STATES]
        if any(v not in ("ACCEPT", "REJECT") for v in values):
            continue
        decoder_upper_bound += max(values.count("ACCEPT"),
                                   values.count("REJECT"))
    fully_informed_b9_equivalent = hist.get("MATCH", 0)
    valid = (
        hist == Counter({"MATCH":8}) and
        sc == Counter({"MATCH":2}) and
        witness_a and witness_b and same_version_different_auth and
        same_candidate_source_across_states and
        same_signed_body_all_candidates and
        decoder_upper_bound == 6 and
        pred["strong_b9"]["prediction_matches"] == 8
    )
    summary = {
        "registered_native_cells": 8,
        "exact_native_cell_matches": hist["MATCH"],
        "native_mismatches": hist["MISMATCH"],
        "native_setup_failures": hist["SETUP_FAILURE"],
        "native_unknown_prediction": hist["PREDICTOR_UNSUPPORTED"],
        "registered_common_anchor_native_setups": 2,
        "successful_native_setups": sc["MATCH"],
        "same_version_different_authority": same_version_different_auth,
        "same_candidate_root3_bytes_across_states":
            same_candidate_source_across_states,
        "all_candidates_same_signed_root3_body":
            same_signed_body_all_candidates,
        "same_candidate_opposite_result_A": witness_a,
        "same_candidate_opposite_result_B": witness_b,
        "strong_fully_informed_B9_possible_exact_matches":
            fully_informed_b9_equivalent,
        "strong_fully_informed_B9_total": 8,
        "best_version_candidate_only_oracle_decoder_matches":
            decoder_upper_bound,
        "best_version_candidate_only_decoder_total": 8,
        "r4_P3_measured": False,
        "r4_independent_superiority_established": False,
        "original_g5_increment": 0,
        "scientific_status": (
            "R4_D0_NATIVE_VERSION_SUFFICIENCY_KILLED_STRONG_B9_TIE"
            if valid else "R4_D0_NATIVE_FAIL_OR_INCOMPLETE"
        ),
    }
    return {
        "schema": "eeq-r4-d0-pinned-source-native-join-v1",
        "summary": summary, "setup_controls": setup_checks,
        "all_eight_native_cases": cases,
        "interpretation": (
            "Domain version+candidate identity is not sufficient on this"
            " controlled contrast; fully informed protocol-native B9 can"
            " represent both signer qualifications without loss."
        ),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pred",required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--native",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    r=compare(*[json.loads(Path(f).read_text(encoding="utf-8"))
                for f in (a.pred,a.manifest,a.native)])
    Path(a.out).write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",
                           encoding="utf-8")
    print(json.dumps(r["summary"],sort_keys=True))


if __name__=="__main__":
    main()
