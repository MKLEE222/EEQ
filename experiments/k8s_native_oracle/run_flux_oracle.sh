#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-results}"
mkdir -p "$OUT"

kubectl version -o yaml > "$OUT/kubectl-version.yaml"
kubectl get --raw /version > "$OUT/server-version.json"

kubectl create namespace eeq-tenant
kubectl label namespace eeq-tenant toolkit.fluxcd.io/tenant=yes
kubectl create namespace eeq-control

kubectl apply -f experiments/k8s_native_oracle/flux_vap.yaml
kubectl wait --for=jsonpath='{.status.typeChecking.expressionWarnings}'='' validatingadmissionpolicy/flux-tenant-pods --timeout=60s || true
kubectl get validatingadmissionpolicy flux-tenant-pods -o yaml > "$OUT/policy-live.yaml"
kubectl get validatingadmissionpolicybinding flux-tenant-pods -o yaml > "$OUT/binding-live.yaml"

cat > "$OUT/cases.tsv" <<'EOF'
case	expected	native_rc	native_label
EOF

run_case () {
  local name="$1" ns="$2" sa="$3" expected="$4"
  local yaml="$OUT/$name.yaml"
  cat > "$yaml" <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: $name
  namespace: $ns
spec:
  restartPolicy: Never
  serviceAccountName: $sa
  containers:
    - name: c
      image: registry.k8s.io/pause:3.10
EOF
  set +e
  kubectl apply --server-side --dry-run=server -f "$yaml" >"$OUT/$name.stdout" 2>"$OUT/$name.stderr"
  rc=$?
  set -e
  if [ "$rc" -eq 0 ]; then label=ACCEPT; else label=REJECT; fi
  printf '%s\t%s\t%s\t%s\n' "$name" "$expected" "$rc" "$label" >> "$OUT/cases.tsv"
  if [ "$label" != "$expected" ]; then
    echo "MISMATCH $name expected=$expected got=$label" >&2
    return 1
  fi
}

run_case tenant-flux eeq-tenant flux REJECT
run_case tenant-default eeq-tenant default ACCEPT
run_case control-flux eeq-control flux ACCEPT
run_case control-default eeq-control default ACCEPT

# Action-effect/control test: removing the tenant selector label changes the native decision
# without changing the submitted Pod manifest.
kubectl label namespace eeq-tenant toolkit.fluxcd.io/tenant-
set +e
kubectl apply --server-side --dry-run=server -f "$OUT/tenant-flux.yaml" >"$OUT/tenant-flux-unlabeled.stdout" 2>"$OUT/tenant-flux-unlabeled.stderr"
rc=$?
set -e
if [ "$rc" -eq 0 ]; then label=ACCEPT; else label=REJECT; fi
printf '%s\t%s\t%s\t%s\n' "tenant-flux-after-label-removal" "ACCEPT" "$rc" "$label" >> "$OUT/cases.tsv"
test "$label" = ACCEPT

sha256sum experiments/k8s_native_oracle/flux_vap.yaml "$OUT"/*.yaml > "$OUT/SHA256SUMS.txt"
cat "$OUT/cases.tsv"

# workflow trigger marker: parityplus-r2
