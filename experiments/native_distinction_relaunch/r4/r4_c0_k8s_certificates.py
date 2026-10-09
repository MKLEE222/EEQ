#!/usr/bin/env python3
"""R4-C0 K8s domain semantics adapter (post-native development integration).

No cluster or kubectl invocation. Re-verifies pinned source predicates,
recorded real native namespace mutation and original VAP attribution.
No imports from the R2A source predictor or from its join-only scorer.
"""
import argparse
import hashlib
import json
from pathlib import Path

BRANCHES = ("a","b")
PHASES = ("current","after_native_label_update")
PROBES = ("flux","default")


def check(ok, why):
    if not ok:
        raise ValueError(why)


def sha(x):
    return hashlib.sha256(x).hexdigest()


def unique(rows, key):
    out = {}
    for row in rows:
        k = key(row)
        check(k not in out, "DUPLICATE_NATIVE_ROW_" + str(k))
        out[k] = row
    return out


def build(source_dir, native_a_file, native_b_file):
    root = Path(source_dir)
    manifest = json.loads((root/"SOURCE_MANIFEST.json").read_text())
    check(manifest["schema"]=="eeq-r2a-k8s-source-manifest-v1",
          "UNREGISTERED_K8S_MANIFEST")
    check(len(manifest["sources"])==7,"SEVEN_PINNED_K8S_SOURCES_REQUIRED")
    sources = {}
    for record in manifest["sources"]:
        raw = (root/"sources"/record["name"]).read_bytes()
        check(len(raw)==record["bytes"] and sha(raw)==record["sha256"],
              "PINNED_SOURCE_CHANGED_"+record["name"])
        sources[record["name"]] = {
            "object":json.loads(raw),"sha256":record["sha256"],
        }
    check(len(sources)==7,"DUPLICATE_SOURCE_NAME")

    policy = sources["policy.json"]["object"]
    spec = policy.get("spec", {})
    check(policy.get("kind")=="ValidatingAdmissionPolicy" and
          policy.get("apiVersion")=="admissionregistration.k8s.io/v1" and
          policy.get("metadata",{}).get("name")=="eeq-r2a-flux-deny" and
          spec.get("failurePolicy")=="Fail",
          "UNREGISTERED_K8S_POLICY")
    check(spec.get("matchConstraints")=={"resourceRules":[{
        "apiGroups":[""],"apiVersions":["v1"],
        "operations":["CREATE"],"resources":["pods"]
    }]},"UNSUPPORTED_POLICY_MATCH_CONSTRAINTS")
    validations=spec.get("validations",[])
    check(len(validations)==1 and
          validations[0].get("expression")==
            "object.spec.serviceAccountName != 'flux'" and
          validations[0].get("message")=="EEQ_R2A_FLUX_SA_DENIED",
          "UNSUPPORTED_K8S_CEL_OR_DENIAL")
    before_source=sources["namespace-before.json"]["object"]
    before_labels=before_source["metadata"]["labels"]
    check(before_source["metadata"]["name"]=="eeq-r2a" and
          before_labels.get("r2a.team")=="tenant" and
          before_labels.get("r2a.mode")=="strict",
          "UNREGISTERED_SOURCE_NAMESPACE")
    action=sources["update-namespace-label.json"]["object"]
    command=["kubectl","label","namespace","eeq-r2a",
             "r2a.mode=relaxed","--overwrite"]
    check(action.get("operation")=="UPDATE_NAMESPACE_LABEL" and
          action.get("full_command")==command and
          action.get("from")=="strict" and action.get("to")=="relaxed" and
          action.get("key")=="r2a.mode",
          "UNREGISTERED_K8S_ACTION")

    native={"a":json.loads(Path(native_a_file).read_text()),
            "b":json.loads(Path(native_b_file).read_text())}
    contexts=set()
    certs=[]
    all_controls=0
    resource_updates=0
    for branch in BRANCHES:
        n=native[branch]
        check(n.get("schema")=="eeq-r2a-native-k8s-dynamic-branch-v1" and
              n.get("branch")==branch and
              n.get("native_predictions_file_read") is False and
              n.get("g5_increment")==0,
              "NATIVE_K8S_SCHEMA_OR_PROVENANCE_INVALID")
        check(n.get("source_digest_map")=={
            name:source["sha256"] for name,source in sources.items()},
            "NATIVE_K8S_SOURCE_HASH_DIVERGENCE")
        ctx=n.get("native_cluster_context")
        check(ctx and ctx not in contexts,"TWO_NATIVE_CLUSTERS_NOT_ISOLATED")
        contexts.add(ctx)
        binding=sources[f"binding-{branch}.json"]["object"]
        bspec=binding.get("spec",{})
        selector=bspec.get("matchResources",{}).get(
            "namespaceSelector",{}).get("matchLabels",{})
        check(binding.get("kind")=="ValidatingAdmissionPolicyBinding" and
              bspec.get("policyName")=="eeq-r2a-flux-deny" and
              bspec.get("validationActions")==["Deny"] and
              selector and n["native_observed_binding_selector"]==selector and
              n["source_binding_selector"]==selector,
              "NATIVE_K8S_BINDING_SCOPE_INVALID_"+branch)
        ns_before=n["native_current_namespace"]
        ns_after=n["native_post_action_namespace"]
        change=n["namespace_label_action_command"]
        changed=(
            n["native_namespace_action_verified"] is True and
            change["exit_code"]==0 and change["command"]==command and
            ns_before["uid"]==ns_after["uid"] and
            ns_before["resource_version"]!=ns_after["resource_version"] and
            ns_before["labels"].get("r2a.team")==
                ns_after["labels"].get("r2a.team")=="tenant" and
            ns_before["labels"].get("r2a.mode")=="strict" and
            ns_after["labels"].get("r2a.mode")=="relaxed"
        )
        check(changed,"NATIVE_NAMESPACE_LABEL_MUTATION_NOT_PROVED_"+branch)
        resource_updates+=1
        ctrls=unique(n["unbound_controls"],lambda r:r["probe"])
        check(set(ctrls)==set(PROBES),"UNBOUND_CONTROL_MISSING_"+branch)
        for probe in PROBES:
            check(ctrls[probe]["native"]=="ACCEPT" and
                  ctrls[probe]["native_attribution"]=="ADMITTED",
                  "UNBOUND_NATIVE_POLICY_CONTROL_FAILED_"+branch)
            all_controls+=1

        case_map=unique(
            n["current_probes"]+n["future_probes"],
            lambda r:(r["phase"],r["probe"])
        )
        check(set(case_map)=={(phase,p) for phase in PHASES for p in PROBES},
              "MISSING_REGISTERED_NATIVE_POD_CASE_"+branch)
        for phase in PHASES:
            labels=ns_before["labels"] if phase=="current" else ns_after["labels"]
            selector_match=all(labels.get(k)==v for k,v in selector.items())
            for probe in PROBES:
                pod=sources[f"pod-{probe}.json"]["object"]
                sa=pod["spec"]["serviceAccountName"]
                check(sa==probe,"POD_SCOPE_TAMPER")
                passes_cel=sa!="flux"
                source_effect=("REJECT" if selector_match and not passes_cel
                               else "ACCEPT")
                observed=case_map[phase,probe]
                source_hash=sources[f"pod-{probe}.json"]["sha256"]
                check(observed["pod_source_sha256"]==source_hash,
                      "NATIVE_POD_SOURCE_HASH_DRIFT")
                native_effect=observed["native"]
                attributable=(
                    (native_effect=="REJECT" and
                     observed.get("native_attribution")=="REGISTERED_VAP_DENY")
                    or
                    (native_effect=="ACCEPT" and
                     observed.get("native_attribution")=="ADMITTED")
                )
                verified=source_effect==native_effect and attributable
                before_state=branch+":mode="+(
                    "strict" if phase=="current" else "relaxed")
                certs.append({
                    "schema":"eeq-r4-qualified-transition-certificate-v0",
                    "domain":"k8s_admission",
                    "contract_id":"R2A_K8S_REGISTERED_VAP_DYNAMIC_POD_CREATE",
                    "case_id":f"{branch}|{phase}|{probe}",
                    "sources":{
                        "policy":sources["policy.json"]["sha256"],
                        "binding":sources[f"binding-{branch}.json"]["sha256"],
                        "pod":source_hash,
                        "initial_namespace":
                            sources["namespace-before.json"]["sha256"],
                        "namespace_update":
                            sources["update-namespace-label.json"]["sha256"],
                    },
                    "original_state":before_state,
                    "qualified_obligations":[
                        {"type":"K8S_REGISTERED_POD_CREATE",
                         "qualified":True,"pod_serviceaccount":sa},
                        {"type":"K8S_BINDING_NAMESPACE_SELECTOR",
                         "qualified":selector_match,
                         "binding_selector":selector},
                        {"type":"K8S_RESTRICTED_CEL_VALIDATION",
                         "qualified":passes_cel,
                         "predicate":"serviceAccountName != flux"},
                        {"type":"K8S_NATIVE_NAMESPACE_ACTION",
                         "qualified":changed if phase!="current" else True,
                         "before_revision":ns_before["resource_version"],
                         "after_revision":ns_after["resource_version"]},
                    ],
                    "action":"DRY_RUN_POD_CREATE_"+probe.upper(),
                    "outcome":source_effect,
                    "native_observation":native_effect,
                    "successor_state":before_state,
                    "native_successor":before_state,
                    "checker_outcome":("VERIFIED" if verified else
                        "UNSUPPORTED" if native_effect==
                        "NATIVE_ORACLE_AMBIGUOUS" else "MISMATCH"),
                    "verifier_domain":"K8S_VAP_SELECTOR_CEL_LABEL_ACTION_SOURCE_RECHECK",
                    "provenance":{
                        "source_artifact_id":11604865804,
                        "native_artifact_id":11604423996,
                        "cluster_context":ctx,
                    },
                })

    check(len(certs)==8 and all_controls==4 and resource_updates==2,
          "K8S_NATIVE_C0_EXPECTED_DENOMINATOR_NOT_MET")
    return {
        "schema":"eeq-r4-c0-k8s-certificates-v0",
        "certificates":certs,
        "unbound_controls_verified":all_controls,
        "actual_native_namespace_updates_verified":resource_updates,
        "native_calls_in_c0":0,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--native-a",required=True)
    p.add_argument("--native-b",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    result=build(a.source,a.native_a,a.native_b)
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",
                           encoding="utf-8")
    from collections import Counter
    print(json.dumps({
        "certificates":len(result["certificates"]),
        "outcomes":dict(Counter(
            x["checker_outcome"] for x in result["certificates"])),
        "native_label_mutation_controls":
            result["actual_native_namespace_updates_verified"],
        "native_calls":0,
    },sort_keys=True))


if __name__=="__main__":
    main()
