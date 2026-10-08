#!/usr/bin/env python3
"""Paired scientific regression tests: plain v2 vs post-pilot factorized v2."""
import unittest

from lawful_quotient import (
    compile_quotient, independent_equivalence_check, quotient_downstream_check,
)
from factorized_quotient import compile_factorized, partition_sets
from synthetic_systems import generate_system, toy_system
from run_scaling import configurations

class FactorizedTests(unittest.TestCase):
    def assert_equivalent(self, spec, horizon, exhaustive_oracle=False):
        plain=compile_quotient(spec,horizon)
        fast=compile_factorized(spec,horizon)
        self.assertEqual(
            partition_sets(plain["states_to_final_class"]),
            partition_sets(fast["states_to_final_class"]),
        )
        self.assertEqual(plain["class_count"],fast["class_count"])
        if exhaustive_oracle:
            oracle=independent_equivalence_check(spec,horizon,fast)
            self.assertEqual(oracle["status"],"PASS",oracle)
        return plain,fast

    def test_toy_all_horizons_and_both_contracts(self):
        for audit in (False,True):
            for horizon in range(6):
                with self.subTest(audit=audit,horizon=horizon):
                    spec=toy_system(audit)
                    _,fast=self.assert_equivalent(spec,horizon,True)
                    self.assertEqual(fast["requested_horizon"],horizon)
                    self.assertEqual(
                        quotient_downstream_check(spec,fast,"continuation","release")["status"],
                        "PASS",
                    )

    def test_finite_systems_all_six_axes(self):
        for config in configurations():
            with self.subTest(config=config):
                spec=generate_system(
                    sources=config["sources"],claims=config["claims"],
                    actions=config["actions"],density=config["density"],
                    contracts=config["contracts"],state_count=config["state_count"],
                )
                self.assert_equivalent(spec,config["horizon"])

    def test_small_independent_oracle_against_both(self):
        for seed in (20261008,20261009):
            spec=generate_system(sources=4,claims=2,actions=2,
                                 contracts=2,density=.4,
                                 state_count=16,seed=seed)
            for horizon in range(5):
                self.assert_equivalent(spec,horizon,True)

    def test_stable_partition_can_stop_before_requested_horizon(self):
        spec=toy_system()
        _,fast=self.assert_equivalent(spec,5,True)
        self.assertIsNotNone(fast["fixed_point_at"])
        self.assertLess(fast["effective_depth"],5)
        self.assertEqual(fast["table"]["mode"],"STATIONARY_FIXED_POINT")
        # Same-depth action relation is well-defined for every class.
        class_ids=set(fast["states_to_final_class"].values())
        for row in fast["table"]["stationary_classes"]:
            self.assertEqual(set(row["successors_at_same_depth"]),set(spec["actions"]))
            self.assertTrue(set(row["successors_at_same_depth"].values())<=class_ids)

    def test_factorization_reports_table_overhead_not_only_codes(self):
        spec=generate_system(contracts=4)
        p,f=self.assert_equivalent(spec,4)
        for result in (p,f):
            cost=result["cost"]
            self.assertEqual(cost["total_encoded_bytes"],
                             cost["quotient_table_bytes"]+cost["class_code_bytes_total"])
        self.assertLess(f["cost"]["total_encoded_bytes"],
                        p["cost"]["total_encoded_bytes"])

    def test_refusal_boundary_remains_identical(self):
        spec=toy_system()
        spec["c1_complete"]=False
        with self.assertRaises(Exception):
            compile_quotient(spec,2)
        with self.assertRaises(Exception):
            compile_factorized(spec,2)
        spec=toy_system()
        spec["states"][0]["native_action"]="POISON"
        with self.assertRaises(Exception):
            compile_quotient(spec,2)
        with self.assertRaises(Exception):
            compile_factorized(spec,2)

if __name__ == "__main__":
    unittest.main()
