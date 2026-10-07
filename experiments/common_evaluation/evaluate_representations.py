#!/usr/bin/env python3
import argparse, hashlib, json, math, statistics
from collections import Counter, defaultdict
from pathlib import Path

NA = "__NOT_APPLICABLE__"
IDS = [f"B{i}" for i in range(11)] + [f"O{i}" for i in range(1, 9)]

def canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def conflict_pairs(counts):
    labels=list(counts)
    total=0
    for i,a in enumerate(labels):
        for b in labels[i+1:]:
            total += counts[a]*counts[b]
    return total

def choose_label(counts, tie_order=None):
    m=max(counts.values())
    tied=[k for k,v in counts.items() if v==m]
    # G4 freezes lexicographic native-label tie breaking.
    return sorted(tied)[0]

def quantile(xs,q):
    if not xs: return None
    ys=sorted(xs)
    if len(ys)==1: return ys[0]
    p=(len(ys)-1)*q
    lo=math.floor(p); hi=math.ceil(p)
    if lo==hi:return ys[lo]
    return ys[lo]*(hi-p)+ys[hi]*(p-lo)

def evaluate(rows, accept_label, tie_order):
    semantic_ids=[r.get("semantic_id") for r in rows]
    if None in semantic_ids or len(semantic_ids)!=len(set(semantic_ids)):
        raise ValueError("Evaluator requires one row per unique semantic case")
    baseline_ids=IDS
    out=[]
    for bid in baseline_ids:
        applicable=[]
        na_reasons=Counter()
        for r in rows:
            if bid not in r.get("representations",{}):
                raise ValueError(f"Missing {bid} on {r['semantic_id']}")
            val=r["representations"][bid]
            if val == NA:
                reason=r.get("not_applicable_reasons",{}).get(bid)
                if not reason:
                    raise ValueError(f"Missing structural/pending reason for {bid} on {r['semantic_id']}")
                na_reasons[reason]+=1
                continue
            applicable.append((r, canon(val)))
        groups=defaultdict(list)
        for r,k in applicable: groups[k].append(r)
        mixed=0; runs_mixed=0; cp=0; correct=0; fp=0; fn=0
        bytes_list=[]; ties=0; confusion=defaultdict(Counter); mixed_hist=[]
        for k,rs in groups.items():
            c=Counter(r["native_action"] for r in rs)
            if len(c)>1:
                mixed += 1; runs_mixed += len(rs); cp += conflict_pairs(c)
                mixed_hist.append({"representation_sha256":hashlib.sha256(k.encode()).hexdigest(),
                                   "native_label_histogram":dict(sorted(c.items())),"case_count":len(rs)})
            m=max(c.values()); correct += m
            if sum(1 for v in c.values() if v==m)>1: ties += 1
            pred=choose_label(c,tie_order)
            for r in rs:
                y=r["native_action"]
                confusion[y][pred]+=1
                if pred==accept_label and y!=accept_label: fp+=1
                if pred!=accept_label and y==accept_label: fn+=1
        for r,k in applicable:
            bytes_list.append(len(k.encode("utf-8")))
        n=len(applicable)
        n_accept=sum(r["native_action"]==accept_label for r,_ in applicable)
        n_non=n-n_accept
        out.append({
            "baseline":bid,
            "status":"OK" if n else "NOT_APPLICABLE_OR_PENDING",
            "applicable_n":n,
            "not_applicable_n":len(rows)-n,
            "not_applicable_reasons":dict(sorted(na_reasons.items())),
            "classes":len(groups),
            "mixed_classes":mixed,
            "runs_in_mixed_classes":runs_mixed,
            "mixed_cases":runs_mixed,
            "zero_error_recoverable":mixed==0 if n else None,
            "mixed_class_histograms":sorted(mixed_hist,key=lambda x:x["representation_sha256"]),
            "conflict_pairs":cp,
            "oracle_optimal_accuracy": (correct/n if n else None),
            "tie_classes":ties,
            "confusion_matrix":{y:dict(sorted(cs.items())) for y,cs in sorted(confusion.items())},
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
    ap.add_argument("--tie-order", default="lexicographic", help="G4 is fixed to lexicographic; retained for old CLI compatibility")
    args=ap.parse_args()
    data=json.loads(Path(args.input).read_text())
    rows=data["rows"] if isinstance(data,dict) else data
    if args.tie_order != "lexicographic":
        raise ValueError("G4 tie order is frozen to lexicographic native-label order")
    result={}
    domains=sorted({r.get("domain", "unspecified") for r in rows})
    for domain in domains:
        result[domain]=evaluate([r for r in rows if r.get("domain", "unspecified")==domain],args.accept_label,None)
    payload={
        "input_sha256":hashlib.sha256(Path(args.input).read_bytes()).hexdigest(),
        "accept_label":args.accept_label,
        "tie_order":"lexicographic",
        "rows":len(rows),
        "domains":result,
    }
    with Path(args.out).open("w", encoding="utf-8", newline="\n") as out:
        out.write(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    for domain, metrics in result.items():
        print(f"{domain}: n={len([r for r in rows if r.get('domain','unspecified')==domain])}")
        for x in metrics:
            acc="NA" if x["oracle_optimal_accuracy"] is None else f'{x["oracle_optimal_accuracy"]:.6f}'
            print(f'  {x["baseline"]}: n={x["applicable_n"]} mixed={x["mixed_classes"]} opt_acc={acc}')

if __name__=="__main__": main()
