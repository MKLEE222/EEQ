#!/usr/bin/env python3
"""Build frozen GitHub v2 G6 representations and eeq-adapter-v1 rows.

Representation/adapter construction is label-blind. Native labels are attached
only after the semantic state and all non-B10 representations are built.
"""
import argparse, copy, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

IDS_BASE=[f"B{i}" for i in range(10)]+[f"O{i}" for i in range(1,9)]
PASS_CONCLUSIONS={"success","neutral","skipped"}
DOMAIN="GitHub:v2-governance"

def canon(v):
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def sha(v):
    return hashlib.sha256(canon(v).encode()).hexdigest()

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def strip_rule_provenance(rule):
    return {
        "type":rule.get("type"),
        "parameters":copy.deepcopy(rule.get("parameters") or {}),
    }

def rule_rows(state,typ):
    return [r for r in state.get("effective_rules",[]) if r.get("type")==typ]

def pull_params(state):
    rows=rule_rows(state,"pull_request")
    return copy.deepcopy((rows[0].get("parameters") or {}) if rows else {})

def check_params(state):
    rows=rule_rows(state,"required_status_checks")
    return copy.deepcopy((rows[0].get("parameters") or {}) if rows else {})

def signature_required(state):
    return bool(rule_rows(state,"required_signatures"))

def normalize_check_observations(obs):
    out={}
    for ctx,xs in sorted((obs or {}).items()):
        vals=[]
        for x in xs:
            vals.append({k:x.get(k) for k in ("kind","status","conclusion","app_id","state") if x.get(k) is not None})
        out[ctx]=sorted(vals,key=canon)
    return out

def review_histogram(state):
    return dict(sorted(Counter((state.get("review_states") or {}).values()).items()))

def verification_summary(state):
    return [
        {"verified":v.get("verified"),"reason":v.get("reason")}
        for v in (state.get("commit_verification") or [])
    ]

def required_checks(state):
    p=check_params(state)
    out=[]
    for x in p.get("required_status_checks",[]) or []:
        if x.get("context"):
            out.append({"context":x.get("context"),"integration_id":x.get("integration_id")})
    return sorted(out,key=canon)

def check_qualification(state):
    obs=normalize_check_observations(state.get("merge_check_observations") or {})
    out=[]
    for req in required_checks(state):
        ctx=req["context"]; iid=req.get("integration_id")
        matches=[]
        for x in obs.get(ctx,[]):
            if x.get("kind")=="check_run":
                if iid is None or x.get("app_id")==iid:
                    matches.append(x)
            elif x.get("kind")=="commit_status" and iid is None:
                matches.append(x)
        passed=any(
            (x.get("kind")=="check_run" and x.get("status")=="completed" and x.get("conclusion") in PASS_CONCLUSIONS)
            or (x.get("kind")=="commit_status" and x.get("state")=="success")
            for x in matches
        )
        terminal_bad=any(
            (x.get("kind")=="check_run" and x.get("status")=="completed" and x.get("conclusion") not in PASS_CONCLUSIONS)
            or (x.get("kind")=="commit_status" and x.get("state") in {"failure","error"})
            for x in matches
        )
        out.append({
            **req,
            "observation_count":len(matches),
            "qualified":bool(passed),
            "terminal_failure_observed":bool(terminal_bad),
        })
    return out

def qualification_summary(state):
    pp=pull_params(state)
    observed=len(state.get("visible_approved_reviewers") or [])
    required=int(pp.get("required_approving_review_count") or 0)
    cq=check_qualification(state)
    return {
        "required_approvals":required,
        "observed_approvals":observed,
        "approval_requirement_satisfied":observed>=required,
        "extra_approval_for_unattributed_changes":bool(pp.get("require_extra_approval_for_unattributed_changes",False)),
        "required_checks":cq,
        "required_checks_total":len(cq),
        "required_checks_qualified":sum(x["qualified"] for x in cq),
        "required_checks_missing_or_unqualified":sum(not x["qualified"] for x in cq),
        "signature_required":signature_required(state),
    }

def normalize_semantic_state(raw):
    # Exclude mutable request identifiers. Keep repository/base because the
    # frozen claim binding and governance source are environment-specific.
    rules=copy.deepcopy(raw.get("effective_rules") or [])
    rules=sorted(rules,key=canon)
    state={
        "repo":raw.get("repo"),
        "base":raw.get("base"),
        "registered_actor_class":raw.get("registered_actor_class"),
        "legacy_protection_enabled":raw.get("legacy_protection_enabled"),
        "effective_rules":rules,
        "ruleset_identity":copy.deepcopy(raw.get("ruleset_identity") or {}),
        "review_state_histogram":review_histogram(raw),
        "visible_approved_reviewers_count":len(raw.get("visible_approved_reviewers") or []),
        "merge_check_observations":normalize_check_observations(raw.get("merge_check_observations") or {}),
        "commit_verification":verification_summary(raw),
        "registered_action":raw.get("registered_action"),
        "future_contract":raw.get("future_contract"),
        "native_action_vocabulary":copy.deepcopy(raw.get("native_action_vocabulary") or []),
        "successor_relation":{
            "MERGE_PR":{
                "branch_head":"synthetic_merge_result",
                "governance_continues":True,
            }
        },
        "post_action_observations":{"branch_head":"merge_result"},
        "horizon":["merge_decision","post_merge_branch_governance"],
    }
    state["qualification_summary"]=qualification_summary(raw)
    return state

def controlled_state():
    raw={
        "repo":"MKLEE222/EEQ",
        "base":"main",
        "registered_actor_class":"ORDINARY_NON_BYPASS_MERGER",
        "legacy_protection_enabled":False,
        "effective_rules":[],
        "ruleset_identity":{"id":None,"name":None,"source":"MKLEE222/EEQ"},
        "review_states":{},
        "visible_approved_reviewers":[],
        "merge_check_observations":{},
        "commit_verification":[],
        "registered_action":"MERGE_PR",
        "future_contract":"BRANCH_GOVERNANCE_CONTINUATION",
        "native_action_vocabulary":["NATIVE_ADMISSIBLE","NATIVE_BLOCKED"],
    }
    return raw

def source_provenance(s):
    return {
        "repo":s["repo"],
        "base":s["base"],
        "ruleset_identity":copy.deepcopy(s["ruleset_identity"]),
        "legacy_protection_enabled":s["legacy_protection_enabled"],
    }

def authority_state(s):
    return {
        "registered_actor_class":s["registered_actor_class"],
        "effective_rules":[strip_rule_provenance(r) for r in s["effective_rules"]],
    }

def current_evidence(s):
    return {
        "review_state_histogram":copy.deepcopy(s["review_state_histogram"]),
        "visible_approved_reviewers_count":s["visible_approved_reviewers_count"],
        "merge_check_observations":copy.deepcopy(s["merge_check_observations"]),
        "commit_verification":copy.deepcopy(s["commit_verification"]),
    }

def mechanism_state(s):
    q=s["qualification_summary"]
    return {
        "required_approvals":q["required_approvals"],
        "observed_approvals":q["observed_approvals"],
        "approval_deficit":max(0,q["required_approvals"]-q["observed_approvals"]),
        "required_checks_total":q["required_checks_total"],
        "required_checks_qualified":q["required_checks_qualified"],
        "required_checks_missing_or_unqualified":q["required_checks_missing_or_unqualified"],
        "signature_required":q["signature_required"],
    }

def represent(s):
    # IMPORTANT: no native/expected label input exists in this function.
    r={}
    r["B0"]=copy.deepcopy(s)
    r["B1"]=current_evidence(s)
    r["B2"]={
        "commit_verification":copy.deepcopy(s["commit_verification"]),
        "signature_required":s["qualification_summary"]["signature_required"],
    }
    r["B3"]=authority_state(s)
    r["B4"]=source_provenance(s)
    r["B5"]={"authority":authority_state(s),"provenance":source_provenance(s)}
    b6=copy.deepcopy(s); b6.pop("future_contract",None)
    r["B6"]=b6
    r["B7"]=mechanism_state(s)
    r["B8"]={
        "legacy_protection_enabled":s["legacy_protection_enabled"],
        "registered_actor_class":s["registered_actor_class"],
        **mechanism_state(s),
    }
    r["B9"]={
        "selected":r["B8"],
        "effective_rule_contract":[strip_rule_provenance(x) for x in s["effective_rules"]],
    }

    o1={
        "authority":authority_state(s),
        "evidence":current_evidence(s),
        "qualification_summary":copy.deepcopy(s["qualification_summary"]),
        "registered_action":s["registered_action"],
        "future_contract":s["future_contract"],
        "successor_relation":copy.deepcopy(s["successor_relation"]),
    }
    r["O1"]=o1
    r["O2"]={
        "provenance":source_provenance(s),
        "authority":authority_state(s),
        "registered_action":s["registered_action"],
        "future_contract":s["future_contract"],
    }
    r["O3"]={
        "provenance":source_provenance(s),
        "qualification_summary":copy.deepcopy(s["qualification_summary"]),
        "evidence":current_evidence(s),
        "successor_relation":copy.deepcopy(s["successor_relation"]),
        "future_contract":s["future_contract"],
    }
    r["O4"]={
        "provenance":source_provenance(s),
        "authority":authority_state(s),
        "qualification_summary":copy.deepcopy(s["qualification_summary"]),
        "merge_check_observations":copy.deepcopy(s["merge_check_observations"]),
        "registered_action":s["registered_action"],
        "future_contract":s["future_contract"],
    }
    o5=copy.deepcopy(s); o5.pop("future_contract",None)
    r["O5"]=o5
    o6=copy.deepcopy(s)
    o6["successor_relation"]={"MERGE_PR":{"branch_head":"UNCHANGED_STATIC_MODEL","governance_continues":True}}
    r["O6"]=o6
    o7=copy.deepcopy(s)
    o7["horizon"]=["merge_decision"]
    o7.pop("future_contract",None)
    o7["successor_relation"]={"MERGE_PR":{"branch_head":"merge_result"}}
    r["O7"]=o7
    o8=copy.deepcopy(s)
    o8["effective_rules"]=[x for x in o8["effective_rules"] if x.get("type")!="pull_request"]
    o8["review_state_histogram"]={}
    o8["visible_approved_reviewers_count"]=0
    q=copy.deepcopy(o8["qualification_summary"])
    q["required_approvals"]=0
    q["observed_approvals"]=0
    q["approval_requirement_satisfied"]=True
    q["extra_approval_for_unattributed_changes"]=False
    o8["qualification_summary"]=q
    r["O8"]=o8
    if set(r)!=set(IDS_BASE):
        raise ValueError(f"representation id mismatch {sorted(r)}")
    return r

def state_to_adapter(s):
    # IMPORTANT: no native/expected label input exists in this function.
    claim="github-ordinary-merge-admissible"
    provenance=source_provenance(s)
    review_q=s["qualification_summary"]
    supports=[
        {"id":"governance_policy","source_identity":f"{s['repo']}:{s['base']}:governance",
         "provenance":provenance},
        {"id":"review_evidence","source_identity":f"{s['repo']}:{s['base']}:reviews",
         "provenance":{"review_state_histogram":s["review_state_histogram"]}},
        {"id":"merge_check_evidence","source_identity":f"{s['repo']}:{s['base']}:synthetic-merge-checks",
         "provenance":{"observations":s["merge_check_observations"]}},
        {"id":"commit_verification","source_identity":f"{s['repo']}:{s['base']}:commit-verification",
         "provenance":{"observations":s["commit_verification"]}},
    ]
    compat=[{"claim":claim,"support":x["id"],"compatible":True} for x in supports]
    quals=[
        {"support":"governance_policy","actor_class":s["registered_actor_class"],
         "legacy_protection_enabled":s["legacy_protection_enabled"],
         "effective_rule_contract":[strip_rule_provenance(x) for x in s["effective_rules"]]},
        {"support":"review_evidence",
         "required_approvals":review_q["required_approvals"],
         "observed_approvals":review_q["observed_approvals"],
         "satisfied":review_q["approval_requirement_satisfied"],
         "extra_approval_for_unattributed_changes":review_q["extra_approval_for_unattributed_changes"],
         "review_state_histogram":s["review_state_histogram"]},
        {"support":"merge_check_evidence",
         "required_checks":review_q["required_checks"],
         "required_checks_total":review_q["required_checks_total"],
         "required_checks_qualified":review_q["required_checks_qualified"]},
        {"support":"commit_verification",
         "signature_required":review_q["signature_required"]},
    ]
    auth=[
        {"support":"governance_policy","lawful_source_observed":True},
        {"support":"review_evidence","lawful_source_observed":True},
        {"support":"merge_check_evidence","lawful_source_observed":True},
        {"support":"commit_verification","verification_observations":s["commit_verification"]},
    ]
    binds=[
        {"claim":claim,"support":x["id"],"repo":s["repo"],"base":s["base"],
         "actor_class":s["registered_actor_class"]}
        for x in supports
    ]
    return {
        "schema_version":"eeq-adapter-v1",
        "C1_support_coverage":{
            "claims":[claim],
            "support_items":supports,
            "compatibility":compat,
        },
        "C2_qualification_fidelity":{
            "qualification_predicates":quals,
            "authentication_predicates":auth,
            "claim_binding":binds,
        },
        "C3_transition_objective_fidelity":{
            "actions":[{"id":"MERGE_PR","actor_class":s["registered_actor_class"]}],
            "successor_relation":copy.deepcopy(s["successor_relation"]),
            "post_action_observations":copy.deepcopy(s["post_action_observations"]),
            "continuation_contract":{
                "id":s["future_contract"],
                "repo":s["repo"],
                "base":s["base"],
                "governance_continues":True,
            },
            "native_action_vocabulary":copy.deepcopy(s["native_action_vocabulary"]),
        },
    }

def build(validation,controlled,base_out,adapter_out):
    vd=load(validation); cd=load(controlled)
    candidates=[]
    for row in vd["rows"]:
        if row.get("adapter_status")!="PREDICTED_C1_COMPLETE":
            continue
        if row.get("native_label") not in {"NATIVE_ADMISSIBLE","NATIVE_BLOCKED"}:
            continue
        candidates.append({
            "provenance":{"repo":row["repo"],"pr":row["pr"]},
            "raw_state":row["v0_c1_c2_c3"],
            "native_action":row["native_label"],
        })

    candidates.append({
        "provenance":{"repo":cd["repository"],"pr":cd["pr_number"]},
        "raw_state":controlled_state(),
        "native_action":cd["native_observation"]["native_label"],
    })

    groups=defaultdict(list)
    for c in candidates:
        state=normalize_semantic_state(c["raw_state"])
        groups[canon(state)].append((c,state))

    base_rows=[]; adapter_rows=[]
    conflicts=[]
    for key,items in sorted(groups.items(),key=lambda kv:kv[0]):
        labels=sorted({c["native_action"] for c,_ in items})
        if len(labels)!=1:
            conflicts.append({
                "semantic_state_sha256":hashlib.sha256(key.encode()).hexdigest(),
                "labels":labels,
                "provenance":[c["provenance"] for c,_ in items],
            })
            continue
        c,state=items[0]
        sid="github-v2:"+hashlib.sha256(key.encode()).hexdigest()
        reps=represent(state)
        adapter=state_to_adapter(state)
        base_rows.append({
            "semantic_id":sid,"domain":DOMAIN,"native_action":labels[0],
            "representations":reps,"not_applicable_reasons":{},
            "source_executions":[x[0]["provenance"] for x in items],
        })
        adapter_rows.append({
            "semantic_id":sid,"domain":DOMAIN,"native_action":labels[0],
            "adapter":adapter,
            "source_executions":[x[0]["provenance"] for x in items],
        })

    if conflicts:
        raise ValueError("semantic-equivalence native-label conflicts: "+json.dumps(conflicts,sort_keys=True))
    payload={
        "schema":"eeq-github-v2-base-representations-v1",
        "status":"development post-native/pre-matrix; representation construction is label-blind",
        "rows":base_rows,
        "raw_execution_candidates":len(candidates),
        "unique_semantic_cases":len(base_rows),
    }
    Path(base_out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    Path(adapter_out).write_text(json.dumps({
        "schema":"eeq-github-v2-adapters-v1",
        "rows":adapter_rows,
        "raw_execution_candidates":len(candidates),
        "unique_semantic_cases":len(adapter_rows),
    },indent=2,sort_keys=True)+"\n")
    print(json.dumps({"raw_candidates":len(candidates),"unique_semantic_cases":len(base_rows),
                      "labels":dict(Counter(r["native_action"] for r in base_rows))},sort_keys=True))

def join(base,b10,out):
    b=load(base); g=load(b10)
    gm={r["semantic_id"]:r for r in g["rows"]}
    rows=[]
    for row in b["rows"]:
        sid=row["semantic_id"]
        if sid not in gm: raise ValueError(f"missing generic B10 {sid}")
        if gm[sid]["native_action"]!=row["native_action"]:
            raise ValueError(f"native action mismatch {sid}")
        x=copy.deepcopy(row)
        x["representations"]["B10"]=gm[sid]["representations"]["B10"]
        expected={f"B{i}" for i in range(11)}|{f"O{i}" for i in range(1,9)}
        if set(x["representations"])!=expected:
            raise ValueError(f"19-ID mismatch {sid}")
        rows.append(x)
    Path(out).write_text(json.dumps({
        "schema":"eeq-github-v2-g6-representations-v1",
        "rows":rows,
        "generic_b10":"frozen WFC v1",
    },indent=2,sort_keys=True)+"\n")
    print(json.dumps({"rows":len(rows),"ids":19},sort_keys=True))

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)
    b=sub.add_parser("build")
    b.add_argument("--validation",required=True)
    b.add_argument("--controlled",required=True)
    b.add_argument("--base-out",required=True)
    b.add_argument("--adapter-out",required=True)
    j=sub.add_parser("join")
    j.add_argument("--base",required=True)
    j.add_argument("--b10",required=True)
    j.add_argument("--out",required=True)
    a=ap.parse_args()
    if a.cmd=="build":
        build(a.validation,a.controlled,a.base_out,a.adapter_out)
    else:
        join(a.base,a.b10,a.out)

if __name__=="__main__":
    main()
