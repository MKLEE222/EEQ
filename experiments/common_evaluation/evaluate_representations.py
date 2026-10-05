#!/usr/bin/env python3
import argparse, json, math, statistics
from collections import Counter, defaultdict
from pathlib import Path

NA = "__NOT_APPLICABLE__"

def canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def conflict_pairs(counts):
    labels=list(counts)
    total=0
    for i,a in enumerate(labels):
        for b in labels[i+1:]:
            total += counts[a]*counts[b]
    return total

def choose_label(counts, tie_order):
    m=max(counts.values())
    tied=[k for k,v in counts.items() if v==m]
    rank={x:i for i,x in enumerate(tie_order)}
    return sorted(tied, key=lambda x:(rank.get(x,10**9), x))[0]

def quantile(xs,q):
    if not xs: return None
    ys=sorted(xs)
    if len(ys)==1: return ys[0]
    p=(len(ys)-1)*q
    lo=math.floor(p); hi=math.ceil(p)
    if lo==hi:return ys[lo]
    return ys[lo]*(hi-p)+ys[hi]*(p-lo)

def evaluate(rows, accept_label, tie_order):
    baseline_ids=sorted({b for r in rows for b in r.get("representations",{})})
    out=[]
    for bid in baseline_ids:
        applicable=[]
        for r in rows:
            if bid not in r.get("representations",{}):
                continue
            val=r["representations"][bid]
            if val == NA:
                continue
            applicable.append((r, canon(val)))
        groups=defaultdict(list)
        for r,k in applicable: groups[k].append(r)
        mixed=0; runs_mixed=0; cp=0; correct=0; fp=0; fn=0
        bytes_list=[]; ties=0
        for k,rs in groups.items():
            c=Counter(r["native_action"] for r in rs)
            if len(c)>1:
                mixed += 1; runs_mixed += len(rs); cp += conflict_pairs(c)
            m=max(c.values()); correct += m
            if sum(1 for v in c.values() if v==m)>1: ties += 1
            pred=choose_label(c,tie_order)
            for r in rs:
                y=r["native_action"]
                if pred==accept_label and y!=accept_label: fp+=1
                if pred!=accept_label and y==accept_label: fn+=1
        for r,k in applicable:
            bytes_list.append(len(k.encode("utf-8")))
        n=len(applicable)
        n_accept=sum(r["native_action"]==accept_label for r,_ in applicable)
        n_non=n-n_accept
        out.append({
            "baseline":bid,
            "applicable_n":n,
            "classes":len(groups),
            "mixed_classes":mixed,
            "runs_in_mixed_classes":runs_mixed,
            "conflict_pairs":cp,
            "oracle_optimal_accuracy": (correct/n if n else None),
            "tie_classes":ties,
            "false_accepts":fp,
            "false_rejects":fn,
            "false_accept_rate": (fp/n_non if n_non else 0.0),
            "false_reject_rate": (fn/n_accept if n_accept else 0.0),
            "serialized_bytes_mean": (statistics.mean(bytes_list) if bytes_list else None),
            "serialized_bytes_median": (statistics.median(bytes_list) if bytes_list else None),
            "serialized_bytes_p95": quantile(bytes_list,0.95),
            "serialized_bytes_max": (max(bytes_list) if bytes_list else None),
        })
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--out", required=True)
    ap.add_argument("--accept-label", default="ACCEPT")
    ap.add_argument("--tie-order", default="REJECT_AUTH,BLOCK_CONFIRM,REJECT,BLOCK,ACCEPT")
    args=ap.parse_args()
    data=json.loads(Path(args.input).read_text())
    rows=data["rows"] if isinstance(data,dict) else data
    tie=[x for x in args.tie_order.split(",") if x]
    result=evaluate(rows,args.accept_label,tie)
    payload={
        "input":str(args.input),
        "accept_label":args.accept_label,
        "tie_order":tie,
        "rows":len(rows),
        "baselines":result,
    }
    Path(args.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    for x in result:
        acc="NA" if x["oracle_optimal_accuracy"] is None else f'{x["oracle_optimal_accuracy"]:.6f}'
        print(f'{x["baseline"]}: n={x["applicable_n"]} classes={x["classes"]} mixed={x["mixed_classes"]} conflict_pairs={x["conflict_pairs"]} opt_acc={acc}')

if __name__=="__main__": main()
