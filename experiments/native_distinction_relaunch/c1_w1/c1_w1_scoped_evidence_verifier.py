#!/usr/bin/env python3
"""C1-W1 structure/integrity verifier, scoped native transport diagnostic ONLY.

No proof that any unobserved admission source class is absent, no real-time
fence, no cryptographic signature on a LIST. All RVs opaque strings.
"""
import copy, hashlib, json, urllib.parse

CLASSES={
 "policy":{"path":"/apis/admissionregistration.k8s.io/v1/validatingadmissionpolicies",
           "kind":"ValidatingAdmissionPolicyList","item_kind":"ValidatingAdmissionPolicy"},
 "binding":{"path":"/apis/admissionregistration.k8s.io/v1/validatingadmissionpolicybindings",
            "kind":"ValidatingAdmissionPolicyBindingList","item_kind":"ValidatingAdmissionPolicyBinding"},
}
STAGES=("S0_INITIAL","A1_POLICY_ADDED","A2_BINDING_ADDED","A3_BINDING_DELETED")
ORIGINAL_POLICIES=("eeq-r3-flux-deny",)
ORIGINAL_BINDINGS=("eeq-r3-binding-team","eeq-r3-binding-mode")
THIRD_POLICY="eeq-r3-m3-default-deny"
THIRD_BINDING="eeq-r3-m3-binding-third"
EXPECTED={
 "S0_INITIAL":{"policy":ORIGINAL_POLICIES,
               "binding":ORIGINAL_BINDINGS},
 "A1_POLICY_ADDED":{"policy":ORIGINAL_POLICIES+(THIRD_POLICY,),
                    "binding":ORIGINAL_BINDINGS},
 "A2_BINDING_ADDED":{"policy":ORIGINAL_POLICIES+(THIRD_POLICY,),
                     "binding":ORIGINAL_BINDINGS+(THIRD_BINDING,)},
 "A3_BINDING_DELETED":{"policy":ORIGINAL_POLICIES+(THIRD_POLICY,),
                       "binding":ORIGINAL_BINDINGS},
}
EVENT_SPEC=(
 ("A1_POLICY_ADDED","policy","ADDED",THIRD_POLICY),
 ("A2_BINDING_ADDED","binding","ADDED",THIRD_BINDING),
 ("A3_BINDING_DELETED","binding","DELETED",THIRD_BINDING),
)
MUTATIONS=("CREATE_THIRD_POLICY","CREATE_THIRD_BINDING","DELETE_THIRD_BINDING")


class Refuse(Exception):
 def __init__(self,reason):
  self.reason=reason
  super().__init__(reason)

def require(ok,reason):
 if not ok: raise Refuse(reason)

def canonical(x):
 return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def snapshot_items(snapshot,kind):
 require(isinstance(snapshot,dict) and
         snapshot.get("kind")==CLASSES[kind]["kind"] and
         snapshot.get("apiVersion")=="admissionregistration.k8s.io/v1",
         "REFUSE_COLLECTION_SHAPE")
 meta=snapshot.get("metadata")
 require(isinstance(meta,dict) and
         isinstance(meta.get("resourceVersion"),str) and bool(meta["resourceVersion"]),
         "REFUSE_INVENTORY_RV_MISSING")
 require(not meta.get("continue"),"REFUSE_INVENTORY_PAGINATION")
 require(isinstance(snapshot.get("items"),list),
         "REFUSE_INVENTORY_MISSING_ITEMS")
 items={}
 for item in snapshot["items"]:
  require(isinstance(item,dict) and
          item.get("kind")==CLASSES[kind]["item_kind"] and
          isinstance(item.get("metadata"),dict), "REFUSE_COLLECTION_ITEM_SHAPE")
  m=item["metadata"]
  require(all(isinstance(m.get(q),str) and bool(m[q])
              for q in ("name","uid","resourceVersion")),
          "REFUSE_ITEM_IDENTITY")
  require(m["name"] not in items,"REFUSE_DUPLICATE_NATIVE_SOURCE")
  items[m["name"]]=item
 return items


def verify(raw, forecast):
 """Return structural PREFIX status or explicit refusal; no native Pod decisions."""
 try:
  require(isinstance(raw,dict) and raw.get("schema")==
          "eeq-c1-w1-native-list-watch-capture-v1" and
          raw.get("source_predictions_file_read") is False,
          "REFUSE_PROVENANCE_OR_SCHEMA")
  require(isinstance(forecast,dict) and forecast.get("schema")==
          "eeq-c1-w1-source-only-forecast-v1" and
          forecast.get("source_only") is True and
          forecast.get("native_outcomes_read") is False,
          "REFUSE_SOURCE_FORECAST_NOT_SEALED")
  require(raw.get("global_admission_accept_claimed") is False and
          raw.get("cross_class_atomic_snapshot_claimed") is False,
          "REFUSE_OVERCLAIM")
  require(raw.get("requested_contract")=="TWO_VAP_COLLECTIONS_SCOPED_SOURCE_CURSOR",
          "REFUSE_GLOBAL_ACCEPT")
  actor=raw.get("actor")
  require(isinstance(actor,dict) and isinstance(actor.get("context"),str)
          and bool(actor["context"]),"REFUSE_ACTOR_IDENTITY")
  rights=actor.get("authorized_native_permissions")
  require(isinstance(rights,dict) and set(rights)==set(CLASSES) and
          all(rights[k]=={"list":True,"watch":True} for k in CLASSES),
          "REFUSE_AUTHORITY")
  lists=raw.get("checkpoints")
  require(isinstance(lists,list) and len(lists)==4,
          "REFUSE_INVENTORY_DENOMINATOR")
  snapshots={}
  for phase,check in zip(STAGES,lists):
   require(check.get("step")==phase,"REFUSE_CHECKPOINT_PHASE")
   collections=check.get("collections")
   require(isinstance(collections,dict) and set(collections)==set(CLASSES),
           "REFUSE_MONITORED_SOURCE_CLASSES")
   snapshots[phase]={}
   for kind,rec in collections.items():
    require(isinstance(rec,dict) and rec.get("request_path")==CLASSES[kind]["path"]
            and rec.get("selector")=="" and rec.get("limit") is None,
            "REFUSE_SCOPE")
    objects=snapshot_items(rec.get("response"),kind)
    require(set(objects)==set(EXPECTED[phase][kind]),
            "REFUSE_MEMBERSHIP_DIFF_FROM_FROZEN_TRACE")
    snapshots[phase][kind]=objects

  # Confirm intact original source identities, UIDs and specs across phases.
  for kind,names in (("policy",ORIGINAL_POLICIES),("binding",ORIGINAL_BINDINGS)):
   for name in names:
    initial=snapshots["S0_INITIAL"][kind][name]
    for phase in STAGES[1:]:
     current=snapshots[phase][kind][name]
     require(initial["metadata"]["uid"]==current["metadata"]["uid"]
             and canonical(initial.get("spec"))==canonical(current.get("spec")),
             "REFUSE_ORIGINAL_SOURCE_MUTATED")
  source_base=lists[0]["collections"]
  watches=raw.get("watches")
  require(isinstance(watches,dict) and set(watches)==set(CLASSES),
          "REFUSE_UNMONITORED_SOURCE_CLASS")
  for kind,watch in watches.items():
   require(isinstance(watch,dict) and
           watch.get("request_path")==CLASSES[kind]["path"] and
           watch.get("resourceVersion")==
                 source_base[kind]["response"]["metadata"]["resourceVersion"],
           "REFUSE_LIST_WATCH_CURSOR_MISMATCH")
   query=urllib.parse.parse_qs(watch.get("request_query",""),strict_parsing=True)
   require(query=={
      "watch":["1"],
      "resourceVersion":[watch.get("resourceVersion")],
      "allowWatchBookmarks":["true"],
      "timeoutSeconds":["150"],
   }, "REFUSE_WATCH_NOT_BEGUN_AT_PINNED_CURSOR")
   if watch.get("status")=="UNSYNCED":
    raise Refuse("REFUSE_CROSS_CLASS")
   require(watch.get("status")=="STOPPED_AFTER_REGISTERED_EVENTS"
           and watch.get("error") is None and
           watch.get("used_allow_watch_bookmarks") is True,
           "RESYNC_REQUIRED")
  events=raw.get("watch_events")
  require(isinstance(events,list) and len(events)==3,
          "REFUSE_WATCH_EVENT_DENOMINATOR")
  for row,(phase,kind,evt_type,name) in zip(events,EVENT_SPEC):
   require(row.get("step")==phase and row.get("source_class")==kind,
           "REFUSE_WATCH_CLASS_OR_PHASE")
   require(row.get("received_source")=="genuine_http_watch_stream_via_kubectl_proxy",
           "REFUSE_WATCH_TRANSPORT_PROVENANCE_UNRECOGNIZED")
   event=row.get("event")
   require(isinstance(event,dict) and event.get("type")==evt_type and
           isinstance(event.get("object"),dict),
           "REFUSE_WATCH_EVENT_TYPE")
   obj=event["object"]
   require(obj.get("kind")==CLASSES[kind]["item_kind"],
           "REFUSE_WATCH_EVENT_KIND")
   m=obj.get("metadata")
   require(isinstance(m,dict) and
           all(isinstance(m.get(q),str) and bool(m[q]) for q in
               ("uid","resourceVersion","name")) and m["name"]==name,
           "REFUSE_WATCH_EVENT_INTEGRITY")
   observed=(snapshots["A2_BINDING_ADDED"]["binding"][name]
             if evt_type=="DELETED" else snapshots[phase][kind][name])
   require(m["uid"]==observed["metadata"]["uid"] and
           (evt_type=="DELETED" or
            canonical(obj.get("spec"))==canonical(observed.get("spec"))),
           "REFUSE_WATCH_LIST_OBJECT_IDENTITY_MISMATCH")
  mutation=raw.get("mutations")
  require(isinstance(mutation,list) and len(mutation)==3,
          "REFUSE_NATIVE_ACTION_DENOMINATOR")
  for row,action in zip(mutation,MUTATIONS):
   require(row.get("action")==action and
           row.get("exit_code")==0 and
           row.get("native_mutation_registered") is True,
           "REFUSE_NATIVE_MUTATION_FAILED")
  require(raw.get("native_pod_decision_calls")==0,
          "REFUSE_UNREGISTERED_NATIVE_DECISION_SCORING")
  return {
   "status":"C1_W1_SCOPED_NATIVE_LIST_WATCH_FEASIBILITY_B9_TIE",
   "watch_event_matched":3,"watch_events_registered":3,
   "source_class_snapshots_matched":8,"snapshots_registered":8,
   "watch_channels":2,"native_source_mutations":3,
   "prefix_reconstruction":"PREFIX_WITNESSED",
   "old_two_binding_accept_at_A2":"OLD_TWO_SOURCE_ACCEPT_INVALIDATED",
   "A3_scoped_restore":"CONDITIONAL_SCOPED_REATTESTATION_ONLY",
   "global_admission_accept_certified":False,
   "cross_resource_atomicity_certified":False,
   "unobserved_admission_mechanisms_excluded":False,
   "unbounded_current_freshness_certified":False,
   "p3_h3_b9_superiority_established":False,
   "fully_informed_b9_can_reproduce":True,
   "new_v1_g5_cases":0
  }
 except Refuse as e:
  return {"status":e.reason,"reason":e.reason,"watch_event_matched":None,
          "global_admission_accept_certified":False,
          "new_v1_g5_cases":0,
          "p3_h3_b9_superiority_established":False}
 except (KeyError,TypeError,AttributeError,IndexError,ValueError) as e:
  return {"status":"REFUSE_MALFORMED_CAPTURE","reason":type(e).__name__,
          "global_admission_accept_certified":False,"new_v1_g5_cases":0,
          "p3_h3_b9_superiority_established":False}

def relist_after_gap(fresh_collections, actor_authorized, requested_scope):
 """Synthetic-only semantics: relist restores a scoped historical snapshot, NOT continuity."""
 try:
  require(requested_scope=="TWO_VAP_COLLECTIONS_SCOPED_SOURCE_CURSOR",
          "REFUSE_GLOBAL_ACCEPT")
  require(actor_authorized is True,"REFUSE_AUTHORITY")
  require(isinstance(fresh_collections,dict) and set(fresh_collections)==set(CLASSES),
          "REFUSE_MONITORED_SOURCE_CLASSES")
  for kind,rec in fresh_collections.items():
   require(rec.get("request_path")==CLASSES[kind]["path"] and
           not rec.get("selector") and rec.get("limit") is None,
           "REFUSE_SCOPE")
   snapshot_items(rec["response"],kind)
  return {
   "status":"CONDITIONAL_SCOPED_REATTESTATION_ONLY",
   "prior_watch_gap_retroactively_repaired":False,
   "cross_kind_atomicity_proven":False,
   "global_current_accept_authorized":False,
  }
 except Refuse as e:
  return {"status":e.reason,"global_current_accept_authorized":False}
 except (KeyError,TypeError,AttributeError) as e:
  return {"status":"REFUSE_MALFORMED_CAPTURE","global_current_accept_authorized":False}
