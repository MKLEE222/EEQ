#!/usr/bin/env node
'use strict';

const fs=require('fs');
const crypto=require('crypto');
const { TrustedMetadataStore }=require('tuf-js/dist/store');

function sha256(buf){ return crypto.createHash('sha256').update(buf).digest('hex'); }
function clone(v){ return JSON.parse(JSON.stringify(v)); }

function transform(control, roots){
  if(control.transform==='replay_current_root'){
    return Buffer.from(roots[1]);
  }
  const root2=JSON.parse(roots[2].toString('utf8'));
  if(control.transform==='remove_all_signatures'){
    root2.signatures=[];
    return Buffer.from(JSON.stringify(root2));
  }
  if(control.transform==='add_signed_field_eeq_controlled_tamper_true'){
    root2.signed.eeq_controlled_tamper=true;
    return Buffer.from(JSON.stringify(root2));
  }
  throw new Error('unknown transform '+control.transform);
}

function main(){
  const predPath=process.argv[2];
  const rootsDir=process.argv[3];
  const outPath=process.argv[4];
  if(!predPath||!rootsDir||!outPath){
    console.error('usage: run_tuf_negative_controls.js PREDICTIONS ROOT_DIR OUT_JSON');
    process.exit(64);
  }
  const pred=JSON.parse(fs.readFileSync(predPath,'utf8'));
  const roots={
    1:fs.readFileSync(rootsDir+'/1.root.json'),
    2:fs.readFileSync(rootsDir+'/2.root.json'),
  };
  const rows=[];
  let failures=0;
  for(const control of pred.controls){
    const store=new TrustedMetadataStore(roots[1]);
    const candidate=transform(control,roots);
    const started=process.hrtime.bigint();
    let nativeAction='ACCEPT';
    let errorClass=null;
    let errorMessage=null;
    try{
      store.updateRoot(candidate);
    }catch(err){
      nativeAction='REJECT';
      errorClass=err && err.constructor ? err.constructor.name : typeof err;
      errorMessage=err && err.message ? err.message : String(err);
    }
    const ended=process.hrtime.bigint();
    const match=
      nativeAction===control.expected_action &&
      errorClass===control.expected_error_class;
    if(!match) failures++;
    rows.push({
      ...control,
      native_action:nativeAction,
      error_class:errorClass,
      error_message:errorMessage,
      match,
      decision_ns:Number(ended-started),
      candidate_sha256:sha256(candidate),
      initial_anchor_sha256:sha256(roots[1]),
    });
  }
  const payload={
    schema:'eeq-bottlerocket-tuf-negative-controls-native-v1',
    native_library:'tuf-js@3.0.1',
    evidence_class:'CONTROLLED_NATIVE',
    rows,
    summary:{
      controls:rows.length,
      matched:rows.filter(r=>r.match).length,
      mismatches:failures,
      native_action_counts:{
        ACCEPT:rows.filter(r=>r.native_action==='ACCEPT').length,
        REJECT:rows.filter(r=>r.native_action==='REJECT').length,
      },
      g5_count_effect:0,
      fifth_family_holdout:'UNOPENED',
    },
  };
  fs.writeFileSync(outPath,JSON.stringify(payload,null,2)+'\n');
  console.log(JSON.stringify(payload.summary));
  for(const r of rows){
    console.log([r.id,r.native_action,r.error_class,r.match?'PASS':'MISMATCH'].join('\t'));
  }
  if(failures) process.exit(2);
}
main();
