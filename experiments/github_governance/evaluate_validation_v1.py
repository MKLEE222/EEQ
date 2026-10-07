#!/usr/bin/env python3
import argparse, hashlib, json, urllib.parse
from pathlib import Path

NATIVE_SCORED={"NATIVE_ADMISSIBLE","NATIVE_BLOCKED"}
PRED_SCORED={"PREDICT_ADMISSIBLE","PREDICT_BLOCKED"}
EXPECTED={
    "PREDICT_ADMISSIBLE":"NATIVE_ADMISSIBLE",
    "PREDICT_BLOCKED":"NATIVE_BLOCKED",
}

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def sha(x):
    return hashlib.sha256(canon(x).encode("utf-8")).hexdigest()

def read(p):
    return json.loads(Path(p).read_text())

def rule_state(repo_dir,base):
    p=repo_dir/"effective_rules"/(urllib.parse.quote(base,safe="")+".json")
    d=read(p)
    if d.get("status")!=200 or not isinstance(d.get("body"),list):
        return {"endpoint_status":d.get("status"),"rules":None}
    rules=[]
    for r in d["body"]:
        params=r.get("parameters")
        rules.append({"type":r.get("type"),"parameters":params})
    return {"endpoint_status":200,"rules":rules}

def semantic_state(row,sample_root):
    repo=row["repo"]; owner,name=repo.split("/",1)
    pdir=sample_root/owner/name/"prs"/str(row["pr"])
    pri=read(pdir/"adapter_pr_input.json")
    # Use the adapter's normalized evidence, but erase concrete actor names and
    # object identities unless they are semantically read by the decision contract.
    evidence=[]
    for e in row.get("evidence",[]):
        kind=e.get("kind")
        if kind=="check_target":
            evidence.append({"kind":kind,"source":e.get("source")})
        elif kind=="review_summary":
            evidence.append({
                "kind":kind,
                "required_approvals":e.get("required_approvals"),
                "authorized_approval_count":len(e.get("authorized_approvals") or []),
                "authorized_change_request_count":len(e.get("authorized_change_requests") or []),
                "unknown_permission_count":len(e.get("unknown_permission_reviewers") or []),
            })
        elif kind in ("check_run","commit_status"):
            clean={k:v for k,v in e.items() if k not in ("creator",)}
            evidence.append(clean)
        elif kind=="rule_not_a_merge_readiness_obligation":
            evidence.append(e)
        else:
            evidence.append(e)

    blockers=[]
    for b in row.get("blockers",[]):
        clean=dict(b)
        if "reviewers" in clean:
            clean["reviewer_count"]=len(clean.pop("reviewers") or [])
        blockers.append(clean)

    return {
        "family":"GITHUB_GOVERNANCE",
        "environment":repo,
        "base":pri.get("base"),
        "author_type":pri.get("author_type"),
        "active_policy":rule_state(sample_root/owner/name,pri.get("base")),
        "pre_action_evidence":evidence,
        "blockers":blockers,
        "action":"MERGE_PR",
        "future_contract":"GITHUB_NATIVE_MERGE_READINESS",
        "native_action_vocabulary":["NATIVE_ADMISSIBLE","NATIVE_BLOCKED"],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("sample_root")
    ap.add_argument("adapter_output")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    sample=Path(args.sample_root)
    adapter=read(args.adapter_output)
    rows=[]
    sigs={}

    for ar in adapter["rows"]:
        owner,name=ar["repo"].split("/",1)
        pdir=sample/owner/name/"prs"/str(ar["pr"])
        native=read(pdir/"native_oracle.json")
        nl=native["native_label"]
        pred=ar["prediction"]

        if nl not in NATIVE_SCORED:
            disposition="NATIVE_NONSCORED"
        elif pred=="ADAPTER_UNSUPPORTED":
            disposition="ADAPTER_UNSUPPORTED"
        elif pred not in PRED_SCORED:
            disposition="ADAPTER_INVALID_OUTPUT"
        elif EXPECTED[pred]==nl:
            disposition="CORRECT"
        else:
            disposition="MISMATCH"

        rec={
            "repo":ar["repo"],"pr":ar["pr"],
            "native_label":nl,"prediction":pred,
            "disposition":disposition,
            "unsupported":ar.get("unsupported",[]),
            "blockers":ar.get("blockers",[]),
        }
        if nl in NATIVE_SCORED and pred in PRED_SCORED:
            state=semantic_state(ar,sample)
            sig=sha(state)
            rec["semantic_signature"]=sig
            rec["semantic_state"]=state
            sigs.setdefault(sig,{"state":state,"cases":[]})
            sigs[sig]["cases"].append({"repo":ar["repo"],"pr":ar["pr"],"native_label":nl,"prediction":pred})
        rows.append(rec)

    counts={}
    for r in rows: counts[r["disposition"]]=counts.get(r["disposition"],0)+1
    scored=[r for r in rows if r["disposition"] in ("CORRECT","MISMATCH")]
    correct=sum(r["disposition"]=="CORRECT" for r in scored)
    mismatch=sum(r["disposition"]=="MISMATCH" for r in scored)

    sig_conflicts=[]
    for sig,info in sigs.items():
        labels=sorted({x["native_label"] for x in info["cases"]})
        if len(labels)>1:
            sig_conflicts.append({"signature":sig,"native_labels":labels,"cases":info["cases"]})

    payload={
        "schema":"github-adapter-v1-validation-report",
        "rows":rows,
        "summary":{
            "collected_cases":len(rows),
            "dispositions":counts,
            "supported_native_scored_cases":len(scored),
            "correct":correct,
            "mismatches":mismatch,
            "accuracy":(correct/len(scored) if scored else None),
            "deduplicated_supported_semantic_cases":len(sigs),
            "semantic_signature_label_conflicts":len(sig_conflicts),
        },
        "semantic_signature_conflicts":sig_conflicts,
        "semantic_signatures":[
            {"signature":s,"state":v["state"],"case_count":len(v["cases"])}
            for s,v in sorted(sigs.items())
        ],
    }
    Path(args.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps(payload["summary"],sort_keys=True))

if __name__=="__main__":
    main()
