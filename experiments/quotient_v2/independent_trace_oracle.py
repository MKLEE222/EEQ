#!/usr/bin/env python3
"""Independent finite-trace oracle for quotient-v2 research tests.

Intentionally does NOT import the production quotient/refinement implementation.
It checks each pair against direct enumeration of all paths up to the frozen
horizon. Exponential by design: small-space oracle only.
"""
from __future__ import annotations
from itertools import combinations, product


def _route(support, claim):
    if claim not in support["compatible_claims"] or claim not in support["claim_binding"]:
        return False
    for field in ("authenticated", "authorized", "qualified"):
        if support[field] is False:
            return False
    for field in ("authenticated", "authorized", "qualified"):
        if support[field] is None:
            return None
    return True


def _status(state, contract, action):
    if action not in contract["allowed_actions"]:
        return "REJECT"
    definite, plausible = set(), set()
    restriction = set(contract["source_restriction"]) if "source_restriction" in contract else None
    for support in state["support_items"]:
        source = support["source_identity"]
        if restriction is not None and source not in restriction:
            continue
        q = _route(support, contract["claim"])
        if q is True:
            definite.add(source)
            plausible.add(source)
        elif q is None:
            plausible.add(source)
    k = contract["min_qualified_sources"]
    if len(definite) >= k:
        return "ACCEPT"
    if state["source_inventory_complete"] and len(plausible) < k:
        return "REJECT"
    return "REFUSE"


def _view(model, state, path):
    states = {s["id"]: s for s in model["states"]}
    for action in path:
        state = states[state]["transitions"][action]
    node = states[state]
    return tuple((c["id"], a, _status(node, c, a))
                 for c in sorted(model["contracts"], key=lambda x: x["id"])
                 for a in sorted(model["actions"]))


def trace_signature(model, state, horizon):
    actions = tuple(sorted(model["actions"]))
    # all paths of length 0...horizon, not merely the deepest paths
    return tuple((path, _view(model, state, path))
                 for k in range(horizon+1)
                 for path in product(actions, repeat=k))


def independent_pair_equivalent(model, left, right, horizon):
    return trace_signature(model, left, horizon) == trace_signature(model, right, horizon)


def check_partition(model, result):
    horizon = result["horizon"]
    ids = sorted(s["id"] for s in model["states"])
    q = result["class_of"]
    if set(q) != set(ids):
        raise AssertionError("missing/extra state IDs in quotient")
    trace = {sid: trace_signature(model, sid, horizon) for sid in ids}
    comparisons = 0
    for a, b in combinations(ids, 2):
        actual = trace[a] == trace[b]
        predicted = q[a] == q[b]
        if actual != predicted:
            raise AssertionError(f"illegal merge or split for {a}/{b} at r={horizon}")
        comparisons += 1
    return {"states": len(ids), "pairs": comparisons, "horizon": horizon,
            "independent_trace_oracle": "PASS"}


def check_witness(model, w):
    left, right = w["states"]
    path = tuple(w["action_prefix"])
    lv = _view(model, left, path)
    rv = _view(model, right, path)
    matches = [(x, y) for x, y in zip(lv, rv)
               if x[0] == w["contract"] and x[1] == w["decision_action"]
               and y[0] == x[0] and y[1] == x[1]]
    if len(matches) != 1:
        raise AssertionError("witness contract/action not present")
    x, y = matches[0]
    if x[2] == y[2]:
        raise AssertionError("witness does not separate")
    if x[2] != w["left_decision"] or y[2] != w["right_decision"]:
        raise AssertionError("witness decision misreported")
    return True
