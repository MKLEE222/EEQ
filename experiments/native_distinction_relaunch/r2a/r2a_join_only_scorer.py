#!/usr/bin/env python3
"""R2A join-only frozen source-vs-native scorer, no native command execution.

Always preserve all eight registered Pod observations, four unbound controls
and both native namespace UPDATE certificates. Fail closed on ambiguity.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

BRANCHES = ("a", "b")
PHASES = ("current", "after_native_label_update")
PROBES = ("flux", "default")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique(rows, key_fn):
    d = {}
    for r in rows:
        k = key_fn(r)
        require(k not in d, "DUPLICATE_NATIVE_CASE_" + str(k))
        d[k] = r
    return d


def score(pred, manifest, results):
    require(pred.get("schema") == "eeq-r2a-k8s-source-predictions-v1",
            "UNFROZEN_SOURCE_SCHEMA")
    require(manifest.get("schema") == "eeq-r2a-k8s-source-manifest-v1",
            "UNFROZEN_MANIFEST_SCHEMA")
    source_hashes = {x["name"]: x["sha256"] for x in manifest["sources"]}
    require(len(source_hashes) == 7, "MISSING_REGISTERED_SOURCES")
    expected = unique(pred["registered_cases"], lambda r: (
        r["branch"], r["phase"], r["probe"]))
    full_cases = {(b, p, q) for b in BRANCHES
                  for p in PHASES for q in PROBES}
    require(set(expected) == full_cases and len(expected) == 8,
            "INCOMPLETE_PREDICTION_EIGHT_CASES")
    require(pred["source_only_no_native_labels"] is True,
            "SOURCE_PREDICTIONS_CONSUMED_NATIVE")
    require(pred["strong_b9"]["predicted_native_matches"] == 8,
            "UNFAIR_STRONG_B9_INPUT_SCOPE")

    require(set(results) == set(BRANCHES), "NATIVE_BRANCH_MISSING")
    observed_cases, controls, actions = [], [], []
    contexts = set()
    for branch in BRANCHES:
        r = results[branch]
        require(r["schema"] == "eeq-r2a-native-k8s-dynamic-branch-v1",
                "BAD_NATIVE_RESULT_SCHEMA")
        require(r["branch"] == branch, "MIXED_NATIVE_BRANCH")
        require(r["native_predictions_file_read"] is False,
                "NATIVE_VERIFIER_READ_PREDICTIONS")
        require(r["source_digest_map"] == source_hashes,
                "NATIVE_SOURCE_HASH_MISMATCH")
        require(r["source_binding_selector"] ==
                pred["binding_selectors"][branch] and
                r["native_observed_binding_selector"] ==
                pred["binding_selectors"][branch],
                "NATIVE_BINDING_SELECTOR_MISMATCH")
        context = r["native_cluster_context"]
        require(context and context not in contexts,
                "NON_INDEPENDENT_NATIVE_KIND_CLUSTERS")
        contexts.add(context)
        current_ns = r["native_current_namespace"]
        post_ns = r["native_post_action_namespace"]
        require(r["native_namespace_action_verified"] is True,
                "UNVERIFIED_ACTUAL_NAMESPACE_UPDATE")
        require(current_ns["uid"] == post_ns["uid"] and
                current_ns["resource_version"] != post_ns["resource_version"],
                "NATIVE_NAMESPACE_REVISION_NOT_CHANGED")
        require(current_ns["labels"].get("r2a.mode") == "strict" and
                post_ns["labels"].get("r2a.mode") == "relaxed" and
                current_ns["labels"].get("r2a.team") ==
                post_ns["labels"].get("r2a.team") == "tenant",
                "REAL_NAMESPACE_LABEL_ACTION_DID_NOT_OCCUR")
        action = r["namespace_label_action_command"]
        require(action["exit_code"] == 0,
                "NATIVE_NAMESPACE_LABEL_ACTION_FAILED")
        require(action["command"] ==
                pred["registered_native_action"],
                "UNREGISTERED_NATIVE_MUTATION_COMMAND")
        actions.append({
            "branch": branch,
            "native_context": context,
            "namespace_uid": current_ns["uid"],
            "before_revision": current_ns["resource_version"],
            "after_revision": post_ns["resource_version"],
            "native_action_verified": True,
        })

        controls_branch = unique(r["unbound_controls"], lambda x: x["probe"])
        require(set(controls_branch) == set(PROBES),
                "PREBINDING_NEGATIVE_CONTROL_MISSING")
        for probe in PROBES:
            item = controls_branch[probe]
            controls.append({
                "branch": branch, "probe": probe,
                "native": item["native"],
                "status": "MATCH" if item["native"] == "ACCEPT"
                          else "AMBIGUOUS_OR_MISMATCH",
            })
        native_cases = unique(
            r["current_probes"] + r["future_probes"],
            lambda x: (x["phase"], x["probe"]))
        require(set(native_cases) ==
                {(p, q) for p in PHASES for q in PROBES},
                "MISSING_NATIVE_CASE_IN_BRANCH_" + branch)
        for phase in PHASES:
            for probe in PROBES:
                e = expected[branch, phase, probe]
                o = native_cases[phase, probe]
                require(o["pod_source_sha256"] ==
                        source_hashes["pod-" + probe + ".json"],
                        "NATIVE_POD_SOURCE_HASH_MISMATCH")
                actual = o["native"]
                correct = actual == e["expected_native"] and (
                    (actual == "REJECT" and
                     o["native_attribution"] == "REGISTERED_VAP_DENY") or
                    (actual == "ACCEPT" and
                     o["native_attribution"] == "ADMITTED")
                )
                observed_cases.append({
                    "branch": branch, "phase": phase, "probe": probe,
                    "expected": e["expected_native"],
                    "native": actual,
                    "native_attribution": o["native_attribution"],
                    "status": "MATCH" if correct else
                              "AMBIGUOUS" if actual == "NATIVE_ORACLE_AMBIGUOUS"
                              else "MISMATCH",
                    "native_exit_code": o["exit_code"],
                })
    native_dict = unique(observed_cases, lambda r: (
        r["branch"], r["phase"], r["probe"]))
    current_a = tuple(native_dict["a","current",p]["native"] for p in PROBES)
    current_b = tuple(native_dict["b","current",p]["native"] for p in PROBES)
    future_a = tuple(native_dict["a","after_native_label_update",p]["native"]
                     for p in PROBES)
    future_b = tuple(native_dict["b","after_native_label_update",p]["native"]
                     for p in PROBES)
    witnessed_a = (
        current_a == current_b == ("REJECT","ACCEPT")
        and future_a == ("REJECT","ACCEPT")
        and future_b == ("ACCEPT","ACCEPT")
        and all(c["status"] == "MATCH" for c in observed_cases)
        and all(c["status"] == "MATCH" for c in controls)
    )
    statuses = Counter(row["status"] for row in observed_cases)
    strong_b9 = sum(row["native"] == row["expected"]
                    for row in observed_cases)
    return {
        "schema": "eeq-r2a-native-k8s-joined-source-action-result-v1",
        "scientific_disposition": (
            "CONTROLLED_K8S_NATIVE_ACTION_INDUCED_A_SPLIT_B9_TIE"
            if witnessed_a and strong_b9 == 8 else
            "R2A_NATIVE_MISMATCH_OR_SCOPE_FAILURE"
        ),
        "source_only_expected_before_action":
            pred["current_complete_decision_vectors"],
        "source_only_expected_after_action":
            pred["post_action_decision_vectors"],
        "native_current_vectors": {"a":current_a,"b":current_b},
        "native_future_vectors": {"a":future_a,"b":future_b},
        "all_eight_native_cases": observed_cases,
        "unbound_native_controls": controls,
        "native_real_namespace_action_certificates": actions,
        "summary": {
            "native_cases_registered": 8, "native_cases_match": statuses["MATCH"],
            "native_cases_mismatch": statuses["MISMATCH"],
            "native_cases_ambiguous": statuses["AMBIGUOUS"],
            "unbound_native_controls": 4,
            "unbound_native_controls_match":
                sum(c["status"] == "MATCH" for c in controls),
            "actual_native_label_updates": len(actions),
            "native_present_decisions_identical": current_a == current_b,
            "native_future_decisions_diverge": future_a != future_b,
            "native_action_induced_a_witness_verified": witnessed_a,
            "strong_b9_native_matches": strong_b9,
            "strong_b9_native_total": 8,
            "insufficient_selector_blind_ablation_source_matches":
                pred["insufficient_selector_blind_ablation"][
                    "matched_source_predictions"],
            "no_b9_unique_advantage_claim": True,
            "evidence_class": "CONTROLLED_NATIVE_DYNAMIC_KUBERNETES",
            "original_g5_increment": 0,
            "r2_a_and_b_in_each_family": False,
        }
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-manifest",required=True)
    p.add_argument("--source-pred",required=True)
    p.add_argument("--native-a",required=True)
    p.add_argument("--native-b",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    payloads=[
        json.loads(Path(p).read_text(encoding="utf-8"))
        for p in (a.source_pred,a.source_manifest,a.native_a,a.native_b)
    ]
    pred,manifest,native_a,native_b=payloads
    result=score(pred,manifest,{"a":native_a,"b":native_b})
    Path(a.out).write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",
                           encoding="utf-8")
    print(json.dumps(result["summary"],sort_keys=True))


if __name__=="__main__":
    main()
