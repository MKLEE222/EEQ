#!/usr/bin/env node
'use strict';
/* E2 TUF subset: compile native source bytes (NOT old prediction labels)
 * into generic role threshold IR. Ed25519 checked with previously pinned
 * source helper. No tuf-js native execution. Hand-coded domain adapter.
 */
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {sourceFixtures,asRoot,authorityCertificate}=
  require('../r4/r4_d0_tuf_sources.js');
const {canon,verifySignature,verifyRole}=
  require('../tuf_trust_transition_extractor_r1b_v3.js');

const SCHEMA='eeq-r4-e2-native-source-qualified-rule-ir-v1';
const STATES=[['s2a','root-2-a.json'],['s2b','root-2-b.json']];
const CANDIDATES=[
  ['root-3-a','root-3-a.json'],
  ['root-3-b','root-3-b.json'],
  ['root-3-old-only','root-3-old-only.json'],
  ['root-3-new-only','root-3-new-only.json']
];

function assert(ok,why){if(!ok)throw Error('E2_TUF_'+why);}
function hash(x){return crypto.createHash('sha256').update(x).digest('hex');}
function verifyOriginalSourceIdentity(record){
 assert(record&&Buffer.isBuffer(record.raw)&&record.obj &&
        hash(record.raw)===record.sha256,
        'SOURCE_RAW_SHA_DOES_NOT_MATCH_OBJECT_ENVELOPE');
 assert(JSON.stringify(JSON.parse(record.raw.toString('utf8')))===
        JSON.stringify(record.obj),
        'SOURCE_OBJECT_NOT_EQUAL_ITS_HASHED_RAW_BYTES');
}
function leaf(id,value,refs,obligation){
 return {op:'ATOM',id,value,source_refs:refs,obligation};
}
function validatedRole(trustedObj,candidateObj,kind){
 const role=trustedObj.signed.roles.root;
 assert(role&&Array.isArray(role.keyids) && role.keyids.length>0,
        'MISSING_REGISTERED_ROOT_ROLE');
 assert(new Set(role.keyids).size===role.keyids.length,
        'DUPLICATE_AUTHORIZED_KEYID');
 assert(Number.isInteger(role.threshold)&&role.threshold>0&&
        role.threshold<=role.keyids.length,'INVALID_ROLE_THRESHOLD');
 const sigs=candidateObj.signatures;
 assert(Array.isArray(sigs)&&new Set(sigs.map(x=>x.keyid)).size===sigs.length,
        'DUPLICATE_CANDIDATE_SIGNATURE_KEYID');
 const signed=Buffer.from(canon(candidateObj.signed),'utf8');
 const atoms=role.keyids.map(kid=>{
  const key=trustedObj.signed.keys[kid];
  assert(key&&typeof key==='object','AUTHORIZED_KEY_MATERIAL_MISSING');
  const sig=sigs.find(x=>x.keyid===kid);
  const good=Boolean(sig&&typeof sig.sig==='string'&&
        verifySignature(key,signed,sig.sig).status==='VERIFIED');
  return leaf(kind+':'+kid,good,
    kind==='OLD_ROOT' ? ['trusted_root','candidate_root'] : ['candidate_root'],
    kind+'_REGISTERED_ROLE_UNIQUE_ED25519_SIGNATURE');
 });
 return {op:'THRESHOLD',k:role.threshold,children:atoms};
}
function compileCase(anchorRecord,trustedRecord,candidateRecord,id){
 for(const record of [anchorRecord,trustedRecord,candidateRecord])
  verifyOriginalSourceIdentity(record);
 const anchor=asRoot(anchorRecord),trusted=asRoot(trustedRecord),
       cand=asRoot(candidateRecord);
 const initialOld=verifyRole(anchor,trusted);
 const initialNew=verifyRole(trusted,trusted);
 assert(initialOld.status==='SUFFICIENT'&&initialNew.status==='SUFFICIENT',
        'INITIAL_ROOT2_HISTORY_NOT_VERIFIED');
 assert(anchor.version===1&&trusted.version===2&&
        candidateRecord.obj.signed._type==='root',
        'UNREGISTERED_ROOT2_TO_ROOT3_GRAMMAR');
 assert(candidateRecord.obj.signed.spec_version==='1.0.31'&&
        trustedRecord.obj.signed.spec_version==='1.0.31',
        'UNREGISTERED_TUF_SPEC_VERSION');
 // Role authority in the OLD root and NEW root are read from exact
 // original JSON, never hard-coded by particular signer label.
 const program={
   schema:SCHEMA,case_id:id,domain:'TUF_ROOT_UPDATE',
   registered_contract:'E2_TUF_ROOT_UPDATE_OLD_NEW_ROLE_V1',
   verified_source_sha256:{
     anchor_root:anchorRecord.sha256,
     trusted_root:trustedRecord.sha256,
     candidate_root:candidateRecord.sha256
   },
   source_closure_is_author_independently_attested:false,
   native_labels_read:false,
   evidence_class:'PREVIOUS_NATIVE_DEVELOPMENT_SOURCE_BYTES_NEW_COMPILER',
   setup:{
     trusted_root_source:trustedRecord.name,
     candidate_source:candidateRecord.name,
     initial_history_source_only_verified:true,
     no_native_tuf_js_called:true
   },
   formula:{op:'AND',children:[
     leaf('VERSION_CONTIGUOUS',
       candidateRecord.obj.signed.version===trustedRecord.obj.signed.version+1,
       ['trusted_root','candidate_root'],
       'TUF_ROOT_VERSION_SUCCESSION_FROM_SOURCE_BYTES'),
     validatedRole(trustedRecord.obj,candidateRecord.obj,'OLD_ROOT'),
     validatedRole(candidateRecord.obj,candidateRecord.obj,'NEW_ROOT')
   ]}
 };
 return program;
}
function build(){
 const {sources}=sourceFixtures();
 const m=new Map(sources.map(x=>[x.name,x]));
 assert(sources.length===7&&m.size===7,'FROZEN_SEVEN_SOURCE_SET_CHANGED');
 const rows=[],reference=[];
 for(const [state,file] of STATES){
  const anchor=m.get('root-1-common.json'),old=m.get(file);
  for(const [action,cname] of CANDIDATES){
   const cand=m.get(cname);
   const caseid='TUF|'+state+'|'+action;
   rows.push(compileCase(anchor,old,cand,caseid));
   // Separate source-only fully informed B9 direct-rule comparator:
   // does NOT consume newly constructed generic IR or native labels.
   const b9=authorityCertificate(asRoot(old),asRoot(cand));
   assert(b9.effect!=='MODEL_UNSUPPORTED','B9_SOURCE_ROLE_UNSUPPORTED');
   reference.push({
     case_id:caseid,
     direct_B9_source_only_effect:b9.effect==='ADVANCE_TRUST_ROOT',
     original_native_outcome_read:false
   });
  }
 }
 assert(rows.length===8&&reference.length===8,'EIGHT_CASES_NOT_COMPLETE');
 return {rows,reference,sources:sources.map(s=>({name:s.name,sha256:s.sha256,
                        bytes:s.bytes}))};
}
function write(out){
 fs.mkdirSync(out,{recursive:true});
 const x=build();
 fs.writeFileSync(path.join(out,'E2_TUF_8_SOURCE_RULE_PROGRAMS.json'),
                  JSON.stringify(x.rows,null,2)+'\n');
 fs.writeFileSync(path.join(out,'E2_TUF_8_FULL_B9_SOURCE_REFERENCE.json'),
                  JSON.stringify(x.reference,null,2)+'\n');
 fs.writeFileSync(path.join(out,'E2_TUF_7_SOURCE_MANIFEST.json'),
                  JSON.stringify(x.sources,null,2)+'\n');
 console.log(JSON.stringify({programs:x.rows.length,
   source_only_b9_reference:x.reference.length,
   verified_source_envelopes:x.sources.length,
   native_calls:0,already_scored_development_only:true}));
}
if(require.main===module){
 assert(process.argv.length===3,'USAGE');
 write(process.argv[2]);
}
module.exports={compileCase,build,validatedRole,write};
