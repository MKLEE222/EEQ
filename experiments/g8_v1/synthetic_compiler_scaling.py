#!/usr/bin/env python3
"""Six-axis synthetic timing for FROZEN compile_wfc_v1 (not a native oracle).

Protocol: G4 section 11 axes; 5 warmups and 30 timed operations per level.
All inputs generated from fixed seed 4108 and predeclared levels.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import resource
import statistics
import time
import tracemalloc
from pathlib import Path

SEED = 4108
DEFAULT = {
    "sources": 8, "claims": 2, "actions": 2,
    "density": 0.5, "contracts": 2, "horizon": 2,
}
LEVELS = {
    "sources": [2, 4, 8, 16, 32],
    "claims": [1, 2, 4, 8],
    "actions": [1, 2, 4, 8],
    "density": [0.2, 0.5, 0.8, 1.0],
    "contracts": [1, 2, 4, 8],
    "horizon": [1, 2, 4, 8],
}


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash_fraction(*tokens):
    digest = hashlib.sha256(canon([SEED, *tokens]).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / (1 << 64)


def gen_adapter(spec):
    sources = [f"source-{i:03d}" for i in range(spec["sources"])]
    claims = [f"claim-{i:03d}" for i in range(spec["claims"])]
    actions = [f"act-{i:03d}" for i in range(spec["actions"])]
    supports = [{"id": s, "source_identity": s, "provenance": f"synthetic-{i:03d}"}
                for i, s in enumerate(sources)]
    compat = []
    binds = []
    for claim in claims:
        for source in sources:
            if hash_fraction("coverage", claim, source) < spec["density"]:
                compat.append({"claim": claim, "support": source, "compatible": True})
                binds.append({"claim": claim, "support": source,
                              "threshold_scope": "registered", "binding_known": True})
    quals = [
        {"id": "qualified", "support": s,
         "value": hash_fraction("qualification", s) < spec["density"]}
        for s in sources
    ]
    auths = [
        {"id": "authenticated", "support": s,
         "value": hash_fraction("authentication", s) < 0.90}
        for s in sources
    ]
    contracts = [
        {"id": f"contract-{i:03d}", "registered_claims": claims,
         "future_qualification_threshold": 1 + (i % max(1, spec["sources"]))}
        for i in range(spec["contracts"])
    ]
    # One deterministic registered successor-prefix per action; grow actual
    # structured transition content with horizon, not just a horizon scalar.
    transition = {
        a: [{"step": k, "source": sources[(k+i) % len(sources)],
             "evidence_event": f"event-{i}-{k}"}
            for k in range(spec["horizon"])]
        for i, a in enumerate(actions)
    }
    return {
        "schema_version": "eeq-adapter-v1",
        "validity_boundary": {"V0_lawful_information": True},
        "C1_support_coverage": {
            "claims": claims,
            "support_items": supports,
            "compatibility": compat,
        },
        "C2_qualification_fidelity": {
            "qualification_predicates": quals,
            "authentication_predicates": auths,
            "claim_binding": binds,
        },
        "C3_transition_objective_fidelity": {
            "actions": actions,
            "successor_relation": transition,
            "post_action_observations": {},
            "continuation_contract": {"registered_contracts": contracts},
            "native_action_vocabulary": ["ACCEPT", "REJECT", "REFUSE"],
        },
    }


def reference_direct(adapter):
    """Separate direct enumeration oracle for the canonical FRONTIER structure.

    This verifies structure only, not decisions/native semantics.
    """
    c1 = adapter["C1_support_coverage"]
    c2 = adapter["C2_qualification_fidelity"]
    c3 = adapter["C3_transition_objective_fidelity"]
    result = []
    for claim in sorted(c1["claims"]):
        rows = []
        for edge in c1["compatibility"]:
            if edge["claim"] != claim:
                continue
            matching = [s for s in c1["support_items"] if s["id"] == edge["support"]]
            if len(matching) != 1:
                raise AssertionError("duplicate or missing support")
            source = matching[0]
            rows.append({
                "support_id": source["id"],
                "source_identity": source.get("source_identity"),
                "provenance": source.get("provenance"),
                "compatible": bool(edge["compatible"]),
                "authentication": sorted(
                    [{k:v for k,v in x.items() if k!="support"}
                     for x in c2["authentication_predicates"]
                     if x["support"] == source["id"]], key=canon),
                "qualification": sorted(
                    [{k:v for k,v in x.items() if k!="support"}
                     for x in c2["qualification_predicates"]
                     if x["support"] == source["id"]], key=canon),
                "claim_binding": sorted(
                    [{k:v for k,v in x.items() if k not in ("claim","support")}
                     for x in c2["claim_binding"]
                     if x["claim"] == claim and x["support"] == source["id"]], key=canon),
            })
        result.append({"claim": claim, "routes": sorted(rows, key=canon)})
    return {
        "claim_frontier": result,
        "transition_frontier": {
            "actions": c3["actions"],
            "successor_relation": c3["successor_relation"],
            "post_action_observations": c3["post_action_observations"],
            "continuation_contract": c3["continuation_contract"],
            "native_action_vocabulary": c3["native_action_vocabulary"],
        },
    }


def quantile(data, ratio):
    xs = sorted(data)
    f = (len(xs)-1)*ratio
    lo = int(f)
    return xs[lo] + (xs[min(lo+1, len(xs)-1)]-xs[lo])*(f-lo)


def run_benchmark(compile_fn):
    rows = []
    for axis in LEVELS:
        for level in LEVELS[axis]:
            spec = dict(DEFAULT)
            spec[axis] = level
            start_gen = time.perf_counter_ns()
            adapter = gen_adapter(spec)
            generation_ns = time.perf_counter_ns() - start_gen
            for _ in range(5):
                compile_fn(adapter)
            times_ns = []
            result = None
            for _ in range(30):
                t0 = time.perf_counter_ns()
                result = compile_fn(adapter)
                times_ns.append(time.perf_counter_ns() - t0)
            # Sanity checks against an independently implemented structural
            # reference, including all small configurations (cheap here).
            expected = reference_direct(adapter)
            if canon(result) != canon(expected):
                raise AssertionError(f"independent structural oracle mismatch {axis}={level}")
            tracemalloc.start()
            compile_fn(adapter)
            peak_allocated_bytes = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            sizes = {
                "atoms": len(adapter["C1_support_coverage"]["support_items"]),
                "support_edges": len(adapter["C1_support_coverage"]["compatibility"]),
                "qualification_atoms": len(adapter["C2_qualification_fidelity"]["qualification_predicates"]),
                "registered_actions": len(adapter["C3_transition_objective_fidelity"]["actions"]),
                "claims": len(adapter["C1_support_coverage"]["claims"]),
                "contracts": len(adapter["C3_transition_objective_fidelity"]["continuation_contract"]["registered_contracts"]),
                "successor_steps": sum(len(v) for v in adapter["C3_transition_objective_fidelity"]["successor_relation"].values()),
            }
            rows.append({
                "axis": axis,
                "level": level,
                "parameters": spec,
                "model_counts": sizes,
                "generation_preprocess_ns": generation_ns,
                "warmups": 5,
                "measured_operations": 30,
                "compile_median_ns": statistics.median(times_ns),
                "compile_iqr_ns": quantile(times_ns, 0.75) - quantile(times_ns, 0.25),
                "compile_p95_ns": quantile(times_ns, 0.95),
                "output_serialized_bytes": len(canon(result).encode("utf-8")),
                "input_serialized_bytes": len(canon(adapter).encode("utf-8")),
                "tracemalloc_peak_bytes": peak_allocated_bytes,
                "process_peak_rss_kib_so_far": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "reference_compiler_exact_match": True,
                "native_decision_oracle_provided": False,
            })
            print(json.dumps({
                "axis": axis, "level": level,
                "median_ns": rows[-1]["compile_median_ns"],
                "input_bytes": rows[-1]["input_serialized_bytes"],
                "output_bytes": rows[-1]["output_serialized_bytes"],
            }, sort_keys=True), flush=True)
    return {
        "schema": "eeq-g8-v1-frozen-compiler-synthetic-scaling",
        "seed": SEED,
        "frozen_levels": LEVELS,
        "frozen_defaults": DEFAULT,
        "evidence_class": "SYNTHETIC",
        "is_g8_complete": False,
        "does_not_count_g5_or_natively_validate_actions": True,
        "notes": [
            "Independent oracle checks canonical frontier construction, not native decision fidelity.",
            "Process peak RSS is a cumulative Linux process high-water mark, not a per-row isolated allocation.",
            "Source acquisition time is zero for local generated synthetic inputs and is excluded from compilation.",
            "Horizon is represented by actual transition-prefix content rather than a scalar only.",
        ],
        "rows": rows,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen-compiler", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location("frozen_wfc_v1", args.frozen_compiler)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = run_benchmark(module.compile_wfc)
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True)+"\n",
                              encoding="utf-8")


if __name__ == "__main__":
    main()
