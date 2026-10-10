#!/usr/bin/env python3
"""R3-M1 SOURCE ONLY two-binding native predictions. No kubectl, native data or scorer."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

NAMES=("policy.json","binding-team.json","binding-mode.json","namespace.json",
       "pod-flux.json","pod-default.json","action-team.json","action-mode.json")
ORDERS={"TM":("team","mode"),"MT":("mode","team")}
PHASES=("initial","after_first","after_second")
PROBES=("flux","default")


class SourceUnavailable(Exception):
    pass


class Unsupported(Exception):
    pass


def check(value,code):
    if not value:
        raise Unsupported(code)


def source_inputs(root):
    d,rows={},[]
    for name in NAMES:
        try: raw=(Path(root)/name).read_bytes()
        except OSError as exc:
            raise SourceUnavailable("SOURCE_UNAVAILABLE:"+name) from exc
        try: obj=json.loads(raw)
        except (UnicodeError,ValueError) as exc:
            raise Unsupported("INVALID_JSON:"+name) from exc
        d[name]=obj
        rows.append({"name":name,"bytes":len(raw),
                     "sha256":hashlib.sha256(raw).hexdigest()})
    return d,rows


def validate(d):
    for name in NAMES:
        if name not in d: raise SourceUnavailable("SOURCE_UNAVAILABLE:"+name)
    check(set(d)==set(NAMES),"UNKNOWN_SOURCE_INVENTORY")
    p=d["policy.json"]
    check(p.get("apiVersion")=="admissionregistration.k8s.io/v1" and
          p.get("kind")=="ValidatingAdmissionPolicy" and
          p.get("metadata",{}).get("name")=="eeq-r3-flux-deny" and
          set(p.get("spec",{}))=={"failurePolicy","matchConstraints","validations"} and
          p["spec"]["failurePolicy"]=="Fail" and
          p["spec"]["matchConstraints"]=={"resourceRules":[{"apiGroups":[""],
             "apiVersions":["v1"],"operations":["CREATE"],"resources":["pods"]}]} and
          p["spec"]["validations"]==[{"expression":
             "object.spec.serviceAccountName != 'flux'",
             "message":"EEQ_R3_FLUX_SA_DENIED","reason":"Forbidden"}],
          "UNSUPPORTED_POLICY_RULE")
    selectors={}
    for key,expected_key,expected_value in (("team","r3.team","tenant"),
                                             ("mode","r3.mode","strict")):
        b=d["binding-"+key+".json"]
        spec=b.get("spec",{})
        check(b.get("apiVersion")=="admissionregistration.k8s.io/v1" and
              b.get("kind")=="ValidatingAdmissionPolicyBinding" and
              b.get("metadata",{}).get("name")=="eeq-r3-binding-"+key and
              set(spec)=={"policyName","validationActions","matchResources"} and
              spec["policyName"]=="eeq-r3-flux-deny" and
              spec["validationActions"]==["Deny"] and
              spec["matchResources"]=={"namespaceSelector":{
                   "matchLabels":{expected_key:expected_value}}},
              "UNSUPPORTED_BINDING:"+key)
        selectors[key]={expected_key:expected_value}
    ns=d["namespace.json"]
    check(ns.get("apiVersion")=="v1" and ns.get("kind")=="Namespace" and
          ns.get("metadata",{}).get("name")=="eeq-r3" and
          ns["metadata"].get("labels")=={"r3.team":"tenant","r3.mode":"strict"},
          "UNSUPPORTED_NAMESPACE")
    pods={}
    for sa in PROBES:
        pod=d["pod-"+sa+".json"]
        spec=pod.get("spec",{})
        check(pod.get("apiVersion")=="v1" and pod.get("kind")=="Pod" and
              pod.get("metadata",{}).get("namespace")=="eeq-r3" and
              pod["metadata"].get("name")=="eeq-r3-"+sa+"-probe" and
              spec.get("serviceAccountName")==sa and
              spec.get("restartPolicy")=="Never" and
              isinstance(spec.get("containers"),list) and len(spec["containers"])==1,
              "UNSUPPORTED_POD:"+sa)
        pods[sa]=sa
    for key,frm,to in (("team","tenant","external"),("mode","strict","relaxed")):
        act=d["action-"+key+".json"]
        fullname="r3."+key
        check(act=={"schema":"eeq-r3-m1-native-action-v1",
              "operation":"UPDATE_NAMESPACE_LABEL","resource":"namespaces/eeq-r3",
              "key":fullname,"from":frm,"to":to,
              "full_command":["kubectl","label","namespace","eeq-r3",
                              fullname+"="+to,"--overwrite"]},
              "UNREGISTERED_ACTION:"+key)
    return selectors,pods


def prediction(d):
    selectors,pods=validate(d)
    rows=[]
    for order,sequence in ORDERS.items():
        labels=d["namespace.json"]["metadata"]["labels"].copy()
        for step,phase in enumerate(PHASES):
            if step:
                action=d["action-"+sequence[step-1]+".json"]
                check(labels.get(action["key"])==action["from"],
                      "INVALID_REGISTERED_ACTION_PRECONDITION")
                labels[action["key"]]=action["to"]
            qualified=[b for b in ("team","mode") if
                all(labels.get(k)==v for k,v in selectors[b].items())]
            for probe in PROBES:
                result="REJECT" if qualified and pods[probe]=="flux" else "ACCEPT"
                rows.append({
                    "order":order,"phase":phase,"probe":probe,
                    "qualified_binding_source_ids":
                        ["binding-"+b+".json" for b in qualified],
                    "expected_native":result,
                    "source_only_namespace_labels":labels.copy(),
                    "source_only_action_prefix":list(sequence[:step]),
                })
    check(len(rows)==12,"PRIMARY_DENOMINATOR_NOT_12")
    controls={
        "unbound":{"flux":"ACCEPT","default":"ACCEPT"},
        "only_team":{"flux":"REJECT","default":"ACCEPT"},
        "only_mode":{"flux":"REJECT","default":"ACCEPT"},
    }
    # Fully informed hand-engineered B9 may read BOTH binding selectors,
    # namespace label updates and registered CEL, therefore it ties.
    return {
        "schema":"eeq-r3-m1-source-only-predictions-v1",
        "evidence_class":"CONTROLLED_NATIVE_DEVELOPMENT",
        "source_only":True,"native_labels_read":False,
        "native_verifier_called":False,"registered_cases":rows,
        "per_cluster_frozen_controls":controls,
        "native_primary_denominator":12,"native_control_denominator":12,
        "native_action_updates":4,"original_v1_g5_increment":0,
        "strong_b9_given_same_inputs_able_to_tie":True,
        "native_success_not_yet_observed":True,
        "r3_general_method_novelty_proven":False,
    }


def build(directory):
    d,rows=source_inputs(directory)
    p=prediction(d)
    return {
        "schema":"eeq-r3-m1-source-manifest-v1",
        "sources":rows,"original_v1_g5_increment":0,
        "source_only_before_native":True
    },p


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--sources",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    m,p=build(a.sources)
    out=Path(a.out)
    out.mkdir(parents=True,exist_ok=True)
    (out/"sources").mkdir(exist_ok=True)
    for name in NAMES:
        (out/"sources"/name).write_bytes((Path(a.sources)/name).read_bytes())
    (out/"SOURCE_MANIFEST.json").write_text(
        json.dumps(m,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    (out/"SOURCE_PREDICTIONS.json").write_text(
        json.dumps(p,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "science_status":"R3_M1_PRESOURCE_SOURCE_ONLY_NO_NATIVE",
        "registered_primary":len(p["registered_cases"]),
        "per_cluster_controls":sum(len(x) for x in p["per_cluster_frozen_controls"].values()),
        "future_actions":4,"strong_b9_tie_expected":True,
        "native_calls":0,"g5_increment":0},sort_keys=True))


if __name__=="__main__":
    main()
