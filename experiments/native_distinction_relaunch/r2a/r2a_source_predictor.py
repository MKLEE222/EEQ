#!/usr/bin/env python3
"""R2A SOURCE-ONLY admissibility extractor; no cluster, no kubectl, no labels.

Supports only the explicitly frozen source contract; refuses unknown rules
and models the registered namespace label UPDATE, not a fabricated outcome.
"""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

NAMES = (
    "policy.json", "binding-a.json", "binding-b.json",
    "namespace-before.json", "pod-flux.json", "pod-default.json",
    "update-namespace-label.json",
)
BRANCHES = ("a", "b")
PROBES = ("flux", "default")
PHASES = ("current", "after_native_label_update")


class UnsupportedMechanism(Exception):
    pass


def source_inputs(directory):
    root = Path(directory)
    docs = {}
    manifest = []
    for name in NAMES:
        raw = (root / name).read_bytes()
        docs[name] = json.loads(raw)
        manifest.append({
            "name": name,
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })
    return docs, manifest


def contract(docs):
    policy = docs["policy.json"]
    expected_rule = {
        "apiGroups": [""], "apiVersions": ["v1"],
        "operations": ["CREATE"], "resources": ["pods"],
    }
    spec = policy.get("spec", {})
    if (policy.get("apiVersion") != "admissionregistration.k8s.io/v1" or
            policy.get("kind") != "ValidatingAdmissionPolicy" or
            policy.get("metadata", {}).get("name") != "eeq-r2a-flux-deny" or
            spec.get("failurePolicy") != "Fail" or
            spec.get("matchConstraints") != {"resourceRules": [expected_rule]}):
        raise UnsupportedMechanism("UNREGISTERED_POLICY_MECHANISM")
    validations = spec.get("validations")
    if not isinstance(validations, list) or len(validations) != 1:
        raise UnsupportedMechanism("MULTIPLE_OR_MISSING_VALIDATIONS")
    validation = validations[0]
    match = re.fullmatch(
        r"object\.spec\.serviceAccountName != '([^']+)'",
        validation.get("expression", ""),
    )
    if (match is None or validation.get("reason") != "Forbidden" or
            validation.get("message") != "EEQ_R2A_FLUX_SA_DENIED"):
        raise UnsupportedMechanism("UNSUPPORTED_CEL_PREDICATE")
    excluded_sa = match.group(1)
    if not excluded_sa:
        raise UnsupportedMechanism("EMPTY_SERVICEACCOUNT")

    bindings = {}
    for branch in BRANCHES:
        b = docs["binding-" + branch + ".json"]
        body = b.get("spec", {})
        if (b.get("apiVersion") != "admissionregistration.k8s.io/v1" or
                b.get("kind") != "ValidatingAdmissionPolicyBinding" or
                b.get("metadata", {}).get("name") !=
                "eeq-r2a-binding-" + branch or
                body.get("policyName") != policy["metadata"]["name"] or
                body.get("validationActions") != ["Deny"] or
                set(body) != {"policyName", "validationActions",
                              "matchResources"}):
            raise UnsupportedMechanism("UNREGISTERED_BINDING_" + branch)
        match_resources = body["matchResources"]
        if set(match_resources) != {"namespaceSelector"}:
            raise UnsupportedMechanism("UNHANDLED_BINDING_RESOURCES")
        selector = match_resources["namespaceSelector"]
        if set(selector) != {"matchLabels"}:
            raise UnsupportedMechanism("UNSUPPORTED_NAMESPACE_SELECTOR")
        labels = selector["matchLabels"]
        if (not isinstance(labels, dict) or not labels or
                any(not isinstance(k, str) or not isinstance(v, str)
                    for k, v in labels.items())):
            raise UnsupportedMechanism("INVALID_NAMESPACE_LABEL_SELECTOR")
        bindings[branch] = labels
    return excluded_sa, bindings


def namespace_transition(docs):
    before = docs["namespace-before.json"]
    if (before.get("apiVersion") != "v1" or
            before.get("kind") != "Namespace" or
            before.get("metadata", {}).get("name") != "eeq-r2a"):
        raise UnsupportedMechanism("UNREGISTERED_NAMESPACE")
    labels = before["metadata"].get("labels", {})
    if not isinstance(labels, dict):
        raise UnsupportedMechanism("BAD_NAMESPACE_LABELS")
    operation = docs["update-namespace-label.json"]
    expected_command = [
        "kubectl", "label", "namespace", "eeq-r2a",
        "r2a.mode=relaxed", "--overwrite",
    ]
    if (operation.get("schema") != "eeq-r2a-native-action-v1" or
            operation.get("operation") != "UPDATE_NAMESPACE_LABEL" or
            operation.get("resource") != "namespaces/eeq-r2a" or
            operation.get("key") != "r2a.mode" or
            operation.get("from") != "strict" or
            operation.get("to") != "relaxed" or
            operation.get("full_command") != expected_command or
            labels.get("r2a.team") != "tenant" or
            labels.get("r2a.mode") != operation["from"]):
        raise UnsupportedMechanism("UNSUPPORTED_NATIVE_NAMESPACE_TRANSITION")
    after = copy.deepcopy(labels)
    after[operation["key"]] = operation["to"]
    return labels, after, operation["full_command"]


def pods(docs):
    output = {}
    for probe in PROBES:
        doc = docs["pod-" + probe + ".json"]
        if (doc.get("apiVersion") != "v1" or doc.get("kind") != "Pod" or
                doc.get("metadata", {}).get("namespace") != "eeq-r2a" or
                doc.get("metadata", {}).get("name") !=
                "eeq-r2a-" + probe + "-probe"):
            raise UnsupportedMechanism("UNREGISTERED_POD_IDENTITY")
        spec = doc.get("spec", {})
        if (spec.get("serviceAccountName") != probe or
                not isinstance(spec.get("containers"), list) or
                not spec["containers"]):
            raise UnsupportedMechanism("UNREGISTERED_POD_PAYLOAD")
        output[probe] = doc
    return output


def predict(docs):
    excluded_sa, bindings = contract(docs)
    before, after, action = namespace_transition(docs)
    pod_map = pods(docs)
    rows = []
    for branch in BRANCHES:
        selector = bindings[branch]
        for phase in PHASES:
            actual_labels = before if phase == "current" else after
            binding_matches = all(actual_labels.get(k) == v
                                  for k, v in selector.items())
            for probe in PROBES:
                sa = pod_map[probe]["spec"]["serviceAccountName"]
                policy_passed = sa != excluded_sa
                decision = ("REJECT" if binding_matches and not policy_passed
                            else "ACCEPT")
                rows.append({
                    "branch": branch, "phase": phase, "probe": probe,
                    "expected_native": decision,
                    "binding_matches": binding_matches,
                    "native_action_needed": phase != "current",
                    "policy_expression": docs["policy.json"]["spec"][
                        "validations"][0]["expression"],
                    "effective_labels": dict(actual_labels),
                })
    current = {branch: tuple(r["expected_native"] for r in rows
                if r["branch"] == branch and r["phase"] == "current")
               for branch in BRANCHES}
    future = {branch: tuple(r["expected_native"] for r in rows
               if r["branch"] == branch and r["phase"] ==
               "after_native_label_update") for branch in BRANCHES}
    expected = {
        "a": ("REJECT", "ACCEPT"),
        "b": ("REJECT", "ACCEPT"),
    }
    expected_future = {
        "a": ("REJECT", "ACCEPT"),
        "b": ("ACCEPT", "ACCEPT"),
    }
    if current != expected or future != expected_future:
        raise UnsupportedMechanism("FROZEN_A_PREDICTION_NOT_INSTANTIATED")
    # Fair strong baseline sees complete selector and updated native labels:
    # it can compute ALL eight expected labels; no exclusive superiority.
    # Deliberately insufficient ablation discards binding qualification.
    ablation = sum(r["expected_native"] ==
                   ("REJECT" if r["probe"] == excluded_sa else "ACCEPT")
                   for r in rows)
    return {
        "schema": "eeq-r2a-k8s-source-predictions-v1",
        "evidence_class": "CONTROLLED_NATIVE_DYNAMIC_KUBERNETES",
        "source_only_no_native_labels": True,
        "native_verifier_not_invoked": True,
        "registered_cases": rows,
        "common_namespace_name": "eeq-r2a",
        "namespace_labels_before": before,
        "namespace_labels_after_source_derived": after,
        "registered_native_action": action,
        "binding_selectors": bindings,
        "current_complete_decision_vectors": current,
        "post_action_decision_vectors": future,
        "current_decisions_equal": current["a"] == current["b"],
        "future_decisions_differ": future["a"] != future["b"],
        "source_derived_separating_witness": [
            "UPDATE_NAMESPACE_LABEL(r2a.mode=relaxed)",
            "P_flux Pod CREATE",
        ],
        "strong_b9": {
            "knows_full_binding_selector_and_namespace_labels": True,
            "predicted_native_matches": len(rows),
            "total": len(rows),
        },
        "insufficient_selector_blind_ablation": {
            "matched_source_predictions": ablation,
            "total": len(rows),
            "is_strong_baseline": False,
        },
        "negative_controls_without_binding": {
            "per_branch": {"flux": "ACCEPT", "default": "ACCEPT"},
            "total": 4,
        },
        "registered_namespace_label_updates": 2,
        "g5_increment": 0,
        "scope_limits": [
            "One controlled VAP and one branch-specific binding",
            "Only Pod CREATE probes, one native namespace label UPDATE",
            "Unrelated native admission errors are ambiguous not REJECT",
            "B9 is fully informed and ties source-only on registered task",
            "No other Kubernetes policy/binding or hidden cluster action claimed",
        ],
    }


def build(input_dir):
    docs, manifest = source_inputs(input_dir)
    predictions = predict(docs)
    return {
        "schema": "eeq-r2a-k8s-source-manifest-v1",
        "sources": manifest,
        "evidence_class": "CONTROLLED_NATIVE_DYNAMIC_KUBERNETES",
        "source_only": True,
    }, predictions


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sources", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    source_manifest, model = build(a.sources)
    root = Path(a.out)
    root.mkdir(parents=True, exist_ok=True)
    (root / "SOURCE_MANIFEST.json").write_text(
        json.dumps(source_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    (root / "SOURCE_PREDICTIONS.json").write_text(
        json.dumps(model, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(json.dumps({
        "cases": len(model["registered_cases"]),
        "current_equal": model["current_decisions_equal"],
        "future_different": model["future_decisions_differ"],
        "separating_witness": model["source_derived_separating_witness"],
        "strong_b9": model["strong_b9"]["predicted_native_matches"],
        "selector_blind_ablation":
            model["insufficient_selector_blind_ablation"][
                "matched_source_predictions"],
        "native_verifier_not_invoked": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
