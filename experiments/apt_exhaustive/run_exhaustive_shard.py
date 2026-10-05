#!/usr/bin/env python3
import argparse, hashlib, json, os, shutil, subprocess, time
from pathlib import Path

PROTECTED=("Origin","Label","Codename")
ALL_FIELDS=("Origin","Label","Codename","Suite","Version")
BASE={"Origin":"EEQ-Origin-A","Label":"EEQ-Label-A","Codename":"alpha","Suite":"stable","Version":"1"}
ALT={"Origin":"EEQ-Origin-B","Label":"EEQ-Label-B","Codename":"beta","Suite":"testing","Version":"2"}
DATE="Wed, 01 Jan 2025 00:00:00 +0000"
VALID_UNTIL="Tue, 01 Jan 2035 00:00:00 +0000"

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def run(cmd, env=None):
    return subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env)

def classify(code,out):
    lo=out.lower()
    if "no_pubkey" in lo or "signatures couldn't be verified" in lo or "is not signed" in lo or "signature verification" in lo or "missing key" in lo:
        return "REJECT_AUTH"
    if "must be accepted explicitly" in lo or ("changed its" in lo and "value from" in lo):
        return "BLOCK_CONFIRM"
    if code==0: return "ACCEPT"
    return "REJECT_OTHER"

def setup_keys(work):
    gnupg=work/"gnupg"; gnupg.mkdir(parents=True,mode=0o700); os.chmod(gnupg,0o700)
    env=dict(os.environ,GNUPGHOME=str(gnupg))
    for uid in ("EEQ Exhaustive A <a@example.invalid>","EEQ Exhaustive B <b@example.invalid>"):
        p=run(["gpg","--batch","--passphrase","","--quick-generate-key",uid,"ed25519","sign","0"],env)
        if p.returncode: raise RuntimeError(p.stdout)
    out=subprocess.check_output(["gpg","--batch","--list-keys","--with-colons"],env=env,text=True)
    ids=[x.split(":")[4] for x in out.splitlines() if x.startswith("pub:")]
    keyrings={}
    for label,kid in zip(("A","B"),ids[:2]):
        path=work/f"key{label}.gpg"
        with open(path,"wb") as fh:
            q=subprocess.run(["gpg","--batch","--yes","--export",kid],env=env,stdout=fh,stderr=subprocess.PIPE)
        if q.returncode: raise RuntimeError(q.stderr.decode())
        keyrings[label]=(kid,path)
    return env,keyrings

def release_text(fields, pkg_path):
    md5=hashlib.md5(pkg_path.read_bytes()).hexdigest()
    sh=hashlib.sha256(pkg_path.read_bytes()).hexdigest()
    rel=Path("main/binary-amd64/Packages")
    s="".join(f"{k}: {fields[k]}\n" for k in ("Origin","Label","Suite","Version","Codename"))
    s+=f"Date: {DATE}\nValid-Until: {VALID_UNTIL}\nArchitectures: amd64\nComponents: main\n"
    s+="Description: EEQ exhaustive APT oracle\n"
    s+=f"MD5Sum:\n {md5} {pkg_path.stat().st_size} {rel.as_posix()}\n"
    s+=f"SHA256:\n {sh} {pkg_path.stat().st_size} {rel.as_posix()}\n"
    return s

def make_signed(fields,label,cache_dir,env,keyrings,pkg_path):
    cache_dir.mkdir(parents=True,exist_ok=True)
    rel=cache_dir/"Release"; inrel=cache_dir/"InRelease"
    rel.write_text(release_text(fields,pkg_path))
    kid=keyrings[label][0]
    p=run(["gpg","--batch","--yes","--local-user",kid,"--clearsign","--output",str(inrel),str(rel)],env)
    if p.returncode: raise RuntimeError(p.stdout)
    return rel,inrel

def install(repo,artifact):
    shutil.copy2(artifact/"Release",repo/"dists/stable/Release")
    shutil.copy2(artifact/"InRelease",repo/"dists/stable/InRelease")

def extras(row):
    xs=[]
    if row["allow_global"]: xs.append("--allow-releaseinfo-change")
    for f in row["allow_fields"]: xs.append("--allow-releaseinfo-change-"+f.lower())
    return xs

def apt_update(root,repo,keyring,extra):
    cmd=[
      "apt-get",
      "-o",f"Dir::Etc::sourcelist={root}/sources.list",
      "-o","Dir::Etc::sourceparts=-",
      "-o",f"Dir::State::lists={root}/lists",
      "-o",f"Dir::Cache={root}/cache",
      "-o","Debug::NoLocking=true",
      "-o","APT::Get::List-Cleanup=false",
      "-o","Acquire::Languages=none",
      "-o","Acquire::Check-Valid-Until=false",
      *extra,"update"
    ]
    t0=time.perf_counter_ns(); p=run(cmd); t1=time.perf_counter_ns()
    return p.returncode,p.stdout,cmd,t1-t0

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--predictions",default="experiments/apt_exhaustive/PREDICTIONS_BEFORE_NATIVE.json")
    ap.add_argument("--out",required=True)
    ap.add_argument("--shard-index",type=int,required=True)
    ap.add_argument("--shard-count",type=int,required=True)
    args=ap.parse_args()
    pred_path=Path(args.predictions).resolve()
    mapping_path=pred_path.with_name("FROZEN_MAPPING.md")
    data=json.loads(pred_path.read_text())
    selected=[r for i,r in enumerate(data["rows"]) if i%args.shard_count==args.shard_index]

    out=Path(args.out).resolve()
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    work=out/"work"; work.mkdir()
    logs=out/"logs"; logs.mkdir()
    repo=work/"repo"; pkg=repo/"dists/stable/main/binary-amd64/Packages"
    pkg.parent.mkdir(parents=True); pkg.write_bytes(b"")
    (out/"frozen_input_hashes.json").write_text(json.dumps({
      "mapping_sha256":sha256(mapping_path),
      "predictions_sha256":sha256(pred_path),
      "predictions_commit_contract":"predictions committed before exhaustive workflow",
    },indent=2)+"\n")

    env,keyrings=setup_keys(work)
    (out/"key_fingerprints.json").write_text(json.dumps({k:v[0] for k,v in keyrings.items()},indent=2)+"\n")
    cache=work/"artifacts"
    prev=cache/"prev-base-A"; make_signed(BASE,"A",prev,env,keyrings,pkg)

    current_cache={}
    for mask in range(32):
        fields=dict(BASE)
        for i,f in enumerate(ALL_FIELDS):
            if mask&(1<<i): fields[f]=ALT[f]
        for signer in ("A","B"):
            d=cache/f"current-{mask:02d}-{signer}"
            make_signed(fields,signer,d,env,keyrings,pkg)
            current_cache[(mask,signer)]=d

    keyA=keyrings["A"][1]
    rows=[]; mismatches=0; other=0
    for row in selected:
        root=work/"roots"/row["id"]
        (root/"lists/partial").mkdir(parents=True)
        (root/"cache/archives/partial").mkdir(parents=True)
        (root/"sources.list").write_text(f"deb [signed-by={keyA}] file:{repo} stable main\n")

        install(repo,prev)
        c0,o0,_,prime_ns=apt_update(root,repo,keyA,[])
        prime_action=classify(c0,o0)
        if prime_action!="ACCEPT":
            (logs/f"{row['id']}.prime.log").write_text(o0)
            raise RuntimeError(f"priming failed {row['id']}: {prime_action}")

        mask=0
        for i,f in enumerate(PROTECTED):
            if row["protected_changed"][f]: mask|=(1<<i)
        if row["suite_changed"]: mask|=(1<<3)
        if row["version_changed"]: mask|=(1<<4)
        signer="A" if row["qualified"] else "B"
        install(repo,current_cache[(mask,signer)])
        code,outtext,cmd,decision_ns=apt_update(root,repo,keyA,extras(row))
        native=classify(code,outtext)
        (logs/f"{row['id']}.log").write_text(outtext)
        match=(native==row["expected"])
        if not match: mismatches+=1
        if native=="REJECT_OTHER": other+=1
        rows.append({
          **row,
          "native_action":native,
          "native_rc":code,
          "match":match,
          "current_mask":mask,
          "current_signer":signer,
          "prime_ns":prime_ns,
          "decision_ns":decision_ns,
          "log_sha256":sha256(logs/f"{row['id']}.log"),
          "command":cmd,
        })
        shutil.rmtree(root)

    summary={
      "apt_version":subprocess.check_output(["apt-get","--version"],text=True).splitlines()[0],
      "shard_index":args.shard_index,
      "shard_count":args.shard_count,
      "selected":len(selected),
      "matched":sum(r["match"] for r in rows),
      "mismatches":mismatches,
      "reject_other":other,
      "rows":rows,
    }
    (out/"shard_results.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in summary.items() if k!="rows"},sort_keys=True))
    if mismatches or other: raise SystemExit(2)

if __name__=="__main__": main()
