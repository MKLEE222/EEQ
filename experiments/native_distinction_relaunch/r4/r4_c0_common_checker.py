#!/usr/bin/env python3
"""R4-C0 COMMON STRUCTURAL certificate verifier (not a semantics oracle).

Per-domain adapters MUST independently recheck original native/source
semantics. This core only enforces evidence identity, types, declared scope,
complete denominators, disposition and nonvacuous qualified obligations.
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

SHA=re.compile(r"^[0-9a-f]{64}$")
TUF_STATES=("s2a","s2b")
TUF_ACTIONS=("submit-root-3-a","submit-root-3-b",
  "submit-root-3-old-only","submit-root-3-new-only")
K8S_BRANCHES=("a","b")
K8S_PHASES=("current","after_native_label_update")
K8S_PROBES=("flux","default")
ALLOWED_EFFECTS={"ACCEPT","REJECT","SOURCE_UNAVAILABLE","MODEL_UNSUPPORTED"}
DOMAIN_OBLIGATIONS={
    "tuf_root_update":{
        "VERSION_CONTINUITY","TUF_OLD_ROOT_AUTHORITY",
        "TUF_NEW_ROOT_AUTHORITY",
    },
    "k8s_admission":{
        "K8S_REGISTERED_POD_CREATE","K8S_BINDING_NAMESPACE_SELECTOR",
        "K8S_RESTRICTED_CEL_VALIDATION",
        "K8S_NATIVE_NAMESPACE_ACTION",
    },
}
EXPECTED_ARTIFACTS={
    "tuf_root_update":(11608811184,11609456107),
    "k8s_admission":(11604865804,11604423996),
}


def require(cond,why):
    if not cond:
        raise ValueError(why)


def issha(v):
    return isinstance(v,str) and SHA.fullmatch(v) is not None


def check_certificate(cert):
    require(cert.get("schema")=="eeq-r4-qualified-transition-certificate-v0",
        "UNREGISTERED_COMMON_CERTIFICATE_SCHEMA")
    domain=cert.get("domain")
    require(domain in DOMAIN_OBLIGATIONS,"UNKNOWN_CERTIFICATE_DOMAIN")
    require(isinstance(cert.get("contract_id"),str) and
            len(cert["contract_id"])>=8,"MISSING_CONTRACT_ID")
    require(isinstance(cert.get("case_id"),str) and
            cert["case_id"],"MISSING_CASE_ID")
    refs=cert.get("sources",{})
    require(isinstance(refs,dict) and len(refs)>=2 and
            all(isinstance(k,str) and issha(v) for k,v in refs.items()),
            "MISSING_OR_BAD_SOURCE_HASH")
    for key in ("original_state","action","successor_state",
                "native_successor","verifier_domain"):
        require(isinstance(cert.get(key),str) and
                bool(cert[key]),"MISSING_CERTIFICATE_"+key)
    outcome=cert.get("outcome")
    require(outcome in ALLOWED_EFFECTS,"UNREGISTERED_CERTIFICATE_OUTCOME")
    require(cert.get("checker_outcome") in
            {"VERIFIED","MISMATCH","UNSUPPORTED"},
            "UNKNOWN_CERTIFICATE_CHECKER_RESULT")
    require(cert.get("native_observation") in
            {"ACCEPT","REJECT","NATIVE_ORACLE_AMBIGUOUS","SETUP_FAILURE"},
            "INVALID_NATIVE_OBSERVATION")
    if cert["checker_outcome"]=="VERIFIED":
        require(outcome in ("ACCEPT","REJECT") and
                outcome==cert["native_observation"] and
                cert["successor_state"]==cert["native_successor"],
                "UNVERIFIED_OR_UNSUPPORTED_CREDIT")
    obligations=cert.get("qualified_obligations")
    require(isinstance(obligations,list) and obligations,
            "CERTIFICATE_MISSING_DOMAIN_OBLIGATIONS")
    bytype={}
    for item in obligations:
        require(isinstance(item,dict) and
                item.get("type") in DOMAIN_OBLIGATIONS[domain] and
                item.get("type") not in bytype and
                isinstance(item.get("qualified"),bool),
                "UNTRUSTWORTHY_OR_DUPLICATE_PROOF_PREMISE")
        bytype[item["type"]]=item
    require(set(bytype)==DOMAIN_OBLIGATIONS[domain],
            "INCOMPLETE_DOMAIN_PROOF_PREMISES")
    if domain=="tuf_root_update":
        version=bytype["VERSION_CONTINUITY"]
        old=bytype["TUF_OLD_ROOT_AUTHORITY"]
        fresh=bytype["TUF_NEW_ROOT_AUTHORITY"]
        require(version.get("old_version")==2 and
                version.get("new_version")==3 and
                version["qualified"],"BAD_ROOT_VERSION_PROOF")
        for role in (old,fresh):
            ids=role.get("verified_unique_keyids")
            threshold=role.get("threshold")
            require(isinstance(ids,list) and
                    len(ids)==len(set(ids)) and
                    all(issha(x) for x in ids) and
                    isinstance(threshold,int) and threshold>=1 and
                    role["qualified"]==(len(ids)>=threshold),
                    "INCONSISTENT_TUF_SIGNER_THRESHOLD_PREMISE")
        inferred=("ACCEPT" if
                  old["qualified"] and fresh["qualified"] else "REJECT")
        require(outcome==inferred,"TUF_OUTCOME_CONTRADICTS_PROOF")
    else:
        pod=bytype["K8S_REGISTERED_POD_CREATE"]
        selector=bytype["K8S_BINDING_NAMESPACE_SELECTOR"]
        cel=bytype["K8S_RESTRICTED_CEL_VALIDATION"]
        native_update=bytype["K8S_NATIVE_NAMESPACE_ACTION"]
        require(pod["qualified"] and native_update["qualified"] and
                pod.get("pod_serviceaccount") in ("flux","default") and
                cel.get("predicate")=="serviceAccountName != flux",
                "UNSUPPORTED_K8S_CERTIFICATE_PREDICATE")
        require(isinstance(selector.get("binding_selector"),dict) and
                selector["binding_selector"],"MISSING_K8S_SELECTOR_PROOF")
        if "after_native_label_update" in cert["case_id"]:
            require(native_update.get("before_revision")!=
                    native_update.get("after_revision"),
                    "K8S_FUTURE_NATIVE_REVISION_NOT_CHANGED")
        predicted="REJECT" if (
            selector["qualified"] and not cel["qualified"]
        ) else "ACCEPT"
        require(outcome==predicted,"K8S_OUTCOME_CONTRADICTS_PROOF")
        require((pod["pod_serviceaccount"]=="flux") != cel["qualified"],
                "BAD_RESTRICTED_K8S_CEL_PROOF")
    p=cert.get("provenance")
    require(isinstance(p,dict) and
            (p.get("source_artifact_id"),p.get("native_artifact_id"))==
            EXPECTED_ARTIFACTS[domain],
            "CERTIFICATE_SOURCE_NATIVE_ARTIFACT_MISMATCH")


def check_all(tuf,k8s):
    require(tuf.get("schema")=="eeq-r4-c0-tuf-certificates-v0" and
            k8s.get("schema")=="eeq-r4-c0-k8s-certificates-v0",
            "C0_ADAPTER_SCHEMA_MISMATCH")
    require(tuf.get("native_calls_in_c0")==0 and
            k8s.get("native_calls_in_c0")==0,
            "C0_UNEXPECTED_NATIVE_EXECUTION")
    require(tuf.get("role_setup_count")==2 and
            k8s.get("unbound_controls_verified")==4 and
            k8s.get("actual_native_namespace_updates_verified")==2,
            "NATIVE_CONTROL_DENOMINATOR_NOT_PROVEN")
    expected_tuf={s+"|"+a for s in TUF_STATES for a in TUF_ACTIONS}
    expected_k8s={b+"|"+phase+"|"+probe for b in K8S_BRANCHES
                  for phase in K8S_PHASES for probe in K8S_PROBES}
    expected={
        "tuf_root_update":expected_tuf,
        "k8s_admission":expected_k8s,
    }
    all_rows=tuf["certificates"]+k8s["certificates"]
    observed={"tuf_root_update":set(),"k8s_admission":set()}
    for cert in all_rows:
        check_certificate(cert)
        d=cert["domain"]
        case=cert["case_id"]
        require(case not in observed[d],"DUPLICATE_COMMON_CERTIFICATE_"+case)
        observed[d].add(case)
    require(all(observed[d]==expected[d] for d in expected),
            "C0_16_CASES_INCOMPLETE_OR_OUT_OF_SCOPE")
    statuses=Counter(c["checker_outcome"] for c in all_rows)
    return {
        "schema":"eeq-r4-c0-cross-family-certificate-integration-result-v0",
        "evidence_class":"POST_NATIVE_REUSE_OF_ALREADY_SCORED_DEVELOPMENT",
        "common_certificate_rows":len(all_rows),
        "tuf_certificate_rows":len(tuf["certificates"]),
        "k8s_certificate_rows":len(k8s["certificates"]),
        "cross_family_checker_outcomes":dict(sorted(statuses.items())),
        "tuf_old_root_setups_from_archive":2,
        "k8s_unbound_controls_from_archive":4,
        "k8s_actual_namespace_actions_from_archive":2,
        "native_calls_in_this_new_integration":0,
        "semantic_domain_adapters_are_still_handwritten":True,
        "new_native_outcomes_scored":0,
        "original_g5_increment":0,
        "novel_automated_source_compiler_established":False,
        "improvement_over_full_b9_established":False,
        "r4_p3_evaluated":False,
        "scientific_status":(
            "C0_COMMON_CERTIFICATE_INTERFACE_FEASIBLE_ON_PREVIOUS_DEVELOPMENT"
            if statuses==Counter({"VERIFIED":16}) else
            "C0_CERTIFICATE_INTEGRATION_NOT_FULLY_VERIFIED"
        ),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tuf",required=True)
    p.add_argument("--k8s",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    tuf=json.loads(Path(a.tuf).read_text())
    k8s=json.loads(Path(a.k8s).read_text())
    report=check_all(tuf,k8s)
    Path(a.out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",
                           encoding="utf-8")
    print(json.dumps(report,sort_keys=True))


if __name__=="__main__":
    main()
