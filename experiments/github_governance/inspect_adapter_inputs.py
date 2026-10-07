#!/usr/bin/env python3
import argparse, json
from collections import Counter, defaultdict
from pathlib import Path

BANNED_NAMES = {"pr.json", "summary.json", "report.json"}

def load_wrapped(path):
    d=json.loads(path.read_text())
    if not isinstance(d,dict) or "status" not in d or "body" not in d:
        raise ValueError(f"unexpected wrapper schema: {path}")
    return d

def shape(x):
    if isinstance(x,dict): return sorted(x.keys())
    if isinstance(x,list): return "list"
    return type(x).__name__

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    root=Path(args.root)

    # Hard anti-leakage guard: this program never opens native-oracle label files.
    for p in root.rglob("*"):
        if p.name in BANNED_NAMES:
            continue

    repos={}
    for owner_dir in sorted([p for p in root.iterdir() if p.is_dir()]):
        for repo_dir in sorted([p for p in owner_dir.iterdir() if p.is_dir()]):
            rel=f"{owner_dir.name}/{repo_dir.name}"
            effective_dir=repo_dir/"effective_rules"
            rulesets_dir=repo_dir/"rulesets"
            prs_dir=repo_dir/"prs"
            if not effective_dir.exists() and not prs_dir.exists():
                continue

            rule_type_counts=Counter()
            effective_rules=[]
            for p in sorted(effective_dir.glob("*.json")):
                wrapped=load_wrapped(p)
                if wrapped["status"] != 200:
                    effective_rules.append({"file":p.name,"status":wrapped["status"],"rules":[]})
                    continue
                body=wrapped["body"]
                if not isinstance(body,list):
                    raise ValueError(f"effective rules not list: {p}")
                rs=[]
                for rule in body:
                    rtype=rule.get("type")
                    rule_type_counts[rtype]+=1
                    params=rule.get("parameters")
                    rs.append({
                        "type":rtype,
                        "ruleset_id":rule.get("ruleset_id"),
                        "ruleset_source":rule.get("ruleset_source"),
                        "ruleset_source_type":rule.get("ruleset_source_type"),
                        "parameter_keys":sorted(params.keys()) if isinstance(params,dict) else [],
                        "parameters":params,
                    })
                effective_rules.append({"file":p.name,"status":200,"rules":rs})

            ruleset_details=[]
            for p in sorted(rulesets_dir.glob("*.json")):
                wrapped=load_wrapped(p)
                body=wrapped["body"]
                if wrapped["status"] != 200 or not isinstance(body,dict):
                    ruleset_details.append({"file":p.name,"status":wrapped["status"]})
                    continue
                rules=[]
                for r in body.get("rules") or []:
                    params=r.get("parameters")
                    rules.append({
                        "type":r.get("type"),
                        "parameter_keys":sorted(params.keys()) if isinstance(params,dict) else [],
                        "parameters":params,
                    })
                ruleset_details.append({
                    "file":p.name,
                    "status":200,
                    "name":body.get("name"),
                    "target":body.get("target"),
                    "enforcement":body.get("enforcement"),
                    "conditions":body.get("conditions"),
                    "rules":rules,
                })

            evidence_shapes=defaultdict(Counter)
            pr_count=0
            for pdir in sorted(prs_dir.iterdir()) if prs_dir.exists() else []:
                if not pdir.is_dir():
                    continue
                pr_count+=1
                for fname in [
                    "combined_status.json","check_runs.json","reviews.json",
                    "requested_reviewers.json","head_commit.json","commits.json",
                    "changed_files.json","commit_verification.json"
                ]:
                    p=pdir/fname
                    if not p.exists():
                        evidence_shapes[fname]["MISSING"]+=1
                        continue
                    data=json.loads(p.read_text())
                    if fname=="commit_verification.json":
                        evidence_shapes[fname][str(shape(data))]+=1
                    else:
                        if not isinstance(data,dict):
                            raise ValueError(f"unexpected evidence wrapper: {p}")
                        evidence_shapes[fname][f"status:{data.get('status')}"]+=1
                        evidence_shapes[fname][f"body-shape:{shape(data.get('body'))}"]+=1

            repos[rel]={
                "effective_rule_type_counts":dict(sorted(rule_type_counts.items())),
                "effective_rules":effective_rules,
                "ruleset_details":ruleset_details,
                "pr_evidence_cases":pr_count,
                "evidence_schema_counts":{k:dict(v) for k,v in sorted(evidence_shapes.items())},
            }

    payload={
        "schema":"github-adapter-input-inventory-v1",
        "anti_leakage":{
            "banned_files_not_opened":sorted(BANNED_NAMES),
            "native_label_fields_used":False,
            "mergeable_state_used":False,
        },
        "repositories":repos,
    }
    Path(args.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        repo:{
            "rule_types":info["effective_rule_type_counts"],
            "pr_evidence_cases":info["pr_evidence_cases"]
        } for repo,info in repos.items()
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
