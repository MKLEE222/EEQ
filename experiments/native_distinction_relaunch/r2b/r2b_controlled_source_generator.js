#!/usr/bin/env node
'use strict';

/**
 * R2-B controlled metadata generator. Signing keys are DETERMINISTIC,
 * PUBLIC, TEST-ONLY and reproducible from literal labels. NEVER for production.
 * No tuf-js, no native oracle, no previous outcome labels.
 */
const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const {canon}=require('../tuf_trust_transition_extractor_r1b_v3.js');

const DOMAIN='EEQ-R2B-20261009-DEVELOPMENT-ONLY::';
const PKCS8=Buffer.from('302e020100300506032b657004220420','hex');
const SPKI=Buffer.from('302a300506032b6570032100','hex');
const EXPIRY='2035-01-01T00:00:00Z';
const ROLES=['ROOT_SHARED','TARGETS_A','TARGETS_B','SNAPSHOT_SHARED','TIMESTAMP_SHARED'];
function check(c,s){if(!c)throw Error(s);}
function sha(x){return crypto.createHash('sha256').update(x).digest('hex');}
function roleKey(label) {
  const seed=crypto.createHash('sha256').update(DOMAIN+label,'utf8').digest();
  check(seed.length===32,'BAD_TEST_ONLY_SEED');
  const privateKey=crypto.createPrivateKey({
    key:Buffer.concat([PKCS8,seed]),type:'pkcs8',format:'der'
  });
  const publicKey=crypto.createPublicKey(privateKey).export({format:'der',type:'spki'});
  check(publicKey.subarray(0,SPKI.length).equals(SPKI) &&
    publicKey.length===SPKI.length+32, 'BAD_ED25519_TEST_KEY');
  const pubObj={keytype:'ed25519',scheme:'ed25519',
    keyval:{public:publicKey.subarray(-32).toString('hex')}};
  const id=sha(Buffer.from(canon(pubObj),'utf8'));
  return {label,id,key:pubObj,privateKey};
}
function sign(signed,key) {
  const bytes=Buffer.from(canon(signed),'utf8');
  const sig=crypto.sign(null,bytes,key.privateKey).toString('hex');
  const publicDer=crypto.createPublicKey(key.privateKey);
  check(crypto.verify(null,bytes,publicDer,Buffer.from(sig,'hex')),
    'TEST_SIGN_SELF_VERIFICATION_FAILURE');
  return {signatures:[{keyid:key.id,sig}],signed};
}
function root(version,targets,keys) {
  const rk=keys.ROOT_SHARED, sk=keys.SNAPSHOT_SHARED, tk=keys.TIMESTAMP_SHARED;
  const dictionary={};
  for(const k of [rk,targets,sk,tk])dictionary[k.id]=k.key;
  const roles={
    root:{keyids:[rk.id],threshold:1},
    targets:{keyids:[targets.id],threshold:1},
    snapshot:{keyids:[sk.id],threshold:1},
    timestamp:{keyids:[tk.id],threshold:1}
  };
  return sign({
    _type:'root',spec_version:'1.0.0',consistent_snapshot:true,
    version,expires:EXPIRY,keys:dictionary,roles
  },rk);
}
function targetMetadata(targetsSigner) {
  return sign({
    _type:'targets',spec_version:'1.0.0',version:1,expires:EXPIRY,
    targets:{
      'artifact.bin':{length:8,hashes:{sha256:sha(Buffer.from('EEQ-R2B-'))}}
    }
  },targetsSigner);
}
function run(dir){
  fs.mkdirSync(dir,{recursive:true});
  const keys=Object.fromEntries(ROLES.map(label=>[label,roleKey(label)]));
  const docs={
    'anchor_a.root.json':root(1,keys.TARGETS_A,keys),
    'anchor_b.root.json':root(1,keys.TARGETS_B,keys),
    'candidate_2.root.json':root(2,keys.TARGETS_A,keys),
    'candidate_3.root.json':root(3,keys.TARGETS_B,keys),
    'targets_a.targets.json':targetMetadata(keys.TARGETS_A),
    'targets_b.targets.json':targetMetadata(keys.TARGETS_B)
  };
  const sourceFiles=[];
  for(const [name,obj] of Object.entries(docs)){
    const raw=Buffer.from(JSON.stringify(obj,null,2)+'\n','utf8');
    fs.writeFileSync(path.join(dir,name),raw);
    sourceFiles.push({name,sha256:sha(raw),bytes:raw.length,
      signed_canonical_sha256:sha(Buffer.from(canon(obj.signed)))});
  }
  const a=docs['anchor_a.root.json'].signed;
  const b=docs['anchor_b.root.json'].signed;
  check(a.roles.root.keyids.join('|')===b.roles.root.keyids.join('|') &&
    a.roles.root.threshold===b.roles.root.threshold && a.version===b.version,
    'ROOT_AUTHORITY_INCORRECTLY_DIFFERENT');
  check(a.roles.targets.keyids.join('|')!==b.roles.targets.keyids.join('|'),
    'TARGETS_AUTHORITY_NOT_ACTUALLY_DIFFERENT');
  check(new Set(sourceFiles.map(x=>x.sha256)).size===sourceFiles.length,
    'SOURCES_NOT_DISTINCT');
  return{
    schema:'eeq-r2b-controlled-sources-v1',
    evidence_class:'CONTROLLED_SIGNED_SOURCE_ONLY_DEVELOPMENT',
    deterministic_test_key_warning:'PRIVATE KEYS DERIVABLE FROM PUBLIC SOURCE; DO NOT USE IN PRODUCTION',
    only_public_signed_metadata_exported:true,
    keyid_method:'SHA256_TUF_OLPC_CANONICAL_PUBLIC_KEY',
    authorized_root_role_keyid:keys.ROOT_SHARED.id,
    root_a_targets_role_keyid:keys.TARGETS_A.id,
    root_b_targets_role_keyid:keys.TARGETS_B.id,
    root_targets_authority_genuinely_differs:true,
    root_update_root_authority_identical:true,
    files:sourceFiles,
    no_native_verifier_invoked:true,
    scored_native_rows:0
  };
}
if(require.main===module){
  if(process.argv.length!==3)
    throw Error('usage: node r2b_controlled_source_generator.js OUT_DIR');
  const report=run(process.argv[2]);
  const outPath=path.join(process.argv[2],'SOURCE_MANIFEST.json');
  fs.writeFileSync(outPath,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({files:report.files.length,
    same_root_role:report.root_update_root_authority_identical,
    different_targets_role:report.root_targets_authority_genuinely_differs,
    native_calls:0}));
}
module.exports={run,roleKey,sign,root,targetMetadata,sha,DOMAIN};
