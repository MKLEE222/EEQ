#!/usr/bin/env node
'use strict';
/* R2B STAGE-II NATIVE TUF ONLY. No imports from source predictor.
 * Independently loads pinned CONTROLLED source bytes and asks tuf-js@3.0.1
 * about source-to-source updates AND target-role delegations. Prediction
 * JSON is never read here. All actions and traces predeclared in R2B freeze.
 */
const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const {TrustedMetadataStore}=require('tuf-js/dist/store');
const {Metadata,MetadataKind}=require('@tufjs/models');
const {canonicalize}=require('@tufjs/canonical-json');
const SHA=v=>crypto.createHash('sha256').update(v).digest('hex');
const STATES=['s2a','s2b','s3a','s3b','s4a','s4b'];
const ACTIONS=['submit-root-3-a','submit-root-3-b','submit-root-4-a','submit-root-4-b'];
function check(ok,detail){if(!ok)throw Error(detail)}
function loadSources(directory){
  const manifest=JSON.parse(fs.readFileSync(
    path.join(directory,'SOURCE_MANIFEST.json'),'utf8'));
  check(manifest.schema==='eeq-r2b-source-manifest-v1','BAD_SOURCE_MANIFEST');
  check(manifest.sources.length===9,'EXPECTED_NINE_PINNED_SOURCES');
  const all=new Map();
  for(const row of manifest.sources){
    check(!all.has(row.name),'DUPLICATE_SOURCE_NAME');
    const raw=fs.readFileSync(path.join(directory,row.name));
    check(raw.length===row.bytes&&SHA(raw)===row.sha256,
      'SOURCE_PIN_MISMATCH_'+row.name);
    const obj=JSON.parse(raw.toString('utf8'));
    all.set(row.name,{name:row.name,raw,obj,sha256:row.sha256,
      signedHash:SHA(Buffer.from(canonicalize(obj.signed),'utf8'))});
  }
  for(const n of ['root-1-common.json',
    'root-2-a.json','root-2-b.json','root-3-a.json','root-3-b.json',
    'root-4-a.json','root-4-b.json','targets-a.json','targets-b.json'])
    check(all.has(n),'SOURCE_MISSING_'+n);
  return {all,manifest};
}
function stateSourceName(s){
  check(STATES.includes(s),'UNREGISTERED_STATE_'+s);
  return 'root-'+s[1]+'-'+s[2]+'.json';
}
function actionSourceName(a){
  const m=/^submit-root-([34])-([ab])$/.exec(a);
  check(!!m&&ACTIONS.includes(a),'UNREGISTERED_ACTION_'+a);
  return 'root-'+m[1]+'-'+m[2]+'.json';
}
function nativeSignedHash(store){
  return SHA(Buffer.from(canonicalize(store.root.signed.toJSON()),'utf8'));
}
function nativeStateId(store,sources){
  const h=nativeSignedHash(store);
  for(const s of STATES)if(sources.all.get(stateSourceName(s)).signedHash===h)
    return s;
  return null;
}
function prepareState(s,sources){
  const variant=s[2],version=Number(s[1]);
  const anchor=sources.all.get('root-1-common.json');
  const store=new TrustedMetadataStore(anchor.raw);
  const setup=['root-1-common.json'];
  for(let n=2;n<=version;n++){
    const name='root-'+n+'-'+variant+'.json';
    const candidate=sources.all.get(name);
    check(!!candidate,'MISSING_SETUP_SOURCE_'+name);
    store.updateRoot(candidate.raw);
    setup.push(name);
  }
  const got=nativeStateId(store,sources);
  check(got===s,'INVALID_NATIVE_SETUP_FOR_'+s+'_GOT_'+got);
  return {store,setup};
}
function exceptionOf(error){
  return {class:error?.constructor?.name||typeof error,
    message:error?.message||String(error)};
}
function attempt(store,action,sources){
  const candidate=sources.all.get(actionSourceName(action));
  const beforeVersion=store.root.signed.version;
  const beforeState=nativeStateId(store,sources);
  let effect='REJECT',error=null;
  const start=process.hrtime.bigint();
  try{
    store.updateRoot(candidate.raw);
    effect='ACCEPT';
  }catch(e){error=exceptionOf(e);}
  const elapsed=Number(process.hrtime.bigint()-start);
  return {effect,action,
    native_before_state:beforeState,
    native_after_state:nativeStateId(store,sources),
    native_before_version:beforeVersion,
    native_after_version:store.root.signed.version,
    native_after_signed_sha256:nativeSignedHash(store),
    candidate_sha256:candidate.sha256,
    decision_ns:elapsed,error};
}
function words(){
  const out=[[]];
  for(const a of ACTIONS)out.push([a]);
  for(const a of ACTIONS)for(const b of ACTIONS)out.push([a,b]);
  check(out.length===21,'NOT_EXACT_21_WORDS');
  return out;
}
function nativeRun(sources){
  const oneStep=[];
  const traces=[];
  const targetControls=[];
  const registeredWords=words();
  for(const startState of STATES){
    for(const action of ACTIONS){
      let result;
      try{
        const {store,setup}=prepareState(startState,sources);
        result={from_state:startState,setup,action,
          ...attempt(store,action,sources),
          initial_source_sha256:sources.all.get(stateSourceName(startState)).sha256};
      }catch(e){
        result={from_state:startState,action,native_effect:'SETUP_FAILURE',
          setup_error:exceptionOf(e),native_after_state:null};
      }
      oneStep.push(result);
    }
    for(const word of registeredWords){
      let result;
      try{
        const {store,setup}=prepareState(startState,sources);
        const events=[];
        for(const a of word)events.push(attempt(store,a,sources));
        result={from_state:startState,setup,word,events,
          terminal_native_state:nativeStateId(store,sources),
          setup_error:null};
      }catch(e){
        result={from_state:startState,word,events:[],
          terminal_native_state:null,setup_error:exceptionOf(e)};
      }
      traces.push(result);
    }
    for(const variant of ['a','b']){
      const target=sources.all.get('targets-'+variant+'.json');
      let result;
      try{
        const {store}=prepareState(startState,sources);
        const md=Metadata.fromJSON(MetadataKind.Targets,target.obj);
        let qualification='QUALIFIED',error=null;
        try{
          store.root.verifyDelegate(MetadataKind.Targets,md);
        }catch(e){
          error=exceptionOf(e);
          qualification=error.class==='UnsignedMetadataError'?
            'UNQUALIFIED':'ERROR';
        }
        result={from_state:startState,target_source_name:target.name,
          target_source_sha256:target.sha256,
          native_qualification:qualification,error,setup_error:null};
      }catch(e){
        result={from_state:startState,target_source_name:target.name,
          native_qualification:'SETUP_FAILURE',setup_error:exceptionOf(e)};
      }
      targetControls.push(result);
    }
  }
  check(oneStep.length===24&&traces.length===126&&targetControls.length===12,
    'NATIVE_REGISTERED_DENOMINATOR_MISMATCH');
  const tally=xs=>xs.reduce((r,x)=>(r[x]=(r[x]||0)+1,r),{});
  const sourceDigests=Object.fromEntries([...sources.all].map(([name,obj])=>
    [name,obj.sha256]));
  return {
    schema:'eeq-r2b-native-tuf-controlled-grid-v1',
    evidence_class:'CONTROLLED_NATIVE_DEVELOPMENT',
    native_oracle:'tuf-js@3.0.1 TrustedMetadataStore.updateRoot and Metadata.verifyDelegate',
    predictions_json_read:false,
    original_g5_increment:0,
    registered_states:STATES,
    registered_actions:ACTIONS,
    registered_horizon:2,
    source_digests:sourceDigests,
    one_step:oneStep,action_traces:traces,target_controls:targetControls,
    summary:{
      one_step:oneStep.length,traces:traces.length,targets:targetControls.length,
      effects:tally(oneStep.map(x=>x.effect||x.native_effect)),
      target_outcomes:tally(targetControls.map(x=>x.native_qualification)),
      native_setup_failures:oneStep.filter(x=>x.setup_error).length+
        traces.filter(x=>x.setup_error).length+
        targetControls.filter(x=>x.setup_error).length,
    },
  };
}
if(require.main===module){
  if(process.argv.length!==4)throw Error('usage: r2b_native_tuf_oracle.js SOURCES_DIR OUT_JSON');
  const result=nativeRun(loadSources(process.argv[2]));
  fs.writeFileSync(process.argv[3],JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result.summary));
}
module.exports={loadSources,nativeRun,stateSourceName,actionSourceName,words};
