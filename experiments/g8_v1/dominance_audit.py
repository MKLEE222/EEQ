#!/usr/bin/env python3
"""Read-only G8-v1 sample-specific information-gain and dominance audit.

Does not change or rescore B0-B10/O1-O8. No native labels are consumed here;
only frozen aggregate matrix metrics are inspected.
"""
import argparse
import json
from pathlib import Path

EPS = 1e-12
B0_B10 = [f"B{i}" for i in range(11)]
OMISSIONS = [f"O{i}" for i in range(1, 9)]
IDS = set(B0_B10 + OMISSIONS)


def audit_matrix(path, source, expected_domains):
    matrix = json.loads(Path(path).read_text(encoding="utf-8"))
    records = {}
    if set(matrix["domains"]) != set(expected_domains):
        raise ValueError(f"unaccounted domains for {source}: {list(matrix['domains'])}")
    for domain, n in expected_domains.items():
        rows = matrix["domains"][domain]
        by = {r["baseline"]: r for r in rows}
        if set(by) != IDS or len(rows) != 19:
            raise ValueError("baseline/omission set differs from frozen G4: " + domain)
        target = by["B10"]
        if target["applicable_n"] != n:
            raise ValueError("B10 missing native cases: " + domain)
        comparison = []
        omission_no_loss = []
        omission_losses = []
        for baseline in B0_B10[:-1] + OMISSIONS:
            b = by[baseline]
            if b["applicable_n"] != n:
                continue
            if b["serialized_bytes_mean"] is None:
                continue
            gain = float(target["oracle_optimal_accuracy"]) - float(b["oracle_optimal_accuracy"])
            if baseline.startswith("O"):
                if gain > EPS or b["mixed_classes"] > target["mixed_classes"]:
                    omission_losses.append(baseline)
                else:
                    omission_no_loss.append(baseline)
            if b["oracle_optimal_accuracy"] + EPS >= target["oracle_optimal_accuracy"] and \
               b["serialized_bytes_mean"] <= target["serialized_bytes_mean"] + EPS:
                comparison.append({
                    "baseline": baseline,
                    "accuracy": b["oracle_optimal_accuracy"],
                    "classes": b["classes"],
                    "serialized_bytes_mean": b["serialized_bytes_mean"],
                })
        b0 = by["B0"]
        ratio = (target["serialized_bytes_mean"] / b0["serialized_bytes_mean"]
                 if b0["applicable_n"] == n and b0["serialized_bytes_mean"] > 0 else None)
        records[domain] = {
            "semantic_cases": n,
            "b10_classes": target["classes"],
            "b10_injective": target["classes"] == n,
            "b10_mixed_classes": target["mixed_classes"],
            "b10_accuracy": target["oracle_optimal_accuracy"],
            "b10_bytes": target["serialized_bytes_mean"],
            "b0_bytes": b0["serialized_bytes_mean"] if b0["applicable_n"] == n else None,
            "b10_to_b0_bytes_ratio": ratio,
            "sample_dominating_representations": comparison,
            "applicable_omission_no_observed_loss": omission_no_loss,
            "applicable_omission_observed_loss": omission_losses,
            "non_diagnostic_all_applicable_omissions": (
                not omission_losses and bool(omission_no_loss)
            ),
        }
    return {"source": source, "domains": records}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6-285", required=True)
    ap.add_argument("--github-v2", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    fixed = [
        audit_matrix(args.g6_285, "frozen-285-g6", {
            "APT:releaseinfo": 144,
            "K8s:5spot-vap": 38,
            "K8s:flux-vap": 10,
            "K8s:gcsfuse-vap": 14,
            "K8s:volcano-vap": 72,
            "TUF:bottlerocket-root": 7,
        }),
        audit_matrix(args.github_v2, "github-v2-g6", {
            "GitHub:v2-governance": 9,
        }),
    ]
    report = {
        "schema": "eeq-g8-v1-frozen-information-pressure-audit",
        "status": "READ_ONLY_DIAGNOSTIC_NOT_G8_PASS",
        "inputs": ["G6_FINAL_285_MATRIX.json", "GITHUB_V2_G6_MATRIX.json"],
        "matrices": fixed,
        "limitation": "Dominance is observed on the SAME evaluated sample; it does not establish a universal algorithmic lower bound.",
    }
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")
    for group in fixed:
        print(json.dumps({
            "source": group["source"],
            "domains": {k: {
                "injective": v["b10_injective"],
                "b10_over_b0_bytes": v["b10_to_b0_bytes_ratio"],
                "dominators": [x["baseline"] for x in v["sample_dominating_representations"]],
                "omission_losses": v["applicable_omission_observed_loss"],
            } for k, v in group["domains"].items()}
        }, sort_keys=True))


if __name__ == "__main__":
    main()
