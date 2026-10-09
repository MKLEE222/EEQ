#!/usr/bin/env python3
"""READ-ONLY R2A/R2B native evidence-envelope audit; not a new native oracle.

Safeguards: no exceptions/omissions are credited as matches, no TUF or
Kubernetes-specific scientific advantage is inferred from common JSON.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path

A_WORLDS=("WORLD_GATE","WORLD_STANDBY")
A_PHASES=("CURRENT","AFTER_BINDING_MUTATION")
A_SAS=("flux","default")
B_INITIALS=("A","B")
B_ACTIONS=("submit-candidate-2","submit-candidate-3")


def require(value,reason):
    if not value:
        raise ValueError(reason)


def b_prefixes():
    return [()] + [(a,) for a in B_ACTIONS] + list(itertools.product(B_ACTIONS,repeat=2))


def unique_rows(rows,key_fn,expected,missing_code):
    out={}
    for row in rows:
        k=key_fn(row)
        require(k not in out,"DUPLICATE_"+missing_code+": "+str(k))
        out[k]=row
    require(set(out)==expected,missing_code+": registered="+str(len(expected))+
            " observed="+str(len(out)))
    return out


def audit_a(data):
    require(data.get("schema")=="eeq-r2a-k8s-native-vs-frozen-source-v1",
            "R2A_SCHEMA_MISMATCH")
    require(data.get("evidence_class")=="CONTROLLED_NATIVE_TWO_ISOLATED_CLUSTER_EPISODES",
            "R2A_EVIDENCE_CLASS_MISMATCH")
    require(data.get("status")=="CONTROLLED_NATIVE_A_CONFIRMED_B9_TIE",
            "R2A_NATIVE_DISPOSITION_NOT_SUCCESS")
    sm=data["summary"]
    require(sm.get("frozen_admission_denominator")==8 and
            sm.get("native_admission_matches")==8 and
            sm.get("native_admission_mismatches_or_unavailable")==0,
            "R2A_SCORE_NOT_8_OF_8")
    require(sm.get("episodes_completed")==2 and
            sm.get("verified_policy_transitions")==2,
            "R2A_NATIVE_MUTATION_OR_EPISODE_NOT_CERTIFIED")
    require(not data.get("infrastructure_failures"),"R2A_INFRASTRUCTURE_FAILURE_RETAINED")
    require(sm.get("current_decision_vectors_identical") is True and
            sm.get("future_decision_vectors_diverge_after_same_native_patch") is True and
            sm.get("source_qualification_distinction_verified") is True,
            "R2A_CONTRAST_OR_SOURCE_QUALIFICATION_UNSUPPORTED")
    require(sm.get("strong_b9_tie_predeclared") is True and
            sm.get("independent_novelty_advantage") is False and
            sm.get("full_R2_gate_pass") is False,
            "R2A_SCIENCE_B9_OR_FULL_GATE_MISREPRESENTED")
    expected={(w,p,sa) for w in A_WORLDS for p in A_PHASES for sa in A_SAS}
    cells=unique_rows(data["case_results"],
        lambda r:(r["world"],r["phase"],r["service_account"]),
        expected,"R2A_REGISTERED_CASE_SET")
    for k,r in cells.items():
        require(r["case_status"]=="MATCH" and
                r["source_only_predicted"]==r["native_observed"],
                "R2A_MISMATCH_OR_UNAVAILABLE: "+str(k))
    require(cells["WORLD_GATE","AFTER_BINDING_MUTATION","flux"]
            ["native_attribution"]=="REGISTERED_VAP",
            "R2A_DIVERGENCE_NOT_ATTRIBUTED_TO_REGISTERED_VAP")
    expected_vectors={
        ("WORLD_GATE","CURRENT"):("ACCEPT","ACCEPT"),
        ("WORLD_STANDBY","CURRENT"):("ACCEPT","ACCEPT"),
        ("WORLD_GATE","AFTER_BINDING_MUTATION"):("REJECT","ACCEPT"),
        ("WORLD_STANDBY","AFTER_BINDING_MUTATION"):("ACCEPT","ACCEPT"),
    }
    for (w,p),tuple_expected in expected_vectors.items():
        obs=tuple(cells[w,p,sa]["native_observed"] for sa in A_SAS)
        require(obs==tuple_expected,"R2A_CURRENT_OR_FUTURE_VECTOR_DRIFT: "+str((w,p)))
    for w in A_WORLDS:
        ws=data["world_summaries"].get(w) or {}
        require(ws.get("episode_status")=="NATIVE_EPISODE_COMPLETED" and
                ws.get("policy_transition_supported") is True and
                ws.get("num_admission_rows")==4 and
                ws.get("num_activation_probes",0)>=1,
                "R2A_CLUSTER_OR_SOURCE_MUTATION_MISSING: "+w)
    wit=data["witness"]
    require(wit["registered_action"]=="PATCH_BINDING_SELECTOR_TO_GATE" and
            wit["pre_action_flux_gate"]=="ACCEPT" and
            wit["pre_action_flux_standby"]=="ACCEPT" and
            wit["post_action_flux_gate"]=="REJECT" and
            wit["post_action_flux_standby"]=="ACCEPT" and
            wit["native_binding_resource_mutation_evidence_required"] is True,
            "R2A_SEPARATOR_WITNESS_NOT_CHECKABLE")
    return {
        "family":"Kubernetes VAP+Binding",
        "evidence_class":"CONTROLLED_NATIVE_DEVELOPMENT",
        "contract":"Pod CREATE admission under actual binding selector mutation",
        "horizon":1,
        "native_denominator":8,"native_matches":8,"native_mismatches":0,
        "native_mutations_verified":2,
        "distinction_kind":"CURRENT_EQUAL_FUTURE_SEPARATED",
        "witness":{
            "action":"PATCH_BINDING_SELECTOR_TO_GATE",
            "challenge":"Pod CREATE, serviceAccountName=flux",
            "current":["ACCEPT","ACCEPT"],
            "after":["REJECT","ACCEPT"],
            "source_qualification":"namespace eeq.r2a/armed gate vs standby"
        },
        "source_semantics_independently_reverified_here":False
    }


def audit_b(data):
    require(data.get("schema")=="eeq-r2b-pinned-source-vs-independent-native-v1",
            "R2B_SCHEMA_MISMATCH")
    require(data.get("evidence_class")=="CONTROLLED_NATIVE_DEVELOPMENT",
            "R2B_EVIDENCE_CLASS_MISMATCH")
    require(data.get("status")=="CONTROLLED_NATIVE_B_CONFIRMED_B9_TIE",
            "R2B_NATIVE_DISPOSITION_NOT_SUCCESS")
    sm=data["summary"]
    require(sm.get("native_challenge_cells")==28 and
            sm.get("native_root_update_matches")==28 and
            sm.get("native_root_update_nonmatches")==0,
            "R2B_SCORE_NOT_28_OF_28")
    require(sm.get("native_targets_authority_cells")==4 and
            sm.get("native_targets_role_matches")==4 and
            sm.get("native_targets_role_nonmatches")==0,
            "R2B_TARGETS_AUTHORITY_NOT_4_OF_4")
    require(sm.get("registered_initial_states")==2 and
            sm.get("prefixes_per_state")==7 and
            sm.get("unresolved_prefix_cells")==0 and
            sm.get("complete_future_trace_equivalence") is True,
            "R2B_FUTURE_EQUIVALENCE_NOT_COMPLETE")
    require(sm.get("strong_b9_tie_predeclared") is True and
            sm.get("classical_quotient_tie_predeclared") is True and
            sm.get("novelty_advantage_established") is False and
            sm.get("R2_A_future_separation_demonstrated") is False and
            sm.get("R2_FULL_GATE_PASS") is False,
            "R2B_UNJUSTIFIED_NOVELTY_OR_GATE_PROMOTION")
    required={
        (ini,p,a) for ini in B_INITIALS for p in b_prefixes() for a in B_ACTIONS
    }
    result=unique_rows(data["root_action_comparisons"],
        lambda r:(r["initial_state"],tuple(r["action_prefix"]),r["challenge_action"]),
        required,"R2B_REGISTERED_NATIVE_CHALLENGE_SET")
    for k,row in result.items():
        require(row["status"]=="MATCH" and row["observed"]==row["expected"] and
                row["expected"] in ("ACCEPT","REJECT") and
                not row.get("prefix_errors") and
                row.get("actual_next_canonical_signed_sha256")==
                    row.get("expected_next_canonical_signed_sha256"),
                "R2B_NATIVE_ACTION_OR_NEXT_SOURCE_INVALID: "+str(k))
    # Independent source-specific scorer already verified canonical source SHA.
    # Here check full cross-history vectors for EVERY registered word.
    for p in b_prefixes():
        left=tuple(result["A",p,a]["observed"] for a in B_ACTIONS)
        right=tuple(result["B",p,a]["observed"] for a in B_ACTIONS)
        require(left==right,"R2B_FUTURE_NATIVE_VECTOR_DIFFERENCE: "+str(p))
    expected_targets={
        ("A","TARGETS_A"):"QUALIFIED",
        ("A","TARGETS_B"):"UNQUALIFIED",
        ("B","TARGETS_A"):"UNQUALIFIED",
        ("B","TARGETS_B"):"QUALIFIED"
    }
    target=unique_rows(data["targets_authority_comparisons"],
        lambda r:(r["initial_state"],r["target_document"]),
        set(expected_targets),"R2B_TARGETS_CROSS_CERTIFICATE_INCOMPLETE")
    for k,v in expected_targets.items():
        row=target[k]
        require(row["status"]=="MATCH" and
                row["predicted_qualified"]==row["native_qualified"]==v,
                "R2B_TARGET_QUALIFICATION_PAIR_INVALID: "+str(k))
    require(data.get("old_G4_unchanged") is True and
            data.get("new_G5_cases")==0 and
            data.get("no_prospective_holdout_claim") is True,
            "R2B_G4_OR_HOLDOUT_CONTAMINATION")
    return {
        "family":"TUF controlled signed root/targets",
        "evidence_class":"CONTROLLED_NATIVE_DEVELOPMENT",
        "contract":"root-update-only, full fixed proposals and horizon 2",
        "horizon":2,
        "native_denominator":28,"native_matches":28,"native_mismatches":0,
        "targets_role_qualification_certificates":4,
        "distinction_kind":"AUTHORITY_DIFFERENT_REGISTERED_FUTURE_EQUIVALENT",
        "witness":{
            "different_claim_authority":"targets role signer A vs B",
            "root_update_future_equal":True,
            "registered_prefixes_per_anchor":7,
            "registered_actions":list(B_ACTIONS),
            "native_targets_cross_qualified":["A:A","B:B"],
            "native_targets_cross_unqualified":["A:B","B:A"]
        },
        "source_semantics_independently_reverified_here":False
    }


def run(a,b):
    return {
        "schema":"eeq-r3-archival-native-witness-envelope-v1",
        "evidence_role":"RETROSPECTIVE_READ_ONLY_NATIVE_RESULT_CONSISTENCY",
        "method_novelty_claim":"NONE_ESTABLISHED",
        "source_to_mechanism_soundness_proved_by_this_envelope":False,
        "native_oracle_reexecuted":False,
        "old_G4_modified":False,
        "A":audit_a(a),
        "B":audit_b(b),
        "status":"R2_NATIVE_A_AND_B_CROSS_FAMILY_CONFIRMED",
        "gate_dispositions":{
            "R2_full_per_family_A_and_B":"OPEN",
            "R3_unified_label_blind_native_compiler":"NOT_DEMONSTRATED",
            "R3_per_family_refusal_multisupport":"OPEN",
            "R4_matched_fully_informed_B9":"NOT_SCORED",
            "R4_novelty_superiority":"UNPROVEN",
            "R5_unseen_family":"UNOPENED"
        },
        "strong_B9":"B9_TIE_EXPECTED_NOT_MATCHED_COST_BENCHMARK",
        "classical_quotient":"FUTURE_EQUIVALENCE_NOT_ALGORITHM_NOVELTY",
        "required_next_test":"LABEL_BLIND_COMMON_SOURCE_TO_CERTIFICATE_COMPILER_AND_FULLY_INFORMED_B9"
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--r2a",required=True)
    p.add_argument("--r2b",required=True)
    p.add_argument("--out",required=True)
    v=p.parse_args()
    result=run(json.loads(Path(v.r2a).read_text(encoding="utf8")),
               json.loads(Path(v.r2b).read_text(encoding="utf8")))
    Path(v.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                           encoding="utf8")
    print(json.dumps({
        "status":result["status"],
        "R2A":result["A"]["native_denominator"],
        "R2B":result["B"]["native_denominator"],
        "R3_common_compiler":result["gate_dispositions"][
            "R3_unified_label_blind_native_compiler"],
        "B9":result["strong_B9"]
    },sort_keys=True))


if __name__=="__main__":
    main()
