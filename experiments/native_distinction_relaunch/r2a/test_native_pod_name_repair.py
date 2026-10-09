#!/usr/bin/env python3
"""Before retry: prove only native Kubernetes Pod metadata names changed."""
import re
import unittest
import copy
from r2a_native_episode import pod_template as old_pod
from r2a_native_episode_v2 import pod_template as repaired_pod

RFC1123 = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")


class NativePodNameRepair(unittest.TestCase):
    def test_six_name_cases_rfc1123(self):
        for world,namespace in (
            ("WORLD_GATE","eeq-r2a-gate"),
            ("WORLD_STANDBY","eeq-r2a-standby")
        ):
            for phase in ("CURRENT","AFTER_BINDING_MUTATION","ACTIVATION_PROBE"):
                for sa in ("flux","default"):
                    with self.subTest(world=world,phase=phase,sa=sa):
                        old=old_pod(namespace,sa,phase,world)
                        repaired=repaired_pod(namespace,sa,phase,world)
                        name=repaired["metadata"]["name"]
                        self.assertIsNotNone(RFC1123.fullmatch(name))
                        self.assertLessEqual(len(name),63)
                        self.assertNotIn("_",name)
                        self.assertIn("_",old["metadata"]["name"])
                        old["metadata"]["name"]=name
                        self.assertEqual(old,repaired)

    def test_fixed_registered_decision_inputs_intact(self):
        for world,namespace in (
            ("WORLD_GATE","eeq-r2a-gate"),
            ("WORLD_STANDBY","eeq-r2a-standby")
        ):
            for phase in ("CURRENT","AFTER_BINDING_MUTATION","ACTIVATION_PROBE"):
                for sa in ("flux","default"):
                    p=repaired_pod(namespace,sa,phase,world)
                    self.assertEqual(p["metadata"]["namespace"],namespace)
                    self.assertEqual(p["spec"]["serviceAccountName"],sa)
                    self.assertEqual(p["spec"]["restartPolicy"],"Never")
                    self.assertEqual(len(p["spec"]["containers"]),1)
                    self.assertEqual(p["spec"]["containers"][0]["image"],
                                     "registry.k8s.io/pause:3.10")


if __name__ == "__main__":
    unittest.main(verbosity=2)
