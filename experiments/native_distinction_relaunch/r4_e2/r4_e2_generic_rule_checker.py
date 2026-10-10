#!/usr/bin/env python3
"""R4-E2 structural typed AND/OR/THRESHOLD proof IR checker.

No TUF/K8s imports, expected signer set, policy name, keyID, source
qualification or native decision labels. Only checks the declared finite
bounded-source/claim IR; CANNOT independently authorize native source closure.
"""
import hashlib,json,re
SHA=re.compile(r"^[0-9a-f]{64}$")
NODES={"ATOM","AND","OR","THRESHOLD"}
SCHEMA="eeq-r4-e2-native-source-qualified-rule-ir-v1"

class Unsupported(Exception):pass

def require(flag,reason):
    if not flag:raise Unsupported(reason)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def check_program(program):
    try:
        require(isinstance(program,dict) and program.get("schema")==SCHEMA,
                "IR_UNREGISTERED_SCHEMA")
        require(program.get("domain") in ("TUF_ROOT_UPDATE","K8S_SCOPED_VAP_DENY"),
                "IR_UNREGISTERED_DOMAIN")
        require(isinstance(program.get("case_id"),str) and program["case_id"],
                "IR_MISSING_CASE_ID")
        require(isinstance(program.get("registered_contract"),str)
                and bool(program["registered_contract"]),"IR_UNREGISTERED_CONTRACT")
        sources=program.get("verified_source_sha256")
        require(isinstance(sources,dict) and len(sources)>=2 and all(
            isinstance(k,str) and bool(k) and isinstance(v,str) and SHA.fullmatch(v)
            for k,v in sources.items()),"IR_MISSING_OR_BAD_NATIVE_SOURCE_HASH")
        require(program.get("source_closure_is_author_independently_attested") is False,
                "IR_UNSUPPORTED_AUTHORITY_COMPLETENESS_ASSERTION")
        require(program.get("native_labels_read") is False and
                program.get("evidence_class")==
                "PREVIOUS_NATIVE_DEVELOPMENT_SOURCE_BYTES_NEW_COMPILER",
                "IR_ORACLE_LEAKAGE_OR_SCOPE")
        seen=set()
        def evaluate(node):
            require(isinstance(node,dict) and node.get("op") in NODES,
                    "IR_INVALID_RULE_OPERATOR")
            op=node["op"]
            if op=="ATOM":
                require(set(node)=={"op","id","value","source_refs","obligation"},
                        "IR_ATOM_FIELDS_INVALID")
                ident=node["id"]
                require(isinstance(ident,str) and ident and ident not in seen,
                        "IR_DUPLICATE_ATOM_ID")
                seen.add(ident)
                require(type(node["value"]) is bool,"IR_ATOM_NOT_QUALIFIED_BOOLEAN")
                refs=node["source_refs"]
                require(isinstance(refs,list) and refs and len(refs)==len(set(refs))
                        and all(r in sources for r in refs),"IR_SOURCE_LINEAGE_NOT_VERIFIED")
                require(isinstance(node["obligation"],str) and node["obligation"],
                        "IR_MISSING_NATIVE_QUALIFICATION_TYPE")
                return node["value"]
            children=node.get("children")
            require(isinstance(children,list) and len(children)>0 and len(children)<=128,
                    "IR_EMPTY_OR_EXCESSIVE_RULE_CHILDREN")
            if op=="THRESHOLD":
                k=node.get("k")
                require(set(node)=={"op","k","children"} and type(k) is int
                        and 1<=k<=len(children),"IR_INVALID_THRESHOLD")
                require(all(isinstance(child,dict) and child.get("op")=="ATOM"
                            for child in children),"IR_THRESHOLD_NOT_INDEPENDENT_ROLE_ATOMS")
                return sum(int(evaluate(x)) for x in children)>=k
            require(set(node)=={"op","children"},"IR_RULE_FIELDS_INVALID")
            results=[evaluate(x) for x in children]
            return all(results) if op=="AND" else any(results)
        result=evaluate(program.get("formula"))
        require(bool(seen),"IR_EMPTY_PROOF")
        return {"status":"QUALIFIED_BOUNDED_RULE_EVALUATED",
                "case_id":program["case_id"],"domain":program["domain"],
                "scope":program["registered_contract"],
                "scoped_effect_bit":result,"checked_proof_atoms":len(seen),
                "no_untracked_source_closure":False,
                "global_k8s_admission_accept_authorized":False,
                "native_domain_semantic_compiler_automatically_general":False,
                "fully_informed_B9_may_use_same_code":True,
                "original_g5_increment":0}
    except Unsupported as e:
        return {"status":"MODEL_UNSUPPORTED",
                "reason":str(e),
                "global_k8s_admission_accept_authorized":False,
                "original_g5_increment":0}
    except (KeyError,TypeError,AttributeError,ValueError) as e:
        return {"status":"MODEL_UNSUPPORTED",
                "reason":"IR_MALFORMED_"+type(e).__name__,
                "global_k8s_admission_accept_authorized":False,
                "original_g5_increment":0}

def verify_registered_pair_sets(tuf,k8s):
    require(isinstance(tuf,list) and len(tuf)==8,
            "E2_TUF_DEVELOPMENT_DENOMINATOR_NOT_8")
    require(isinstance(k8s,list) and len(k8s)==8,
            "E2_K8S_DEVELOPMENT_DENOMINATOR_NOT_8")
    outcomes={}
    for p in tuf+k8s:
        require(p.get("case_id") not in outcomes,"E2_DUPLICATE_CROSS_DOMAIN_CASE")
        verdict=check_program(p)
        require(verdict["status"]=="QUALIFIED_BOUNDED_RULE_EVALUATED",
                "E2_UNSUPPORTED_SOURCE_PROGRAM:"+str(verdict))
        outcomes[p["case_id"]]=verdict
    return outcomes
