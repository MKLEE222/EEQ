#!/usr/bin/env python3
"""Emit the frozen G7 X.509 holdout adapter instances.

Reads only frozen source metadata and case contracts. The prediction file and
native OpenSSL outcomes are deliberately not inputs.
"""
import argparse
import datetime as dt
import json
from pathlib import Path

CLAIM="x509-server-identity-valid"
PURPOSE_KEYS={
    "sslserver":"ssl_server",
    "sslclient":"ssl_client",
    "timestampsign":"time_stamp_signing",
}

def parse_openssl_time(s):
    return dt.datetime.strptime(s, "%b %d %H:%M:%S %Y GMT").replace(tzinfo=dt.timezone.utc)

def merge_case(common, row):
    out=dict(common)
    out.update(row)
    return out

def emit(case, sources):
    target=sources["target_leaf"]
    trust_name=case.get("trust_source")
    trust=sources.get(trust_name) if trust_name else None

    when=dt.datetime.fromtimestamp(int(case["attime"]),tz=dt.timezone.utc)
    nb=parse_openssl_time(target["not_before"])
    na=parse_openssl_time(target["not_after"])
    time_ok=nb <= when <= na

    hostname=case["hostname"]
    hostname_ok=hostname in target.get("san_dns",[])

    purpose=case["purpose"]
    pk=PURPOSE_KEYS.get(purpose)
    purpose_ok=bool(pk and target.get("purposes",{}).get(pk) is True)

    trust_present=trust is not None
    trust_correct=trust_name=="correct_trust_anchor"
    trust_ca=bool(trust and trust.get("basic_constraints")=="CA:TRUE")
    issuer_match=bool(trust and target.get("issuer")==trust.get("subject"))

    target_support={
        "id":"target-leaf",
        "source_identity":target["sha256_fingerprint"],
        "provenance":target["path"],
        "sha256":target["sha256"],
    }
    if trust:
        trust_support={
            "id":"selected-trust-source",
            "source_identity":trust["sha256_fingerprint"],
            "provenance":trust["path"],
            "sha256":trust["sha256"],
        }
    else:
        trust_support={
            "id":"selected-trust-source",
            "source_identity":"__MISSING_TRUST_SOURCE__",
            "provenance":"explicitly absent in frozen case contract",
            "sha256":None,
        }

    adapter={
      "schema_version":"eeq-adapter-v1",
      "validity_boundary":{"V0_lawful_information":True},
      "C1_support_coverage":{
        "claims":[CLAIM],
        "support_items":[target_support,trust_support],
        "compatibility":[
          {"claim":CLAIM,"support":"target-leaf","compatible":True},
          {"claim":CLAIM,"support":"selected-trust-source","compatible":trust_correct},
        ],
      },
      "C2_qualification_fidelity":{
        "qualification_predicates":[
          {"id":"hostname-san-match","support":"target-leaf","value":hostname_ok,
           "hostname":hostname,"registered_san":target.get("san_dns",[])},
          {"id":"verification-time-in-target-validity","support":"target-leaf","value":time_ok,
           "attime":case["attime"],"not_before":target["not_before"],"not_after":target["not_after"]},
          {"id":"target-purpose-compatible","support":"target-leaf","value":purpose_ok,
           "purpose":purpose},
          {"id":"trust-source-present","support":"selected-trust-source","value":trust_present},
          {"id":"registered-trust-source-selected","support":"selected-trust-source","value":trust_correct},
          {"id":"trust-source-ca-qualified","support":"selected-trust-source","value":trust_ca},
          {"id":"target-issuer-matches-trust-subject","support":"selected-trust-source","value":issuer_match,
           "target_issuer":target.get("issuer"),"trust_subject":trust.get("subject") if trust else None},
        ],
        "authentication_predicates":[
          {"id":"target-bytes-pinned","support":"target-leaf","value":bool(target.get("sha256"))},
          {"id":"trust-bytes-pinned","support":"selected-trust-source",
           "value":bool(trust and trust.get("sha256"))},
        ],
        "claim_binding":[
          {"claim":CLAIM,"support":"target-leaf",
           "target_fingerprint":target["sha256_fingerprint"],
           "hostname":hostname,"purpose":purpose,"attime":case["attime"]},
          {"claim":CLAIM,"support":"selected-trust-source",
           "trust_source":trust_name,
           "trust_fingerprint":trust.get("sha256_fingerprint") if trust else None},
        ],
      },
      "C3_transition_objective_fidelity":{
        "actions":["VERIFY_X509_TLS_SERVER"],
        "successor_relation":{
          "verification_context_id":case["case_id"],
          "target_fingerprint":target["sha256_fingerprint"],
        },
        "post_action_observations":{},
        "continuation_contract":{
          "contract_id":"X509_TLS_SERVER_IDENTITY_CONTINUATION",
          "hostname":hostname,
          "purpose":purpose,
          "attime":case["attime"],
          "auth_level":case["auth_level"],
          "trust_source":trust_name,
          "disable_default_CAfile":bool(case.get("disable_default_CAfile",False)),
          "disable_default_CApath":bool(case.get("disable_default_CApath",False)),
          "disable_default_CAstore":bool(case.get("disable_default_CAstore",False)),
        },
        "native_action_vocabulary":["ACCEPT","REJECT"],
      },
    }
    return adapter

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("metadata",type=Path)
    ap.add_argument("cases",type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()

    meta=json.loads(args.metadata.read_text())
    cfg=json.loads(args.cases.read_text())
    sources=meta["sources"]
    rows=[]
    for raw in cfg["cases"]:
        case=merge_case(cfg["common_contract"],raw)
        case["case_id"]=raw["case_id"]
        rows.append({
          "case_id":case["case_id"],
          "domain":"OpenSSL:X509-path-validation",
          "adapter":emit(case,sources),
          "native_command_contract":{
            "target_source":case["target_source"],
            "trust_source":case.get("trust_source"),
            "hostname":case["hostname"],
            "attime":case["attime"],
            "purpose":case["purpose"],
            "auth_level":case["auth_level"],
            "disable_default_CAfile":bool(case.get("disable_default_CAfile",False)),
            "disable_default_CApath":bool(case.get("disable_default_CApath",False)),
            "disable_default_CAstore":bool(case.get("disable_default_CAstore",False)),
          },
        })
    if len(rows)!=7 or len({r["case_id"] for r in rows})!=7:
        raise ValueError("expected seven unique holdout cases")
    args.out.write_text(json.dumps({
      "schema":"eeq-x509-holdout-adapter-instance-set-v1",
      "rows":rows,
      "prediction_file_read":False,
      "native_outcome_read":False,
    },indent=2,sort_keys=True)+"\n")
    print(json.dumps({"rows":len(rows),"domain":"OpenSSL:X509-path-validation"},sort_keys=True))

if __name__=="__main__":
    main()
