#!/usr/bin/env python3
"""F0 registered logical countermodels: NOT real native API or new v1 G5 cases.

Source and authorization states here are toy finite worlds. Real TUF root
updates and Kubernetes RBAC/policy mutation motivate the problem but their
individual native semantics are NOT claimed to be implemented by this model.
"""
from copy import deepcopy

SCHEMA="eeq-f0-endogenous-observation-formal-dev-v1"
EVIDENCE_CLASS="SOURCE_FREE_SYNTHETIC_FOUNDATIONAL_COUNTERMODEL_ONLY"
WORLD_IDS=("w0","w1")
REGISTERED={
  "I01":{
    "objective":"PRE", "action":"NONE", "mode":"PRESERVE",
    "rooted_grant":False, "pre_bits":[0,1],
    "expected_status":"UNIDENTIFIABLE_WITH_LAWFUL_OBSERVATIONS",
    "expected_groups":1,
    "expected_collision":True,
  },
  "I02":{
    "objective":"PRE", "action":"GRANT_THEN_READ", "mode":"PRESERVE",
    "rooted_grant":True, "pre_bits":[0,1],
    "expected_status":"IDENTIFIABLE_AFTER_NONINTERFERING_INTERVENTION",
    "expected_groups":2,
    "expected_collision":False,
  },
  "I03":{
    "objective":"PRE", "action":"GRANT_THEN_READ", "mode":"OVERWRITE_TRUE",
    "rooted_grant":True, "pre_bits":[0,1],
    "expected_status":"UNIDENTIFIABLE_AFTER_DESTRUCTIVE_INTERVENTION",
    "expected_groups":1,
    "expected_collision":True,
  },
  "I04":{
    "objective":"POST", "action":"GRANT_THEN_READ", "mode":"OVERWRITE_TRUE",
    "rooted_grant":True, "pre_bits":[0,1],
    "expected_status":"CERTAIN_POST_TRUE_NOT_PRE",
    "expected_groups":1,
    "expected_collision":False,
  },
  "I05":{
    "objective":"AUTHORITY_TO_GRANT", "action":"REQUEST_GRANT",
    "mode":"PRESERVE", "rooted_grant":False, "pre_bits":[0,1],
    "expected_status":"ROOTLESS_DELEGATION_REFUSE",
    "expected_groups":0,
    "expected_collision":False,
  },
  "I06":{
    "objective":"GLOBAL_NO_DENY", "action":"READ_VISIBLE_ONLY",
    "mode":"PRESERVE", "rooted_grant":False, "pre_bits":[0,1],
    "visible_deny":0, "independently_closed_inventory":False,
    "expected_status":"GLOBAL_NEGATIVE_NOT_IDENTIFIABLE_WITHOUT_CLOSURE",
    "expected_groups":1,
    "expected_collision":True,
  },
}
# Fixed cyclic delegation: authenticated *statements* with no trusted root
# CANNOT create its own authority. Issuer -> grantee.
DELEGATIONS=(("A","B"),("B","A"))
TRUST_ROOTS=()
REGISTERED_EXPECTED={
  "I01":"UNIDENTIFIABLE_WITH_LAWFUL_OBSERVATIONS",
  "I02":"IDENTIFIABLE_AFTER_NONINTERFERING_INTERVENTION",
  "I03":"UNIDENTIFIABLE_AFTER_DESTRUCTIVE_INTERVENTION",
  "I04":"CERTAIN_POST_TRUE_NOT_PRE",
  "I05":"ROOTLESS_DELEGATION_REFUSE",
  "I06":"GLOBAL_NEGATIVE_NOT_IDENTIFIABLE_WITHOUT_CLOSURE",
}


def scenarios():
    return deepcopy(REGISTERED)


def is_registered(caseid,row):
    return caseid in REGISTERED and isinstance(row,dict) and row==REGISTERED[caseid]
