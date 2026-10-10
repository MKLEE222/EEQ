#!/usr/bin/env python3
"""Independent finite possible-world oracle for preregistered R3-M2 F0.

This module does NOT import the candidate, native results, prior predictions or
decision certificate implementation. It models admissible boolean binding
applicability completions plus an unregistered extra veto when world is open.
"""
from itertools import product

REGISTERED_MASKS = {
    "FULL_CLOSED","TEAM_ONLY_CLOSED","MODE_ONLY_CLOSED",
    "NO_SELECTORS_CLOSED","OPEN_INVENTORY_KNOWN_BINDINGS",
    "POLICY_SOURCE_UNAVAILABLE","POLICY_SOURCE_TAMPERED",
    "BINDING_FRESHNESS_UNPROVEN"
}


def possible_native_vap_effects(packet):
    """Return ALL possible scoped effects, not the actual native label."""
    if packet["mask_id"] not in REGISTERED_MASKS:
        raise ValueError("ORACLE_UNREGISTERED_MASK")
    policy=packet["policy"]
    membership=packet["binding_provenance"]
    # No assurance of policy/Binding effect; permit both effects.
    if (policy["state"]!="AVAILABLE" or
        membership["individual_bindings_fresh_in_scoped_native_archive"] is not True):
        return frozenset(("ACCEPT","REJECT"))
    known=[]
    unknown_count=0
    for slot in packet["binding_slots"]:
        if slot["selector_status"]=="SOURCE_UNAVAILABLE":
            unknown_count+=1
        elif slot["selector_status"]=="AVAILABLE":
            known.append(all(packet["namespace_labels"].get(k)==v
                             for k,v in slot["selector"].items()))
        else:
            return frozenset(("ACCEPT","REJECT"))
    possible=set()
    open_world=packet["mask_id"]=="OPEN_INVENTORY_KNOWN_BINDINGS"
    # Unknown registered selectors can either match or not; opening the
    # inventory adds a possible OTHER-policy denial even for default Pods.
    combinations=product((False,True),repeat=unknown_count+(1 if open_world else 0))
    for combo in combinations:
        bindings=known+list(combo[:unknown_count])
        unknown_other_denial=bool(combo[-1]) if open_world else False
        denials_from_known_policy=(packet["pod"]["serviceAccountName"]=="flux"
                                   and any(bindings))
        possible.add("REJECT" if denials_from_known_policy or unknown_other_denial
                     else "ACCEPT")
    return frozenset(possible)


def strongest_b9_with_equal_partial_inputs(packet):
    """Oracle-optimal full-information-engineered baseline gets the SAME packet."""
    worlds=possible_native_vap_effects(packet)
    if worlds==frozenset(("REJECT",)):
        return "PROVEN_REJECT"
    if worlds==frozenset(("ACCEPT",)):
        return "PROVEN_ACCEPT"
    return ("SOURCE_UNAVAILABLE_REFUSE"
            if (packet["policy"]["state"]=="SOURCE_UNAVAILABLE" or
                any(b["selector_status"]=="SOURCE_UNAVAILABLE"
                    for b in packet["binding_slots"]))
            and packet["mask_id"]!="BINDING_FRESHNESS_UNPROVEN"
            else "MODEL_UNSUPPORTED_REFUSE")
