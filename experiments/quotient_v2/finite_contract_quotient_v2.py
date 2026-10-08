#!/usr/bin/env python3
"""Development-only EEQ quotient-frontier v2 for FINITE declared contracts.

A standard Moore-style partition refiner over lawful, contract-derived
three-valued decisions. No native labels or prior holdout cases are inputs.
This is NOT a replacement for frozen compile_wfc_v1.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

FORBIDDEN = {
    "native_label", "native_action", "mergeable", "mergeable_state",
    "scored_native_outcome", "post_hoc_expected_label",
    "future_information_unavailable_at_decision_time",
}
TRUTH_VALUES = (True, False, None)
TOP_FIELDS = {"schema", "evidence_class", "actions", "claims", "contracts", "states"}
CONTRACT_FIELDS = {"id", "claim", "min_qualified_sources", "allowed_actions",
                   "source_restriction"}
STATE_FIELDS = {"id", "source_inventory_complete", "support_items",
                "transitions", "decoration_not_in_registered_contract"}
SUPPORT_FIELDS = {"id", "source_identity", "provenance", "compatible_claims",
                  "claim_binding", "authenticated", "authorized", "qualified"}


def _reject_unknown_fields(obj, allowed, where):
    if not isinstance(obj, dict):
        raise ValueError(f"expected object at {where}")
    extras = set(obj) - allowed
    if extras:
        raise ValueError(f"unsupported semantics at {where}: {sorted(extras)}")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _reject_label_fields(obj, where="root"):
    if isinstance(obj, dict):
        for key, value in obj.items():
            _require(key not in FORBIDDEN, "native/forbidden field at " + where + "/" + key)
            _reject_label_fields(value, where + "/" + key)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            _reject_label_fields(value, where + "/" + str(i))


class FiniteContractModel:
    """All source/contract data are supplied before any native scoring."""

    def __init__(self, payload):
        _reject_label_fields(payload)
        _reject_unknown_fields(payload, TOP_FIELDS, "model")
        _require(payload.get("schema") == "eeq-finite-contract-model-v2",
                 "wrong finite model schema")
        self.raw = payload
        self.actions = tuple(sorted(payload.get("actions", [])))
        _require(bool(self.actions) and len(set(self.actions)) == len(self.actions),
                 "actions must be nonempty unique names")
        _require(all(isinstance(x, str) and x for x in self.actions), "bad action")
        self.claims = tuple(sorted(payload.get("claims", [])))
        _require(bool(self.claims) and len(set(self.claims)) == len(self.claims),
                 "claims must be nonempty unique names")
        contracts = payload.get("contracts", [])
        self.contracts = sorted(contracts, key=lambda x: x["id"])
        _require(bool(self.contracts) and
                 len({x["id"] for x in contracts}) == len(contracts),
                 "contracts must have unique IDs")
        for c in self.contracts:
            _reject_unknown_fields(c, CONTRACT_FIELDS, "contract")
            _require(c.get("claim") in self.claims, "unknown contract claim")
            threshold = c.get("min_qualified_sources")
            _require(type(threshold) is int and threshold > 0, "threshold must be positive integer")
            aa = c.get("allowed_actions")
            _require(isinstance(aa, list) and
                     set(aa).issubset(self.actions) and len(set(aa)) == len(aa),
                     "invalid allowed action list")
            if "source_restriction" in c:
                restrict = c["source_restriction"]
                _require(isinstance(restrict, list) and
                         len(set(restrict)) == len(restrict), "invalid source restriction")
        states = payload.get("states", [])
        self.states = {s["id"]: s for s in states}
        _require(len(self.states) == len(states) and bool(self.states),
                 "state ids must be nonempty and unique")
        _require(all(isinstance(sid, str) and sid for sid in self.states),
                 "invalid state id")
        self.ids = tuple(sorted(self.states))
        for sid, state in self.states.items():
            _reject_unknown_fields(state, STATE_FIELDS, "state/" + sid)
            _require(type(state.get("source_inventory_complete")) is bool,
                     "source inventory completeness must be explicit: " + sid)
            transitions = state.get("transitions")
            _require(isinstance(transitions, dict) and
                     set(transitions) == set(self.actions),
                     "total action transition model required: " + sid)
            _require(all(dst in self.states for dst in transitions.values()),
                     "transition to unknown state: " + sid)
            supports = state.get("support_items")
            _require(isinstance(supports, list), "support_items must be list: " + sid)
            _require(len({s["id"] for s in supports}) == len(supports),
                     "duplicate support ID: " + sid)
            for support in supports:
                _reject_unknown_fields(support, SUPPORT_FIELDS, "support/" + sid)
                _require(isinstance(support.get("source_identity"), str)
                         and support["source_identity"], "missing lawful source identity")
                for name in ("authenticated", "authorized", "qualified"):
                    _require(any(support.get(name) is t for t in TRUTH_VALUES),
                             "invalid truth value: " + name)
                for name in ("compatible_claims", "claim_binding"):
                    v = support.get(name)
                    _require(isinstance(v, list) and set(v).issubset(self.claims),
                             "invalid claim set: " + name)
        self.observations = {sid: self._observation(sid) for sid in self.ids}

    @staticmethod
    def _route(support, claim):
        if claim not in support["compatible_claims"]:
            return False
        if claim not in support["claim_binding"]:
            return False
        values = [support[k] for k in ("authenticated", "authorized", "qualified")]
        if False in values:
            return False
        if None in values:
            return None
        return True

    def _status(self, state, contract, action):
        if action not in contract["allowed_actions"]:
            return "REJECT"
        claim = contract["claim"]
        allowed = (set(contract["source_restriction"])
                   if "source_restriction" in contract else None)
        lower = set()
        possible = set()
        for support in state["support_items"]:
            source = support["source_identity"]
            if allowed is not None and source not in allowed:
                continue
            route = self._route(support, claim)
            if route is True:
                lower.add(source)
                possible.add(source)
            elif route is None:
                possible.add(source)
        threshold = contract["min_qualified_sources"]
        if len(lower) >= threshold:
            return "ACCEPT"
        if state["source_inventory_complete"] and len(possible) < threshold:
            return "REJECT"
        return "REFUSE"

    def _observation(self, sid):
        state = self.states[sid]
        return tuple(
            (c["id"], action, self._status(state, c, action))
            for c in self.contracts for action in self.actions
        )

    def step(self, sid, action):
        return self.states[sid]["transitions"][action]

    def trace_observation(self, sid, path):
        for action in path:
            sid = self.step(sid, action)
        return self.observations[sid]

    def quotient(self, horizon):
        _require(type(horizon) is int and horizon >= 0,
                 "horizon must be a nonnegative integer")
        # The signatures themselves are canonicalized; IDs are per-run symbols,
        # NOT global hash promises and NOT free-standing evidence certificates.
        stage = []
        mapping = {}
        for k in range(horizon + 1):
            signatures = {}
            for sid in self.ids:
                if k == 0:
                    key = ("observation", self.observations[sid])
                else:
                    key = ("observation", self.observations[sid],
                           "successors", tuple((a, mapping[self.step(sid, a)])
                                               for a in self.actions))
                signatures[sid] = canonical(key)
            unique = sorted(set(signatures.values()))
            table = {v: i for i, v in enumerate(unique)}
            mapping = {sid: table[signatures[sid]] for sid in self.ids}
            stage.append({"horizon": k, "classes": len(unique)})
        groups = defaultdict(list)
        for sid in self.ids:
            groups[mapping[sid]].append(sid)
        return {
            "horizon": horizon,
            "class_of": mapping,
            "classes": [{"id": cid, "members": groups[cid]}
                        for cid in sorted(groups)],
            "refinement": stage,
        }

    def witness(self, left, right, horizon):
        """Shortest lexicographic separating trace; None iff equivalent."""
        _require(left in self.states and right in self.states, "unknown state")
        _require(horizon >= 0, "invalid horizon")
        from collections import deque
        todo = deque([(left, right, ())])
        seen = set()
        while todo:
            a, b, trace = todo.popleft()
            key = (a, b, len(trace))
            if key in seen:
                continue
            seen.add(key)
            x, y = self.observations[a], self.observations[b]
            for i, (lx, ry) in enumerate(zip(x, y)):
                if lx != ry:
                    return {
                        "states": [left, right],
                        "action_prefix": list(trace),
                        "contract": lx[0],
                        "decision_action": lx[1],
                        "left_decision": lx[2],
                        "right_decision": ry[2],
                    }
            if len(trace) < horizon:
                for action in self.actions:
                    todo.append((self.step(a, action), self.step(b, action),
                                 trace + (action,)))
        return None

    def run(self, horizon, witness_limit=0):
        quotient = self.quotient(horizon)
        # Codebook size is explicitly charged. Keep original source bytes
        # separate: no representation may make provenance acquisition free.
        codebook = {
            "alphabet": self.actions,
            "contracts": self.contracts,
            "observations": {
                str(cl["id"]): list(self.observations[cl["members"][0]])
                for cl in quotient["classes"]
            },
            "transitions": {
                str(cl["id"]): {
                    a: quotient["class_of"][self.step(cl["members"][0], a)]
                    for a in self.actions
                } for cl in quotient["classes"]
            },
        }
        # For finite horizons successor classes at depth r need not be a
        # congruence at depth r. The transition table is diagnostic only
        # unless quotient(r) == quotient(r+1).
        stable = (len(quotient["classes"]) ==
                  len(self.quotient(horizon + 1)["classes"]))
        counterexamples = []
        if witness_limit:
            for i, s in enumerate(self.ids):
                for t in self.ids[i+1:]:
                    if quotient["class_of"][s] == quotient["class_of"][t]:
                        continue
                    counterexamples.append(self.witness(s, t, horizon))
                    _require(counterexamples[-1] is not None, "missing separation witness")
                    if len(counterexamples) >= witness_limit:
                        break
                if len(counterexamples) >= witness_limit:
                    break
        cost = {
            "input_source_model_bytes": len(canonical(self.raw).encode("utf-8")),
            "codebook_bytes": len(canonical(codebook).encode("utf-8")),
            "assignment_bytes": len(canonical(quotient["class_of"]).encode("utf-8")),
        }
        cost["codebook_plus_assignments_bytes"] = (cost["codebook_bytes"] +
                                                   cost["assignment_bytes"])
        return {
            "schema": "eeq-quotient-frontier-v2",
            "scope": "finite deterministic declared evidence/contract model only",
            "not_native_label_accuracy": True,
            "horizon": horizon,
            "state_count": len(self.ids),
            "quotient_class_count": len(quotient["classes"]),
            "class_of": quotient["class_of"],
            "classes": quotient["classes"],
            "refinement": quotient["refinement"],
            "stable_transition_congruence": stable,
            "cost": cost,
            "separation_witnesses": counterexamples,
            "core_version": "DEVELOPMENT_V2_PROTOCOL_BREAK_FROM_G4_V1",
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", type=Path)
    ap.add_argument("--horizon", type=int, default=1)
    ap.add_argument("--witness-limit", type=int, default=20)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    data = json.loads(args.model.read_text(encoding="utf-8"))
    result = FiniteContractModel(data).run(args.horizon, args.witness_limit)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "state_count": result["state_count"],
        "quotient_class_count": result["quotient_class_count"],
        "horizon": result["horizon"],
        "stable_transition_congruence": result["stable_transition_congruence"],
        "cost": result["cost"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
