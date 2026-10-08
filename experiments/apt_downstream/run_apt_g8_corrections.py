#!/usr/bin/env python3
"""G8 APT native-grid legal-action and correction-path recovery.

Development post-native analysis. Uses only frozen APT outcomes as an
independent finite successor oracle; G6 representations are never rebuilt.
"""
import argparse
import json
import statistics
from collections import Counter, defaultdict, deque
from pathlib import Path

FIELDS=("Origin","Label","Codename")
EDIT_ACTIONS={
    "ADD_ALLOW_ORIGIN":"Origin",
    "ADD_ALLOW_LABEL":"Label",
    "ADD_ALLOW_CODENAME":"Codename",
}
GLOBAL="SET_ALLOW_GLOBAL"
IDS=[f"B{i}" for i in range(11)]+[f"O{i}" for i in range(1,9)]
NA="__NOT_APPLICABLE__"

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def key(qualified,changed,allow_global,allow_fields):
    if any(f not in FIELDS for f in allow_fields):
        raise ValueError("unknown allow field")
    return (
        bool(qualified),
        tuple(bool(changed[f]) for f in FIELDS),
        bool(allow_global),
        tuple(sorted(allow_fields)),
    )

def key_native(r):
    return key(r["qualified"],r["protected_changed"],
               r["allow_global"],r["allow_fields"])

def key_rep(r):
    b9=r["representations"]["B9"]
    return key(b9["qualified"],b9["protected_changed"],
               b9["allow_global"],b9["allow_fields"])

def build_native_grid(aggregate):
    rows=aggregate["rows"]
    if len(rows)!=576:
        raise ValueError("unexpected APT frozen execution count")
    templates=defaultdict(list)
    for r in rows:
        templates[r["semantic_template_id"]].append(r)
    if len(templates)!=144:
        raise ValueError("unexpected semantic APT count")
    grid={}
    for template,records in templates.items():
        if len(records)!=4:
            raise ValueError("Suite/Version control multiplicity changed")
        variants={(bool(r["suite_changed"]),bool(r["version_changed"])) for r in records}
        if variants!={(False,False),(False,True),(True,False),(True,True)}:
            raise ValueError("missing frozen zero-control variant")
        observed={r["native_action"] for r in records}
        if len(observed)!=1:
            raise ValueError("Suite/Version zero-control native mismatch")
        unmodified=next(r for r in records
                        if not r["suite_changed"] and not r["version_changed"])
        sig=key_native(unmodified)
        if sig in grid:
            raise ValueError("duplicate APT semantic signature")
        grid[sig]=unmodified
    if len(grid)!=144:
        raise ValueError("wrong canonical APT grid")
    groups=Counter((k[0],k[1]) for k in grid)
    if len(groups)!=16 or set(groups.values())!={9}:
        raise ValueError("APT grid lacks nine allowance states per source state")
    return grid

def available_actions(k):
    _,_,global_allowed,allowed=k
    if global_allowed:
        return {}
    offered={}
    existing=set(allowed)
    for action,field in sorted(EDIT_ACTIONS.items()):
        if field not in existing:
            offered[action]=key(k[0],dict(zip(FIELDS,k[1])),False,existing|{field})
    offered[GLOBAL]=key(k[0],dict(zip(FIELDS,k[1])),True,[])
    return offered

def successors(k,grid):
    edges=available_actions(k)
    for act,successor in edges.items():
        if successor not in grid:
            raise ValueError("invented successor case: "+str((k,act)))
    return edges

def safe_next_actions(k,grid):
    return sorted(a for a,n in successors(k,grid).items()
                  if grid[n]["native_action"]=="ACCEPT")

def shortest_corrections(k,grid,max_depth=3,field_only=False):
    if grid[k]["native_action"]=="ACCEPT":
        return [[]]
    frontier=[(k,())]
    for depth in range(1,max_depth+1):
        next_layer=[]
        accepted=[]
        for state,history in frontier:
            for act,nxt in sorted(successors(state,grid).items()):
                if field_only and act==GLOBAL:
                    continue
                new=history+(act,)
                if grid[nxt]["native_action"]=="ACCEPT":
                    accepted.append(new)
                else:
                    next_layer.append((nxt,new))
        if accepted:
            if field_only:
                return sorted({tuple(sorted(EDIT_ACTIONS[a] for a in p))
                               for p in accepted})
            return [list(p) for p in sorted(set(accepted))]
        frontier=next_layer
    return []

def task_label(k,grid,task):
    if task=="safe_next":
        return safe_next_actions(k,grid)
    if task=="shortest":
        return shortest_corrections(k,grid,3,False)
    if task=="least_privilege":
        return [list(x) for x in shortest_corrections(k,grid,3,True)]
    raise ValueError("unknown task")

def oracle_optimal(rows,task,baseline):
    applicability=[]
    na_reasons=Counter()
    for r in rows:
        rep=r["representations"][baseline]
        if rep==NA:
            reason=r.get("not_applicable_reasons",{}).get(baseline)
            if not reason: raise ValueError("missing N/A reason")
            na_reasons[reason]+=1
        else:
            applicability.append((r,canon(rep)))
    grouping=defaultdict(list)
    for row,representation in applicability:
        grouping[representation].append(row)
    mixed=0; conflicts=0; accurate=0
    mixed_hist=[]
    for repr_string,members in grouping.items():
        counts=Counter(canon(row["downstream_tasks"][task]) for row in members)
        accurate+=max(counts.values())
        if len(counts)>1:
            mixed+=1
            hist=list(counts.values())
            conflicts+=sum(hist[i]*hist[j]
                           for i in range(len(hist)) for j in range(i+1,len(hist)))
            mixed_hist.append({
                "representation_fingerprint":__import__("hashlib").sha256(
                    repr_string.encode()).hexdigest(),
                "task_output_histogram":dict(sorted(counts.items())),
            })
    n=len(applicability)
    bytes_count=[len(rep.encode("utf-8")) for _,rep in applicability]
    return {
        "baseline":baseline,
        "applicable_n":n,
        "structurally_not_applicable_n":len(rows)-n,
        "structural_na_reasons":dict(sorted(na_reasons.items())),
        "equivalence_classes":len(grouping),
        "mixed_output_classes":mixed,
        "conflict_pairs":conflicts,
        "exact_output_recoverable":mixed==0 if n else None,
        "oracle_optimal_exact_output_accuracy":accurate/n if n else None,
        "serialized_bytes_mean":statistics.mean(bytes_count) if n else None,
        "mixed_histograms":mixed_hist,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--apt-aggregate",type=Path,required=True)
    p.add_argument("--g6-representations",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    native=json.loads(args.apt_aggregate.read_text())
    reps=json.loads(args.g6_representations.read_text())
    grid=build_native_grid(native)
    rs=[r for r in reps["rows"] if r["domain"]=="APT:releaseinfo"]
    if len(rs)!=144:
        raise ValueError("APT G6 representation count is not 144")
    seen=set()
    rows=[]
    for item in rs:
        sig=key_rep(item)
        if sig in seen: raise ValueError("duplicate joined APT representation state")
        seen.add(sig)
        if sig not in grid: raise ValueError("representation state missing from native source grid")
        if item["native_action"]!=grid[sig]["native_action"]:
            raise ValueError("native outcome mismatch between pinned artifacts")
        if set(item["representations"])!=set(IDS):
            raise ValueError("all 19 frozen ID representations required")
        tasks={t:task_label(sig,grid,t) for t in
               ("safe_next","shortest","least_privilege")}
        rows.append({
            "semantic_id":item["semantic_id"],
            "native_action":item["native_action"],
            "representations":item["representations"],
            "not_applicable_reasons":item.get("not_applicable_reasons",{}),
            "downstream_tasks":tasks,
        })
    if set(grid)!=seen:
        raise ValueError("APT G6-native join did not exhaust all canonical cases")
    result={}
    for task in ("safe_next","shortest","least_privilege"):
        result[task]=[oracle_optimal(rows,task,bid) for bid in IDS]
    hist=Counter(row["native_action"] for row in rows)
    tasks_by_case={r["semantic_id"]:r["downstream_tasks"] for r in rows}
    payload={
        "schema":"eeq-apt-g8-native-downstream-action-recovery-v1",
        "evidence_class":"CONTROLLED_NATIVE",
        "role":"retrospective post-native frozen finite counterfactual graph",
        "native_executions":576,
        "native_semantic_cases":144,
        "source_state_groups":16,
        "allowance_profiles_per_group":9,
        "native_histogram":dict(sorted(hist.items())),
        "registered_contract_actions":sorted(EDIT_ACTIONS)+[GLOBAL],
        "horizon_max_edits":3,
        "tasks":result,
        "all_semantic_outputs":tasks_by_case,
        "native_label_used_to_construct_representation":False,
        "native_label_used_only_as_frozen_successor_oracle":True,
        "g5_count_effect":0,
        "original_g4_scoring_changed":False,
        "b10_v1_changed":False,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    compact={
        t:{x["baseline"]:{
            "accuracy":x["oracle_optimal_exact_output_accuracy"],
            "mixed":x["mixed_output_classes"],
            "conflict_pairs":x["conflict_pairs"]
        } for x in rows if x["baseline"] in {"B0","B1","B8","B9","B10"}}
        for t,rows in result.items()
    }
    print(json.dumps({
        "case_count":len(rows),
        "histogram":dict(hist),
        "task_compact":compact
    },sort_keys=True))

if __name__=="__main__":
    main()
