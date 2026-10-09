#!/usr/bin/env node
'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const {
  build,sourceFixtures,allKeys,asRoot,authorityCertificate,
}=require('./r4_d0_tuf_sources.js');
const {canon,verifySignature,verifyRole}=
  require('../tuf_trust_transition_extractor_r1b_v3.js');

test('all seven controlled source files are uniquely signed and repeatable',()=>{
  const p=sourceFixtures(),q=sourceFixtures();
  assert.equal(p.sources.length,7);
  assert.deepEqual(p.sources.map(s=>s.sha256),q.sources.map(s=>s.sha256));
  assert.equal(new Set(p.sources.map(s=>s.sha256)).size,7);
  assert.equal(new Set(p.sources.filter(s=>s.name.startsWith('root-3-'))
    .map(s=>s.signed_sha256)).size,1);
});
test('root2 A and B have same version but genuinely different root authority',()=>{
  const {stage1}=build();
  assert.deepEqual(stage1.states.map(s=>s.root_version),[2,2]);
  assert.notDeepEqual(stage1.states[0].root_keyids,stage1.states[1].root_keyids);
  assert.equal(stage1.summary.common_root1_legal_setup_preverified,true);
});
test('common anchor authenticates both distinct root2 states',()=>{
  const {sources}=sourceFixtures(),names=new Map(sources.map(s=>[s.name,s]));
  const anchor=asRoot(names.get('root-1-common.json'));
  for(const b of ['a','b']){
    const root=asRoot(names.get('root-2-'+b+'.json'));
    const cert=authorityCertificate(anchor,root);
    assert.equal(cert.old.status,'SUFFICIENT');
    assert.equal(cert.fresh.status,'SUFFICIENT');
    assert.equal(cert.effect,'ADVANCE_TRUST_ROOT');
  }
});
test('same candidate C_A is accepted from state A and refused from B',()=>{
  const {stage1}=build(),a=stage1.predictions.find(x=>
    x.state==='s2a'&&x.action==='submit-root-3-a'),
  b=stage1.predictions.find(x=>
    x.state==='s2b'&&x.action==='submit-root-3-a');
  assert.equal(a.native_expected,'ACCEPT');
  assert.equal(b.native_expected,'REJECT');
  assert.equal(a.candidate_source_sha256,b.candidate_source_sha256);
  assert.equal(a.initial_root_version,b.initial_root_version);
  assert.equal(a.candidate_root_version,b.candidate_root_version);
  assert.equal(a.old_authority.status,'SUFFICIENT');
  assert.equal(b.old_authority.status,'INSUFFICIENT');
  assert.equal(a.new_authority.status,'SUFFICIENT');
  assert.equal(b.new_authority.status,'SUFFICIENT');
});
test('symmetrically candidate C_B accepts only under ROOT_B',()=>{
  const {stage1}=build();
  const rows=stage1.predictions.filter(x=>x.action==='submit-root-3-b');
  assert.deepEqual(rows.map(x=>x.native_expected),['REJECT','ACCEPT']);
});
test('old-only signatures are insufficient at NEW role on both states',()=>{
  const {stage1}=build();
  const rows=stage1.predictions.filter(x=>
    x.action==='submit-root-3-old-only');
  assert.equal(rows.length,2);
  assert.ok(rows.every(x=>x.native_expected==='REJECT'));
  assert.ok(rows.every(x=>x.new_authority.status==='INSUFFICIENT'));
});
test('new-only signatures are insufficient at OLD role on both states',()=>{
  const {stage1}=build();
  const rows=stage1.predictions.filter(x=>
    x.action==='submit-root-3-new-only');
  assert.ok(rows.every(x=>x.old_authority.status==='INSUFFICIENT'));
});
test('all eight cells present, two accept six reject, strong B9 eight',()=>{
  const {stage1}=build();
  assert.equal(stage1.predictions.length,8);
  assert.equal(stage1.summary.accepted,2);
  assert.equal(stage1.summary.rejected,6);
  assert.equal(stage1.strong_b9.prediction_matches,8);
});
test('best version+candidate-only representation cannot exceed six',()=>{
  const {stage1}=build();
  const groups=new Map();
  for(const row of stage1.predictions){
    const key=[row.initial_root_version,row.candidate_root_version,row.action]
      .join('|');
    if(!groups.has(key))groups.set(key,[]);
    groups.get(key).push(row.native_expected);
  }
  const best=[...groups.values()].reduce((n,values)=>
    n+Math.max(
      values.filter(x=>x==='ACCEPT').length,
      values.filter(x=>x==='REJECT').length),0);
  assert.equal(best,6);
  assert.equal(stage1.version_only_ablation
    .strongest_version_plus_candidate_identity_optimal_matches,best);
});
test('wrong signed byte contents invalidate genuine crypto signature',()=>{
  const {sources}=sourceFixtures();
  const candidate=sources.find(x=>x.name==='root-3-a.json');
  const k=allKeys();
  const sig=candidate.obj.signatures.find(s=>s.keyid===k.ROOT_A.keyid);
  const tampered={...candidate.obj.signed,expires:'2037-01-01T00:00:00Z'};
  assert.equal(verifySignature(k.ROOT_A.key,Buffer.from(canon(tampered)),
    sig.sig).status,'INVALID');
});
test('candidate unknown signing key scheme is material UNKNOWN not false',()=>{
  const {sources}=sourceFixtures(),byName=new Map(sources.map(x=>[x.name,x]));
  const trusted=asRoot(byName.get('root-2-a.json'));
  const cand=asRoot(byName.get('root-3-a.json'));
  const id=trusted.obj.signed.roles.root.keyids[0];
  const modified={...trusted,obj:{...trusted.obj,signed:{
    ...trusted.obj.signed,keys:{...trusted.obj.signed.keys,
      [id]:{...trusted.obj.signed.keys[id],scheme:'nonexistent-curve'}}}}};
  const cert=authorityCertificate(modified,cand);
  assert.equal(cert.old.status,'UNKNOWN');
  assert.equal(cert.effect,'MODEL_UNSUPPORTED');
});
test('distinct public test signing identities produce different TUF keyids',()=>{
  const k=allKeys();
  assert.equal(new Set(Object.values(k).map(v=>v.keyid)).size,7);
  for(const o of Object.values(k))
    assert.equal(crypto.createPublicKey(o.priv).asymmetricKeyType,'ed25519');
});
