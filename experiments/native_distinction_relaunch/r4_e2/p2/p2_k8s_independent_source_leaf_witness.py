#!/usr/bin/env python3
"""P2 *independent* Kubernetes raw-source semantic leaf witness builder.

No imports from E2 rule compiler, E2 direct B9, archived native labels or
score. This is deliberately an independent domain-limited checker of the
registered source grammar, NOT a live Kubernetes policy evaluator.
"""
import hashlib,json,re
from pathlib import Path

SRC=Path(__file__).resolve().parents[2]
PIN={
 "namespace":("r3_m1/sources/namespace.json","428f16bc92ac27dec26b87ad24951113cf463922"),
 "flux_policy":("r3_m1/sources/policy.json","c22a8134447649d202a49b644ddb8485835c0fc2"),
 "team_binding":("r3_m1/sources/binding-team.json","2bc5a5706910196c5cd0631c4034ca3ccdbb890b"),
 "mode_binding":("r3_m1/sources/binding-mode.json","357ef4bd582f47e2308f6e640307077bafe47b68"),
 "third_policy":("r3_m3/sources/policy-third.json","ae7ab92b2d15f7793ec41232752efc2c30ebf347"),
 "third_binding":("r3_m3/sources/binding-third.json","e2a774ee92c2af6411e1a516e48af4695f096088"),
 "flux_pod":("r3_m1/sources/pod-flux.json","def429a28e90544d9f2274101b97950801e8d924"),
 "default_pod":("r3_m1/sources/pod-default.json","9f82b811c2c6154ed20e1145f926be1d45f2c1fc"),
}
PHASES=[
 ("S0_INITIAL",("team_binding","mode_binding"),("flux_policy",)),
 ("A1_POLICY_ADDED",("team_binding","mode_binding"),("flux_policy","third_policy")),
 ("A2_BINDING_ADDED",("team_binding","mode_binding","third_binding"),("flux_policy","third_policy")),
 ("A3_BINDING_DELETED",("team_binding","mode_binding"),("flux_policy","third_policy"))
]
CEL=re.compile(r"object\.spec\.serviceAccountName != '([a-z][a-z0-9_-]*)'\Z")
MATCH_RULES={"resourceRules":[{"apiGroups":[""],"apiVersions":["v1"],"operations":["CREATE"],"resources":["pods"]}]}

def fail(why):raise ValueError("P2_K8S_"+why)
def blob(raw):return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(x,reason):
 if not x:fail(reason)

def original():
 docs={}
 for name,(path,expected_blob) in PIN.items():
  raw=(SRC/path).read_bytes()
  require(blob(raw)==expected_blob,"REGISTERED_RAW_SOURCE_CHANGED_"+name)
  docs[name]={"data":json.loads(raw),"digest":sha(raw)}
 return docs

def checkgrammar(d):
 require(set(d)==set(PIN),"ACTOR_REGISTRY_MISSING_SOURCE")
 namespace=d["namespace"]["data"]
 require(namespace.get("kind")=="Namespace" and
         namespace.get("metadata",{}).get("name")=="eeq-r3" and
         isinstance(namespace["metadata"].get("labels"),dict),
         "NAMESPACE_SHAPE_OR_AUTHORITY_UNSUPPORTED")
 for pod in ("flux","default"):
  obj=d[pod+"_pod"]["data"]
  require(obj.get("kind")=="Pod" and
          obj.get("metadata",{}).get("namespace")=="eeq-r3" and
          obj.get("spec",{}).get("serviceAccountName")==pod,
          "UNEXPECTED_NATIVE_POD_SOURCE")
 policies={}
 for key in ("flux_policy","third_policy"):
  obj=d[key]["data"]
  s=obj.get("spec",{})
  require(obj.get("kind")=="ValidatingAdmissionPolicy" and
          obj.get("apiVersion")=="admissionregistration.k8s.io/v1" and
          set(s)=={"failurePolicy","matchConstraints","validations"} and
          s["failurePolicy"]=="Fail" and
          s["matchConstraints"]==MATCH_RULES and
          isinstance(s["validations"],list) and len(s["validations"])==1 and
          isinstance(s["validations"][0],dict) and
          set(s["validations"][0])=={"expression","message","reason"} and
          s["validations"][0]["reason"]=="Forbidden",
          "POLICY_GRAMMAR_UNSUPPORTED")
  expr=s["validations"][0]["expression"]
  match=CEL.fullmatch(expr) if isinstance(expr,str) else None
  require(match is not None,"UNREGISTERED_POLICY_CEL")
  name=obj.get("metadata",{}).get("name")
  require(isinstance(name,str) and name and name not in policies,
          "POLICY_DUPLICATE_OR_MISSING_NATIVE_IDENTITY")
  policies[name]={"key":key,"rejected_sa":match.group(1)}
 bindings={}
 for key in ("team_binding","mode_binding","third_binding"):
  obj=d[key]["data"]
  s=obj.get("spec",{})
  require(obj.get("kind")=="ValidatingAdmissionPolicyBinding" and
          obj.get("apiVersion")=="admissionregistration.k8s.io/v1" and
          set(s)=={"policyName","validationActions","matchResources"} and
          s["policyName"] in policies and s["validationActions"]==["Deny"] and
          isinstance(s["matchResources"],dict) and
          set(s["matchResources"])=={"namespaceSelector"} and
          isinstance(s["matchResources"]["namespaceSelector"],dict) and
          set(s["matchResources"]["namespaceSelector"])=={"matchLabels"},
          "BINDING_SEMANTIC_GRAMMAR_UNSUPPORTED")
  labels=s["matchResources"]["namespaceSelector"]["matchLabels"]
  require(isinstance(labels,dict) and bool(labels) and
          all(isinstance(k,str) and bool(k) and isinstance(v,str) and bool(v)
              for k,v in labels.items()),"BINDING_MATCHLABELS_UNSUPPORTED")
  name=obj.get("metadata",{}).get("name")
  require(isinstance(name,str) and name and name not in bindings,
          "BINDING_DUPLICATE_OR_MISSING_NATIVE_IDENTITY")
  bindings[name]={"key":key,"selector":labels,"policy_name":s["policyName"]}
 return policies,bindings

def leaf(id_,value,refs,obligation):
 return {"op":"ATOM","id":id_,"value":value,"source_refs":refs,
         "obligation":obligation}

def build():
 d=original()
 policies,bindings=checkgrammar(d)
 result=[]
 namespace=d["namespace"]["data"]["metadata"]["labels"]
 for phase,active,installed in PHASES:
  installed_names={d[k]["data"]["metadata"]["name"] for k in installed}
  for probe in ("flux","default"):
   source_refs={"namespace",probe+"_pod"}
   account=d[probe+"_pod"]["data"]["spec"]["serviceAccountName"]
   children=[]
   for b_key in active:
    raw_binding=d[b_key]["data"]
    bname=raw_binding["metadata"]["name"]
    binding=bindings[bname]
    policy=policies[binding["policy_name"]]
    require(binding["policy_name"] in installed_names,
            "BOUND_POLICY_NOT_YET_IN_REGISTERED_SOURCE_SCOPE")
    applicable=all(namespace.get(k)==v
                   for k,v in binding["selector"].items())
    violation=account==policy["rejected_sa"]
    source_refs.update((b_key,policy["key"]))
    children.append({"op":"AND","children":[
        leaf(phase+"|"+probe+"|"+bname+"|selector",applicable,
             ["namespace",b_key],
             "K8S_BINDING_MATCHLABELS_SOURCE_QUALIFIED"),
        leaf(phase+"|"+probe+"|"+bname+"|cel",violation,
             [policy["key"],probe+"_pod"],
             "K8S_REGISTERED_CEL_NOT_EQUAL_SUBSET")
    ]})
   source_refs.update(installed)
   result.append({
     "case_id":"K8S|"+phase+"|"+probe,
     "domain":"K8S_SCOPED_VAP_DENY",
     "registered_contract":"E2_K8S_REGISTERED_VAP_BINDING_DENY_POD_CREATE",
     "verified_source_sha256":{k:d[k]["digest"] for k in sorted(source_refs)},
     "formula":{"op":"OR","children":children},
     "authored_membership_NOT_a_live_authorized_list":True,
     "old_native_decisions_never_read":True,
   })
 require(len(result)==8 and len(set(x["case_id"] for x in result))==8,
         "EIGHT_EXPECTED_SOURCE_WITNESSES")
 return result

def main():
 import argparse
 p=argparse.ArgumentParser()
 p.add_argument("--out",required=True)
 a=p.parse_args()
 rows=build()
 Path(a.out).write_text(json.dumps(rows,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"K8S_independent_original_source_witnesses":len(rows),
                   "live_authoritative_source_inventory_proven":False,
                   "original_native_labels_read":False},sort_keys=True))

if __name__=="__main__":main()
