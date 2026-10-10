#!/usr/bin/env python3
"""C1 W1 V2b POST-NATIVE TypeMeta-only COPY; never changes original raw evidence.

Exactly 16 missing item.kind and 16 missing item.apiVersion may be inferred
from the fully identified enclosing native Kubernetes LIST source class.
No other native or watch bytes/values are amended.
"""
import argparse,copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from c1_w1_scoped_evidence_verifier import CLASSES,STAGES,EXPECTED

class RefuseNativeShape(Exception):
 pass

def require(x,s):
 if not x:raise RefuseNativeShape(s)

def clean(raw):
 require(isinstance(raw,dict) and
         raw.get("schema")=="eeq-c1-w1-native-list-watch-capture-v1",
         "REFUSE_RAW_SCHEMA")
 checkpoints=raw.get("checkpoints")
 require(isinstance(checkpoints,list) and len(checkpoints)==4,
         "REFUSE_NATIVE_LIST_DENOMINATOR")
 candidate=copy.deepcopy(raw)
 added=[]
 originals=checkpoints
 for i,(old_phase,new_phase) in enumerate(zip(originals,candidate["checkpoints"])):
  phase=STAGES[i]
  require(old_phase.get("step")==phase and new_phase.get("step")==phase,
          "REFUSE_LIST_PHASE")
  cols=old_phase.get("collections")
  require(isinstance(cols,dict) and set(cols)==set(CLASSES),
          "REFUSE_LIST_SOURCE_CLASS")
  for kind in ("policy","binding"):
   old_rec=cols[kind]
   new_rec=new_phase["collections"][kind]
   require(old_rec.get("request_path")==CLASSES[kind]["path"] and
           old_rec.get("selector")=="" and old_rec.get("limit") is None,
           "REFUSE_LIST_SCOPE")
   src=old_rec.get("response")
   dst=new_rec.get("response")
   require(isinstance(src,dict) and
           src.get("kind")==CLASSES[kind]["kind"] and
           src.get("apiVersion")=="admissionregistration.k8s.io/v1" and
           isinstance(src.get("metadata"),dict) and
           isinstance(src["metadata"].get("resourceVersion"),str) and
           bool(src["metadata"]["resourceVersion"]) and
           not src["metadata"].get("continue"),
           "REFUSE_COLLECTION_TYPE_OR_COMPLETENESS")
   items=src.get("items")
   require(isinstance(items,list),"REFUSE_LIST_ITEMS_MISSING")
   ids=set()
   for j,original in enumerate(items):
    require(isinstance(original,dict) and isinstance(original.get("metadata"),dict),
            "REFUSE_RAW_ITEM_SHAPE")
    m=original["metadata"]
    require(all(isinstance(m.get(q),str) and bool(m[q])
                for q in ("name","uid","resourceVersion"))
            and isinstance(original.get("spec"),dict),
            "REFUSE_NATIVE_ITEM_IDENTITY_OR_SPEC")
    require(m["name"] not in ids,"REFUSE_DUPLICATE_MEMBER_ID")
    ids.add(m["name"])
    # V2B matches the measured original native shape EXACTLY. If a field
    # was present, even correct, this version is not authorized to edit it.
    require("kind" not in original and "apiVersion" not in original,
            "REFUSE_NATIVE_TYPEMETA_NOT_ABSENT_AS_FORENSIC_FREEZE")
    repaired=dst["items"][j]
    repaired["kind"]=CLASSES[kind]["item_kind"]
    repaired["apiVersion"]="admissionregistration.k8s.io/v1"
    added.append({"phase":phase,"source_class":kind,
                  "item_name":m["name"],"fields":["kind","apiVersion"]})
   require(ids==set(EXPECTED[phase][kind]),
           "REFUSE_NATIVE_SOURCE_INVENTORY_OUT_OF_FROZEN_SCOPE")
 require(len(added)==16,"REFUSE_NATIVE_ITEM_COUNT_NOT_16")
 # The only changes anywhere must be 2 extra TypeMeta keys per LIST item.
 restored=copy.deepcopy(candidate)
 for i in range(4):
  for kind in ("policy","binding"):
   for item in restored["checkpoints"][i]["collections"][kind]["response"]["items"]:
    del item["kind"]
    del item["apiVersion"]
 require(restored==raw,"REFUSE_ANY_OTHER_NORMALIZATION_OR_PROVENANCE_EDIT")
 return candidate,{
  "normalization_schema":"eeq-c1-w1-v2b-readonly-copy-typemeta-only-v1",
  "original_native_raw_unchanged":True,
  "native_list_items_typed_on_new_copy":16,
  "added_absent_item_typemeta_fields":32,
  "watch_events_changed":0,
  "native_actions_changed":0,
  "original_V1_native_workflow_scientific_status":"FAILURE",
  "result_evidence_class":"RETROSPECTIVE_POSTNATIVE_SHAPE_CALIBRATION",
  "global_c1_proven":False,"B9_independent_value":False,
  "typed_members":added,
 }

def dump(original,copy_file,audit_file):
 raw=Path(original).read_bytes()
 norm,report=clean(json.loads(raw))
 report["original_native_raw_sha256"]=hashlib.sha256(raw).hexdigest()
 output=json.dumps(norm,sort_keys=True,indent=2)+"\n"
 Path(copy_file).write_text(output,encoding="utf-8")
 report["new_copy_sha256"]=hashlib.sha256(output.encode()).hexdigest()
 Path(audit_file).write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
 print(json.dumps({k:report[k] for k in (
  "native_list_items_typed_on_new_copy",
  "added_absent_item_typemeta_fields","watch_events_changed",
  "original_V1_native_workflow_scientific_status",
  "result_evidence_class")},sort_keys=True))

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--original",required=True)
 p.add_argument("--copy",required=True)
 p.add_argument("--audit",required=True)
 a=p.parse_args()
 dump(a.original,a.copy,a.audit)
