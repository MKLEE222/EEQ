#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://updates.bottlerocket.aws/2020-07-07/aws-k8s-1.35/x86_64"
OUT_DIR="${1:-bottlerocket-native-chain}"
ROOT_DIR="${OUT_DIR}/roots"
mkdir -p "${ROOT_DIR}"

for version in 1 2 3 4 5 6 7 8; do
  curl -fsSLo "${ROOT_DIR}/${version}.root.json" "${BASE_URL}/${version}.root.json"
done

python3 - "${ROOT_DIR}" <<'PY'
import hashlib, json, pathlib, re, sys
root_dir = pathlib.Path(sys.argv[1])
inventory = pathlib.Path("experiments/bottlerocket/FROZEN_SOURCE_INVENTORY.md").read_text()
expected = {}
for line in inventory.splitlines():
    m = re.match(r"\|\s*([1-8])\s*\|\s*([0-9a-f]{64})\s*\|\s*(\d+)\s*\|", line)
    if m:
        expected[int(m.group(1))] = (m.group(2), int(m.group(3)))
if sorted(expected) != list(range(1,9)):
    raise SystemExit(f"failed to parse frozen inventory: {sorted(expected)}")
rows = []
for version in range(1,9):
    p = root_dir / f"{version}.root.json"
    data = p.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    sha, size = expected[version]
    parsed = json.loads(data)
    signed_version = parsed.get("signed",{}).get("version")
    ok = digest == sha and len(data) == size and signed_version == version
    rows.append({
        "version": version,
        "sha256": digest,
        "bytes": len(data),
        "signed_version": signed_version,
        "matches_frozen_inventory": ok,
    })
    if not ok:
        raise SystemExit(f"root {version} differs from frozen inventory")
(root_dir.parent / "source_verification.json").write_text(json.dumps(rows, indent=2) + "\n")
PY

status="$(curl -sS -o "${ROOT_DIR}/9.root.response" -w '%{http_code}' "${BASE_URL}/9.root.json")"
printf '%s\n' "${status}" > "${ROOT_DIR}/9.root.http_status"
if [ "${status}" != "403" ]; then
  echo "frozen source boundary changed: root 9 returned HTTP ${status}, expected 403" >&2
  exit 3
fi

(
  cd experiments/bottlerocket/native_tuf
  npm ci --ignore-scripts --no-audit --no-fund
)

node experiments/bottlerocket/native_tuf/verify_root_chain.js   "${ROOT_DIR}"   "${OUT_DIR}/BOTTLE_ROCKET_NATIVE_ROOT_CHAIN.json"

sha256sum   experiments/bottlerocket/FROZEN_SOURCE_INVENTORY.md   experiments/bottlerocket/native_tuf/package.json   experiments/bottlerocket/native_tuf/package-lock.json   experiments/bottlerocket/native_tuf/verify_root_chain.js   "${OUT_DIR}/source_verification.json"   "${OUT_DIR}/BOTTLE_ROCKET_NATIVE_ROOT_CHAIN.json"   > "${OUT_DIR}/SHA256SUMS.txt"

python3 - "${OUT_DIR}/BOTTLE_ROCKET_NATIVE_ROOT_CHAIN.json" <<'PY'
import json, sys
p=json.load(open(sys.argv[1]))
s=p["summary"]
assert s["transitions"] == 7, s
assert s["accepted"] == 7, s
assert s["rejected"] == 0, s
assert s["final_trusted_root_version"] == 8, s
assert s["complete"] is True, s
print(json.dumps(s, sort_keys=True))
PY
