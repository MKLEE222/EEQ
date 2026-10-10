#!/usr/bin/env python3
"""F0 source-free foundational preimage and intervention result emitter.

Six pre-frozen abstract countermodels only; no native source labels and no
method-originality or full B9 dominance claim. Independently verify all
six with separately implemented B9-eligible world-trace semantics.
"""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path

from f0_registry import scenarios,REGISTERED_EXPECTED,EVIDENCE_CLASS
from f0_intervention_semantics import analyze_registered
from f0_independent_b9_preimage_oracle import (
    independently_verify,diagnostic_pinned_trust_rotation,
    diagnostic_positive_local_deny,reference_anchored
)

SCIENTIFIC_STATUS="F0_ENDOGENOUS_OBSERVATION_COUNTERMODEL_REDUCIBLE_TO_EPISTEMIC_PLANNING_B9_TIE"

def evidence():
    frozen=scenarios()
    if len(frozen)!=6 or set(frozen)!=set(REGISTERED_EXPECTED):
        raise ValueError("F0_ORIGINAL_SIX_FALSIFIERS_CHANGED")
    rows=[]
    for id_,input_ in frozen.items():
        candidate=analyze_registered(id_,input_)
        if candidate["status"]!=REGISTERED_EXPECTED[id_]:
            raise ValueError("F0_PRE_FROZEN_CAUSAL_CLAIM_KILLED:"+id_)
        proof=independently_verify(candidate,input_)
        rows.append({"registered_case":id_,"frozen_spec":input_,
                     "candidate":candidate,
                     "independent_fully_informed_B9":proof})
    statuses=Counter(row["candidate"]["status"] for row in rows)
    if len(statuses)!=6 or any(n!=1 for n in statuses.values()):
        raise ValueError("F0_PRE_FROZEN_SIX_CATEGORIES_NOT_OBSERVED")
    inter=[r["candidate"] for r in rows if r["registered_case"]=="I03"][0]
    if not inter["converged_pre_histories_erase_pre_target"]:
        raise ValueError("F0_INFORMATION_DESTRUCTION_SEPARATION_NOT_ESTABLISHED")
    control=diagnostic_pinned_trust_rotation()
    if not control["byte_identity_preserved"] or control["after_current_qualified"] is not False:
        raise ValueError("F0_AUTHORITY_QUALIFICATION_CONTROL_WRONG")
    if reference_anchored(set()):
        raise ValueError("F0_SELF_AUTHORIZED_DELEGATION_CYCLE_WAS_ACCEPTED")
    summary={
     "schema":"eeq-f0-endogenous-evidence-foundational-audit-v1",
     "evidence_class":EVIDENCE_CLASS,
     "preimplementation_freeze_commit":"e7aff530a6a393f4b44ff78d79e91d2faa51390d",
     "registered_synthetic_foundational_countermodels":6,
     "executed_countermodels":len(rows),
     "each_countermodel_has_two_lawful_initial_possible_worlds":True,
     "full_B9_equal_lawful_information_independent_reference_ties":6,
     "I01_static_unidentifiable":True,
     "I02_noninterfering_read_authorization_recovers_pre":True,
     "I03_destructive_observation_action_erases_pre_identification":True,
     "I03_complete_post_action_states_equal":True,
     "I04_post_effect_certain_not_pre":True,
     "I05_rootless_authority_cycle_refused":True,
     "I06_open_world_global_negative_refused":True,
     "source_bytes_stable_during_trust_rotation_current_qualification_can_change":True,
     "positive_scoped_deny_survives_hidden_uncertain_additional_deny":(
       diagnostic_positive_local_deny(1,None)=="SCOPED_DENY_WITNESSED"),
     "negative_scoped_no_deny_does_not_authorize_global_k8s_accept":True,
     "native_calls":0,
     "old_G5_case_increment":0,
     "old_G8_case_increment":0,
     "fifth_family_unseen_holdout_opened":False,
     "independent_P3_maintainer_trial_executed":False,
     "native_qualification_and_external_source_inventory_satisfied":False,
     "dynamic_epistemic_logic_and_epistemic_planning_prior_art_reduction":True,
     "proof_of_new_nonreducible_EEQ_theorem":False,
     "strong_B9_independent_value_proven":False,
     "scientific_status":SCIENTIFIC_STATUS,
     "known_standard_reduction":(
         "finite_deterministic_transition+legal_observation_preimage;"
         "noninjective_poststate_map_prevents_preclaim_recovery;"
         "rooted_trust_delegation_least_fixpoint;"
         "partial-information_negative_source_certain-answers"
     ),
     "epistemic_limits":(
         "toy root/grant/observation action grammar is not actual TUF or "
         "Kubernetes RBAC/VAP API; no native current authority claim"
     ),
     "historical_G4_G5_G6_G8_unchanged":True,
    }
    return summary,rows,control

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    root=Path(args.out);root.mkdir(parents=True,exist_ok=True)
    summary,rows,control=evidence()
    for name,value in (
      ("F0_FOUNDATIONAL_STATUS.json",summary),
      ("F0_ALL_SIX_CAUSAL_COUNTERMODELS.json",rows),
      ("F0_SOURCE_EPOCH_QUALIFICATION_CONTROL.json",control)):
        (root/name).write_text(json.dumps(value,sort_keys=True,indent=2)+"\n")
    names=[
       "F0_FOUNDATIONAL_STATUS.json",
       "F0_ALL_SIX_CAUSAL_COUNTERMODELS.json",
       "F0_SOURCE_EPOCH_QUALIFICATION_CONTROL.json",
    ]
    (root/"F0_SHA256_MANIFEST.txt").write_text(
       "".join(hashlib.sha256((root/name).read_bytes()).hexdigest()+
               "  "+name+"\n" for name in names))
    print(json.dumps({k:summary[k] for k in (
       "registered_synthetic_foundational_countermodels",
       "full_B9_equal_lawful_information_independent_reference_ties",
       "I03_destructive_observation_action_erases_pre_identification",
       "proof_of_new_nonreducible_EEQ_theorem",
       "scientific_status")},sort_keys=True))

if __name__=="__main__":main()
