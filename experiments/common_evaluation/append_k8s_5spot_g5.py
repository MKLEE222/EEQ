#!/usr/bin/env python3
"""Append the frozen 5-Spot Kubernetes carrier to the integrated G4 ledger.

Two Kubernetes versions are execution replications of the same 38 preregistered
semantic cases. The script verifies exact cross-version agreement, constructs
G4 semantic signatures without version/retry inflation, and refuses to pass G5
unless the resulting deduplicated count is derived mechanically.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

DOMAIN = "K8s:5spot-vap"
EVIDENCE = "PUBLIC_MAINTAINED_CONFIG_NATIVE_REPLAY"
RUN_ID = 37565593683
SOURCES = {
    "v1.34.3": {
        "artifact_id": 11458747514,
        "zip_sha256": "578eeb44a000a9889c615d6abe6e0461581607bd7b497f3fc7232079db75cc8b",
    },
    "v1.35.0": {
        "artifact_id": 11458757437,
        "zip_sha256": "b8bc280f2f92d79df1e9c83fd3b55230581a091a589276386fb969ab24bc8984",
    },
}

def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

def digest(v):
    return hashlib.sha256(canonical(v).encode("utf-8")).hexdigest()

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def validate_run(root, version):
    root=Path(root)
    summary=load(root/"summary.json")
    rows=load(root/"grid_results.json")
    expected={
        "frozen_rows":38,
        "eligible_rows":38,
        "preexcluded_native_schema_invalid":0,
        "passes":38,
        "mismatches":0,
        "ambiguous_eligible_rows":0,
    }
    for k,v in expected.items():
        if summary.get(k)!=v:
            raise ValueError(f"{version} summary mismatch for {k}: {summary.get(k)} != {v}")
    if len(rows)!=38:
        raise ValueError(f"{version} grid must retain 38 rows")
    by_id={}
    for row in rows:
        if row["id"] in by_id:
            raise ValueError(f"duplicate row id {row['id']} in {version}")
        if row.get("status")!="PASS" or row.get("observed")!=row.get("expected"):
            raise ValueError(f"non-passing row in {version}: {row['id']}")
        if row.get("attribution") not in {"ADMITTED","TARGET_POLICY"}:
            raise ValueError(f"bad attribution in {version}: {row['id']} {row.get('attribution')}")
        by_id[row["id"]]=row
    return by_id

def semantic_signature(row):
    state={
        "binding_scope": row["scope"],
        "namespace": row["namespace"],
        "service_account": row["service_account"],
        "identity": row["identity"],
        "security_profile": row["profile"],
    }
    return {
        "semantic_domain": DOMAIN,
        "pre_action_state": state,
        "registered_action": "CREATE Pod",
        "future_contract": "5SPOT_VAP_ADMISSION",
        "native_action_vocabulary": ["ACCEPT","REJECT"],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-ledger", required=True, type=Path)
    ap.add_argument("--v134", required=True, type=Path)
    ap.add_argument("--v135", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a=ap.parse_args()

    ledger=load(a.base_ledger)
    if ledger["summary"]["scored_unique_semantic_cases"]!=247:
        raise ValueError("base integrated ledger must contain exactly 247 G4-counted cases")
    if ledger["summary"].get("fifth_family_holdout")!="UNOPENED":
        raise ValueError("fifth-family holdout unexpectedly opened")

    runs={
        "v1.34.3": validate_run(a.v134, "v1.34.3"),
        "v1.35.0": validate_run(a.v135, "v1.35.0"),
    }
    ids=set(runs["v1.34.3"])
    if ids!=set(runs["v1.35.0"]) or len(ids)!=38:
        raise ValueError("Kubernetes version runs do not cover the same 38 frozen cases")

    existing={c["semantic_id"]:c for c in ledger["cases"]}
    new_cases={}
    new_exec=[]
    for case_id in sorted(ids):
        r34=runs["v1.34.3"][case_id]
        r35=runs["v1.35.0"][case_id]
        frozen_fields=("scope","namespace","service_account","identity","profile","expected")
        if any(r34.get(k)!=r35.get(k) for k in frozen_fields):
            raise ValueError(f"cross-version frozen-state disagreement: {case_id}")
        if r34["observed"]!=r35["observed"]:
            raise ValueError(f"cross-version native-action disagreement: {case_id}")

        sig=semantic_signature(r34)
        sid=digest(sig)
        if sid in existing:
            raise ValueError(f"5-Spot semantic signature collides with pre-existing case: {case_id}")
        if sid in new_cases:
            raise ValueError(f"5-Spot semantic dedup collision: {case_id}")

        new_cases[sid]={
            "semantic_id":sid,
            "signature":sig,
            "family":"K8s",
            "environments":["k8s-v1.34.3","k8s-v1.35.0"],
            "evidence_classes":[EVIDENCE],
            "native_action":r34["observed"],
            "frozen_expected":r34["expected"],
            "execution_ids":[f"5spot-v1.34.3-{case_id}",f"5spot-v1.35.0-{case_id}"],
        }
        for version,row in (("v1.34.3",r34),("v1.35.0",r35)):
            new_exec.append({
                "execution_id":f"5spot-{version}-{case_id}",
                "semantic_id":sid,
                "environment":f"k8s-{version}",
                "source_artifact":f"k8s_5spot_{version}",
                "evidence_class":EVIDENCE,
                "status":"SCORED",
                "native_action":row["observed"],
                "frozen_expected":row["expected"],
                "match":True,
                "native_attribution":row["attribution"],
                "decision_ns":row.get("decision_ns"),
            })

    if len(new_cases)!=38 or len(new_exec)!=76:
        raise ValueError("unexpected 5-Spot case/execution cardinality")

    ledger["cases"].extend(new_cases.values())
    ledger["cases"]=sorted(ledger["cases"],key=lambda x:(x["family"],x["semantic_id"]))
    ledger["executions"].extend(new_exec)
    ledger["schema"]="eeq-g4-unified-case-ledger-g5-v1"
    ledger["source_artifacts"]["k8s_5spot_v1.34.3"]={
        "run_id":RUN_ID, **SOURCES["v1.34.3"]}
    ledger["source_artifacts"]["k8s_5spot_v1.35.0"]={
        "run_id":RUN_ID, **SOURCES["v1.35.0"]}

    ledger["summary"]["scored_unique_semantic_cases"]=len(ledger["cases"])
    ledger["summary"]["all_executions"]=len(ledger["executions"])
    ledger["summary"]["execution_statuses"]=dict(sorted(Counter(
        x["status"] for x in ledger["executions"]).items()))
    ledger["summary"]["unique_by_domain"]=dict(sorted(Counter(
        c["signature"]["semantic_domain"] for c in ledger["cases"]).items()))
    ledger["summary"]["g5_target"]=250
    ledger["summary"]["g5_status"]="PASS" if len(ledger["cases"])>=250 else "OPEN"
    ledger["summary"]["fifth_family_holdout"]="UNOPENED"

    if ledger["summary"]["scored_unique_semantic_cases"]!=285:
        raise ValueError(f"deduplicated count is {ledger['summary']['scored_unique_semantic_cases']}, expected 285")
    if ledger["summary"]["g5_status"]!="PASS":
        raise ValueError("G5 did not close")

    a.out.write_text(json.dumps(ledger,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "base_semantic_cases":247,
        "new_5spot_semantic_cases":len(new_cases),
        "new_5spot_executions":len(new_exec),
        "scored_unique_semantic_cases":ledger["summary"]["scored_unique_semantic_cases"],
        "all_executions":ledger["summary"]["all_executions"],
        "g5_status":ledger["summary"]["g5_status"],
        "fifth_family_holdout":ledger["summary"]["fifth_family_holdout"],
    },sort_keys=True))

if __name__=="__main__":
    main()
