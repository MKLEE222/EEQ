#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
from pathlib import Path

def first(root, name):
    xs = sorted(Path(root).rglob(name))
    if len(xs) != 1:
        raise SystemExit(f"expected exactly one {name} under {root}, found {len(xs)}: {xs}")
    return xs[0]

def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def digest_signature(parts):
    return hashlib.sha256(canon(parts).encode("utf-8")).hexdigest()

def audit_apt(root):
    p = first(root, "APT_EXHAUSTIVE_RESULTS.json")
    d = json.loads(p.read_text())
    assert d["total"] == 576, d
    assert d["matched"] == 576, d
    assert d["mismatches"] == 0, d
    assert d["reject_other"] == 0, d
    rows = d["rows"]
    template_ids = {r["semantic_template_id"] for r in rows}
    controls = {(bool(r["suite_changed"]), bool(r["version_changed"])) for r in rows}
    assert len(template_ids) == 144, len(template_ids)
    assert len(controls) == 4, controls
    signatures = {
        digest_signature({
            "family": "APT",
            "semantic_template_id": tid,
        })
        for tid in template_ids
    }
    return {
        "family": "APT",
        "native_configurations": 576,
        "semantic_cases": len(signatures),
        "zero_control_variants_per_template": 4,
        "signatures": sorted(signatures),
        "source_file": str(p),
    }

def read_k8s_base(root):
    summary = json.loads(first(root, "summary.json").read_text())
    assert summary["eligible_rows"] == 24, summary
    assert summary["passes"] == 24, summary
    assert summary["mismatches"] == 0, summary
    assert summary["ambiguous_eligible_rows"] == 0, summary
    assert summary["preexcluded_native_schema_invalid"] == 6, summary

    tsv = first(root, "grid_results.tsv")
    rows = []
    with tsv.open(newline="") as fh:
        rd = csv.DictReader(fh, delimiter="\t")
        for r in rd:
            if r["status"] == "PREEXCLUDED":
                continue
            assert r["status"] == "PASS", r
            assert r["observed"] == r["expected"], r
            params = json.loads(r["params"])
            rows.append({
                "family": r["family"],
                "params": params,
                "native_action": r["observed"],
            })
    assert len(rows) == 24, len(rows)
    sig = {
        digest_signature({
            "family": "KUBERNETES",
            "environment": r["family"],
            "params": r["params"],
        }): r["native_action"]
        for r in rows
    }
    assert len(sig) == 24, len(sig)
    return sig

def audit_k8s_base(root_a, root_b):
    a = read_k8s_base(root_a)
    b = read_k8s_base(root_b)
    assert a == b, "Kubernetes base semantic grid differs across native versions"
    return {
        "family": "Kubernetes-Flux-GCSFuse",
        "semantic_cases": len(a),
        "native_version_executions": 2 * len(a),
        "version_repetitions_counted_as_new_cases": False,
        "signatures": sorted(a),
        "labels_by_signature": a,
    }

def read_volcano(root):
    summary = json.loads(first(root, "summary.json").read_text())
    assert summary["frozen_rows"] == 72, summary
    assert summary["eligible_rows"] == 72, summary
    assert summary["passes"] == 72, summary
    assert summary["mismatches"] == 0, summary
    assert summary["ambiguous_eligible_rows"] == 0, summary
    rows = json.loads(first(root, "grid_results.json").read_text())
    assert len(rows) == 72, len(rows)
    sig = {}
    for r in rows:
        assert r["status"] == "PASS", r
        assert r["observed"] == r["expected"], r
        s = digest_signature({
            "family": "KUBERNETES",
            "environment": "volcano",
            "scheduler": r["scheduler"],
            "min": r["min"],
            "max": r["max"],
        })
        if s in sig:
            raise AssertionError(f"duplicate Volcano semantic signature {s}")
        sig[s] = r["observed"]
    return sig

def audit_volcano(root_a, root_b):
    a = read_volcano(root_a)
    b = read_volcano(root_b)
    assert a == b, "Volcano semantic grid differs across native versions"
    return {
        "family": "Kubernetes-Volcano",
        "semantic_cases": len(a),
        "native_version_executions": 2 * len(a),
        "version_repetitions_counted_as_new_cases": False,
        "signatures": sorted(a),
        "labels_by_signature": a,
    }

def audit_bottlerocket(root):
    p = first(root, "BOTTLE_ROCKET_NATIVE_ROOT_CHAIN.json")
    d = json.loads(p.read_text())
    s = d["summary"]
    assert s["transitions"] == 7, s
    assert s["accepted"] == 7, s
    assert s["rejected"] == 0, s
    assert s["final_trusted_root_version"] == 8, s
    assert s["complete"] is True, s
    signatures = {}
    for r in d["rows"]:
        assert r["native_action"] == "ACCEPT", r
        sig = digest_signature({
            "family": "TUF",
            "environment": r["environment"],
            "action": r["action"],
            "from_version": r["from_version"],
            "to_version": r["to_version"],
            "future_contract": r["future_contract"],
        })
        if sig in signatures:
            raise AssertionError(f"duplicate Bottlerocket semantic signature {sig}")
        signatures[sig] = r["native_action"]
    assert len(signatures) == 7, len(signatures)
    return {
        "family": "TUF-Bottlerocket",
        "semantic_cases": len(signatures),
        "signatures": sorted(signatures),
        "labels_by_signature": signatures,
        "source_file": str(p),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apt", required=True)
    ap.add_argument("--k8s-134", required=True)
    ap.add_argument("--k8s-135", required=True)
    ap.add_argument("--volcano-134", required=True)
    ap.add_argument("--volcano-135", required=True)
    ap.add_argument("--bottlerocket", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    parts = [
        audit_apt(args.apt),
        audit_k8s_base(args.k8s_134, args.k8s_135),
        audit_volcano(args.volcano_134, args.volcano_135),
        audit_bottlerocket(args.bottlerocket),
    ]

    all_sigs = []
    for part in parts:
        all_sigs.extend((part["family"], s) for s in part["signatures"])
    if len(all_sigs) != len(set(all_sigs)):
        raise SystemExit("cross-component semantic signature collision")

    total = sum(p["semantic_cases"] for p in parts)
    target = 250
    payload = {
        "schema": "eeq-g5-semantic-dedup-audit-v1",
        "counting_rule": "Count frozen semantic cases; do not count version repetitions or preregistered zero-control multiplicity as new core cases.",
        "components": [{k:v for k,v in p.items() if k not in ("signatures","labels_by_signature")} for p in parts],
        "semantic_cases_total": total,
        "g5_target": target,
        "g5_status": "PASS" if total >= target else "OPEN",
        "remaining_to_target": max(0, target-total),
        "notes": [
            "APT 576 native configurations collapse to 144 frozen core semantic templates.",
            "Kubernetes v1.34.3 and v1.35.0 are robustness repetitions and are counted once per semantic case.",
            "Bottlerocket currently contributes only the seven newly reconstructed adjacent production-root transitions; no legacy 24-row task ledger is inferred from aggregate paper numbers.",
            "GitHub governance cases are intentionally absent until its adapter is frozen and machine-deduplicated.",
        ],
    }
    Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if total >= target:
        print("G5_COUNT_THRESHOLD_REACHED")
    else:
        print(f"G5_OPEN_NEEDS_{target-total}_MORE_DEDUPED_SEMANTIC_CASES")

if __name__ == "__main__":
    main()
