#!/usr/bin/env bash
set -euo pipefail
BASE="https://updates.bottlerocket.aws/2020-07-07/aws-k8s-1.35/x86_64"
OUT="${1:-bottlerocket-discovery}"
mkdir -p "$OUT/files"
printf 'name\thttp_code\tbytes\tsha256\tmetadata_version\n' > "$OUT/inventory.tsv"

fetch_one () {
  local name="$1"
  local body="$OUT/files/$name"
  local code
  code="$(curl -sS -L --connect-timeout 20 --max-time 60 -o "$body" -w '%{http_code}' "$BASE/$name" || true)"
  if [ "$code" = "200" ]; then
    local bytes sha version
    bytes="$(wc -c < "$body" | tr -d ' ')"
    sha="$(sha256sum "$body" | awk '{print $1}')"
    version="$(python3 - "$body" <<'PY'
import json,sys
p=sys.argv[1]
try:
    d=json.load(open(p))
    print(d.get("signed",{}).get("version",""))
except Exception:
    print("")
PY
)"
    printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$code" "$bytes" "$sha" "$version" >> "$OUT/inventory.tsv"
  else
    local bytes
    bytes="$(wc -c < "$body" 2>/dev/null | tr -d ' ' || echo 0)"
    printf '%s\t%s\t%s\t\t\n' "$name" "$code" "$bytes" >> "$OUT/inventory.tsv"
  fi
}

fetch_one root.json
for n in $(seq 1 20); do fetch_one "$n.root.json"; done
printf '%s\n' "$BASE" > "$OUT/metadata_base_url.txt"
cat "$OUT/inventory.tsv"
