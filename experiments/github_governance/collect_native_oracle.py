#!/usr/bin/env python3
import json, os, sys, time, hashlib, urllib.request, urllib.parse, urllib.error
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "github-native-oracle-results")
OUT.mkdir(parents=True, exist_ok=True)
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"
REPOS = ["nodejs/node", "microsoft/vscode", "home-assistant/core", "llvm/llvm-project"]
PER_REPO = 25

def request(path):
    url = path if path.startswith("http") else API + path
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "EEQ-GitHub-native-oracle/1.1",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try: data = json.loads(body)
        except Exception: data = {"raw": body}
        return e.code, data

def request_all(path, per_page=100, max_pages=20):
    sep = "&" if "?" in path else "?"
    out = []
    statuses = []
    for page in range(1, max_pages + 1):
        code, body = request(f"{path}{sep}per_page={per_page}&page={page}")
        statuses.append(code)
        if code != 200 or not isinstance(body, list):
            return code, out, statuses, body
        out.extend(body)
        if len(body) < per_page:
            return 200, out, statuses, None
    return 206, out, statuses, {"reason":"max_pages_reached","max_pages":max_pages}

def dump_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def label_pr(p):
    if p.get("draft"):
        return "DRAFT"
    m = p.get("mergeable")
    s = p.get("mergeable_state")
    if m is False:
        return "CONFLICT"
    if m is True and s == "clean":
        return "NATIVE_ADMISSIBLE"
    if m is True and s == "blocked":
        return "NATIVE_BLOCKED"
    return "NATIVE_ORACLE_AMBIGUOUS"

summary_rows = []
errors = []
branch_cache = {}

for repo in REPOS:
    owner, name = repo.split("/", 1)
    rdir = OUT / owner / name

    # Repository rulesets are archived independently of PR outcomes.
    code, rulesets = request(f"/repos/{repo}/rulesets")
    dump_json(rdir / "rulesets.list.json", {"status": code, "body": rulesets})
    if code == 200 and isinstance(rulesets, list):
        for rs in rulesets:
            rid = rs.get("id")
            c, detail = request(f"/repos/{repo}/rulesets/{rid}")
            dump_json(rdir / "rulesets" / f"{rid}.json", {"status": c, "body": detail})
            if c != 200:
                errors.append([repo, f"rulesets/{rid}", c])
    else:
        errors.append([repo, "rulesets", code])

    q = urllib.parse.urlencode({"state":"open","sort":"updated","direction":"desc","per_page":PER_REPO,"page":1})
    code, prs = request(f"/repos/{repo}/pulls?{q}")
    dump_json(rdir / "prs.list.json", {"status": code, "body": prs})
    if code != 200 or not isinstance(prs, list):
        errors.append([repo, "prs", code])
        continue

    for item in prs[:PER_REPO]:
        num = item["number"]
        pdir = rdir / "prs" / str(num)
        final = None
        polls = []
        for attempt in range(1, 4):
            c, p = request(f"/repos/{repo}/pulls/{num}")
            polls.append({
                "attempt":attempt,
                "status":c,
                "mergeable":p.get("mergeable") if isinstance(p,dict) else None,
                "mergeable_state":p.get("mergeable_state") if isinstance(p,dict) else None
            })
            final = (c,p)
            if c != 200 or not isinstance(p, dict) or p.get("mergeable") is not None:
                break
            time.sleep(2)
        c, p = final
        dump_json(pdir / "pr.json", {"status":c,"polls":polls,"body":p})
        if c != 200 or not isinstance(p,dict):
            errors.append([repo, f"pr/{num}", c])
            continue

        head = (p.get("head") or {}).get("sha")
        base = (p.get("base") or {}).get("ref")
        ep_status = {}

        # Archive branch-level native governance inputs once per repo/base.
        branch_key = (repo, base)
        if base and branch_key not in branch_cache:
            enc = urllib.parse.quote(base, safe="")
            bc, branch_obj = request(f"/repos/{repo}/branches/{enc}")
            dump_json(rdir / "branches" / f"{enc}.json", {"status":bc,"body":branch_obj})
            ep_status["base_branch"] = bc
            rc, effective_rules = request(f"/repos/{repo}/rules/branches/{enc}")
            dump_json(rdir / "effective_rules" / f"{enc}.json", {"status":rc,"body":effective_rules})
            ep_status["effective_rules"] = rc
            branch_cache[branch_key] = {"base_branch":bc,"effective_rules":rc}
            if bc != 200:
                errors.append([repo, f"branches/{base}", bc])
            if rc != 200:
                errors.append([repo, f"rules/branches/{base}", rc])
        elif base:
            ep_status.update(branch_cache[branch_key])

        endpoints = {
            "combined_status": f"/repos/{repo}/commits/{head}/status" if head else None,
            "check_runs": f"/repos/{repo}/commits/{head}/check-runs?per_page=100" if head else None,
            "reviews": f"/repos/{repo}/pulls/{num}/reviews?per_page=100",
            "requested_reviewers": f"/repos/{repo}/pulls/{num}/requested_reviewers",
            "head_commit": f"/repos/{repo}/commits/{head}" if head else None,
        }
        for key, path in endpoints.items():
            if not path:
                continue
            ec, body = request(path)
            dump_json(pdir / f"{key}.json", {"status":ec,"body":body})
            ep_status[key] = ec
            if ec != 200:
                errors.append([repo, f"pr/{num}/{key}", ec])

        # Full PR commit and changed-file ledgers. These are attribution inputs,
        # never native labels.
        cc, commits, cpages, cextra = request_all(f"/repos/{repo}/pulls/{num}/commits")
        dump_json(pdir / "commits.json", {
            "status":cc, "page_statuses":cpages, "body":commits, "extra":cextra
        })
        ep_status["commits"] = cc
        if cc != 200:
            errors.append([repo, f"pr/{num}/commits", cc])

        fc, files, fpages, fextra = request_all(f"/repos/{repo}/pulls/{num}/files")
        dump_json(pdir / "changed_files.json", {
            "status":fc, "page_statuses":fpages, "body":files, "extra":fextra
        })
        ep_status["changed_files"] = fc
        if fc != 200:
            errors.append([repo, f"pr/{num}/files", fc])

        verification = []
        for commit in commits:
            sha = commit.get("sha")
            ver = ((commit.get("commit") or {}).get("verification") or {})
            verification.append({
                "sha":sha,
                "verified":ver.get("verified"),
                "reason":ver.get("reason"),
                "verified_at":ver.get("verified_at"),
                "author_login":(commit.get("author") or {}).get("login"),
                "committer_login":(commit.get("committer") or {}).get("login")
            })
        dump_json(pdir / "commit_verification.json", verification)

        lab = label_pr(p)
        summary_rows.append({
            "repo": repo,
            "pr": num,
            "base": base,
            "head_sha": head,
            "draft": p.get("draft"),
            "mergeable": p.get("mergeable"),
            "mergeable_state": p.get("mergeable_state"),
            "native_label": lab,
            "poll_count": len(polls),
            "updated_at": p.get("updated_at"),
            "commit_count_archived": len(commits),
            "changed_file_count_archived": len(files),
            "verified_commit_count": sum(1 for v in verification if v.get("verified") is True),
            "endpoint_status": ep_status,
        })

dump_json(OUT / "summary.json", summary_rows)
dump_json(OUT / "errors.json", errors)

counts = {}
for r in summary_rows:
    counts[r["native_label"]] = counts.get(r["native_label"],0)+1
report = {
    "collector_version": "1.1",
    "repos": REPOS,
    "per_repo_target": PER_REPO,
    "cases_collected": len(summary_rows),
    "label_counts": counts,
    "errors": len(errors),
}
dump_json(OUT / "report.json", report)

entries=[]
for p in sorted(OUT.rglob("*")):
    if p.is_file() and p.name != "SHA256SUMS.txt":
        entries.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT)}")
(OUT / "SHA256SUMS.txt").write_text("\n".join(entries)+"\n",encoding="utf-8")

print(json.dumps(report, sort_keys=True))
for r in summary_rows:
    print("\t".join(str(r.get(k,"")) for k in [
        "repo","pr","base","head_sha","mergeable","mergeable_state",
        "native_label","poll_count","commit_count_archived","changed_file_count_archived"
    ]))
if errors:
    print("endpoint_errors="+json.dumps(errors), file=sys.stderr)
