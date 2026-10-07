#!/usr/bin/env python3
"""Retain both GitHub samples in the unified G4 ledger without inflating G5.

The v1 adapter exposes lawful evidence but has unresolved C1 predicates and no
defensible semantic-equivalence normalization. Thus every PR is an execution
record with a native protocol label and C1 coverage failure, not a unique
scored semantic case.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

FIRST_ZIP_SHA256 = "851ac6dce9070be3947010d9e889b4043fc2b58eb5343cb7939e5cac32a50541"
FIRST_ARTIFACT_ID = 11327648114
FIRST_RUN_ID = 37270160203
REPOS = {"nodejs/node", "microsoft/vscode", "home-assistant/core", "llvm/llvm-project"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validated_sample(root, validation_path, zip_path, expected_sha, name):
    observed = sha256(zip_path)
    if observed != expected_sha:
        raise ValueError(f"{name} artifact SHA256 mismatch: {observed}")
    summary = load(root / "summary.json")
    validation = load(validation_path)
    if len(summary) != 100 or validation["sample_rows"] != 100:
        raise ValueError(f"{name} must retain exactly 100 mechanically selected PRs")
    by_id = {(r["repo"], r["pr"]): r for r in validation["rows"]}
    if len(by_id) != 100:
        raise ValueError(f"{name} adapter rows contain duplicates")
    counts = Counter(r["repo"] for r in summary)
    if set(counts) != REPOS or any(n != 25 for n in counts.values()):
        raise ValueError(f"{name} violates frozen 25-per-repository rule")
    for row in summary:
        key = row["repo"], row["pr"]
        adapter = by_id[key]
        if row["native_label"] != adapter["native_label"] or adapter["g4_count_eligible"]:
            raise ValueError(f"{name} adapter/native join or G4 count eligibility failed: {key}")
    return summary, by_id


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-ledger", required=True, type=Path)
    p.add_argument("--first-dir", required=True, type=Path)
    p.add_argument("--first-validation", required=True, type=Path)
    p.add_argument("--first-zip", required=True, type=Path)
    p.add_argument("--second-dir", required=True, type=Path)
    p.add_argument("--second-validation", required=True, type=Path)
    p.add_argument("--second-zip", required=True, type=Path)
    p.add_argument("--second-sha256", required=True)
    p.add_argument("--second-artifact-id", required=True, type=int)
    p.add_argument("--second-run-id", required=True, type=int)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    ledger = load(a.base_ledger)
    if ledger["summary"]["scored_unique_semantic_cases"] != 247:
        raise ValueError("Unexpected base ledger count")
    first, first_adapter = validated_sample(a.first_dir, a.first_validation, a.first_zip, FIRST_ZIP_SHA256, "first")
    second, second_adapter = validated_sample(a.second_dir, a.second_validation, a.second_zip,
                                               a.second_sha256, "second")
    first_ids = {(r["repo"], r["pr"]) for r in first}
    second_ids = {(r["repo"], r["pr"]) for r in second}
    if first_ids & second_ids:
        raise ValueError(f"Second sample overlaps first in {len(first_ids & second_ids)} PR IDs")
    for name, rows, adapters in (("first", first, first_adapter), ("second", second, second_adapter)):
        for row in rows:
            adapter = adapters[row["repo"], row["pr"]]
            ledger["executions"].append({
                "execution_id": f"github-{name}-{row['repo']}#{row['pr']}",
                "semantic_id": None,
                "family": "GitHub",
                "environment": row["repo"],
                "source_artifact": f"github_{name}",
                "evidence_class": "PRODUCTION_HISTORY",
                "status": "C1_COVERAGE_FAILURE",
                "native_protocol_scored": row["native_label"] in {"NATIVE_ADMISSIBLE", "NATIVE_BLOCKED"},
                "native_action": row["native_label"],
                "adapter_status": adapter["adapter_status"],
                "adapter_predicted_label": adapter["predicted_native_label"],
                "adapter_match": adapter["native_match"],
                "raw_lawful_state_sha256": adapter.get("raw_state_sha256"),
                "g4_count_eligible": False,
                "g4_count_reason": adapter["g4_count_reason"],
                "head_sha": row["head_sha"],
                "base": row["base"],
                "endpoint_status": row.get("endpoint_status"),
                "attribution_incomplete": any(code != 200 for code in row.get("endpoint_status", {}).values()),
            })
    ledger["schema"] = "eeq-g4-unified-case-ledger-with-github-v1"
    ledger["source_artifacts"]["github_first"] = {
        "run_id": FIRST_RUN_ID, "artifact_id": FIRST_ARTIFACT_ID, "sha256": FIRST_ZIP_SHA256}
    ledger["source_artifacts"]["github_second"] = {
        "run_id": a.second_run_id, "artifact_id": a.second_artifact_id,
        "sha256": a.second_sha256}
    ledger["summary"]["all_executions"] = len(ledger["executions"])
    ledger["summary"]["execution_statuses"] = dict(sorted(Counter(x["status"] for x in ledger["executions"]).items()))
    ledger["summary"]["github_native_protocol_scored"] = sum(
        x.get("native_protocol_scored", False) for x in ledger["executions"])
    ledger["summary"]["github_g4_count_eligible"] = 0
    ledger["summary"]["github_attribution_incomplete"] = sum(
        x.get("attribution_incomplete", False) for x in ledger["executions"])
    ledger["summary"]["scored_unique_semantic_cases"] = len(ledger["cases"])
    with a.out.open("w", encoding="utf-8", newline="\n") as out:
        out.write(json.dumps(ledger, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps(ledger["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
