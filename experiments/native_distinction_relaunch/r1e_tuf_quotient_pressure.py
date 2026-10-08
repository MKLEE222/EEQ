#!/usr/bin/env python3
"""Read-only nonvacuity pressure on the pinned 8x7 SOURCE-derived TUF graph.

No native verdicts are loaded; this is post-calibration exploration, NOT R2.
"""
import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path


def run(data):
    assert data["grid_cells"] == 56
    states=sorted(s["state"] for s in data["states"])
    actions=sorted(data["action_names"])
    assert len(states)==8 and len(actions)==7
    edges={(r["from_state"],r["action"]):r for r in data["transitions"]}
    assert len(edges)==56
    for s in states:
        for a in actions:
            r=edges[s,a]
            assert r["derived_effect"] in ("KEEP_TRUST_ROOT","ADVANCE_TRUST_ROOT")
            assert r["to_state"] in states

    def observation(s):
        return tuple(edges[s,a]["derived_effect"] == "ADVANCE_TRUST_ROOT"
                     for a in actions)
    obs={s:observation(s) for s in states}
    signatures={}
    rows=[]
    class_of={}
    for h in range(3):
        sig={}
        for s in states:
            sig[s]= (obs[s],) if h==0 else (
                obs[s],tuple((a,class_of[edges[s,a]["to_state"]]) for a in actions)
            )
        codes={value:i for i,value in enumerate(sorted(set(sig.values())))}
        class_of={s:codes[sig[s]] for s in states}
        groups=defaultdict(list)
        for s in states:groups[class_of[s]].append(s)
        rows.append({
            "horizon":h,"class_count":len(groups),
            "classes":[sorted(v) for k,v in sorted(groups.items())],
            "merges":len(states)-len(groups),
        })
        signatures[h]=dict(class_of)

    def trace(s,path):
        for action in path:
            s=edges[s,action]["to_state"]
        return obs[s]
    direct_signatures={s:tuple((p,trace(s,p))
        for length in range(3) for p in itertools.product(actions,repeat=length))
        for s in states}
    separable_at_zero=0
    all_pairs=0
    latent_pairs=0
    for x,y in itertools.combinations(states,2):
        all_pairs+=1
        equivalent=direct_signatures[x]==direct_signatures[y]
        assert equivalent == (signatures[2][x] == signatures[2][y]),(x,y)
        if obs[x]!=obs[y]:separable_at_zero+=1
        if obs[x]==obs[y] and not equivalent:latent_pairs+=1

    b9_matches=0
    for (state,action),r in edges.items():
        n=int(state.split("-")[-1])
        m=int(action.split("-")[-1])
        b9_predicted="ADVANCE_TRUST_ROOT" if m==n+1 else "KEEP_TRUST_ROOT"
        b9_matches+=b9_predicted==r["derived_effect"]
    return {
        "schema":"eeq-r1e-postcalibration-source-quotient-nonvacuity-v1",
        "evidence_class":"POST_NATIVE_DEVELOPMENT_SOURCE_DERIVED_DIAGNOSTIC",
        "source_only_no_native_labels":True,
        "state_count":8,"actions":7,"full_action_domain_preserved":True,
        "unrestricted_r2_claim":False,
        "refinement":rows,
        "unordered_state_pairs":all_pairs,
        "immediate_separable_pairs":separable_at_zero,
        "same_current_future_separated_pairs":latent_pairs,
        "bounded_version_only_b9_matches":b9_matches,
        "bounded_b9_total":56,
        "decision":"NO_R2_B_PAIR_IN_THIS_REGISTERED_CARRIER"
             if all(row["merges"]==0 for row in rows) else
             "NONTRIVIAL_SOURCE_QUOTIENT_OBSERVED_DEV_ONLY",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pred",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    data=json.loads(Path(a.pred).read_text(encoding="utf-8"))
    answer=run(data)
    Path(a.out).write_text(json.dumps(answer,indent=2,sort_keys=True)+"\n",
                           encoding="utf-8")
    print(json.dumps({
        "classes":[x["class_count"] for x in answer["refinement"]],
        "merges":[x["merges"] for x in answer["refinement"]],
        "pairs":answer["unordered_state_pairs"],
        "same_current_future_separated_pairs":answer["same_current_future_separated_pairs"],
        "version_only_b9_matches":answer["bounded_version_only_b9_matches"],
        "decision":answer["decision"],
    },sort_keys=True))


if __name__=="__main__":
    main()
