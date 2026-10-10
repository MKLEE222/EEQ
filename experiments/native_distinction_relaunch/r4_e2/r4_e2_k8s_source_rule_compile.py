#!/usr/bin/env python3
"""E2 K8s source-backed, whitelisted VAP/Binding/CEL -> generic rule IR.

No native kubectl/LIST/Watch; phase inventories are ORIGINAL AUTHOR-REGISTERED
development actions, NOT independently established currently closed native
API source sets. Does not import archived R3M3 decisions or prediction labels.
"""
import hashlib,json,re,sys
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
PINS={
 "namespace":("r3_m1/sources/namespace.json","428f16bc92ac27dec26b87ad24951113cf463922"),
 "flux_policy":("r3_m1/sources/policy.json","c22a8134447649d202a49b644ddb8485835c0fc2"),
 "team_binding":("r3_m1/sources/binding-team.json","2bc5a5706910196c5cd0631c4034ca3ccdbb890b"),
 "mode_binding":("r3_m1/sources/binding-mode.json","357ef4bd582f47e2308f6e640307077bafe47b68"),
 "third_policy":("r3_m3/sources/policy-third.json","ae7ab92b2d15f7793ec41232752efc2c30ebf347"),
 "third_binding":("r3_m3/sources/binding-third.json","e2a774ee92c2af6411e1a516e48af4695f096088"),
 "flux_pod":("r3_m1/sources/pod-flux.json","def429a28e90544d9f2274101b97950801e8d924"),
 "default_pod":("r3_m1/sources/pod-default.json","9f82b811c2c6154ed20e1145f926be1d45f2c1fc"),
}
PHASES=(
 ("S0_INITIAL",("team_binding","mode_binding"),("flux_policy",)),
 ("A1_POLICY_ADDED",("team_binding","mode_binding"),("flux_policy","third_policy")),
 ("A2_BINDING_ADDED",("team_binding","mode_binding","third_binding"),("flux_policy","third_policy")),
 ("A3_BINDING_DELETED",("team_binding","mode_binding"),("flux_policy","third_policy")),
)
RULE={"resourceRules":[{"apiGroups":[""],"apiVersions":["v1"],
                       "operations":["CREATE"],"resources":["pods"]}]}
CEL=re.compile(r"^object\.spec\.serviceAccountName != '([a-z][a-z0-9_-]*)'$")
SCHEMA="eeq-r4-e2-native-source-qualified-rule-ir-v1"

class Unsupported(Exception):pass

def need(ok,msg):
    if not ok:raise Unsupported(msg)

def sha256(raw):return hashlib.sha256(raw).hexdigest()

def canonical_object_sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def pinned_native_docs():
    docs={}
    for key,(p,expected) in PINS.items():
        raw=(BASE/p).read_bytes()
        need(git_blob(raw)==expected,"ORIGINAL_NATIVE_SOURCE_GIT_BLOB_CHANGED:"+key)
        obj=json.loads(raw)
        docs[key]={"obj":obj,"sha256":sha256(raw),
                   "canonical_object_sha256":canonical_object_sha(obj)}
    return docs

def verify_inputs(docs):
    need(isinstance(docs,dict) and set(docs)==set(PINS),
         "SOURCE_OR_BINDING_INVENTORY_UNREGISTERED")
    for name,record in docs.items():
        need(isinstance(record,dict) and
             isinstance(record.get("obj"),dict) and
             isinstance(record.get("sha256"),str) and len(record["sha256"])==64 and
             record.get("canonical_object_sha256")==canonical_object_sha(record["obj"]),
             "SOURCE_RECORD_MALFORMED:"+name)
    n=docs["namespace"]["obj"]
    need(n.get("kind")=="Namespace" and n.get("apiVersion")=="v1" and
         n.get("metadata",{}).get("name")=="eeq-r3" and
         isinstance(n.get("metadata",{}).get("labels"),dict),
         "NAMESPACE_SOURCE_UNSUPPORTED")
    for pod_name in ("flux_pod","default_pod"):
        p=docs[pod_name]["obj"]
        need(p.get("kind")=="Pod" and p.get("apiVersion")=="v1" and
             p.get("metadata",{}).get("namespace")=="eeq-r3" and
             p.get("spec",{}).get("serviceAccountName")==
                   ("flux" if pod_name=="flux_pod" else "default"),
             "POD_SOURCE_UNREGISTERED:"+pod_name)
    policies={}
    for name in ("flux_policy","third_policy"):
        p=docs[name]["obj"]
        spec=p.get("spec",{})
        v=spec.get("validations")
        need(p.get("kind")=="ValidatingAdmissionPolicy" and
             p.get("apiVersion")=="admissionregistration.k8s.io/v1" and
             spec.get("failurePolicy")=="Fail" and
             spec.get("matchConstraints")==RULE and
             set(spec)=={"failurePolicy","matchConstraints","validations"} and
             isinstance(v,list) and len(v)==1 and
             isinstance(v[0],dict) and set(v[0])==
                {"expression","message","reason"} and
             v[0]["reason"]=="Forbidden" and
             isinstance(v[0]["message"],str),
             "UNSUPPORTED_POLICY_CEL_OR_ADMISSION_GRAMMAR:"+name)
        expr=v[0]["expression"]
        match=CEL.fullmatch(expr) if isinstance(expr,str) else None
        need(match is not None,"UNSUPPORTED_K8S_CEL_SYNTAX:"+name)
        id_=p.get("metadata",{}).get("name")
        need(isinstance(id_,str) and bool(id_) and id_ not in policies,
             "DUPLICATE_K8S_POLICY_NAME")
        policies[id_]={"source":name,"denied_sa":match.group(1)}
    bindings={}
    for name in ("team_binding","mode_binding","third_binding"):
        b=docs[name]["obj"]
        spec=b.get("spec",{})
        need(b.get("kind")=="ValidatingAdmissionPolicyBinding" and
             b.get("apiVersion")=="admissionregistration.k8s.io/v1" and
             isinstance(spec,dict) and set(spec)==
               {"policyName","validationActions","matchResources"} and
             spec["validationActions"]==["Deny"] and
             spec["policyName"] in policies and
             isinstance(spec["matchResources"],dict) and
             set(spec["matchResources"])=={"namespaceSelector"} and
             isinstance(spec["matchResources"]["namespaceSelector"],dict) and
             set(spec["matchResources"]["namespaceSelector"])=={"matchLabels"},
             "UNSUPPORTED_BINDING_OR_SELECTOR_GRAMMAR:"+name)
        selector=spec["matchResources"]["namespaceSelector"]["matchLabels"]
        need(isinstance(selector,dict) and selector and
             all(isinstance(k,str) and k and isinstance(v,str) and v
                 for k,v in selector.items()),"MALFORMED_SELECTOR:"+name)
        id_=b.get("metadata",{}).get("name")
        need(isinstance(id_,str) and bool(id_) and id_ not in bindings,
             "DUPLICATE_BINDING_NAME")
        bindings[id_]={"source":name,"selector":selector,
                        "policy_name":spec["policyName"]}
    return policies,bindings

def compile_case(docs,phase,probe):
    policies,bindings=verify_inputs(docs)
    phases={x[0]:(x[1],x[2]) for x in PHASES}
    need(phase in phases and probe in ("flux","default"),
         "UNREGISTERED_ACTION_PHASE_OR_ACTOR")
    active,policy_sources=phases[phase]
    active_native_policy_names={docs[p]["obj"]["metadata"]["name"] for p in policy_sources}
    ns=docs["namespace"]["obj"]["metadata"]["labels"]
    pdoc=docs[probe+"_pod"]["obj"]
    sa=pdoc["spec"]["serviceAccountName"]
    used={"namespace","flux_pod" if probe=="flux" else "default_pod"}
    terms=[]
    for key in active:
        b=docs[key]["obj"]
        bname=b["metadata"]["name"]
        binfo=bindings[bname]
        policy_id=binfo["policy_name"]
        need(policy_id in active_native_policy_names,
             "ACTIVE_BINDING_WITHOUT_NATIVE_POLICY:"+bname)
        pi=policies[policy_id]
        selector=binfo["selector"]
        matched=all(ns.get(k)==v for k,v in selector.items())
        violation=(sa==pi["denied_sa"])
        used|={key,pi["source"]}
        terms.append({"op":"AND","children":[
          {"op":"ATOM","id":phase+"|"+probe+"|"+bname+"|selector",
           "value":matched,
           "source_refs":["namespace",key],
           "obligation":"K8S_BINDING_MATCHLABELS_SOURCE_QUALIFIED"},
          {"op":"ATOM","id":phase+"|"+probe+"|"+bname+"|cel",
           "value":violation,
           "source_refs":[pi["source"],probe+"_pod"],
           "obligation":"K8S_REGISTERED_CEL_NOT_EQUAL_SUBSET"}
        ]})
    # Preserve all source policy inventory members, including an UNBOUND policy.
    used.update(policy_sources)
    return {
       "schema":SCHEMA,
       "domain":"K8S_SCOPED_VAP_DENY",
       "case_id":"K8S|"+phase+"|"+probe,
       "registered_contract":"E2_K8S_REGISTERED_VAP_BINDING_DENY_POD_CREATE",
       "verified_source_sha256":{k:docs[k]["sha256"] for k in sorted(used)},
       "native_labels_read":False,
       "evidence_class":"PREVIOUS_NATIVE_DEVELOPMENT_SOURCE_BYTES_NEW_COMPILER",
       "source_closure_is_author_independently_attested":False,
       "author_registered_phase_membership_not_live_native_list":True,
       "authz_scope":"ONLY_REGISTERED_VALIDATING_ADMISSION_POLICIES_AND_BINDINGS",
       "formula":{"op":"OR","children":terms}
    }

def emit(out):
    root=Path(out);root.mkdir(parents=True,exist_ok=True)
    docs=pinned_native_docs()
    programs=[compile_case(docs,phase,probe)
              for phase,_,_ in PHASES for probe in ("flux","default")]
    need(len(programs)==8,"K8S_SOURCE_PROGRAM_DENOMINATOR_CHANGED")
    (root/"E2_K8S_8_SOURCE_RULE_PROGRAMS.json").write_text(
        json.dumps(programs,sort_keys=True,indent=2)+"\n")
    manifest=[{"source":k,"sha256":docs[k]["sha256"],"git_blob":PINS[k][1]}
              for k in sorted(PINS)]
    (root/"E2_K8S_SOURCE_MANIFEST.json").write_text(
        json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"source_documents":len(docs),"k8s_compiled_programs":8,
                      "native_calls":0,"historical_native_labels_read":False,
                      "live_native_source_roster_certified":False},sort_keys=True))

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    emit(p.parse_args().out)
