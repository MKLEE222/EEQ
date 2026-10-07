#!/usr/bin/env python3
from evaluate_representations import IDS, NA, evaluate


def row(sid, label, b1, b10):
    reps = {k: NA for k in IDS}
    reps.update({"B1": {"x": b1}, "B10": {"z": b10}})
    return {"semantic_id": sid, "native_action": label, "representations": reps,
            "not_applicable_reasons": {k: "synthetic structural example" for k in IDS if k not in {"B1", "B10"}}}


rows = [row("a", "ACCEPT", 0, 0), row("b", "REJECT", 0, 1), row("c", "ACCEPT", 1, 2)]
r = {x["baseline"]: x for x in evaluate(rows, "ACCEPT", None)}
assert r["B1"]["classes"] == 2
assert r["B1"]["mixed_classes"] == 1
assert r["B1"]["mixed_cases"] == 2
assert r["B1"]["conflict_pairs"] == 1
assert abs(r["B1"]["oracle_optimal_accuracy"] - 2 / 3) < 1e-12
assert r["B1"]["zero_error_recoverable"] is False
assert r["B1"]["confusion_matrix"] == {"ACCEPT": {"ACCEPT": 2}, "REJECT": {"ACCEPT": 1}}
assert r["B10"]["mixed_classes"] == 0
assert r["B10"]["zero_error_recoverable"] is True
assert r["B10"]["oracle_optimal_accuracy"] == 1.0
try:
    evaluate(rows + [rows[0]], "ACCEPT", None)
except ValueError:
    pass
else:
    raise AssertionError("Duplicated semantic cases must be rejected")
print("ok")
