#!/usr/bin/env python3
"""Recover the reachable REST file-list tail for the frozen PR 66546 sample.

This is a later source supplement, never an adapter input or a new sample row.
"""
import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import requests

API = "https://api.github.com/repos/nodejs/node/pulls/66546"
EXPECTED_HEAD = "49072a0be4c7410982557aebf5b5c924fe7db597"
EXPECTED_CHANGED_FILES = 3109


def get(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "EEQ-PR-file-source-supplement/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            return response.status_code, response.content, dict(response.headers)
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def pr_identity():
    code, raw, headers = get(API)
    if code != 200:
        raise ValueError(f"PR identity HTTP {code}")
    pr = json.loads(raw)
    if pr["head"]["sha"] != EXPECTED_HEAD or pr["changed_files"] != EXPECTED_CHANGED_FILES:
        raise ValueError("PR head or file count changed since frozen sample")
    return {"head_sha": pr["head"]["sha"], "base_sha": pr["base"]["sha"],
            "changed_files": pr["changed_files"], "updated_at": pr["updated_at"],
            "http_date": headers.get("Date")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archived-files", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    archived = json.loads(args.archived_files.read_text(encoding="utf-8"))
    if archived["status"] != 206 or len(archived["body"]) != 2000:
        raise ValueError("Expected frozen 2,000-file partial archive")
    before = pr_identity()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for page in (1, 20, *range(21, 32)):
        code, raw, headers = get(API + f"/files?per_page=100&page={page}")
        if code != 200:
            raise ValueError(f"page {page} HTTP {code}")
        body = json.loads(raw)
        if not isinstance(body, list):
            raise ValueError(f"page {page} did not return an array")
        if page in (1, 20):
            original = archived["body"][(page-1)*100:page*100]
            key = lambda rows: [(x.get("filename"), x.get("sha")) for x in rows]
            if key(body) != key(original):
                raise ValueError(f"boundary page {page} differs from frozen archive")
        elif page <= 30 and len(body) != 100:
            raise ValueError(f"page {page} expected 100 files, got {len(body)}")
        elif page == 31 and body:
            raise ValueError("GitHub unexpectedly returned files beyond documented 3,000 cap")
        if page >= 21:
            path = args.out_dir / f"page-{page:02}.json"
            path.write_bytes(raw)
            manifest.append({"page": page, "count": len(body), "sha256": hashlib.sha256(raw).hexdigest(),
                             "http_date": headers.get("Date"), "file": path.name})
    after = pr_identity()
    if before["head_sha"] != after["head_sha"] or before["base_sha"] != after["base_sha"]:
        raise ValueError("PR refs changed during source supplement")
    payload = {
        "schema": "eeq-github-pr-66546-file-supplement-v1",
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_second_sample_run_id": 37562674312,
        "frozen_second_sample_artifact_id": 11458025511,
        "frozen_archived_files": 2000,
        "source_supplement_files": sum(x["count"] for x in manifest),
        "rest_accessible_total": 3000,
        "reported_changed_files": EXPECTED_CHANGED_FILES,
        "beyond_rest_file_list_cap": EXPECTED_CHANGED_FILES - 3000,
        "before": before, "after": after, "pages": manifest,
        "boundary_pages_matched_frozen_archive": [1, 20],
        "adapter_input": False,
        "g4_semantic_count_increment": 0,
    }
    with (args.out_dir / "SUPPLEMENT_MANIFEST.json").open("w", encoding="utf-8", newline="\n") as out:
        out.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: payload[k] for k in ("frozen_archived_files", "source_supplement_files",
                                           "rest_accessible_total", "beyond_rest_file_list_cap")}, sort_keys=True))


if __name__ == "__main__":
    main()
