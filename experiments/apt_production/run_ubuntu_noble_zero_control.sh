#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-ubuntu-production-results}"
mkdir -p "$OUT"/{lists/partial,meta,log}

SNAP1=20250901T120000Z
SNAP2=20250915T120000Z

cat > "$OUT/ubuntu.sources" <<'EOF'
Types: deb
URIs: http://archive.ubuntu.com/ubuntu
Suites: noble-updates
Components: main
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
Snapshot: yes
EOF

APT_COMMON=(
  -o "Dir::Etc::sourcelist=$PWD/$OUT/ubuntu.sources"
  -o "Dir::Etc::sourceparts=-"
  -o "Dir::State::lists=$PWD/$OUT/lists"
  -o "APT::Get::List-Cleanup=0"
  -o "Acquire::Languages=none"
  -o "Debug::NoLocking=true"
)

apt-get --version > "$OUT/meta/apt-version-full.txt"
sed -n '1p' "$OUT/meta/apt-version-full.txt" | tee "$OUT/meta/apt-version.txt"
dpkg-query -W ubuntu-keyring | tee "$OUT/meta/keyring-version.txt"

fetch_release () {
  local stamp="$1" tag="$2"
  curl -fsSL "https://snapshot.ubuntu.com/ubuntu/$stamp/dists/noble-updates/InRelease" -o "$OUT/meta/$tag.InRelease"
  sha256sum "$OUT/meta/$tag.InRelease" > "$OUT/meta/$tag.InRelease.sha256"
  grep -E '^(Origin|Label|Suite|Codename|Version|Date|Valid-Until|Snapshots):' "$OUT/meta/$tag.InRelease" > "$OUT/meta/$tag.fields"
}

fetch_release "$SNAP1" snapshot1
fetch_release "$SNAP2" snapshot2

set +e
apt-get update -S "$SNAP1" "${APT_COMMON[@]}" >"$OUT/log/01-snapshot.stdout" 2>"$OUT/log/01-snapshot.stderr"
RC1=$?
set -e

set +e
apt-get update -S "$SNAP2" "${APT_COMMON[@]}" >"$OUT/log/02-snapshot.stdout" 2>"$OUT/log/02-snapshot.stderr"
RC2=$?
set -e

{
  printf 'phase\trc\n'
  printf 'snapshot1\t%s\n' "$RC1"
  printf 'snapshot2\t%s\n' "$RC2"
} | tee "$OUT/native_exit_codes.tsv"

test "$RC1" -eq 0
test "$RC2" -eq 0
test "$(sha256sum "$OUT/meta/snapshot1.InRelease" | cut -d' ' -f1)" != "$(sha256sum "$OUT/meta/snapshot2.InRelease" | cut -d' ' -f1)"

# Protected release identity must remain stable; Date/hash should be allowed to evolve.
for field in Origin Label Suite Codename; do
  a=$(grep "^$field:" "$OUT/meta/snapshot1.fields" || true)
  b=$(grep "^$field:" "$OUT/meta/snapshot2.fields" || true)
  test "$a" = "$b"
done

if grep -Ei "changed its .(Origin|Label|Suite|Codename). value|release info" "$OUT/log/02-snapshot.stderr"; then
  echo "unexpected protected release-info warning" >&2
  exit 1
fi

cat "$OUT/meta/snapshot1.fields"
echo '---'
cat "$OUT/meta/snapshot2.fields"
sha256sum "$OUT/ubuntu.sources" "$OUT/meta/"*.InRelease "$OUT/log/"* > "$OUT/SHA256SUMS.txt"
