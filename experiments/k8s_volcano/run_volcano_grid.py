#!/usr/bin/env python3
import json, subprocess, sys, time, hashlib, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRED = ROOT / "experiments/k8s_volcano/VOLCANO_GRID_PREDICTIONS_BEFORE_NATIVE.json"
MAP = ROOT / "experiments/k8s_volcano/VOLCANO_FROZEN_MAPPING.md"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "volcano-results")
OUT.mkdir(parents=True, exist_ok=True)

UPSTREAM_COMMIT = "e0905bab6fe49b5df2948edb001703c523525784"
UPSTREAM_BLOB = "435232ea78684f2406a0b20e577ef8ffd8dd12aa"
UPSTREAM_URL = f"https://raw.githubusercontent.com/volcano-sh/volcano/{UPSTREAM_COMMIT}/installer/helm/chart/volcano/policy/pods-validating.yaml"
TARGET_MESSAGES = [
    "not allow configure multiple annotations at same time",
    "jdb-min-available must be a positive integer or a valid percentage which between 1% ~ 99%",
    "jdb-max-unavailable must be a positive integer or a valid percentage which between 1% ~ 99%",
]

def run(cmd, check=True, input_text=None):
    p = subprocess.run(cmd, text=True, input=input_text,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and p.returncode != 0:
        sys.stderr.write("$ " + " ".join(cmd) + "\n" + p.stdout + p.stderr)
        raise SystemExit(p.returncode)
    return p

def k(*args, check=True):
    return run(["kubectl", *args], check=check)

policy = OUT / "upstream-pods-validating.yaml"
with urllib.request.urlopen(UPSTREAM_URL, timeout=120) as r:
    policy.write_bytes(r.read())
blob = run(["git","hash-object",str(policy)]).stdout.strip()
(OUT / "UPSTREAM_IDENTITY.txt").write_text(
    f"commit\t{UPSTREAM_COMMIT}\nexpected_blob\t{UPSTREAM_BLOB}\nobserved_blob\t{blob}\nurl\t{UPSTREAM_URL}\n",
    encoding="utf-8")
if blob != UPSTREAM_BLOB:
    raise SystemExit(f"upstream blob mismatch: {blob} != {UPSTREAM_BLOB}")

k("apply","-f",str(policy))
k("get","validatingadmissionpolicy","pod-validation-policy","-o","yaml")
k("get","validatingadmissionpolicybinding","pod-validation-policy-binding","-o","yaml")

# Preserve exact frozen input identities used by this run.
with (OUT / "FROZEN_INPUT_SHA256SUMS.txt").open("w", encoding="utf-8") as fh:
    for p in [MAP, PRED]:
        fh.write(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n")

def pod_yaml(case_id, scheduler, minv, maxv):
    lines = [
        "apiVersion: v1",
        "kind: Pod",
        "metadata:",
        f"  name: {case_id}",
    ]
    anns=[]
    if minv != "absent":
        anns.append(("volcano.sh/jdb-min-available", minv))
    if maxv != "absent":
        anns.append(("volcano.sh/jdb-max-unavailable", maxv))
    if anns:
        lines.append("  annotations:")
        for key,val in anns:
            lines.append(f'    {key}: "{val}"')
    lines += [
        "spec:",
        f"  schedulerName: {scheduler}",
        "  restartPolicy: Never",
        "  containers:",
        "    - name: c",
        "      image: registry.k8s.io/pause:3.10",
    ]
    return "\n".join(lines)+"\n"

def execute(case_id, yaml_text):
    pth=OUT/f"{case_id}.yaml"
    pth.write_text(yaml_text, encoding="utf-8")
    p=k("create","--dry-run=server","-f",str(pth),check=False)
    (OUT/f"{case_id}.stdout").write_text(p.stdout,encoding="utf-8")
    (OUT/f"{case_id}.stderr").write_text(p.stderr,encoding="utf-8")
    if p.returncode == 0:
        return "ACCEPT","ADMITTED"
    if any(msg in p.stderr for msg in TARGET_MESSAGES):
        return "REJECT","TARGET_POLICY"
    return "REJECT","NATIVE_ORACLE_AMBIGUOUS"

# Wait for exact target-policy activation before scoring.
activation_yaml=pod_yaml("activation-probe","volcano","1","1")
activated=False
for attempt in range(1,61):
    observed, attr=execute("activation-probe",activation_yaml)
    if observed=="REJECT" and attr=="TARGET_POLICY":
        activated=True
        break
    time.sleep(0.5)
(OUT/"activation.json").write_text(json.dumps({"attempts":attempt,"activated":activated},indent=2)+"\n")
if not activated:
    raise SystemExit("Volcano VAP did not activate with attributable native rejection")

preds=json.loads(PRED.read_text(encoding="utf-8"))
rows=[]
mismatches=0
ambiguous=0
for idx,row in enumerate(preds,1):
    case_id=f"volcano-{idx:03d}"
    observed,attr=execute(case_id,pod_yaml(case_id,row["scheduler"],row["min"],row["max"]))
    if attr=="NATIVE_ORACLE_AMBIGUOUS":
        status="AMBIGUOUS"; ambiguous+=1
    elif observed==row["expected"]:
        status="PASS"
    else:
        status="MISMATCH"; mismatches+=1
    rows.append({
        "case":case_id, **row, "observed":observed,
        "attribution":attr, "status":status
    })

(OUT/"grid_results.json").write_text(json.dumps(rows,indent=2,sort_keys=True)+"\n",encoding="utf-8")
with (OUT/"grid_results.tsv").open("w",encoding="utf-8") as fh:
    fh.write("case\tscheduler\tmin\tmax\texpected\tobserved\tattribution\tstatus\n")
    for r in rows:
        fh.write("\t".join(str(r[k]) for k in ["case","scheduler","min","max","expected","observed","attribution","status"])+"\n")

summary={
    "frozen_rows":len(preds),
    "eligible_rows":len(rows),
    "passes":sum(r["status"]=="PASS" for r in rows),
    "mismatches":mismatches,
    "ambiguous_eligible_rows":ambiguous,
}
(OUT/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps(summary,sort_keys=True))
print((OUT/"grid_results.tsv").read_text(encoding="utf-8"))

entries=[]
for p in sorted(OUT.rglob("*")):
    if p.is_file() and p.name!="SHA256SUMS.txt":
        entries.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(OUT)}")
(OUT/"SHA256SUMS.txt").write_text("\n".join(entries)+"\n",encoding="utf-8")
if mismatches or ambiguous:
    raise SystemExit(1)
