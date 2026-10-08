#!/usr/bin/env python3
"""In-toto prospective family source preflight; absolutely NO native scoring.

Only pinned wheel and git-blob identities are verified. Inert JSON is parsed.
This script neither imports in_toto nor invokes in-toto-verify.
"""
import argparse
import hashlib
import json
from pathlib import Path

WHEEL_NAME="in_toto-3.1.0-py3-none-any.whl"
WHEEL_SHA="fe8c69a8dae32690d116bb8112e7d6da53bbad3b9a4057ff8d43f1a5a90ee2d4"
EXPECTED={
    "tests/demo_files/demo.layout.template":"64ca25099e4b6afcb6710fd9552b7c4e539ce7ba",
    "tests/demo_files/write-code.776a00e2.link":"1baf159c75e0b4bc408021e34e444c019646e762",
    "tests/demo_files/package.2f89b927.link":"e7bde5860ec468c445c9d9bf987663775230e6e8",
    "tests/demo_files/foo.tar.gz":"5de7b881306435ec0cef766267d07c4f684ae76c",
    "tests/pems/rsa_private_unencrypted.pem":"82406424dc8a606e5a9e4d78f14f913006885ec9",
    "tests/pems/rsa_public.pem":"02e7bb778798af806c77efe92a3cabe161cd45a6",
    "tests/pems/ed25519_public.pem":"137861a38e86c0c32598ac56d1297e2895e55548",
    "tests/scripts/tar":"9cb701375915f0019cdede414f30cf1426aea20d",
}

def git_blob_id(data):
    h=hashlib.sha1()
    h.update(b"blob "+str(len(data)).encode("ascii")+b"\0")
    h.update(data)
    return h.hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--fixtures",type=Path,required=True)
    parser.add_argument("--wheel",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if args.wheel.name != WHEEL_NAME:
        raise ValueError("unexpected pinned wheel filename")
    wheel=args.wheel.read_bytes()
    wheel_digest=hashlib.sha256(wheel).hexdigest()
    if wheel_digest != WHEEL_SHA:
        raise ValueError("published wheel digest mismatch")
    hashes={}
    for name,expected in EXPECTED.items():
        data=(args.fixtures/name).read_bytes()
        got=git_blob_id(data)
        if got!=expected:
            raise ValueError("upstream Git blob mismatch: "+name)
        hashes[name]={
            "git_blob_sha1":got,
            "raw_sha256":hashlib.sha256(data).hexdigest(),
            "byte_size":len(data),
        }
    layout=json.loads((args.fixtures/"tests/demo_files/demo.layout.template").read_text())
    write=json.loads((args.fixtures/"tests/demo_files/write-code.776a00e2.link").read_text())
    package=json.loads((args.fixtures/"tests/demo_files/package.2f89b927.link").read_text())
    signed=layout["signed"]
    if signed.get("_type")!="layout":
        raise ValueError("fixture is not an in-toto layout template")
    steps=signed.get("steps",[])
    inspections=signed.get("inspect",[])
    if not steps or not inspections:
        raise ValueError("missing frozen in-toto continuation structure")
    metadata={
        "schema":"eeq-in-toto-g7-nonscoring-source-preflight-v1",
        "status":"SOURCE_IDENTITIES_AND_INERT_JSON_VERIFIED",
        "native_oracle_invoked":False,
        "in_toto_verify_invoked":False,
        "native_labels_observed":0,
        "pre_native_predictions_generated":False,
        "signed_layout_created":False,
        "wheel":{
            "file_name":WHEEL_NAME,
            "sha256":wheel_digest,
            "byte_size":len(wheel),
        },
        "upstream_repository":"in-toto/in-toto",
        "upstream_commit":"c82fe5d21aaa61c7f1a213db20a46f10bb3f411a",
        "frozen_git_blobs":hashes,
        "source_characterization":{
            "steps":[{
                "name":s.get("name"),
                "key_ids":sorted(s.get("pubkeys",[])),
                "threshold":s.get("threshold"),
                "expected_material_rules":s.get("expected_materials",[]),
                "expected_product_rules":s.get("expected_products",[]),
            } for s in steps],
            "inspections":[{
                "name":s.get("name"),
                "expected_material_rules":s.get("expected_materials",[]),
                "expected_product_rules":s.get("expected_products",[]),
                "command_declared_only":s.get("run",[]),
            } for s in inspections],
            "links":[{
                "name":obj["signed"].get("name"),
                "source_file":name,
                "signature_key_ids":sorted(v.get("keyid") for v in obj.get("signatures",[])),
                "material_names":sorted(obj["signed"].get("materials",{})),
                "product_names":sorted(obj["signed"].get("products",{})),
            } for name,obj in (
                ("write-code.776a00e2.link",write),("package.2f89b927.link",package)
            )],
            "owner_template_key_count":len(signed.get("keys",{})),
            "template_signature_count":len(layout.get("signatures",[])),
        },
        "future_fifth_family_gate_claim":"NONE_NO_NATIVE_SCORING",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(metadata,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":metadata["status"],
        "files":len(hashes),
        "steps":len(steps),
        "inspections":len(inspections),
        "no_native_scoring":True,
    },sort_keys=True))

if __name__=="__main__":
    main()
