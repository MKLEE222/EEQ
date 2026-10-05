#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-results}"
mkdir -p "$OUT"

kubectl version -o yaml > "$OUT/kubectl-version.yaml"
kubectl get --raw /version > "$OUT/server-version.json"

kubectl create namespace eeq-tenant
kubectl label namespace eeq-tenant toolkit.fluxcd.io/tenant=yes
kubectl create namespace eeq-control
kubectl create serviceaccount flux -n eeq-tenant
kubectl create serviceaccount flux -n eeq-control

kubectl apply -f experiments/k8s_native_oracle/flux_vap.yaml
kubectl get validatingadmissionpolicy flux-tenant-pods -o yaml
kubectl get validatingadmissionpolicy flux-tenant-pods -o yaml > "$OUT/policy-live.yaml"
kubectl get validatingadmissionpolicybinding flux-tenant-pods -o yaml > "$OUT/binding-live.yaml"

# Native VAP activation is asynchronously observed by kube-apiserver admission.
# Measure the propagation delay instead of assuming object creation is instantly enforced.
cat > "$OUT/activation-probe.yaml" <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: activation-probe
  namespace: eeq-tenant
spec:
  restartPolicy: Never
  serviceAccountName: flux
  containers:
    - name: c
      image: registry.k8s.io/pause:3.10
EOF
start_ns=$(date +%s%N)
activated=0
attempt=0
while [ "$attempt" -lt 60 ]; do
  attempt=$((attempt+1))
  set +e
  kubectl apply --server-side --dry-run=server -f "$OUT/activation-probe.yaml" >"$OUT/activation-$attempt.stdout" 2>"$OUT/activation-$attempt.stderr"
  rc=$?
  set -e
  if [ "$rc" -ne 0 ] && grep -F "pods in tenant namespaces cannot run under the 'flux' ServiceAccount" "$OUT/activation-$attempt.stderr" >/dev/null; then
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
    cat "$OUT/$name.stderr" >&2
    return 1
  fi
  if [ "$expected" = REJECT ]; then
    grep -F "pods in tenant namespaces cannot run under the 'flux' ServiceAccount" "$OUT/$name.stderr" >/dev/null
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
