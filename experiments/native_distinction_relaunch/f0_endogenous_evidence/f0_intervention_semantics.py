#!/usr/bin/env python3
"""F0: cause-aware finite PRE/POST evidence identifiability from possible worlds.

This models observation as possibly state-changing authorization ACTION. It
never returns Kubernetes native admission ACCEPT or cryptographic TUF proofs;
proof qualification and actor ability are toy PRE-REGISTERED parameters.
The construction is classically reducible to DEL/partial-information preimages.
"""
import json
from collections import defaultdict
from f0_registry import (REGISTERED_EXPECTED,DELEGATIONS,
                         scenarios,is_registered,EVIDENCE_CLASS)

def least_anchored_authorities(roots=(),delegations=DELEGATIONS):
    # Inductive closure, not coinductively assuming a cycle proves itself.
    result=set(roots)
    while True:
        extra={recipient for issuer,recipient in delegations if issuer in result}
        new=result|extra
        if new==result:return tuple(sorted(result))
        result=new

def authorized_grant(row):
    roots=("A",) if row["rooted_grant"] else ()
    return "A" in least_anchored_authorities(roots)

def initial_world(bit):
    return {"policy":bit,"epoch":0,"may_read":False}

def transition(old,action,mode,is_authorized):
    """Registered deterministic transitions, NOT native K8s RBAC or TUF API."""
    if action in ("NONE","READ_VISIBLE_ONLY"):
        return old.copy()
    if action=="GRANT_THEN_READ":
        if not is_authorized:
            raise PermissionError("GRANT_NOT_LAWFULLY_ANCHORED")
        nxt=old.copy()
        nxt["policy"]=old["policy"] if mode=="PRESERVE" else 1
        nxt["epoch"]=old["epoch"]+1
        nxt["may_read"]=True
        return nxt
    raise ValueError("UNREGISTERED_INTERVENTION_ACTION")

def lawful_observation(row,state):
    action=row["action"]
    if action=="NONE":
        return {"observable":"EMPTY_NO_LAWFUL_READ"}
    if action=="GRANT_THEN_READ":
        if not state["may_read"]:
            raise PermissionError("OBSERVATION_ACTOR_HAS_NO_READ_RIGHT")
        return {"policy_value":state["policy"],"observed_epoch":state["epoch"]}
    if action=="READ_VISIBLE_ONLY":
        return {"visible_registered_deny":row["visible_deny"],
                "authoritative_hidden_source_inventory_proven":False}
    raise PermissionError("NO_REGISTERED_AUTHORITY_TO_PERFORM_OBSERVATION")

def requested_claim(row,prebit,post):
    typ=row["objective"]
    if typ=="PRE":return prebit
    if typ=="POST":return post["policy"]
    if typ=="GLOBAL_NO_DENY":
        # Hidden possibility bit, not a source that this actor can legally LIST.
        return int(row["visible_deny"]==0 and prebit==0)
    raise ValueError("UNREGISTERED_CONTRACT_OR_OBJECTIVE")

def analyze_registered(id_,row):
    if not is_registered(id_,row):
        return {"case_id":id_,"status":"MODEL_UNSUPPORTED",
                "reason":"F0_UNREGISTERED_OR_CHANGED_SCIENTIFIC_OBJECT"}
    result={
        "schema":"eeq-f0-intervention-conditioned-identifiability-v1",
        "case_id":id_,
        "objective_scope":row["objective"],
        "registered_action":row["action"],
        "registered_transition_mode":row["mode"],
        "evidence_class":EVIDENCE_CLASS,
        "observed_native_outcomes":0,
        "new_G5_cases":0,
        "global_k8s_admission_claim_authorized":False,
        "external_native_source_roster_qualifier_proven":False,
        "full_B9_gets_same_lawful_observation_model":True,
        "method_novelty_established":False,
    }
    grant=authorized_grant(row)
    if id_=="I05":
        if grant:
            raise ValueError("UNROOTED_CYCLE_WAS_WRONGLY_TREATED_AS_AUTHORITY")
        return {
          **result,"status":"ROOTLESS_DELEGATION_REFUSE",
          "least_trust_fixed_point":list(least_anchored_authorities()),
          "independent_grant_anchor_present":False,
          "authoritative_grant_actions_available":0,
          "observation_classes":0,
          "worlds_considered":2,
          "source_complete_negative_certified":False,
          "actor_not_authorized_is_NOT_a_native_REJECT":True,
        }
    records=[]
    partitions=defaultdict(list)
    for i,prebit in enumerate(row["pre_bits"]):
        original=initial_world(prebit)
        after=transition(original,row["action"],row["mode"],grant)
        obs=lawful_observation(row,after)
        value=requested_claim(row,prebit,after)
        record={
            "world":"w"+str(i),"pre_hidden_effect":prebit,
            "after_physical_state":after,"lawful_observation":obs,
            "registered_objective_effect":value,
        }
        records.append(record)
        partitions[json.dumps(obs,sort_keys=True)].append(record)
    ambiguous=[]
    for members in partitions.values():
        vals={rec["registered_objective_effect"] for rec in members}
        if len(vals)>1:
            a=next(x for x in members if x["registered_objective_effect"]==0)
            b=next(x for x in members if x["registered_objective_effect"]==1)
            ambiguous.append({
                "worlds":[a["world"],b["world"]],
                "opposite_target_effects":[0,1],
                "identical_lawful_post_observations":True,
                "observation":a["lawful_observation"],
                "pre_target_values":[a["pre_hidden_effect"],b["pre_hidden_effect"]],
                "same_complete_successor_state":(
                    a["after_physical_state"]==b["after_physical_state"]),
            })
    outcomes_by_observation=[
        {"observation":members[0]["lawful_observation"],
         "possible_contract_effects":sorted({
             m["registered_objective_effect"] for m in members}),
         "represented_worlds":[m["world"] for m in members]}
        for members in partitions.values()
    ]
    expected=REGISTERED_EXPECTED[id_]
    status=expected if ((expected in (
         "UNIDENTIFIABLE_WITH_LAWFUL_OBSERVATIONS",
         "UNIDENTIFIABLE_AFTER_DESTRUCTIVE_INTERVENTION",
         "GLOBAL_NEGATIVE_NOT_IDENTIFIABLE_WITHOUT_CLOSURE")
         and len(ambiguous)>0) or
         (expected not in (
         "UNIDENTIFIABLE_WITH_LAWFUL_OBSERVATIONS",
         "UNIDENTIFIABLE_AFTER_DESTRUCTIVE_INTERVENTION",
         "GLOBAL_NEGATIVE_NOT_IDENTIFIABLE_WITHOUT_CLOSURE")
         and len(ambiguous)==0)) else "F0_MODEL_COUNTEREXAMPLE_TO_FROZEN_HYPOTHESIS"
    return {
      **result,"status":status,
      "worlds_considered":2,"observation_classes":len(partitions),
      "ambiguous_post_observation_classes":len(ambiguous),
      "identical_observation_opposite_preimage_pair":ambiguous,
      "worlds":records,"partitions":outcomes_by_observation,
      "independent_grant_anchor_present":bool(grant),
      "source_complete_negative_certified":False,
      "converged_pre_histories_erase_pre_target":(
          id_=="I03" and bool(ambiguous)
          and ambiguous[0]["same_complete_successor_state"]),
      "all_pre_worlds_separated_by_lawful_post_observation":(
          id_=="I02" and len(partitions)==2 and not ambiguous),
      "post_effect_certain_from_action_semantics_not_pre_recovery":(
          id_=="I04" and len(partitions)==1 and not ambiguous),
    }

def analyze_all():
    return [analyze_registered(i,x) for i,x in scenarios().items()]
