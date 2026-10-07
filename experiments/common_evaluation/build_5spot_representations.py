#!/usr/bin/env python3
"""Materialize frozen G4 representations for the 5-Spot Kubernetes carrier.

Representation construction reads only the semantic signature. The native
action is copied into the output only after all representations are built and
is never consulted by any branch in represent().
"""
import argparse
import json
from pathlib import Path

IDS=[f"B{i}" for i in range(11)]+[f"O{i}" for i in range(1,9)]
NA="__NOT_APPLICABLE__"
DOMAIN="K8s:5spot-vap"

def forecast(s):
    if s["binding_scope"]!="scoped":
        return "ACCEPT"
    ident=s["identity"]
    p=s["security_profile"]
    if p=="baseline":
        return "ACCEPT"
    if p in {"host_network","host_ipc","privileged_rw","cap_sys_admin"}:
        return "REJECT"
    if p=="host_pid":
        return "ACCEPT" if ident in {"kata","reclaim"} else "REJECT"
    if p=="privileged_ro":
        return "ACCEPT" if ident=="kata" else "REJECT"
    if p=="hostpath_root":
        return "ACCEPT" if ident=="kata" else "REJECT"
    if p=="hostpath_proc":
        return "ACCEPT" if ident=="reclaim" else "REJECT"
    if p=="cap_net_admin":
        return "ACCEPT" if ident=="reclaim" else "REJECT"
    if p=="run_as_root":
        return "ACCEPT" if ident in {"kata","reclaim"} else "REJECT"
    raise ValueError(f"unregistered 5-Spot profile {p}")

def profile_features(p):
    return {
        "host_network": p=="host_network",
        "host_ipc": p=="host_ipc",
        "host_pid": p=="host_pid",
        "privileged": p in {"privileged_ro","privileged_rw"},
        "read_only_root_fs": False if p=="privileged_rw" else True,
        "hostpath": "/" if p=="hostpath_root" else ("/proc" if p=="hostpath_proc" else None),
        "capability": "NET_ADMIN" if p=="cap_net_admin" else ("SYS_ADMIN" if p=="cap_sys_admin" else None),
        "explicit_root": p=="run_as_root",
    }

def represent(s):
    r={k:NA for k in IDS}
    reasons={}
    scope=s["binding_scope"]
    namespace=s["namespace"]
    sa=s["service_account"]
    ident=s["identity"]
    profile=s["security_profile"]
    feat=profile_features(profile)

    r["B0"]=s
    r["B1"]={
        "metadata_namespace":namespace,
        "service_account":sa,
        "security_profile":profile,
        "security_features":feat,
    }
    r["B3"]={
        "binding_scope":scope,
        "service_account_identity":ident,
    }
    r["B6"]={
        "binding_scope":scope,
        "namespace":namespace,
        "service_account":sa,
        "identity":ident,
        "security_profile":profile,
    }
    r["B7"]={"frozen_mechanism_forecast":forecast(s)}
    r["B8"]={
        "binding_applies":scope=="scoped",
        "is_kata_agent":ident=="kata",
        "is_reclaim_agent":ident=="reclaim",
        **feat,
    }
    r["B9"]={
        "binding_applies":scope=="scoped",
        "identity":ident,
        "security_profile":profile,
    }
    r["B10"]={
        "qualified_policy_source":{"binding_scope":scope=="scoped"},
        "claim_binding":{
            "service_account_identity":ident,
            "security_profile":profile,
            "security_features":feat,
        },
        "registered_action":"CREATE Pod",
    }
    r["O2"]={"security_profile":profile,"security_features":feat}
    r["O3"]={"binding_scope":scope,"service_account_identity":ident}

    fixed_reasons={
        "B2":"No authentication or cryptographic-validity distinction in registered Pod carrier",
        "B4":"One pinned policy source; no registered provenance alternatives",
        "B5":"No registered provenance alternatives",
        "O1":"One pinned policy source; source provenance has no variable distinction",
        "O4":"One-step admission carrier has no prior continuation history",
        "O5":"No future continuation contract in one-step admission carrier",
        "O6":"Grid scores the request, not a later action-induced evidence change",
        "O7":"One-step admission is the full registered horizon",
        "O8":"One registered matching VAP support mechanism",
    }
    for k,v in fixed_reasons.items():
        reasons[k]=v
    for k in IDS:
        if r[k]==NA and k not in reasons:
            raise ValueError(f"missing NA reason for {k}")
    return r,reasons

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("ledger",type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    ledger=json.loads(args.ledger.read_text(encoding="utf-8"))
    cases=[c for c in ledger["cases"] if c["signature"]["semantic_domain"]==DOMAIN]
    if len(cases)!=38:
        raise ValueError(f"expected 38 5-Spot semantic cases, got {len(cases)}")
    rows=[]
    for case in cases:
        s=case["signature"]["pre_action_state"]
        reps,reasons=represent(s)
        rows.append({
            "semantic_id":case["semantic_id"],
            "domain":DOMAIN,
            "native_action":case["native_action"],
            "representations":reps,
            "not_applicable_reasons":reasons,
        })
    payload={
        "schema":"eeq-g4-5spot-representations-v1",
        "status":"development post-native/pre-matrix freeze; native_action not used to construct representations",
        "b10_status":"adapter-state pilot; generic EEQ/WFC compiler integration pending",
        "rows":sorted(rows,key=lambda r:r["semantic_id"]),
    }
    args.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"rows":len(rows),"ids":len(IDS)},sort_keys=True))

if __name__=="__main__":
    main()
