#!/usr/bin/env python3
import json, subprocess, sys, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
EVAL=HERE/"evaluate_validation_v1.py"

def dump(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj))

with tempfile.TemporaryDirectory() as td:
    root=Path(td)/"sample"
    repo=root/"o"/"r"
    rules={"status":200,"body":[{"type":"pull_request","parameters":{"required_approving_review_count":1}}]}
    dump(repo/"effective_rules"/"main.json",rules)

    adapter_rows=[]
    cases=[
      (1,"NATIVE_ADMISSIBLE","PREDICT_ADMISSIBLE"),
      (2,"NATIVE_ADMISSIBLE","PREDICT_ADMISSIBLE"), # exact semantic duplicate
      (3,"NATIVE_BLOCKED","PREDICT_ADMISSIBLE"),    # forces signature label conflict
      (4,"DRAFT","PREDICT_ADMISSIBLE"),
      (5,"NATIVE_BLOCKED","ADAPTER_UNSUPPORTED"),
    ]
    for pr,native,pred in cases:
        pdir=repo/"prs"/str(pr)
        dump(pdir/"adapter_pr_input.json",{
          "repo":"o/r","pr":pr,"base":"main","head_sha":f"h{pr}",
          "merge_commit_sha":f"m{pr}","author_login":"u","author_type":"User",
        })
        dump(pdir/"native_oracle.json",{"native_label":native})
        adapter_rows.append({
          "repo":"o/r","pr":pr,"prediction":pred,
          "unsupported":["x"] if pred=="ADAPTER_UNSUPPORTED" else [],
          "blockers":[],
          "evidence":[
            {"kind":"check_target","source":"head","sha":f"h{pr}"},
            {"kind":"review_summary","required_approvals":1,
             "authorized_approvals":["alice"],"authorized_change_requests":[],
             "unknown_permission_reviewers":[]},
          ],
        })

    adapter={"rows":adapter_rows}
    ap=Path(td)/"adapter.json"; out=Path(td)/"report.json"
    dump(ap,adapter)
    subprocess.run([sys.executable,str(EVAL),str(root),str(ap),"--out",str(out)],check=True)
    report=json.loads(out.read_text())
    s=report["summary"]
    assert s["collected_cases"]==5,s
    assert s["supported_native_scored_cases"]==3,s
    assert s["correct"]==2,s
    assert s["mismatches"]==1,s
    assert s["deduplicated_supported_semantic_cases"]==1,s
    assert s["semantic_signature_label_conflicts"]==1,s
    assert s["dispositions"]["NATIVE_NONSCORED"]==1,s
    assert s["dispositions"]["ADAPTER_UNSUPPORTED"]==1,s

print("evaluate_validation_v1 synthetic tests: ok")
