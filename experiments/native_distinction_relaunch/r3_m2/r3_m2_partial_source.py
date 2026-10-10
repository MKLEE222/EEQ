#!/usr/bin/env python3
"""R3-M2 F0: conditional, *scoped* partial-evidence decision certificates.

This is an authored controlled-development evidence projection, not a native
Kubernetes oracle, a general support-inventory authority, or a new theorem.
Candidate never consumes R3-M1 SOURCE_PREDICTIONS or native scoring artifacts.
"""
import copy
import json
from pathlib import Path

from sys import path as module_path
module_path.insert(0, str(Path(__file__).resolve().parents[1] / "r3_m1"))
from r3_m1_source_only import source_inputs, validate

ROOT = Path(__file__).resolve().parents[1] / "r3_m1" / "sources"
MASKS = (
    "FULL_CLOSED", "TEAM_ONLY_CLOSED", "MODE_ONLY_CLOSED",
    "NO_SELECTORS_CLOSED", "OPEN_INVENTORY_KNOWN_BINDINGS",
    "POLICY_SOURCE_UNAVAILABLE", "POLICY_SOURCE_TAMPERED",
    "BINDING_FRESHNESS_UNPROVEN",
)
ORDERS = {"TM": ("team", "mode"), "MT": ("mode", "team")}
PHASES = ("initial", "after_first", "after_second")
PROBES = ("flux", "default")
CONTRACT = "R3_M2_REGISTERED_TWO_BINDINGS_ONE_POLICY_POD_CREATE"
REGISTERED_POLICY_NAME = "eeq-r3-flux-deny"
DENIAL_EXPRESSION = "object.spec.serviceAccountName != 'flux'"
BOUND_SOURCE_NAMES = ("binding-team.json", "binding-mode.json")
EVIDENCE_CLASS = "POST_NATIVE_REUSE_OF_ALREADY_SCORED_CONTROLLED_DEVELOPMENT"


def registered_rows():
    """Source-derived states and registered actions. No native result is read."""
    docs, manifest = source_inputs(ROOT)
    selectors, accounts = validate(docs)
    rows = []
    for order, actions in ORDERS.items():
        labels = docs["namespace.json"]["metadata"]["labels"].copy()
        for i, phase in enumerate(PHASES):
            if i:
                act = docs["action-" + actions[i-1] + ".json"]
                if labels.get(act["key"]) != act["from"]:
                    raise ValueError("ACTION_PRECONDITION_NOT_REGISTERED")
                labels[act["key"]] = act["to"]
            for probe in PROBES:
                rows.append({
                    "id": order + "|" + phase + "|" + probe,
                    "order": order, "phase": phase, "probe": probe,
                    "labels": labels.copy(),
                    "service_account": accounts[probe],
                    "selectors": copy.deepcopy(selectors),
                })
    if len(rows) != 12:
        raise ValueError("SOURCE_CASE_DENOMINATOR_NOT_12")
    return rows, manifest


def projected_packet(row, mask):
    """Simulate unavailable *decision-time* source projections.

    Known binding identities and common-policy metadata are an authored,
    registered-envelope assumption, not live third-party signed attestation.
    """
    if mask not in MASKS:
        raise ValueError("UNREGISTERED_MASK")
    selected = {
        "FULL_CLOSED": ("team", "mode"),
        "TEAM_ONLY_CLOSED": ("team",),
        "MODE_ONLY_CLOSED": ("mode",),
        "NO_SELECTORS_CLOSED": (),
        "OPEN_INVENTORY_KNOWN_BINDINGS": ("team", "mode"),
        "POLICY_SOURCE_UNAVAILABLE": ("team", "mode"),
        "POLICY_SOURCE_TAMPERED": ("team", "mode"),
        "BINDING_FRESHNESS_UNPROVEN": ("team", "mode"),
    }[mask]
    status = ("SOURCE_UNAVAILABLE" if mask == "POLICY_SOURCE_UNAVAILABLE"
              else "DIGEST_INVALID" if mask == "POLICY_SOURCE_TAMPERED"
              else "AVAILABLE")
    binding_fresh = mask != "BINDING_FRESHNESS_UNPROVEN"
    return {
        "schema": "eeq-r3-m2-partial-evidence-packet-f0",
        "contract": CONTRACT,
        "case_id": row["id"], "mask_id": mask,
        "order": row["order"], "phase": row["phase"],
        "pod": {"serviceAccountName": row["service_account"]},
        "namespace_labels": row["labels"].copy(),
        "policy": {
            "state": status,
            "name": REGISTERED_POLICY_NAME,
            "validation": DENIAL_EXPRESSION if status == "AVAILABLE" else None,
            "validation_action": "Deny",
            "failure_policy": "Fail",
        },
        "binding_provenance": {
            "source": "R3_M1_PINNED_CONTROLLED_REGISTRY_NOT_PRODUCTION_AUTHORITY",
            "individual_bindings_fresh_in_scoped_native_archive": binding_fresh,
        },
        "binding_slots": [
            {
                "source_id": "binding-" + b + ".json",
                "policy_name": REGISTERED_POLICY_NAME,
                "validation_action": "Deny",
                "selector_status": ("AVAILABLE" if b in selected
                                    else "SOURCE_UNAVAILABLE"),
                "selector": (row["selectors"][b].copy()
                             if b in selected else None),
            } for b in ("team", "mode")
        ],
        # This untrusted hint is NEVER used to authorize closed-world reuse.
        "caller_claimed_complete": True,
        "evidence_class": EVIDENCE_CLASS,
    }


def registered_mask_packet_rows():
    rows, _ = registered_rows()
    packets = [projected_packet(row, mask) for mask in MASKS for row in rows]
    if len(packets) != 96 or len({(p["case_id"],p["mask_id"]) for p in packets}) != 96:
        raise ValueError("REGISTERED_PACKET_DENOMINATOR_NOT_96")
    return packets


def validate_packet(p):
    """Input validation using explicit frozen mask grammar, not caller completeness."""
    if not isinstance(p, dict) or p.get("schema") != "eeq-r3-m2-partial-evidence-packet-f0":
        return "INVALID_PACKET_SCHEMA"
    if p.get("contract") != CONTRACT or p.get("mask_id") not in MASKS:
        return "INVALID_CONTRACT_OR_MASK"
    order, phase = p.get("order"), p.get("phase")
    if order not in ORDERS or phase not in PHASES:
        return "INVALID_ORDER_OR_PHASE"
    probe = p.get("pod")
    if not isinstance(probe, dict) or set(probe) != {"serviceAccountName"}:
        return "INVALID_POD"
    if probe["serviceAccountName"] not in PROBES:
        return "OUTSIDE_POD_CONTRACT"
    expected_id = order + "|" + phase + "|" + probe["serviceAccountName"]
    if p.get("case_id") != expected_id:
        return "CASE_BINDING_MISMATCH"
    expected_labels = {"r3.team": "tenant", "r3.mode": "strict"}
    for act in ORDERS[order][:PHASES.index(phase)]:
        expected_labels["r3." + act] = {
            "team": "external", "mode": "relaxed"}[act]
    if p.get("namespace_labels") != expected_labels:
        return "UNREGISTERED_NAMESPACE_CONTINUATION"
    pol = p.get("policy")
    if not isinstance(pol,dict) or set(pol) != {
            "state","name","validation","validation_action","failure_policy"}:
        return "INVALID_POLICY_PACKET"
    if pol.get("name") != REGISTERED_POLICY_NAME or pol.get("validation_action") != "Deny" or pol.get("failure_policy") != "Fail":
        return "UNREGISTERED_POLICY_ENVELOPE"
    mask = p["mask_id"]
    want_pol_status = (
        "SOURCE_UNAVAILABLE" if mask == "POLICY_SOURCE_UNAVAILABLE" else
        "DIGEST_INVALID" if mask == "POLICY_SOURCE_TAMPERED" else "AVAILABLE")
    if pol["state"] != want_pol_status or pol["validation"] != (
            DENIAL_EXPRESSION if want_pol_status == "AVAILABLE" else None):
        return "SOURCE_POLICY_MASK_INCONSISTENT"
    prov = p.get("binding_provenance")
    if not isinstance(prov,dict) or prov.get("source") != "R3_M1_PINNED_CONTROLLED_REGISTRY_NOT_PRODUCTION_AUTHORITY":
        return "NO_SCOPED_MEMBERSHIP_ENVELOPE"
    if prov.get("individual_bindings_fresh_in_scoped_native_archive") is not (
            mask != "BINDING_FRESHNESS_UNPROVEN"):
        return "BINDING_FRESHNESS_MASK_INCONSISTENT"
    slots = p.get("binding_slots")
    if not isinstance(slots,list) or len(slots)!=2 or any(not isinstance(x,dict) for x in slots):
        return "MISSING_OR_DUPLICATE_SUPPORT_SLOTS"
    if [s.get("source_id") for s in slots]!=list(BOUND_SOURCE_NAMES):
        return "REGISTERED_SUPPORT_SLOT_IDENTITY_NOT_PRESERVED"
    expected_selected = {
        "FULL_CLOSED": {"team","mode"},
        "TEAM_ONLY_CLOSED": {"team"},
        "MODE_ONLY_CLOSED": {"mode"},
        "NO_SELECTORS_CLOSED": set(),
        "OPEN_INVENTORY_KNOWN_BINDINGS": {"team","mode"},
        "POLICY_SOURCE_UNAVAILABLE": {"team","mode"},
        "POLICY_SOURCE_TAMPERED": {"team","mode"},
        "BINDING_FRESHNESS_UNPROVEN": {"team","mode"},
    }[mask]
    for idx,b in enumerate(("team","mode")):
        s=slots[idx]
        if set(s)!={"source_id","policy_name","validation_action",
                    "selector_status","selector"} or s["policy_name"] != REGISTERED_POLICY_NAME or s["validation_action"]!="Deny":
            return "UNSUPPORTED_BINDING_ENVELOPE"
        should_be_known=b in expected_selected
        if s["selector_status"]!=("AVAILABLE" if should_be_known else "SOURCE_UNAVAILABLE"):
            return "SOURCE_AVAILABILITY_MASK_INCONSISTENT"
        if should_be_known:
            expected={("r3.team" if b=="team" else "r3.mode"):
                      ("tenant" if b=="team" else "strict")}
            if s["selector"]!=expected:
                return "UNREGISTERED_SELECTOR_SOURCE"
        elif s["selector"] is not None:
            return "HIDDEN_SOURCE_LEAKED_INTO_PACKET"
    return None


def candidate(p):
    """Source-qualified, fail-closed candidate; no native decision or strong-B9 advantage."""
    bad=validate_packet(p)
    if bad:
        return {"disposition":"MODEL_UNSUPPORTED_REFUSE",
                "reason":bad,"witness":[]}
    pol=p["policy"]
    if pol["state"]=="SOURCE_UNAVAILABLE":
        return {"disposition":"SOURCE_UNAVAILABLE_REFUSE",
                "reason":"POLICY_REQUIRED_SOURCE_UNAVAILABLE","witness":[]}
    if pol["state"]=="DIGEST_INVALID" or not p["binding_provenance"]["individual_bindings_fresh_in_scoped_native_archive"]:
        return {"disposition":"MODEL_UNSUPPORTED_REFUSE",
                "reason":"POLICY_OR_BINDING_AUTHORITY_NOT_CURRENT","witness":[]}
    denied_by=[]
    missing=[]
    for binding in p["binding_slots"]:
        if binding["selector_status"]=="SOURCE_UNAVAILABLE":
            missing.append(binding["source_id"])
        elif all(p["namespace_labels"].get(k)==v
                 for k,v in binding["selector"].items()):
            if p["pod"]["serviceAccountName"]=="flux":
                denied_by.append(binding["source_id"])
    if denied_by:
        return {"disposition":"PROVEN_REJECT",
                "reason":"INDEPENDENT_VALID_DENIAL_WITNESS",
                "witness":sorted(denied_by)}
    if p["mask_id"]=="OPEN_INVENTORY_KNOWN_BINDINGS":
        return {"disposition":"MODEL_UNSUPPORTED_REFUSE",
                "reason":"ADDITIONAL_UNOBSERVED_DENYING_POLICY_POSSIBLE","witness":[]}
    if p["pod"]["serviceAccountName"]=="default":
        return {"disposition":"PROVEN_ACCEPT",
                "reason":"COMMON_POLICY_PASSES_WITH_CLOSED_REGISTERED_INVENTORY",
                "witness":list(BOUND_SOURCE_NAMES)}
    if missing:
        return {"disposition":"SOURCE_UNAVAILABLE_REFUSE",
                "reason":"UNOBSERVED_BINDING_COULD_STILL_DENY",
                "witness":sorted(missing)}
    return {"disposition":"PROVEN_ACCEPT",
            "reason":"ALL_REGISTERED_BINDINGS_PROVEN_NOT_APPLICABLE",
            "witness":list(BOUND_SOURCE_NAMES)}


if __name__=="__main__":
    packets=registered_mask_packet_rows()
    from collections import Counter
    statuses=Counter(candidate(p)["disposition"] for p in packets)
    print(json.dumps({"schema":"eeq-r3-m2-f0-source-only-summary-v0",
                      "evidence_class":EVIDENCE_CLASS,
                      "registered_source_rows":12,"virtual_packets":len(packets),
                      "native_calls":0,"original_g5_increment":0,
                      "candidate_dispositions":dict(sorted(statuses.items())),
                      "method_novelty_established":False},sort_keys=True))
