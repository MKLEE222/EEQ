#!/usr/bin/env python3
"""Paired plain-v2/factorized-v2 synthetic cost study after first pilot."""
import argparse
import json
import statistics
import time
from pathlib import Path

from lawful_quotient import compile_quotient, independent_equivalence_check
from factorized_quotient import compile_factorized, partition_sets
from synthetic_systems import SEED, generate_system
from run_scaling import configurations, quantile, WARMUPS, MEASUREMENTS

def cost_comparison(config):
    kwargs = {k:config[k] for k in (
        "sources","claims","actions","density","contracts","state_count")}
    spec = generate_system(seed=SEED,**kwargs)
    horizon=config["horizon"]
    plain=compile_quotient(spec,horizon)
    fast=compile_factorized(spec,horizon)
    if partition_sets(plain["states_to_final_class"]) != partition_sets(fast["states_to_final_class"]):
        raise AssertionError("factorized quotient mismatch")
    samples={"plain":[],"factorized":[]}
    functions={"plain":compile_quotient,"factorized":compile_factorized}
    for _ in range(WARMUPS):
        for name in ("plain","factorized"):
            functions[name](spec,horizon)
    for rep in range(MEASUREMENTS):
        order = ("plain","factorized") if rep % 2 == 0 else ("factorized","plain")
        for name in order:
            t0=time.perf_counter_ns()
            functions[name](spec,horizon)
            samples[name].append(time.perf_counter_ns()-t0)
    pbytes=plain["cost"]["total_encoded_bytes"]
    fbytes=fast["cost"]["total_encoded_bytes"]
    raw=plain["cost"]["raw_state_bytes_total"]
    perf={
        name:{
            "warmups":WARMUPS,
            "measurements":MEASUREMENTS,
            "median_ns":statistics.median(samples[name]),
            "iqr_ns":quantile(samples[name],.75)-quantile(samples[name],.25),
            "p95_ns":quantile(samples[name],.95),
        }
        for name in samples
    }
    return {
        "axis":config["axis"], "axis_value":config["axis_value"],
        "config":kwargs, "horizon":horizon,
        "states":plain["state_count"],"equivalence_classes":plain["class_count"],
        "quotient_relation_identical":True,
        "plain_bytes":pbytes,
        "factorized_bytes":fbytes,
        "raw_state_bytes":raw,
        "factorized_to_plain_bytes":fbytes/pbytes,
        "factorized_to_raw_bytes":fbytes/raw,
        "plain_to_raw_bytes":pbytes/raw,
        "fixed_point_at":fast["fixed_point_at"],
        "effective_depth":fast["effective_depth"],
        "factorized_table_bytes":fast["cost"]["quotient_table_bytes"],
        "factorized_code_bytes":fast["cost"]["class_code_bytes_total"],
        "performance":perf,
    }

def run():
    records=[cost_comparison(c) for c in configurations()]
    if len(records)!=15 or not all(x["quotient_relation_identical"] for x in records):
        raise AssertionError("paired cost study incomplete")
    # Independent brute-force oracle for a separate, small fixed carrier.
    small=generate_system(sources=4,claims=2,actions=2,
                          density=.4,contracts=2,state_count=16,seed=SEED)
    q=compile_factorized(small,2)
    oracle=independent_equivalence_check(small,2,q)
    if oracle["status"]!="PASS" or oracle["pairs_compared"]!=120:
        raise AssertionError(oracle)
    return {
        "schema":"eeq-wfc-v2-paired-factor-cost-study-v1",
        "evidence_class":"SYNTHETIC",
        "seed":SEED,
        "warmups":WARMUPS,
        "measurements":MEASUREMENTS,
        "comparison_design":"alternating paired execution within same runner/process",
        "original_plain_operator":"preserved in lawful_quotient.py",
        "factorized_operator":"post-first-pilot development variant",
        "G4_frozen_B10_replaced":False,
        "native_G5_effect":0,
        "independent_small_oracle":oracle,
        "workloads":records,
        "summary":{
            "rows":len(records),
            "factor_bytes_below_plain":sum(x["factorized_bytes"]<x["plain_bytes"] for x in records),
            "factor_bytes_equal_plain":sum(x["factorized_bytes"]==x["plain_bytes"] for x in records),
            "factor_bytes_above_plain":sum(x["factorized_bytes"]>x["plain_bytes"] for x in records),
            "factor_bytes_above_raw":sum(x["factorized_bytes"]>x["raw_state_bytes"] for x in records),
            "fixed_point_early":sum(x["fixed_point_at"] is not None and x["effective_depth"]<x["horizon"] for x in records),
            "median_factor_to_plain_ratio":statistics.median(x["factorized_to_plain_bytes"] for x in records),
        },
        "limitations":[
            "data intentionally contain four historical replicas per semantic bucket",
            "an exact finite action model is provided; deriving it lawfully from native source is unsolved",
            "not globally minimum-bit coding or a new automata-minimization theorem",
            "synthetic simulation cannot close native-family G8",
            "timing excludes real source-fetch/adapter precomputation",
        ],
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    res=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print(json.dumps(res["summary"],sort_keys=True))
    for rec in res["workloads"]:
        print(json.dumps({
            "axis":rec["axis"],"value":rec["axis_value"],
            "raw":rec["raw_state_bytes"],
            "plain":rec["plain_bytes"],
            "factor":rec["factorized_bytes"],
            "fixed_point":rec["fixed_point_at"],
            "plain_median_ns":int(rec["performance"]["plain"]["median_ns"]),
            "factor_median_ns":int(rec["performance"]["factorized"]["median_ns"]),
        },sort_keys=True))

if __name__=="__main__":
    main()
