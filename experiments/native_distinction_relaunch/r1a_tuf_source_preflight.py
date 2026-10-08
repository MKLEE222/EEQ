#!/usr/bin/env python3
"""R1a: immutable TUF authority-inventory extraction; NEVER native scoring.

Reads only pinned public root metadata bytes and the already frozen inventory.
No native verifier is called. Syntactic signature overlap is NOT signature
verification. Historical native action labels are never loaded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROW = re.compile(r"^\|\s*(\d+)\s*\|\s*([0-9a-f]{64})\s*\|\s*(\d+)\s*\|")
V = tuple(range(1, 9))


def load_inventory(path):
    rows = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        hit = ROW.match(line)
        if hit:
            n = int(hit.group(1))
            if n in rows:
                raise ValueError(f"duplicate source inventory version {n}")
            rows[n] = (hit.group(2), int(hit.group(3)))
    if tuple(sorted(rows)) != V:
        raise ValueError(f"source inventory must contain exact versions 1..8: {sorted(rows)}")
    return rows


def load_root(blob, expected_version):
    obj = json.loads(blob)
    signed = obj["signed"]
    if signed.get("_type") != "root":
        raise ValueError("expected root signed metadata")
    if type(signed.get("version")) is not int or signed["version"] != expected_version:
        raise ValueError("signed version mismatch")

    keys = signed["keys"]
    role = signed["roles"]["root"]
    if not isinstance(keys, dict) or not keys:
        raise ValueError("empty or missing signed.keys")
    ids = role["keyids"]
    if not isinstance(ids, list) or any(not isinstance(x, str) or not x for x in ids):
        raise ValueError("bad root role keyids")
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate root role keyid")
    if not set(ids).issubset(keys):
        raise ValueError("root role references missing signed key")
    threshold = role["threshold"]
    if type(threshold) is not int or not (1 <= threshold <= len(ids)):
        raise ValueError("invalid root role threshold")
    sigs = obj["signatures"]
    if not isinstance(sigs, list):
        raise ValueError("missing signature list")
    signers = []
    for sig in sigs:
        keyid = sig.get("keyid")
        if not isinstance(keyid, str) or not keyid:
            raise ValueError("bad signature envelope")
        signers.append(keyid)
    return {
        "declared_root_role_keyids": sorted(ids),
        "declared_signed_keys_count": len(keys),
        "declared_root_threshold": threshold,
        "signature_envelope_keyids": sorted(set(signers)),
        "signature_entry_count": len(sigs),
        "duplicate_signature_keyid_count": len(signers) - len(set(signers)),
    }


def report(inventory_path, roots_dir):
    expected = load_inventory(inventory_path)
    roots = []
    for version in V:
        source = Path(roots_dir) / f"{version}.root.json"
        raw = source.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        expect_hash, expect_bytes = expected[version]
        if digest != expect_hash or len(raw) != expect_bytes:
            raise ValueError(f"source version {version}: PIN_MISMATCH")
        parsed = load_root(raw, version)
        roots.append({
            "version": version,
            "raw_sha256": digest,
            "raw_bytes": len(raw),
            **parsed,
        })

    adjacent = []
    changed = 0
    for old, new in zip(roots[:-1], roots[1:]):
        prior = set(old["declared_root_role_keyids"])
        future = set(new["declared_root_role_keyids"])
        envelopes = set(new["signature_envelope_keyids"])
        different = (prior != future or
                     old["declared_root_threshold"] != new["declared_root_threshold"])
        if different:
            changed += 1
        adjacent.append({
            "from_root_version": old["version"],
            "to_root_version": new["version"],
            "candidate_action": "SUBMIT_ADJACENT_ROOT_METADATA",
            "candidate_not_native_verified": True,
            "old_root_threshold": old["declared_root_threshold"],
            "new_root_threshold": new["declared_root_threshold"],
            "retained_role_keyids": sorted(prior & future),
            "removed_role_keyids": sorted(prior - future),
            "added_role_keyids": sorted(future - prior),
            "root_authority_descriptor_changed": different,
            "old_role_keyids_syntactically_in_new_signature_envelope": sorted(prior & envelopes),
            "new_role_keyids_syntactically_in_new_signature_envelope": sorted(future & envelopes),
            "signature_crypto_verified": False,
        })
    return {
        "schema": "eeq-native-distinction-r1a-source-only-preflight-v1",
        "evidence_class": "PRODUCTION_HISTORY_SOURCE_METADATA_ONLY",
        "frozen_source_versions": list(V),
        "native_oracle_invoked": False,
        "native_action_predictions_generated": False,
        "old_native_outcome_labels_read": False,
        "method_scored_rows": 0,
        "g5_count_effect": 0,
        "roots": roots,
        "adjacent_candidate_transitions": adjacent,
        "source_count": len(roots),
        "candidate_transition_count": len(adjacent),
        "authority_descriptor_changes": changed,
        "interpretation": (
            "Source-only structural authority inventory. Signatures were NOT "
            "cryptographically verified; candidate transitions are NOT native "
            "successor-graph edges. Does NOT establish native A/B contrasts."
        ),
        "r1_status": "PREFLIGHT_SOURCE_STRUCTURE_ONLY",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--roots", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    obj = report(args.inventory, args.roots)
    Path(args.out).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")
    print(json.dumps({
        "root_count": obj["source_count"],
        "candidate_adjacencies": obj["candidate_transition_count"],
        "authority_descriptor_changes": obj["authority_descriptor_changes"],
        "native_oracle_invoked": obj["native_oracle_invoked"],
        "method_scored_rows": obj["method_scored_rows"],
        "r1_status": obj["r1_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
