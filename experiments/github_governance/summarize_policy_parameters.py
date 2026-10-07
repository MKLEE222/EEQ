#!/usr/bin/env python3
import argparse, json
from pathlib import Path

RELEVANT = {
    "pull_request",
    "required_status_checks",
    "required_signatures",
    "commit_message_pattern",
    "required_linear_history",
    "merge_queue",
    "code_scanning",
    "copilot_code_review",
}

def compact_rule(rule):
    typ=rule.get("type")
    params=rule.get("parameters")
    out={
        "type":typ,
        "ruleset_id":rule.get("ruleset_id"),
        "ruleset_source":rule.get("ruleset_source"),
        "ruleset_source_type":rule.get("ruleset_source_type"),
    }
    if typ=="required_status_checks" and isinstance(params,dict):
        checks=params.get("required_status_checks") or []
        out["strict_required_status_checks_policy"]=params.get("strict_required_status_checks_policy")
        out["do_not_enforce_on_create"]=params.get("do_not_enforce_on_create")
        out["required_status_checks"]=[
            {
                "context":c.get("context"),
                "integration_id":c.get("integration_id"),
            } for c in checks
        ]
    else:
        out["parameters"]=params
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("inventory")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    inv=json.loads(Path(args.inventory).read_text())
    repos={}
    for repo,info in sorted(inv["repositories"].items()):
        bases=[]
        for entry in info["effective_rules"]:
            rules=[compact_rule(r) for r in entry["rules"] if r.get("type") in RELEVANT]
            bases.append({
                "effective_rules_file":entry["file"],
                "status":entry["status"],
                "relevant_rules":rules,
            })
        repos[repo]=bases
    payload={
        "schema":"github-adapter-policy-parameter-summary-v1",
        "source_inventory_schema":inv["schema"],
        "native_labels_read":False,
        "repositories":repos,
    }
    Path(args.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps(payload,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
