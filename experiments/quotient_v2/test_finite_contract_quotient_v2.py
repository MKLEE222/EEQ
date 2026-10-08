#!/usr/bin/env python3
"""Pre-registered v2 kill tests; all inputs are SYNTHETIC development fixtures."""
import copy
import itertools
import json
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from finite_contract_quotient_v2 import FiniteContractModel
from independent_trace_oracle import check_partition, check_witness


def support(sid="sup1", source="sourceA", authenticated=True,
            authorized=True, qualified=True, claims=("claimA",)):
    return {
        "id": sid,
        "source_identity": source,
        "provenance": "synthetic-lawful-fixture",
        "compatible_claims": list(claims),
        "claim_binding": list(claims),
        "authenticated": authenticated,
        "authorized": authorized,
        "qualified": qualified,
    }


def state(sid, supports, transitions=None, inventory=True, decoration=None):
    return {
        "id": sid,
        "source_inventory_complete": inventory,
        "support_items": supports,
        "transitions": transitions or {"inspect": sid, "rotate": sid},
        "decoration_not_in_registered_contract": decoration or sid,
    }


def fixture():
    good = lambda: [support()]
    states = [
        state("A", good(), {"inspect": "A", "rotate": "C"}),
        state("B", good(), {"inspect": "B", "rotate": "B"}),
        state("C", [], {"inspect": "C", "rotate": "C"}),
        state("D", [], {"inspect": "D", "rotate": "D"}, decoration="different raw bytes"),
        state("E", [support(authorized=None)], {"inspect": "E", "rotate": "E"}),
        state("F", [support(authenticated=True, authorized=False)],
              {"inspect": "F", "rotate": "F"}),
        state("G", good(), {"inspect": "G", "rotate": "D"},
              decoration="completely different irrelevant metadata"),
    ]
    return {
        "schema": "eeq-finite-contract-model-v2",
        "evidence_class": "SYNTHETIC",
        "claims": ["claimA"],
        "actions": ["inspect", "rotate"],
        "contracts": [{
            "id": "contractA", "claim": "claimA", "min_qualified_sources": 1,
            "allowed_actions": ["inspect", "rotate"],
        }],
        "states": states,
    }


def random_fixture(seed):
    rng = random.Random(seed)
    n = 5
    actions = ["inspect", "rotate"]
    claims = ["claimA", "claimB"]
    states = []
    for i in range(n):
        supports = []
        for j in range(3):
            claims_here = [x for x in claims if rng.randrange(3) != 0]
            supports.append(support(
                sid=f"s{j}", source=f"source{rng.randrange(3)}",
                authenticated=rng.choice([True, False, None]),
                authorized=rng.choice([True, False, None]),
                qualified=rng.choice([True, False, None]),
                claims=claims_here))
        states.append(state(
            f"S{i}", supports,
            transitions={a: f"S{rng.randrange(n)}" for a in actions},
            inventory=rng.choice([True, False])))
    return {
        "schema": "eeq-finite-contract-model-v2",
        "evidence_class": "SYNTHETIC",
        "claims": claims,
        "actions": actions,
        "contracts": [
            {"id": "c1", "claim": "claimA", "min_qualified_sources": 1,
             "allowed_actions": ["inspect", "rotate"]},
            {"id": "c2", "claim": "claimB", "min_qualified_sources": 2,
             "allowed_actions": ["inspect"]},
        ],
        "states": states,
    }


class QuotientV2KillTests(unittest.TestCase):
    def test_01_nontrivial_merges_at_zero_horizon(self):
        model = FiniteContractModel(fixture())
        q = model.run(0, witness_limit=20)
        self.assertEqual(q["quotient_class_count"], 3)
        self.assertEqual(q["class_of"]["A"], q["class_of"]["B"])
        self.assertEqual(q["class_of"]["A"], q["class_of"]["G"])
        self.assertEqual(q["class_of"]["C"], q["class_of"]["D"])
        self.assertEqual(q["class_of"]["C"], q["class_of"]["F"])
        self.assertNotEqual(q["class_of"]["C"], q["class_of"]["E"])
        check_partition(fixture(), q)
        for w in q["separation_witnesses"]:
            check_witness(fixture(), w)

    def test_02_action_conditioned_future_separates(self):
        p = fixture()
        model = FiniteContractModel(p)
        q0, q1 = model.run(0), model.run(1, witness_limit=50)
        self.assertEqual(q0["class_of"]["A"], q0["class_of"]["B"])
        self.assertNotEqual(q1["class_of"]["A"], q1["class_of"]["B"])
        self.assertEqual(q1["class_of"]["A"], q1["class_of"]["G"])
        self.assertEqual(q1["quotient_class_count"], 4)
        witness = model.witness("A", "B", 1)
        self.assertEqual(witness["action_prefix"], ["rotate"])
        self.assertTrue(check_witness(p, witness))
        check_partition(p, q1)

    def test_03_unknown_is_not_negative(self):
        m = FiniteContractModel(fixture())
        self.assertEqual(m.observations["E"][0][2], "REFUSE")
        self.assertEqual(m.observations["F"][0][2], "REJECT")
        p = fixture()
        p["states"][2]["source_inventory_complete"] = False
        m2 = FiniteContractModel(p)
        self.assertEqual(m2.observations["C"][0][2], "REFUSE")
        self.assertEqual(m2.observations["A"][0][2], "ACCEPT")

    def test_04_authenticated_but_unauthorized_rejects(self):
        m = FiniteContractModel(fixture())
        self.assertEqual(m.observations["F"][0][2], "REJECT")
        self.assertEqual(m.observations["A"][0][2], "ACCEPT")

    def test_05_contract_tightening_and_loosen(self):
        p = fixture()
        before = FiniteContractModel(p)
        p2 = copy.deepcopy(p)
        p2["contracts"][0]["min_qualified_sources"] = 2
        after = FiniteContractModel(p2)
        self.assertEqual(before.observations["A"][0][2], "ACCEPT")
        self.assertEqual(after.observations["A"][0][2], "REJECT")
        self.assertNotEqual(before.quotient(0)["class_of"],
                            after.quotient(0)["class_of"])
        # The compressed certificate belongs to a frozen contract version.
        self.assertNotEqual(before.run(1)["cost"]["codebook_bytes"],
                            after.run(1)["cost"]["codebook_bytes"])

    def test_06_source_identity_and_binding_matter_only_when_declared(self):
        p = fixture()
        p["contracts"][0]["min_qualified_sources"] = 2
        p["states"][0]["support_items"] = [
            support("s1", "sourceA"), support("s2", "sourceB")]
        p["states"][1]["support_items"] = [
            support("s1", "sourceA"), support("s2", "sourceA")]
        m = FiniteContractModel(p)
        self.assertEqual(m.observations["A"][0][2], "ACCEPT")
        self.assertEqual(m.observations["B"][0][2], "REJECT")
        p["contracts"][0]["source_restriction"] = ["sourceB"]
        p["contracts"][0]["min_qualified_sources"] = 1
        m2 = FiniteContractModel(p)
        self.assertEqual(m2.observations["A"][0][2], "ACCEPT")
        self.assertEqual(m2.observations["B"][0][2], "REJECT")

    def test_07_irrelevant_metadata_invariant(self):
        p1 = fixture()
        p2 = copy.deepcopy(p1)
        for i, s in enumerate(p2["states"]):
            s["decoration_not_in_registered_contract"] = "cosmetic " + str(i*113)
            for sup in s["support_items"]:
                sup["provenance"] = "cosmetic-but-no-contract-provenance-query"
        q1 = FiniteContractModel(p1).quotient(2)["class_of"]
        q2 = FiniteContractModel(p2).quotient(2)["class_of"]
        self.assertEqual(q1, q2)

    def test_08_explicit_native_label_field_rejected(self):
        p = fixture()
        p["states"][0]["native_action"] = "ACCEPT"
        with self.assertRaisesRegex(ValueError, "forbidden"):
            FiniteContractModel(p)

    def test_09_small_space_oracle_randomized(self):
        pair_checks = 0
        for seed in range(20):
            p = random_fixture(seed)
            m = FiniteContractModel(p)
            for horizon in range(4):
                result = m.run(horizon, witness_limit=30)
                audit = check_partition(p, result)
                pair_checks += audit["pairs"]
                for w in result["separation_witnesses"]:
                    self.assertTrue(check_witness(p, w))
                self.assertLessEqual(result["quotient_class_count"], len(p["states"]))
        self.assertEqual(pair_checks, 20*4*10)

    def test_10_stable_partition_and_codebook_charged(self):
        p = fixture()
        m = FiniteContractModel(p)
        q = m.run(2)
        self.assertTrue(q["stable_transition_congruence"])
        self.assertGreater(q["cost"]["codebook_bytes"], 0)
        self.assertGreater(q["cost"]["assignment_bytes"], 0)
        self.assertEqual(
            q["cost"]["codebook_plus_assignments_bytes"],
            q["cost"]["codebook_bytes"] + q["cost"]["assignment_bytes"])

    def test_11_qualifying_sources_with_unknown_inventory(self):
        p = fixture()
        p["states"][0]["source_inventory_complete"] = False
        m = FiniteContractModel(p)
        self.assertEqual(m.observations["A"][0][2], "ACCEPT")
        p["states"][0]["support_items"] = []
        m2 = FiniteContractModel(p)
        self.assertEqual(m2.observations["A"][0][2], "REFUSE")

    def test_12_undocumented_transition_rejected(self):
        p = fixture()
        del p["states"][0]["transitions"]["rotate"]
        with self.assertRaisesRegex(ValueError, "total action"):
            FiniteContractModel(p)


if __name__ == "__main__":
    unittest.main(verbosity=2)
