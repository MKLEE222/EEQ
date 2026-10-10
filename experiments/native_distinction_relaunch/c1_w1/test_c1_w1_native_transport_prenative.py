#!/usr/bin/env python3
"""Pure pre-native HTTP Watch parser and source-pinning kill tests (zero API calls)."""
import unittest
from unittest.mock import patch
from c1_w1_native_watch_capture import (
 HTTPWatch,CLASSES,EXPECTED_EVENTS,pinned_sources,permission_probe
)

def event(kind,evt,name):
 return {"type":evt,"object":{
   "apiVersion":"admissionregistration.k8s.io/v1",
   "kind":"ValidatingAdmissionPolicy" if kind=="policy" else "ValidatingAdmissionPolicyBinding",
   "metadata":{"name":name,"uid":"registered-uid","resourceVersion":"OPAQUE@rev"}}}

class NativeTransportPrenativeKill(unittest.TestCase):
 def test_01_original_source_git_blobs_unchanged(self):
  self.assertEqual(len(pinned_sources()),6)
 def test_02_http_watch_url_has_exact_scoped_collection_rv(self):
  w=HTTPWatch("policy","abc/opaque+cursor")
  self.assertEqual(w.rv,"abc/opaque+cursor")
  self.assertIn("resourceVersion=abc%2Fopaque%2Bcursor",w.url)
  self.assertIn("allowWatchBookmarks=true",w.url)
  self.assertIn("timeoutSeconds=150",w.url)
 def test_03_watch_event_exact_type_source_and_identity(self):
  w=HTTPWatch("binding","cursor")
  w.queue.put(("EVENT",event("binding","ADDED","third")))
  self.assertEqual(w.expected("ADDED","third",0.2)["object"]["metadata"]["name"],"third")
 def test_04_bookmark_not_substituted_for_registered_change(self):
  w=HTTPWatch("binding","cursor")
  w.queue.put(("EVENT",{"type":"BOOKMARK","object":{"metadata":{"resourceVersion":"bar"}}}))
  w.queue.put(("EVENT",event("binding","ADDED","third")))
  self.assertEqual(w.expected("ADDED","third",0.2)["type"],"ADDED")
 def test_05_410_error_event_fails_closed(self):
  w=HTTPWatch("binding","cursor")
  w.queue.put(("EVENT",{"type":"ERROR","object":{"code":410,"message":"Gone"}}))
  with self.assertRaisesRegex(RuntimeError,"NATIVE_WATCH_ERROR_EVENT"):
   w.expected("ADDED","third",0.2)
 def test_06_different_member_is_not_an_acceptable_event(self):
  w=HTTPWatch("binding","cursor")
  w.queue.put(("EVENT",event("binding","ADDED","other")))
  with self.assertRaisesRegex(RuntimeError,"UNREGISTERED_WATCH_EVENT_IDENTITY"):
   w.expected("ADDED","third",0.2)
 def test_07_different_event_type_never_fulfills_target(self):
  w=HTTPWatch("binding","cursor")
  w.queue.put(("EVENT",event("binding","MODIFIED","third")))
  with self.assertRaisesRegex(RuntimeError,"UNREGISTERED_WATCH_EVENT_TYPE"):
   w.expected("ADDED","third",0.2)
 def test_08_missing_uid_cannot_create_witness(self):
  w=HTTPWatch("policy","cursor")
  q=event("policy","ADDED","third")
  del q["object"]["metadata"]["uid"]
  w.queue.put(("EVENT",q))
  with self.assertRaisesRegex(RuntimeError,"UNREGISTERED_WATCH_EVENT_IDENTITY"):
   w.expected("ADDED","third",0.2)
 def test_09_fully_closed_early_stream_cannot_be_replayed(self):
  w=HTTPWatch("binding","cursor")
  w.ended=True
  with self.assertRaisesRegex(RuntimeError,"NATIVE_WATCH_EARLY_CLOSED"):
   w.expected("ADDED","third",0.1)
 def test_10_denied_watch_authorization_is_not_overridden_by_list(self):
  def fake(*args,check=False):
   status="no" if args[2]=="watch" and "bindings" in args[3] else "yes"
   return {"exit_code":0,"stdout":status+"\n"}
  with patch("c1_w1_native_watch_capture.kubectl",side_effect=fake):
   rights=permission_probe()
  self.assertTrue(rights["binding"]["list"])
  self.assertFalse(rights["binding"]["watch"])

if __name__=="__main__":
 unittest.main(verbosity=2)
