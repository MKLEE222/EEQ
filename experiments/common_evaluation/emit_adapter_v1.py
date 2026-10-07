#!/usr/bin/env python3
"""Emit G4 eeq-adapter-v1 instances for APT and Kubernetes carriers.

Family-specific logic ends here. No native label is consulted while building an
adapter. The generic WFC compiler consumes only the resulting C1/C2/C3 object.
"""
import argparse, json
from pathlib import Path

TUF_DOMAIN="TUF:bottlerocket-root"

def base(case):
    sig=case["signature"]
    return {
      "schema_version":"eeq-adapter-v1",
      "validity_boundary":{"V0_lawful_information":True},
      "C1_support_coverage":{},
      "C2_qualification_fidelity":{},
      "C3_transition_objective_fidelity":{
        "actions":[sig["registered_action"]],
        "native_action_vocabulary":sig["native_action_vocabulary"],
      },
    }

def emit(case):
    dom=case["signature"]["semantic_domain"]
    s=case["signature"]["pre_action_state"]
    a=base(case); c1=a["C1_support_coverage"]; c2=a["C2_qualification_fidelity"]; c3=a["C3_transition_objective_fidelity"]
    contract=case["signature"]["future_contract"]
    if dom=="APT:releaseinfo":
        c1.update({"claims":["releaseinfo-transition"],
          "support_items":[{"id":"current-InRelease","source_identity":"configured-Signed-By","provenance":"registered-apt-source"}],
          "compatibility":[{"claim":"releaseinfo-transition","support":"current-InRelease","compatible":True}]})
        q=bool(s["qualified"])
        c2.update({"qualification_predicates":[{"id":"signed-by-qualified","support":"current-InRelease","value":q}],
          "authentication_predicates":[{"id":"available-trust-verifies-current-signature","support":"current-InRelease","value":q}],
          "claim_binding":[{"claim":"releaseinfo-transition","support":"current-InRelease","protected_fields":["Origin","Label","Codename"]}]})
        c3.update({"successor_relation":{"protected_changed":s["protected_changed"]},"post_action_observations":{},
          "continuation_contract":{"contract_id":contract,"allow_global":s["allow_global"],"allow_fields":s["allow_fields"]}})
    elif dom=="K8s:flux-vap":
        c1.update({"claims":["pod-admission"],"support_items":[{"id":"flux-vap","source_identity":"pinned-public-policy"}],
                   "compatibility":[{"claim":"pod-admission","support":"flux-vap","compatible":True}]})
        c2.update({"qualification_predicates":[{"id":"tenant-scope","support":"flux-vap","value":s["tenant_label"]}],
                   "authentication_predicates":[],
                   "claim_binding":[{"claim":"pod-admission","support":"flux-vap","service_account":s["service_account"]}]})
        c3.update({"successor_relation":{"operation":s["operation"]},"post_action_observations":{},
                   "continuation_contract":{"contract_id":contract,"rule":"tenant-scope-forbids-flux-service-account"}})
    elif dom=="K8s:gcsfuse-vap":
        c1.update({"claims":["pod-admission"],"support_items":[{"id":"gcsfuse-vap","source_identity":"pinned-public-policy"}],
                   "compatibility":[{"claim":"pod-admission","support":"gcsfuse-vap","compatible":True}]})
        c2.update({"qualification_predicates":[{"id":"gcsfuse-scope","support":"gcsfuse-vap","value":bool(s["annotation"] and s["sidecar"])}],
                   "authentication_predicates":[],
                   "claim_binding":[{"claim":"pod-admission","support":"gcsfuse-vap","annotation":s["annotation"],"sidecar":s["sidecar"]}]})
        c3.update({"successor_relation":{"restart":s["restart"],"env":s["env"]},"post_action_observations":{},
                   "continuation_contract":{"contract_id":contract,"restart_required":"Always","env_required":"TRUE"}})
    elif dom=="K8s:volcano-vap":
        c1.update({"claims":["pod-admission"],"support_items":[{"id":"volcano-vap","source_identity":"pinned-public-policy"}],
                   "compatibility":[{"claim":"pod-admission","support":"volcano-vap","compatible":True}]})
        c2.update({"qualification_predicates":[{"id":"volcano-scheduler-scope","support":"volcano-vap","value":s["scheduler"]=="volcano"}],
                   "authentication_predicates":[],
                   "claim_binding":[{"claim":"pod-admission","support":"volcano-vap","min":s["min"],"max":s["max"]}]})
        c3.update({"successor_relation":{},"post_action_observations":{},
                   "continuation_contract":{"contract_id":contract,"valid_single_values":["absent","1","25%"],"mutual_exclusion":True}})
    elif dom=="K8s:5spot-vap":
        c1.update({"claims":["pod-admission"],"support_items":[{"id":"5spot-vap","source_identity":"pinned-public-policy"}],
                   "compatibility":[{"claim":"pod-admission","support":"5spot-vap","compatible":True}]})
        c2.update({"qualification_predicates":[
                       {"id":"namespace-binding-scope","support":"5spot-vap","value":s["binding_scope"]=="scoped"},
                       {"id":"service-account-identity","support":"5spot-vap","value":s["identity"]}],
                   "authentication_predicates":[],
                   "claim_binding":[{"claim":"pod-admission","support":"5spot-vap","security_profile":s["security_profile"]}]})
        c3.update({"successor_relation":{},"post_action_observations":{},
                   "continuation_contract":{"contract_id":contract,"registered_identity":s["identity"]}})
    else:
        raise ValueError(f"unsupported non-TUF domain {dom}")
    return a

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("ledger",type=Path); ap.add_argument("--out",required=True,type=Path); args=ap.parse_args()
    ledger=json.loads(args.ledger.read_text())
    rows=[]
    for case in ledger["cases"]:
        dom=case["signature"]["semantic_domain"]
        if dom==TUF_DOMAIN: continue
        adapter=emit(case)  # native_action is deliberately unavailable to emit()
        rows.append({"semantic_id":case["semantic_id"],"domain":dom,"adapter":adapter,"native_action":case["native_action"]})
    args.out.write_text(json.dumps({"schema":"eeq-adapter-instance-set-v1","rows":rows},indent=2,sort_keys=True)+"\n")
    print(json.dumps({"rows":len(rows),"domains":sorted({r["domain"] for r in rows})}))

if __name__=="__main__": main()
