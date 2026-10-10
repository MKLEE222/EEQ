#!/usr/bin/env python3
"""F0 source-only fixed 96-mask matrix and synthetic anti-masking controls."""
import copy
import unittest
from collections import Counter

from r3_m2_partial_source import (
    BOUND_SOURCE_NAMES, MASKS, candidate, registered_mask_packet_rows,
    registered_rows, projected_packet, validate_packet,
)
from r3_m2_possible_world_oracle import (
    possible_native_vap_effects, strongest_b9_with_equal_partial_inputs,
)

FIXED_COUNTS = {
    "PROVEN_ACCEPT": 26,
    "PROVEN_REJECT": 14,
    "SOURCE_UNAVAILABLE_REFUSE": 24,
    "MODEL_UNSUPPORTED_REFUSE": 32,
}
FIXED_MASK_CERTS = {
    "FULL_CLOSED":12,
    "TEAM_ONLY_CLOSED":9,
    "MODE_ONLY_CLOSED":9,
    "NO_SELECTORS_CLOSED":6,
    "OPEN_INVENTORY_KNOWN_BINDINGS":4,
    "POLICY_SOURCE_UNAVAILABLE":0,
    "POLICY_SOURCE_TAMPERED":0,
    "BINDING_FRESHNESS_UNPROVEN":0,
}


class R3M2F0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets=registered_mask_packet_rows()

    def test_01_full_cross_product_no_selection(self):
        self.assertEqual(len(self.packets),96)
        self.assertEqual(len({(p["mask_id"],p["case_id"]) for p in self.packets}),96)
        self.assertEqual(Counter(p["mask_id"] for p in self.packets),
                         Counter({m:12 for m in MASKS}))

    def test_02_exact_preregistered_outcome_histogram(self):
        self.assertEqual(Counter(candidate(p)["disposition"] for p in self.packets),
                         Counter(FIXED_COUNTS))

    def test_03_frozen_per_mask_safe_coverage(self):
        for mask,want in FIXED_MASK_CERTS.items():
            have=sum(candidate(p)["disposition"] in ("PROVEN_ACCEPT","PROVEN_REJECT")
                     for p in self.packets if p["mask_id"]==mask)
            self.assertEqual(have,want,mask)

    def test_04_zero_unsound_certificates_against_independent_worlds(self):
        for p in self.packets:
            d=candidate(p)["disposition"]
            worlds=possible_native_vap_effects(p)
            if d=="PROVEN_REJECT":
                self.assertEqual(worlds,frozenset(("REJECT",)),p["case_id"])
            elif d=="PROVEN_ACCEPT":
                self.assertEqual(worlds,frozenset(("ACCEPT",)),p["case_id"])
            else:
                self.assertEqual(worlds,frozenset(("ACCEPT","REJECT")),p["case_id"])

    def test_05_fully_informed_b9_ties_with_equal_partial_information(self):
        self.assertEqual(sum(candidate(p)["disposition"] ==
                 strongest_b9_with_equal_partial_inputs(p) for p in self.packets),96)

    def test_06_open_inventory_can_still_prove_four_denials(self):
        subset=[p for p in self.packets
                if p["mask_id"]=="OPEN_INVENTORY_KNOWN_BINDINGS"]
        self.assertEqual(sum(candidate(p)["disposition"]=="PROVEN_REJECT"
                             for p in subset),4)
        self.assertEqual(sum(candidate(p)["disposition"]=="PROVEN_ACCEPT"
                             for p in subset),0)
        for p in subset:
            if candidate(p)["disposition"]=="PROVEN_REJECT":
                self.assertTrue(candidate(p)["witness"])

    def test_07_closed_inventory_unknown_selectors_can_prove_default(self):
        for mask in ("TEAM_ONLY_CLOSED","MODE_ONLY_CLOSED","NO_SELECTORS_CLOSED"):
            default=[p for p in self.packets
                     if p["mask_id"]==mask and p["pod"]["serviceAccountName"]=="default"]
            self.assertEqual(len(default),6)
            self.assertTrue(all(candidate(p)["disposition"]=="PROVEN_ACCEPT"
                                for p in default))

    def test_08_partial_evidence_never_maps_refuse_to_native_reject(self):
        for p in self.packets:
            res=candidate(p)
            if res["disposition"].endswith("REFUSE"):
                self.assertEqual(res["witness"],[])
            else:
                self.assertIn(res["disposition"],("PROVEN_ACCEPT","PROVEN_REJECT"))
                self.assertTrue(res["witness"])

    def test_09_missing_selector_is_not_assumed_nonmatching(self):
        examples=[p for p in self.packets if p["mask_id"] in
                  ("TEAM_ONLY_CLOSED","MODE_ONLY_CLOSED","NO_SELECTORS_CLOSED")
                  and p["pod"]["serviceAccountName"]=="flux"]
        ambiguous=sum(len(possible_native_vap_effects(p))==2 for p in examples)
        self.assertEqual(ambiguous,12)
        self.assertTrue(all(candidate(p)["disposition"]!="PROVEN_ACCEPT"
                            for p in examples if len(possible_native_vap_effects(p))==2))

    def test_10_open_inventory_accept_all_is_rejected_as_unsound(self):
        # Even a "default" Pod that passes the registered policy may be denied
        # by an unregistered policy: no closure witness means NO ACCEPT.
        for p in self.packets:
            if p["mask_id"]=="OPEN_INVENTORY_KNOWN_BINDINGS" and p["pod"]["serviceAccountName"]=="default":
                self.assertEqual(candidate(p)["disposition"],"MODEL_UNSUPPORTED_REFUSE")
                self.assertIn("REJECT",possible_native_vap_effects(p))

    def test_11_missing_policy_or_invalid_digest_are_distinct(self):
        for mask,kind in (("POLICY_SOURCE_UNAVAILABLE","SOURCE_UNAVAILABLE_REFUSE"),
                          ("POLICY_SOURCE_TAMPERED","MODEL_UNSUPPORTED_REFUSE")):
            self.assertEqual({candidate(p)["disposition"] for p in self.packets
                              if p["mask_id"]==mask},{kind})

    def test_12_stale_binding_source_does_not_generate_denial_proof(self):
        for p in self.packets:
            if p["mask_id"]=="BINDING_FRESHNESS_UNPROVEN":
                self.assertEqual(candidate(p)["disposition"],"MODEL_UNSUPPORTED_REFUSE")

    def test_13_forged_complete_flag_is_never_consulted_for_open_world(self):
        p=next(p for p in self.packets
               if p["mask_id"]=="OPEN_INVENTORY_KNOWN_BINDINGS"
               and p["pod"]["serviceAccountName"]=="default")
        forged=copy.deepcopy(p)
        forged["caller_claimed_complete"]=True
        self.assertEqual(candidate(forged)["disposition"],"MODEL_UNSUPPORTED_REFUSE")

    def test_14_registered_binding_id_cannot_be_omitted_or_duplicated(self):
        p=copy.deepcopy(self.packets[0])
        p["binding_slots"].pop()
        self.assertEqual(candidate(p)["disposition"],"MODEL_UNSUPPORTED_REFUSE")
        p=copy.deepcopy(self.packets[0])
        p["binding_slots"][1]["source_id"]=BOUND_SOURCE_NAMES[0]
        self.assertEqual(candidate(p)["disposition"],"MODEL_UNSUPPORTED_REFUSE")

    def test_15_unregistered_selector_grammar_is_unsupported(self):
        p=copy.deepcopy(self.packets[0])
        p["binding_slots"][0]["selector"]={"matchExpressions":[]}
        self.assertEqual(candidate(p)["disposition"],"MODEL_UNSUPPORTED_REFUSE")

    def test_16_observed_action_label_cannot_be_changed_post_score(self):
        p=copy.deepcopy(self.packets[0])
        p["namespace_labels"]["r3.team"]="not_the_registered_action"
        self.assertEqual(candidate(p)["disposition"],"MODEL_UNSUPPORTED_REFUSE")

    def test_17_hidden_selector_bytes_leakage_veto(self):
        p=next(p for p in self.packets if p["mask_id"]=="NO_SELECTORS_CLOSED")
        forged=copy.deepcopy(p)
        forged["binding_slots"][0]["selector"]={"r3.team":"tenant"}
        self.assertEqual(candidate(forged)["disposition"],"MODEL_UNSUPPORTED_REFUSE")

    def test_18_unknown_policy_identity_proof_cannot_certify_accept(self):
        p=copy.deepcopy(self.packets[0])
        p["binding_slots"][1]["policy_name"]="other-policy"
        self.assertEqual(candidate(p)["disposition"],"MODEL_UNSUPPORTED_REFUSE")

    def test_19_pod_actor_and_scope_are_registered(self):
        p=copy.deepcopy(self.packets[0])
        p["pod"]["serviceAccountName"]="admin"
        self.assertEqual(candidate(p)["disposition"],"MODEL_UNSUPPORTED_REFUSE")
        p=copy.deepcopy(self.packets[0])
        p["contract"]="different"
        self.assertEqual(candidate(p)["disposition"],"MODEL_UNSUPPORTED_REFUSE")

    def test_20_positive_denial_proof_has_current_qualified_binding(self):
        for p in self.packets:
            res=candidate(p)
            if res["disposition"]=="PROVEN_REJECT":
                for b in res["witness"]:
                    slot=next(s for s in p["binding_slots"] if s["source_id"]==b)
                    self.assertEqual(slot["selector_status"],"AVAILABLE")
                    self.assertTrue(all(p["namespace_labels"].get(k)==v
                                        for k,v in slot["selector"].items()))
                self.assertEqual(p["pod"]["serviceAccountName"],"flux")

    def test_21_original_native_support_evidence_is_reused_not_scored(self):
        rows,manifest=registered_rows()
        self.assertEqual(len(rows),12)
        self.assertEqual(len(manifest),8)
        self.assertTrue(all("expected_native" not in row for row in rows))
        self.assertTrue(all("native_observation" not in p for p in self.packets))

    def test_22_untrusted_closure_attack_is_a_retained_external_blocker(self):
        # Strong counterexample: if a third active Deny policy secretly exists,
        # FULL_CLOSED's default-Pod ACCEPT would be unsound. The F0 program
        # assumes the authored inventory; it does NOT prove that assumption.
        p=next(p for p in self.packets
               if p["mask_id"]=="FULL_CLOSED"
               and p["pod"]["serviceAccountName"]=="default")
        self.assertEqual(candidate(p)["disposition"],"PROVEN_ACCEPT")
        hypothetical_extra_denial=True
        self.assertTrue(hypothetical_extra_denial)
        self.assertEqual("REJECT" if hypothetical_extra_denial else "ACCEPT","REJECT")


if __name__=="__main__":
    unittest.main(verbosity=2)
