#!/usr/bin/env python3
"""R1c join-only scorer of independently frozen source predictions and native outcomes.

No predictor calls, no feature construction or outcome-dependent exclusions.
"""
import argparse
import json
from collections import Counter
from pathlib import Path


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def key(row):
    return (row["from_state"], row["action"])


def unique(rows):
    out = {}
    for r in rows:
        k = key(r)
        if k in out:
            raise ValueError(f"DUPLICATE_REGISTERED_CELL: {k}")
        out[k] = r
    return out


def compare(pred, native):
    if pred["schema"] != "eeq-r1b-tuf-source-crypto-transition-v1":
        raise ValueError("wrong predictions schema")
    if native["schema"] != "eeq-r1c-tuf-native-root-grid-v1":
        raise ValueError("wrong native schema")
    assert pred["grid_cells"] == native["grid_rows"] == 56
    ps, ns = unique(pred["transitions"]), unique(native["rows"])
    required = {
        (f"trusted-root-{n}", f"submit-root-{m}")
        for n in range(1, 9) for m in range(2, 9)
    }
    if set(ps) != required or set(ns) != required:
        raise ValueError("registered grid rows missing, added or changed")
    rows = []
    for n in range(1, 9):
        for m in range(2, 9):
            cell = (f"trusted-root-{n}", f"submit-root-{m}")
            p, o = ps[cell], ns[cell]
            if p["candidate_source_sha256"] != o["candidate_source_sha256"]:
                raise ValueError("candidate source SHA mismatch: " + str(cell))
            if o["from_root_source_sha256"] != next(
                s["source_sha256"] for s in pred["states"] if s["state"] == cell[0]
            ):
                raise ValueError("trusted source SHA mismatch: " + str(cell))
            effect = p["derived_effect"]
            if o["native_action"] == "SETUP_FAILURE":
                status = "NATIVE_SETUP_FAILURE"
            elif effect == "MODEL_UNSUPPORTED":
                status = "PREDICTOR_UNSUPPORTED"
            else:
                expected_action = ("ACCEPT" if effect == "ADVANCE_TRUST_ROOT"
                                   else "REJECT")
                expected_state = p["to_state"]
                actual_state = ("trusted-root-" + str(o["after_native_version"])
                                if o["after_native_version"] is not None else None)
                status = ("MATCH" if expected_action == o["native_action"] and
                          expected_state == actual_state else "MISMATCH")
            rows.append({
                "from_state":cell[0],"action":cell[1],
                "previously_known_adjacent_development": m == n + 1,
                "frozen_predicted_effect":effect,
                "frozen_predicted_next_state":p["to_state"],
                "native_action":o["native_action"],
                "native_next_state":("trusted-root-"+str(o["after_native_version"])
                                     if o["after_native_version"] is not None else None),
                "comparison_status":status,
                "native_exception":o.get("candidate_error"),
                "native_setup_exception":o.get("setup_error"),
                "native_decision_ns":o.get("decision_ns"),
            })
    statuses = Counter(r["comparison_status"] for r in rows)
    hist = Counter(r["native_action"] for r in rows)
    legacy = [r for r in rows if r["previously_known_adjacent_development"]]
    new_cells = [r for r in rows if not r["previously_known_adjacent_development"]]
    def group(rs):
        c=Counter(x["comparison_status"] for x in rs)
        return {"total":len(rs),"statuses":dict(sorted(c.items()))}
    return {
        "schema":"eeq-r1c-tuf-native-vs-pinned-source-grid-v1",
        "status":"RESTRICTED_NATIVE_TRANSITION_CALIBRATION_NOT_R2_OR_HOLDOUT",
        "rows":rows,
        "summary":{
            "registered_total":56,
            "comparison_statuses":dict(sorted(statuses.items())),
            "native_actions":dict(sorted(hist.items())),
            "known_prior_adjacent":group(legacy),
            "other_version_proposals":group(new_cells),
            "method_native_matches":statuses.get("MATCH",0),
            "method_native_mismatches":statuses.get("MISMATCH",0),
            "method_unsupported":statuses.get("PREDICTOR_UNSUPPORTED",0),
            "native_setup_failures":statuses.get("NATIVE_SETUP_FAILURE",0),
        },
        "g5_increment":0,
        "g4_frozen":True,
        "r2_bidirectional_native_pair_proved":False,
        "b9_superiority_proved":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pred",required=True)
    p.add_argument("--native",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    output=compare(load(a.pred),load(a.native))
    Path(a.out).write_text(json.dumps(output,indent=2,sort_keys=True)+"\n",
                           encoding="utf-8")
    print(json.dumps(output["summary"],sort_keys=True))


if __name__=="__main__":
    main()
