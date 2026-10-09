"""F0 synthetic preregistered 20-row kill matrix: no native labels, no P3 primary score."""
import copy
import unittest
from p3b_dependency_reuse_guard import check
A="a"*64
B="b"*64
C="c"*64
def base():
    return {
        "schema":"eeq-p3b-dependency-snapshot-f0",
        "scope":{"contract":"TUF_ROOT_UPDATE_ONLY","claim":"root3_accepted",
                 "actor":"registered_tuf_client","action":"UPDATE_ROOT","horizon":1},
        "closure":{"sources":["trusted_root"],"qualifications":["old_root_authority"]},
        "sources":{"trusted_root":{"digest":A,"status":"AVAILABLE"},
                   "targets":{"digest":B,"status":"AVAILABLE"}},
        "qualifications":{"old_root_authority":{"digest":B,"status":"QUALIFIED"},
                          "targets_authority":{"digest":B,"status":"QUALIFIED"}}
    }

class PreregisteredF0(unittest.TestCase):
    def test_fixed_f01_to_f20(self):
        reuse="REUSE_CANDIDATE_CONDITIONAL"
        rev="REVERIFY_REQUIRED"
        unavailable="SOURCE_UNAVAILABLE"
        unsupported="MODEL_UNSUPPORTED"
        expected=[reuse,reuse,rev,rev,reuse,unavailable,unavailable,unsupported,
                  unsupported,unsupported,unsupported,rev,rev,unsupported,
                  unsupported,rev,rev,unsupported,unsupported,unsupported]
        results=[]
        for case in range(1,21):
            old=base()
            fresh=copy.deepcopy(old)
            closure=copy.deepcopy(old["closure"])
            complete=True
            abort=False
            if case==2: fresh["sources"]["targets"]["digest"]=C
            elif case==3: fresh["sources"]["trusted_root"]["digest"]=C
            elif case==4: fresh["qualifications"]["old_root_authority"]["digest"]=C
            elif case==5: fresh["qualifications"]["targets_authority"]["digest"]=C
            elif case==6: fresh["sources"]["trusted_root"]={"digest":None,"status":"UNAVAILABLE"}
            elif case==7: fresh["qualifications"]["old_root_authority"]={"digest":None,"status":"UNAVAILABLE"}
            elif case==8: complete=False
            elif case==9: fresh["scope"]["contract"]="TUF_ROOT_AND_TARGETS"
            elif case==10: fresh["scope"]["action"]="VERIFY_TARGETS"
            elif case==11: fresh["scope"]["horizon"]=2
            elif case==12: closure["sources"].append("targets")
            elif case==13: closure["qualifications"].append("targets_authority")
            elif case==14: del fresh["sources"]["trusted_root"]
            elif case==15: del fresh["qualifications"]["old_root_authority"]
            elif case==16: fresh["qualifications"]["old_root_authority"]["status"]="UNQUALIFIED"
            elif case==17: fresh["sources"]["trusted_root"]["status"]="INVALID"
            elif case==18: fresh["schema"]="unregistered"
            elif case==19: abort=True
            elif case==20: fresh["sources"]["trusted_root"]["digest"]="malformed"
            def audit(_snapshot):
                if abort: raise RuntimeError("auditor failed")
                return {**closure,"complete":complete}
            result=check(old,fresh,audit)
            self.assertEqual(result,expected[case-1],"F%02d" % case)
            results.append(result)
        self.assertEqual(len(results),20)
        self.assertNotIn("ACCEPT",results)
        self.assertNotIn("REJECT",results)

if __name__=="__main__":
    unittest.main(verbosity=2)
