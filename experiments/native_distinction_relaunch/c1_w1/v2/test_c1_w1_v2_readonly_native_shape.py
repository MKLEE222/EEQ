#!/usr/bin/env python3
"""Synthetic read-only forensic tests, no original native archive consulted."""
import copy,hashlib,json,unittest
from c1_w1_v2_readonly_native_shape import inspect
from test_c1_w1_scoped_evidence_verifier import make_nominal


def artifact(raw):
 bytes_=json.dumps(raw,sort_keys=True).encode()
 digest=hashlib.sha256(bytes_).hexdigest()
 return digest,""+digest+"  out/C1_W1_RAW_NATIVE_HTTP_WATCH.json\n"


class ReadOnlyNativeShapeTests(unittest.TestCase):
 def setUp(self):self.raw=make_nominal()
 def run_audit(self):
  sha,manifest=artifact(self.raw)
  return inspect(self.raw,sha,manifest)
 def test_01_nominal_survives_as_forensic_only(self):
  x=self.run_audit()
  self.assertEqual(x["science_disposition"],"READONLY_POSTNATIVE_FORENSIC_ONLY")
  self.assertTrue(x["first_original_workflow_remains_failure"])
  self.assertEqual((x["watch_event_count"],x["raw_collection_list_count"]),(3,8))
 def test_02_missing_member_kind_is_reported_not_retrospectively_patched(self):
  del self.raw["checkpoints"][0]["collections"]["policy"]["response"]["items"][0]["kind"]
  x=self.run_audit()
  self.assertEqual(x["missing_native_item_fields"]["kind"],1)
  self.assertEqual(x["per_item_shape"][0]["item_kind"],"<ABSENT>")
 def test_03_wrong_present_member_kind_is_not_silent(self):
  self.raw["checkpoints"][0]["collections"]["policy"]["response"]["items"][0]["kind"]="Pod"
  x=self.run_audit()
  self.assertEqual(x["per_item_shape"][0]["item_kind"],"Pod")
  self.assertEqual(x["science_disposition"],"READONLY_POSTNATIVE_FORENSIC_ONLY")
 def test_04_missing_member_identity_is_flagged(self):
  del self.raw["checkpoints"][1]["collections"]["binding"]["response"]["items"][0]["metadata"]["uid"]
  x=self.run_audit()
  self.assertTrue(x["unexpected_collection_or_source_identity"])
 def test_05_wrong_collection_kind_recorded(self):
  self.raw["checkpoints"][0]["collections"]["policy"]["response"]["kind"]="WrongList"
  x=self.run_audit()
  self.assertTrue(x["unexpected_collection_or_source_identity"])
 def test_06_raw_bytes_must_match_archived_SHA(self):
  sha,manifest=artifact(self.raw)
  with self.assertRaisesRegex(ValueError,"SHA256_MISMATCH"):
   inspect(self.raw,"0"*64,manifest)
 def test_07_prescore_histories_never_relabelled(self):
  x=self.run_audit()
  self.assertFalse(x["global_c1_established"])
  self.assertFalse(x["B9_independent_superiority_established"])
  self.assertEqual(x["native_pod_decisions_scored"],0)
  self.assertEqual(x["original_G5_increment"],0)
 def test_08_watch_source_identity_and_count_visible_for_readonly_audit(self):
  x=self.run_audit()
  self.assertEqual(len(x["per_watch_event_shape"]),3)
  self.assertEqual([r["event_type"] for r in x["per_watch_event_shape"]],
                   ["ADDED","ADDED","DELETED"])

if __name__=="__main__":
 unittest.main(verbosity=2)
