#!/usr/bin/env node
'use strict';
/**
 * R2-B source-only prediction compiler.
 * Reads ONLY signed fixture bytes generated under the frozen R2-B source
 * contract. No tuf-js, no native decisions, no old labels.
 */
const fs=require('fs'), path=require('path');
const crypto=require('crypto');
const {canon,edge,verifySignature}=require('../tuf_trust_transition_extractor_r1b_v3.js');
const {sha}=require('./r2b_controlled_source_generator.js');

const ANCHORS=['A','B'], ACTIONS=['submit-candidate-2','submit-candidate-3'];
const CANDIDATE={ 'submit-candidate-2':'C2', 'submit-candidate-3':'C3' };
const FILES={
 A:'anchor_a.root.json',B:'anchor_b.root.json',
 C2:'candidate_2.root.json',C3:'candidate_3.root.json',
 TARGETS_A:'targets_a.targets.json',TARGETS_B:'targets_b.targets.json'
};
function check(c,s){if(!c)throw Error(s);}
function readSources(dir){
  const source={};
  for(const [id,name] of Object.entries(FILES)){
    const raw=fs.readFileSync(path.join(dir,name));
    const obj=JSON.parse(raw.toString('utf8'));
    const bytes=Buffer.from(canon(obj.signed),'utf8');
    source[id]={
      id,name,sha256:sha(raw),obj,
      version:obj.signed.version,signedBytes:bytes,
      hash:sha(raw),signedHash:sha(bytes)
    };
    check(Array.isArray(obj.signatures),'NO_SIGNATURES_'+id);
  }
  check(source.A.version===1&&source.B.version===1&&
    source.C2.version===2&&source.C3.version===3,'WRONG_ROOT_VERSIONS');
  return source;
}
function qualifyRootSelf(root){
  const role=root.obj.signed.roles.root;
  const signatures=new Map(root.obj.signatures.map(s=>[s.keyid,s.sig]));
  const valid=new Set();
  for(const id of role.keyids){
    const pub=root.obj.signed.keys[id];
    const sig=signatures.get(id);
    if(sig && verifySignature(pub,root.signedBytes,sig).status==='VERIFIED')
      valid.add(id);
  }
  return {status:valid.size>=role.threshold,
    verified_signers:[...valid].sort(),threshold:role.threshold};
}
function qualifyTargets(anchor,target){
  const role=anchor.obj.signed.roles.targets;
  const signatures=new Map(target.obj.signatures.map(s=>[s.keyid,s.sig]));
  const valid=new Set();
  for(const id of role.keyids){
    const pub=anchor.obj.signed.keys[id];
    const sig=signatures.get(id);
    if(sig&&verifySignature(pub,target.signedBytes,sig).status==='VERIFIED')
      valid.add(id);
  }
  return {qualified:valid.size>=role.threshold,
    verified_unique_signer_keyids:[...valid].sort(),
    required_signers:role.threshold};
}
function pathsUpTo2(){
  return [[],...ACTIONS.map(a=>[a]),
    ...ACTIONS.flatMap(a=>ACTIONS.map(b=>[a,b]))];
}
function step(current,action,sources){
  const candidate=sources[CANDIDATE[action]];
  const x=edge(current,candidate);
  check(x.derived_effect!=='MODEL_UNSUPPORTED','UNKNOWN_SOURCE_CRYPTO');
  return {effect:x.derived_effect,next:
    x.derived_effect==='ADVANCE_TRUST_ROOT'?candidate:current,
    certificate:{
      old_qualified_ids:x.old_authority.verified_unique_keyids,
      old_threshold:x.old_authority.threshold,
      new_qualified_ids:x.new_authority.verified_unique_keyids,
      new_threshold:x.new_authority.threshold,
      version_contiguous:x.version_contiguous,
      next_source_sha256: x.derived_effect==='ADVANCE_TRUST_ROOT' ?
        candidate.sha256:current.sha256
    }};
}
function derive(dir){
  const source=readSources(dir);
  const checks=Object.fromEntries(['A','B','C2','C3'].map(id=>
    [id,qualifyRootSelf(source[id])]));
  check(Object.values(checks).every(x=>x.status),'ROOT_SELF_SIGNING_INVALID');
  const ra=source.A.obj.signed,rb=source.B.obj.signed;
  const equalRootRole=JSON.stringify(ra.roles.root)===JSON.stringify(rb.roles.root);
  const differentTargetsRole=JSON.stringify(ra.roles.targets)!==
    JSON.stringify(rb.roles.targets);
  check(equalRootRole&&differentTargetsRole,'AUTHORITY_CONTRAST_NOT_SATISFIED');
  const targetQualification={
    A:{
      TARGETS_A:qualifyTargets(source.A,source.TARGETS_A),
      TARGETS_B:qualifyTargets(source.A,source.TARGETS_B)
    },
    B:{
      TARGETS_A:qualifyTargets(source.B,source.TARGETS_A),
      TARGETS_B:qualifyTargets(source.B,source.TARGETS_B)
    }
  };
  check(targetQualification.A.TARGETS_A.qualified&&
    !targetQualification.A.TARGETS_B.qualified&&
    !targetQualification.B.TARGETS_A.qualified&&
    targetQualification.B.TARGETS_B.qualified,
  'NONCOSMETIC_TARGETS_QUALIFICATION_CONTRAST_FAILED');
  const rows=[];
  for(const initial of ANCHORS){
    for(const prefix of pathsUpTo2()){
      let current=source[initial],attempts=[];
      for(const action of prefix){
        const outcome=step(current,action,source);
        attempts.push({
          action,source_state_before_sha256:current.sha256,
          effect:outcome.effect,source_state_after_sha256:outcome.next.sha256
        });
        current=outcome.next;
      }
      const observation=ACTIONS.map(action=>{
        const outcome=step(current,action,source);
        return {action,effect:outcome.effect,
          to_source_sha256:outcome.next.sha256,
          source_qualification_certificate:outcome.certificate};
      });
      rows.push({
        initial_state:initial,
        prefix,
        prefix_effects:attempts,
        state_after_prefix_source_sha256:current.sha256,
        state_after_prefix_version:current.version,
        continuation:observation
      });
    }
  }
  const byInitial=initial=>rows.filter(r=>r.initial_state===initial);
  const a=byInitial('A'),b=byInitial('B');
  check(a.length===7&&b.length===7,'WRONG_EXHAUSTIVE_PREFIX_COUNT');
  const equivalent=a.every((row,i)=>row.prefix.join(',')===b[i].prefix.join(',')
    &&row.continuation.every((e,j)=>e.effect===b[i].continuation[j].effect));
  check(equivalent,'CONTROLLED_ROOT_ONLY_SOURCE_EQUIVALENCE_BROKEN');
  const b9key=r=>{
    const s=r.obj.signed;
    return JSON.stringify([s.version,s.roles.root.threshold,
      [...s.roles.root.keyids].sort()]);
  };
  const b9Equivalent=b9key(source.A)===b9key(source.B);
  check(b9Equivalent,'STRONG_B9_EXPECTED_TIE_BROKEN');
  return {
    schema:'eeq-r2b-source-only-predictions-v1',
    evidence_class:'CONTROLLED_SIGNED_SOURCE_ONLY_DEVELOPMENT',
    registered_initial_states:ANCHORS,
    registered_actions:ACTIONS,
    horizon:2,
    prefixes_per_state:7,
    expected_comparison_count:14,
    native_scored_rows:0,
    no_native_import:true,
    no_previous_native_outcomes_read:true,
    source_files:Object.fromEntries(Object.entries(source).map(([k,v])=>[
      k,{name:v.name,sha256:v.sha256,version:v.version}
    ])),
    root_self_qualification:checks,
    targets_role_qualification:targetQualification,
    root_only_current_and_future_equivalent:equivalent,
    equal_root_role:equalRootRole,
    different_targets_role:differentTargetsRole,
    strong_b9_initial_equivalence:b9Equivalent,
    classical_moore_quotient_initial_equivalence:equivalent,
    no_novelty_advantage_over_strong_b9_claimed:true,
    rows
  };
}
if(require.main===module){
  if(process.argv.length!==4)
    throw Error('usage: node r2b_source_predict.js SOURCE_DIR OUTPUT_JSON');
  const report=derive(process.argv[2]);
  fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({
    source_rows:report.rows.length,
    root_only_equivalent:report.root_only_current_and_future_equivalent,
    targets_authority_diff:report.different_targets_role,
    strong_b9_tie:report.strong_b9_initial_equivalence,
    native_scored:report.native_scored_rows
  }));
}
module.exports={derive,pathsUpTo2,step,readSources,qualifyTargets,qualifyRootSelf};
