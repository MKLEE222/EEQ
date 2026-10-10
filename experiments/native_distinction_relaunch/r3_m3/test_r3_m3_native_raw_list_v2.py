#!/usr/bin/env python3
"""Pre-native V2 raw-list parsing tests, no actual kubectl/Kubernetes."""
import copy
import json
import unittest
from unittest.mock import patch
from r3_m3_native_k8s import raw_collection,membership_snapshot


def native_raw(kind, rv="200", items=None):
    return {
        "apiVersion":"admissionregistration.k8s.io/v1",
        "kind":kind,
        "metadata":{"resourceVersion":rv},
        "items":items if items is not None else [],
    }


class RawNativeListV2Tests(unittest.TestCase):
    def test_api_policy_source_list_yields_nonempty_opaque_rv(self):
        record=native_raw("ValidatingAdmissionPolicyList","RV-opaque")
        with patch("r3_m3_native_k8s.kubectl",
                   return_value={"stdout":json.dumps(record)}) as fn:
            out=raw_collection("validatingadmissionpolicies")
        self.assertEqual(out["metadata"]["resourceVersion"],"RV-opaque")
        fn.assert_called_once_with(
            "get","--raw",
            "/apis/admissionregistration.k8s.io/v1/validatingadmissionpolicies")

    def test_api_binding_source_list_yields_resource_version(self):
        record=native_raw("ValidatingAdmissionPolicyBindingList","RV-binding")
        with patch("r3_m3_native_k8s.kubectl",
                   return_value={"stdout":json.dumps(record)}):
            out=raw_collection("validatingadmissionpolicybindings")
        self.assertEqual(out["metadata"]["resourceVersion"],"RV-binding")

    def test_absent_resource_version_blocks(self):
        record=native_raw("ValidatingAdmissionPolicyList")
        del record["metadata"]["resourceVersion"]
        with patch("r3_m3_native_k8s.kubectl",
                   return_value={"stdout":json.dumps(record)}):
            with self.assertRaisesRegex(RuntimeError,
                                        "RAW_API_NATIVE_SOURCE_LIST_RV"):
                raw_collection("validatingadmissionpolicies")

    def test_empty_resource_version_blocks(self):
        record=native_raw("ValidatingAdmissionPolicyBindingList","")
        with patch("r3_m3_native_k8s.kubectl",
                   return_value={"stdout":json.dumps(record)}):
            with self.assertRaisesRegex(RuntimeError,
                                        "RAW_API_NATIVE_SOURCE_LIST_RV"):
                raw_collection("validatingadmissionpolicybindings")

    def test_wrong_kind_and_unsupported_collection_block(self):
        record=native_raw("ValidatingAdmissionPolicyBindingList","RV")
        with patch("r3_m3_native_k8s.kubectl",
                   return_value={"stdout":json.dumps(record)}):
            with self.assertRaisesRegex(RuntimeError,"RAW_API_NATIVE_SOURCE_LIST_RV"):
                raw_collection("validatingadmissionpolicies")
        with self.assertRaisesRegex(RuntimeError,
                                    "UNREGISTERED_NATIVE_SOURCE_COLLECTION"):
            raw_collection("validatingwebhookconfigurations")

    def test_joint_snapshot_keeps_both_collection_versions_separate(self):
        policies=native_raw("ValidatingAdmissionPolicyList","RV-101")
        bindings=native_raw("ValidatingAdmissionPolicyBindingList","RV-307")
        with patch("r3_m3_native_k8s.kubectl",side_effect=[
            {"stdout":json.dumps(policies)},
            {"stdout":json.dumps(bindings)},
        ]):
            got=membership_snapshot()
        self.assertEqual(got["policy_list_resource_version"],"RV-101")
        self.assertEqual(got["binding_list_resource_version"],"RV-307")
        self.assertTrue(got["not_global_k8s_admission_authority"])


if __name__=="__main__":
    unittest.main(verbosity=2)
