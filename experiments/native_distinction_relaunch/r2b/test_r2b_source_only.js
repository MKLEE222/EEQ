#!/usr/bin/env node
'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {verifyRole}=require('../tuf_trust_transition_extractor_r1b_v3.js');
const gen=require('./r2b_generate_controlled_sources.js');

test('deterministic PUBLIC test-only cryptographic signed sources',()=>{
  const a=gen.registeredSources(),b=gen.registeredSources();
  assert.equal(a.records.length,9);
  assert.deepEqual(a.records.map(r=>r.sha256),b.records.map(r=>r.sha256));
  assert.equal(new Set(a.records.map(r=>r.sha256)).size,9);
  assert.equal(a.public_keyids.ROOT,b.public_keyids.ROOT);
  assert.notEqual(a.public_keyids.TARGET_A,a.public_keyids.TARGET_B);
});
test('all controlled roots have authentic root-role signatures',()=>{
  const {records}=gen.registeredSources();
  const ctx=gen.context(records);
  for(const [name,root] of ctx.roots)
    assert.equal(verifyRole(root,root).status,'SUFFICIENT',name);
});
test('same root authorization but actual targets authorization differs',()=>{
  const x=gen.build();
  for(const version of [2,3,4]){
    const a=x.model.states.find(s=>s.state==='s'+version+'a');
    const b=x.model.states.find(s=>s.state==='s'+version+'b');
    assert.deepEqual(a.root_role_keyids,b.root_role_keyids);
    assert.notDeepEqual(a.targets_role_keyids,b.targets_role_keyids);
    assert.notEqual(a.source_sha256,b.source_sha256);
  }
});
test('the current FULL action set is fixed and every step has a closed edge',()=>{
  const {model}=gen.build();
  assert.deepEqual(model.actions.map(a=>a.action),
    ['submit-root-3-a','submit-root-3-b','submit-root-4-a','submit-root-4-b']);
  assert.equal(model.predictions.length,24);
  assert.equal(model.summary.advances,8);
  assert.equal(model.summary.keeps,16);
  assert.equal(model.summary.unsupported,0);
  for(const p of model.predictions)
    assert.ok(model.states.some(s=>s.state===p.to_state));
});
test('fully direct trace oracle and Moore both give 3 noncosmetic merge classes',()=>{
  const {model}=gen.build();
  assert.deepEqual(model.quotient.horizons.map(x=>x.class_count),[3,3,3]);
  assert.deepEqual(model.quotient.horizons.map(x=>x.legal_merges),[3,3,3]);
  assert.equal(model.quotient.direct_trace_oracle_agrees,true);
  assert.equal(model.quotient.action_words_per_state,21);
});
test('a fair strong version-only B9 exactly matches all source predictions',()=>{
  const {model}=gen.build();
  assert.equal(model.strong_b9.matched_source_predictions,24);
  assert.equal(model.strong_b9.total,24);
});
test('native targets qualification predictions separate A and B',()=>{
  const {model}=gen.build();
  const count={QUALIFIED:0,UNQUALIFIED:0};
  for(const q of model.qualifications){
    count[q.status]++;
    assert.equal(q.status,
      q.targets_source_name==='targets-'+q.state.slice(-1)+'.json'?
      'QUALIFIED':'UNQUALIFIED');
  }
  assert.equal(count.QUALIFIED,6);
  assert.equal(count.UNQUALIFIED,6);
});
test('changing a candidate signature makes source-derived transition reject',()=>{
  const {records}=gen.registeredSources();
  const ctx=gen.context(records);
  const old=ctx.stateRoots.get('s2a');
  const candidate=ctx.roots.get('root-3-a.json');
  const tampered={...candidate,obj:{
    signed:candidate.obj.signed,
    signatures:candidate.obj.signatures.map(s=>({
      ...s,sig:'00'.repeat(64)}))}};
  const out=gen.edge({state:'s2a',root:old},
    {action:'submit-root-3-a'},tampered);
  assert.equal(out.effect,'KEEP_TRUST_ROOT');
  assert.equal(out.to_state,'s2a');
});
test('unsupported signing scheme must not count as known invalid',()=>{
  const {records}=gen.registeredSources();
  const ctx=gen.context(records);
  const old=ctx.stateRoots.get('s2a');
  const candidate=ctx.roots.get('root-3-a.json');
  const rootKey=old.obj.signed.roles.root.keyids[0];
  const keys={...old.obj.signed.keys,
    [rootKey]:{...old.obj.signed.keys[rootKey],scheme:'unknown-test-curve'}};
  const badOld={...old,obj:{...old.obj,signed:{
    ...old.obj.signed,keys}}};
  const out=gen.edge({state:'s2a',root:badOld},
    {action:'submit-root-3-a'},candidate);
  assert.equal(out.effect,'MODEL_UNSUPPORTED');
  assert.equal(out.to_state,null);
});
test('public test material does not touch prior production freeze or oracle',()=>{
  const {model,manifest}=gen.build();
  assert.equal(model.native_outcomes_read,false);
  assert.equal(manifest.native_oracle_invoked,false);
  assert.equal(manifest.original_g5_increment,0);
});
