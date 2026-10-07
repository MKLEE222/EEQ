#!/usr/bin/env python3
import json, tempfile
from pathlib import Path
from github_adapter_v1 import evaluate_case

def dump(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj))

def make_case(root, *, last_push=False, approval=True, change_request=False,
              check_conclusion="success", check_app=123, required_app=123,
              reviewer_permission="write"):
    repo=root/"o"/"r"; pdir=repo/"prs"/"1"; pdir.mkdir(parents=True)
    rules=[
      {"type":"pull_request","parameters":{
        "allowed_merge_methods":["squash"],
        "dismiss_stale_reviews_on_push":False,
        "require_code_owner_review":False,
        "require_extra_approval_for_unattributed_changes":True,
        "require_last_push_approval":last_push,
        "required_approving_review_count":1,
        "required_review_thread_resolution":False,
        "required_reviewers":[],
      }},
      {"type":"required_status_checks","parameters":{
        "strict_required_status_checks_policy":False,
        "do_not_enforce_on_create":False,
        "required_status_checks":[{"context":"Build","integration_id":required_app}],
      }},
      {"type":"non_fast_forward","parameters":None},
    ]
    dump(repo/"effective_rules"/"main.json",{"status":200,"body":rules})
    dump(pdir/"adapter_pr_input.json",{
      "repo":"o/r","pr":1,"base":"main","head_sha":"h1","merge_commit_sha":"m1",
      "author_login":"human","author_type":"User",
    })
    reviews=[]
    if approval:
        reviews.append({"id":1,"state":"APPROVED","submitted_at":"2026-01-01T00:00:00Z",
                        "commit_id":"h1","user":{"login":"alice"}})
    if change_request:
        reviews.append({"id":2,"state":"CHANGES_REQUESTED","submitted_at":"2026-01-01T00:01:00Z",
                        "commit_id":"h1","user":{"login":"bob"}})
    dump(pdir/"reviews.json",{"status":200,"body":reviews})
    perms={"alice":{"permission":reviewer_permission}}
    if change_request: perms["bob"]={"permission":"write"}
    dump(pdir/"reviewer_permissions.json",perms)
    head_checks=[]
    if check_conclusion is not None:
        head_checks=[{"id":10,"name":"Build","status":"completed","conclusion":check_conclusion,
                      "completed_at":"2026-01-01T00:02:00Z","app":{"id":check_app}}]
    dump(pdir/"head_check_runs.json",{"status":200,"body":{"check_runs":head_checks}})
    dump(pdir/"merge_check_runs.json",{"status":200,"body":{"check_runs":[]}})
    dump(pdir/"head_statuses.json",{"status":200,"body":[]})
    dump(pdir/"merge_statuses.json",{"status":200,"body":[]})
    return evaluate_case(pdir,repo)

with tempfile.TemporaryDirectory() as td:
    r=make_case(Path(td))
    assert r["prediction"]=="PREDICT_ADMISSIBLE",r

with tempfile.TemporaryDirectory() as td:
    r=make_case(Path(td),check_conclusion=None)
    assert r["prediction"]=="PREDICT_BLOCKED",r
    assert any(x["kind"]=="required_check_missing_expected_app" for x in r["blockers"]),r

with tempfile.TemporaryDirectory() as td:
    r=make_case(Path(td),last_push=True)
    assert r["prediction"]=="ADAPTER_UNSUPPORTED",r
    assert "require_last_push_approval" in r["unsupported"],r

with tempfile.TemporaryDirectory() as td:
    r=make_case(Path(td),change_request=True)
    assert r["prediction"]=="PREDICT_BLOCKED",r
    assert any(x["kind"]=="authorized_change_request" for x in r["blockers"]),r

with tempfile.TemporaryDirectory() as td:
    r=make_case(Path(td),check_app=999)
    assert r["prediction"]=="PREDICT_BLOCKED",r
    assert any(x["kind"]=="required_check_missing_expected_app" for x in r["blockers"]),r

with tempfile.TemporaryDirectory() as td:
    r=make_case(Path(td),reviewer_permission="read")
    assert r["prediction"]=="PREDICT_BLOCKED",r
    assert any(x["kind"]=="insufficient_approvals" for x in r["blockers"]),r

print("github_adapter_v1 synthetic tests: ok")
