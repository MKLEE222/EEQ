#!/usr/bin/env python3
"""R3-M3 V2B read-only native API default normalization on archived evidence.

This is explicitly POST-NATIVE, never a prescored independent experiment.
ONLY six specified server-added default values are removable from a COPY
of each policy or binding spec; exact source equality required afterwards.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

FILES={
 "eeq-r3-flux-deny":"policy.json",
 "eeq-r3-m3-default-deny":"policy-third.json",
 "eeq-r3-binding-team":"binding-team.json",
 "eeq-r3-binding-mode":"binding-mode.json",
 "eeq-r3-m3-binding-third":"binding-third.json"
}
POLICY_NAMES={"eeq-r3-flux-deny","eeq-r3-m3-default-deny"}
PHASES={"T0_OLD_TWO_BINDINGS","T1_THIRD_POLICY_UNBOUND",
 "T2_THIRD_BINDING_ACTIVE","T3_THIRD_BINDING_REMOVED"}
CHECKED_DEFAULTS={
 "policy":{
  ("matchConstraints","matchPolicy"):"Equivalent",
  ("matchConstraints","namespaceSelector"):{},
  ("matchConstraints","objectSelector"):{},
 },
 "binding":{
  ("matchResources","matchPolicy"):"Equivalent",
  ("matchResources","objectSelector"):{}
 }
}

def fail(msg):
    raise ValueError(msg)

def sha(x):
    return hashlib.sha256(x).hexdigest()

def path_get(obj,path):
    node=obj
    for key in path:
        if not isinstance(node,dict) or key not in node:
            return False,None
        node=node[key]
    return True,node

def pop_one_default(source,live,path,value):
    present_original,_=path_get(source,path)
    has_native,native_val=path_get(live,path)
    if present_original:
        return None
    if not has_native:
        return None
    if native_val!=value:
        fail("UNRECOGNIZED_OR_MATERIAL_SERVER_DEFAULT_"+"/".join(path))
    parent=live
    for p in path[:-1]:
        if not isinstance(parent,dict) or p not in parent:
            fail("BAD_SERVER_DEFAULT_CONTAINER_"+"/".join(path))
        parent=parent[p]
    del parent[path[-1]]
    return ".".join(path)

def normalize_spec(source,live,kind):
    if kind not in CHECKED_DEFAULTS:
        fail("NOT_REGISTERED_NATIVE_SOURCE_KIND")
    output=copy.deepcopy(live)
    normalized=[]
    for path,value in CHECKED_DEFAULTS[kind].items():
        removed=pop_one_default(source,output,path,value)
        if removed:normalized.append(removed)
    if kind=="policy":
        rules_orig=source.get("matchConstraints",{}).get("resourceRules")
        rules_live=output.get("matchConstraints",{}).get("resourceRules")
        if (not isinstance(rules_orig,list) or not rules_orig or
            not isinstance(rules_live,list) or
            len(rules_orig)!=len(rules_live)):
            fail("NATIVE_POLICY_RULE_SCOPE_OR_LENGTH_DRIFT")
        for i,(orig,parsed) in enumerate(zip(rules_orig,rules_live)):
            if "scope" not in orig and "scope" in parsed:
                if parsed["scope"]!="*":
                    fail("UNKNOWN_POLICY_SCOPE_DEFAULT")
                del parsed["scope"]
                normalized.append("matchConstraints.resourceRules["+str(i)+"].scope")
    if output!=source:
        fail("SOURCE_VS_NATIVE_MATERIAL_SPEC_DRIFT_"+kind+
             ":source="+json.dumps(source,sort_keys=True)+
             ":native="+json.dumps(output,sort_keys=True))
    return output,normalized

def run(source_dir,manifest,native_raw,native_sha_expected=None):
    originals={}
    source_dir=Path(source_dir)
    sources=manifest["sources"]
    if (manifest.get("schema")!="eeq-r3-m3-source-manifest-v1" or
        len(sources)!=8):
        fail("SOURCE_MANIFEST_SCHEMA_OR_COUNT_INVALID")
    for ent in sources:
        raw=(source_dir/ent["name"]).read_bytes()
        if sha(raw)!=ent["sha256"] or len(raw)!=ent["bytes"]:
            fail("SOURCE_SHA_MISMATCH_"+ent["name"])
        originals[ent["name"]]=json.loads(raw)
    if set(FILES.values())-set(originals):
        fail("MISSING_REGISTERED_SOURCE")
    if native_raw.get("schema")!="eeq-r3-m3-native-third-membership-v1":
        fail("NATIVE_SCHEMA_CHANGED")
    if (native_raw.get("source_predictions_read") is not False or
        native_raw.get("error") is not None or
        len(native_raw.get("observed_cases",[]))!=8 or
        len(native_raw.get("control_rows",[]))!=2 or
        len(native_raw.get("native_membership_actions",[]))!=3 or
        len(native_raw.get("phase_inventories",[]))!=4):
        fail("NATIVE_CASES_OR_ERROR_CHANGED")
    if native_raw.get("source_digest_map")!={
            ent["name"]:ent["sha256"] for ent in sources}:
        fail("NATIVE_SOURCE_IDENTITY_OR_HASH_TAMPER")
    duplicate=set()
    by_phase=set()
    result=copy.deepcopy(native_raw)
    audit=[]
    for phase in result["phase_inventories"]:
        phase_id=phase["phase"]
        if phase_id not in PHASES or phase_id in by_phase:
            fail("NATIVE_PHASE_SET_OR_DUPLICATE")
        by_phase.add(phase_id)
        collections=(("policy_items","policy"),
                     ("binding_items","binding"))
        for coll,kind in collections:
            for live in phase["native_inventory"][coll]:
                objname=live["name"]
                if objname not in FILES:
                    fail("UNKNOWN_ADMISSION_SOURCE_"+objname)
                if (objname in POLICY_NAMES)!=(kind=="policy"):
                    fail("NATIVE_SOURCE_CATEGORY_CHANGED_"+objname)
                if (phase_id,coll,objname) in duplicate:
                    fail("DUPLICATE_NATIVE_SOURCE")
                duplicate.add((phase_id,coll,objname))
                original=originals[FILES[objname]]
                edited,removed=normalize_spec(original["spec"],live["spec"],kind)
                live["spec"]=edited
                audit.append({"phase":phase_id,"source_name":objname,
                    "source_file":FILES[objname],"removed_defaults":removed,
                    "source_sha256":next(x["sha256"] for x in sources
                                           if x["name"]==FILES[objname])})
    if by_phase!=PHASES:
        fail("INCOMPLETE_NATIVE_PHASE_SET")
    # No Pod effects, controls, native action evidence, source digests,
    # UID and resourceVersions can be altered by the default normalizer.
    for field in ("observed_cases","control_rows",
                  "native_membership_actions",
                  "source_digest_map","source_manifest_sha256"):
        if result[field]!=native_raw[field]:
            fail("FORBIDDEN_NATIVE_EVIDENCE_MUTATION_"+field)
    for a,b in zip(native_raw["phase_inventories"],result["phase_inventories"]):
        for field in ("policy_list_resource_version",
                      "binding_list_resource_version"):
            if a["native_inventory"][field]!=b["native_inventory"][field]:
                fail("NATIVE_COLLECTION_RV_TAMPER")
        for coll in ("policy_items","binding_items"):
            a_items=a["native_inventory"][coll]
            b_items=b["native_inventory"][coll]
            if len(a_items)!=len(b_items):
                fail("NATIVE_SOURCE_INVENTORY_MEMBER_REMOVED")
            for first,second in zip(a_items,b_items):
                for key in ("name","uid","resource_version","spec_sha256"):
                    if first[key]!=second[key]:
                        fail("NATIVE_SOURCE_IDENTITY_TAMPER_"+key)
    return result,{
        "schema":"eeq-r3-m3-v2b-default-equivalence-audit-v1",
        "evidence_class":"POST_NATIVE_RETROSPECTIVE_DIAGNOSTIC",
        "original_v2_science_gate":"FAILURE_UNCHANGED",
        "original_native_rows_count":8,"native_calls":0,
        "source_records_reexamined":len(audit),
        "normalization_records":audit,
        "material_source_spec_differences_after_narrow_normalization":0,
        "normalization_does_not_validate_global_C1":True,
        "full_B9_can_use_same_default_semantics":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--native",required=True)
    p.add_argument("--out-copy",required=True)
    p.add_argument("--out-audit",required=True)
    a=p.parse_args()
    raw=Path(a.native).read_bytes()
    original=json.loads(raw)
    manifest=json.loads(Path(a.manifest).read_text())
    copy_result,audit=run(a.source_dir,manifest,original)
    audit["immutable_original_native_raw_sha256"]=sha(raw)
    output=json.dumps(copy_result,indent=2,sort_keys=True)+"\n"
    audit["normalized_copy_sha256"]=sha(output.encode())
    Path(a.out_copy).write_text(output)
    Path(a.out_audit).write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "original_native_raw_sha256":sha(raw),
        "source_objects_audited":audit["source_records_reexamined"],
        "defaulted_fields_removed":sum(
            len(x["removed_defaults"]) for x in audit["normalization_records"]),
        "source_material_mismatches_after_check":0,
        "new_native_calls":0,
        "original_v2_gate":"FAILURE_UNCHANGED"
    },sort_keys=True))

if __name__=="__main__":
    main()
