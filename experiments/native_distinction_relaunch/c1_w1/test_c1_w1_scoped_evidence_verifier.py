#!/usr/bin/env python3
"""C1-W1 16 pre-registered synthetic adversarial cursor tests; NO live native evidence."""
import copy,unittest,urllib.parse
from c1_w1_source_only import registered_forecast
from c1_w1_scoped_evidence_verifier import (
 CLASSES,STAGES,EVENT_SPEC,EXPECTED,ORIGINAL_POLICIES,ORIGINAL_BINDINGS,
 THIRD_POLICY,THIRD_BINDING,verify,relist_after_gap,
)

FORECAST=registered_forecast()[1]
CONTRACT="TWO_VAP_COLLECTIONS_SCOPED_SOURCE_CURSOR"


def item(kind,name,uid=None):
    return {
      "apiVersion":"admissionregistration.k8s.io/v1",
      "kind":CLASSES[kind]["item_kind"],
      "metadata":{"name":name,"uid":uid or ("uid-"+name),
                  "resourceVersion":"item-"+name},
      "spec":{"policyName":"eeq-r3-flux-deny"} if kind=="binding"
             else {"validations":[{"expression":"true"}]}
    }


def make_nominal():
    cp=[]
    for i,step in enumerate(STAGES):
        classes={}
        for kind in CLASSES:
            names=EXPECTED[step][kind]
            classes[kind]={
                "request_path":CLASSES[kind]["path"],
                "selector":"","limit":None,
                "response":{
                    "kind":CLASSES[kind]["kind"],
                    "apiVersion":"admissionregistration.k8s.io/v1",
                    "metadata":{"resourceVersion":("RV-P"+str(i)
                       if kind=="policy" else "RV-B"+str(i)),"continue":""},
                    "items":[item(kind,name) for name in names],
                }
            }
        cp.append({"step":step,"collections":classes})
    events=[]
    for step,kind,etype,name in EVENT_SPEC:
        obj=item(kind,name)
        events.append({"step":step,"source_class":kind,
                       "event":{"type":etype,"object":obj},
                       "received_source":"genuine_http_watch_stream_via_kubectl_proxy"})
    watches={}
    for kind in CLASSES:
        watches[kind]={
            "request_path":CLASSES[kind]["path"],
            "resourceVersion":cp[0]["collections"][kind]["response"]["metadata"]["resourceVersion"],
            "status":"STOPPED_AFTER_REGISTERED_EVENTS",
            "error":None,"used_allow_watch_bookmarks":True,
            "request_query":urllib.parse.urlencode({
              "watch":"1",
              "resourceVersion":cp[0]["collections"][kind]["response"]["metadata"]["resourceVersion"],
              "allowWatchBookmarks":"true","timeoutSeconds":"150"}),
        }
    return {
        "schema":"eeq-c1-w1-native-list-watch-capture-v1",
        "source_predictions_file_read":False,
        "requested_contract":CONTRACT,
        "global_admission_accept_claimed":False,
        "cross_class_atomic_snapshot_claimed":False,
        "native_pod_decision_calls":0,
        "actor":{"context":"kind-synthetic-c1-w1",
                 "authorized_native_permissions":{
                    "policy":{"list":True,"watch":True},
                    "binding":{"list":True,"watch":True}}},
        "checkpoints":cp,"watches":watches,"watch_events":events,
        "mutations":[{"action":a,"exit_code":0,
                      "native_mutation_registered":True}
                     for a in ("CREATE_THIRD_POLICY","CREATE_THIRD_BINDING",
                               "DELETE_THIRD_BINDING")]
    }


class FixedC1W1SyntheticAdversaries(unittest.TestCase):
    def setUp(self):
        self.x=make_nominal()

    def status(self):
        return verify(self.x,FORECAST)["status"]

    def test_T01_healthy_list_to_watch_is_only_a_scoped_prefix(self):
        r=verify(self.x,FORECAST)
        self.assertEqual(r["status"],"C1_W1_SCOPED_NATIVE_LIST_WATCH_FEASIBILITY_B9_TIE")
        self.assertEqual(r["prefix_reconstruction"],"PREFIX_WITNESSED")
        self.assertFalse(r["global_admission_accept_certified"])
        self.assertEqual((r["watch_event_matched"],
                          r["source_class_snapshots_matched"]),(3,8))

    def test_T02_binding_addition_revokes_earlier_two_source_accept(self):
        r=verify(self.x,FORECAST)
        self.assertEqual(r["old_two_binding_accept_at_A2"],
                         "OLD_TWO_SOURCE_ACCEPT_INVALIDATED")
        self.assertFalse(r["global_admission_accept_certified"])

    def test_T03_deletion_reinstates_only_conditional_scoped_basis(self):
        r=verify(self.x,FORECAST)
        self.assertEqual(r["A3_scoped_restore"],
                         "CONDITIONAL_SCOPED_REATTESTATION_ONLY")
        self.assertFalse(r["unbounded_current_freshness_certified"])

    def test_T04_old_bytes_but_new_unobserved_binding_not_safe(self):
        del self.x["watch_events"][1]
        self.assertEqual(self.status(),"REFUSE_WATCH_EVENT_DENOMINATOR")

    def test_T05_410_gone_requires_a_new_list_not_gap_masking(self):
        self.x["watches"]["binding"]["status"]="ERROR_410_GONE"
        self.x["watches"]["binding"]["error"]="410 Gone"
        self.assertEqual(self.status(),"RESYNC_REQUIRED")

    def test_T06_watch_disconnect_before_checkpoint_is_gap(self):
        self.x["watches"]["policy"]["status"]="DISCONNECTED_UNEXPECTEDLY"
        self.assertEqual(self.status(),"RESYNC_REQUIRED")

    def test_T07_watch_access_denied_refuses_authority(self):
        self.x["actor"]["authorized_native_permissions"]["binding"]["watch"]=False
        self.assertEqual(self.status(),"REFUSE_AUTHORITY")

    def test_T08_continue_token_means_incomplete_inventory(self):
        self.x["checkpoints"][0]["collections"]["binding"]["response"]["metadata"]["continue"]="NEXT"
        self.assertEqual(self.status(),"REFUSE_INVENTORY_PAGINATION")

    def test_T09_filtered_list_cannot_prove_full_registered_scope(self):
        self.x["checkpoints"][0]["collections"]["policy"]["selector"]="metadata.name=only-old"
        self.assertEqual(self.status(),"REFUSE_SCOPE")

    def test_T10_untrusted_complete_boolean_cannot_replace_list(self):
        self.x["caller_claimed_complete"]=True
        self.x["checkpoints"]=[]
        self.assertEqual(self.status(),"REFUSE_INVENTORY_DENOMINATOR")

    def test_T11_policy_bookmark_does_not_complete_unsynced_binding_watch(self):
        self.x["watches"]["policy"]["bookmark_rv"]="some-progress"
        self.x["watches"]["binding"]["status"]="UNSYNCED"
        self.assertEqual(self.status(),"REFUSE_CROSS_CLASS")

    def test_T12_opaque_different_collection_RVs_do_not_claim_atomicity(self):
        self.x["checkpoints"][0]["collections"]["policy"]["response"]["metadata"]["resourceVersion"]="z_RV"
        self.x["checkpoints"][0]["collections"]["binding"]["response"]["metadata"]["resourceVersion"]="a_RV"
        self.x["watches"]["policy"]["resourceVersion"]="z_RV"
        self.x["watches"]["binding"]["resourceVersion"]="a_RV"
        for kind,rv in (("policy","z_RV"),("binding","a_RV")):
            self.x["watches"][kind]["request_query"]=urllib.parse.urlencode({
                "watch":"1","resourceVersion":rv,
                "allowWatchBookmarks":"true","timeoutSeconds":"150"})
        r=verify(self.x,FORECAST)
        self.assertEqual(r["status"],"C1_W1_SCOPED_NATIVE_LIST_WATCH_FEASIBILITY_B9_TIE")
        self.assertFalse(r["cross_resource_atomicity_certified"])

    def test_T13_event_must_have_uid_rv_and_correct_kind(self):
        for key,change in (("uid",None),("resourceVersion",None),("kind","Pod")):
            x=copy.deepcopy(self.x)
            if key=="kind": x["watch_events"][1]["event"]["object"]["kind"]=change
            else: x["watch_events"][1]["event"]["object"]["metadata"].pop(key)
            self.assertTrue(verify(x,FORECAST)["status"].startswith("REFUSE_"))

    def test_T14_unwatched_global_source_classes_refuse_global_accept(self):
        self.x["requested_contract"]="ALL_ADMISSION"
        self.assertEqual(self.status(),"REFUSE_GLOBAL_ACCEPT")

    def test_T15_old_deny_proof_may_be_revoked_if_old_binding_changed(self):
        self.x["checkpoints"][2]["collections"]["binding"]["response"]["items"][0]["spec"]["policyName"]="different-policy"
        self.assertEqual(self.status(),"REFUSE_ORIGINAL_SOURCE_MUTATED")

    def test_T16_relist_after_gap_cannot_retroactively_restore_continuity(self):
        self.x["watches"]["policy"]["status"]="ERROR_410_GONE"
        self.assertEqual(self.status(),"RESYNC_REQUIRED")
        fresh=self.x["checkpoints"][-1]["collections"]
        reset=relist_after_gap(fresh,True,CONTRACT)
        self.assertEqual(reset["status"],"CONDITIONAL_SCOPED_REATTESTATION_ONLY")
        self.assertFalse(reset["prior_watch_gap_retroactively_repaired"])
        self.assertFalse(reset["global_current_accept_authorized"])


if __name__=="__main__":
    unittest.main(verbosity=2)
