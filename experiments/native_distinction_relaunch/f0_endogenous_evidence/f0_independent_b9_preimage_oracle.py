#!/usr/bin/env python3
"""F0 strong B9-eligible REFERENCE independently computes each legal trace.

Does NOT import or call the candidate intervention_semantics functions.
This is a transparent brute-force two-world/one-action transition enumerator.
B9 is given exactly the SAME lawful readings, update rules and trust roots.
"""
import json
from collections import defaultdict
from f0_registry import REGISTERED_EXPECTED,DELEGATIONS

def reference_anchored(roots):
    # Worklist formulation, independent of candidate fixed-point routine.
    reached=list(roots)
    pending=list(roots)
    while pending:
        issuer=pending.pop()
        for src,dst in DELEGATIONS:
            if src==issuer and dst not in reached:
                reached.append(dst)
                pending.append(dst)
    return set(reached)

def reference_per_world(row,bit):
    if row["action"]=="NONE":
        return ("NO_AUTHORIZED_OBSERVATION",),bit,bit,0
    if row["action"]=="GRANT_THEN_READ":
        grant="A" in reference_anchored({"A"} if row["rooted_grant"] else set())
        if not grant:raise PermissionError("FORBIDDEN_GRANT")
        p=bit if row["mode"]=="PRESERVE" else 1
        return ("POLICY_OBSERVED",1,p),bit,p,1
    if row["action"]=="READ_VISIBLE_ONLY":
        return ("VISIBLE_ONLY",int(row["visible_deny"]),False),bit,bit,0
    raise ValueError("UNREGISTERED_OBSERVATION_ACTION")

def exhaustive_reference(row):
    if row["action"]=="REQUEST_GRANT":
        rooted=reference_anchored(set())
        assert len(rooted)==0
        return {
            "status":"ROOTLESS_DELEGATION_REFUSE",
            "classes":0,
            "preimage_collision":False,
            "worlds":2,
            "grant_authority_proven":False,
            "same_successor_from_distinct_pre_worlds":False,
        }
    obs_groups=defaultdict(list)
    successors=[]
    for pre in (0,1):
        obs,prebit,postbit,epoch=reference_per_world(row,pre)
        if row["objective"]=="PRE":target=prebit
        elif row["objective"]=="POST":target=postbit
        elif row["objective"]=="GLOBAL_NO_DENY":
            target=int(row["visible_deny"]==0 and prebit==0)
        else:raise ValueError("UNREGISTERED_OBJECTIVE")
        obs_groups[obs].append((prebit,postbit,target,epoch))
        successors.append((postbit,epoch,
                row["action"]=="GRANT_THEN_READ"))
    collision=any(len({x[2] for x in group})>1 for group in obs_groups.values())
    if row["objective"]=="POST" and not collision:
        status="CERTAIN_POST_TRUE_NOT_PRE"
    elif row["action"]=="GRANT_THEN_READ" and row["mode"]=="PRESERVE" and not collision:
        status="IDENTIFIABLE_AFTER_NONINTERFERING_INTERVENTION"
    elif row["action"]=="GRANT_THEN_READ" and row["mode"]=="OVERWRITE_TRUE" and collision:
        status="UNIDENTIFIABLE_AFTER_DESTRUCTIVE_INTERVENTION"
    elif row["objective"]=="GLOBAL_NO_DENY" and collision:
        status="GLOBAL_NEGATIVE_NOT_IDENTIFIABLE_WITHOUT_CLOSURE"
    elif row["action"]=="NONE" and collision:
        status="UNIDENTIFIABLE_WITH_LAWFUL_OBSERVATIONS"
    else:
        status="REFERENCE_DOES_NOT_MATCH_PRE_FROZEN_CATEGORY"
    return {
        "status":status,
        "classes":len(obs_groups),
        "preimage_collision":collision,
        "worlds":2,
        "grant_authority_proven":bool(
           row["rooted_grant"] and row["action"]=="GRANT_THEN_READ"),
        "same_successor_from_distinct_pre_worlds":successors[0]==successors[1],
        "partition_effect_sets":sorted(tuple(sorted({x[2] for x in grp}))
                                       for grp in obs_groups.values()),
    }

def independently_verify(candidate,row):
    own=exhaustive_reference(row)
    if candidate["status"]!=own["status"] or own["status"]!=row["expected_status"]:
        raise AssertionError("F0_FULL_B9_SAME_LAWFUL_INFORMATION_DISPOSITION_DISAGREES")
    if candidate["worlds_considered"]!=own["worlds"] or candidate["observation_classes"]!=own["classes"]:
        raise AssertionError("F0_OBSERVATION_DENOMINATOR_DISAGREES")
    if bool(candidate.get("identical_observation_opposite_preimage_pair"))!=own["preimage_collision"]:
        raise AssertionError("F0_PREIMAGE_COLLISION_PROOF_MISSING_OR_SPURIOUS")
    if bool(candidate.get("independent_grant_anchor_present"))!=own["grant_authority_proven"]:
        raise AssertionError("F0_UNANCHORED_ACCESS_GRANTED_OR_ROOTED_ACCESS_LOST")
    if candidate.get("global_k8s_admission_claim_authorized") is not False:
        raise AssertionError("F0_UNAUTHORIZED_GLOBAL_ADMISSION")
    if candidate.get("observed_native_outcomes")!=0 or candidate.get("new_G5_cases")!=0:
        raise AssertionError("F0_TOY_MODEL_CLAIMED_NATIVE_SCORE")
    if row["expected_status"]=="UNIDENTIFIABLE_AFTER_DESTRUCTIVE_INTERVENTION":
        if not own["same_successor_from_distinct_pre_worlds"]:
            raise AssertionError("F0_POSTACTION_STATES_ARE_NOT_IDENTICAL")
        pair=candidate["identical_observation_opposite_preimage_pair"]
        if len(pair)!=1 or pair[0]["same_complete_successor_state"] is not True:
            raise AssertionError("F0_NONINJECTIVITY_CERTIFICATE_NOT_VERIFIED")
    if row["expected_status"]=="CERTAIN_POST_TRUE_NOT_PRE":
        if own["partition_effect_sets"]!=[(1,)] or candidate.get(
           "post_effect_certain_from_action_semantics_not_pre_recovery") is not True:
            raise AssertionError("F0_POST_CLAIM_CONFUSED_WITH_PRE_CLAIM")
    if row["expected_status"]=="ROOTLESS_DELEGATION_REFUSE":
        if own["grant_authority_proven"] or candidate.get("least_trust_fixed_point")!=[]:
            raise AssertionError("F0_CIRCULAR_AUTHORITY_BOOTSTRAP")
    return {"independent_bruteforce_B9_equal":True,
            "checked_worlds":2,
            "reference":own,
            "scientific_scope":"ABSTRACT_FINITE_LOGIC_ONLY"}

def diagnostic_pinned_trust_rotation():
    """Historical authorization does not imply CURRENT authority after rotation."""
    raw_signed_source_sha256="f"*64
    cert={"issuer":"A","issued_epoch":0,"claim":"old_delegation",
          "signed_source_sha256":raw_signed_source_sha256}
    before={"epoch":0,"trust_anchors":{"A"}}
    after={"epoch":1,"trust_anchors":{"B"}}
    current_before=cert["issuer"] in before["trust_anchors"]
    current_after=cert["issuer"] in after["trust_anchors"]
    historical_after=cert["issuer"] in before["trust_anchors"]
    return {"byte_identity_preserved":True,
            "before_qualified":current_before,
            "after_current_qualified":current_after,
            "after_historical_epoch0_qualified":historical_after,
            "inference_that_same_bytes_implies_current_qualification":False}

def diagnostic_positive_local_deny(visible,unknown_extra):
    """A qualified visible scoped Deny is enough for positive Deny, not global allow."""
    if visible==1:return "SCOPED_DENY_WITNESSED"
    if unknown_extra is None:return "GLOBAL_NEGATIVE_NOT_PROVEN"
    return "GLOBAL_NO_DENY_CONDITIONAL_ON_EXTERNALLY_CERTIFIED_CLOSURE_ONLY"
