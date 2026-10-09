#!/usr/bin/env node
'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('fs');
const path=require('path');
const os=require('os');
const crypto=require('crypto');
const {generate,publicTestKey}=require('./r2b_signed_sources.js');
const {hash,canon,edge}=require('../tuf_trust_transition_extractor_r1b_v3.js');

function inTemp(fn) {
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'eeq-r2b-source-test-'));
  try{return fn(dir);} finally {fs.rmSync(dir,{recursive:true,force:true});}
}
function read(dir,name){return JSON.parse(fs.readFileSync(path.join(dir,name),'utf8'));}

test('controlled public key IDs are deterministic TUF-canonical public key hashes',()=>{
  const a=publicTestKey('targets_A'),b=publicTestKey('targets_A');
  assert.equal(a.id,b.id);
  assert.equal(a.id,hash(Buffer.from(canon(a.pub),'utf8')));
  assert.match(a.pub.keyval.public,/^[a-f0-9]{64}$/);
  assert.notEqual(a.id,publicTestKey('targets_B').id);
});
test('seven source blobs and source-only predictions reproduce byte exactly',()=>{
  const before=inTemp(d=>generate(d));
  const after=inTemp(d=>generate(d));
  assert.deepEqual(before.source_files,after.source_files);
  assert.equal(before.native_oracle_called,false);
  assert.equal(before.prior_native_outcomes_used,false);
  assert.equal(before.source_only_root_update_traces_equal,true);
});
test('root2 sources have genuinely different TARGETS qualified key identity',()=>{
  inTemp(d=>{
    const p=generate(d);
    const a=read(d,'root2_A.json'),b=read(d,'root2_B.json');
    assert.deepEqual(a.signed.roles.root,b.signed.roles.root);
    assert.notDeepEqual(a.signed.roles.targets,b.signed.roles.targets);
    assert.notDeepEqual(a.signed.keys,b.signed.keys);
    assert.notEqual(p.source_files['root2_A.json'].sha256,p.source_files['root2_B.json'].sha256);
    const c=p.real_targets_qualification_cross_check;
    assert.equal(c.A.A.authorized,true);
    assert.equal(c.A.B.authorized,false);
    assert.equal(c.B.A.authorized,false);
    assert.equal(c.B.B.authorized,true);
  });
});
test('root1 -> root2A and root1 -> root2B independently pass dual signing obligations',()=>{
  inTemp(d=>{
    const p=generate(d);
    assert.deepEqual(p.root1_source_only_setup_effects,
      ['ADVANCE_TRUST_ROOT','ADVANCE_TRUST_ROOT']);
  });
});
test('root3 candidate source signature corruption fails cryptographic old/new checks',()=>{
  inTemp(d=>{
    const p=generate(d);
    const matching=p.registered_graph.filter(x=>x.action==='submit_root3_bad_sig');
    assert.equal(matching.length,3);
    assert(matching.every(x=>x.expected_effect==='KEEP_TRUST_ROOT'));
    assert(matching.every(x=>x.expected_next===x.state));
  });
});
test('root2_A replay never advances under any registered initial state',()=>{
  inTemp(d=>{
    const p=generate(d);
    const matching=p.registered_graph.filter(x=>x.action==='submit_root2_A_replay');
    assert.equal(matching.length,3);
    assert(matching.every(x=>x.expected_effect==='KEEP_TRUST_ROOT'));
  });
});
test('full 3-action alphabet remains registered at every state',()=>{
  inTemp(d=>{
    const p=generate(d);
    assert.equal(p.registered_graph.length,9);
    assert.equal(new Set(p.registered_graph.map(x=>x.state+'|'+x.action)).size,9);
    assert.deepEqual(p.refinement_classes.map(x=>x.length),[2,2,2]);
    for(const groups of p.refinement_classes){
      assert(groups.some(g=>g.includes('H_A')&&g.includes('H_B')));
      assert(groups.some(g=>g.length===1&&g[0]==='H_3'));
    }
  });
});
test('all action traces through horizon two are checked for both histories',()=>{
  inTemp(d=>{
    const p=generate(d);
    assert.equal(p.source_trace_A.length,13);
    assert.equal(p.source_trace_B.length,13);
    assert.deepEqual(p.source_trace_A,p.source_trace_B);
    const paths=new Set(p.source_trace_A.map(x=>x.action_word.join('|')));
    assert.equal(paths.size,13);
    assert(p.source_trace_A.some(x=>x.action_word.length===2));
  });
});
test('a root-role alias is NOT allowed to erase targets-role audit differences',()=>{
  inTemp(d=>{
    const p=generate(d);
    assert.equal(p.source_only_root_update_traces_equal,true);
    assert.notDeepEqual(p.real_targets_qualification_cross_check.A,
      p.real_targets_qualification_cross_check.B);
    assert.equal(p.r4_independent_advantage,false);
    assert.equal(p.r2_b_native_verified,false);
  });
});
test('all controlled seed material is TEST-ONLY and NOT written as private key file',()=>{
  inTemp(d=>{
    const p=generate(d);
    const files=fs.readdirSync(d);
    assert.deepEqual(files.sort(),
      ['root1.json','root2_A.json','root2_B.json','root3.json',
       'root3_bad_sig.json','targets_A.json','targets_B.json'].sort());
    for(const name of files){
      const raw=fs.readFileSync(path.join(d,name),'utf8');
      assert(!raw.includes('BEGIN PRIVATE KEY'));
      assert(!raw.includes('privateKey'));
    }
    assert.equal(p.no_private_key_artifacts,true);
  });
});
