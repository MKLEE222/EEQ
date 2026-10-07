#!/usr/bin/env python3
import json, os, sys, time, hashlib, urllib.request, urllib.parse, urllib.error
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "github-validation-sample")
OUT.mkdir(parents=True, exist_ok=True)
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"
REPOS = ["nodejs/node", "microsoft/vscode", "home-assistant/core", "llvm/llvm-project"]
PER_REPO = 25
OFFSET = 25
COLLECTOR_VERSION = "validation-v1"

def request(path):
    url = path if path.startswith("http") else API + path
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "EEQ-GitHub-validation/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw=r.read().decode("utf-8")
            return r.status, json.loads(raw)
    except urllib.error.HTTPError as e:
        raw=e.read().decode("utf-8",errors="replace")
        try: body=json.loads(raw)
        except Exception: body={"raw":raw}
        return e.code, body

def request_list_all(path, per_page=100, max_pages=30):
    sep="&" if "?" in path else "?"
    rows=[]; statuses=[]
    for page in range(1,max_pages+1):
        code,body=request(f"{path}{sep}per_page={per_page}&page={page}")
        statuses.append(code)
        if code != 200 or not isinstance(body,list):
            return code,rows,statuses,body
        rows.extend(body)
        if len(body)<per_page:
            return 200,rows,statuses,None
    return 206,rows,statuses,{"reason":"max_pages_reached"}

def request_check_runs_all(path, per_page=100, max_pages=30):
    sep="&" if "?" in path else "?"
    rows=[]; statuses=[]; total=None
    for page in range(1,max_pages+1):
        code,body=request(f"{path}{sep}per_page={per_page}&page={page}")
        statuses.append(code)
        if code != 200 or not isinstance(body,dict) or not isinstance(body.get("check_runs"),list):
            return code,rows,statuses,body
        if total is None: total=body.get("total_count")
        part=body["check_runs"]; rows.extend(part)
        if len(part)<per_page:
            return 200,rows,statuses,{"total_count":total}
    return 206,rows,statuses,{"reason":"max_pages_reached","total_count":total}

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

errors=[]
summary=[]
branch_cache={}

for repo in REPOS:
    owner,name=repo.split("/",1)
    rdir=OUT/owner/name

    code,rulesets=request(f"/repos/{repo}/rulesets")
    dump(rdir/"rulesets.list.json",{"status":code,"body":rulesets})
    if code==200 and isinstance(rulesets,list):
        for rs in rulesets:
            rid=rs.get("id")
            c,b=request(f"/repos/{repo}/rulesets/{rid}")
            dump(rdir/"rulesets"/f"{rid}.json",{"status":c,"body":b})
            if c!=200: errors.append([repo,f"ruleset/{rid}",c])
    else:
        errors.append([repo,"rulesets",code])

    q=urllib.parse.urlencode({
        "state":"open","sort":"updated","direction":"desc",
        "per_page":OFFSET+PER_REPO,"page":1
    })
    code,prs=request(f"/repos/{repo}/pulls?{q}")
    dump(rdir/"prs.selection.json",{
        "status":code,
        "selection_rule":{
            "sort":"updated","direction":"desc","offset":OFFSET,"count":PER_REPO
        },
        "body":prs if isinstance(prs,list) else prs,
    })
    if code!=200 or not isinstance(prs,list):
        errors.append([repo,"prs.selection",code]); continue

    selected=prs[OFFSET:OFFSET+PER_REPO]
    for item in selected:
        num=item["number"]; pdir=rdir/"prs"/str(num)
        final=None; polls=[]
        for attempt in range(1,4):
            c,p=request(f"/repos/{repo}/pulls/{num}")
            polls.append({
                "attempt":attempt,"status":c,
                "mergeable":p.get("mergeable") if isinstance(p,dict) else None,
                "mergeable_state":p.get("mergeable_state") if isinstance(p,dict) else None,
            })
            final=(c,p)
            if c!=200 or not isinstance(p,dict) or p.get("mergeable") is not None: break
            time.sleep(2)
        c,p=final
        if c!=200 or not isinstance(p,dict):
            errors.append([repo,f"pr/{num}",c]); continue

        head=(p.get("head") or {}).get("sha")
        base=(p.get("base") or {}).get("ref")
        base_sha=(p.get("base") or {}).get("sha")
        merge_sha=p.get("merge_commit_sha")
        author=p.get("user") or {}

        # Physically separated safe adapter input. No mergeability/native label.
        adapter_input={
            "repo":repo,"pr":num,"base":base,"base_sha":base_sha,
            "head_sha":head,"merge_commit_sha":merge_sha,
            "author_login":author.get("login"),"author_type":author.get("type"),
            "updated_at":p.get("updated_at"),
        }
        dump(pdir/"adapter_pr_input.json",adapter_input)

        # Physically separated native oracle. Adapter v1 never opens this file.
        native={
            "repo":repo,"pr":num,"polls":polls,
            "draft":p.get("draft"),"mergeable":p.get("mergeable"),
            "mergeable_state":p.get("mergeable_state"),
            "native_label":label_pr(p),
        }
        dump(pdir/"native_oracle.json",native)

        if base:
            bkey=(repo,base)
            if bkey not in branch_cache:
                enc=urllib.parse.quote(base,safe="")
                bc,branch=request(f"/repos/{repo}/branches/{enc}")
                dump(rdir/"branches"/f"{enc}.json",{"status":bc,"body":branch})
                rc,rules=request(f"/repos/{repo}/rules/branches/{enc}")
                dump(rdir/"effective_rules"/f"{enc}.json",{"status":rc,"body":rules})
                branch_cache[bkey]=(bc,rc)
                if bc!=200: errors.append([repo,f"branch/{base}",bc])
                if rc!=200: errors.append([repo,f"effective_rules/{base}",rc])

        # Reviews, plus exact calculated repository permission for every reviewer.
        rv_code,reviews,rv_pages,rv_extra=request_list_all(f"/repos/{repo}/pulls/{num}/reviews")
        dump(pdir/"reviews.json",{"status":rv_code,"page_statuses":rv_pages,"body":reviews,"extra":rv_extra})
        if rv_code!=200: errors.append([repo,f"pr/{num}/reviews",rv_code])
        perms={}
        raw_perms={}
        for login in sorted({(r.get("user") or {}).get("login") for r in reviews if isinstance(r,dict)}-{None}):
            pc,pb=request(f"/repos/{repo}/collaborators/{urllib.parse.quote(login,safe='')}/permission")
            raw_perms[login]={"status":pc,"body":pb}
            perms[login]={
                "status":pc,
                "permission":pb.get("permission") if pc==200 and isinstance(pb,dict) else None,
                "role_name":pb.get("role_name") if pc==200 and isinstance(pb,dict) else None,
            }
            # 404 legitimately means no calculated repository permission.
            if pc not in (200,404): errors.append([repo,f"permission/{login}",pc])
        dump(pdir/"reviewer_permissions.raw.json",raw_perms)
        dump(pdir/"reviewer_permissions.json",perms)

        # Required checks can be evaluated on the PR test-merge commit when it
        # carries status information; archive both merge and head candidates.
        for prefix,sha in [("head",head),("merge",merge_sha)]:
            if not sha:
                dump(pdir/f"{prefix}_check_runs.json",{"status":0,"body":[],"reason":"missing_sha"})
                dump(pdir/f"{prefix}_statuses.json",{"status":0,"body":[],"reason":"missing_sha"})
                continue
            cc,checks,cpages,cextra=request_check_runs_all(f"/repos/{repo}/commits/{sha}/check-runs")
            dump(pdir/f"{prefix}_check_runs.json",{
                "status":cc,"page_statuses":cpages,
                "body":{"total_count":len(checks),"check_runs":checks},"extra":cextra
            })
            if cc!=200: errors.append([repo,f"pr/{num}/{prefix}_checks",cc])

            sc,statuses,spages,sextra=request_list_all(f"/repos/{repo}/commits/{sha}/statuses")
            dump(pdir/f"{prefix}_statuses.json",{
                "status":sc,"page_statuses":spages,"body":statuses,"extra":sextra
            })
            if sc!=200: errors.append([repo,f"pr/{num}/{prefix}_statuses",sc])

        cc,commits,cpages,cextra=request_list_all(f"/repos/{repo}/pulls/{num}/commits")
        dump(pdir/"commits.json",{"status":cc,"page_statuses":cpages,"body":commits,"extra":cextra})
        if cc!=200: errors.append([repo,f"pr/{num}/commits",cc])

        fc,files,fpages,fextra=request_list_all(f"/repos/{repo}/pulls/{num}/files")
        dump(pdir/"changed_files.json",{"status":fc,"page_statuses":fpages,"body":files,"extra":fextra})
        if fc!=200: errors.append([repo,f"pr/{num}/files",fc])

        verification=[]
        for cm in commits:
            ver=((cm.get("commit") or {}).get("verification") or {})
            verification.append({
                "sha":cm.get("sha"),"verified":ver.get("verified"),
                "reason":ver.get("reason"),"verified_at":ver.get("verified_at"),
                "author_login":(cm.get("author") or {}).get("login"),
                "committer_login":(cm.get("committer") or {}).get("login"),
                "message":((cm.get("commit") or {}).get("message")),
            })
        dump(pdir/"commit_verification.json",verification)

        summary.append({
            "repo":repo,"pr":num,"base":base,"head_sha":head,
            "native_label":native["native_label"],
        })

dump(OUT/"native_summary.json",summary)
dump(OUT/"errors.json",errors)
dump(OUT/"collection_contract.json",{
    "collector_version":COLLECTOR_VERSION,
    "repos":REPOS,
    "per_repo":PER_REPO,
    "offset":OFFSET,
    "selection":"open PRs sorted updated desc, positions 26-50 at collection time",
    "adapter_oracle_physical_separation":True,
})

entries=[]
for p in sorted(OUT.rglob("*")):
    if p.is_file() and p.name!="SHA256SUMS.txt":
        entries.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT)}")
(OUT/"SHA256SUMS.txt").write_text("\n".join(entries)+"\n",encoding="utf-8")

counts={}
for r in summary: counts[r["native_label"]]=counts.get(r["native_label"],0)+1
print(json.dumps({"cases":len(summary),"labels":counts,"endpoint_errors":len(errors)},sort_keys=True))
if errors:
    print(json.dumps(errors),file=sys.stderr)
