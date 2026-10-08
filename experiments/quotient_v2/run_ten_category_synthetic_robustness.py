#!/usr/bin/env python3
"""Execute ten previously frozen synthetic robustness perturbations.

The independent reference oracle computes each response directly from the
declared source/contract model. This is NOT cross-family native robustness.
"""
import argparse
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from finite_contract_quotient_v2 import FiniteContractModel
from independent_trace_oracle import trace_signature, check_partition
from test_finite_contract_quotient_v2 import fixture


SCENARIOS = [
    (1, "client_server_version", "PRESERVE_DECISION", "ACCEPT"),
    (2, "stale_prior_evidence", "RECOMPILE_THEN_DECIDE", "REJECT"),
    (3, "missing_noncritical_metadata", "PRESERVE_DECISION", "ACCEPT"),
    (4, "missing_critical_authorization", "INSUFFICIENT_EVIDENCE_REFUSE", "REFUSE"),
    (5, "corrupt_authentication", "RECOMPILE_THEN_DECIDE", "REJECT"),
    (6, "source_unavailable", "INSUFFICIENT_EVIDENCE_REFUSE", "REFUSE"),
    (7, "authority_rotation", "RECOMPILE_THEN_DECIDE", "REJECT"),
    (8, "tighten_contract", "RECOMPILE_THEN_DECIDE", "REJECT"),
    (9, "loosen_contract", "RECOMPILE_THEN_DECIDE", "ACCEPT"),
    (10, "stale_observation_quarantine", "INSUFFICIENT_EVIDENCE_REFUSE", "REFUSE"),
]


def decide_independently(payload):
    sig = trace_signature(payload, "A", 0)[0][1]
    answers = [d for c, a, d in sig if c == "contractA" and a == "inspect"]
    if len(answers) != 1:
        raise AssertionError("registered challenge missing")
    return answers[0]


def scenario(number):
    before = fixture()
    if number == 7:
        before["contracts"][0]["source_restriction"] = ["sourceA"]
    if number == 9:
        before["contracts"][0]["min_qualified_sources"] = 2
    after = copy.deepcopy(before)
    s = after["states"][0]
    support = s["support_items"][0]
    contract = after["contracts"][0]
    if number == 1:
        s["decoration_not_in_registered_contract"] = "client=v8 server=v99"
    elif number == 2:
        support["qualified"] = False
    elif number == 3:
        s.pop("decoration_not_in_registered_contract", None)
    elif number == 4:
        support["authorized"] = None
    elif number == 5:
        support["authenticated"] = False
    elif number == 6:
        s["support_items"] = []
        s["source_inventory_complete"] = False
    elif number == 7:
        support["source_identity"] = "sourceB"
    elif number == 8:
        contract["min_qualified_sources"] = 2
    elif number == 9:
        contract["min_qualified_sources"] = 1
    elif number == 10:
        support["qualified"] = None
    else:
        raise ValueError(number)
    return before, after


def run_all():
    results = []
    for number, name, response, frozen_after in SCENARIOS:
        before, after = scenario(number)
        old = decide_independently(before)
        new = decide_independently(after)
        if new != frozen_after:
            raise AssertionError((number, name, "wrong outcome", frozen_after, new))
        if response == "PRESERVE_DECISION":
            if new != old:
                raise AssertionError((name, "must preserve"))
        elif response == "INSUFFICIENT_EVIDENCE_REFUSE":
            if new != "REFUSE":
                raise AssertionError((name, "must refuse"))
        elif response == "RECOMPILE_THEN_DECIDE":
            if old == new:
                raise AssertionError((name, "must change under perturbation"))
        else:
            raise AssertionError((number, "unknown response"))
        a = FiniteContractModel(before).run(1)
        b = FiniteContractModel(after).run(1)
        qa = check_partition(before, a)
        qb = check_partition(after, b)
        if response == "PRESERVE_DECISION" and a["class_of"] != b["class_of"]:
            raise AssertionError((name, "irrelevant metadata changed quotient"))
        results.append({
            "category": number,
            "name": name,
            "predicted_response": response,
            "before_decision": old,
            "predicted_after_decision": frozen_after,
            "observed_after_decision_direct_oracle": new,
            "before_classes": a["quotient_class_count"],
            "after_classes": b["quotient_class_count"],
            "independent_oracle_before": qa,
            "independent_oracle_after": qb,
            "status": "PASS",
        })
    return {
        "schema": "eeq-quotient-v2-ten-category-synthetic-robustness",
        "evidence_class": "SYNTHETIC",
        "frozen_categories": 10,
        "executed_categories": len(results),
        "matched": sum(x["status"] == "PASS" for x in results),
        "mismatches": 0,
        "native_robustness_claim": False,
        "g8_original_protocol_closed": False,
        "results": results,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    a = p.parse_args()
    result = run_all()
    Path(a.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"categories": result["executed_categories"],
                      "matched": result["matched"],
                      "evidence_class": result["evidence_class"]}, sort_keys=True))


if __name__ == "__main__":
    main()
