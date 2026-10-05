#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-apt-production-results}"
mkdir -p "$OUT"/{lists/partial,log,meta}
PORT=18080
TARGET_FILE="$OUT/upstream.txt"

BEFORE=20250808T120000Z
AFTER=20250810T120000Z

echo "$BEFORE" > "$TARGET_FILE"
python3 experiments/apt_production/snapshot_proxy.py "$PORT" "$TARGET_FILE" >"$OUT/proxy.stdout" 2>"$OUT/proxy.stderr" &
PROXY_PID=$!
trap 'kill "$PROXY_PID" 2>/dev/null || true' EXIT
sleep 1

cat > "$OUT/sources.list" <<EOF
deb [signed-by=/usr/share/keyrings/debian-archive-keyring.gpg] http://127.0.0.1:$PORT/debian stable main
EOF

APT_COMMON=(
  -o "Dir::Etc::sourcelist=$PWD/$OUT/sources.list"
  -o "Dir::Etc::sourceparts=-"
  -o "Dir::State::lists=$PWD/$OUT/lists"
  -o "APT::Get::List-Cleanup=0"
  -o "Acquire::Check-Valid-Until=false"
  -o "Acquire::Languages=none"
  -o "Debug::NoLocking=true"
)

apt-get --version > "$OUT/meta/apt-version-full.txt"
sed -n '1p' "$OUT/meta/apt-version-full.txt" | tee "$OUT/meta/apt-version.txt"
dpkg-query -W debian-archive-keyring | tee "$OUT/meta/keyring-version.txt"

fetch_release () {
  local stamp="$1" tag="$2"
  curl -fsSL "https://snapshot.debian.org/archive/debian/$stamp/dists/stable/InRelease" -o "$OUT/meta/$tag.InRelease"
  sha256sum "$OUT/meta/$tag.InRelease" > "$OUT/meta/$tag.InRelease.sha256"
  grep -E '^(Origin|Label|Suite|Codename|Version|Date|Valid-Until):' "$OUT/meta/$tag.InRelease" > "$OUT/meta/$tag.fields"
}

fetch_release "$BEFORE" before
fetch_release "$AFTER" after

set +e
apt-get update "${APT_COMMON[@]}" >"$OUT/log/01-before.stdout" 2>"$OUT/log/01-before.stderr"
RC1=$?
set -e

echo "$AFTER" > "$TARGET_FILE"
sleep 1

set +e
apt-get update "${APT_COMMON[@]}" >"$OUT/log/02-after-block.stdout" 2>"$OUT/log/02-after-block.stderr"
RC2=$?
set -e

set +e
apt-get update --allow-releaseinfo-change-codename "${APT_COMMON[@]}" >"$OUT/log/03-after-allow-codename.stdout" 2>"$OUT/log/03-after-allow-codename.stderr"
RC3=$?
set -e

{
  printf 'phase\trc\n'
  printf 'before\t%s\n' "$RC1"
  printf 'after_block\t%s\n' "$RC2"
  printf 'after_allow_codename\t%s\n' "$RC3"
} | tee "$OUT/native_exit_codes.tsv"

cat "$OUT/meta/before.fields" "$OUT/meta/after.fields" > "$OUT/meta/release_fields.txt"

# Promotion checks: initial production snapshot accepted; transition blocked; codename-specific allowance accepted.
test "$RC1" -eq 0
test "$RC2" -ne 0
test "$RC3" -eq 0

grep -Ei "changed its .Codename.|release info|codename" "$OUT/log/02-after-block.stderr" > "$OUT/log/02-decision-evidence.txt"

sha256sum "$OUT/sources.list" "$OUT/meta/"*.InRelease "$OUT/log/"* > "$OUT/SHA256SUMS.txt"
cat "$OUT/native_exit_codes.tsv"
cat "$OUT/meta/release_fields.txt"
cat "$OUT/log/02-decision-evidence.txt"
