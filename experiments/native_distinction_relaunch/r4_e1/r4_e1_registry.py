#!/usr/bin/env python3
"""R4-E1: immutable PRE-CODE synthetic registry, no TUF/K8s native labels.

Finite Boolean atoms denote ALREADY QUALIFIED native-source predicates,
not original signature bytes or global API source-inventory completeness.
This module only models the *registered* bounded hypothetical contracts.
"""
import copy
from types import MappingProxyType

SCHEMA="eeq-r4-e1-synthetic-authorized-source-probe-v1"
TUF_SCOPE="TUF_ROOT2_TO_ROOT3_DUAL_THRESHOLD_POST_QUALIFICATION"
K8S_FLUX_SCOPE="K8S_FLUX_POD_REGISTERED_TWO_BINDING_DENY_ONLY"
K8S_DEFAULT_SCOPE="K8S_DEFAULT_POD_REGISTERED_AND_POSSIBLE_EXTRA_DENY"
ACTOR="REGISTERED_HYPOTHETICAL_ACTOR_NOT_NATIVE_RBAC_ATTESTED"
ASSUMPTION="AUTHOR_REGISTERED_FINITE_SOURCE_ROSTER_NOT_EXTERNALLY_COMPLETE"
COSTS={"old":1,"new":1,"team":1,"mode":1,"third":1,"additional":3}
PROGRAMS={
 "TUF":{"domain":"TUF","scope":TUF_SCOPE,"formula":"AND","atoms":("old","new"),
        "true_effect":"AUTHORIZED_ROOT_UPDATE","false_effect":"REJECT_ROOT_UPDATE"},
 "K8S_FLUX":{"domain":"K8S","scope":K8S_FLUX_SCOPE,"formula":"OR",
             "atoms":("team","mode"),"true_effect":"SCOPED_VAP_DENY",
             "false_effect":"NO_REGISTERED_VAP_DENY"},
 "K8S_DEFAULT":{"domain":"K8S","scope":K8S_DEFAULT_SCOPE,"formula":"OR",
             "atoms":("third","additional"),"true_effect":"SCOPED_VAP_DENY",
             "false_effect":"NO_REGISTERED_VAP_DENY"},
}
# Observations: 1=verified TRUE, 0=verified FALSE, ?=not yet observed.
# Permitted IDs are actor-authorized hypothetical observation actions.
ROWS=[
 ("T01","TUF",{"old":"?","new":1},()),
 ("T02","TUF",{"old":0,"new":"?"},()),
 ("T03","TUF",{"old":1,"new":"?"},("new",)),
 ("T04","TUF",{"old":"?","new":"?"},("old","new")),
 ("T05","TUF",{"old":"?","new":"?"},()),
 ("T06","TUF",{"old":1,"new":1},()),
 ("T07","TUF",{"old":0,"new":1},()),
 ("T08","TUF",{"old":1,"new":1},()),
 ("K01","K8S_FLUX",{"team":"?","mode":"?"},("team","mode")),
 ("K02","K8S_FLUX",{"team":1,"mode":"?"},()),
 ("K03","K8S_FLUX",{"team":0,"mode":"?"},()),
 ("K04","K8S_DEFAULT",{"third":"?","additional":0},()),
 ("K05","K8S_DEFAULT",{"third":0,"additional":"?"},()),
 ("K06","K8S_DEFAULT",{"third":0,"additional":0},()),
 ("K07","K8S_DEFAULT",{"third":1,"additional":"?"},()),
 ("K08","K8S_DEFAULT",{"third":"?","additional":0},("third",)),
 ("K09","K8S_DEFAULT",{"third":"?","additional":"?"},("third","additional")),
]
FROZEN_STATUS_COUNTS={
 "CERTAIN_TRUE":4,
 "CERTAIN_FALSE":3,
 "GUARANTEED_RESOLVABLE":5,
 "IMPOSSIBLE_UNDER_ACTOR_ACCESS":5,
}
EXPECTATIONS={
 "T01":("IMPOSSIBLE_UNDER_ACTOR_ACCESS",None),
 "T02":("CERTAIN_FALSE",0),
 "T03":("GUARANTEED_RESOLVABLE",1),
 "T04":("GUARANTEED_RESOLVABLE",2),
 "T05":("IMPOSSIBLE_UNDER_ACTOR_ACCESS",None),
 "T06":("CERTAIN_TRUE",0),
 "T07":("CERTAIN_FALSE",0),
 "T08":("CERTAIN_TRUE",0),
 "K01":("GUARANTEED_RESOLVABLE",2),
 "K02":("CERTAIN_TRUE",0),
 "K03":("IMPOSSIBLE_UNDER_ACTOR_ACCESS",None),
 "K04":("IMPOSSIBLE_UNDER_ACTOR_ACCESS",None),
 "K05":("IMPOSSIBLE_UNDER_ACTOR_ACCESS",None),
 "K06":("CERTAIN_FALSE",0),
 "K07":("CERTAIN_TRUE",0),
 "K08":("GUARANTEED_RESOLVABLE",1),
 "K09":("GUARANTEED_RESOLVABLE",4),
}
TOTAL_COST_SUM={"T04":6,"K01":6,"K09":10}


def registry():
    result=[]
    for id_,program_id,observed,allowed in ROWS:
        p=PROGRAMS[program_id]
        s={
           "schema":SCHEMA,"case_id":id_,
           "program_id":program_id,"family":p["domain"],
           "registered_scope":p["scope"],
           "registered_actor":ACTOR,
           "closure_basis":ASSUMPTION,
           "formula":p["formula"],
           "atoms":list(p["atoms"]),
           "observed":copy.deepcopy(observed),
           "lawful_reads":list(allowed),
           "read_costs":{k:COSTS[k] for k in p["atoms"]},
           "true_effect":p["true_effect"],
           "false_effect":p["false_effect"],
           "native_source_bytes_read":False,
           "externally_attested_authority":False,
           "native_actor_rbac_proven":False,
        }
        result.append(s)
    return result


def immutable_case(case_id):
    for row in registry():
        if row["case_id"]==case_id:return row
    raise ValueError("UNREGISTERED_E1_CASE:"+str(case_id))


def registered_input_check(s):
    if not isinstance(s,dict) or s.get("case_id") not in EXPECTATIONS:
        return False
    return s==immutable_case(s["case_id"])
