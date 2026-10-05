#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-gcsfuse-results}"
mkdir -p "$OUT"
UPSTREAM_COMMIT=841695fb72d8e8fa329a19dad4be341f28d7a26c
URL="https://raw.githubusercontent.com/GoogleCloudPlatform/gcs-fuse-csi-driver/${UPSTREAM_COMMIT}/deploy/base/webhook/validating_admission_policy.yaml"

curl -fsSL "$URL" -o "$OUT/validating_admission_policy.yaml"
sha256sum "$OUT/validating_admission_policy.yaml" > "$OUT/UPSTREAM_SHA256SUM.txt"
printf '%s\n' "$UPSTREAM_COMMIT" > "$OUT/UPSTREAM_COMMIT.txt"

kubectl apply -f "$OUT/validating_admission_policy.yaml"
kubectl get validatingadmissionpolicy gcsfuse-sidecar-validator.csi.storage.gke.io -o yaml > "$OUT/policy-live.yaml"
kubectl get validatingadmissionpolicybinding gcsfuse-sidecar-validator-binding.csi.storage.gke.io -o yaml > "$OUT/binding-live.yaml"

make_pod () {
  local name="$1" annotation="$2" restart="$3" envval="$4"
  local f="$OUT/$name.yaml"
  {
    echo 'apiVersion: v1'
    echo 'kind: Pod'
    echo 'metadata:'
    echo "  name: $name"
    if [ "$annotation" = yes ]; then
      echo '  annotations:'
      echo '    gke-gcsfuse/volumes: "true"'
    fi
    echo 'spec:'
    echo '  restartPolicy: Never'
    echo '  initContainers:'
    echo '    - name: gke-gcsfuse-sidecar'
    echo '      image: registry.k8s.io/pause:3.10'
    if [ "$restart" != absent ]; then echo "      restartPolicy: $restart"; fi
    if [ "$envval" != absent ]; then
      echo '      env:'
      echo '        - name: NATIVE_SIDECAR'
      echo "          value: \"$envval\""
    fi
    echo '  containers:'
    echo '    - name: app'
    echo '      image: registry.k8s.io/pause:3.10'
  } > "$f"
}

make_pod reject-no-restart yes absent TRUE
make_pod reject-wrong-env yes Always FALSE
make_pod accept-valid yes Always TRUE
make_pod accept-unscoped no absent FALSE

# Wait for exact target-policy rejection before scoring.
start_ns=$(date +%s%N)
attempt=0
activated=0
while [ "$attempt" -lt 60 ]; do
  attempt=$((attempt+1))
  set +e
  kubectl apply --server-side --dry-run=server -f "$OUT/reject-no-restart.yaml" >"$OUT/activation-$attempt.stdout" 2>"$OUT/activation-$attempt.stderr"
  rc=$?
  set -e
  if [ "$rc" -ne 0 ] && grep -F "native gcsfuse sidecar init container must have restartPolicy:Always" "$OUT/activation-$attempt.stderr" >/dev/null; then
    activated=1
    break
  fi
  sleep 0.5
done
end_ns=$(date +%s%N)
printf 'attempts\t%s\nelapsed_ns\t%s\n' "$attempt" "$((end_ns-start_ns))" > "$OUT/activation.tsv"
test "$activated" -eq 1

cat > "$OUT/cases.tsv" <<'EOF'
case	expected	native_rc	native_label
EOF
run_case () {
  local name="$1" expected="$2"
  set +e
  kubectl apply --server-side --dry-run=server -f "$OUT/$name.yaml" >"$OUT/$name.stdout" 2>"$OUT/$name.stderr"
  rc=$?
  set -e
  if [ "$rc" -eq 0 ]; then label=ACCEPT; else label=REJECT; fi
  printf '%s\t%s\t%s\t%s\n' "$name" "$expected" "$rc" "$label" >> "$OUT/cases.tsv"
  if [ "$label" != "$expected" ]; then cat "$OUT/$name.stderr" >&2; return 1; fi
}
run_case reject-no-restart REJECT
run_case reject-wrong-env REJECT
run_case accept-valid ACCEPT
run_case accept-unscoped ACCEPT

grep -F "restartPolicy:Always" "$OUT/reject-no-restart.stderr" >/dev/null
grep -F "env var NATIVE_SIDECAR with value TRUE" "$OUT/reject-wrong-env.stderr" >/dev/null
sha256sum "$OUT"/*.yaml > "$OUT/SHA256SUMS.txt"
cat "$OUT/activation.tsv"
cat "$OUT/cases.tsv"
