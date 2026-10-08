#!/usr/bin/env python3
"""Finite-horizon, contract-relative lawful observation quotient (v2 research).

This module intentionally does not import, replace or patch the frozen G4 B10
compiler. The table-based finite input is an explicitly SYNTHETIC model.
Partition refinement and its minimality theorem are classical; the research
question is whether C1/C2/C3-lawful contract observations are useful.
"""
import itertools
import json
from collections import defaultdict

SCHEMA = "eeq-wfc-v2-finite-system-v1"
REFUSAL = "INSUFFICIENT_EVIDENCE_REFUSE"
FORBIDDEN_FIELDS = {
    "native_action", "native_label", "scored_native_outcome",
    "post_hoc_expected_label", "mergeable", "mergeable_state",
    "future_information_unavailable_at_decision_time",
}

def reject_label_leakage(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in FORBIDDEN_FIELDS:
                raise EvidenceRefusal("forbidden_native_outcome_field")
            reject_label_leakage(value)
    elif isinstance(obj, list):
        for value in obj:
            reject_label_leakage(value)

class EvidenceRefusal(ValueError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)

def canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def byte_size(obj):
    return len(canon(obj).encode("utf-8"))

def _unique_strings(values, what):
    if not isinstance(values, list) or not values:
        raise EvidenceRefusal("missing_" + what)
    if any(not isinstance(x, str) or not x for x in values):
        raise EvidenceRefusal("invalid_" + what)
    if len(values) != len(set(values)):
        raise EvidenceRefusal("duplicate_" + what)
    return values

def validate_spec(spec):
    if not isinstance(spec, dict) or spec.get("schema") != SCHEMA:
        raise EvidenceRefusal("unsupported_v2_spec_schema")
    reject_label_leakage(spec)
    for name in ("c1_complete", "c2_complete", "c3_complete", "decision_time_visible"):
        if spec.get(name) is not True:
            raise EvidenceRefusal(name + "_not_proven")
    claims = _unique_strings(spec.get("claims"), "claims")
    actions = _unique_strings(spec.get("actions"), "actions")
    sources = spec.get("sources")
    contracts = spec.get("contracts")
    states = spec.get("states")
    if not isinstance(sources, list) or not sources:
        raise EvidenceRefusal("missing_source_inventory")
    if not isinstance(contracts, list) or not contracts:
        raise EvidenceRefusal("missing_contracts")
    if not isinstance(states, list) or not states:
        raise EvidenceRefusal("missing_states")
    source_ids = _unique_strings([x.get("id") for x in sources], "source_ids")
    contract_ids = _unique_strings([x.get("id") for x in contracts], "contract_ids")
    state_ids = _unique_strings([x.get("id") for x in states], "state_ids")
    claim_set = set(claims)
    for src in sources:
        if not isinstance(src.get("claims"), list) or not set(src["claims"]) <= claim_set:
            raise EvidenceRefusal("invalid_source_claim_binding")
        if src.get("identity_provenance_available") is not True:
            raise EvidenceRefusal("source_provenance_unavailable")
    for contract in contracts:
        requested = contract.get("claims")
        if not isinstance(requested, list) or not requested or not set(requested) <= claim_set:
            raise EvidenceRefusal("invalid_contract_claims")
        threshold = contract.get("min_support")
        if type(threshold) is not int or threshold < 1:
            raise EvidenceRefusal("invalid_contract_threshold")
        if type(contract.get("audit_provenance")) is not bool:
            raise EvidenceRefusal("missing_audit_requirement")
    ids = set(state_ids)
    for st in states:
        quals = st.get("qualification")
        trans = st.get("transitions")
        if not isinstance(quals, dict) or set(quals) != set(source_ids):
            raise EvidenceRefusal("incomplete_c1_source_state")
        if not isinstance(trans, dict) or set(trans) != set(actions):
            raise EvidenceRefusal("incomplete_c3_action_relation")
        if any(v not in ids for v in trans.values()):
            raise EvidenceRefusal("transition_outside_registered_state_space")
        for source_id in source_ids:
            q = quals[source_id]
            if not isinstance(q, dict) or set(q) != {"authenticated", "authorized"}:
                raise EvidenceRefusal("incomplete_c2_source_qualification")
            for field in ("authenticated", "authorized"):
                if q[field] not in (True, False, None):
                    raise EvidenceRefusal("invalid_c2_qualification_value")
    return True

def build_index(spec):
    validate_spec(spec)
    return {s["id"]: s for s in spec["states"]}

def _support_status(q):
    if q["authenticated"] is False or q["authorized"] is False:
        return "INELIGIBLE"
    if q["authenticated"] is True and q["authorized"] is True:
        return "ELIGIBLE"
    return "UNKNOWN"

def observable(spec, state):
    """Lawful output derived only from registered evidence, never native labels."""
    catalog = {src["id"]: set(src["claims"]) for src in spec["sources"]}
    out = []
    for contract in sorted(spec["contracts"], key=lambda x: x["id"]):
        for claim in sorted(contract["claims"]):
            eligible = []
            unknown = []
            for source_id in sorted(catalog):
                if claim not in catalog[source_id]:
                    continue
                status = _support_status(state["qualification"][source_id])
                if status == "ELIGIBLE":
                    eligible.append(source_id)
                elif status == "UNKNOWN":
                    unknown.append(source_id)
            required = contract["min_support"]
            audit = contract["audit_provenance"]
            if audit and unknown:
                verdict = "REFUSE"
            elif len(eligible) >= required:
                verdict = "ALLOW"
            elif len(eligible) + len(unknown) < required:
                verdict = "DENY"
            else:
                verdict = "REFUSE"
            result = {
                "contract": contract["id"], "claim": claim,
                "verdict": verdict,
            }
            if audit:
                # The contract explicitly asks for the COMPLETE authorized
                # witness set, not merely one convenient supporting source.
                result["qualified_support_sources"] = eligible if not unknown else None
            out.append(result)
    return out

def _partition(signatures, state_ids):
    keys = sorted(set(canon(signatures[s]) for s in state_ids))
    names = {v: i for i, v in enumerate(keys)}
    return ({s: names[canon(signatures[s])] for s in state_ids},
            [(i, json.loads(k)) for i, k in enumerate(keys)])

def compile_quotient(spec, horizon):
    validate_spec(spec)
    if type(horizon) is not int or not 0 <= horizon <= 12:
        raise ValueError("horizon must be an integer in [0,12]")
    states = build_index(spec)
    ids = sorted(states)
    actions = sorted(spec["actions"])
    obs = {sid: observable(spec, states[sid]) for sid in ids}
    layers = []
    assignments = []
    first_ids, first_classes = _partition(obs, ids)
    assignments.append(first_ids)
    layers.append({
        "depth": 0, "classes": [
            {"id": k, "observation": v} for k, v in first_classes
        ],
    })
    for depth in range(1, horizon + 1):
        signatures = {
            sid: {
                "observation": obs[sid],
                "successors": [assignments[-1][states[sid]["transitions"][act]]
                               for act in actions],
            }
            for sid in ids
        }
        class_ids, classes = _partition(signatures, ids)
        assignments.append(class_ids)
        layers.append({
            "depth": depth,
            "classes": [
                {"id": k, "observation": v["observation"],
                 "successors_at_depth_minus_one": dict(zip(actions, v["successors"]))}
                for k, v in classes
            ],
        })
    table = {
        "contracts": sorted(spec["contracts"], key=lambda x: x["id"]),
        "actions": actions,
        "horizon": horizon,
        "layers": layers,
    }
    last = assignments[-1]
    classes = len(set(last.values()))
    full_bytes = sum(byte_size(states[sid]) for sid in ids)
    code_bytes = sum(byte_size(last[sid]) for sid in ids)
    tab_bytes = byte_size(table)
    return {
        "schema": "eeq-wfc-v2-lawful-quotient-result",
        "status": "COMPILED",
        "evidence_class": "SYNTHETIC",
        "source_spec_schema": SCHEMA,
        "state_count": len(ids),
        "class_count": classes,
        "class_count_by_depth": [len(layer["classes"]) for layer in layers],
        "states_to_final_class": dict(sorted(last.items())),
        "state_to_class_by_depth": [dict(sorted(x.items())) for x in assignments],
        "table": table,
        "cost": {
            "raw_state_bytes_total": full_bytes,
            "class_code_bytes_total": code_bytes,
            "quotient_table_bytes": tab_bytes,
            "total_encoded_bytes": tab_bytes + code_bytes,
            "amortized_bytes_per_state": (tab_bytes + code_bytes) / len(ids),
            "raw_state_bytes_per_state": full_bytes / len(ids),
            "shared_source_catalog_bytes": byte_size(spec["sources"]),
            "shared_action_contract_bytes": byte_size({
                "actions": spec["actions"], "contracts": spec["contracts"]}),
        },
        "limitations": [
            "bounded_horizon_only",
            "class_count_minimality_not_bit_minimality",
            "no_native_outcome_labels_consumed",
            "synthetic_model_not_real_family_parity",
        ],
    }

def safe_compile(spec, horizon):
    try:
        return compile_quotient(spec, horizon)
    except EvidenceRefusal as e:
        return {"status": REFUSAL, "reason": e.reason, "evidence_class": "SYNTHETIC"}

def action_words(actions, horizon):
    for k in range(horizon + 1):
        for w in itertools.product(sorted(actions), repeat=k):
            yield w

def _follow(states, sid, word):
    for a in word:
        sid = states[sid]["transitions"][a]
    return sid

def independent_trace(spec, sid, horizon):
    """Brute-force action-word oracle. No use of quotient partitions."""
    states = build_index(spec)
    return [
        canon(observable(spec, states[_follow(states, sid, word)]))
        for word in action_words(spec["actions"], horizon)
    ]

def independent_equivalence_check(spec, horizon, quotient, exhaustive=True, max_pairs=None):
    """Compare pairwise quotient equality to independently enumerated traces."""
    ids = sorted(build_index(spec))
    if not exhaustive and max_pairs is None:
        raise ValueError("max_pairs required for sampled oracle check")
    traces = {sid: independent_trace(spec, sid, horizon) for sid in ids}
    compared = 0
    for left, right in itertools.combinations(ids, 2):
        same_oracle = traces[left] == traces[right]
        same_quotient = (quotient["states_to_final_class"][left] ==
                         quotient["states_to_final_class"][right])
        if same_oracle != same_quotient:
            return {
                "status": "FAIL", "left": left, "right": right,
                "oracle_equal": same_oracle, "quotient_equal": same_quotient,
                "pairs_compared": compared + 1,
            }
        compared += 1
        if not exhaustive and compared >= max_pairs:
            break
    return {
        "status": "PASS", "pairs_compared": compared,
        "oracle": "brute_force_all_registered_action_words",
        "pair_coverage": "EXHAUSTIVE" if exhaustive else "PREFIX_SAMPLE",
    }

def distinction_witness(spec, left, right, horizon):
    """Shortest lexicographic registered action word separating two states."""
    states = build_index(spec)
    if left not in states or right not in states:
        raise ValueError("unknown witness state")
    for word in action_words(spec["actions"], horizon):
        lo = observable(spec, states[_follow(states, left, word)])
        ro = observable(spec, states[_follow(states, right, word)])
        if lo != ro:
            return {"actions": list(word), "length": len(word),
                    "left_observation": lo, "right_observation": ro}
    return None

def legal_next_actions(spec, sid, contract_id, claim):
    """Direct independent downstream native-model oracle, not quotient labels."""
    states = build_index(spec)
    if sid not in states:
        raise ValueError("unknown state")
    outcome = []
    for a in sorted(spec["actions"]):
        following = states[sid]["transitions"][a]
        obs = observable(spec, states[following])
        matches = [o for o in obs if o["contract"] == contract_id and o["claim"] == claim]
        if len(matches) != 1:
            raise ValueError("unknown contract/claim")
        if matches[0]["verdict"] == "ALLOW":
            outcome.append(a)
    return outcome

def correction_words(spec, sid, contract_id, claim, horizon):
    states = build_index(spec)
    legal = []
    for word in action_words(spec["actions"], horizon):
        obs = observable(spec, states[_follow(states, sid, word)])
        matches = [o for o in obs if o["contract"] == contract_id and o["claim"] == claim]
        if len(matches) != 1:
            raise ValueError("unknown contract/claim")
        if matches[0]["verdict"] == "ALLOW":
            legal.append(list(word))
    return legal

def quotient_downstream_check(spec, compiled, contract_id, claim):
    """Check class-based decisions against independent direct state actions."""
    ids = sorted(build_index(spec))
    classes = defaultdict(list)
    for sid in ids:
        classes[compiled["states_to_final_class"][sid]].append(sid)
    violations = []
    for members in classes.values():
        representative = members[0]
        safe = legal_next_actions(spec, representative, contract_id, claim)
        horizon = compiled["table"]["horizon"]
        paths = correction_words(spec, representative, contract_id, claim, horizon)
        for sid in members[1:]:
            if safe != legal_next_actions(spec, sid, contract_id, claim):
                if horizon >= 1: violations.append([representative, sid, "safe_actions"])
            if paths != correction_words(spec, sid, contract_id, claim, horizon):
                violations.append([representative, sid, "correction_words"])
    return {"status": "PASS" if not violations else "FAIL",
            "violations": violations, "classes": len(classes)}

if __name__ == "__main__":
    raise SystemExit("Import module from frozen tests; no unreviewed native scoring CLI.")
