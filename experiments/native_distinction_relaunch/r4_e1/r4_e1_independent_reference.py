#!/usr/bin/env python3
"""Independent reference B9-eligible finite truth table and tree proof checker.

DOES NOT IMPORT E1 frontier candidate. Defines native contract Boolean
truth separately, brute force searches all readable decision trees.
This is not a human-written native B9 benchmark or external qualification.
"""
from functools import lru_cache
from itertools import product


def native_contract_boolean_reference(program_id,world):
    if program_id=="TUF":return bool(world["old"] and world["new"])
    if program_id=="K8S_FLUX":return bool(world["team"] or world["mode"])
    if program_id=="K8S_DEFAULT":return bool(world["third"] or world["additional"])
    raise ValueError("UNKNOWN_REGISTERED_ORACLE_CONTRACT")


def enumerate_truth(s):
    fields=tuple(s["atoms"])
    unknown=[k for k in fields if s["observed"][k]=="?"]
    values=[]
    for bits in product((0,1),repeat=len(unknown)):
        world=dict(s["observed"])
        world.update(dict(zip(unknown,bits)))
        values.append((world,int(native_contract_boolean_reference(s["program_id"],world))))
    return values


def b9_exact_optimum_reference(s):
    """A full-access-equal B9 may run this exhaustive optimal decision tree."""
    records=enumerate_truth(s)
    effects={x[1] for x in records}
    if len(effects)==1:return {"status":"CERTAIN","worst":0,"total":0}
    readable=tuple(sorted(a for a in s["lawful_reads"] if s["observed"][a]=="?"))
    signature={}
    for world,effect in records:
        key=tuple(world[a] for a in readable)
        signature.setdefault(key,set()).add(effect)
    if any(len(effects)>1 for effects in signature.values()):
        return {"status":"IMPOSSIBLE","worst":None,"total":None}
    costs=s["read_costs"]
    @lru_cache(None)
    def recurse(rows,remaining):
        observed_results={records[i][1] for i in rows}
        if len(observed_results)==1:
            return (0,0)
        if not remaining:return None
        possibilities=[]
        for q in remaining:
            yes=tuple(i for i in rows if records[i][0][q]==1)
            no=tuple(i for i in rows if records[i][0][q]==0)
            rem=tuple(x for x in remaining if x!=q)
            left=recurse(no,rem)
            right=recurse(yes,rem)
            if left is None or right is None:continue
            worst=costs[q]+max(left[0],right[0])
            total=costs[q]*len(rows)+left[1]+right[1]
            possibilities.append((worst,total,q))
        if not possibilities:return None
        p=min(possibilities)
        return p[:2]
    opt=recurse(tuple(range(len(records))),readable)
    if opt is None:
        raise AssertionError("ORACLE_PLANNING_CONTRADICTION")
    return {"status":"OPTIMAL","worst":opt[0],"total":opt[1]}


def check_frontier_cert(s,candidate):
    """Independent verifier of ALL worlds, proof of lawful query cost and B9 parity."""
    rows=enumerate_truth(s)
    possible={x[1] for x in rows}
    baseline=b9_exact_optimum_reference(s)
    res=candidate["status"]
    if res in ("CERTAIN_TRUE","CERTAIN_FALSE"):
        expected_effect=1 if res=="CERTAIN_TRUE" else 0
        if possible!={expected_effect} or baseline["status"]!="CERTAIN":
            raise AssertionError("ORACLE_FALSE_EVIDENCE_CERTAINTY")
        if candidate["read_cost_worst_case"]!=0 or candidate["read_cost_over_all_finite_worlds"]!=0:
            raise AssertionError("INVALID_CERTAIN_READ_COST")
        return {"sound":True,"same_optimal_B9":True,"worlds_checked":len(rows)}
    if res=="IMPOSSIBLE_UNDER_ACTOR_ACCESS":
        if baseline["status"]!="IMPOSSIBLE":
            raise AssertionError("FALSE_IMPOSSIBILITY_CLAIM")
        pair=candidate["inaccessible_distinction_pair"]
        if not isinstance(pair,list) or len(pair)!=2:
            raise AssertionError("INCOMPLETE_INDISCERNIBILITY_PAIR")
        for world in pair:
            if world not in [x[0] for x in rows]:
                raise AssertionError("WITNESS_WORLD_NOT_IN_LAWFUL_COMPLETIONS")
        a,b=pair
        if native_contract_boolean_reference(s["program_id"],a)==native_contract_boolean_reference(s["program_id"],b):
            raise AssertionError("NO_OPPOSITE_EFFECTS")
        if any(a[k]!=b[k] for k in s["lawful_reads"]):
            raise AssertionError("WORLD_PAIR_NOT_ACCESS_INDISCERNIBLE")
        return {"sound":True,"same_optimal_B9":True,
                "worlds_checked":len(rows),"impossibility_witness_checked":True}
    if res!="GUARANTEED_RESOLVABLE" or baseline["status"]!="OPTIMAL":
        raise AssertionError("EXPECTED_FULLY_RESOLVABLE_OR_UNSUPPORTED_DISPOSITION")
    tree=candidate["adaptive_plan"]
    costs=[]
    for world,effect in rows:
        node=tree
        used=set()
        accumulated=0
        while "ask" in node:
            q=node["ask"]
            if q not in s["lawful_reads"] or q in used or s["observed"][q]!="?":
                raise AssertionError("ILLEGAL_OR_DUPLICATE_EVIDENCE_QUERY")
            if node.get("read_cost")!=s["read_costs"][q]:
                raise AssertionError("FORGED_EVIDENCE_ACQUISITION_COST")
            used.add(q)
            accumulated+=s["read_costs"][q]
            node=node["if_true"] if world[q] else node["if_false"]
        if node!={"effect":effect}:
            raise AssertionError("PLAN_MISCLASSIFIES_A_LAWFUL_SOURCE_WORLD")
        costs.append(accumulated)
    if max(costs)!=candidate["read_cost_worst_case"] or sum(costs)!=candidate["read_cost_over_all_finite_worlds"]:
        raise AssertionError("COST_DENOMINATOR_OR_CERTIFIED_PLAN_WRONG")
    if (max(costs),sum(costs))!=(baseline["worst"],baseline["total"]):
        raise AssertionError("NOT_STRONG_B9_EQUAL_INFORMATION_OPTIMAL")
    return {"sound":True,"same_optimal_B9":True,
            "worlds_checked":len(rows),
            "qualified_read_cost_worst":max(costs),
            "uniform_world_cost_sum":sum(costs)}
