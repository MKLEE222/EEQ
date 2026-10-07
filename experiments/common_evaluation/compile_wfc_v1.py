#!/usr/bin/env python3
"""Generic EEQ/WFC frontier compiler for eeq-adapter-v1 instances.

There is intentionally no domain/family branch in compile_wfc(). The compiler
does not claim globally minimal coding or minimum bits. It compiles the
declared C1 support/compatibility, C2 qualification/binding, and C3
transition/continuation semantics into a canonical future-decision frontier.
"""
import argparse, json
from collections import defaultdict
from pathlib import Path

FORBIDDEN={"scored_native_outcome","post_hoc_expected_label","reviewer_only_annotation","future_information_unavailable_at_decision_time"}

def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sorted_objs(xs): return sorted(xs,key=canon)

def reject_forbidden(v,path=""):
    if isinstance(v,dict):
        for k,x in v.items():
            if k in FORBIDDEN: raise ValueError(f"forbidden adapter field {path}/{k}")
            reject_forbidden(x,path+"/"+k)
    elif isinstance(v,list):
        for i,x in enumerate(v): reject_forbidden(x,f"{path}/{i}")

def compile_wfc(adapter):
    if adapter.get("schema_version")!="eeq-adapter-v1": raise ValueError("wrong adapter schema")
    reject_forbidden(adapter)
    c1=adapter["C1_support_coverage"]; c2=adapter["C2_qualification_fidelity"]; c3=adapter["C3_transition_objective_fidelity"]
    supports={x["id"]:x for x in c1.get("support_items",[])}
    quals=defaultdict(list); auths=defaultdict(list); binds=defaultdict(list)
    for q in c2.get("qualification_predicates",[]):
        sid=q.get("support"); quals[sid].append({k:v for k,v in q.items() if k!="support"})
    for q in c2.get("authentication_predicates",[]):
        sid=q.get("support"); auths[sid].append({k:v for k,v in q.items() if k!="support"})
    for b in c2.get("claim_binding",[]):
        binds[(b.get("claim"),b.get("support"))].append({k:v for k,v in b.items() if k not in {"claim","support"}})
    claim_frontier=[]
    for claim in sorted(c1.get("claims",[])):
        routes=[]
        for edge in c1.get("compatibility",[]):
            if edge.get("claim")!=claim: continue
            sid=edge.get("support")
            if sid not in supports: raise ValueError(f"unknown support {sid}")
            src=supports[sid]
            routes.append({
              "support_id":sid,
              "source_identity":src.get("source_identity"),
              "provenance":src.get("provenance"),
              "compatible":bool(edge.get("compatible")),
              "authentication":sorted_objs(auths[sid]),
              "qualification":sorted_objs(quals[sid]),
              "claim_binding":sorted_objs(binds[(claim,sid)]),
            })
        claim_frontier.append({"claim":claim,"routes":sorted_objs(routes)})
    return {
      "claim_frontier":claim_frontier,
      "transition_frontier":{
        "actions":c3.get("actions",[]),
        "successor_relation":c3.get("successor_relation",{}),
        "post_action_observations":c3.get("post_action_observations",{}),
        "continuation_contract":c3.get("continuation_contract",{}),
        "native_action_vocabulary":c3.get("native_action_vocabulary",[]),
      },
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("inputs",nargs="+",type=Path); ap.add_argument("--out",required=True,type=Path); args=ap.parse_args()
    all_rows=[]
    for p in args.inputs:
        d=json.loads(p.read_text())
        all_rows.extend(d["rows"])
    seen=set(); out=[]
    for row in all_rows:
        if row["semantic_id"] in seen: raise ValueError(f"duplicate semantic id {row['semantic_id']}")
        seen.add(row["semantic_id"])
        compiled=compile_wfc(row["adapter"])  # no label passed to compiler
        out.append({"semantic_id":row["semantic_id"],"domain":row["domain"],"native_action":row["native_action"],
                    "representations":{"B10":compiled},"not_applicable_reasons":{}})
    args.out.write_text(json.dumps({"schema":"eeq-generic-wfc-v1","rows":out,
      "claim_boundary":"canonical qualified-support + transition/continuation frontier; not global minimum coding"},
      indent=2,sort_keys=True)+"\n")
    print(json.dumps({"rows":len(out),"domains":sorted({r['domain'] for r in out})}))

if __name__=="__main__": main()
