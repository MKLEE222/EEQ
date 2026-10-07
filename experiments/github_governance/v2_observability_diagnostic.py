#!/usr/bin/env python3
"""GitHub governance v2 development-only observability diagnostic.

This script does not score an adapter and does not use native labels to decide
what evidence to fetch. It enriches the already-frozen second sample with:
- synthetic/test merge commit check-runs and combined statuses;
- explicit classic branch-protection endpoint status;
- issue timeline events for push-actor observability auditing.

The resulting evidence may be used to design adapter v2, which must be frozen
before a fresh third mechanical sample is collected.
"""
import argparse, json, os, urllib.error, urllib.parse, urllib.request
from collections import Counter, defaultdict
from pathlib import Path

API="https://api.github.com"
TOKEN=os.environ.get("GITHUB_TOKEN","")

def request(path, accept="application/vnd.github+json"):
    url=path if path.startswith("http") else API+path
    headers={
        "Accept":accept,
        "User-Agent":"EEQ-GitHub-governance-v2-diagnostic",
        "X-GitHub-Api-Version":"2022-11-28",
    }
    if TOKEN:
        headers["Authorization"]="Bearer "+TOKEN
    req=urllib.request.Request(url,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=60) as r:
            data=r.read().decode("utf-8")
            return r.status, json.loads(data) if data else None
    except urllib.error.HTTPError as e:
        raw=e.read().decode("utf-8",errors="replace")
        try: body=json.loads(raw)
        except Exception: body={"raw":raw}
        return e.code,body

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def wrapper(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("second_native",type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    root=args.second_native
    out=args.out
    summary=json.loads((root/"summary.json").read_text(encoding="utf-8"))
    branch_cache={}
    rows=[]
    endpoint_counts=Counter()
    timeline_event_counts=Counter()
    for native in summary:
        repo=native["repo"]; num=native["pr"]
        owner,name=repo.split("/",1)
        pdir=root/owner/name/"prs"/str(num)
        prw=wrapper(pdir/"pr.json")
        pr=prw.get("body") or {}
        merge_sha=pr.get("merge_commit_sha")
        base=(pr.get("base") or {}).get("ref")
        record={
            "repo":repo,
            "pr":num,
            "base":base,
            "head_sha":(pr.get("head") or {}).get("sha"),
            "merge_commit_sha":merge_sha,
            "merge_commit_differs_from_head":bool(merge_sha and merge_sha!=(pr.get("head") or {}).get("sha")),
            "endpoint_status":{},
        }

        if merge_sha:
            for key,path in {
                "merge_check_runs":f"/repos/{repo}/commits/{merge_sha}/check-runs?per_page=100",
                "merge_combined_status":f"/repos/{repo}/commits/{merge_sha}/status",
            }.items():
                code,body=request(path)
                dump(out/owner/name/"prs"/str(num)/(key+".json"),{"status":code,"body":body})
                record["endpoint_status"][key]=code
                endpoint_counts[(key,code)]+=1
        else:
            record["endpoint_status"]["merge_check_runs"]=None
            record["endpoint_status"]["merge_combined_status"]=None

        # Timeline is diagnostic only: determine whether GitHub exposes a
        # reliable actor for the most recent reviewable push.
        code,body=request(f"/repos/{repo}/issues/{num}/timeline?per_page=100")
        dump(out/owner/name/"prs"/str(num)/"timeline.json",{"status":code,"body":body})
        record["endpoint_status"]["timeline"]=code
        endpoint_counts[("timeline",code)]+=1
        if code==200 and isinstance(body,list):
            types=Counter(x.get("event","__NONE__") for x in body if isinstance(x,dict))
            for k,v in types.items():
                timeline_event_counts[k]+=v
            # A committed event exposes commit author/committer but no GitHub
            # push actor. Preserve a mechanical indicator rather than infer it.
            committed=[x for x in body if isinstance(x,dict) and x.get("event")=="committed"]
            record["timeline_committed_events"]=len(committed)
            record["timeline_committed_with_actor"]=sum(
                1 for x in committed if isinstance(x.get("actor"),dict) and x["actor"].get("login")
            )

        bkey=(repo,base)
        if base and bkey not in branch_cache:
            enc=urllib.parse.quote(base,safe="")
            code,body=request(f"/repos/{repo}/branches/{enc}/protection")
            dump(out/owner/name/"branch_protection"/(enc+".json"),{"status":code,"body":body})
            branch_cache[bkey]=code
            endpoint_counts[("classic_branch_protection",code)]+=1
        if base:
            record["endpoint_status"]["classic_branch_protection"]=branch_cache[bkey]
        rows.append(record)

    counts={
        "sample_rows":len(rows),
        "merge_commit_sha_present":sum(bool(r["merge_commit_sha"]) for r in rows),
        "merge_commit_differs_from_head":sum(r["merge_commit_differs_from_head"] for r in rows),
        "merge_check_runs_200":sum(r["endpoint_status"].get("merge_check_runs")==200 for r in rows),
        "merge_combined_status_200":sum(r["endpoint_status"].get("merge_combined_status")==200 for r in rows),
        "timeline_200":sum(r["endpoint_status"].get("timeline")==200 for r in rows),
        "timeline_committed_events":sum(r.get("timeline_committed_events",0) for r in rows),
        "timeline_committed_with_actor":sum(r.get("timeline_committed_with_actor",0) for r in rows),
        "classic_branch_keys":len(branch_cache),
        "classic_branch_protection_statuses":dict(sorted(Counter(branch_cache.values()).items())),
        "endpoint_status_counts":{
            f"{k[0]}:{k[1]}":v for k,v in sorted(endpoint_counts.items(),key=lambda x:str(x[0]))
        },
        "timeline_event_counts":dict(sorted(timeline_event_counts.items())),
        "adapter_scoring_performed":False,
        "sample_role":"development diagnostic on frozen second sample",
        "third_sample_opened":False,
        "fifth_family_holdout":"UNOPENED",
    }
    dump(out/"rows.json",rows)
    dump(out/"summary.json",counts)
    print(json.dumps(counts,sort_keys=True))

if __name__=="__main__":
    main()
