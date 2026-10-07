#!/usr/bin/env python3
import argparse, json
from collections import defaultdict
from pathlib import Path

NA="__NOT_APPLICABLE__"
PROTECTED=("Origin","Label","Codename")
BASE={"Origin":"EEQ-Origin-A","Label":"EEQ-Label-A","Codename":"alpha","Suite":"stable","Version":"1"}
ALT={"Origin":"EEQ-Origin-B","Label":"EEQ-Label-B","Codename":"beta","Suite":"testing","Version":"2"}

def current_fields(r):
    out=dict(BASE)
    for f in PROTECTED:
        if r["protected_changed"][f]:
            out[f]=ALT[f]
    if r["suite_changed"]:
        out["Suite"]=ALT["Suite"]
    if r["version_changed"]:
        out["Version"]=ALT["Version"]
    return out

def contract(r):
    return {
        "allow_global":bool(r["allow_global"]),
        "allow_fields":sorted(r["allow_fields"]),
    }

def unresolved(r):
    if r["allow_global"]:
        return []
    allowed=set(r["allow_fields"])
    return sorted(f for f in PROTECTED if r["protected_changed"][f] and f not in allowed)

def build_rep(r):
    source=r["current_signer"]
    qual=bool(r["qualified"])
    changed={f:bool(r["protected_changed"][f]) for f in PROTECTED}
    c=contract(r)
    u=unresolved(r)
    cur=current_fields(r)

    reps={
      "B0":{
        "signer_lineage":source,
        "qualified":qual,
        "pre_metadata":dict(BASE),
        "current_metadata":cur,
        "continuation_contract":c,
      },
      "B1":{
        "current_signer_lineage":source,
        "current_metadata":cur,
      },
      "B2":{"configured_signature_authentication":qual},
      "B3":{"authorized_qualified_source":qual},
      "B4":{"signer_lineage":source},
      "B5":{"signer_lineage":source,"qualified":qual},
      "B6":{
        "signer_lineage":source,
        "qualified":qual,
        "protected_changed":changed,
      },
      "B7":NA,
      "B8":{
        "qualified":qual,
        "protected_changed":changed,
      },
      "B9":{
        "qualified":qual,
        "protected_changed":changed,
        "allow_global":c["allow_global"],
        "allow_fields":c["allow_fields"],
      },
      "B10":{
        "signer_lineage":source,
        "qualified":qual,
        "unresolved_continuation_obligations":u,
      },
      "O1":{
        "qualified":qual,
        "unresolved_continuation_obligations":u,
      },
      "O2":{
        "signer_lineage":source,
        "unresolved_continuation_obligations":u,
      },
      "O3":{
        "signer_lineage":source,
        "qualified":qual,
        "protected_change_count":sum(changed.values()),
        "allow_global":c["allow_global"],
        "allowed_field_count":len(c["allow_fields"]),
      },
      "O4":{
        "signer_lineage":source,
        "qualified":qual,
        "continuation_contract":c,
      },
      "O5":{
        "signer_lineage":source,
        "qualified":qual,
        "protected_changed":changed,
      },
      "O6":NA,
      "O7":NA,
      "O8":NA,
    }
    return reps

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("aggregate")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    data=json.loads(Path(args.aggregate).read_text())
    if data.get("total")!=576 or data.get("core_semantic_templates")!=144:
        raise SystemExit("unexpected APT exhaustive aggregate dimensions")
    if data.get("mismatches")!=0 or data.get("reject_other")!=0:
        raise SystemExit("native exhaustive aggregate contains mismatches/REJECT_OTHER")

    groups=defaultdict(list)
    for r in data["rows"]:
        groups[r["semantic_template_id"]].append(r)
    if len(groups)!=144:
        raise SystemExit(f"expected 144 templates, got {len(groups)}")

    out_rows=[]
    for tid,rows in sorted(groups.items()):
        if len(rows)!=4:
            raise SystemExit(f"{tid}: expected four zero-control variants")
        controls={(bool(r["suite_changed"]),bool(r["version_changed"])) for r in rows}
        if controls!={(False,False),(False,True),(True,False),(True,True)}:
            raise SystemExit(f"{tid}: incomplete Suite/Version controls: {controls}")
        actions={r["native_action"] for r in rows}
        if len(actions)!=1:
            raise SystemExit(f"{tid}: zero-control native-action disagreement: {actions}")
        if not all(r.get("match") for r in rows):
            raise SystemExit(f"{tid}: at least one native execution mismatched frozen prediction")

        reps=[r for r in rows if not r["suite_changed"] and not r["version_changed"]]
        if len(reps)!=1:
            raise SystemExit(f"{tid}: missing canonical representative")
        r=reps[0]
        out_rows.append({
            "case_id":tid,
            "family":"APT",
            "environment":"APT-3.0.3-exhaustive-controlled-native",
            "evidence_class":"CONTROLLED_NATIVE",
            "native_action":next(iter(actions)),
            "representations":build_rep(r),
            "source_execution_ids":sorted(x["id"] for x in rows),
            "negative_control_agreement":{
                "suite_version_variants":4,
                "native_actions":sorted(actions),
            },
        })

    payload={
        "schema":"apt-g6-representation-ledger-v1",
        "native_source":{
            "total_configurations":576,
            "core_semantic_templates":144,
            "zero_control_variants_per_template":4,
        },
        "rows":out_rows,
    }
    Path(args.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "rows":len(out_rows),
        "native_action_counts":{
            a:sum(r["native_action"]==a for r in out_rows)
            for a in sorted({r["native_action"] for r in out_rows})
        },
        "na_representations":sorted({
            b for r in out_rows for b,v in r["representations"].items() if v==NA
        }),
    },sort_keys=True))

if __name__=="__main__":
    main()
