#!/usr/bin/env node
'use strict';
/* Adversarial source-only TUF compiler tests, no tuf-js native or old scores */
const assert=require('assert'),crypto=require('crypto');
const {sourceFixtures}=require('../r4/r4_d0_tuf_sources.js');
const {compileCase,build}=require('./r4_e2_tuf_source_rule_compile.js');
const {canon}=require('../tuf_trust_transition_extractor_r1b_v3.js');
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const fixture=()=>new Map(sourceFixtures().sources.map(s=>[s.name,s]));
function repack(rec,obj){
 const raw=Buffer.from(JSON.stringify(obj,null,2)+'\n');
 return {...rec,obj,raw,sha256:hash(raw)};
}
function localEval(n){
 if(n.op==='ATOM')return n.value;
 const v=n.children.map(localEval);
 if(n.op==='AND')return v.every(Boolean);
 if(n.op==='OR')return v.some(Boolean);
 if(n.op==='THRESHOLD')return v.filter(Boolean).length>=n.k;
 throw Error('UNREGISTERED_OPERATOR');
}
let tests=0;
function t(name,callback){callback();tests++;}
const get=(m,n)=>{assert(m.has(n));return m.get(n);};
t('01 fixed eight source-only D0 candidate programs and no outcomes leaked',()=>{
 const x=build();assert.strictEqual(x.rows.length,8);
 assert.strictEqual(x.reference.length,8);
 assert.strictEqual(x.sources.length,7);
 assert(x.rows.every(q=>q.native_labels_read===false));
 assert(x.rows.every(q=>!Object.hasOwn(q,'native_expected')));
});
t('02 generic candidate source role expression agrees with full source B9 all eight',()=>{
 const x=build();const m=new Map(x.reference.map(r=>[r.case_id,r.direct_B9_source_only_effect]));
 assert(x.rows.every(r=>localEval(r.formula)===m.get(r.case_id)));
 assert.strictEqual(x.rows.filter(r=>localEval(r.formula)).length,2);
});
t('03 root2 same-version different old authority discriminates identical candidate',()=>{
 const m=fixture(),anchor=get(m,'root-1-common.json'),cand=get(m,'root-3-a.json');
 const a=compileCase(anchor,get(m,'root-2-a.json'),cand,'A');
 const b=compileCase(anchor,get(m,'root-2-b.json'),cand,'B');
 assert.strictEqual(localEval(a.formula),true);
 assert.strictEqual(localEval(b.formula),false);
 assert.strictEqual(cand.obj.signed.version,3);
 assert.strictEqual(a.verified_source_sha256.candidate_root,b.verified_source_sha256.candidate_root);
});
t('04 candidate missing new signer has definitive checked false',()=>{
 const m=fixture(),a=compileCase(get(m,'root-1-common.json'),
        get(m,'root-2-a.json'),get(m,'root-3-old-only.json'),'old_only');
 assert.strictEqual(localEval(a.formula),false);
});
t('05 candidate missing old signer has definitive checked false',()=>{
 const m=fixture(),a=compileCase(get(m,'root-1-common.json'),
        get(m,'root-2-a.json'),get(m,'root-3-new-only.json'),'new_only');
 assert.strictEqual(localEval(a.formula),false);
});
t('06 duplicate candidate signature key IDs are not threshold-counted',()=>{
 const m=fixture(),record=get(m,'root-3-a.json');
 const o=structuredClone(record.obj);
 o.signatures.push(structuredClone(o.signatures[0]));
 const bad=repack(record,o);
 assert.throws(()=>compileCase(get(m,'root-1-common.json'),
        get(m,'root-2-a.json'),bad,'bad'),
        /DUPLICATE_CANDIDATE_SIGNATURE_KEYID/);
});
t('07 inconsistent hashed object is refused before proof generation',()=>{
 const m=fixture(),record=get(m,'root-3-a.json');
 const altered={...record,obj:structuredClone(record.obj)};
 altered.obj.signed.version=7;
 assert.throws(()=>compileCase(get(m,'root-1-common.json'),
        get(m,'root-2-a.json'),altered,'bad'),
        /SOURCE_OBJECT_NOT_EQUAL/);
});
t('08 missing or wrong old authorized source is not assumed false',()=>{
 const m=fixture(),cand=get(m,'root-3-a.json');
 const altered={...get(m,'root-2-a.json'),raw:null};
 assert.throws(()=>compileCase(get(m,'root-1-common.json'),altered,cand,'bad'),
        /SOURCE_RAW_SHA/);
});
t('09 invalid new role threshold from signed bytes refuses unsupported grammar',()=>{
 const m=fixture(),record=get(m,'root-3-a.json');
 const o=structuredClone(record.obj);
 o.signed.roles.root.threshold=2;
 const bad=repack(record,o);
 assert.throws(()=>compileCase(get(m,'root-1-common.json'),
        get(m,'root-2-a.json'),bad,'bad'),/INVALID_ROLE_THRESHOLD/);
});
t('10 corrupted signed bytes cannot be counted as verified old/new signatures',()=>{
 const m=fixture(),record=get(m,'root-3-a.json');
 const o=structuredClone(record.obj);
 o.signatures[0].sig='00'.repeat(64);
 const modified=repack(record,o);
 const prog=compileCase(get(m,'root-1-common.json'),
        get(m,'root-2-a.json'),modified,'invalid_signature');
 assert.strictEqual(localEval(prog.formula),false);
});
t('11 original old root setup cannot be silently swapped',()=>{
 const m=fixture();
 assert.throws(()=>compileCase(get(m,'root-1-common.json'),
   get(m,'root-3-a.json'),get(m,'root-3-b.json'),'bad_setup'),
   /INITIAL_ROOT2_HISTORY_NOT_VERIFIED|UNREGISTERED_ROOT2_TO_ROOT3_GRAMMAR/);
});
t('12 verifier explicitly reports original native label absent',()=>{
 const x=build();assert(x.reference.every(r=>r.original_native_outcome_read===false));
});
console.log(JSON.stringify({synthetic_tuf_compiler_tests:tests,
  source_only_programs:8,new_native_calls:0,
  original_previously_scored_native_labels_read:false}));
