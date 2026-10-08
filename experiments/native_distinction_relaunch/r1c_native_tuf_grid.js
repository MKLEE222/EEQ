#!/usr/bin/env node
'use strict';
// R1c native comparator ONLY. MUST run only after predictions artifact freeze.
// Does NOT import any source-derived extractor or read a predicted effect.
const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const {TrustedMetadataStore}=require('tuf-js/dist/store');
function hash(bytes){return crypto.createHash('sha256').update(bytes).digest('hex')}
function rootBytes(dir,n){return fs.readFileSync(path.join(dir,n+'.root.json'))}
function nativeGrid(dir){
 const roots=new Map();
 for(let n=1;n<=8;n++)roots.set(n,rootBytes(dir,n));
 const rows=[];
 for(let n=1;n<=8;n++){
  for(let m=2;m<=8;m++){
   const before=roots.get(n),candidate=roots.get(m);
   let store,setup_error=null,candidate_error=null;
   const prefix=[];
   try{
    store=new TrustedMetadataStore(roots.get(1));
    for(let p=2;p<=n;p++){
     store.updateRoot(roots.get(p));
     prefix.push(p);
    }
   }catch(error){
    setup_error={class:error?.constructor?.name||typeof error,
      message:error?.message||String(error)};
   }
   let action='SETUP_FAILURE',decision_ns=null;
   let beforeVersion=null,afterVersion=null;
   if(!setup_error){
    beforeVersion=store.root.signed.version;
    if(beforeVersion!==n){
      setup_error={class:'SETUP_STATE_MISMATCH',
        message:'native trusted root version != declared initial state'};
    }else{
      const start=process.hrtime.bigint();
      try{
       store.updateRoot(candidate);
       action='ACCEPT';
      }catch(error){
       action='REJECT';
       candidate_error={class:error?.constructor?.name||typeof error,
         message:error?.message||String(error)};
      }finally{
       decision_ns=Number(process.hrtime.bigint()-start);
       afterVersion=store.root.signed.version;
      }
    }
   }
   rows.push({
    from_state:'trusted-root-'+n,action:'submit-root-'+m,
    from_root_source_sha256:hash(before),
    candidate_source_sha256:hash(candidate),
    prefix_setup_versions:prefix,
    native_action:setup_error?'SETUP_FAILURE':action,
    before_native_version:beforeVersion,
    after_native_version:afterVersion,
    setup_error,candidate_error,decision_ns,
    known_prior_development_adjacent:(m===n+1),
   });
  }
 }
 const counts={};
 for(const r of rows)counts[r.native_action]=(counts[r.native_action]||0)+1;
 return {
  schema:'eeq-r1c-tuf-native-root-grid-v1',
  native_library:'tuf-js@3.0.1',
  operation:'TrustedMetadataStore.updateRoot',
  evidence_class:'CONTROLLED_NATIVE_DEVELOPMENT_REPLAY',
  registered_states:8,registered_actions:7,grid_rows:56,
  registered_actions_as_pinned_source_versions:[2,3,4,5,6,7,8],
  rows,summary:counts,
  previous_native_positive_observations_in_scoring:false,
  prediction_file_not_read:true,
  new_g5_cases:0,
 };
}
if(require.main===module){
 if(process.argv.length!==4)throw new Error('usage: node r1c_native.js ROOT_DIR OUT_JSON');
 const p=nativeGrid(process.argv[2]);
 fs.writeFileSync(process.argv[3],JSON.stringify(p,null,2)+'\n');
 console.log(JSON.stringify({rows:p.grid_rows,counts:p.summary}));
}
module.exports={nativeGrid};
