#!/usr/bin/env python3
"""C1-W1 NATIVE ONLY Kubernetes List->Watch cursor capture via kubectl proxy.

No source predictions, no original scored R3-M3 artifact, no Pod decisions.
Starts two REAL native Kubernetes HTTP watches from two opaque RAW LIST
collection resourceVersions. All failures/partial evidence retained.
"""
import argparse,hashlib,json,queue,subprocess,threading,time,urllib.parse,urllib.request
from pathlib import Path

POLICY_API="/apis/admissionregistration.k8s.io/v1/validatingadmissionpolicies"
BINDING_API="/apis/admissionregistration.k8s.io/v1/validatingadmissionpolicybindings"
CLASSES={"policy":POLICY_API,"binding":BINDING_API}
EXPECTED_EVENTS=(
 ("A1_POLICY_ADDED","policy","ADDED","eeq-r3-m3-default-deny"),
 ("A2_BINDING_ADDED","binding","ADDED","eeq-r3-m3-binding-third"),
 ("A3_BINDING_DELETED","binding","DELETED","eeq-r3-m3-binding-third"),
)
STEPS=(
 ("CREATE_THIRD_POLICY","policy-third.json",True),
 ("CREATE_THIRD_BINDING","binding-third.json",True),
 ("DELETE_THIRD_BINDING","binding-third.json",False),
)
BASE=Path(__file__).resolve().parents[1]
SOURCE_PATHS={
 "namespace":"r3_m1/sources/namespace.json",
 "policy":"r3_m1/sources/policy.json",
 "team":"r3_m1/sources/binding-team.json",
 "mode":"r3_m1/sources/binding-mode.json",
 "third_policy":"r3_m3/sources/policy-third.json",
 "third_binding":"r3_m3/sources/binding-third.json",
}
PINS={
 "namespace":"428f16bc92ac27dec26b87ad24951113cf463922",
 "policy":"c22a8134447649d202a49b644ddb8485835c0fc2",
 "team":"2bc5a5706910196c5cd0631c4034ca3ccdbb890b",
 "mode":"357ef4bd582f47e2308f6e640307077bafe47b68",
 "third_policy":"ae7ab92b2d15f7793ec41232752efc2c30ebf347",
 "third_binding":"e2a774ee92c2af6411e1a516e48af4695f096088",
}


def execute(command,check=True):
 start=time.perf_counter_ns()
 x=subprocess.run(command,capture_output=True,text=True,timeout=180)
 row={"command":command,"exit_code":x.returncode,
      "stdout":x.stdout,"stderr":x.stderr,
      "elapsed_ns":time.perf_counter_ns()-start}
 if check and x.returncode:
  raise RuntimeError("NATIVE_INFRA_COMMAND_FAILED:"+json.dumps(row))
 return row


def kubectl(*args,check=True):
 return execute(["kubectl",*args],check=check)


def pinned_sources():
 out={}
 for key,rel in SOURCE_PATHS.items():
  file=BASE/rel
  raw=file.read_bytes()
  blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
  if blob!=PINS[key]:
   raise RuntimeError("NATIVE_ORIGINAL_SOURCE_PIN_CHANGED:"+key)
  out[key]=file
 return out


def list_raw(kind):
 path=CLASSES[kind]
 response=kubectl("get","--raw",path)
 try:
  doc=json.loads(response["stdout"])
 except ValueError as exc:
  raise RuntimeError("NATIVE_RAW_LIST_JSON_ERROR:"+kind) from exc
 expect="ValidatingAdmissionPolicyList" if kind=="policy" else "ValidatingAdmissionPolicyBindingList"
 if (doc.get("kind")!=expect or
     doc.get("apiVersion")!="admissionregistration.k8s.io/v1" or
     not isinstance(doc.get("items"),list) or
     not doc.get("metadata",{}).get("resourceVersion") or
     doc["metadata"].get("continue")):
  raise RuntimeError("NATIVE_UNSCOPED_OR_INCOMPLETE_LIST:"+kind)
 return {"request_path":path,"selector":"","limit":None,"response":doc,
         "transport":"kubectl_get_raw_unfiltered_native_api"}


def checkpoint(step):
 return {"step":step,"collections":{c:list_raw(c) for c in ("policy","binding")}}


def permission_probe():
 result={}
 for cls,name in (("policy","validatingadmissionpolicies.admissionregistration.k8s.io"),
                  ("binding","validatingadmissionpolicybindings.admissionregistration.k8s.io")):
  verbs={}
  for verb in ("list","watch"):
   r=kubectl("auth","can-i",verb,name,check=False)
   verbs[verb]=(r["exit_code"]==0 and r["stdout"].strip().lower()=="yes")
  result[cls]=verbs
 return result


class HTTPWatch:
 def __init__(self,source_class,collection_rv):
  self.cls=source_class
  self.rv=collection_rv
  self.params=urllib.parse.urlencode({
   "watch":"1","resourceVersion":collection_rv,
   "allowWatchBookmarks":"true","timeoutSeconds":"150"})
  self.url="http://127.0.0.1:8001"+CLASSES[source_class]+"?"+self.params
  self.ready=threading.Event()
  self.queue=queue.Queue()
  self.all=[]
  self.fault=None
  self.expected_stop=False
  self.ended=False
  self.resp=None
  self.thread=threading.Thread(target=self._read,daemon=True)

 def start(self): self.thread.start()

 def _read(self):
  try:
   req=urllib.request.Request(self.url,headers={"Accept":"application/json"})
   with urllib.request.urlopen(req,timeout=160) as resp:
    self.resp=resp
    if resp.status!=200:
     self.fault="WATCH_HTTP_STATUS_"+str(resp.status)
     self.ready.set()
     return
    self.ready.set()
    for line in resp:
     if self.expected_stop:break
     if not line.strip():continue
     try:
      obj=json.loads(line)
     except ValueError:
      self.fault="NATIVE_WATCH_INVALID_JSON_LINE"
      self.queue.put(("FAULT",self.fault))
      break
     self.all.append(obj)
     self.queue.put(("EVENT",obj))
  except Exception as exc:
   if not self.expected_stop:
    self.fault=type(exc).__name__+":"+str(exc)[:400]
    self.queue.put(("FAULT",self.fault))
   self.ready.set()
  finally:
   self.ended=True

 def expected(self,etype,name,deadline_seconds=12):
  deadline=time.monotonic()+deadline_seconds
  while time.monotonic()<deadline:
   if self.fault:
    raise RuntimeError("NATIVE_WATCH_FAILURE:"+self.cls+":"+self.fault)
   try:
    k,obj=self.queue.get(timeout=min(0.5,max(0.01,deadline-time.monotonic())))
   except queue.Empty:
    if self.ended:
     raise RuntimeError("NATIVE_WATCH_EARLY_CLOSED:"+self.cls)
    continue
   if k=="FAULT":raise RuntimeError("NATIVE_WATCH_FAILURE:"+str(obj))
   if obj.get("type")=="BOOKMARK":
    continue
   if obj.get("type")=="ERROR":
    raise RuntimeError("NATIVE_WATCH_ERROR_EVENT:"+json.dumps(obj)[:1200])
   if obj.get("type")!=etype:
    raise RuntimeError("UNREGISTERED_WATCH_EVENT_TYPE:"+json.dumps(obj)[:1200])
   item=obj.get("object",{})
   meta=item.get("metadata",{})
   if meta.get("name")!=name or not meta.get("uid") or not meta.get("resourceVersion"):
    raise RuntimeError("UNREGISTERED_WATCH_EVENT_IDENTITY:"+json.dumps(obj)[:1200])
   return obj
  raise RuntimeError("NATIVE_WATCH_DEADLINE_EXPIRED:"+self.cls+":"+etype+":"+name)

 def close(self):
  self.expected_stop=True
  if self.resp is not None:
   try:self.resp.close()
   except Exception:pass

 def metadata(self,successful):
  return {
   "request_path":CLASSES[self.cls],
   "resourceVersion":self.rv,
   "status":("STOPPED_AFTER_REGISTERED_EVENTS" if successful and not self.fault
             else "NATIVE_WATCH_CAPTURE_FAILED"),
   "error":self.fault,
   "used_allow_watch_bookmarks":True,
   "request_query":self.params,
   "http_watch_connected":self.ready.is_set(),
   "raw_wire_events_seen":len(self.all),
   "bookmarks_seen":sum(x.get("type")=="BOOKMARK" for x in self.all),
  }


def run():
 src=pinned_sources()
 context=kubectl("config","current-context")["stdout"].strip()
 data={
  "schema":"eeq-c1-w1-native-list-watch-capture-v1",
  "requested_contract":"TWO_VAP_COLLECTIONS_SCOPED_SOURCE_CURSOR",
  "source_predictions_file_read":False,
  "actor":{"context":context,"authorized_native_permissions":{}},
  "checkpoints":[],"watch_events":[],"watches":{},
  "mutations":[],"native_pod_decision_calls":0,
  "global_admission_accept_claimed":False,
  "cross_class_atomic_snapshot_claimed":False,
  "native_errors":[],"source_git_blob_pins_verified":True,
 }
 watchers={}
 proxy=None
 try:
  if not context.startswith("kind-eeq-c1-w1"):
   raise RuntimeError("NATIVE_NOT_EXPECTED_FRESH_KIND_CONTEXT:"+context)
  kubectl("apply","-f",str(src["namespace"]))
  for key in ("policy","team","mode"):
   kubectl("apply","-f",str(src[key]))
  time.sleep(10.0)
  data["actor"]["authorized_native_permissions"]=permission_probe()
  if any(not data["actor"]["authorized_native_permissions"][k][v]
        for k in CLASSES for v in ("list","watch")):
   raise RuntimeError("NATIVE_ACTOR_LIST_WATCH_AUTHORIZATION_MISSING")
  first=checkpoint("S0_INITIAL")
  data["checkpoints"].append(first)
  proxy=subprocess.Popen(["kubectl","proxy","--port=8001","--address=127.0.0.1"],
                         stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                         text=True)
  time.sleep(1.0)  # frozen single proxy bootstrap, no retry
  if proxy.poll() is not None:
   raise RuntimeError("NATIVE_KUBECTL_PROXY_EXITED_EARLY")
  for cls in ("policy","binding"):
   rv=first["collections"][cls]["response"]["metadata"]["resourceVersion"]
   watchers[cls]=HTTPWatch(cls,rv)
   watchers[cls].start()
  if not all(w.ready.wait(5.0) and not w.fault for w in watchers.values()):
   raise RuntimeError("NATIVE_WATCH_CONNECT_NOT_ESTABLISHED")
  time.sleep(2.0)
  for i,(action,source_key,apply) in enumerate(STEPS):
   expected_step,cls,etype,name=EXPECTED_EVENTS[i]
   source_file=src["third_policy" if source_key=="policy-third.json" else "third_binding"]
   if apply:
    mutation=kubectl("apply","-f",str(source_file),check=False)
   else:
    mutation=kubectl("delete","-f",str(source_file),check=False)
   data["mutations"].append({
    "action":action,**mutation,
    "native_mutation_registered":mutation["exit_code"]==0,
   })
   if mutation["exit_code"]!=0:
    raise RuntimeError("NATIVE_REGISTERED_MUTATION_FAILED:"+action)
   time.sleep(6.0)
   event=watchers[cls].expected(etype,name,deadline_seconds=12)
   data["watch_events"].append({
    "step":expected_step,"source_class":cls,
    "event":event,"received_source":"genuine_http_watch_stream_via_kubectl_proxy",
   })
   data["checkpoints"].append(checkpoint(expected_step))
  if any(w.fault or w.ended for w in watchers.values()):
   raise RuntimeError("NATIVE_WATCH_DISCONNECTED_BEFORE_COMPLETE_EVIDENCE")
 except Exception as exc:
  data["native_errors"].append(type(exc).__name__+":"+str(exc))
 finally:
  complete=(not data["native_errors"] and len(data["mutations"])==3 and
            len(data["watch_events"])==3 and len(data["checkpoints"])==4)
  for kind,w in watchers.items():
   data["watches"][kind]=w.metadata(complete)
   w.close()
  if proxy is not None:
   proxy.terminate()
   try:proxy.wait(timeout=5)
   except subprocess.TimeoutExpired:proxy.kill()
  data["registered_main_native_watch_events"]=3
  data["registered_full_source_list_snapshots"]=8
  data["registered_independent_watch_channels"]=2
  data["registered_native_source_mutations"]=3
  data["observed_native_watch_events"]=len(data["watch_events"])
  data["observed_source_list_snapshots"]=2*len(data["checkpoints"])
  data["observed_native_source_mutations"]=len(data["mutations"])
  data["native_validated_scored_pod_decisions"]=0
  data["historical_g5_new_cases"]=0
 return data


def main():
 p=argparse.ArgumentParser()
 p.add_argument("--out",required=True)
 args=p.parse_args()
 data=run()
 Path(args.out).write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
 print(json.dumps({
  "captured_events":data["observed_native_watch_events"],
  "full_list_snapshots":data["observed_source_list_snapshots"],
  "native_actions":data["observed_native_source_mutations"],
  "watches":{k:v["status"] for k,v in data["watches"].items()},
  "native_errors":data["native_errors"],
  "new_pod_scoring":0,"g5_increment":0
 },sort_keys=True))
 if data["native_errors"]:
  raise SystemExit("C1_W1_RAW_NATIVE_ERROR_RETAINED_NO_POSTHOC_RESCUE")


if __name__=="__main__":
 main()
