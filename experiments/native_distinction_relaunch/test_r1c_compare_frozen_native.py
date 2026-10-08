#!/usr/bin/env python3
"""No-native test of the future immutable R1c scorer; fully synthetic rows."""
import copy
import unittest
from r1c_compare_frozen_native import compare


def fixtures():
    states=[{"state":f"trusted-root-{n}","source_sha256":f"sha-root-{n}"}
            for n in range(1,9)]
    transitions=[]
    native=[]
    for n in range(1,9):
        for m in range(2,9):
            yes=(m==n+1)
            transitions.append({
                "from_state":f"trusted-root-{n}","action":f"submit-root-{m}",
                "candidate_source_sha256":f"sha-root-{m}",
                "derived_effect":"ADVANCE_TRUST_ROOT" if yes else "KEEP_TRUST_ROOT",
                "to_state":f"trusted-root-{m if yes else n}",
            })
            native.append({
                "from_state":f"trusted-root-{n}","action":f"submit-root-{m}",
                "candidate_source_sha256":f"sha-root-{m}",
                "from_root_source_sha256":f"sha-root-{n}",
                "native_action":"ACCEPT" if yes else "REJECT",
                "after_native_version":m if yes else n,
                "setup_error":None,"candidate_error":None,
                "decision_ns":100,
            })
    return (
      {"schema":"eeq-r1b-tuf-source-crypto-transition-v1",
       "grid_cells":56,"states":states,"transitions":transitions},
      {"schema":"eeq-r1c-tuf-native-root-grid-v1",
       "grid_rows":56,"rows":native}
    )


class ComparatorContractTests(unittest.TestCase):
    def test_exact_56(self):
        pred,native=fixtures()
        r=compare(pred,native)
        self.assertEqual(r["summary"]["method_native_matches"],56)
        self.assertEqual(r["summary"]["known_prior_adjacent"]["total"],7)
        self.assertEqual(r["summary"]["other_version_proposals"]["total"],49)
    def test_forced_bad_native_is_retained_as_mismatch(self):
        pred,native=fixtures()
        native["rows"][0]["native_action"]="REJECT"
        native["rows"][0]["after_native_version"]=1
        r=compare(pred,native)
        self.assertEqual(r["summary"]["method_native_mismatches"],1)
    def test_setup_failure_is_not_a_match(self):
        pred,native=fixtures()
        native["rows"][0]["native_action"]="SETUP_FAILURE"
        native["rows"][0]["after_native_version"]=None
        r=compare(pred,native)
        self.assertEqual(r["summary"]["native_setup_failures"],1)
        self.assertEqual(r["summary"]["method_native_matches"],55)
    def test_unsupported_is_not_credited_as_accuracy(self):
        pred,native=fixtures()
        pred["transitions"][0]["derived_effect"]="MODEL_UNSUPPORTED"
        pred["transitions"][0]["to_state"]=None
        r=compare(pred,native)
        self.assertEqual(r["summary"]["method_unsupported"],1)
        self.assertEqual(r["summary"]["method_native_matches"],55)
    def test_source_hash_drift_aborts(self):
        pred,native=fixtures()
        native["rows"][0]["candidate_source_sha256"]="tampered"
        with self.assertRaisesRegex(ValueError,"candidate source SHA"):
            compare(pred,native)
    def test_case_drop_aborts(self):
        pred,native=fixtures()
        native["rows"].pop()
        with self.assertRaises(Exception):
            compare(pred,native)


if __name__=="__main__":
    unittest.main(verbosity=2)
