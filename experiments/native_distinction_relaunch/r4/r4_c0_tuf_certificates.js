#!/usr/bin/env node
'use strict';
/* R4-C0 TUF domain semantics adapter; post-native DEV integration.
 * Does NOT import R4-D0 source predictions/generator or call native TUF.
 * Cryptographically REVERIFIES old/new root roles from ORIGINAL signed bytes.
 */
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {canon,verifyRole}=require('../tuf_trust_transition_extractor_r1b_v3.js');
const sha=v=>crypto.createHash('sha256').update(v).digest('hex');
const STATES=['s2a','s2b'];
const ACTIONS=['submit-root-3-a','submit-root-3-b',
  'submit-root-3-old-only','submit-root-3-new-only'];
function check(ok,msg){if(!ok)throw Error(msg)}
function rootDoc(name,raw){
  const obj=JSON.parse(raw.toString('utf8'));
  const signedBytes=Buffer.from(canon(obj.signed),'utf8');
  return {name,version:obj.signed.version,obj,
    hash:sha(raw),signedBytes,signedHash:sha(signedBytes)};
}
function fingerprint(o){
  const signedHash=sha(Buffer.from(canon(o.signed),'utf8'));
  const sigs=[...o.signatures].map(x=>({keyid:x.keyid,sig:x.sig}))
    .sort((a,b)=>a.keyid.localeCompare(b.keyid));
  const signatureHash=sha(Buffer.from(canon(sigs),'utf8'));
  return sha(Buffer.concat([
    Buffer.from(signedHash,'hex'),Buffer.from(signatureHash,'hex')]));
}
function prepare(dir,nativeFile){
  const manifest=JSON.parse(fs.readFileSync(
    path.join(dir,'SOURCE_MANIFEST.json'),'utf8'));
  check(manifest.schema==='eeq-r4-d0-source-manifest-v1',
    'BAD_SOURCE_MANIFEST_VERSION');
  const docMap=new Map();
  for(const item of manifest.sources){
    const raw=fs.readFileSync(path.join(dir,item.name));
    check(sha(raw)===item.sha256&&raw.length===item.bytes,
      'SOURCE_HASH_PIN_MISMATCH_'+item.name);
    docMap.set(item.name,rootDoc(item.name,raw));
  }
  check(docMap.size===7,'SOURCE_DOCUMENT_COUNT_NOT_SEVEN');
  const native=JSON.parse(fs.readFileSync(nativeFile,'utf8'));
  check(native.schema==='eeq-r4-d0-tuf-native-auth-contrast-v1',
    'BAD_IMMUTABLE_NATIVE_SCHEMA');
  check(native.source_predictions_read===false &&
    native.original_g5_increment===0,
    'NATIVE_SOURCE_PREDICTION_CONTAMINATION');
  const rows=new Map();
  for(const row of native.native_rows){
    const k=row.state+'|'+row.action;
    check(!rows.has(k),'DUPLICATE_NATIVE_CASE_'+k);
    rows.set(k,row);
  }
  check(rows.size===8,'NATIVE_CASE_MISSING');
  const anchor=docMap.get('root-1-common.json');
  for(const state of STATES){
    const root=docMap.get('root-2-'+state[2]+'.json');
    const old=verifyRole(anchor,root),fresh=verifyRole(root,root);
    check(old.status==='SUFFICIENT'&&fresh.status==='SUFFICIENT'&&
      root.version===2,'NATIVE_STATE_SETUP_NOT_LAWFUL_'+state);
  }
  check(native.setup_controls.length===2,'NATIVE_TWO_SETUPS_REQUIRED');
  const setupMap=new Map(native.setup_controls.map(x=>[x.state,x]));
  for(const state of STATES){
    const s=setupMap.get(state);
    const file='root-2-'+state[2]+'.json';
    check(s&&s.result==='PASS'&&s.native_source_name===file&&
      s.setup_source_sha256===docMap.get(file).hash&&
      s.native_version===2,'NATIVE_ANCHOR_SETUP_MISMATCH_'+state);
  }
  const certificates=[];
  for(const state of STATES){
    const trustedName='root-2-'+state[2]+'.json';
    const trusted=docMap.get(trustedName);
    for(const action of ACTIONS){
      const name='root-3-'+action.slice('submit-root-3-'.length)+'.json';
      const candidate=docMap.get(name);
      check(!!candidate,'REGISTERED_CANDIDATE_NOT_FOUND');
      const nativeRow=rows.get(state+'|'+action);
      check(!!nativeRow,'NATIVE_CASE_MISSING_'+state+'|'+action);
      const old=verifyRole(trusted,candidate);
      const fresh=verifyRole(candidate,candidate);
      const next=candidate.version===trusted.version+1;
      const unknown=old.status==='UNKNOWN'||fresh.status==='UNKNOWN';
      const status=unknown&&next?'MODEL_UNSUPPORTED':
        next&&old.status==='SUFFICIENT'&&fresh.status==='SUFFICIENT'?
        'ACCEPT':'REJECT';
      const post=status==='ACCEPT'?candidate:trusted;
      const expectedFingerprint=fingerprint(post.obj);
      const matches=(
        status!=='MODEL_UNSUPPORTED' &&
        status===nativeRow.native_outcome &&
        nativeRow.state_setup_source===trustedName &&
        nativeRow.candidate_source===name &&
        nativeRow.state_source_sha256===trusted.hash &&
        nativeRow.candidate_source_sha256===candidate.hash &&
        nativeRow.initial_native_source===trustedName &&
        nativeRow.post_native_source===post.name &&
        nativeRow.initial_metadata_identity===fingerprint(trusted.obj) &&
        nativeRow.post_metadata_identity===expectedFingerprint &&
        nativeRow.initial_native_version===2 &&
        nativeRow.post_native_version===(status==='ACCEPT'?3:2) &&
        nativeRow.setup_error===null
      );
      certificates.push({
        schema:'eeq-r4-qualified-transition-certificate-v0',
        domain:'tuf_root_update',
        contract_id:'R4_D0_TUF_SIGNED_ROOT_UPDATE_ONLY',
        case_id:state+'|'+action,
        sources:{
          trusted_root:trusted.hash,
          proposed_root:candidate.hash,
        },
        original_state:trustedName,
        qualified_obligations:[
          {type:'VERSION_CONTINUITY',qualified:next,
            old_version:trusted.version,new_version:candidate.version},
          {type:'TUF_OLD_ROOT_AUTHORITY',qualified:old.status==='SUFFICIENT',
            status:old.status,verified_unique_keyids:old.verified_unique_keyids,
            threshold:old.threshold},
          {type:'TUF_NEW_ROOT_AUTHORITY',qualified:fresh.status==='SUFFICIENT',
            status:fresh.status,verified_unique_keyids:fresh.verified_unique_keyids,
            threshold:fresh.threshold},
        ],
        action,
        outcome:status,
        native_observation:nativeRow.native_outcome,
        successor_state:post.name,
        native_successor:nativeRow.post_native_source,
        source_signed_sha256:candidate.signedHash,
        expected_post_metadata_identity:expectedFingerprint,
        native_post_metadata_identity:nativeRow.post_metadata_identity,
        checker_outcome:matches?'VERIFIED':unknown?'UNSUPPORTED':'MISMATCH',
        verifier_domain:'TUF_OLPC_ED25519_OLD_NEW_ROLE_RECHECK',
        provenance:{
          source_artifact_id:11608811184,
          native_artifact_id:11609456107,
        },
      });
    }
  }
  return {schema:'eeq-r4-c0-tuf-certificates-v0',certificates,
    role_setup_count:2,common_state_versions:[2,2],
    native_calls_in_c0:0};
}
if(require.main===module){
  check(process.argv.length===5,
    'usage: r4_c0_tuf_certificates.js SIGNED_SOURCES_DIR NATIVE_RAW_JSON CERT_OUT_JSON');
  const out=prepare(process.argv[2],process.argv[3]);
  fs.writeFileSync(process.argv[4],JSON.stringify(out,null,2)+'\n');
  const statuses={};
  for(const x of out.certificates)statuses[x.checker_outcome]=
    (statuses[x.checker_outcome]||0)+1;
  console.log(JSON.stringify({certificates:out.certificates.length,
    outcomes:statuses,native_calls:0}));
}
module.exports={prepare,fingerprint};
