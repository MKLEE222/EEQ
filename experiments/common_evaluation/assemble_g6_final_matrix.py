#!/usr/bin/env python3
"""Assemble the final G6 19-column matrix inputs without redefining baselines.

This script is intentionally non-semantic. B0-B9/O1-O8 come from already
frozen family-specific representation builders. B10 comes only from the frozen
generic WFC compiler v1. The script performs joins and consistency checks.
"""
import argparse
import json
from pathlib import Path

IDS=[f"B{i}" for i in range(11)]+[f"O{i}" for i in range(1,9)]
NA="__NOT_APPLICABLE__"

APT_DOMAIN="APT:releaseinfo"
K8S_COMMON={"K8s:flux-vap","K8s:gcsfuse-vap","K8s:volcano-vap"}
K8S_5SPOT="K8s:5spot-vap"
TUF_DOMAIN="TUF:bottlerocket-root"

APT_NA_REASONS={
    "B7":"Frozen APT carrier has no independent behavioral predictor or learned state",
    "O6":"Frozen APT carrier has one registered update action; no alternate action-conditioned successor model",
    "O7":"Frozen APT carrier itself has a one-transition horizon",
    "O8":"Frozen APT carrier has one configured Signed-By support binding",
}

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def apt_key_from_aggregate(r):
    return (
        bool(r["qualified"]),
        tuple((k,bool(r["protected_changed"][k])) for k in ("Origin","Label","Codename")),
        bool(r["allow_global"]),
        tuple(sorted(r["allow_fields"])),
    )

def apt_key_from_case(c):
    s=c["signature"]["pre_action_state"]
    return (
        bool(s["qualified"]),
        tuple((k,bool(s["protected_changed"][k])) for k in ("Origin","Label","Codename")),
        bool(s["allow_global"]),
        tuple(sorted(s["allow_fields"])),
    )

def index_unique(rows,key_name):
    out={}
    for r in rows:
        k=r[key_name]
        if k in out:
            raise ValueError(f"duplicate {key_name}={k}")
        out[k]=r
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--g5-ledger",required=True)
    ap.add_argument("--apt-aggregate",required=True)
    ap.add_argument("--apt-reps",required=True)
    ap.add_argument("--common-reps",required=True)
    ap.add_argument("--five-spot-reps",required=True)
    ap.add_argument("--tuf-reps",required=True)
    ap.add_argument("--generic-wfc",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    g5=load(args.g5_ledger)
    aptagg=load(args.apt_aggregate)
    aptreps=load(args.apt_reps)
    common=load(args.common_reps)
    spot=load(args.five_spot_reps)
    tuf=load(args.tuf_reps)
    generic=load(args.generic_wfc)

    g5_cases=index_unique(g5["cases"],"semantic_id")
    if len(g5_cases)!=285:
        raise ValueError(f"expected 285 G5 cases, got {len(g5_cases)}")

    generic_rows=index_unique(generic["rows"],"semantic_id")
    if set(generic_rows)!=set(g5_cases):
        raise ValueError("generic WFC semantic-id set differs from G5 case set")

    # Rejoin the historical APT G6 case_id rows to current G5 semantic IDs
    # using the exact frozen semantic dimensions. Suite/Version controls are
    # excluded from the semantic key by the original protocol.
    canonical={}
    for r in aptagg["rows"]:
        if r["suite_changed"] or r["version_changed"]:
            continue
        key=apt_key_from_aggregate(r)
        if key in canonical:
            raise ValueError(f"duplicate canonical APT semantic key {key}")
        canonical[key]=r
    if len(canonical)!=144:
        raise ValueError(f"expected 144 canonical APT aggregate rows, got {len(canonical)}")

    apt_by_case=index_unique(aptreps["rows"],"case_id")
    if len(apt_by_case)!=144:
        raise ValueError(f"expected 144 APT representation rows, got {len(apt_by_case)}")

    assembled={}
    apt_cases=[c for c in g5["cases"] if c["signature"]["semantic_domain"]==APT_DOMAIN]
    if len(apt_cases)!=144:
        raise ValueError(f"expected 144 G5 APT cases, got {len(apt_cases)}")
    for c in apt_cases:
        key=apt_key_from_case(c)
        src=canonical.get(key)
        if src is None:
            raise ValueError(f"no APT aggregate row for {c['semantic_id']}")
        rr=apt_by_case.get(src["semantic_template_id"])
        if rr is None:
            raise ValueError(f"missing APT frozen representation row {src['semantic_template_id']}")
        if rr["native_action"]!=c["native_action"]:
            raise ValueError(f"APT native-action mismatch for {c['semantic_id']}")
        reasons={k:v for k,v in APT_NA_REASONS.items() if rr["representations"].get(k)==NA}
        assembled[c["semantic_id"]]={
            "semantic_id":c["semantic_id"],
            "domain":APT_DOMAIN,
            "native_action":c["native_action"],
            "representations":dict(rr["representations"]),
            "not_applicable_reasons":reasons,
            "representation_source":"APT G6 pre-score frozen mapping",
        }

    for payload,allowed,source in [
        (common,K8S_COMMON,"G4 integrated frozen development mapping"),
        (spot,{K8S_5SPOT},"5-Spot post-native/pre-matrix frozen mapping"),
        (tuf,{TUF_DOMAIN},"TUF post-native/pre-matrix frozen mapping"),
    ]:
        for r in payload["rows"]:
            if r["domain"] not in allowed:
                continue
            sid=r["semantic_id"]
            if sid in assembled:
                raise ValueError(f"duplicate assembled semantic id {sid}")
            if sid not in g5_cases:
                raise ValueError(f"representation row not in G5 ledger: {sid}")
            if r["native_action"]!=g5_cases[sid]["native_action"]:
                raise ValueError(f"native-action mismatch for {sid}")
            assembled[sid]={
                "semantic_id":sid,
                "domain":r["domain"],
                "native_action":r["native_action"],
                "representations":dict(r["representations"]),
                "not_applicable_reasons":dict(r.get("not_applicable_reasons",{})),
                "representation_source":source,
            }

    if set(assembled)!=set(g5_cases):
        missing=sorted(set(g5_cases)-set(assembled))
        extra=sorted(set(assembled)-set(g5_cases))
        raise ValueError(f"assembled semantic-id mismatch missing={missing[:5]} extra={extra[:5]}")

    # The only semantic-column replacement performed here: B10 is the frozen,
    # domain-agnostic generic compiler output. No other representation changes.
    for sid,row in assembled.items():
        gr=generic_rows[sid]
        if gr["native_action"]!=row["native_action"]:
            raise ValueError(f"generic/native-action mismatch for {sid}")
        b10=gr.get("representations",{}).get("B10")
        if b10 is None:
            raise ValueError(f"generic B10 missing for {sid}")
        row["representations"]["B10"]=b10
        if set(row["representations"])!=set(IDS):
            raise ValueError(f"19-ID representation set mismatch for {sid}")
        for bid,val in row["representations"].items():
            if val==NA and bid not in row["not_applicable_reasons"]:
                raise ValueError(f"missing N/A reason for {sid}/{bid}")
            if val!=NA and bid in row["not_applicable_reasons"]:
                # Stale reason from a replaced/now-applicable field is not allowed.
                row["not_applicable_reasons"].pop(bid,None)

    rows=sorted(assembled.values(),key=lambda r:r["semantic_id"])
    domains={}
    for r in rows:
        domains[r["domain"]]=domains.get(r["domain"],0)+1
    expected={
        "APT:releaseinfo":144,
        "K8s:flux-vap":10,
        "K8s:gcsfuse-vap":14,
        "K8s:volcano-vap":72,
        "K8s:5spot-vap":38,
        "TUF:bottlerocket-root":7,
    }
    if domains!=expected:
        raise ValueError(f"domain counts mismatch: {domains}")

    payload={
        "schema":"eeq-g6-final-285-representations-v1",
        "rows":rows,
        "domains":domains,
        "assembly_rule":"B0-B9/O1-O8 from pinned historical frozen family mappings; B10 from generic WFC v1 only",
        "github":"excluded from 19-column family matrix because frozen v1 family-complete C1 is not established",
        "fifth_family_holdout":"UNOPENED",
    }
    Path(args.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"rows":len(rows),"domains":domains,"ids":len(IDS)},sort_keys=True))

if __name__=="__main__":
    main()
