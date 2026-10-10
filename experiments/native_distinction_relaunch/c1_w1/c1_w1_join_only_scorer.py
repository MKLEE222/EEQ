#!/usr/bin/env python3
"""C1-W1 JOIN ONLY: consumes already saved native capture + earlier sealed source plan.

No kubectl / live API, no Pod correctness claims, no rewriting source truth.
"""
import argparse,hashlib,json
from pathlib import Path

from c1_w1_scoped_evidence_verifier import verify

EXPECTED={
 "watch_channels":2,"watch_events":3,
 "full_list_snapshots":8,"native_mutations":3,
 "native_decisions":0
}

def require(check,reason):
 if not check: raise ValueError(reason)

def join(source_manifest,forecast,native,source_manifest_bytes=None):
 require(source_manifest.get("schema")=="eeq-c1-w1-source-only-manifest-v1"
         and source_manifest.get("source_model_native_observations_read") is False
         and source_manifest.get("new_native_decision_cells")==0
         and source_manifest.get("main_v1_g5_increment")==0
         and len(source_manifest.get("source_files",[]))==6,
         "SOURCE_ONLY_PROVENANCE_OR_SCOPE_NOT_FROZEN")
 require(forecast.get("registrations")==EXPECTED
         and forecast.get("native_outcomes_read") is False
         and forecast.get("global_admission_accept_certified") is False,
         "PRESCORE_EVENT_DENOMINATOR_OR_CLAIM_INVALID")
 if native.get("native_errors"):
  raise ValueError("NATIVE_RAW_CAPTURE_ERROR_RETAINED:"+repr(native["native_errors"]))
 for key,count in (
   ("registered_main_native_watch_events",3),
   ("registered_full_source_list_snapshots",8),
   ("registered_independent_watch_channels",2),
   ("registered_native_source_mutations",3),
   ("observed_native_watch_events",3),
   ("observed_source_list_snapshots",8),
   ("observed_native_source_mutations",3),
   ("native_validated_scored_pod_decisions",0),
   ("historical_g5_new_cases",0),
   ("native_pod_decision_calls",0)):
  require(native.get(key)==count,"NATIVE_REGISTERED_DENOMINATOR_FAILED:"+key)
 verdict=verify(native,forecast)
 require(verdict["status"]=="C1_W1_SCOPED_NATIVE_LIST_WATCH_FEASIBILITY_B9_TIE",
         "NATIVE_SOURCE_CUSTODY_INVALID:"+verdict["status"])
 # The strong B9 must be allowed to reuse ALL lawful source APIs and even
 # this checker. No independent method novelty or engineering trial implied.
 return {
  "schema":"eeq-c1-w1-native-join-only-result-v1",
  "evidence_class":"CONTROLLED_KUBERNETES_NATIVE_LIST_WATCH_DEV",
  "native_pod_decisions_scored":0,"old_v1_G5_increment":0,
  "registered_native_list_snapshots":8,
  "registered_native_watch_channels":2,
  "registered_native_watch_events":3,
  "registered_native_source_mutations":3,
  "captured_native_list_snapshots":8,
  "captured_native_watch_events":3,
  "native_source_mutations_verified":3,
  "exact_opaque_per_class_cursor_binding":True,
  "real_global_c1_authority_proven":False,
  "source_inventory_beyond_two_vap_classes_proven":False,
  "cross_collection_atomicity_proven":False,
  "unbounded_realtime_accept_authorized":False,
  "fully_informed_b9_allowed_to_reuse_all_apis_and_checker":True,
  "independent_b9_superiority_study_scored":False,
  "method_novelty_established":False,
  "scientific_status":verdict["status"],
  "verifier":verdict,
 }

def main():
 p=argparse.ArgumentParser()
 for key in ("source-manifest","source-predictions","native-raw","out"):
  p.add_argument("--"+key,required=True)
 args=p.parse_args()
 manifestbytes=Path(args.source_manifest).read_bytes()
 load=lambda f:json.loads(Path(f).read_text())
 scored=join(json.loads(manifestbytes),load(args.source_predictions),
             load(args.native_raw),manifestbytes)
 Path(args.out).write_text(json.dumps(scored,sort_keys=True,indent=2)+"\n")
 print(json.dumps({k:scored[k] for k in (
  "scientific_status","native_pod_decisions_scored",
  "captured_native_watch_events","captured_native_list_snapshots",
  "real_global_c1_authority_proven","method_novelty_established")},sort_keys=True))

if __name__=="__main__":
 main()
