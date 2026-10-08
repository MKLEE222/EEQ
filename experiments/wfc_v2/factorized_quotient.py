#!/usr/bin/env python3
"""Post-pilot experimental factorization of lawful quotient tables.

Uses exactly the same finite-horizon observation relation as plain v2.
Interns observations; stops at a proven deterministic partition fixed point.
This is a storage/runtime research variant, NOT the frozen G4 B10 method.
"""
import json
from collections import defaultdict

from lawful_quotient import (
    SCHEMA, build_index, byte_size, canon, observable, validate_spec, _partition,
)

def partition_sets(class_ids):
    groups = defaultdict(list)
    for state_id, cls in class_ids.items():
        groups[cls].append(state_id)
    return tuple(sorted(tuple(sorted(states)) for states in groups.values()))

def compile_factorized(spec, horizon):
    validate_spec(spec)
    if type(horizon) is not int or not 0 <= horizon <= 12:
        raise ValueError("horizon must be an integer in [0,12]")

    states = build_index(spec)
    state_ids = sorted(states)
    actions = sorted(spec["actions"])
    observations = {sid:observable(spec, states[sid]) for sid in state_ids}
    obs_codes = sorted({canon(v) for v in observations.values()})
    obs_ref = {key:i for i,key in enumerate(obs_codes)}
    pool = [json.loads(s) for s in obs_codes]
    ref_for = {sid:obs_ref[canon(observations[sid])] for sid in state_ids}

    previous, classes0 = _partition(observations, state_ids)
    assignments = [previous]
    layers = [{
        "depth":0,
        "classes":[{"id":idx,"observation_ref":obs_ref[canon(obj)]}
                   for idx,obj in classes0],
    }]
    fixed_point_at = None
    stationary_classes = None

    for depth in range(1, horizon+1):
        signatures={
            sid:{
                "observation":observations[sid],
                "successors":[previous[states[sid]["transitions"][a]] for a in actions],
            }
            for sid in state_ids
        }
        current, descriptors = _partition(signatures, state_ids)
        assignments.append(current)
        layers.append({
            "depth":depth,
            "classes":[
                {
                    "id":idx,
                    "observation_ref":obs_ref[canon(desc["observation"])],
                    "successors_at_depth_minus_one":dict(zip(actions,desc["successors"])),
                }
                for idx,desc in descriptors
            ],
        })

        if partition_sets(current)==partition_sets(previous):
            # A stable deterministic Moore partition remains fixed forever.
            groups=defaultdict(list)
            for sid,cls in current.items():
                groups[cls].append(sid)
            stationary_classes=[]
            for cls in sorted(groups):
                members=groups[cls]
                successor_tuples={
                    tuple(current[states[sid]["transitions"][a]] for a in actions)
                    for sid in members
                }
                if len(successor_tuples)!=1:
                    raise AssertionError("invalid fixed-point class transition")
                obs_refs={ref_for[sid] for sid in members}
                if len(obs_refs)!=1:
                    raise AssertionError("fixed-point class merged unlike observations")
                successor=next(iter(successor_tuples))
                stationary_classes.append({
                    "id":cls,
                    "observation_ref":next(iter(obs_refs)),
                    "successors_at_same_depth":dict(zip(actions,successor)),
                })
            fixed_point_at=depth
            break
        previous=current

    final = assignments[-1]
    if fixed_point_at is None:
        table={
            "mode":"BOUNDED",
            "requested_horizon":horizon,
            "horizon":horizon,
            "observation_pool":pool,
            "actions":actions,
            "contracts":sorted(spec["contracts"],key=lambda x:x["id"]),
            "layers":layers,
        }
    else:
        table={
            "mode":"STATIONARY_FIXED_POINT",
            "requested_horizon":horizon,
            "horizon":horizon,
            "fixed_point_at":fixed_point_at,
            "observation_pool":pool,
            "actions":actions,
            "contracts":sorted(spec["contracts"],key=lambda x:x["id"]),
            "stationary_classes":stationary_classes,
        }
    state_bytes = sum(byte_size(states[sid]) for sid in state_ids)
    class_bytes = sum(byte_size(final[sid]) for sid in state_ids)
    table_bytes = byte_size(table)
    return {
        "schema":"eeq-wfc-v2-factorized-quotient-result",
        "evidence_class":"SYNTHETIC",
        "status":"COMPILED",
        "state_count":len(state_ids),
        "class_count":len(set(final.values())),
        "states_to_final_class":dict(sorted(final.items())),
        "state_to_class_by_computed_depth":[dict(sorted(x.items())) for x in assignments],
        "requested_horizon":horizon,
            "horizon":horizon,
        "effective_depth":len(assignments)-1,
        "fixed_point_at":fixed_point_at,
        "table":table,
        "cost":{
            "raw_state_bytes_total":state_bytes,
            "class_code_bytes_total":class_bytes,
            "quotient_table_bytes":table_bytes,
            "total_encoded_bytes":class_bytes+table_bytes,
            "amortized_bytes_per_state":(class_bytes+table_bytes)/len(state_ids),
            "raw_state_bytes_per_state":state_bytes/len(state_ids),
        },
        "limitations":[
            "classical_partition_refinement_not_claimed_as_new_theorem",
            "no_native_label_read",
            "fixed_point_only_for_complete_deterministic_registered_graph",
            "synthesis_requires_future_natively_grounded_action_graph",
        ],
    }

if __name__ == "__main__":
    raise SystemExit("Run frozen paired comparison tests; no native scoring CLI.")
