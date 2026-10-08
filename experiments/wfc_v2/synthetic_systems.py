#!/usr/bin/env python3
"""Declared synthetic lawfully-observable transition systems for WFC v2.

Nothing from the G5 ledger, GitHub native labels, X.509 or in-toto holdouts
is loaded here. This is controlled structural stress, not production data.
"""
import hashlib
import json

from lawful_quotient import SCHEMA

SEED = 20261008

def _fraction(*parts):
    s = "|".join(str(x) for x in parts).encode("utf-8")
    n = int.from_bytes(hashlib.sha256(s).digest()[:8], "big")
    return n / float(2**64)

def generate_system(sources=8, claims=3, actions=3, density=0.40,
                    contracts=2, state_count=64, seed=SEED):
    for name, value in (("sources",sources),("claims",claims),("actions",actions),
                        ("contracts",contracts),("state_count",state_count)):
        if type(value) is not int or value < 1:
            raise ValueError("invalid " + name)
    if state_count % 4:
        raise ValueError("state_count must be divisible by 4 for clone control")
    if not (0.0 < density <= 1.0):
        raise ValueError("density must be in (0,1]")
    claim_ids = ["claim-%02d" % i for i in range(claims)]
    source_ids = ["source-%02d" % i for i in range(sources)]
    acts = ["action-%02d" % i for i in range(actions)]
    catalog = []
    for si, source_id in enumerate(source_ids):
        attached = [
            claim for ci, claim in enumerate(claim_ids)
            if _fraction(seed, "binding", si, ci) < density
        ]
        if not attached:
            attached = [claim_ids[si % claims]]
        catalog.append({
            "id": source_id,
            "claims": attached,
            "identity_provenance_available": True,
        })
    ctrs = []
    for ci in range(contracts):
        ctrs.append({
            "id": "contract-%02d" % ci,
            "claims": claim_ids,
            "min_support": 1 + (ci % 2),
            "audit_provenance": ci % 2 == 1,
        })
    # Four history/serialization replicas of each semantic bucket. The
    # generated transition graph never depends on the replica index.
    base_states = state_count // 4
    states = []
    for index in range(state_count):
        bucket = index % base_states
        replica = index // base_states
        qualification = {}
        for si, source_id in enumerate(source_ids):
            x = _fraction(seed, "auth", bucket, si)
            y = _fraction(seed, "qual", bucket, si)
            authenticated = None if x < 0.06 else (x < 0.88)
            authorized = None if y < 0.06 else (y < density)
            qualification[source_id] = {
                "authenticated": authenticated,
                "authorized": authorized,
            }
        next_states = {}
        for ai, action in enumerate(acts):
            shift = (ai + 1) * (ai + 2) // 2
            next_bucket = (bucket + shift) % base_states
            next_states[action] = "s%03d" % (replica * base_states + next_bucket)
        states.append({
            "id": "s%03d" % index,
            "qualification": qualification,
            "transitions": next_states,
            "irrelevant_metadata": {
                "build_nonce": hashlib.sha256(
                    ("%s:%s:%s" % (seed,index,replica)).encode()).hexdigest(),
                "history_replica": replica,
            },
        })
    return {
        "schema": SCHEMA,
        "evidence_class": "SYNTHETIC",
        "c1_complete": True,
        "c2_complete": True,
        "c3_complete": True,
        "decision_time_visible": True,
        "claims": claim_ids, "actions": acts, "sources": catalog,
        "contracts": ctrs, "states": states,
        "generator": {
            "seed": seed, "sources": sources, "claims": claims,
            "actions": actions, "support_density": density,
            "contracts": contracts, "state_count": state_count,
            "structural_redundancy": "four factual clones per transition bucket",
            "limitation": "mechanically generated graph, not a native-policy history",
        },
    }

def toy_system(audit=False):
    sources = [
        {"id":"A", "claims":["release"], "identity_provenance_available":True},
        {"id":"B", "claims":["release"], "identity_provenance_available":True},
    ]
    # 0/1 are byte-distinct yet contract/future-equivalent; so are 3/6.
    entries = {
        "s0": (True,False,["s3","s0","s0"]),
        "s1": (True,False,["s6","s1","s1"]),
        "s2": (False,True,["s2","s3","s4"]),
        "s3": (False,False,["s3","s3","s0"]),
        "s4": (True,True,["s2","s0","s4"]),
        "s5": (None,False,["s5","s5","s5"]),
        "s6": (False,False,["s6","s6","s1"]),
    }
    actions=["revoke_A","revoke_B","restore_A"]
    states=[]
    for i,(sid,(qa,qb,succ)) in enumerate(entries.items()):
        states.append({
            "id":sid,
            "qualification":{
                "A":{"authenticated":True,"authorized":qa},
                "B":{"authenticated":True,"authorized":qb},
            },
            "transitions":dict(zip(actions,succ)),
            "irrelevant_metadata":{"original_bytes":"noise-%03d" % i},
        })
    return {
        "schema": SCHEMA,
        "evidence_class": "SYNTHETIC",
        "c1_complete": True, "c2_complete": True, "c3_complete": True,
        "decision_time_visible": True,
        "claims": ["release"], "actions": actions,
        "sources": sources,
        "contracts":[{
            "id":"continuation", "claims":["release"],
            "min_support":1, "audit_provenance": audit,
        }],
        "states": states,
        "generator":{"seed":None,"type":"tiny counterexample"},
    }

if __name__ == "__main__":
    raise SystemExit("Use run_scaling.py or frozen tests.")
