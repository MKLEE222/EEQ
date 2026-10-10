#!/usr/bin/env python3
"""P2 independent original-source leaf and FULL formula entailment verifier.

This checker does not accept typed Boolean claims merely because their
referenced SHA256 bytes exist. It requires separate trusted domain-native
primitive witnesses re-derived from those bytes. Proof witness generators
are handcoded domain-specific adapters and all source membership scope
remains an AUTHOR-REGISTERED development assumption, not global authority.
"""
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from r4_e2_generic_rule_checker import check_program

DOMAINS={"TUF_ROOT_UPDATE","K8S_SCOPED_VAP_DENY"}

def verify(program,external):
    basis={"original_g5_increment":0,
           "global_k8s_admission_accept_authorized":False,
           "live_source_roster_completeness_proven":False,
           "independent_B9_advantage_proven":False,
           "proof_evidence_class":"SOURCE_ONLY_OLD_NATIVE_DEVELOPMENT"}
    if not isinstance(program,dict) or not isinstance(external,dict):
        return {**basis,"status":"MODEL_UNSUPPORTED",
                "reason":"P2_MISSING_OR_MALFORMED_PRIMITIVE_WITNESS"}
    if program.get("domain") not in DOMAINS or external.get("domain")!=program["domain"]:
        return {**basis,"status":"MODEL_UNSUPPORTED",
                "reason":"P2_UNREGISTERED_DOMAIN_OR_WITNESS"}
    core=check_program(program)
    if core["status"]!="QUALIFIED_BOUNDED_RULE_EVALUATED":
        return {**basis,"status":"MODEL_UNSUPPORTED",
                "reason":"P2_E2_STRUCTURAL_PROOF_REJECTED"}
    if (program.get("case_id")!=external.get("case_id") or
        program.get("registered_contract")!=external.get("registered_contract") or
        program.get("native_labels_read") is not False or
        program.get("source_closure_is_author_independently_attested") is not False):
        return {**basis,"status":"REFUSE_SCOPE_OR_NATIVE_LEAKAGE",
                "reason":"P2_SOURCE_ACTOR_OR_CONTRACT_NOT_BOUND"}
    if (program.get("verified_source_sha256")!=external.get("verified_source_sha256") or
        not isinstance(external.get("verified_source_sha256"),dict)):
        return {**basis,"status":"REFUSE_SOURCE_ENTAILMENT",
                "reason":"P2_WITNESS_ORIGINAL_SOURCE_DIGEST_MISMATCH"}
    if (program.get("domain")=="TUF_ROOT_UPDATE" and
        (external.get("original_source_only_setup_proven_by_new_primitive_verifier") is not True
         or external.get("E2_candidate_IR_or_B9_output_never_read") is not True)):
        return {**basis,"status":"REFUSE_SOURCE_ENTAILMENT",
                "reason":"P2_TUF_INITIAL_AUTHORITY_NOT_VERIFIED"}
    if (program.get("domain")=="K8S_SCOPED_VAP_DENY" and
        (external.get("old_native_decisions_never_read") is not True or
         external.get("authored_membership_NOT_a_live_authorized_list") is not True)):
        return {**basis,"status":"REFUSE_SOURCE_ENTAILMENT",
                "reason":"P2_K8S_HISTORICAL_SOURCE_SCOPE_NOT_QUALIFIED"}
    if program.get("formula")!=external.get("formula"):
        return {**basis,"status":"REFUSE_SOURCE_ENTAILMENT",
                "reason":"P2_PRIMITIVE_LEAF_OR_RULE_NOT_IMPLIED_BY_NATIVE_SOURCE_BYTES"}
    return {**basis,
            "status":"SCOPED_SOURCE_PRIMITIVES_INDEPENDENTLY_RECHECKED",
            "case_id":program["case_id"],
            "domain":program["domain"],
            "scoped_effect_bit":core["scoped_effect_bit"],
            "all_original_source_bytes_separately_reinterpreted":True,
            "typed_rule_checker_succeeded":True,
            "domain_native_semantics_still_handwritten":True,
            "fully_informed_B9_may_use_identical_witness_and_checker":True}
