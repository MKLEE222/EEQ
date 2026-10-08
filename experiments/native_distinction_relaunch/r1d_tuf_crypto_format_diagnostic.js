#!/usr/bin/env node
'use strict';
// R1d DIAGNOSTIC ONLY. Compares cryptographic input formats; never invokes
// TrustedMetadataStore/updateRoot, reads native decisions or scores methods.
const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const {canonicalize}=require('@tufjs/canonical-json');
const {canon,hash}=require('./tuf_trust_transition_extractor_r1b_v2.js');

function verifyWith(pub,buf,signature,algorithm,salt){
  if(!pub || !signature) return false;
  try{
    const k=crypto.createPublicKey(pub);
    return crypto.verify(algorithm,buf,{
      key:k,padding:crypto.constants.RSA_PKCS1_PSS_PADDING,
      saltLength:salt}, Buffer.from(signature,'hex'));
  }catch(_){return false}
}
function probe(root, candidate, candidates){
  const role=root.signed.roles.root;
  const sigs=new Map(candidate.signatures.map(s=>[s.keyid,s.sig]));
  const rows=[];
  for(const id of role.keyids){
    const key=root.signed.keys[id];
    const sig=sigs.get(id);
    if(!sig)continue;
    const pub=key && key.keyval && key.keyval.public;
    rows.push({
      keyid:id,scheme:key?.scheme,keytype:key?.keytype,
      public_is_pem:!!pub&&pub.startsWith('-----BEGIN PUBLIC KEY-----'),
      signature_hex_length:typeof sig==='string'?sig.length:null,
      own_sha256_auto:verifyWith(pub,candidates.own,sig,'sha256',crypto.constants.RSA_PSS_SALTLEN_AUTO),
      reference_sha256_auto:verifyWith(pub,candidates.ref,sig,'sha256',crypto.constants.RSA_PSS_SALTLEN_AUTO),
      reference_sha256_digest:verifyWith(pub,candidates.ref,sig,'sha256',crypto.constants.RSA_PSS_SALTLEN_DIGEST),
      reference_default_auto:verifyWith(pub,candidates.ref,sig,undefined,crypto.constants.RSA_PSS_SALTLEN_AUTO),
    });
  }
  const counts={};
  for(const mode of ['own_sha256_auto','reference_sha256_auto','reference_sha256_digest','reference_default_auto']){
    counts[mode]=rows.filter(x=>x[mode]).length;
  }
  return {
    threshold:role.threshold,
    role_keyids:role.keyids.length,
    envelope_matches:rows.length,
    verified_counts:counts,
    signers:rows,
  };
}
function diffInfo(a,b){
  let k=0;
  while(k<a.length && k<b.length && a[k]===b[k])k++;
  return {
    identical:a.equals(b),own_len:a.length,reference_len:b.length,
    first_byte_mismatch:k===a.length&&k===b.length?null:k,
    // Public canonical JSON only. Context is hex to avoid rendering ambiguity.
    own_context_hex:a.subarray(Math.max(0,k-16),k+40).toString('hex'),
    reference_context_hex:b.subarray(Math.max(0,k-16),k+40).toString('hex'),
  };
}
function audit(dir){
  const roots=new Map();
  for(let i=1;i<=8;i++){
    roots.set(i,JSON.parse(fs.readFileSync(path.join(dir,i+'.root.json'),'utf8')));
  }
  const pairs=[];
  for(let n=1;n<=7;n++){
    const before=roots.get(n),after=roots.get(n+1);
    const own=Buffer.from(canon(after.signed),'utf8');
    const ref=Buffer.from(canonicalize(after.signed),'utf8');
    const bytes={own,ref};
    const old=probe(before,after,bytes);
    const fresh=probe(after,after,bytes);
    pairs.push({
      from_version:n,to_version:n+1,
      own_canonical_sha256:hash(own),
      reference_canonical_sha256:hash(ref),
      canonical_comparison:diffInfo(own,ref),
      old_role:old,new_role:fresh,
      native_oracle_invoked:false,
    });
  }
  return {
    schema:'eeq-r1d-source-crypto-format-diagnostic-v1',
    evidence_class:'SOURCE_ONLY_REFERENCE_FORMAT_DIAGNOSIS',
    native_oracle_invoked:false,native_outcome_labels_read:false,
    pairs,
    summary:{
      pairs:pairs.length,
      canonical_equal:pairs.filter(p=>p.canonical_comparison.identical).length,
      threshold_satisfied_with_reference_auto:pairs.filter(p=>
        p.old_role.verified_counts.reference_sha256_auto>=p.old_role.threshold &&
        p.new_role.verified_counts.reference_sha256_auto>=p.new_role.threshold).length,
      threshold_satisfied_with_reference_default:pairs.filter(p=>
        p.old_role.verified_counts.reference_default_auto>=p.old_role.threshold &&
        p.new_role.verified_counts.reference_default_auto>=p.new_role.threshold).length,
    },
  };
}
if(require.main===module){
 if(process.argv.length!==4)throw new Error('usage: node diag.js ROOT_DIR OUT_JSON');
 const p=audit(process.argv[2]);
 fs.writeFileSync(process.argv[3],JSON.stringify(p,null,2)+'\n');
 console.log(JSON.stringify(p.summary));
 for(const x of p.pairs){
  console.log(JSON.stringify({
    from:x.from_version,to:x.to_version,canon_same:x.canonical_comparison.identical,
    old_threshold:x.old_role.threshold,new_threshold:x.new_role.threshold,
    old:x.old_role.verified_counts,new:x.new_role.verified_counts,
  }));
 }
}
module.exports={audit};
