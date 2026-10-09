#!/usr/bin/env python3
"""Join-only, denominator-preserving R2-B source-predictions/native scorer.

Does not import a predictor, a native verifier or any result-fitting logic.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

ACTIONS = ("submit-candidate-2", "submit-candidate-3")
INITIALS = ("A", "B")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def expected_paths():
    return ((), *((a,) for a in ACTIONS),
            *((a, b) for a in ACTIONS for b in ACTIONS))


def validate_rows(rows):
    expected = {(i, p) for i in INITIALS for p in expected_paths()}
    out = {}
    for row in rows:
        k = (row["initial_state"], tuple(row["prefix"]))
        if k in out:
            raise ValueError("DUPLICATE_PREFIX_ROW")
        out[k] = row
    if set(out) != expected:
        raise ValueError("UNREGISTERED_OR_MISSING_PREFIX")
    return out


def compare(pred, native, manifest):
    if pred["schema"] != "eeq-r2b-source-only-predictions-v1":
        raise ValueError("WRONG_PREDICTION_SCHEMA")
    if native["schema"] != "eeq-r2b-independent-native-tuf-v1":
        raise ValueError("WRONG_NATIVE_SCHEMA")
    if manifest["schema"] != "eeq-r2b-controlled-sources-v1":
        raise ValueError("WRONG_SOURCE_MANIFEST_SCHEMA")
    if tuple(pred["registered_actions"]) != ACTIONS:
        raise ValueError("FROZEN_ACTIONS_CHANGED")
    if tuple(native["fixed_actions"]) != ACTIONS:
        raise ValueError("NATIVE_ACTIONS_CHANGED")
    if pred["horizon"] != native["fixed_horizon"] != 2:
        raise ValueError("FROZEN_HORIZON_CHANGED")
    if native["source_only_predictions_never_read"] is not True:
        raise ValueError("NATIVE_ORACLE_NOT_INDEPENDENT")

    # Canonical signed source digests bridge exact public source provenance to
    # the store's decoded native root. No scored labels or features involved.
    canonical_by_raw = {
        f["sha256"]: f["signed_canonical_sha256"]
        for f in manifest["files"]
    }
    ps = validate_rows(pred["rows"])
    ns = validate_rows(native["rows"])
    audit = []
    observed_word_vectors = {"A": {}, "B": {}}

    for initial in INITIALS:
        for prefix in expected_paths():
            p, n = ps[(initial, prefix)], ns[(initial, prefix)]
            row_errors = []
            state_raw = p["state_after_prefix_source_sha256"]
            predicted_canonical = canonical_by_raw.get(state_raw)
            if predicted_canonical is None:
                raise ValueError("UNPINNED_POST_PREFIX_SOURCE")
            observed_canonical = (n.get("post_prefix_state") or {}).get(
                "canonical_signed_sha256")
            if not n.get("prefix_completed") or n.get("setup_error"):
                row_errors.append("PREFIX_NATIVE_SETUP_OR_EXECUTION_FAILED")
            elif observed_canonical != predicted_canonical:
                row_errors.append("POST_PREFIX_TRUSTED_SOURCE_MISMATCH")

            pre = p["prefix_effects"]
            native_pre = n.get("prefix_trace") or []
            if len(pre) != len(native_pre):
                row_errors.append("PREFIX_LENGTH_MISMATCH")
            else:
                for expected, got in zip(pre, native_pre):
                    wanted = ("ACCEPT" if expected["effect"] == "ADVANCE_TRUST_ROOT"
                              else "REJECT")
                    if got["action"] != expected["action"] or (
                        got["native_outcome"] != wanted
                    ):
                        row_errors.append("PREFIX_NATIVE_EFFECT_MISMATCH")
                        break

            p_ch = {x["action"]: x for x in p["continuation"]}
            n_ch = {x["action"]: x for x in n["challenges"]}
            if set(p_ch) != set(ACTIONS) or set(n_ch) != set(ACTIONS):
                raise ValueError("MISSING_OR_ADDED_REGISTERED_CHALLENGE")
            vector = []
            for action in ACTIONS:
                expected = p_ch[action]
                observed = n_ch[action]
                exp_action = ("ACCEPT" if expected["effect"] == "ADVANCE_TRUST_ROOT"
                              else "REJECT" if expected["effect"] == "KEEP_TRUST_ROOT"
                              else "MODEL_UNSUPPORTED")
                raw_dest = expected["to_source_sha256"]
                expected_hash = canonical_by_raw.get(raw_dest)
                if expected_hash is None:
                    raise ValueError("UNPINNED_PREDICTED_NEXT_SOURCE")
                result = observed.get("native_decision") or {}
                actual_action = result.get("native_outcome", "SETUP_FAILURE")
                actual_state_hash = (result.get("after") or {}).get(
                    "canonical_signed_sha256")
                matches = (exp_action != "MODEL_UNSUPPORTED" and
                           actual_action == exp_action and
                           actual_state_hash == expected_hash and
                           observed.get("replay_setup_ok") is True)
                status = ("MATCH" if matches else
                          "MODEL_UNSUPPORTED" if exp_action == "MODEL_UNSUPPORTED"
                          else "NATIVE_MISMATCH_OR_SETUP_FAILURE")
                vector.append(actual_action)
                audit.append({
                    "initial_state": initial,
                    "action_prefix": list(prefix),
                    "challenge_action": action,
                    "expected": exp_action,
                    "observed": actual_action,
                    "expected_next_canonical_signed_sha256": expected_hash,
                    "actual_next_canonical_signed_sha256": actual_state_hash,
                    "status": status,
                    "decision_ns": result.get("decision_ns"),
                    "error": result.get("error"),
                    "prefix_errors": row_errors,
                })
            observed_word_vectors[initial][prefix] = tuple(vector)

    target_expected = {
        (i, t): (pred["targets_role_qualification"][i][t]["qualified"])
        for i in INITIALS for t in ("TARGETS_A", "TARGETS_B")
    }
    target_observed = {}
    for row in native["target_authorizations"]:
        key = (row["initial_state"], row["target_document"])
        if key in target_observed:
            raise ValueError("DUPLICATE_NATIVE_TARGET_AUTHORIZATION")
        target_observed[key] = row
    if set(target_expected) != set(target_observed):
        raise ValueError("TARGET_ROLE_CROSS_MATRIX_INCOMPLETE")
    targets = []
    for key in sorted(target_expected):
        observed = target_observed[key]
        actual = observed["native_role_authority_status"]
        expected = "QUALIFIED" if target_expected[key] else "UNQUALIFIED"
        targets.append({
            "initial_state": key[0],
            "target_document": key[1],
            "predicted_qualified": expected,
            "native_qualified": actual,
            "status": "MATCH" if actual == expected else "MISMATCH",
            "error": observed.get("error"),
        })

    equivalence = all(
        observed_word_vectors["A"][p] == observed_word_vectors["B"][p]
        for p in expected_paths()
    )
    cells = Counter(x["status"] for x in audit)
    target_counts = Counter(x["status"] for x in targets)
    no_prefix_errors = sum(bool(x["prefix_errors"]) for x in audit) == 0
    all_good = (cells.get("MATCH", 0) == 28 and target_counts.get("MATCH", 0) == 4
                and no_prefix_errors and equivalence)
    return {
        "schema": "eeq-r2b-pinned-source-vs-independent-native-v1",
        "evidence_class": "CONTROLLED_NATIVE_DEVELOPMENT",
        "status": ("CONTROLLED_NATIVE_B_CONFIRMED_B9_TIE"
                   if all_good else "CONTROLLED_NATIVE_B_REJECTED_OR_INCOMPLETE"),
        "summary": {
            "registered_initial_states": 2,
            "prefixes_per_state": 7,
            "native_challenge_cells": 28,
            "native_root_update_matches": cells.get("MATCH", 0),
            "native_root_update_nonmatches": 28-cells.get("MATCH", 0),
            "native_targets_authority_cells": 4,
            "native_targets_role_matches": target_counts.get("MATCH", 0),
            "native_targets_role_nonmatches": 4-target_counts.get("MATCH", 0),
            "unresolved_prefix_cells": sum(bool(x["prefix_errors"]) for x in audit),
            "complete_future_trace_equivalence": equivalence,
            "strong_b9_tie_predeclared": True,
            "classical_quotient_tie_predeclared": True,
            "novelty_advantage_established": False,
            "R2_A_future_separation_demonstrated": False,
            "R2_FULL_GATE_PASS": False,
        },
        "root_action_comparisons": audit,
        "targets_authority_comparisons": targets,
        "old_G4_unchanged": True,
        "new_G5_cases": 0,
        "no_prospective_holdout_claim": True,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pred", required=True)
    p.add_argument("--native", required=True)
    p.add_argument("--source-manifest", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    payload = compare(read(a.pred), read(a.native), read(a.source_manifest))
    Path(a.out).write_text(json.dumps(payload, sort_keys=True, indent=2)+"\n",
                           encoding="utf-8")
    print(json.dumps(payload["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
