#!/usr/bin/env node
'use strict';
/*
 * R4-D0 pre-registered SOURCE-ONLY controlled TUF experiment.
 * All keys are deterministic PUBLIC TEST material. NO tuf-js imports.
 * Native outcomes are never loaded or consulted.
 */
const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const {canon,verifySignature,verifyRole,hash}=
  require('../tuf_trust_transition_extractor_r1b_v3.js');
const DOMAIN='EEQ_R4_TUF_AUTHORITY_V1_TEST_ONLY/';
const ED_PKCS8=Buffer.from('302e020100300506032b657004220420','hex');
const LABELS=['ANCHOR','ROOT_A','ROOT_B','ROOT_NEXT','TARGETS','SNAPSHOT','TIMESTAMP'];
const SOURCE_NAMES=[
 'root-1-common.json','root-2-a.json','root-2-b.json',
 'root-3-a.json','root-3-b.json','root-3-old-only.json','root-3-new-only.json'
];
const STATES=['s2a','s2b'];
const ACTIONS=[
 'submit-root-3-a','submit-root-3-b',
 'submit-root-3-old-only','submit-root-3-new-only'
];
function check(ok,msg){if(!ok)throw Error(msg);}
const sha=v=>crypto.createHash('sha256').update(v).digest('hex');
function material(label){
  check(LABELS.includes(label),'UNREGISTERED_TEST_KEY_LABEL');
  const seed=crypto.createHash('sha256').update(DOMAIN+label,'utf8').digest();
  const priv=crypto.createPrivateKey({
    key:Buffer.concat([ED_PKCS8,seed]),type:'pkcs8',format:'der'});
  const spki=crypto.createPublicKey(priv).export({format:'der',type:'spki'});
  const key={keytype:'ed25519',scheme:'ed25519',
    keyval:{public:spki.subarray(spki.length-32).toString('hex')}};
  const keyid=sha(Buffer.from(canon(key),'utf8'));
  return {label,key,keyid,priv};
}
function allKeys(){
  return Object.fromEntries(LABELS.map(l=>[l,material(l)]));
}
function signedRoot(version,signer,k){
  check([1,2,3].includes(version),'BAD_REGISTERED_VERSION');
  check(['ANCHOR','ROOT_A','ROOT_B','ROOT_NEXT'].includes(signer),'BAD_SIGNER_ROLE');
  const roleSigner=k[signer],targets=k.TARGETS,snapshot=k.SNAPSHOT,timestamp=k.TIMESTAMP;
  const keys={};
  for(const key of [roleSigner,targets,snapshot,timestamp])
    keys[key.keyid]=key.key;
  return {
    _type:'root',spec_version:'1.0.31',
    version,expires:'2036-01-01T00:00:00Z',
    consistent_snapshot:true,
    keys,roles:{
      root:{keyids:[roleSigner.keyid],threshold:1},
      targets:{keyids:[targets.keyid],threshold:1},
      snapshot:{keyids:[snapshot.keyid],threshold:1},
      timestamp:{keyids:[timestamp.keyid],threshold:1},
    },
  };
}
function envelope(signed,signers){
  const bytes=Buffer.from(canon(signed),'utf8');
  const signatures=signers.map(s=>{
    const sig=crypto.sign(null,bytes,s.priv).toString('hex');
    check(verifySignature(s.key,bytes,sig).status==='VERIFIED',
      'SOURCE_SIGN_SELF_CHECK_FAILED_'+s.label);
    return {keyid:s.keyid,sig};
  });
  check(new Set(signatures.map(x=>x.keyid)).size===signatures.length,
    'DUPLICATE_SOURCE_SIGNATURE_KEY');
  return {signed,signatures};
}
function source(name,signed,signers){
  const obj=envelope(signed,signers);
  const raw=Buffer.from(JSON.stringify(obj,null,2)+'\n','utf8');
  return {name,obj,raw,sha256:sha(raw),bytes:raw.length,
    signed_sha256:sha(Buffer.from(canon(signed),'utf8')),
    signer_keyids:signers.map(x=>x.keyid).sort()};
}
function sourceFixtures(){
  const k=allKeys(),out=[];
  out.push(source('root-1-common.json',signedRoot(1,'ANCHOR',k),[k.ANCHOR]));
  out.push(source('root-2-a.json',signedRoot(2,'ROOT_A',k),[k.ANCHOR,k.ROOT_A]));
  out.push(source('root-2-b.json',signedRoot(2,'ROOT_B',k),[k.ANCHOR,k.ROOT_B]));
  const signed3=signedRoot(3,'ROOT_NEXT',k);
  out.push(source('root-3-a.json',signed3,[k.ROOT_A,k.ROOT_NEXT]));
  out.push(source('root-3-b.json',signed3,[k.ROOT_B,k.ROOT_NEXT]));
  out.push(source('root-3-old-only.json',signed3,[k.ROOT_A]));
  out.push(source('root-3-new-only.json',signed3,[k.ROOT_NEXT]));
  check(out.length===7,'SEVEN_SOURCES_REQUIRED');
  check(SOURCE_NAMES.every((v,i)=>v===out[i].name),'SOURCE_SET_CHANGED');
  check(new Set(out.map(s=>s.sha256)).size===7,'SOURCE_BYTES_COLLISION');
  check(new Set(out.filter(s=>s.name.startsWith('root-3-'))
    .map(s=>s.signed_sha256)).size===1,
    'CANDIDATE_SIGNED_ROOT_BODY_CHANGED');
  return {k,sources:out};
}
function asRoot(record){
  const obj=record.obj;
  const signedBytes=Buffer.from(canon(obj.signed),'utf8');
  return {version:obj.signed.version,obj,signedBytes,signedHash:sha(signedBytes),
    hash:record.sha256,name:record.name};
}
function authorityCertificate(trusted,candidate){
  const old=verifyRole(trusted,candidate);
  const fresh=verifyRole(candidate,candidate);
  const next=candidate.version===trusted.version+1;
  let effect='KEEP_TRUST_ROOT';
  if(next && (old.status==='UNKNOWN'||fresh.status==='UNKNOWN'))
    effect='MODEL_UNSUPPORTED';
  else if(next && old.status==='SUFFICIENT'&&fresh.status==='SUFFICIENT')
    effect='ADVANCE_TRUST_ROOT';
  let reason='SOURCE_AUTHORITY_INCOMPLETE';
  if(!next)reason='VERSION_NOT_CONTIGUOUS';
  else if(effect==='MODEL_UNSUPPORTED')reason='MATERIAL_UNKNOWN';
  else if(effect==='ADVANCE_TRUST_ROOT')reason='DUAL_ROLE_AUTHORIZED';
  else if(old.status!=='SUFFICIENT')reason='OLD_AUTHORITY_NOT_SATISFIED';
  else if(fresh.status!=='SUFFICIENT')reason='NEW_AUTHORITY_NOT_SATISFIED';
  return {old,fresh,version_contiguous:next,effect,reason};
}
function build(){
  const {k,sources}=sourceFixtures();
  const sourceMap=new Map(sources.map(s=>[s.name,s]));
  const anchor=asRoot(sourceMap.get('root-1-common.json'));
  const states=[
    {state:'s2a',file:'root-2-a.json'},
    {state:'s2b',file:'root-2-b.json'}
  ].map(x=>{
    const root=asRoot(sourceMap.get(x.file));
    const prior=authorityCertificate(anchor,root);
    check(prior.effect==='ADVANCE_TRUST_ROOT',
      'CONTROLLED_NATIVE_ANCHOR_AUTHORIZATION_FAIL_'+x.state);
    check(verifyRole(root,root).status==='SUFFICIENT','ROOT2_NOT_SELF_SIGNED');
    return {state:x.state,source_file:x.file,source_sha256:root.hash,
      signed_source_sha256:root.signedHash,root_version:root.version,
      root_keyids:[...root.obj.signed.roles.root.keyids].sort(),
      setup_proof:prior};
  });
  check(states[0].root_version===states[1].root_version &&
    states[0].root_keyids[0]!==states[1].root_keyids[0],
    'SAME_VERSION_DIFFERENT_AUTHORITY_NOT_INSTANTIATED');
  const candidates=ACTIONS.map(action=>{
    const suffix=action.replace('submit-root-3-','');
    const file='root-3-'+suffix+'.json';
    const s=sourceMap.get(file);
    check(!!s,'UNREGISTERED_CANDIDATE_SOURCE');
    return {action,source_file:file,source_sha256:s.sha256,
      signed_source_sha256:s.signed_sha256,signature_keyids:s.signer_keyids};
  });
  const predictions=[];
  for(const state of states){
    const trusted=asRoot(sourceMap.get(state.source_file));
    for(const c of candidates){
      const root=asRoot(sourceMap.get(c.source_file));
      const proof=authorityCertificate(trusted,root);
      predictions.push({
        state:state.state,action:c.action,
        initial_source_sha256:trusted.hash,
        candidate_source_sha256:root.hash,
        candidate_signed_sha256:root.signedHash,
        initial_root_version:trusted.version,
        candidate_root_version:root.version,
        native_expected:proof.effect==='ADVANCE_TRUST_ROOT'?'ACCEPT':
          proof.effect==='KEEP_TRUST_ROOT'?'REJECT':'MODEL_UNSUPPORTED',
        model_effect:proof.effect,
        expected_post_source_file:proof.effect==='ADVANCE_TRUST_ROOT'?
          c.source_file:state.source_file,
        expected_post_source_sha256:proof.effect==='ADVANCE_TRUST_ROOT'?
          root.hash:trusted.hash,
        old_authority:proof.old,
        new_authority:proof.fresh,
        certificate_reason:proof.reason,
        native_labels_read:false,
      });
    }
  }
  check(predictions.length===8,'EIGHT_REGISTERED_CELLS_REQUIRED');
  const positives=predictions.filter(p=>p.native_expected==='ACCEPT');
  check(positives.length===2 &&
    positives.some(p=>p.state==='s2a'&&p.action==='submit-root-3-a')&&
    positives.some(p=>p.state==='s2b'&&p.action==='submit-root-3-b'),
    'EXPECTED_D0_CONTRAST_NOT_INSTANTIATED');
  check(predictions.every(p=>p.native_expected!=='MODEL_UNSUPPORTED'),
    'MATERIAL_SIGNER_UNRESOLVED');
  const stage1={
    schema:'eeq-r4-d0-source-only-prediction-v1',
    purpose:'TEST_VERSION_SUFFICIENCY_NOT_R4_B9_SUPERIORITY',
    native_outcomes_read:false,native_oracle_invoked:false,
    evidence_class:'CONTROLLED_CRYPTOGRAPHIC_NATIVE_DEVELOPMENT',
    states,candidates,predictions,
    strong_b9:{
      receives:'FULL_NATIVE_TRUST_ROOT_KEYS_CANDIDATE_KEYIDS_SIGNATURE_BYTES',
      prediction_matches:8,total:8,
      fairness_note:'Same admissible signer/role/version sources as EEQ',
    },
    version_only_ablation:{
      sufficient:false,
      strongest_version_plus_candidate_identity_optimal_matches:6,
      total:8,
      naive_version_adjacent_accept_matches:2,
      strong_b9:false,
    },
    summary:{
      registered_states:2,registered_candidates:4,registered_cells:8,
      accepted:2,rejected:6,unknown:0,
      common_root1_legal_setup_preverified:true,
      same_root_version_different_old_role_keyids:true,
      identical_signed_root3_body:true,
    },
    original_g5_increment:0,
  };
  const manifest={
    schema:'eeq-r4-d0-source-manifest-v1',
    public_test_seed_domain:DOMAIN,
    sources:sources.map(x=>({
      name:x.name,sha256:x.sha256,bytes:x.bytes,
      signed_sha256:x.signed_sha256,
    })),
    public_keyids:Object.fromEntries(LABELS.map(x=>[x,k[x].keyid])),
    native_called:false,
    original_g5_increment:0,
  };
  return {sources,stage1,manifest};
}
function write(outDir){
  fs.mkdirSync(outDir,{recursive:true});
  const data=build();
  for(const source of data.sources)
    fs.writeFileSync(path.join(outDir,source.name),source.raw);
  fs.writeFileSync(path.join(outDir,'SOURCE_PREDICTIONS.json'),
    JSON.stringify(data.stage1,null,2)+'\n');
  fs.writeFileSync(path.join(outDir,'SOURCE_MANIFEST.json'),
    JSON.stringify(data.manifest,null,2)+'\n');
  console.log(JSON.stringify({
    ...data.stage1.summary,
    version_only_ceiling:data.stage1.version_only_ablation
      .strongest_version_plus_candidate_identity_optimal_matches,
    strong_b9:data.stage1.strong_b9.prediction_matches,
    native_called:false,
  }));
}
if(require.main===module){
  check(process.argv.length===3,'usage: r4_d0_tuf_sources.js OUT_DIR');
  write(process.argv[2]);
}
module.exports={allKeys,sourceFixtures,asRoot,authorityCertificate,build,write};
