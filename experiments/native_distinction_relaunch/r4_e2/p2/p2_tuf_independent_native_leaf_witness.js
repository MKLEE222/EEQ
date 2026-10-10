#!/usr/bin/env node
'use strict';
/* P2 independently RECHECK native TUF primitives from source bytes.
 * This module must NOT import the E2 compiler, E2 expected result, or P1
 * result. All Ed25519 signature bits and roots are recomputed here.
 * The original TUF canonicalizer is part of the trusted native primitive.
 */
const crypto=require('crypto'),fs=require('fs'),path=require('path');
const {sourceFixtures}=require('../../r4/r4_d0_tuf_sources.js');
const {canon}=require('../../tuf_trust_transition_extractor_r1b_v3.js');

const SPKI_ED25519=Buffer.from('302a300506032b6570032100','hex');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
function demand(x,msg){if(!x)throw Error('P2_TUF_'+msg);}
const STATES=[['s2a','root-2-a.json'],['s2b','root-2-b.json']];
const CANDIDATES=[
 ['root-3-a','root-3-a.json'],
 ['root-3-b','root-3-b.json'],
 ['root-3-old-only','root-3-old-only.json'],
 ['root-3-new-only','root-3-new-only.json']
];

function verifiedSource(rec){
 demand(rec&&Buffer.isBuffer(rec.raw)&&rec.obj&&rec.sha256===sha(rec.raw),
        'SOURCE_RAW_DIGEST_OR_BYTES_INVALID');
 demand(JSON.stringify(JSON.parse(rec.raw.toString('utf8')))===
        JSON.stringify(rec.obj),'RAW_JSON_OBJECT_MISMATCH');
 demand(rec.obj.signed&&rec.obj.signed._type==='root'&&
        rec.obj.signed.spec_version==='1.0.31'&&
        Array.isArray(rec.obj.signatures),'SOURCE_NOT_REGISTERED_ROOT');
}

function ed25519Verify(key,bytes,sig) {
 if(!key || key.keytype!=='ed25519' || key.scheme!=='ed25519' ||
    !key.keyval || !/^[0-9a-f]{64}$/.test(key.keyval.public||'') ||
    !sig || !/^[0-9a-f]{128}$/.test(sig)) return false;
 const pub=crypto.createPublicKey({
    key:Buffer.concat([SPKI_ED25519,Buffer.from(key.keyval.public,'hex')]),
    type:'spki',format:'der'
 });
 return crypto.verify(null,bytes,pub,Buffer.from(sig,'hex'));
}

function nativeRoleThreshold(trustRootRec,candidateRec,qualifier,refs){
 const authority=trustRootRec.obj.signed;
 const role=authority.roles&&authority.roles.root;
 demand(role&&Array.isArray(role.keyids)&&role.keyids.length>0 &&
        new Set(role.keyids).size===role.keyids.length &&
        Number.isInteger(role.threshold)&&
        role.threshold>=1&&role.threshold<=role.keyids.length,
        'INVALID_AUTHORIZED_OLD_OR_NEW_ROLE_THRESHOLD');
 const signatures=candidateRec.obj.signatures;
 demand(signatures.every(x=>x&&typeof x.keyid==='string'&&
        typeof x.sig==='string') &&
        new Set(signatures.map(x=>x.keyid)).size===signatures.length,
        'DUPLICATE_OR_MALFORMED_SIGNER_ID');
 const bytes=Buffer.from(canon(candidateRec.obj.signed),'utf8');
 const children=role.keyids.map(kid=>{
    const key=authority.keys&&authority.keys[kid];
    demand(key&&typeof key==='object','AUTHORIZED_PUBLIC_KEY_MISSING');
    const signature=signatures.find(s=>s.keyid===kid);
    const verified=Boolean(signature&&ed25519Verify(key,bytes,signature.sig));
    return {op:'ATOM',id:qualifier+':'+kid,value:verified,
            source_refs:refs,
            obligation:qualifier+'_REGISTERED_ROLE_UNIQUE_ED25519_SIGNATURE'};
 });
 return {op:'THRESHOLD',k:role.threshold,children};
}

function thresholdSatisfied(node){
 demand(node.op==='THRESHOLD','NOT_THRESHOLD');
 return node.children.filter(c=>c.value===true).length>=node.k;
}
function checkCommonAnchor(anchor,old){
 demand(anchor.obj.signed.version===1&&old.obj.signed.version===2,
        'UNSUPPORTED_INITIAL_ROOT_VERSION');
 const anchorProof=nativeRoleThreshold(anchor,old,'SETUP_ANCHOR',
                                    ['anchor_root','trusted_root']);
 const root2Proof=nativeRoleThreshold(old,old,'SETUP_ROOT2',
                                    ['trusted_root']);
 demand(thresholdSatisfied(anchorProof)&&thresholdSatisfied(root2Proof),
        'UNTRUSTED_INITIAL_ROOT2_HISTORY');
}

function build(){
 const all=sourceFixtures();
 demand(all.sources.length===7,'SEVEN_REGISTERED_SOURCE_FILES');
 const records=new Map(all.sources.map(s=>[s.name,s]));
 demand(records.size===7,'SOURCE_FILE_ID_COLLISION');
 for(const rec of records.values())verifiedSource(rec);
 const anchor=records.get('root-1-common.json');
 const result=[];
 for(const [state,oldSource] of STATES){
   const old=records.get(oldSource);
   checkCommonAnchor(anchor,old);
   for(const [action,candidateSource] of CANDIDATES){
    const candidate=records.get(candidateSource);
    demand(candidate.obj.signed.version===3,'CANDIDATE_VERSION_UNREGISTERED');
    const oldRole=nativeRoleThreshold(old,candidate,'OLD_ROOT',
                                      ['trusted_root','candidate_root']);
    const newRole=nativeRoleThreshold(candidate,candidate,'NEW_ROOT',
                                      ['candidate_root']);
    const expected={
      case_id:'TUF|'+state+'|'+action,
      domain:'TUF_ROOT_UPDATE',
      registered_contract:'E2_TUF_ROOT_UPDATE_OLD_NEW_ROLE_V1',
      verified_source_sha256:{
        anchor_root:anchor.sha256,
        trusted_root:old.sha256,
        candidate_root:candidate.sha256,
      },
      formula:{op:'AND',children:[
       {op:'ATOM',id:'VERSION_CONTIGUOUS',
        value:candidate.obj.signed.version===old.obj.signed.version+1,
        source_refs:['trusted_root','candidate_root'],
        obligation:'TUF_ROOT_VERSION_SUCCESSION_FROM_SOURCE_BYTES'},
       oldRole,newRole
      ]},
      original_source_only_setup_proven_by_new_primitive_verifier:true,
      original_native_tuf_js_not_called:true,
      author_complete_source_roster_not_externally_attested:true,
      E2_candidate_IR_or_B9_output_never_read:true
    };
    result.push(expected);
   }
 }
 demand(result.length===8&&new Set(result.map(x=>x.case_id)).size===8,
        'TUF_SOURCE_WITNESS_DENOMINATOR');
 return result;
}
function main(){
 demand(process.argv.length===3,'USAGE_EXPECTS_OUT_FILE');
 const rows=build();
 fs.mkdirSync(path.dirname(process.argv[2]),{recursive:true});
 fs.writeFileSync(process.argv[2],JSON.stringify(rows,null,2)+'\n');
 console.log(JSON.stringify({
  TUF_original_source_primitive_witnesses:rows.length,
  signed_source_bytes_read:true,
  independent_native_crypto_verify_invoked:true,
  original_scored_native_labels_read:false,
  fully_informed_B9_allowed_same_verification:true
 }));
}
if(require.main===module)main();
module.exports={build,nativeRoleThreshold,ed25519Verify};
