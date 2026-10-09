#!/usr/bin/env node
'use strict';
/* R4-D0 native TUF updateRoot experiment.
 * NO imported source-only predictor and NO SOURCE_PREDICTIONS read.
 * Fresh independently initialized native store for EVERY state-action cell.
 * Post-state identity uses both signed root bytes AND signature envelopes:
 * the candidate root3 signed bodies are intentionally IDENTICAL.
 */
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {TrustedMetadataStore}=require('tuf-js/dist/store');
const {canonicalize}=require('@tufjs/canonical-json');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const STATES=[
 {id:'s2a',setup:'root-2-a.json'},
 {id:'s2b',setup:'root-2-b.json'}
];
const ACTIONS=[
 {id:'submit-root-3-a',file:'root-3-a.json'},
 {id:'submit-root-3-b',file:'root-3-b.json'},
 {id:'submit-root-3-old-only',file:'root-3-old-only.json'},
 {id:'submit-root-3-new-only',file:'root-3-new-only.json'}
];
function check(ok,error){if(!ok)throw Error(error)}
function source(dir){
  const m=JSON.parse(fs.readFileSync(path.join(dir,'SOURCE_MANIFEST.json'),'utf8'));
  check(m.schema==='eeq-r4-d0-source-manifest-v1'&&m.sources.length===7,
    'BAD_REGISTERED_SOURCE_MANIFEST');
  const docs=new Map();
  for(const rec of m.sources){
    const raw=fs.readFileSync(path.join(dir,rec.name));
    check(sha(raw)===rec.sha256&&raw.length===rec.bytes,
      'PINNED_SOURCE_SHA_LENGTH_MISMATCH_'+rec.name);
    const parsed=JSON.parse(raw.toString('utf8'));
    docs.set(rec.name,{name:rec.name,raw,obj:parsed,sha:rec.sha256});
  }
  check(docs.size===7&&docs.has('root-1-common.json'),
    'SOURCE_MANIFEST_MISSING_ROOT');
  for(const s of STATES)check(docs.has(s.setup),'SETUP_SOURCE_MISSING');
  for(const a of ACTIONS)check(docs.has(a.file),'ACTION_SOURCE_MISSING');
  return {manifest:m,docs};
}
function envelopeFingerprint(obj){
  const signed=Buffer.from(canonicalize(obj.signed),'utf8');
  const signatures=[...obj.signatures].map(s=>({keyid:s.keyid,sig:s.sig}))
    .sort((a,b)=>a.keyid.localeCompare(b.keyid));
  const signatureBytes=Buffer.from(canonicalize(signatures),'utf8');
  return {
    signed_sha256:sha(signed),
    signature_set_sha256:sha(signatureBytes),
    // This identity is NOT a raw source-file byte hash.
    trusted_metadata_identity:sha(Buffer.concat([
      Buffer.from(sha(signed),'hex'),Buffer.from(sha(signatureBytes),'hex')
    ])),
    signature_count:signatures.length,
  };
}
function nativeFingerprint(store){return envelopeFingerprint(store.root.toJSON())}
function findSourceNative(root,inputs){
  const id=nativeFingerprint(root).trusted_metadata_identity;
  const matches=[...inputs.docs.values()].filter(x=>
    envelopeFingerprint(x.obj).trusted_metadata_identity===id);
  check(matches.length===1,'NATIVE_METADATA_IDENTITY_NOT_UNIQUE_OR_UNKNOWN_'+id);
  return matches[0].name;
}
function errorObject(e){
  return {class:e?.constructor?.name||typeof e,message:e?.message||String(e)};
}
function setupOne(branch,inputs){
  const anchor=inputs.docs.get('root-1-common.json');
  const trial=new TrustedMetadataStore(anchor.raw);
  const setup=inputs.docs.get(branch.setup);
  trial.updateRoot(setup.raw);
  const resulting=findSourceNative(trial,inputs);
  check(resulting===branch.setup,
    'NATIVE_ANCHOR_SETUP_IDENTITY_MISMATCH_'+branch.id);
  return {trial,setup_native_state:resulting,
    setup_result_sha256:setup.sha,
    setup_native_fingerprint:nativeFingerprint(trial)};
}
function run(dir){
  const inputs=source(dir),rows=[],setups=[];
  for(const s of STATES){
    let checkSetup;
    try{
      const result=setupOne(s,inputs);
      checkSetup={state:s.id,result:'PASS',
        native_source_name:result.setup_native_state,
        native_metadata_identity:result.setup_native_fingerprint.trusted_metadata_identity,
        setup_source_sha256:result.setup_result_sha256,
        native_version:result.trial.root.signed.version};
    }catch(e){checkSetup={state:s.id,result:'FAIL',error:errorObject(e)};}
    setups.push(checkSetup);
    for(const a of ACTIONS){
      let entry={state:s.id,action:a.id,
        state_setup_source:s.setup,
        candidate_source:a.file,
        state_source_sha256:inputs.docs.get(s.setup).sha,
        candidate_source_sha256:inputs.docs.get(a.file).sha,
        native_outcome:'SETUP_FAILURE',
        initial_native_source:null,post_native_source:null,
        initial_metadata_identity:null,post_metadata_identity:null,
        setup_error:null,candidate_error:null,elapsed_ns:null,
      };
      try{
        const {trial}=setupOne(s,inputs);
        entry.initial_native_source=findSourceNative(trial,inputs);
        entry.initial_native_version=trial.root.signed.version;
        entry.initial_metadata_identity=nativeFingerprint(trial)
          .trusted_metadata_identity;
        const candidate=inputs.docs.get(a.file);
        const start=process.hrtime.bigint();
        try{
          trial.updateRoot(candidate.raw);
          entry.native_outcome='ACCEPT';
        }catch(e){
          entry.native_outcome='REJECT';
          entry.candidate_error=errorObject(e);
        }
        entry.elapsed_ns=Number(process.hrtime.bigint()-start);
        entry.post_native_source=findSourceNative(trial,inputs);
        entry.post_native_version=trial.root.signed.version;
        entry.post_metadata_identity=nativeFingerprint(trial)
          .trusted_metadata_identity;
      }catch(e){
        entry.setup_error=errorObject(e);
      }
      rows.push(entry);
    }
  }
  check(rows.length===8&&setups.length===2,'NATIVE_D0_GRID_INCOMPLETE');
  const count={};
  for(const r of rows)count[r.native_outcome]=(count[r.native_outcome]||0)+1;
  return {
    schema:'eeq-r4-d0-tuf-native-auth-contrast-v1',
    evidence_class:'CONTROLLED_TUF_NATIVE_DEVELOPMENT',
    native_verifier:'tuf-js@3.0.1 TrustedMetadataStore.updateRoot',
    source_predictions_read:false,
    states:STATES.map(x=>x.id),actions:ACTIONS.map(x=>x.id),
    registered_cells:8,setup_controls:setups,native_rows:rows,
    summary:{effects:count,setup_controls:setups.length},
    original_g5_increment:0,
  };
}
if(require.main===module){
  check(process.argv.length===4,
    'usage: r4_d0_tuf_native.js FROZEN_SOURCES_DIR NATIVE_RAW_OUT.json');
  const output=run(process.argv[2]);
  fs.writeFileSync(process.argv[3],JSON.stringify(output,null,2)+'\n');
  console.log(JSON.stringify(output.summary));
}
module.exports={source,envelopeFingerprint,run};
