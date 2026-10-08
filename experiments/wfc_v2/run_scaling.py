#!/usr/bin/env python3
"""Frozen six-axis v2 synthetic scaling and downstream experiment.

Reports performance without conflating deterministic logical repetitions
with native semantic cases. All 15 configurations vary one axis at a time.
"""
import argparse
import json
import math
import resource
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path

from lawful_quotient import (
    canon, compile_quotient, independent_equivalence_check,
    legal_next_actions, correction_words, observable, quotient_downstream_check,
)
from synthetic_systems import SEED, generate_system, toy_system

BASE = {
    "sources": 8, "claims": 3, "actions": 3, "density": .40,
    "contracts": 2, "state_count": 64, "horizon": 2,
}
AXES = {
    "sources": [4, 8, 12, 20],
    "claims": [1, 3, 6],
    "actions": [1, 3, 6],
    "density": [.15, .40, .80],
    "contracts": [1, 2, 4],
    "horizon": [0, 1, 2, 4],
}
WARMUPS = 5
MEASUREMENTS = 30

def quantile(values, fraction):
    xs = sorted(values)
    z = (len(xs) - 1) * fraction
    lo = math.floor(z); hi = math.ceil(z)
    return xs[lo] if lo == hi else xs[lo] * (hi-z) + xs[hi] * (z-lo)

def configurations():
    rows = [{"axis": "baseline", "axis_value": None, **BASE}]
    for axis, values in AXES.items():
        for value in values:
            if value == BASE[axis]:
                continue
            values_copy = dict(BASE)
            values_copy[axis] = value
            rows.append({"axis": axis, "axis_value": value, **values_copy})
    assert len(rows) == 15, len(rows)
    return rows

def benchmark(config):
    opts = {k: config[k] for k in ("sources","claims","actions",
                                   "density","contracts","state_count")}
    t0 = time.perf_counter_ns()
    spec = generate_system(seed=SEED, **opts)
    generate_ns = time.perf_counter_ns() - t0
    horizon = config["horizon"]
    for _ in range(WARMUPS):
        compile_quotient(spec, horizon)
    samples=[]
    for _ in range(MEASUREMENTS):
        start=time.perf_counter_ns()
        out=compile_quotient(spec, horizon)
        samples.append(time.perf_counter_ns()-start)
    stats=out["cost"]
    return {
        "axis":config["axis"],
        "axis_value":config["axis_value"],
        "spec_parameters":opts,
        "horizon":horizon,
        "states":out["state_count"],
        "classes":out["class_count"],
        "classes_by_depth":out["class_count_by_depth"],
        "sources":config["sources"],
        "claims":config["claims"],
        "actions":config["actions"],
        "contracts":config["contracts"],
        "support_density":config["density"],
        "support_binding_edges":sum(len(x["claims"]) for x in spec["sources"]),
        "oracle_status":"NOT_RUN_ON_THIS_SCALING_INSTANCE",
        "generation_wall_ns":generate_ns,
        "compilation_wall_ns":{
            "warmups":WARMUPS,
            "measurements":MEASUREMENTS,
            "median":statistics.median(samples),
            "iqr":quantile(samples,.75)-quantile(samples,.25),
            "p95":quantile(samples,.95),
        },
        "cost":stats,
        "process_peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "rss_scope":"entire Python process high-water mark, not isolated compile RSS",
        "source_fetch_ns":None,
        "source_fetch_scope":"NO_FETCH_SYNTHETIC_IN_PROCESS_GENERATION",
    }

def downstream():
    spec=toy_system()
    q=compile_quotient(spec,2)
    by_current=defaultdict(Counter)
    ids=sorted(x["id"] for x in spec["states"])
    for sid in ids:
        state=next(x for x in spec["states"] if x["id"]==sid)
        key=canon(observable(spec,state))
        legal=tuple(legal_next_actions(spec,sid,"continuation","release"))
        by_current[key][legal]+=1
    correct_current=sum(max(cnt.values()) for cnt in by_current.values())
    oracle_check=independent_equivalence_check(spec,2,q)
    future_check=quotient_downstream_check(spec,q,"continuation","release")
    if oracle_check["status"]!="PASS" or future_check["status"]!="PASS":
        raise AssertionError("downstream quotient failed independent oracle")
    return {
        "role":"SYNTHETIC_CONSTRUCTIVE_MECHANISM_TEST_NOT_NATIVE",
        "states":len(ids),
        "registered_actions":spec["actions"],
        "horizon":2,
        "current_only_legal_action_set_accuracy":correct_current/len(ids),
        "quotient_legal_action_set_accuracy":1.0,
        "current_only_correct_states_oracle_optimal":correct_current,
        "quotient_correct_states":len(ids),
        "exact_legal_actions_examples":{
            sid:legal_next_actions(spec,sid,"continuation","release")
            for sid in ("s0","s2","s3","s5")
        },
        "denied_state_correction_words":{
            sid:correction_words(spec,sid,"continuation","release",2)
            for sid in ("s3","s6")
        },
        "independent_exhaustive_oracle":oracle_check,
        "quotient_downstream_check":future_check,
    }

def run():
    # Independent exhaustive small carrier, not spot-checking the compiler.
    small=generate_system(sources=4,claims=2,actions=2,density=.4,
                          contracts=2,state_count=16,seed=SEED)
    small_q=compile_quotient(small,2)
    independent=independent_equivalence_check(small,2,small_q)
    if independent["status"]!="PASS" or independent["pairs_compared"] != 120:
        raise AssertionError(independent)

    records=[benchmark(c) for c in configurations()]
    return {
        "schema":"eeq-wfc-v2-synthetic-scaling-v1",
        "evidence_class":"SYNTHETIC",
        "seed":SEED,
        "protocol_g4_unchanged":True,
        "core_b10_v1_unchanged":True,
        "native_g5_case_effect":0,
        "synthetic_scaling_rows":len(records),
        "axis_isolation":"one parameter at a time relative to BASE",
        "base_parameters":BASE,
        "axes":AXES,
        "independent_small_oracle":independent,
        "downstream":downstream(),
        "benchmarks":records,
        "limitations":[
            "synthetic state transition graphs do not substitute for native-family robustness",
            "controlled fourfold factual clones make compression opportunities explicit",
            "partition refinement is a classical algorithm, not standalone novelty",
            "shared quotient table and class-code bytes both included in cost",
            "native compiler/adapter/source-fetch timing has not been measured",
            "not a replacement for frozen G4 B10 or old holdout results",
        ],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "rows":result["synthetic_scaling_rows"],
        "independent_pairs":result["independent_small_oracle"]["pairs_compared"],
        "downstream":result["downstream"]["quotient_downstream_check"]["status"],
        "median_compile_ns":[
            int(x["compilation_wall_ns"]["median"]) for x in result["benchmarks"]
        ],
    },sort_keys=True))

if __name__ == "__main__":
    main()
