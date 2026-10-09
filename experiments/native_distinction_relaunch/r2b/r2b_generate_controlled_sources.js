#!/usr/bin/env node
'use strict';
/* R2B STAGE I: deterministic CONTROLLED test-only TUF root + targets
 * signature source fixtures and label-blind transitions. NO tuf-js imports.
 * Private signing seeds are PUBLIC, FIXED, TEST-ONLY. NEVER deploy them.
 */
const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const {canon,verifyRole,verifySignature,hash}=
  require('../tuf_trust_transition_extractor_r1b_v3.js');
const DOMAIN='EEQ_R2B_CONTROLLED_PUBLIC_TEST_ONLY_V1/';
const PKCS8_ED=Buffer.from('302e020100300506032b657004220420','hex');
const SHA=v=>crypto.createHash('sha256').update(v).digest('hex');
const STATES=['s2a','s2b','s3a','s3b','s4a','s4b'];
const ACTIONS=['submit-root-3-a','submit-root-3-b','submit-root-4-a','submit-root-4-b'];
const EXPIRY='2036-01-01T00:00:00Z';
function check(v,m){if(!v)throw Error(m);}
function material(label){
  check(['ROOT','TARGET_A','TARGET_B','SNAPSHOT','TIMESTAMP'].includes(label),
    'UNREGISTERED_SIGNER');
  const seed=crypto.createHash('sha256').update(DOMAIN+label,'utf8').digest();
  const privateKey=crypto.createPrivateKey({
    key:Buffer.concat([PKCS8_ED,seed]),format:'der',type:'pkcs8'});
  const der=crypto.createPublicKey(privateKey).export({format:'der',type:'spki'});
  const publicHex=der.subarray(der.length-32).toString('hex');
  check(publicHex.length===64,'BAD_ED25519_PUBLIC');
  const key={keytype:'ed25519',scheme:'ed25519',keyval:{public:publicHex}};
  return {label,key,keyid:SHA(Buffer.from(canon(key),'utf8')),privateKey};
}
function rootSigned(version,variant,signers){
  check([1,2,3,4].includes(version)&&['a','b'].includes(variant),'BAD_ROOT_VARIANT');
  const r=signers.ROOT,t=signers[variant==='a'?'TARGET_A':'TARGET_B'];
  const s=signers.SNAPSHOT,ts=signers.TIMESTAMP,keys={};
  for(const x of [r,t,s,ts])keys[x.keyid]=x.key;
  return {
    _type:'root',spec_version:'1.0.31',version,expires:EXPIRY,
    keys,roles:{
      root:{keyids:[r.keyid],threshold:1},
      targets:{keyids:[t.keyid],threshold:1},
      snapshot:{keyids:[s.keyid],threshold:1},
      timestamp:{keyids:[ts.keyid],threshold:1}},
    consistent_snapshot:true,
  };
}
function targetsSigned(){
  return {_type:'targets',spec_version:'1.0.31',version:1,
    expires:EXPIRY,targets:{}};
}
function signEnvelope(signed,signer){
  const bytes=Buffer.from(canon(signed),'utf8');
  const sig=crypto.sign(null,bytes,signer.privateKey).toString('hex');
  check(verifySignature(signer.key,bytes,sig).status==='VERIFIED',
    'SIGNATURE_GENERATOR_SELF_CHECK_FAILED');
  return {signed,signatures:[{keyid:signer.keyid,sig}]};
}
function sourceRecord(doc,name){
  const bytes=Buffer.from(JSON.stringify(doc,null,2)+'\n','utf8');
  return {name,bytes,parsed:JSON.parse(bytes.toString('utf8')),
    sha256:SHA(bytes),byte_count:bytes.length};
}
function registeredSources(){
  const signers={};
  for(const label of ['ROOT','TARGET_A','TARGET_B','SNAPSHOT','TIMESTAMP'])
    signers[label]=material(label);
  const records=[];
  function add(name,signed,signer){
    records.push(sourceRecord(signEnvelope(signed,signer),name));
  }
  add('root-1-common.json',rootSigned(1,'a',signers),signers.ROOT);
  for(const version of [2,3,4])for(const branch of ['a','b'])
    add('root-'+version+'-'+branch+'.json',
      rootSigned(version,branch,signers),signers.ROOT);
  for(const branch of ['a','b'])
    add('targets-'+branch+'.json',targetsSigned(),
      signers[branch==='a'?'TARGET_A':'TARGET_B']);
  check(records.length===9,'BAD_FIXTURE_COUNT');
  return {records,public_keyids:Object.fromEntries(
    Object.entries(signers).map(([name,s])=>[name,s.keyid]))};
}
function context(records){
  const files=new Map(records.map(r=>[r.name,r]));
  const roots=new Map();
  for(const [name,record] of files){
    if(!name.startsWith('root-'))continue;
    const m=/^root-([1-4])-(common|a|b)\.json$/.exec(name);
    check(!!m,'BAD_ROOT_FILE_NAME');
    const version=Number(m[1]);
    check(record.parsed.signed.version===version,'BAD_SIGNED_SOURCE_VERSION');
    const bytes=Buffer.from(canon(record.parsed.signed),'utf8');
    const root={version,obj:record.parsed,signedBytes:bytes,
      signedHash:SHA(bytes),hash:record.sha256,name};
    check(verifyRole(root,root).status==='SUFFICIENT','BAD_SELF_SIGNED_ROOT');
    roots.set(name,root);
  }
  const stateRoots=new Map(STATES.map(s=>[s,roots.get(
    'root-'+s[1]+'-'+s[2]+'.json')]));
  return {files,roots,stateRoots};
}
function qualification(root,targetsRecord){
  const role=root.obj.signed.roles.targets,keys=root.obj.signed.keys;
  const signedBytes=Buffer.from(canon(targetsRecord.parsed.signed),'utf8');
  const verified=new Set(),unknown=new Set();
  for(const signature of targetsRecord.parsed.signatures){
    if(!role.keyids.includes(signature.keyid))continue;
    const proof=verifySignature(keys[signature.keyid],
      signedBytes,signature.sig);
    if(proof.status==='VERIFIED')verified.add(signature.keyid);
    else if(proof.status==='UNKNOWN')unknown.add(signature.keyid);
  }
  const status=verified.size>=role.threshold?'QUALIFIED':
    verified.size+unknown.size>=role.threshold?'MODEL_UNSUPPORTED':'UNQUALIFIED';
  return {status,verified_keyids:[...verified].sort(),
    unknown_keyids:[...unknown].sort(),threshold:role.threshold};
}
function edge(start,action,candidate){
  const oldProof=verifyRole(start.root,candidate);
  const newProof=verifyRole(candidate,candidate);
  const contiguous=candidate.version===start.root.version+1;
  let effect='KEEP_TRUST_ROOT';
  if(contiguous){
    if(oldProof.status==='UNKNOWN'||newProof.status==='UNKNOWN')
      effect='MODEL_UNSUPPORTED';
    else if(oldProof.status==='SUFFICIENT'&&newProof.status==='SUFFICIENT')
      effect='ADVANCE_TRUST_ROOT';
  }
  const branch=/-([ab])\.json$/.exec(candidate.name);
  check(!!branch,'BAD_ACTION_SOURCE');
  const to=effect==='MODEL_UNSUPPORTED'?null:
    effect==='ADVANCE_TRUST_ROOT'?'s'+candidate.version+branch[1]:start.state;
  return {
    from_state:start.state,action:action.action,
    from_source_sha256:start.root.hash,
    candidate_source_sha256:candidate.hash,
    candidate_signed_sha256:candidate.signedHash,
    old_role:oldProof,new_role:newProof,
    version_contiguous:contiguous,effect,to_state:to,native_called:false,
  };
}
function quotient(states,actions,edges){
  const byKey=new Map(edges.map(e=>[e.from_state+'|'+e.action,e]));
  check(byKey.size===states.length*actions.length,'MISSING_EDGE');
  function get(s,a){
    const e=byKey.get(s+'|'+a);
    check(e&&e.to_state,'UNSUPPORTED_OR_MISSING_FUTURE_EDGE');
    return e;
  }
  function output(s){return actions.map(a=>get(s,a).effect)}
  let previous=null,groups=[];
  for(let horizon=0;horizon<=2;horizon++){
    const sigs=states.map(s=>JSON.stringify(horizon===0?output(s):
      [output(s),actions.map(a=>previous.get(get(s,a).to_state))]));
    const distinct=[...new Set(sigs)].sort();
    const code=new Map(states.map((s,i)=>[s,distinct.indexOf(sigs[i])]));
    const classes=distinct.map((_,i)=>states.filter(s=>code.get(s)===i));
    groups.push({horizon,classes,class_count:classes.length,
      legal_merges:states.length-classes.length});
    previous=code;
  }
  const words=[[]];
  for(const a of actions)words.push([a]);
  for(const a of actions)for(const b of actions)words.push([a,b]);
  check(words.length===21,'INCORRECT_REGISTERED_WORD_COUNT');
  function trace(s,word){
    const events=[];
    for(const a of word){
      const e=get(s,a);events.push(e.effect);s=e.to_state;
    }
    return events;
  }
  for(const a of states)for(const b of states){
    const same=JSON.stringify(words.map(w=>trace(a,w)))===
               JSON.stringify(words.map(w=>trace(b,w)));
    check(same===(previous.get(a)===previous.get(b)),
      'EXHAUSTIVE_TRACE_QUOTIENT_DISAGREE');
  }
  return {horizons:groups,action_words_per_state:words.length,
    direct_trace_oracle_agrees:true,full_action_alphabet:true};
}
function build(){
  const {records,public_keyids}=registeredSources();
  const ctx=context(records);
  const states=STATES.map(s=>{
    const root=ctx.stateRoots.get(s),branch=s[2],version=Number(s[1]);
    check(!!root,'UNREGISTERED_STATE');
    return {state:s,version,branch,source_name:root.name,
      source_sha256:root.hash,
      setup_source_names:['root-1-common.json',
        ...Array.from({length:version-1},(_,i)=>
          'root-'+(i+2)+'-'+branch+'.json')],
      root_role_keyids:[...root.obj.signed.roles.root.keyids].sort(),
      targets_role_keyids:[...root.obj.signed.roles.targets.keyids].sort()};
  });
  const actions=ACTIONS.map(action=>{
    const m=/^submit-root-([34])-([ab])$/.exec(action);
    check(!!m,'UNREGISTERED_ACTION');
    const file='root-'+m[1]+'-'+m[2]+'.json';
    return {action,source_name:file,source_sha256:ctx.files.get(file).sha256,
      version:Number(m[1]),branch:m[2]};
  });
  const predictions=[];
  for(const state of states)for(const action of actions){
    predictions.push(edge({state:state.state,
      root:ctx.stateRoots.get(state.state)},action,
      ctx.roots.get(action.source_name)));
  }
  check(predictions.length===24,'BAD_PREDICTION_COUNT');
  const counts={};
  for(const p of predictions)counts[p.effect]=(counts[p.effect]||0)+1;
  check(counts.ADVANCE_TRUST_ROOT===8 &&
        counts.KEEP_TRUST_ROOT===16 && !counts.MODEL_UNSUPPORTED,
        'PREDICTION_CONTRACT_NOT_MET');
  const qualifications=[];
  for(const state of states)for(const branch of ['a','b']){
    const target=ctx.files.get('targets-'+branch+'.json');
    const q=qualification(ctx.stateRoots.get(state.state),target);
    qualifications.push({state:state.state,
      targets_source_name:target.name,targets_sha256:target.sha256,...q});
    check(q.status===(branch===state.branch?'QUALIFIED':'UNQUALIFIED'),
      'TARGET_AUTHORITY_CONTRAST_NOT_PRESENT');
  }
  const q=quotient(STATES,ACTIONS,predictions);
  check(q.horizons.every(x=>x.class_count===3&&x.legal_merges===3),
    'NO_R2B_SOURCE_NONCOSMETIC_MERGE');
  const lastClasses=q.horizons[2].classes.map(a=>a.join(',')).sort();
  check(JSON.stringify(lastClasses)===
    JSON.stringify(['s2a,s2b','s3a,s3b','s4a,s4b']),
    'R2B_BAD_EQUIVALENCE_CLASSES');
  const b9Correct=predictions.filter(row=>{
    const state=states.find(s=>s.state===row.from_state);
    const action=actions.find(a=>a.action===row.action);
    const expected=action.version===state.version+1?
      'ADVANCE_TRUST_ROOT':'KEEP_TRUST_ROOT';
    return expected===row.effect;
  }).length;
  check(b9Correct===24,'B9_STRONG_CEILING_MISSING');

  const manifest={schema:'eeq-r2b-source-manifest-v1',
    evidence_class:'CONTROLLED_NATIVE_CRYPTO',
    sources:records.map(x=>({name:x.name,sha256:x.sha256,bytes:x.byte_count})),
    public_keyids,deterministic_public_test_seed_domain:DOMAIN,
    native_oracle_invoked:false,original_g5_increment:0};
  const model={schema:'eeq-r2b-source-predictions-v1',
    contract:'REGISTERED_ROOT_UPDATE_ONLY_PLUS_TARGETS_QUALIFICATION_NEGATIVE_CONTROL',
    native_outcomes_read:false,native_oracle_invoked:false,
    evidence_class:'CONTROLLED_CRYPTOGRAPHIC_NATIVE_DEVELOPMENT',
    common_anchor_sha256:ctx.files.get('root-1-common.json').sha256,
    states,actions,predictions,qualifications,quotient:q,
    strong_b9:{rule:'trusted_root_version_plus_action_candidate_version',
      matched_source_predictions:b9Correct,total:24},
    summary:{
      states:6,actions:4,one_step_cells:24,
      action_words_per_state:21,total_action_traces:126,
      target_qualification_checks:12,
      advances:counts.ADVANCE_TRUST_ROOT,
      keeps:counts.KEEP_TRUST_ROOT,
      unsupported:counts.MODEL_UNSUPPORTED||0,
      quotient_classes:q.horizons.map(x=>x.class_count),
      valid_noncosmetic_merges:q.horizons[2].legal_merges,
      source_unavailable_challenge:'SOURCE_UNAVAILABLE',
      source_unavailable_native_scored:false,
    },
    warnings:['B9 version-only ceiling ties for J_root',
      'Conventional Moore quotient ties candidate partition',
      'Controlled native feasibility is NOT unseen-family generality',
      'No R2 A future-only distinction or unique method gain scored'],
  };
  return {records,manifest,model};
}
function write(outDir){
  const {records,manifest,model}=build();
  fs.mkdirSync(outDir,{recursive:true});
  for(const x of records)fs.writeFileSync(path.join(outDir,x.name),x.bytes);
  fs.writeFileSync(path.join(outDir,'SOURCE_MANIFEST.json'),
    JSON.stringify(manifest,null,2)+'\n');
  fs.writeFileSync(path.join(outDir,'SOURCE_PREDICTIONS.json'),
    JSON.stringify(model,null,2)+'\n');
  console.log(JSON.stringify({...model.summary,
    native_oracle_invoked:false,b9_source_match:model.strong_b9.matched_source_predictions}));
}
if(require.main===module){
  if(process.argv.length!==3)throw Error('usage: r2b_generate_controlled_sources.js OUTPUT_DIR');
  write(process.argv[2]);
}
module.exports={material,rootSigned,targetsSigned,signEnvelope,
  registeredSources,context,qualification,edge,quotient,build,write};
