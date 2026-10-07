#!/usr/bin/env python3
import argparse, json, urllib.parse
from pathlib import Path

PASS_CHECK_CONCLUSIONS={"success","neutral","skipped"}
WRITE_PERMISSIONS={"write","admin"}

IRRELEVANT_FOR_PR_MERGE={
    "deletion",
    "non_fast_forward",
    "creation",
    "copilot_code_review",
}
SUPPORTED_RULES={"pull_request","required_status_checks"} | IRRELEVANT_FOR_PR_MERGE

def read_json(p):
    return json.loads(Path(p).read_text())

def wrapped_body(p):
    d=read_json(p)
    if not isinstance(d,dict) or "status" not in d or "body" not in d:
        raise ValueError(f"bad wrapper: {p}")
    if d["status"] != 200:
        raise RuntimeError(f"endpoint status {d['status']} for {p}")
    return d["body"]

def permission_map(p):
    d=read_json(p)
    out={}
    for login,rec in d.items():
        if isinstance(rec,dict):
            out[login.lower()]=rec.get("permission")
    return out

def latest_decisive_reviews(reviews):
    decisive={"APPROVED","CHANGES_REQUESTED","DISMISSED"}
    latest={}
    ordered=sorted(
        [r for r in reviews if isinstance(r,dict)],
        key=lambda r: ((r.get("submitted_at") or ""), int(r.get("id") or 0))
    )
    for r in ordered:
        user=(r.get("user") or {}).get("login")
        state=(r.get("state") or "").upper()
        if user and state in decisive:
            latest[user.lower()]={
                "login":user,
                "state":state,
                "submitted_at":r.get("submitted_at"),
                "commit_id":r.get("commit_id"),
            }
    return latest

def latest_by(items, key_name):
    groups={}
    for x in items:
        if not isinstance(x,dict): continue
        k=x.get(key_name)
        if not k: continue
        cur=groups.get(k)
        stamp=(x.get("completed_at") or x.get("updated_at") or x.get("created_at") or "", int(x.get("id") or 0))
        if cur is None or stamp > cur[0]:
            groups[k]=(stamp,x)
    return {k:v[1] for k,v in groups.items()}

def choose_check_target(pr_input, head_checks, merge_checks, head_statuses, merge_statuses):
    # GitHub evaluates the test merge commit when it has status/check information;
    # otherwise required checks are evaluated on the latest head commit.
    if merge_checks or merge_statuses:
        return {
            "sha":pr_input.get("merge_commit_sha"),
            "checks":merge_checks,
            "statuses":merge_statuses,
            "source":"merge_commit",
        }
    return {
        "sha":pr_input["head_sha"],
        "checks":head_checks,
        "statuses":head_statuses,
        "source":"head",
    }

def eval_status_rule(params, target):
    blockers=[]
    evidence=[]
    checks=target["checks"]
    statuses=target["statuses"]

    latest_checks={}
    for cr in checks:
        if not isinstance(cr,dict): continue
        name=cr.get("name")
        app_id=(cr.get("app") or {}).get("id")
        key=(name,app_id)
        cur=latest_checks.get(key)
        stamp=(cr.get("completed_at") or cr.get("started_at") or "", int(cr.get("id") or 0))
        if cur is None or stamp > cur[0]:
            latest_checks[key]=(stamp,cr)

    latest_status=latest_by(statuses,"context")

    required=params.get("required_status_checks") or []
    for req in required:
        context=req.get("context")
        integration=req.get("integration_id")
        matched_check=None
        if integration is None:
            candidates=[v[1] for (name,_app),v in latest_checks.items() if name==context]
            if candidates:
                matched_check=sorted(candidates,key=lambda x:(x.get("completed_at") or "",int(x.get("id") or 0)))[-1]
        else:
            pair=latest_checks.get((context,integration))
            matched_check=pair[1] if pair else None

        status_obj=latest_status.get(context)
        has_evidence = matched_check is not None or status_obj is not None

        if integration is not None and matched_check is None:
            blockers.append({"kind":"required_check_missing_expected_app","context":context,"integration_id":integration})
        elif not has_evidence:
            blockers.append({"kind":"required_check_missing","context":context})

        if matched_check is not None:
            ok=(matched_check.get("status")=="completed" and matched_check.get("conclusion") in PASS_CHECK_CONCLUSIONS)
            evidence.append({
                "kind":"check_run",
                "context":context,
                "integration_id":(matched_check.get("app") or {}).get("id"),
                "status":matched_check.get("status"),
                "conclusion":matched_check.get("conclusion"),
                "passes":ok,
            })
            if not ok:
                blockers.append({"kind":"required_check_not_successful","context":context,"source":"check_run"})

        # If a commit status with the same required name exists, it must also pass.
        if status_obj is not None:
            ok=status_obj.get("state")=="success"
            evidence.append({
                "kind":"commit_status",
                "context":context,
                "state":status_obj.get("state"),
                "creator":(status_obj.get("creator") or {}).get("login"),
                "passes":ok,
            })
            if not ok:
                blockers.append({"kind":"required_check_not_successful","context":context,"source":"commit_status"})

    return blockers,evidence

def eval_pull_request_rule(params, reviews, permissions, pr_input):
    unsupported=[]
    blockers=[]
    evidence=[]

    if params.get("dismiss_stale_reviews_on_push"):
        unsupported.append("dismiss_stale_reviews_on_push")
    if params.get("require_last_push_approval"):
        unsupported.append("require_last_push_approval")
    if params.get("require_code_owner_review"):
        unsupported.append("require_code_owner_review")
    if params.get("required_review_thread_resolution"):
        unsupported.append("required_review_thread_resolution")
    if params.get("required_reviewers"):
        unsupported.append("required_reviewers")

    if params.get("require_extra_approval_for_unattributed_changes"):
        atype=(pr_input.get("author_type") or "").lower()
        alogin=(pr_input.get("author_login") or "").lower()
        if atype=="bot" or "copilot" in alogin:
            unsupported.append("unattributed_copilot_extra_approval")

    latest=latest_decisive_reviews(reviews)
    approved=[]
    change_requests=[]
    unknown_permissions=[]
    for login,r in sorted(latest.items()):
        perm=permissions.get(login)
        if perm is None:
            unknown_permissions.append(login)
            continue
        if perm not in WRITE_PERMISSIONS:
            continue
        if r["state"]=="APPROVED":
            approved.append(r)
        elif r["state"]=="CHANGES_REQUESTED":
            change_requests.append(r)

    # Unknown reviewer permission only matters if the configured approval threshold
    # cannot already be met deterministically or if that reviewer requested changes.
    required=int(params.get("required_approving_review_count") or 0)
    if len(approved) < required and unknown_permissions:
        unsupported.append("missing_reviewer_permission_for_threshold")

    if change_requests:
        blockers.append({
            "kind":"authorized_change_request",
            "reviewers":[r["login"] for r in change_requests],
        })
    if len(approved) < required:
        blockers.append({
            "kind":"insufficient_approvals",
            "required":required,
            "observed_authorized":len(approved),
        })

    evidence.append({
        "kind":"review_summary",
        "required_approvals":required,
        "authorized_approvals":[r["login"] for r in approved],
        "authorized_change_requests":[r["login"] for r in change_requests],
        "unknown_permission_reviewers":unknown_permissions,
    })
    return unsupported,blockers,evidence

def evaluate_case(case_dir, repo_dir):
    pr_input=read_json(case_dir/"adapter_pr_input.json")
    base=pr_input["base"]
    rules_path=repo_dir/"effective_rules"/(urllib.parse.quote(base,safe="")+".json")
    if not rules_path.exists():
        return {"prediction":"ADAPTER_UNSUPPORTED","unsupported":["missing_effective_rules"],"blockers":[],"evidence":[]}

    rules=wrapped_body(rules_path)
    if not isinstance(rules,list):
        return {"prediction":"ADAPTER_UNSUPPORTED","unsupported":["effective_rules_not_list"],"blockers":[],"evidence":[]}

    types={r.get("type") for r in rules}
    unknown=sorted(t for t in types if t not in SUPPORTED_RULES)
    if unknown:
        return {"prediction":"ADAPTER_UNSUPPORTED","unsupported":["unsupported_rule:"+x for x in unknown],"blockers":[],"evidence":[]}

    reviews=wrapped_body(case_dir/"reviews.json")
    permissions=permission_map(case_dir/"reviewer_permissions.json")

    def checks(name):
        p=case_dir/name
        if not p.exists(): return []
        d=read_json(p)
        if d.get("status") != 200: raise RuntimeError(f"{name} status={d.get('status')}")
        body=d.get("body")
        if isinstance(body,dict) and "check_runs" in body: return body["check_runs"]
        if isinstance(body,list): return body
        return []

    def statuses(name):
        p=case_dir/name
        if not p.exists(): return []
        d=read_json(p)
        if d.get("status") != 200: raise RuntimeError(f"{name} status={d.get('status')}")
        body=d.get("body")
        return body if isinstance(body,list) else []

    target=choose_check_target(
        pr_input,
        checks("head_check_runs.json"),
        checks("merge_check_runs.json"),
        statuses("head_statuses.json"),
        statuses("merge_statuses.json"),
    )

    unsupported=[]
    blockers=[]
    evidence=[{"kind":"check_target","source":target["source"],"sha":target["sha"]}]

    for rule in rules:
        typ=rule.get("type")
        params=rule.get("parameters") or {}
        if typ=="pull_request":
            u,b,e=eval_pull_request_rule(params,reviews,permissions,pr_input)
            unsupported.extend(u); blockers.extend(b); evidence.extend(e)
        elif typ=="required_status_checks":
            if params.get("strict_required_status_checks_policy"):
                unsupported.append("strict_required_status_checks_policy")
            b,e=eval_status_rule(params,target)
            blockers.extend(b); evidence.extend(e)
        elif typ in IRRELEVANT_FOR_PR_MERGE:
            evidence.append({"kind":"rule_not_a_merge_readiness_obligation","type":typ})

    if unsupported:
        pred="ADAPTER_UNSUPPORTED"
    elif blockers:
        pred="PREDICT_BLOCKED"
    else:
        pred="PREDICT_ADMISSIBLE"
    return {
        "prediction":pred,
        "unsupported":sorted(set(unsupported)),
        "blockers":blockers,
        "evidence":evidence,
        "base":base,
        "head_sha":pr_input.get("head_sha"),
        "merge_commit_sha":pr_input.get("merge_commit_sha"),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("sample_root")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    root=Path(args.sample_root)
    rows=[]
    for owner in sorted(p for p in root.iterdir() if p.is_dir()):
        for repo in sorted(p for p in owner.iterdir() if p.is_dir()):
            repo_name=f"{owner.name}/{repo.name}"
            prs=repo/"prs"
            if not prs.exists(): continue
            for pdir in sorted((p for p in prs.iterdir() if p.is_dir()), key=lambda p:int(p.name)):
                try:
                    result=evaluate_case(pdir,repo)
                    rows.append({"repo":repo_name,"pr":int(pdir.name),**result})
                except Exception as exc:
                    rows.append({
                        "repo":repo_name,"pr":int(pdir.name),
                        "prediction":"ADAPTER_UNSUPPORTED",
                        "unsupported":["adapter_input_error"],
                        "error_class":exc.__class__.__name__,
                        "error_message":str(exc),
                        "blockers":[],"evidence":[],
                    })
    counts={}
    for r in rows: counts[r["prediction"]]=counts.get(r["prediction"],0)+1
    payload={
        "schema":"github-eeq-adapter-v1-output",
        "oracle_fields_read":False,
        "rows":rows,
        "summary":{"cases":len(rows),"prediction_counts":counts},
    }
    Path(args.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps(payload["summary"],sort_keys=True))

if __name__=="__main__":
    main()
