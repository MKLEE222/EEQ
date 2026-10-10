#!/usr/bin/env python3
"""R4-E1 EVIDENCE QUERY FRONTIER: exact finite actor-authorized minimax planner.

This program gets synthetically qualified Boolean source predicates.
It DOES NOT parse actual TUF signatures or K8s policy; MUST NOT certify
production source closure or admission ACCEPT. Fully informed B9 can copy it.
"""
from functools import lru_cache
from itertools import combinations, product
from r4_e1_registry import registered_input_check

SCIENTIFIC_CATEGORY="R4_E1_SOURCE_FREE_SYNTHETIC_DEVELOPMENT_ONLY"


def model_effect(s,world):
    # Generic formula evaluation, deliberately *not* a domain-native oracle.
    bits=[world[k] for k in s["atoms"]]
    if s["formula"]=="AND":return int(all(bits))
    if s["formula"]=="OR":return int(any(bits))
    raise ValueError("UNREGISTERED_FORMULA")


def possible_worlds(s):
    observations=s["observed"]
    unknown=[a for a in s["atoms"] if observations[a]=="?"]
    complete=[]
    for values in product((0,1),repeat=len(unknown)):
        w={a:observations[a] for a in s["atoms"]}
        w.update(dict(zip(unknown,values)))
        complete.append(w)
    return complete


def cannot_distinguish_pair(s,worlds):
    readable=set(s["lawful_reads"])
    for w1,w2 in combinations(worlds,2):
        if (model_effect(s,w1)!=model_effect(s,w2) and
            all(w1[a]==w2[a] for a in readable)):
            return [w1,w2]
    return None


def frontier(s):
    """Returns an exact plan or verified-access impossibility witness.

    Dynamic programming minimizes worst-case lawful read cost, followed by
    a sum over ALL finite consistent worlds (uniform synthetic diagnostic).
    It never uses unknown=FALSE or a caller-declared inventory closure.
    """
    if not registered_input_check(s):
        return {"case_id":s.get("case_id") if isinstance(s,dict) else None,
                "status":"MODEL_UNSUPPORTED",
                "reason":"UNREGISTERED_OR_MUTATED_SCOPED_AUTHORITY_INPUT",
                "research_class":SCIENTIFIC_CATEGORY,
                "global_k8s_admission_authorized":False}
    worlds=possible_worlds(s)
    effects={model_effect(s,w) for w in worlds}
    immutable={
        "case_id":s["case_id"],
        "program_id":s["program_id"],
        "registered_scope":s["registered_scope"],
        "registered_actor":s["registered_actor"],
        "conditional_on_external_source_qualification":True,
        "external_source_inventory_completeness_proven":False,
        "global_k8s_admission_authorized":False,
        "independent_method_advantage_over_full_B9":False,
        "native_calls":0,"original_g5_new_cases":0,
        "research_class":SCIENTIFIC_CATEGORY,
        "possible_world_count":len(worlds),
    }
    if len(effects)==1:
        effect=next(iter(effects))
        return {**immutable,
                "status":"CERTAIN_TRUE" if effect==1 else "CERTAIN_FALSE",
                "scoped_effect":s["true_effect"] if effect else s["false_effect"],
                "world_effects":[effect],
                "read_cost_worst_case":0,
                "read_cost_over_all_finite_worlds":0,
                "adaptive_plan":{"effect":effect},
                "witness_observed_atoms":{a:v for a,v in s["observed"].items()
                                           if v!="?"}}
    witness=cannot_distinguish_pair(s,worlds)
    if witness is not None:
        return {**immutable,
                "status":"IMPOSSIBLE_UNDER_ACTOR_ACCESS",
                "world_effects":[0,1],
                "inaccessible_distinction_pair":witness,
                "read_cost_worst_case":None,
                "read_cost_over_all_finite_worlds":None,
                "adaptive_plan":None,
                "refusal":"ACTOR_CANNOT_DISTINGUISH_OPPOSITE_LEGAL_CONTRACT_EFFECTS"}
    # No pair with equal lawful observations means reading ALL lawful atoms
    # guarantees deciding. Exact DP below optimizes over all lawful trees.
    observed={a:v for a,v in s["observed"].items() if v!="?"}
    readable=tuple(sorted(a for a in s["lawful_reads"] if s["observed"][a]=="?"))

    @lru_cache(None)
    def solve(fixed):
        known={**observed,**dict(fixed)}
        remaining=[w for w in worlds if all(w[a]==v for a,v in fixed)]
        outcomes={model_effect(s,w) for w in remaining}
        if len(outcomes)==1:
            effect=next(iter(outcomes))
            return (0,0,{"effect":effect})
        options=[]
        for atom in readable:
            if atom in known:
                continue
            alternatives=[]
            for value in (0,1):
                sub=tuple(sorted(fixed+((atom,value),)))
                alternative=solve(sub)
                if alternative is None:break
                alternatives.append(alternative)
            if len(alternatives)!=2:
                continue
            worst=s["read_costs"][atom]+max(z[0] for z in alternatives)
            total=s["read_costs"][atom]*len(remaining)+sum(z[1] for z in alternatives)
            options.append((worst,total,atom,
              {"ask":atom,"read_cost":s["read_costs"][atom],
               "if_false":alternatives[0][2],
               "if_true":alternatives[1][2]}))
        if not options:
            return None
        best=min(options,key=lambda z:(z[0],z[1],z[2]))
        return (best[0],best[1],best[3])

    result=solve(tuple())
    if result is None:
        raise RuntimeError("INTERNAL_FRONTIER_SOLVER_CONTRADICTS_PAIR_CERTIFICATE")
    worst,total,tree=result
    return {**immutable,
            "status":"GUARANTEED_RESOLVABLE",
            "world_effects":[0,1],
            "read_cost_worst_case":worst,
            "read_cost_over_all_finite_worlds":total,
            "read_cost_uniform_diagnostic_mean":total/len(worlds),
            "adaptive_plan":tree,
            "lawful_unobserved_atoms":list(readable),
            "guarantee_conditional_on_successful_qualified_read":True}
