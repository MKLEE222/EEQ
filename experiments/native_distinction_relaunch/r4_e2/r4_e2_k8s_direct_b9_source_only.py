#!/usr/bin/env python3
"""Direct source-only K8s hand-engineered B9 reference, WITHOUT generic IR.

Reads the same original pinned native source docs, uses native-documented
matchLabels selector and exact preregistered CEL inequality subset.
Not a new Pod dry-run or independent human engineering trial.
"""
import json
from pathlib import Path
from r4_e2_k8s_source_rule_compile import pinned_native_docs,PHASES

def direct_b9():
    docs=pinned_native_docs()
    out=[]
    for phase,active,installed in PHASES:
        for probe in ("flux","default"):
            denied=False
            namespace=docs["namespace"]["obj"]["metadata"]["labels"]
            service_account=docs[probe+"_pod"]["obj"]["spec"]["serviceAccountName"]
            installed_by_name={docs[p]["obj"]["metadata"]["name"]:docs[p]["obj"]
                               for p in installed}
            for binding_file in active:
                binding=docs[binding_file]["obj"]
                policy=installed_by_name.get(binding["spec"]["policyName"])
                if policy is None:
                    raise ValueError("SOURCE_ONLY_B9_BINDING_REFERENCES_MISSING_POLICY")
                assert binding["spec"]["validationActions"]==["Deny"]
                required=binding["spec"]["matchResources"]["namespaceSelector"]["matchLabels"]
                matched=all(namespace.get(k)==v for k,v in required.items())
                expr=policy["spec"]["validations"][0]["expression"]
                expected_prefix="object.spec.serviceAccountName != '"
                if not (expr.startswith(expected_prefix) and expr.endswith("'")):
                    raise ValueError("SOURCE_ONLY_B9_UNSUPPORTED_CEL")
                forbidden=expr[len(expected_prefix):-1]
                failed=(service_account==forbidden)
                denied=denied or (matched and failed)
            out.append({"case_id":"K8S|"+phase+"|"+probe,
                        "direct_B9_source_only_effect":denied,
                        "native_labels_read":False,
                        "source_closure_externally_attested":False})
    return out

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    out=direct_b9()
    if len(out)!=8:raise ValueError("K8S_B9_SOURCE_ONLY_DENOMINATOR_CHANGED")
    Path(args.out).write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"source_only_k8s_b9_cases":8,"native_calls":0},sort_keys=True))

if __name__=="__main__":main()
