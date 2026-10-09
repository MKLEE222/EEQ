#!/usr/bin/env python3
"""Synthetic anti-masking unit tests ONLY. No native TUF oracle is imported."""
import copy
import json
import sys
import unittest
from pathlib import Path

from r2b_join_only_scorer import ACTIONS, STATES, action_words, compare

PRED = None
MANIFEST = None


def fake_native(p, m):
    edges = {(e["from_state"], e["action"]): e for e in p["predictions"]}
    states = {s["state"]: s for s in p["states"]}
    sources = {x["name"]: x["sha256"] for x in m["sources"]}
    rows, traces, controls = [], [], []
    for s in STATES:
        for a in ACTIONS:
            e = edges[s, a]
            rows.append({
                "from_state": s, "action": a,
                "effect": "ACCEPT" if e["effect"] == "ADVANCE_TRUST_ROOT"
                          else "REJECT",
                "native_after_state": e["to_state"],
                "initial_source_sha256": e["from_source_sha256"],
                "candidate_sha256": e["candidate_source_sha256"],
                "setup_error": None,
                "error": None,
            })
        for word in action_words():
            pos, events = s, []
            for a in word:
                e = edges[pos, a]
                pos = e["to_state"]
                events.append({
                    "effect": "ACCEPT" if e["effect"] == "ADVANCE_TRUST_ROOT"
                              else "REJECT",
                    "native_after_state": pos,
                })
            traces.append({
                "from_state": s,
                "word": list(word),
                "events": events,
                "terminal_native_state": pos,
                "setup_error": None,
            })
        for t in "ab":
            controls.append({
                "from_state": s,
                "target_source_name": "targets-" + t + ".json",
                "target_source_sha256": sources["targets-" + t + ".json"],
                "native_qualification": (
                    "QUALIFIED" if s[2] == t else "UNQUALIFIED"),
                "setup_error": None,
                "error": None,
            })
    return {
        "schema": "eeq-r2b-native-tuf-controlled-grid-v1",
        "registered_states": list(STATES),
        "registered_actions": list(ACTIONS),
        "registered_horizon": 2,
        "predictions_json_read": False,
        "original_g5_increment": 0,
        "source_digests": sources,
        "one_step": rows,
        "action_traces": traces,
        "target_controls": controls,
    }


class ScorerKillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pred, cls.manifest = PRED, MANIFEST

    def clean(self):
        return fake_native(self.pred, self.manifest)

    def test_clean_mock_oracle_counts_not_native_evidence(self):
        s = compare(self.pred, self.clean(), self.manifest)["summary"]
        self.assertEqual(s["one_step_matches"], 24)
        self.assertEqual(s["trace_matches"], 126)
        self.assertEqual(s["targets_controls_matches"], 12)
        self.assertEqual(s["noncosmetic_native_b_pairs_verified"], 3)
        self.assertEqual(s["strong_b9_native_matches"], 24)

    def test_one_bad_native_update_is_retained(self):
        n = self.clean()
        n["one_step"][0]["effect"] = "REJECT"
        r = compare(self.pred, n, self.manifest)["summary"]
        self.assertEqual(r["one_step_mismatches"], 1)
        self.assertEqual(r["one_step_matches"], 23)

    def test_bad_native_successor_id_is_not_hidden_by_correct_label(self):
        n = self.clean()
        n["one_step"][0]["native_after_state"] = "s4b"
        s = compare(self.pred, n, self.manifest)["summary"]
        self.assertEqual(s["one_step_mismatches"], 1)

    def test_dropped_one_step_is_fatal(self):
        n = self.clean()
        n["one_step"].pop()
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_NATIVE_24_GRID"):
            compare(self.pred, n, self.manifest)

    def test_dropped_native_trace_is_fatal(self):
        n = self.clean()
        n["action_traces"].pop()
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_NATIVE_126_TRACES"):
            compare(self.pred, n, self.manifest)

    def test_one_bad_native_trace_does_not_allow_b_pair_credit(self):
        n = self.clean()
        row = next(r for r in n["action_traces"]
                   if r["from_state"] == "s2a" and r["word"] == [ACTIONS[0]])
        row["events"][0]["effect"] = "REJECT"
        summary = compare(self.pred, n, self.manifest)["summary"]
        self.assertEqual(summary["trace_mismatches"], 1)
        self.assertLess(summary["noncosmetic_native_b_pairs_verified"], 3)

    def test_broken_target_role_negative_control_is_not_merge_evidence(self):
        n = self.clean()
        row = next(r for r in n["target_controls"]
                   if r["from_state"] == "s2b" and
                   r["target_source_name"] == "targets-a.json")
        row["native_qualification"] = "QUALIFIED"
        s = compare(self.pred, n, self.manifest)["summary"]
        self.assertEqual(s["targets_controls_matches"], 11)
        self.assertLess(s["noncosmetic_native_b_pairs_verified"], 3)

    def test_source_hash_drift_fails_before_scoring(self):
        n = self.clean()
        n["source_digests"]["targets-a.json"] = "bad-hash"
        with self.assertRaisesRegex(ValueError, "SOURCE_HASH_MISMATCH"):
            compare(self.pred, n, self.manifest)

    def test_duplicate_or_missing_targets_control_fails(self):
        n = self.clean()
        n["target_controls"].pop()
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_TARGET_12"):
            compare(self.pred, n, self.manifest)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: test_r2b_join_only_scorer.py SOURCE_PREDICTIONS SOURCE_MANIFEST")
    PRED = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    MANIFEST = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    unittest.main(argv=[sys.argv[0]], verbosity=2)
