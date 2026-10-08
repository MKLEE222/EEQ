#!/usr/bin/env python3
"""No-label audit of whether v1 adapter instances can feed finite quotient v2.

A symbolic successor descriptor is not assumed to be a total transition graph.
This audits v2 model *liftability* only; no native or G4 scoring is performed.
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def check_domain(rows):
    semantic_ids = {x["semantic_id"] for x in rows}
    results = []
    for row in rows:
        a = row["adapter"]
        c1 = a.get("C1_support_coverage") or {}
        c2 = a.get("C2_qualification_fidelity") or {}
        c3 = a.get("C3_transition_objective_fidelity") or {}
        actions = c3.get("actions") or []
        faults = []
        machine_actions = (isinstance(actions, list) and bool(actions) and
                           all(type(a) is str and a for a in actions) and
                           len(set(actions)) == len(actions))
        if not machine_actions:
            faults.append("ACTION_ALPHABET_NEEDS_MACHINE_NORMALIZATION")
        if not isinstance(c1.get("support_items"), list) or \
           not isinstance(c1.get("compatibility"), list):
            faults.append("C1_SOURCE_COVERAGE_NOT_EXPLICIT")
        if not isinstance(c2.get("qualification_predicates"), list) or \
           not isinstance(c2.get("claim_binding"), list):
            faults.append("C2_BINDING_NOT_EXPLICIT")
        if "continuation_contract" not in c3:
            faults.append("C3_CONTINUATION_NOT_DECLARED")

        successor = c3.get("successor_relation")
        # A per-case semantic descriptor alone does not allow deterministic
        # finite-state partition refinement. Require explicit semantic IDs.
        transitions = (successor.get("transitions") if isinstance(successor, dict)
                       else None)
        if not machine_actions or not isinstance(transitions, dict) or set(transitions) != set(actions):
            faults.append("C3_TOTAL_GRAPH_NOT_AVAILABLE")
        elif not all(type(transitions[action]) is str and
                     transitions[action] in semantic_ids
                     for action in actions):
            faults.append("C3_GRAPH_NOT_CLOSED_WITHIN_REGISTERED_DOMAIN")

        results.append({
            "semantic_id": row["semantic_id"],
            "liftable_as_is": not faults,
            "unresolved": sorted(set(faults)),
        })
    return {
        "rows": len(rows),
        "liftable_as_is": sum(x["liftable_as_is"] for x in results),
        "fault_counts": dict(sorted(Counter(y for x in results for y in x["unresolved"]).items())),
        "sample_failures": [x for x in results if x["unresolved"]][:5],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapters", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    by_domain = defaultdict(list)
    for file in args.adapters:
        data = load(file)
        for row in data["rows"]:
            # Deliberate narrow projection: do not access any scored outcome.
            projected = {k:row[k] for k in ("semantic_id", "domain", "adapter")}
            by_domain[projected["domain"]].append(projected)
    audit = {domain: check_domain(rows) for domain, rows in sorted(by_domain.items())}
    payload = {
        "schema": "eeq-quotient-v2-no-label-native-liftability",
        "scope": "existing frozen v1 adapters only",
        "total_cases": sum(x["rows"] for x in audit.values()),
        "directly_liftable": sum(x["liftable_as_is"] for x in audit.values()),
        "native_decision_labels_consumed": False,
        "g4_v1_results_unchanged": True,
        "disposition": "DIRECT_NATIVE_V2_GRAPH_SUPPORTED"
        if all(x["liftable_as_is"] == x["rows"] for x in audit.values())
        else "V2_NATIVE_GRAPH_EXTRACTION_REMAINS_OPEN",
        "domains": audit,
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True)+"\n")
    print(json.dumps({
        "total_cases": payload["total_cases"],
        "directly_liftable": payload["directly_liftable"],
        "disposition": payload["disposition"],
        "domain_faults": {k:v["fault_counts"] for k,v in audit.items()},
    }, sort_keys=True))


if __name__ == "__main__":
    main()
