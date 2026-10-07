#!/usr/bin/env python3
"""Frozen GitHub governance adapter v1: lawful inputs and conservative decision.

The adapter reads archived governance evidence only. Native mergeability fields
are read solely by the separate validation function, never by adapt_pr().
"""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote


MERGE_RULE_TYPES = {
    "pull_request", "required_status_checks", "required_signatures",
    "commit_message_pattern", "required_deployments", "required_conversation_resolution",
}
PASS_CHECK_CONCLUSIONS = {"success", "neutral", "skipped"}


def read_wrapper(path):
    try:
        wrapper = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, None
    return wrapper.get("status"), wrapper.get("body")


def frozen_signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def latest_reviews(reviews):
    by_user = {}
    for review in reviews:
        user = (review.get("user") or {}).get("login")
        if user and review.get("state") in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            if user not in by_user or (review.get("submitted_at") or "") >= (by_user[user].get("submitted_at") or ""):
                by_user[user] = review
    return by_user


def check_observations(check_runs, combined_status):
    observations = defaultdict(list)
    for run in (check_runs or {}).get("check_runs", []):
        observations[run.get("name")].append({
            "kind": "check_run", "status": run.get("status"), "conclusion": run.get("conclusion"),
            "app_id": (run.get("app") or {}).get("id"), "completed_at": run.get("completed_at"),
        })
    for status in (combined_status or {}).get("statuses", []):
        observations[status.get("context")].append({
            "kind": "commit_status", "state": status.get("state"),
            "updated_at": status.get("updated_at"),
        })
    return dict(sorted(observations.items()))


def adapt_pr(root, repo, number):
    owner, name = repo.split("/", 1)
    rdir = root / owner / name
    pdir = rdir / "prs" / str(number)
    pr_status, pr = read_wrapper(pdir / "pr.json")
    if pr_status != 200 or not isinstance(pr, dict):
        return {"repo": repo, "pr": number, "adapter_status": "SOURCE_UNAVAILABLE", "predicted_native_label": None}
    base = (pr.get("base") or {}).get("ref")
    head_sha = (pr.get("head") or {}).get("sha")
    branch_status, branch = read_wrapper(rdir / "branches" / (quote(base or "", safe="") + ".json"))
    rules_status, rules = read_wrapper(rdir / "effective_rules" / (quote(base or "", safe="") + ".json"))
    reviews_status, reviews = read_wrapper(pdir / "reviews.json")
    checks_status, checks = read_wrapper(pdir / "check_runs.json")
    statuses_status, statuses = read_wrapper(pdir / "combined_status.json")
    commits_status, commits = read_wrapper(pdir / "commits.json")
    verification_path = pdir / "commit_verification.json"
    verification = json.loads(verification_path.read_text()) if verification_path.exists() else None
    unknown, blockers = [], []
    if branch_status != 200 or rules_status != 200:
        unknown.append("missing_branch_or_effective_rules")
    if reviews_status != 200:
        unknown.append("missing_reviews")
    if checks_status != 200 or statuses_status != 200:
        unknown.append("missing_check_observations")
    if commits_status != 200 or verification is None:
        unknown.append("missing_commit_chain")
    rules = rules if isinstance(rules, list) else []
    branch_protection = ((branch or {}).get("protection") or {}) if isinstance(branch, dict) else {}
    branch_checks = ((branch_protection.get("required_status_checks") or {}).get("checks") or [])
    required_checks = {(x.get("context"), x.get("app_id")) for x in branch_checks if x.get("context")}
    for rule in rules:
        if rule.get("type") == "required_status_checks":
            for x in (rule.get("parameters") or {}).get("required_status_checks", []):
                if x.get("context"):
                    required_checks.add((x["context"], x.get("integration_id")))
    observations = check_observations(checks, statuses)
    if required_checks:
        # The first collector archived HEAD checks, not the synthetic merge
        # commit. GitHub may use the latter when both have a status. A missing
        # or failed HEAD check therefore cannot establish a native blocker.
        unknown.append("required_checks_merge_commit_unobserved")
    for rule in rules:
        typ = rule.get("type")
        p = rule.get("parameters") or {}
        if typ == "pull_request":
            required = p.get("required_approving_review_count", 0)
            if reviews_status == 200:
                current = latest_reviews(reviews if isinstance(reviews, list) else [])
                approvals = sum(x.get("state") == "APPROVED" for x in current.values())
                if approvals < required:
                    blockers.append({"mechanism": "required_reviews", "required": required, "observed": approvals})
            for flag in ("require_code_owner_review", "require_last_push_approval",
                         "require_extra_approval_for_unattributed_changes", "required_review_thread_resolution"):
                if p.get(flag):
                    unknown.append("unresolved_" + flag)
            if p.get("required_reviewers"):
                unknown.append("unresolved_required_reviewers")
        elif typ == "required_signatures":
            if verification is not None and any(v.get("verified") is not True for v in verification):
                blockers.append({"mechanism": "required_signatures"})
        elif typ in MERGE_RULE_TYPES and typ != "required_status_checks":
            unknown.append("unresolved_" + typ)
    # The branch API does not expose all legacy protection predicates. Preserve
    # this as an explicit C1 uncertainty, even when positive visible checks pass.
    if (branch or {}).get("protected"):
        unknown.append("legacy_branch_protection_predicates_unavailable")
    # A missing required approval or invalid signature is a sufficient blocker
    # for an ordinary merger. All other rules remain exposed but unresolved;
    # v1 never predicts the positive class from partial governance metadata.
    predicted = "NATIVE_BLOCKED" if blockers else None
    adapter_status = "PREDICTED_SUFFICIENT_BLOCKER" if predicted else "INSUFFICIENT_EVIDENCE_REFUSE"
    mechanisms = [{"type": r.get("type"), "ruleset_id": r.get("ruleset_id"),
                   "source": r.get("ruleset_source"), "parameters": r.get("parameters")}
                  for r in rules if r.get("type") in MERGE_RULE_TYPES]
    state = {
        "repo": repo, "base": base, "head_sha": head_sha,
        "branch_protection": branch_protection,
        "active_merge_mechanisms": mechanisms,
        "review_states": {k: v.get("state") for k, v in latest_reviews(reviews if isinstance(reviews, list) else []).items()},
        "required_checks": sorted([{"context": c, "app_id": a} for c, a in required_checks], key=str),
        "check_observations": observations,
        "commit_verification": verification,
        "registered_action": "MERGE_PR",
        "future_contract": "BRANCH_GOVERNANCE_CONTINUATION",
        "native_action_vocabulary": ["NATIVE_ADMISSIBLE", "NATIVE_BLOCKED"],
    }
    return {
        "repo": repo, "pr": number, "adapter_version": "github-governance-v1",
        "adapter_status": adapter_status, "predicted_native_label": predicted,
        "blocking_reasons": blockers, "unresolved_predicates": sorted(set(unknown)),
        "v0_c1_c2_c3": state, "raw_state_sha256": frozen_signature(state),
        "g4_count_eligible": False,
        "g4_count_reason": "C1 and semantic equivalence normalization remain unresolved",
    }


def validate(root, out):
    summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
    rows = []
    for native in summary:
        result = adapt_pr(root, native["repo"], native["pr"])
        result["native_label"] = native["native_label"]
        result["scored"] = native["native_label"] in {"NATIVE_ADMISSIBLE", "NATIVE_BLOCKED"}
        result["native_match"] = (result["predicted_native_label"] == native["native_label"]
                                  if result["scored"] and result["predicted_native_label"] else None)
        rows.append(result)
    report = {
        "adapter_version": "github-governance-v1", "sample_rows": len(rows),
        "scored_native_rows": sum(x["scored"] for x in rows),
        "predicted_scored_rows": sum(x["native_match"] is not None for x in rows),
        "predicted_matches": sum(x["native_match"] is True for x in rows),
        "predicted_mismatches": sum(x["native_match"] is False for x in rows),
        "refusals": sum(x["adapter_status"] == "INSUFFICIENT_EVIDENCE_REFUSE" for x in rows),
        "rows": rows,
    }
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {k: v for k, v in report.items() if k != "rows"}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("artifact_dir", type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(validate(a.artifact_dir, a.out), sort_keys=True))
