#!/usr/bin/env node
'use strict';

/** Independent native TUF oracle for the frozen R2-B CONTROLLED development
 * experiment. This script does NOT import the source predictor or generator
 * and it does NOT read R2-B_PRE_NATIVE_PREDICTIONS.json.
 */
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {TrustedMetadataStore}=require('tuf-js/dist/store');
const {Metadata,MetadataKind}=require('@tufjs/models');
const {canonicalize}=require('@tufjs/canonical-json');

const NAMES={
 A:'anchor_a.root.json',B:'anchor_b.root.json',
 C2:'candidate_2.root.json',C3:'candidate_3.root.json',
 TARGETS_A:'targets_a.targets.json',TARGETS_B:'targets_b.targets.json'
};
const ACTIONS=['submit-candidate-2','submit-candidate-3'];
const ACTION_CANDIDATE={
 'submit-candidate-2':'C2','submit-candidate-3':'C3'
};
function hash(buf){return crypto.createHash('sha256').update(buf).digest('hex')}
function assert(x,msg){if(!x)throw Error(msg)}
function prefixes(){
  return [[],...ACTIONS.map(a=>[a]),
    ...ACTIONS.flatMap(a=>ACTIONS.map(b=>[a,b]))];
}
function state(store){
  const root=store.root.signed;
  return {
    version:root.version,
    root_keyids:[...root.roles.root.keyIDs].sort(),
    root_threshold:root.roles.root.threshold,
    targets_keyids:[...root.roles.targets.keyIDs].sort(),
    targets_threshold:root.roles.targets.threshold,
    canonical_signed_sha256:hash(Buffer.from(canonicalize(root.toJSON()))),
  };
}
function attempt(store,candidate){
  const before=state(store);
  const start=process.hrtime.bigint();
  let outcome='ACCEPT',error=null;
  try{store.updateRoot(candidate)}
  catch(e){
    const errorClass=e?.constructor?.name || typeof e;
    const expectedFailure=['BadVersionError','UnsignedMetadataError'];
    outcome=expectedFailure.includes(errorClass)?'REJECT':'NATIVE_ERROR';
    error={class:errorClass,message:e?.message||String(e)};
  }
  const decisionNs=Number(process.hrtime.bigint()-start);
  return {native_outcome:outcome,
    before,after:state(store),error,decision_ns:decisionNs};
}
function loadSources(dir){
  const manifest=JSON.parse(fs.readFileSync(path.join(dir,'SOURCE_MANIFEST.json'),'utf8'));
  assert(manifest.schema==='eeq-r2b-controlled-sources-v1','BAD_SOURCE_MANIFEST');
  const byFilename=new Map(manifest.files.map(x=>[x.name,x]));
  assert(byFilename.size===6,'WRONG_SOURCE_MANIFEST_SIZE');
  const sources={};
  for(const [key,filename] of Object.entries(NAMES)){
    const raw=fs.readFileSync(path.join(dir,filename));
    const pin=byFilename.get(filename);
    assert(pin && hash(raw)===pin.sha256 && raw.length===pin.bytes,
      'SOURCE_HASH_OR_SIZE_DRIFT_'+filename);
    sources[key]=raw;
  }
  return sources;
}
function fresh(sources,initial){
  return new TrustedMetadataStore(sources[initial]);
}
function runOnePrefix(sources,initial,prefix){
  let store,setupError=null;
  try{store=fresh(sources,initial)}
  catch(e){setupError={class:e?.constructor?.name||typeof e,
     message:e?.message||String(e)}}
  const trace=[];
  if(!setupError){
    for(const action of prefix){
      const r=attempt(store,sources[ACTION_CANDIDATE[action]]);
      trace.push({action,...r});
      if(r.native_outcome==='NATIVE_ERROR')break;
    }
  }
  return {
    initial_state:initial,prefix,prefix_trace:trace,
    setup_error:setupError,
    post_prefix_state:store?state(store):null,
    prefix_completed:!setupError && trace.length===prefix.length &&
      !trace.some(x=>x.native_outcome==='NATIVE_ERROR')
  };
}
function run(dir){
  const sources=loadSources(dir);
  const rows=[];
  for(const initial of ['A','B']){
    for(const prefix of prefixes()){
      const p=runOnePrefix(sources,initial,prefix);
      const challenges=[];
      for(const action of ACTIONS){
        // Recreate an isolated native store for each challenge, ensuring
        // no reuse of a mutated store across sibling future paths.
        const freshPrefix=runOnePrefix(sources,initial,prefix);
        let decision=null;
        if(freshPrefix.prefix_completed){
          const store=fresh(sources,initial);
          for(const pa of prefix)attempt(store,sources[ACTION_CANDIDATE[pa]]);
          decision=attempt(store,sources[ACTION_CANDIDATE[action]]);
        }
        challenges.push({
          action,
          from_state_after_prefix:freshPrefix.post_prefix_state,
          replay_setup_ok:freshPrefix.prefix_completed,
          native_decision:decision
        });
      }
      rows.push({...p,challenges});
    }
  }
  const targetAuthorizations=[];
  for(const initial of ['A','B']){
    for(const targetId of ['TARGETS_A','TARGETS_B']){
      let status='QUALIFIED',error=null;
      try{
        const store=fresh(sources,initial);
        const metadata=Metadata.fromJSON(MetadataKind.Targets,
          JSON.parse(sources[targetId].toString('utf8')));
        store.root.verifyDelegate(MetadataKind.Targets,metadata);
      }catch(e){
        const cls=e?.constructor?.name||typeof e;
        status=cls==='UnsignedMetadataError'?'UNQUALIFIED':'NATIVE_ERROR';
        error={class:cls,message:e?.message||String(e)};
      }
      targetAuthorizations.push({
        initial_state:initial,target_document:targetId,
        native_role_authority_status:status,error
      });
    }
  }
  const outcomes={},qualifications={};
  for(const row of rows)for(const ch of row.challenges){
    const status=ch.native_decision?.native_outcome || 'SETUP_FAILURE';
    outcomes[status]=(outcomes[status]||0)+1;
  }
  for(const row of targetAuthorizations)
    qualifications[row.native_role_authority_status]=
      (qualifications[row.native_role_authority_status]||0)+1;
  return {
    schema:'eeq-r2b-independent-native-tuf-v1',
    evidence_class:'CONTROLLED_NATIVE_DEVELOPMENT',
    native_library:'tuf-js@3.0.1',
    native_operation:'TrustedMetadataStore.updateRoot',
    native_targets_check:'Metadata.verifyDelegate(targets) ONLY, not full updater',
    fixed_actions:ACTIONS,
    fixed_horizon:2,
    rows,target_authorizations:targetAuthorizations,
    summary:{prefix_rows:rows.length,challenge_cells:28,
      target_authority_cells:4,
      update_outcomes:outcomes,target_role_outcomes:qualifications},
    source_only_predictions_never_read:true,
    old_g4_v1_unchanged:true,
    new_g5_cases:0,
    R2_A_witness_not_sought:true,
    scientific_claim:'CONTROLLED_B_EQUIVALENCE_NATIVE_DIAGNOSTIC_ONLY'
  };
}
if(require.main===module){
  if(process.argv.length!==4)
    throw Error('usage: node r2b_native_tuf.js FROZEN_SOURCE_DIR OUT_JSON');
  const result=run(process.argv[2]);
  fs.writeFileSync(process.argv[3],JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result.summary));
}
module.exports={run,prefixes,state,attempt};
