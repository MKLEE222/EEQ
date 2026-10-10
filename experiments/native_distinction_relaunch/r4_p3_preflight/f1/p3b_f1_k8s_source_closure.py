#!/usr/bin/env python3
"""F1 source-backed, *bounded* K8s dependency read-set audit.

No native call, no scored label input, no general K8s source-to-model compiler.
Static namespace read sets are complete ONLY for the whitelist of ONE
ValidatingAdmissionPolicy, ONE matchLabels-only binding and Pod CREATE.
"""
import hashlib
import json
import re
from pathlib import Path

PINNED_BLOBS = {
    "policy.json": "bf5b9f7a99e3cbd11713352e83be2a4e345a03fc",
    "binding-a.json": "4dff26ab237254d7de45c2008d68dd03800b4346",
    "binding-b.json": "d78be9f01690f4c65b8bff78069dc1ed2aecdd2d",
    "namespace-before.json": "b998f3e99380e8a04e34629048724726a591dbc1",
    "pod-flux.json": "de2f62f788726ed90d5f76889fb33126850d770b",
    "pod-default.json": "2dce4b8e5e69b9333d63e24885f94e5639b2d51a",
    "update-namespace-label.json": "778c7a043daa2e3c5048a6cd5ed27b4563133368",
}
SOURCES = Path(__file__).resolve().parents[2] / "r2a" / "sources"
SCOPE = {
    "contract": "R2A_SINGLE_VAP_ONE_BINDING_MATCHLABELS_ONLY",
    "actor": "REGISTERED_NATIVE_POD_CREATE",
    "action": "UPDATE_NAMESPACE_LABEL(r2a.mode=relaxed)",
    "horizon": 1,
}
NATIVE_ARCHIVED_RUN_ID = 37906692298  # provenance, NEVER read by model
EXPECTED_RULE = {
    "apiGroups": [""], "apiVersions": ["v1"],
    "operations": ["CREATE"], "resources": ["pods"],
}
EXPRESSION = "object.spec.serviceAccountName != 'flux'"
COMMAND = ["kubectl", "label", "namespace", "eeq-r2a",
           "r2a.mode=relaxed", "--overwrite"]
MISSING = object()


class SourceUnavailable(Exception):
    pass


class ModelUnsupported(Exception):
    pass


def check(ok, code):
    if not ok:
        raise ModelUnsupported(code)


def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def original_docs(base=SOURCES):
    """Pin the archived Git fixture BY EXACT RAW BYTES, never by native labels."""
    result = {}
    for name, expected in PINNED_BLOBS.items():
        path = Path(base) / name
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise SourceUnavailable("MISSING_REGISTERED_SOURCE:" + name) from exc
        check(git_blob_sha(raw) == expected, "ORIGINAL_SOURCE_PIN_CHANGED:" + name)
        try:
            result[name] = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            raise ModelUnsupported("MALFORMED_SOURCE_JSON:" + name) from exc
    return result


def parse_registered(docs):
    """Whitelist exact relevant native *source* grammar; reject unmodeled features."""
    check(isinstance(docs, dict), "NO_DOCUMENT_MAP")
    for name in PINNED_BLOBS:
        if name not in docs:
            raise SourceUnavailable("MISSING_REGISTERED_SOURCE:" + name)
        check(isinstance(docs[name], dict), "INVALID_SOURCE_DOCUMENT:" + name)
    check(set(docs) == set(PINNED_BLOBS), "UNREGISTERED_EXTRA_SOURCE_DOCUMENT")
    p = docs["policy.json"]
    check(set(p) == {"apiVersion","kind","metadata","spec"} and
          p.get("apiVersion") == "admissionregistration.k8s.io/v1" and
          p.get("kind") == "ValidatingAdmissionPolicy" and
          p["metadata"].get("name") == "eeq-r2a-flux-deny",
          "UNREGISTERED_POLICY")
    spec = p["spec"]
    check(isinstance(spec, dict) and
          set(spec) == {"failurePolicy","matchConstraints","validations"} and
          spec["failurePolicy"] == "Fail" and
          spec["matchConstraints"] == {"resourceRules":[EXPECTED_RULE]} and
          isinstance(spec["validations"], list) and len(spec["validations"]) == 1 and
          spec["validations"][0] == {
              "expression":EXPRESSION,
              "message":"EEQ_R2A_FLUX_SA_DENIED",
              "reason":"Forbidden",
          }, "UNREGISTERED_POLICY_SEMANTICS")
    selectors = {}
    for branch in ("a", "b"):
        b = docs["binding-" + branch + ".json"]
        check(set(b) == {"apiVersion","kind","metadata","spec"} and
              b.get("apiVersion") == "admissionregistration.k8s.io/v1" and
              b.get("kind") == "ValidatingAdmissionPolicyBinding" and
              b["metadata"].get("name") == "eeq-r2a-binding-" + branch and
              isinstance(b["spec"],dict) and
              set(b["spec"]) == {"policyName","validationActions","matchResources"} and
              b["spec"]["policyName"] == p["metadata"]["name"] and
              b["spec"]["validationActions"] == ["Deny"],
              "UNREGISTERED_BINDING_SEMANTICS")
        resources = b["spec"]["matchResources"]
        check(isinstance(resources,dict) and set(resources)=={"namespaceSelector"} and
              isinstance(resources["namespaceSelector"],dict) and
              set(resources["namespaceSelector"])=={"matchLabels"},
              "UNSUPPORTED_BINDING_SELECTOR_GRAMMAR")
        labels = resources["namespaceSelector"]["matchLabels"]
        check(isinstance(labels,dict) and bool(labels) and
              all(isinstance(k,str) and bool(k) and isinstance(v,str) and bool(v)
                  for k,v in labels.items()),
              "INVALID_MATCHLABELS")
        selectors[branch] = labels.copy()

    ns = docs["namespace-before.json"]
    check(ns.get("apiVersion")=="v1" and ns.get("kind")=="Namespace" and
          isinstance(ns.get("metadata"),dict) and
          ns["metadata"].get("name")=="eeq-r2a" and
          isinstance(ns["metadata"].get("labels"),dict) and
          all(isinstance(k,str) and isinstance(v,str)
              for k,v in ns["metadata"]["labels"].items()),
          "UNREGISTERED_NAMESPACE_OR_INCOMPLETE_LABEL_OBSERVATION")
    before = ns["metadata"]["labels"].copy()
    op = docs["update-namespace-label.json"]
    check(op == {"schema":"eeq-r2a-native-action-v1",
                 "operation":"UPDATE_NAMESPACE_LABEL",
                 "resource":"namespaces/eeq-r2a",
                 "key":"r2a.mode","from":"strict","to":"relaxed",
                 "full_command":COMMAND} and
          before.get("r2a.mode") == "strict", "UNREGISTERED_FUTURE_ACTION")
    after = before.copy()
    after["r2a.mode"] = "relaxed"
    service_accounts = {}
    for probe in ("flux","default"):
        pod=docs["pod-" + probe + ".json"]
        check(set(pod)=={"apiVersion","kind","metadata","spec"} and
              pod.get("apiVersion")=="v1" and pod.get("kind")=="Pod" and
              pod["metadata"].get("namespace")=="eeq-r2a" and
              pod["metadata"].get("name")=="eeq-r2a-" + probe + "-probe" and
              isinstance(pod.get("spec"),dict) and
              set(pod["spec"])=={"serviceAccountName","restartPolicy",
                                "securityContext","containers"} and
              pod["spec"].get("serviceAccountName")==probe and
              pod["spec"].get("restartPolicy")=="Never" and
              isinstance(pod["spec"].get("containers"),list) and
              len(pod["spec"]["containers"])==1,
              "UNREGISTERED_POD_SCOPE")
        service_accounts[probe]=pod["spec"]["serviceAccountName"]
    return selectors, before, after, service_accounts


def evaluate_from_sources(selectors, labels, sa, branch):
    """Restricted source-only VAP predicate; NEVER consumes native outcomes."""
    qualified = all(labels.get(k,MISSING)==v for k,v in selectors[branch].items())
    return "REJECT" if qualified and sa=="flux" else "ACCEPT"


def changed_registered_reads(selectors, before, after):
    """Synthetic-only if before/after are not from the registered native action."""
    return {branch: [
        key for key in sorted(selectors[branch])
        if before.get(key,MISSING)!=after.get(key,MISSING)
    ] for branch in ("a","b")}


def audit(docs,scope=None):
    """Check registered policy structure and conservative source-backed reuse eligibility.

    REUSE_DECISION_ONLY is NOT a verified native outcome, unchanged certificate,
    nor permission to skip proof of actual native UPDATE execution.
    """
    if scope is None:
        scope=SCOPE
    if scope!=SCOPE or type(scope) is not dict:
        return {"scientific_status":"SCOPED_SOURCE_BACKED_DEV_DIAGNOSTIC",
                "status":"MODEL_UNSUPPORTED","reason":"UNREGISTERED_SCOPE"}
    try:
        selectors,before,after,sas = parse_registered(docs)
    except SourceUnavailable as exc:
        return {"scientific_status":"SCOPED_SOURCE_BACKED_DEV_DIAGNOSTIC",
                "status":"SOURCE_UNAVAILABLE","reason":str(exc)}
    except (ModelUnsupported,TypeError,KeyError,AttributeError) as exc:
        return {"scientific_status":"SCOPED_SOURCE_BACKED_DEV_DIAGNOSTIC",
                "status":"MODEL_UNSUPPORTED","reason":str(exc)}
    pair=[]
    rows=[]
    changed_by_branch=changed_registered_reads(selectors,before,after)
    for branch in ("a","b"):
        keys=sorted(selectors[branch])
        changed=changed_by_branch[branch]
        for probe in ("flux","default"):
            pair.append({
                "branch":branch,"probe":probe,
                "read_set":["policy:CELL_VALIDATION","binding:"+branch+":matchLabels",
                            "pod:"+probe+":serviceAccountName"]+
                           ["namespace.labels:"+key for key in keys],
                "changed_registered_namespace_keys":changed,
                "reuse_disposition":("REVERIFY_REQUIRED" if changed else
                                     "REUSE_DECISION_ONLY"),
                "requires_new_provenance_for_native_revision":True,
                "conditional_on_actual_registered_native_update":True,
            })
            for phase,labels in (("current",before),
                                 ("after_native_label_update",after)):
                rows.append({
                    "branch":branch,"phase":phase,"probe":probe,
                    "source_only_expected":evaluate_from_sources(
                        selectors,labels,sas[probe],branch)
                })
    return {
        "scientific_status":"SCOPED_SOURCE_BACKED_DEV_DIAGNOSTIC",
        "status":"SOURCE_BACKED_READ_SET_DERIVED",
        "evidence_class":"POST_NATIVE_REUSE_OF_ALREADY_SCORED_DEVELOPMENT",
        "source_only_no_native_labels_read":True,
        "native_calls_in_this_audit":0,
        "new_g5_cases":0,"p3_independent_advantage":False,
        "single_binding_only":True,"fully_informed_b9_entitled_same_read_set":True,
        "pairs":pair,"source_only_rows":rows,
    }


def main():
    try:
        report=audit(original_docs())
    except SourceUnavailable as exc:
        report={"status":"SOURCE_UNAVAILABLE","reason":str(exc)}
    except ModelUnsupported as exc:
        report={"status":"MODEL_UNSUPPORTED","reason":str(exc)}
    print(json.dumps(report,indent=2,sort_keys=True))
    if report["status"]!="SOURCE_BACKED_READ_SET_DERIVED":
        raise SystemExit(1)


if __name__=="__main__":
    main()
