#!/usr/bin/env python3
"""GitHub governance adapter v2 for the C1-repair carrier.

adapt_public_row() reads only lawful pre-decision evidence. Native mergeability
labels are joined only by validate() after adaptation.
"""
import argparse, hashlib, json
from collections import defaultdict
from pathlib import Path

PASS_CHECK_CONCLUSIONS={"success","neutral","skipped"}
EXPECTED_CHECKS={
    ("code-owner-approval",97978),
    ("cla-bot",97978),
    ("docs-missing",97978),
    ("Collect information & changes data",15368),
    ("blocking-label-awaiting-frontend",97978),
    ("Check all requirements",15368),
    ("Check hassfest",15368),
    ("required-labels",97978),
}

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def read_wrapper(path):
    try: w=load(path)
    except FileNotFoundError: return None,None
    return w.get("status"),w.get("body")

def frozen_signature(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def latest_reviews(reviews):
    by={}
    for r in reviews or []:
        user=(r.get("user") or {}).get("login")
        if not user: continue
        if user not in by or (r.get("submitted_at") or "") >= (by[user].get("submitted_at") or ""):
            by[user]=r
    return by

def check_observations(check_runs,combined):
    obs=defaultdict(list)
    for run in (check_runs or {}).get("check_runs",[]):
        obs[run.get("name")].append({
            "kind":"check_run",
            "status":run.get("status"),
            "conclusion":run.get("conclusion"),
            "app_id":(run.get("app") or {}).get("id"),
            "completed_at":run.get("completed_at"),
        })
    for st in (combined or {}).get("statuses",[]):
        obs[st.get("context")].append({
            "kind":"commit_status","state":st.get("state"),"updated_at":st.get("updated_at"),
        })
    return dict(sorted(obs.items()))

def effective_rule_index(rules):
    out=defaultdict(list)
    for r in rules if isinstance(rules,list) else []:
        out[r.get("type")].append(r)
    return out

def validate_contract(branch,effective,ruleset):
    problems=[]
    protection=((branch or {}).get("protection") or {}) if isinstance(branch,dict) else {}
    if protection.get("enabled") is not False:
        problems.append("legacy_protection_not_proven_disabled")

    idx=effective_rule_index(effective)
    allowed={"deletion","non_fast_forward","pull_request","required_status_checks","copilot_code_review"}
    extra=set(idx)-allowed
    if extra: problems.append("unexpected_effective_rules:"+",".join(sorted(extra)))
    if len(idx.get("pull_request",[]))!=1:
        problems.append("pull_request_rule_count")
    if len(idx.get("required_status_checks",[]))!=1:
        problems.append("required_status_rule_count")

    if idx.get("pull_request"):
        p=(idx["pull_request"][0].get("parameters") or {})
        expected={
            "required_approving_review_count":1,
            "dismiss_stale_reviews_on_push":False,
            "required_reviewers":[],
            "require_code_owner_review":False,
            "require_last_push_approval":False,
            "required_review_thread_resolution":False,
            "require_extra_approval_for_unattributed_changes":True,
            "allowed_merge_methods":["squash"],
        }
        for k,v in expected.items():
            if p.get(k)!=v: problems.append("pull_param_drift:"+k)

    if idx.get("required_status_checks"):
        p=(idx["required_status_checks"][0].get("parameters") or {})
        got={(x.get("context"),x.get("integration_id"))
             for x in p.get("required_status_checks",[]) if x.get("context")}
        if got!=EXPECTED_CHECKS:
            problems.append("required_checks_drift")
        if p.get("strict_required_status_checks_policy") is not False:
            problems.append("strict_policy_drift")

    # The detailed public ruleset is retained as source identity, but hidden
    # bypass lists are outside the explicitly registered non-bypass actor class.
    if not isinstance(ruleset,dict) or ruleset.get("id")!=6332198 or ruleset.get("enforcement")!="active":
        problems.append("ruleset_identity_or_enforcement_drift")
    return problems

def adapt_public_row(root,number):
    repo="home-assistant/core"
    pdir=root/"prs"/str(number)
    pstatus,pr=read_wrapper(pdir/"pr.json")
    if pstatus!=200 or not isinstance(pr,dict):
        return {"repo":repo,"pr":number,"adapter_status":"SOURCE_UNAVAILABLE","predicted_native_label":None}

    bstatus,branch=read_wrapper(root/"governance"/"branch.json")
    estatus,effective=read_wrapper(root/"governance"/"effective_rules.json")
    rstatus,ruleset=read_wrapper(root/"governance"/"ruleset.json")
    rvstatus,reviews=read_wrapper(pdir/"reviews.json")
    mcstatus,mchecks=read_wrapper(pdir/"merge_check_runs.json")
    msstatus,mstatus=read_wrapper(pdir/"merge_combined_status.json")
    cstatus,commits=read_wrapper(pdir/"commits.json")
    verification_path=pdir/"commit_verification.json"
    verification=load(verification_path) if verification_path.exists() else None

    source_gaps=[]
    if bstatus!=200 or estatus!=200 or rstatus!=200:
        source_gaps.append("missing_branch_or_rules")
    source_gaps.extend(validate_contract(branch,effective,ruleset))
    if rvstatus!=200: source_gaps.append("missing_reviews")
    if mcstatus!=200 or msstatus!=200: source_gaps.append("missing_merge_commit_checks")
    if cstatus!=200 or verification is None: source_gaps.append("missing_commit_chain")

    base=(pr.get("base") or {}).get("ref")
    if base!="dev": source_gaps.append("outside_frozen_base_contract")

    current=latest_reviews(reviews if isinstance(reviews,list) else [])
    approvals=[u for u,r in current.items() if r.get("state")=="APPROVED"]

    state={
        "repo":repo,
        "base":base,
        "head_sha":(pr.get("head") or {}).get("sha"),
        "merge_commit_sha":pr.get("merge_commit_sha"),
        "registered_actor_class":"ORDINARY_NON_BYPASS_MERGER",
        "legacy_protection_enabled":(((branch or {}).get("protection") or {}).get("enabled")
                                     if isinstance(branch,dict) else None),
        "effective_rules":effective if isinstance(effective,list) else [],
        "ruleset_identity":{
            "id":ruleset.get("id") if isinstance(ruleset,dict) else None,
            "name":ruleset.get("name") if isinstance(ruleset,dict) else None,
            "source":ruleset.get("source") if isinstance(ruleset,dict) else None,
        },
        "review_states":{u:r.get("state") for u,r in sorted(current.items())},
        "visible_approved_reviewers":sorted(approvals),
        "merge_check_observations":check_observations(mchecks,mstatus),
        "commit_verification":verification,
        "registered_action":"MERGE_PR",
        "future_contract":"BRANCH_GOVERNANCE_CONTINUATION",
        "native_action_vocabulary":["NATIVE_ADMISSIBLE","NATIVE_BLOCKED"],
    }

    if source_gaps:
        return {
            "repo":repo,"pr":number,"adapter_version":"github-governance-v2",
            "adapter_status":"PREEXCLUDED_UNAVAILABLE_REQUIRED_SOURCE",
            "predicted_native_label":None,
            "preclusion_reasons":sorted(set(source_gaps)),
            "c1_complete":False,"v0_c1_c2_c3":state,
            "raw_state_sha256":frozen_signature(state),"g4_count_eligible":False,
        }

    # Reviewer write/maintain permission is not lawfully observable from the
    # available public credentials. Any visible approval therefore makes the
    # required source incomplete and is preexcluded before native comparison.
    if approvals:
        return {
            "repo":repo,"pr":number,"adapter_version":"github-governance-v2",
            "adapter_status":"PREEXCLUDED_UNAVAILABLE_REQUIRED_SOURCE",
            "predicted_native_label":None,
            "preclusion_reasons":["approving_reviewer_permission_unavailable"],
            "c1_complete":False,"v0_c1_c2_c3":state,
            "raw_state_sha256":frozen_signature(state),"g4_count_eligible":False,
        }

    if pr.get("draft") is True:
        return {
            "repo":repo,"pr":number,"adapter_version":"github-governance-v2",
            "adapter_status":"NATIVE_ORACLE_NON_SCORED_DRAFT",
            "predicted_native_label":None,"preclusion_reasons":[],
            "c1_complete":True,"v0_c1_c2_c3":state,
            "raw_state_sha256":frozen_signature(state),"g4_count_eligible":False,
        }

    # Zero visible approvals under a frozen rule requiring one approval is a
    # complete, actor-independent blocker for the registered non-bypass actor.
    return {
        "repo":repo,"pr":number,"adapter_version":"github-governance-v2",
        "adapter_status":"PREDICTED_C1_COMPLETE",
        "predicted_native_label":"NATIVE_BLOCKED",
        "blocking_reasons":[{"mechanism":"required_reviews","required":1,"observed_approved":0}],
        "preclusion_reasons":[],"c1_complete":True,"v0_c1_c2_c3":state,
        "raw_state_sha256":frozen_signature(state),"g4_count_eligible":False,
    }

def validate(root,out):
    native=load(root/"summary.json")
    rows=[]
    for n in native:
        a=adapt_public_row(root,int(n["pr"]))
        a["native_label"]=n["native_label"]
        a["native_scored"]=n["native_label"] in {"NATIVE_ADMISSIBLE","NATIVE_BLOCKED"}
        a["comparison_scored"]=bool(a["native_scored"] and a.get("predicted_native_label"))
        a["native_match"]=(a["predicted_native_label"]==n["native_label"]
                           if a["comparison_scored"] else None)
        rows.append(a)
    report={
        "schema":"eeq-github-governance-v2-validation",
        "sample_rows":len(rows),
        "c1_complete_rows":sum(bool(x.get("c1_complete")) for x in rows),
        "predicted_scored_rows":sum(x["comparison_scored"] for x in rows),
        "predicted_matches":sum(x["native_match"] is True for x in rows),
        "predicted_mismatches":sum(x["native_match"] is False for x in rows),
        "preexcluded_unavailable_source":sum(x["adapter_status"]=="PREEXCLUDED_UNAVAILABLE_REQUIRED_SOURCE" for x in rows),
        "rows":rows,
    }
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return {k:v for k,v in report.items() if k!="rows"}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("artifact_dir",type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    print(json.dumps(validate(args.artifact_dir,args.out),sort_keys=True))
