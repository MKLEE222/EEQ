#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-zalando-results}"
mkdir -p "$OUT"
UPSTREAM_COMMIT=4d07119eca42ec94a31e6365cb48fa7e991e3f30
BASE="https://raw.githubusercontent.com/zalando-incubator/kubernetes-on-aws/${UPSTREAM_COMMIT}/cluster/manifests/fabric-gateway"

curl -fsSL "$BASE/fabricgateway_crd.yaml" -o "$OUT/fabricgateway_crd.yaml"
curl -fsSL "$BASE/02-validation.yaml" -o "$OUT/02-validation.yaml"
sha256sum "$OUT/fabricgateway_crd.yaml" "$OUT/02-validation.yaml" > "$OUT/UPSTREAM_SHA256SUMS.txt"
printf '%s\n' "$UPSTREAM_COMMIT" > "$OUT/UPSTREAM_COMMIT.txt"

kubectl apply -f "$OUT/fabricgateway_crd.yaml"
kubectl wait --for=condition=Established crd/fabricgateways.zalando.org --timeout=120s
kubectl apply -f "$OUT/02-validation.yaml"
kubectl get validatingadmissionpolicy fabricgateway-policy.zalando.org -o yaml > "$OUT/policy-live.yaml"
kubectl get validatingadmissionpolicybinding fabricgateway-policy.zalando.org -o yaml > "$OUT/binding-live.yaml"

cat > "$OUT/reject-missing-stackversion.yaml" <<'EOF'
apiVersion: zalando.org/v1
kind: FabricGateway
metadata:
  name: reject-missing-stackversion
  namespace: default
spec:
  x-external-service-provider:
    hosts: ["example.test"]
    stackSetName: example
EOF
cat > "$OUT/accept-with-stackversion.yaml" <<'EOF'
apiVersion: zalando.org/v1
kind: FabricGateway
metadata:
  name: accept-with-stackversion
  namespace: default
spec:
  x-external-service-provider:
    hosts: ["example.test"]
    stackSetName: example
    stackVersion: "1.0.0"
EOF
cat > "$OUT/accept-fabric-service.yaml" <<'EOF'
apiVersion: zalando.org/v1
kind: FabricGateway
metadata:
  name: accept-fabric-service
  namespace: default
spec:
  x-fabric-service:
    - host: example.test
      serviceName: example
EOF
cat > "$OUT/reject-empty-spec.yaml" <<'EOF'
apiVersion: zalando.org/v1
kind: FabricGateway
metadata:
  name: reject-empty-spec
  namespace: default
spec: {}
EOF

# Wait until the admission policy is observed as active.
start_ns=$(date +%s%N)
attempt=0
activated=0
while [ "$attempt" -lt 60 ]; do
  attempt=$((attempt+1))
  set +e
  kubectl apply --server-side --dry-run=server -f "$OUT/reject-missing-stackversion.yaml" >"$OUT/activation-$attempt.stdout" 2>"$OUT/activation-$attempt.stderr"
  rc=$?
  set -e
  if [ "$rc" -ne 0 ] && grep -F "x-external-service-provider.stackVersion must be set" "$OUT/activation-$attempt.stderr" >/dev/null; then
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
  local file="$1" expected="$2"
  local name
  name=$(basename "$file" .yaml)
  set +e
  kubectl apply --server-side --dry-run=server -f "$file" >"$OUT/$name.stdout" 2>"$OUT/$name.stderr"
  rc=$?
  set -e
  if [ "$rc" -eq 0 ]; then label=ACCEPT; else label=REJECT; fi
  printf '%s\t%s\t%s\t%s\n' "$name" "$expected" "$rc" "$label" >> "$OUT/cases.tsv"
  if [ "$label" != "$expected" ]; then
    cat "$OUT/$name.stderr" >&2
    return 1
  fi
}
run_case "$OUT/reject-missing-stackversion.yaml" REJECT
run_case "$OUT/accept-with-stackversion.yaml" ACCEPT
run_case "$OUT/accept-fabric-service.yaml" ACCEPT
run_case "$OUT/reject-empty-spec.yaml" REJECT

grep -F "x-external-service-provider.stackVersion must be set" "$OUT/reject-missing-stackversion.stderr" >/dev/null
sha256sum "$OUT"/*.yaml > "$OUT/SHA256SUMS.txt"
cat "$OUT/activation.tsv"
cat "$OUT/cases.tsv"
