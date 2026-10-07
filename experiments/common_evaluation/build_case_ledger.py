#!/usr/bin/env python3
"""Build the G4 case and execution ledgers from pinned native artifacts.

The semantic signature deliberately excludes machine, Kubernetes/APT version,
retries, and APT Suite/Version zero controls. All native rows remain in the
execution ledger, including pre-exclusions and non-scored observations.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


SOURCES = {
    "apt": {"artifact_id": 11324225958, "sha256": "177fc73578c602834d19d3842a5fb8b6cf9f46155e7d4007a45bb8a1611ff966"},
    "k8s_flux_gcs": {"artifact_id": 11323401781, "sha256": "49a7113823f01f35e92fa7f5ab37f3dfab939c6334774eca9e38c2005321a61c"},
    "k8s_volcano": {"artifact_id": 11330264652, "sha256": "cc92c8ff6feee4e68763107c2cf024f9725e19bcfefa3fff82ddbc1f6889e521"},
    "bottlerocket": {"artifact_id": 11456204296, "sha256": "50a09cbd256f5e4b6f4941ad28a6a1c087da95f6f9b0d0479aaca454fea2f156"},
}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def add(case_map, executions, *, domain, environment, state, action, contract,
        vocabulary, native, expected, execution_id, source, evidence_class,
        status="SCORED", extra=None):
    signature = {
        "semantic_domain": domain,
        "pre_action_state": state,
        "registered_action": action,
        "future_contract": contract,
        "native_action_vocabulary": sorted(vocabulary),
    }
    semantic_id = digest(signature)
    execution = {
        "execution_id": execution_id,
        "semantic_id": semantic_id,
        "environment": environment,
        "source_artifact": source,
        "evidence_class": evidence_class,
        "status": status,
        "native_action": native,
        "frozen_expected": expected,
        "match": native == expected if status == "SCORED" else None,
    }
    if extra:
        execution.update(extra)
    executions.append(execution)
    if status != "SCORED":
        return
    if semantic_id not in case_map:
        case_map[semantic_id] = {
            "semantic_id": semantic_id,
            "signature": signature,
            "family": domain.split(":", 1)[0],
            "environments": [environment],
            "evidence_classes": [evidence_class],
            "native_action": native,
            "frozen_expected": expected,
            "execution_ids": [execution_id],
        }
    else:
        case = case_map[semantic_id]
        if case["native_action"] != native or case["frozen_expected"] != expected:
            raise ValueError(f"Contradictory executions of {semantic_id}: {execution_id}")
        case["execution_ids"].append(execution_id)
        if environment not in case["environments"]:
            case["environments"].append(environment)
        if evidence_class not in case["evidence_classes"]:
            case["evidence_classes"].append(evidence_class)


def build(args):
    if set(args.source_zip) != set(SOURCES):
        raise ValueError(f"All four pinned source ZIPs are required: {sorted(SOURCES)}")
    for key, path in args.source_zip.items():
        observed = file_sha(path)
        if observed != SOURCES[key]["sha256"]:
            raise ValueError(f"Artifact SHA256 mismatch for {key}: {observed}")
    cases, executions = {}, []
    apt = read_json(args.apt)
    if apt["total"] != 576 or apt["matched"] != 576 or apt["core_semantic_templates"] != 144:
        raise ValueError("APT aggregate does not match the frozen 576/144 manifest")
    for row in apt["rows"]:
        state = {k: row[k] for k in ("qualified", "protected_changed", "allow_global", "allow_fields")}
        add(cases, executions, domain="APT:releaseinfo", environment="apt-3.0.3-exhaustive",
            state=state, action="apt-get update", contract="SIGNED_BY_AND_RELEASEINFO_CONTINUATION",
            vocabulary=["ACCEPT", "BLOCK_CONFIRM", "REJECT_AUTH"], native=row["native_action"],
            expected=row["expected"], execution_id=row["id"], source="apt",
            evidence_class="CONTROLLED_NATIVE",
            extra={"frozen_template_id": row["semantic_template_id"],
                   "zero_controls": {"suite_changed": row["suite_changed"], "version_changed": row["version_changed"]},
                   "native_log_sha256": row["log_sha256"]})
    apt_cases = [c for c in cases.values() if c["family"] == "APT"]
    if len(apt_cases) != 144 or any(len(c["execution_ids"]) != 4 for c in apt_cases):
        raise ValueError("APT zero-control dedup is not exactly 144 x 4")

    with Path(args.k8s).open(newline="", encoding="utf-8") as f:
        k8s_rows = list(csv.DictReader(f, delimiter="\t"))
    if len(k8s_rows) != 30:
        raise ValueError("K8s frozen grid must retain 30 rows")
    for row in k8s_rows:
        params = json.loads(row["params"])
        family = row["family"]
        status = "SCORED" if row["status"] == "PASS" else "PREEXCLUDED_NATIVE_SCHEMA_INVALID"
        add(cases, executions, domain=f"K8s:{family}-vap", environment="k8s-v1.34.3",
            state=params, action=params.get("operation", "CREATE") + " Pod",
            contract=f"{family.upper()}_VAP_ADMISSION", vocabulary=["ACCEPT", "REJECT"],
            native=row["observed"], expected=row["expected"], execution_id=row["case"],
            source="k8s_flux_gcs", evidence_class="PUBLIC_MAINTAINED_CONFIG_NATIVE_REPLAY",
            status=status, extra={"native_attribution": row["attribution"]})
    if sum(c["family"] == "K8s" for c in cases.values()) != 24:
        raise ValueError("K8s eligible semantic count must be 24")

    volcano = read_json(args.volcano)
    if len(volcano) != 72:
        raise ValueError("Volcano frozen grid must have 72 rows")
    for row in volcano:
        state = {k: row[k] for k in ("scheduler", "min", "max")}
        add(cases, executions, domain="K8s:volcano-vap", environment="k8s-v1.34.3",
            state=state, action="CREATE Pod", contract="VOLCANO_VAP_ADMISSION",
            vocabulary=["ACCEPT", "REJECT"], native=row["observed"], expected=row["expected"],
            execution_id=row["case"], source="k8s_volcano",
            evidence_class="PUBLIC_MAINTAINED_CONFIG_NATIVE_REPLAY",
            status="SCORED" if row["status"] == "PASS" else row["status"],
            extra={"native_attribution": row["attribution"]})
    if sum(c["signature"]["semantic_domain"] == "K8s:volcano-vap" for c in cases.values()) != 72:
        raise ValueError("Volcano semantic count must be 72")

    tuf = read_json(args.bottlerocket)
    if tuf["summary"]["transitions"] != 7 or not tuf["summary"]["complete"]:
        raise ValueError("Bottlerocket native root chain is incomplete")
    for row in tuf["rows"]:
        state = {
            "trusted_root_threshold": row["pre_action_state"]["trusted_root_threshold"],
            "trusted_root_keyids": row["pre_action_state"]["trusted_root_keyids"],
            "candidate_root_threshold": row["candidate_state"]["root_threshold"],
            "candidate_root_keyids": row["candidate_state"]["root_keyids"],
            "candidate_signed_bytes_sha256": row["source_sha256"]["to_root"],
        }
        add(cases, executions, domain="TUF:bottlerocket-root", environment=row["environment"],
            state=state, action=row["action"], contract=row["future_contract"],
            vocabulary=row["native_action_vocabulary"], native=row["native_action"],
            expected="ACCEPT", execution_id=row["case_id"], source="bottlerocket",
            evidence_class=row["evidence_class"],
            extra={"from_version": row["from_version"], "to_version": row["to_version"],
                   "source_sha256": row["source_sha256"], "oracle": row["oracle"]})

    if any(x["match"] is False for x in executions):
        raise ValueError("Native mismatch retained; inspect before scoring")
    payload = {
        "schema": "eeq-g4-unified-case-ledger-v1",
        "g4_freeze_commit": "c15b212ad0c2be3856a03d38802aaffa628aefd1",
        "source_artifacts": SOURCES,
        "counting_rule": "One semantic signature across environments; versions, retries and APT Suite/Version zero controls are executions only.",
        "cases": sorted(cases.values(), key=lambda x: (x["family"], x["semantic_id"])),
        "executions": executions,
        "summary": {
            "scored_unique_semantic_cases": len(cases),
            "unique_by_domain": dict(sorted(Counter(c["signature"]["semantic_domain"] for c in cases.values()).items())),
            "all_executions": len(executions),
            "execution_statuses": dict(sorted(Counter(x["status"] for x in executions).items())),
            "fifth_family_holdout": "UNOPENED",
        },
    }
    with Path(args.out).open("w", encoding="utf-8", newline="\n") as out:
        out.write(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return payload["summary"]


def main():
    p = argparse.ArgumentParser()
    for name in ("apt", "k8s", "volcano", "bottlerocket", "out"):
        p.add_argument(f"--{name}", required=True)
    p.add_argument("--source-zip", action="append", required=True, metavar="KEY=PATH")
    args = p.parse_args()
    args.source_zip = dict(item.split("=", 1) for item in args.source_zip)
    print(json.dumps(build(args), sort_keys=True))


if __name__ == "__main__":
    main()
