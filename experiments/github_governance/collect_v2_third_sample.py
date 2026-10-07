#!/usr/bin/env python3
"""Collect GitHub v2 fresh Home Assistant dev sample.

Selection is mechanical and label-independent. Native labels are archived only
after PR IDs have been selected. The collector never scores the adapter.
"""
import argparse, hashlib, json, os, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

API="https://api.github.com"
TOKEN=os.environ.get("GITHUB_TOKEN","")
REPO="home-assistant/core"
BASE="dev"
TARGET=25
RULESET_ID=6332198

def request(path):
    url=path if path.startswith("http") else API+path
    headers={
        "Accept":"application/vnd.github+json",
        "User-Agent":"EEQ-GitHub-governance-v2-collector",
        "X-GitHub-Api-Version":"2022-11-28",
    }
    if TOKEN:
        headers["Authorization"]="Bearer "+TOKEN
    req=urllib.request.Request(url,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=60) as r:
            raw=r.read().decode("utf-8")
            return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw=e.read().decode("utf-8",errors="replace")
        try: body=json.loads(raw)
        except Exception: body={"raw":raw}
        return e.code,body

def request_all_list(path, per_page=100, max_pages=20):
    sep="&" if "?" in path else "?"
    out=[]; statuses=[]
    for page in range(1,max_pages+1):
        code,body=request(f"{path}{sep}per_page={per_page}&page={page}")
        statuses.append(code)
        if code!=200 or not isinstance(body,list):
            return code,out,statuses,body
        out.extend(body)
        if len(body)<per_page:
            return 200,out,statuses,None
    return 206,out,statuses,{"reason":"max_pages_reached","max_pages":max_pages}

def request_all_checks(path, per_page=100, max_pages=20):
    sep="&" if "?" in path else "?"
    runs=[]; statuses=[]; total=None
    for page in range(1,max_pages+1):
        code,body=request(f"{path}{sep}per_page={per_page}&page={page}")
        statuses.append(code)
        if code!=200 or not isinstance(body,dict):
            return code,{"total_count":total,"check_runs":runs},statuses,body
        if total is None: total=body.get("total_count")
        chunk=body.get("check_runs") or []
        runs.extend(chunk)
        if len(chunk)<per_page:
            return 200,{"total_count":total,"check_runs":runs},statuses,None
    return 206,{"total_count":total,"check_runs":runs},statuses,{"reason":"max_pages_reached"}

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def label_pr(p):
    if p.get("draft"): return "DRAFT"
    m=p.get("mergeable"); s=p.get("mergeable_state")
    if m is False: return "CONFLICT"
    if m is True and s=="clean": return "NATIVE_ADMISSIBLE"
    if m is True and s=="blocked": return "NATIVE_BLOCKED"
    return "NATIVE_ORACLE_AMBIGUOUS"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--first-ids",required=True,type=Path)
    ap.add_argument("--second-summary",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    out=args.out; out.mkdir(parents=True,exist_ok=True)

    first=json.loads(args.first_ids.read_text(encoding="utf-8"))
    second=json.loads(args.second_summary.read_text(encoding="utf-8"))
    excluded=set(first.get(REPO,[]))
    excluded.update(int(r["pr"]) for r in second if r.get("repo")==REPO)
    dump(out/"excluded_previous_ids.json",sorted(excluded))

    selected=[]; pages=[]
    for page in range(1,11):
        q=urllib.parse.urlencode({
            "state":"open","base":BASE,"sort":"updated","direction":"desc",
            "per_page":100,"page":page,
        })
        code,body=request(f"/repos/{REPO}/pulls?{q}")
        dump(out/"selection_pages"/f"page-{page:02d}.json",{"status":code,"body":body})
        pages.append({"page":page,"status":code,"rows":len(body) if isinstance(body,list) else None})
        if code!=200 or not isinstance(body,list):
            raise SystemExit(f"selection page failed page={page} status={code}")
        for pr in body:
            n=int(pr["number"])
            if n in excluded or n in selected:
                continue
            selected.append(n)
            if len(selected)==TARGET: break
        if len(selected)==TARGET or len(body)<100: break
    if len(selected)!=TARGET:
        raise SystemExit(f"fresh sample shortfall selected={len(selected)} target={TARGET}")
    dump(out/"selection.json",{
        "repo":REPO,"base":BASE,"target":TARGET,"selected":selected,
        "selection_rule":"first 25 open dev PRs sorted updated desc excluding frozen first+second sample IDs",
        "pages":pages,
        "native_label_used_for_selection":False,
    })

    # Archive carrier governance independently of outcomes.
    bc,branch=request(f"/repos/{REPO}/branches/{urllib.parse.quote(BASE,safe='')}")
    ec,effective=request(f"/repos/{REPO}/rules/branches/{urllib.parse.quote(BASE,safe='')}?per_page=100")
    rc,ruleset=request(f"/repos/{REPO}/rulesets/{RULESET_ID}")
    dump(out/"governance"/"branch.json",{"status":bc,"body":branch})
    dump(out/"governance"/"effective_rules.json",{"status":ec,"body":effective})
    dump(out/"governance"/"ruleset.json",{"status":rc,"body":ruleset})

    rows=[]; errors=[]
    for num in selected:
        pdir=out/"prs"/str(num)
        final=None; polls=[]
        for attempt in range(1,4):
            c,p=request(f"/repos/{REPO}/pulls/{num}")
            polls.append({
                "attempt":attempt,"status":c,
                "mergeable":p.get("mergeable") if isinstance(p,dict) else None,
                "mergeable_state":p.get("mergeable_state") if isinstance(p,dict) else None,
            })
            final=(c,p)
            if c!=200 or not isinstance(p,dict) or p.get("mergeable") is not None: break
            time.sleep(2)
        c,p=final
        dump(pdir/"pr.json",{"status":c,"polls":polls,"body":p})
        if c!=200 or not isinstance(p,dict):
            errors.append([num,"pr",c]); continue

        merge_sha=p.get("merge_commit_sha")
        ep={}
        # Complete review list.
        rv,reviews,rvpages,rvextra=request_all_list(f"/repos/{REPO}/pulls/{num}/reviews")
        dump(pdir/"reviews.json",{"status":rv,"page_statuses":rvpages,"body":reviews,"extra":rvextra})
        ep["reviews"]=rv

        # Complete PR commit list + verification.
        cc,commits,cpages,cextra=request_all_list(f"/repos/{REPO}/pulls/{num}/commits")
        dump(pdir/"commits.json",{"status":cc,"page_statuses":cpages,"body":commits,"extra":cextra})
        ep["commits"]=cc
        verification=[]
        for cm in commits:
            ver=((cm.get("commit") or {}).get("verification") or {})
            verification.append({
                "sha":cm.get("sha"),"verified":ver.get("verified"),
                "reason":ver.get("reason"),"verified_at":ver.get("verified_at"),
            })
        dump(pdir/"commit_verification.json",verification)

        if merge_sha:
            mc,checks,mcpages,mcextra=request_all_checks(f"/repos/{REPO}/commits/{merge_sha}/check-runs")
            dump(pdir/"merge_check_runs.json",{"status":mc,"page_statuses":mcpages,"body":checks,"extra":mcextra})
            ep["merge_check_runs"]=mc
            ms,status=request(f"/repos/{REPO}/commits/{merge_sha}/status")
            dump(pdir/"merge_combined_status.json",{"status":ms,"body":status})
            ep["merge_combined_status"]=ms
        else:
            ep["merge_check_runs"]=None; ep["merge_combined_status"]=None

        for k,v in ep.items():
            if v not in (200,None): errors.append([num,k,v])
        latest={}
        for review in reviews:
            user=(review.get("user") or {}).get("login")
            if not user: continue
            if user not in latest or (review.get("submitted_at") or "") >= (latest[user].get("submitted_at") or ""):
                latest[user]=review
        approvals=sum(1 for x in latest.values() if x.get("state")=="APPROVED")

        rows.append({
            "repo":REPO,"pr":num,"base":(p.get("base") or {}).get("ref"),
            "head_sha":(p.get("head") or {}).get("sha"),
            "merge_commit_sha":merge_sha,"draft":p.get("draft"),
            "native_label":label_pr(p),"poll_count":len(polls),
            "visible_latest_approvals":approvals,
            "review_rows":len(reviews),"commit_rows":len(commits),
            "endpoint_status":ep,
        })

    dump(out/"summary.json",rows)
    dump(out/"errors.json",errors)
    report={
        "schema":"eeq-github-v2-third-sample-native",
        "repo":REPO,"base":BASE,"selected":len(selected),"collected":len(rows),
        "label_histogram":{k:sum(r["native_label"]==k for r in rows) for k in
            ["NATIVE_ADMISSIBLE","NATIVE_BLOCKED","DRAFT","CONFLICT","NATIVE_ORACLE_AMBIGUOUS"]},
        "selection_used_native_labels":False,
        "adapter_scoring_performed":False,
        "errors":len(errors),
    }
    dump(out/"report.json",report)

    entries=[]
    for p in sorted(out.rglob("*")):
        if p.is_file() and p.name!="SHA256SUMS.txt":
            entries.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out)}")
    (out/"SHA256SUMS.txt").write_text("\n".join(entries)+"\n",encoding="utf-8")
    print(json.dumps(report,sort_keys=True))

if __name__=="__main__":
    main()
