#!/usr/bin/env python3
"""V2 READ ONLY post-native forensic inspection of original W1 raw API evidence.

Cannot emit a repaired verdict. Never calls kubectl or writes source JSONs.
"""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path

def hashbytes(raw):
 return hashlib.sha256(raw).hexdigest()

def inspect(raw,source_bytes_sha,archived_hash_text):
 archived_lines={}
 for line in archived_hash_text.splitlines():
  parts=line.split()
  if len(parts)==2:
   archived_lines[parts[1].split("/")[-1]]=parts[0]
 evidence_name="C1_W1_RAW_NATIVE_HTTP_WATCH.json"
 if archived_lines.get(evidence_name)!=source_bytes_sha:
  raise ValueError("ORIGINAL_NATIVE_SOURCE_RAW_SHA256_MISMATCH")
 if raw.get("schema")!="eeq-c1-w1-native-list-watch-capture-v1":
  raise ValueError("ORIGINAL_NATIVE_CAPTURE_SCHEMA_MISMATCH")
 snapshots=raw.get("checkpoints",[])
 events=raw.get("watch_events",[])
 reports=[]
 missing=Counter()
 wrong=[]
 for i,phase in enumerate(snapshots):
  for source_class in ("policy","binding"):
   record=phase["collections"][source_class]
   response=record["response"]
   kind=response.get("kind")
   expected_kind=("ValidatingAdmissionPolicyList" if source_class=="policy"
                  else "ValidatingAdmissionPolicyBindingList")
   if kind!=expected_kind:
    wrong.append({"phase":i,"source_class":source_class,
                  "unexpected_collection_kind":kind})
   for item in response.get("items",[]):
    meta=item.get("metadata",{})
    rec={
       "phase_index":i,"step":phase.get("step"),
       "source_class":source_class,
       "collection_kind":kind,
       "collection_api_version":response.get("apiVersion"),
       "collection_rv_present":bool(response.get("metadata",{}).get("resourceVersion")),
       "collection_continue":response.get("metadata",{}).get("continue",""),
       "item_name":meta.get("name"),
       "item_kind":item.get("kind","<ABSENT>"),
       "item_api_version":item.get("apiVersion","<ABSENT>"),
       "has_item_uid":bool(meta.get("uid")),
       "has_item_resource_version":bool(meta.get("resourceVersion")),
       "has_item_spec":isinstance(item.get("spec"),dict),
       "item_top_keys":sorted(item),
    }
    for field in ("kind","apiVersion"):
     if field not in item:missing[field]+=1
    if not all((rec["item_name"],rec["has_item_uid"],
                rec["has_item_resource_version"],rec["has_item_spec"])):
     wrong.append({"phase":i,"source_class":source_class,
                   "missing_required_item_identity_or_spec":rec["item_name"]})
    reports.append(rec)
 ev_report=[]
 for e in events:
  obj=e.get("event",{}).get("object",{})
  meta=obj.get("metadata",{})
  ev_report.append({
   "source_class":e.get("source_class"),"step":e.get("step"),
   "event_type":e.get("event",{}).get("type"),
   "item_name":meta.get("name"),
   "item_kind":obj.get("kind","<ABSENT>"),
   "item_api_version":obj.get("apiVersion","<ABSENT>"),
   "has_uid":bool(meta.get("uid")),
   "has_object_rv":bool(meta.get("resourceVersion")),
   "has_spec":isinstance(obj.get("spec"),dict),
  })
 return {
  "schema":"eeq-c1-w1-v2-postnative-readonly-shape-forensics-v1",
  "forensic_evidence_class":"POSTNATIVE_RAW_NATIVE_INSPECTION_NO_REPAIR",
  "first_original_workflow_run":38029036440,
  "first_original_workflow_science_gate":"FAILURE_REFUSE_COLLECTION_ITEM_SHAPE",
  "first_original_workflow_remains_failure":True,
  "verified_original_native_raw_sha256":source_bytes_sha,
  "raw_native_error_count":len(raw.get("native_errors",[])),
  "watch_channels_reported":len(raw.get("watches",{})),
  "watch_event_count":len(events),
  "native_source_list_checkpoint_count":len(snapshots),
  "raw_collection_list_count":2*len(snapshots),
  "native_source_mutation_count":len(raw.get("mutations",[])),
  "native_pod_decisions_scored":0,
  "original_G5_increment":0,
  "collection_item_count":len(reports),
  "missing_native_item_fields":dict(sorted(missing.items())),
  "unexpected_collection_or_source_identity":wrong,
  "per_item_shape":reports,
  "per_watch_event_shape":ev_report,
  "global_c1_established":False,
  "B9_independent_superiority_established":False,
  "science_disposition":"READONLY_POSTNATIVE_FORENSIC_ONLY",
 }

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--native",required=True)
 p.add_argument("--native-hash",required=True)
 p.add_argument("--out",required=True)
 a=p.parse_args()
 rawbytes=Path(a.native).read_bytes()
 doc=json.loads(rawbytes)
 forensic=inspect(doc,hashbytes(rawbytes),Path(a.native_hash).read_text())
 Path(a.out).write_text(json.dumps(forensic,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:forensic[k] for k in (
  "watch_event_count","raw_collection_list_count",
  "collection_item_count","missing_native_item_fields",
  "unexpected_collection_or_source_identity",
  "science_disposition")},sort_keys=True))

if __name__=="__main__":
 main()
