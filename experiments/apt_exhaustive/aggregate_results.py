#!/usr/bin/env python3
import argparse, json
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--out",required=True); args=ap.parse_args()
files=sorted(Path(args.root).rglob("shard_results.json"))
rows=[]; versions=set(); shards=[]
for f in files:
    d=json.loads(f.read_text()); versions.add(d["apt_version"]); shards.append(d["shard_index"]); rows.extend(d["rows"])
ids=[r["id"] for r in rows]
if len(ids)!=len(set(ids)): raise SystemExit("duplicate ids")
rows=sorted(rows,key=lambda r:r["id"])
summary={
 "apt_versions":sorted(versions),
 "shards":sorted(shards),
 "total":len(rows),
 "matched":sum(r["match"] for r in rows),
 "mismatches":sum(not r["match"] for r in rows),
 "reject_other":sum(r["native_action"]=="REJECT_OTHER" for r in rows),
 "core_semantic_templates":len({r["semantic_template_id"] for r in rows}),
 "zero_control_variants":len({(r["suite_changed"],r["version_changed"]) for r in rows}),
 "native_action_counts":{a:sum(r["native_action"]==a for r in rows) for a in sorted({r["native_action"] for r in rows})},
 "rows":rows,
}
if summary["total"]!=576 or summary["core_semantic_templates"]!=144 or summary["zero_control_variants"]!=4:
    raise SystemExit(str({k:v for k,v in summary.items() if k!="rows"}))
Path(args.out).write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:v for k,v in summary.items() if k!="rows"},indent=2,sort_keys=True))
if summary["mismatches"] or summary["reject_other"]: raise SystemExit(2)
