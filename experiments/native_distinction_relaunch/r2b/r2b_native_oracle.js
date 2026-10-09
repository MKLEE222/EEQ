#!/usr/bin/env node
'use strict';
/**
 * R2-B NATIVE-ONLY oracle. Absolutely no predictor / quotient imports.
 * Invoke only after frozen source & predictor hash, scorer and package-lock.
 */
const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const {TrustedMetadataStore}=require('tuf-js/dist/store');
const {Metadata,MetadataKind}=require('@tufjs/models');

const ACTIONS=['submit_root3_valid','submit_root3_bad_sig',
               'submit_root2_A_replay'];
const NAMES=['root1.json','root2_A.json','root2_B.json','root3.json',
             'root3_bad_sig.json','targets_A.json','targets_B.json'];
function sha(v){return crypto.createHash('sha256').update(v).digest('hex');}
function parse(dir,name){const v=fs.readFileSync(path.join(dir,name));return {
  bytes:v,sha256:sha(v),json:JSON.parse(v.toString('utf8'))
};}
function errorInfo(e){return {class:e?.constructor?.name||typeof e,
  message:e?.message||String(e)};}
function rootMeta(store){
  if(!store || !store.root || !store.root.signed)return null;
  const s=store.root.signed;
  const roles=s.roles||{};
  function getIDs(role){
    const r=roles[role];
    return Array.isArray(r?.keyIDs)?[...r.keyIDs].sort():null;
  }
  return {root_version:s.version,
    root_role_keyids:getIDs('root'),
    root_role_threshold:roles.root?.threshold??null,
    targets_role_keyids:getIDs('targets'),
    targets_role_threshold:roles.targets?.threshold??null};
}
function actionWords(){
  const all=[[]];
  for(const a of ACTIONS)all.push([a]);
  for(const a of ACTIONS)for(const b of ACTIONS)all.push([a,b]);
  if(all.length!==13 || new Set(all.map(x=>x.join('|'))).size!==13)
    throw new Error('NATIVE_GRID_NOT_13_DISTINCT_WORDS');
  return all;
}
function freshStore(sources,branch){
  let store;
  try{
    store=new TrustedMetadataStore(sources['root1.json'].bytes);
    const next='root2_'+branch+'.json';
    store.updateRoot(sources[next].bytes);
    if(store.root.signed.version!==2)
      throw new Error('TRUST_ROOT_SETUP_STATE_NOT_2');
    return {store,error:null};
  }catch(e){return {store,error:errorInfo(e)}}
}
function runWord(sources,branch,word){
  const setup=freshStore(sources,branch);
  const steps=[],startState=rootMeta(setup.store);
  const actionSource={
    submit_root3_valid:'root3.json',
    submit_root3_bad_sig:'root3_bad_sig.json',
    submit_root2_A_replay:'root2_A.json'
  };
  if(setup.error || !startState || startState.root_version!==2){
    return {
      branch,action_word:word,
      setup_status:'SETUP_FAILURE',setup_error:setup.error||
        {class:'ROOT_STATE_UNOBSERVABLE',message:'root2 not native observable'},
      initial_native_state:startState,steps:[],
      completed:false
    };
  }
  for(const action of word) {
    const from=rootMeta(setup.store);
    const src=sources[actionSource[action]];
    let decision='REJECT',err=null;
    const t0=process.hrtime.bigint();
    try{
      setup.store.updateRoot(src.bytes);
      decision='ACCEPT';
    }catch(e){err=errorInfo(e);}
    const elapsedNs=Number(process.hrtime.bigint()-t0);
    const after=rootMeta(setup.store);
    steps.push({
      action,source_sha256:src.sha256,
      native_action:decision,error:err,
      before_native_state:from,after_native_state:after,
      decision_ns:elapsedNs
    });
  }
  return {branch,action_word:word,
    setup_status:'PASS',setup_error:null,
    initial_native_state:startState,steps,completed:true};
}
function nativeQualifiedTargets(sources){
  const result={};
  const signed={
    A:Metadata.fromJSON(MetadataKind.Targets,sources['targets_A.json'].json),
    B:Metadata.fromJSON(MetadataKind.Targets,sources['targets_B.json'].json)
  };
  for(const state of ['A','B']){
    const root=Metadata.fromJSON(
      MetadataKind.Root,sources['root2_'+state+'.json'].json);
    result[state]={};
    for(const signer of ['A','B']){
      try{
        root.verifyDelegate('targets',signed[signer]);
        result[state][signer]={verified:true,error:null};
      }catch(e){
        result[state][signer]={verified:false,error:errorInfo(e)};
      }
    }
  }
  return result;
}
function run(rootDir){
  const sources=Object.fromEntries(NAMES.map(name=>[name,parse(rootDir,name)]));
  const attempts=[];
  for(const branch of ['A','B'])
    for(const word of actionWords())
      attempts.push(runWord(sources,branch,word));
  const roles=nativeQualifiedTargets(sources);
  const counts={};
  for(const a of attempts){
    const k=a.setup_status;
    counts[k]=(counts[k]||0)+1;
  }
  const actions={};
  for(const a of attempts)for(const step of a.steps)
    actions[step.native_action]=(actions[step.native_action]||0)+1;
  return {
    schema:'eeq-r2b-controlled-tuf-native-oracle-v1',
    evidence_class:'CONTROLLED_NATIVE_DEVELOPMENT',
    package_and_operation:'tuf-js@3.0.1 TrustedMetadataStore.updateRoot',
    targets_qualification_operation:'@tufjs/models Metadata.verifyDelegate',
    actions:ACTIONS,
    branches:['A','B'],
    action_horizon:2,
    source_files:Object.fromEntries(NAMES.map(name=>[
      name,{sha256:sources[name].sha256,bytes:sources[name].bytes.length}
    ])),
    native_outcomes_generated_independently_from_predictions:true,
    predictor_loaded:false,
    native_targets_authorization_cross_check:roles,
    trace_results:attempts,
    summary:{trace_count:attempts.length,traces_per_branch:13,
      setup_status_counts:counts,native_step_action_counts:actions},
    status:'RAW_NATIVE_OUTCOMES_NO_SCIENTIFIC_SCORE_YET'
  };
}
if(require.main===module){
  if(process.argv.length!==4){
    console.error('usage: node r2b_native_oracle.js SOURCE_DIR OUTPUT_JSON');
    process.exit(64);
  }
  try{
    const out=run(process.argv[2]);
    fs.writeFileSync(process.argv[3],JSON.stringify(out,null,2)+'\n');
    console.log(JSON.stringify({
      traces:out.summary.trace_count,
      setup:out.summary.setup_status_counts,
      native_actions:out.summary.native_step_action_counts,
      targets_verified:[
        out.native_targets_authorization_cross_check.A.A.verified,
        out.native_targets_authorization_cross_check.A.B.verified,
        out.native_targets_authorization_cross_check.B.A.verified,
        out.native_targets_authorization_cross_check.B.B.verified
      ],
      predictor_loaded:false
    }));
  }catch(e){console.error(e.stack||String(e));process.exit(2);}
}
module.exports={run,actionWords};
