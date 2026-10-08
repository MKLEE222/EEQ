#!/usr/bin/env python3
"""Prospective synthetic downstream legal-path recovery for quotient-v2.

Direct trace oracle is independent of the quotient implementation. This is a
development proof of feasibility, NOT per-native-family G8 downstream evidence.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from finite_contract_quotient_v2 import FiniteContractModel
from independent_trace_oracle import trace_signature, check_partition
from test_finite_contract_quotient_v2 import fixture


def status(view, contract, action):
    rows = [v[2] for v in view if v[0] == contract and v[1] == action]
    if len(rows) != 1:
        raise AssertionError("missing registered challenge")
    return rows[0]


def legal_paths(model, state_id, horizon, contract, decision_action):
    views = trace_signature(model, state_id, horizon)
    return {tuple(prefix) for prefix, view in views
            if status(view, contract, decision_action) == "ACCEPT"}


def audit():
    p = fixture()
    machine = FiniteContractModel(p)
    horizon = 1
    full = machine.run(horizon, witness_limit=50)
    snapshot = machine.run(0, witness_limit=50)
    check_partition(p, full)
    ids = sorted(s["id"] for s in p["states"])
    direct = {sid: legal_paths(p, sid, horizon, "contractA", "inspect") for sid in ids}

    comparisons = {}
    for name, q in (("finite_future_quotient", full), ("current_only_ablation", snapshot)):
        members = {}
        for sid, cls in q["class_of"].items():
            members.setdefault(cls, []).append(sid)
        representative = {cl: min(names) for cl, names in members.items()}
        exact_states = 0
        misses = []
        false_accepts = 0
        false_rejects = 0
        for sid in ids:
            rep = representative[q["class_of"][sid]]
            expected = direct[sid]
            got = direct[rep]
            if expected == got:
                exact_states += 1
            else:
                misses.append({
                    "state": sid,
                    "representative": rep,
                    "missing_legal_paths": [list(x) for x in sorted(expected-got)],
                    "spuriously_legal_paths": [list(x) for x in sorted(got-expected)],
                })
                false_rejects += len(expected-got)
                false_accepts += len(got-expected)
        comparisons[name] = {
            "classes": q["quotient_class_count"],
            "exact_legal_path_sets": exact_states,
            "total_states": len(ids),
            "false_accept_paths": false_accepts,
            "false_reject_paths": false_rejects,
            "errors": misses,
        }
    if comparisons["finite_future_quotient"]["exact_legal_path_sets"] != len(ids):
        raise AssertionError("future quotient failed legal path recovery")
    if comparisons["current_only_ablation"]["exact_legal_path_sets"] == len(ids):
        raise AssertionError("synthetic downstream fixture was non-diagnostic")
    return {
        "schema": "eeq-quotient-v2-synthetic-downstream-path-recovery",
        "evidence_class": "SYNTHETIC",
        "status": "DEVELOPMENT_ONLY_NOT_NATIVE_G8_CLOSURE",
        "challenge": {"registered_contract": "contractA", "decision_action": "inspect",
                      "future_action_prefix_horizon": horizon},
        "independent_direct_trace_oracle": "PASS",
        "no_native_label_used": True,
        "comparisons": comparisons,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    report = audit()
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True)+"\n",
                              encoding="utf-8")
    print(json.dumps(report["comparisons"], sort_keys=True))


if __name__ == "__main__":
    main()
