#!/usr/bin/env python3
"""Contract checker synthetic kill tests. No native or crypto calls."""
import copy
import unittest
from r4_c0_common_checker import check_all

S="a"*64
ID="b"*64
TUF_ACTIONS=[
 "submit-root-3-a","submit-root-3-b",
 "submit-root-3-old-only","submit-root-3-new-only"
]


def initial():
    tuf=[]
    for state in ("s2a","s2b"):
        for act in TUF_ACTIONS:
            old_good=(act=="submit-root-3-a" and state=="s2a") or (
                act=="submit-root-3-b" and state=="s2b") or (
                act=="submit-root-3-old-only" and state=="s2a")
            new_good=act not in ("submit-root-3-old-only",)
            accept=old_good and new_good
            outcome="ACCEPT" if accept else "REJECT"
            after=("root-3-"+act[len("submit-root-3-"):]+".json"
                   if accept else "root-2-"+state[-1]+".json")
            tuf.append({
                "schema":"eeq-r4-qualified-transition-certificate-v0",
                "domain":"tuf_root_update",
                "contract_id":"R4_D0_TUF_SIGNED_ROOT_UPDATE_ONLY",
                "case_id":state+"|"+act,
                "sources":{"trusted_root":S,"proposed_root":S},
                "original_state":"root-2-"+state[-1]+".json",
                "qualified_obligations":[
                  {"type":"VERSION_CONTINUITY","qualified":True,
                   "old_version":2,"new_version":3},
                  {"type":"TUF_OLD_ROOT_AUTHORITY","qualified":old_good,
                   "status":"SUFFICIENT" if old_good else "INSUFFICIENT",
                   "verified_unique_keyids":[ID] if old_good else [],
                   "threshold":1},
                  {"type":"TUF_NEW_ROOT_AUTHORITY","qualified":new_good,
                   "status":"SUFFICIENT" if new_good else "INSUFFICIENT",
                   "verified_unique_keyids":[ID] if new_good else [],
                   "threshold":1},
                ],
                "action":act,"outcome":outcome,"native_observation":outcome,
                "successor_state":after,"native_successor":after,
                "verifier_domain":"TEST_RECHECK_TUF",
                "checker_outcome":"VERIFIED",
                "provenance":{"source_artifact_id":11608811184,
                              "native_artifact_id":11609456107},
            })
    k8s=[]
    for branch in ("a","b"):
        for phase in ("current","after_native_label_update"):
            match=branch=="a" or phase=="current"
            for probe in ("flux","default"):
                cel=probe!="flux"
                output="REJECT" if match and not cel else "ACCEPT"
                state=branch+":mode="+(
                    "strict" if phase=="current" else "relaxed")
                k8s.append({
                    "schema":"eeq-r4-qualified-transition-certificate-v0",
                    "domain":"k8s_admission",
                    "contract_id":"R2A_K8S_REGISTERED_VAP_DYNAMIC_POD_CREATE",
                    "case_id":branch+"|"+phase+"|"+probe,
                    "sources":{"policy":S,"binding":S,"pod":S,
                               "namespace_update":S},
                    "original_state":state,
                    "qualified_obligations":[
                        {"type":"K8S_REGISTERED_POD_CREATE","qualified":True,
                         "pod_serviceaccount":probe},
                        {"type":"K8S_BINDING_NAMESPACE_SELECTOR",
                         "qualified":match,
                         "binding_selector":{"r2a.team":"tenant"}},
                        {"type":"K8S_RESTRICTED_CEL_VALIDATION",
                         "qualified":cel,
                         "predicate":"serviceAccountName != flux"},
                        {"type":"K8S_NATIVE_NAMESPACE_ACTION",
                         "qualified":True,
                         "before_revision":"101",
                         "after_revision":"102"},
                    ],
                    "action":"DRY_RUN_POD_CREATE_"+probe.upper(),
                    "outcome":output,"native_observation":output,
                    "successor_state":state,"native_successor":state,
                    "verifier_domain":"TEST_RECHECK_K8S",
                    "checker_outcome":"VERIFIED",
                    "provenance":{"source_artifact_id":11604865804,
                                  "native_artifact_id":11604423996},
                })
    return (
        {"schema":"eeq-r4-c0-tuf-certificates-v0","certificates":tuf,
         "role_setup_count":2,"native_calls_in_c0":0},
        {"schema":"eeq-r4-c0-k8s-certificates-v0","certificates":k8s,
         "unbound_controls_verified":4,
         "actual_native_namespace_updates_verified":2,
         "native_calls_in_c0":0},
    )


class CommonCertificateKillTests(unittest.TestCase):
    def test_nominal_synthetic_envelope_is_structurally_valid(self):
        t,k=initial()
        s=check_all(t,k)
        self.assertEqual(s["common_certificate_rows"],16)
        self.assertEqual(s["scientific_status"],
                         "C0_COMMON_CERTIFICATE_INTERFACE_FEASIBLE_ON_PREVIOUS_DEVELOPMENT")
        self.assertFalse(s["improvement_over_full_b9_established"])

    def test_missing_one_case_aborts(self):
        t,k=initial()
        t["certificates"].pop()
        with self.assertRaisesRegex(ValueError,"C0_16_CASES"):
            check_all(t,k)

    def test_duplicate_case_aborts(self):
        t,k=initial()
        t["certificates"].append(copy.deepcopy(t["certificates"][0]))
        with self.assertRaisesRegex(ValueError,"DUPLICATE_COMMON_CERTIFICATE"):
            check_all(t,k)

    def test_bad_source_digest_aborts(self):
        t,k=initial()
        t["certificates"][0]["sources"]["trusted_root"]="wrong-sha"
        with self.assertRaisesRegex(ValueError,"MISSING_OR_BAD_SOURCE_HASH"):
            check_all(t,k)

    def test_native_mismatch_cannot_claim_verified(self):
        t,k=initial()
        t["certificates"][0]["native_observation"]="REJECT"
        with self.assertRaisesRegex(ValueError,"UNVERIFIED_OR_UNSUPPORTED_CREDIT"):
            check_all(t,k)

    def test_unknown_source_cannot_be_counted_as_verified_accept(self):
        t,k=initial()
        t["certificates"][0]["outcome"]="SOURCE_UNAVAILABLE"
        with self.assertRaisesRegex(ValueError,"UNVERIFIED_OR_UNSUPPORTED_CREDIT"):
            check_all(t,k)

    def test_old_root_threshold_forgery_aborts(self):
        t,k=initial()
        t["certificates"][0]["qualified_obligations"][1]["qualified"]=False
        with self.assertRaisesRegex(ValueError,"INCONSISTENT_TUF_SIGNER_THRESHOLD"):
            check_all(t,k)

    def test_new_root_unqualified_but_accept_is_not_verifiable(self):
        t,k=initial()
        t["certificates"][0]["qualified_obligations"][2]={
            "type":"TUF_NEW_ROOT_AUTHORITY","qualified":False,
            "status":"INSUFFICIENT","verified_unique_keyids":[],
            "threshold":1}
        with self.assertRaisesRegex(ValueError,"TUF_OUTCOME_CONTRADICTS_PROOF"):
            check_all(t,k)

    def test_k8s_wrong_cel_proof_aborts(self):
        t,k=initial()
        k["certificates"][0]["qualified_obligations"][2]["qualified"]=True
        with self.assertRaisesRegex(ValueError,
                                    "K8S_OUTCOME_CONTRADICTS_PROOF|BAD_RESTRICTED_K8S_CEL_PROOF"):
            check_all(t,k)

    def test_missing_domain_proof_component_aborts(self):
        t,k=initial()
        k["certificates"][0]["qualified_obligations"].pop()
        with self.assertRaisesRegex(ValueError,"INCOMPLETE_DOMAIN_PROOF_PREMISES"):
            check_all(t,k)

    def test_future_native_label_action_without_revision_change_aborts(self):
        t,k=initial()
        c=next(c for c in k["certificates"] if
               "after_native_label_update" in c["case_id"])
        c["qualified_obligations"][-1]["after_revision"]="101"
        with self.assertRaisesRegex(ValueError,
                                    "K8S_FUTURE_NATIVE_REVISION_NOT_CHANGED"):
            check_all(t,k)

    def test_native_control_denominator_cannot_drop(self):
        t,k=initial()
        k["unbound_controls_verified"]=3
        with self.assertRaisesRegex(ValueError,"NATIVE_CONTROL_DENOMINATOR"):
            check_all(t,k)

    def test_native_actions_not_hidden(self):
        t,k=initial()
        k["native_calls_in_c0"]=1
        with self.assertRaisesRegex(ValueError,"C0_UNEXPECTED_NATIVE_EXECUTION"):
            check_all(t,k)

    def test_cross_family_wrong_artifact_identity_aborts(self):
        t,k=initial()
        k["certificates"][0]["provenance"]["native_artifact_id"]=0
        with self.assertRaisesRegex(ValueError,
                                    "CERTIFICATE_SOURCE_NATIVE_ARTIFACT_MISMATCH"):
            check_all(t,k)


if __name__=="__main__":
    unittest.main(verbosity=2)
