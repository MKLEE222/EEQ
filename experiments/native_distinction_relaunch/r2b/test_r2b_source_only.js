#!/usr/bin/env node
'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('fs'),os=require('os'),path=require('path');
const {run}=require('./r2b_controlled_source_generator.js');
const {derive,pathsUpTo2}=require('./r2b_source_predict.js');

function withSource(fn){
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'eeq-r2b-source-'));
  try{run(dir);return fn(dir);}finally{
    fs.rmSync(dir,{recursive:true,force:true});
  }
}
test('six source files are deterministic and fully reproducible',()=>{
  withSource(a=>withSource(b=>{
    const A=run(a),B=run(b);
    assert.deepEqual(A.files,B.files);
    assert.equal(A.files.length,6);
    assert.equal(new Set(A.files.map(x=>x.sha256)).size,6);
  }));
});
test('all four root anchors/candidates are truly self-signed',()=>{
  withSource(dir=>{
    const x=derive(dir);
    for(const id of ['A','B','C2','C3']){
      assert.equal(x.root_self_qualification[id].status,true,id);
    }
  });
});
test('targets authorization differs by valid source, not JSON cosmetics',()=>{
  withSource(dir=>{
    const x=derive(dir);
    assert.equal(x.equal_root_role,true);
    assert.equal(x.different_targets_role,true);
    assert.equal(x.targets_role_qualification.A.TARGETS_A.qualified,true);
    assert.equal(x.targets_role_qualification.B.TARGETS_B.qualified,true);
    assert.equal(x.targets_role_qualification.A.TARGETS_B.qualified,false);
    assert.equal(x.targets_role_qualification.B.TARGETS_A.qualified,false);
  });
});
test('root-only decision traces match for every frozen action word up to r=2',()=>{
  withSource(dir=>{
    const x=derive(dir);
    assert.equal(x.root_only_current_and_future_equivalent,true);
    assert.equal(x.strong_b9_initial_equivalence,true);
    assert.equal(x.classical_moore_quotient_initial_equivalence,true);
    assert.equal(x.no_novelty_advantage_over_strong_b9_claimed,true);
    assert.equal(x.rows.length,14);
    assert.equal(pathsUpTo2().length,7);
    assert.deepEqual(
      [...new Set(x.rows.map(r=>r.prefix.join(',')))].sort(),
      pathsUpTo2().map(p=>p.join(',')).sort()
    );
  });
});
test('source signing bytes cannot be tampered without detection',()=>{
  withSource(dir=>{
    const file=path.join(dir,'anchor_a.root.json');
    const obj=JSON.parse(fs.readFileSync(file,'utf8'));
    obj.signed.roles.targets.threshold=2;
    fs.writeFileSync(file,JSON.stringify(obj,null,2)+'\n');
    assert.throws(()=>derive(dir),/ROOT_SELF_SIGNING_INVALID/);
  });
});
test('targets capability proof fails on forged targets signature',()=>{
  withSource(dir=>{
    const file=path.join(dir,'targets_a.targets.json');
    const obj=JSON.parse(fs.readFileSync(file,'utf8'));
    obj.signatures[0].sig='00'.repeat(64);
    fs.writeFileSync(file,JSON.stringify(obj,null,2)+'\n');
    assert.throws(()=>derive(dir),
      /NONCOSMETIC_TARGETS_QUALIFICATION_CONTRAST_FAILED/);
  });
});
test('root-update requires old/new crypto, not just version continuity',()=>{
  withSource(dir=>{
    const file=path.join(dir,'candidate_2.root.json');
    const obj=JSON.parse(fs.readFileSync(file,'utf8'));
    obj.signatures[0].sig='00'.repeat(64);
    fs.writeFileSync(file,JSON.stringify(obj,null,2)+'\n');
    assert.throws(()=>derive(dir),/ROOT_SELF_SIGNING_INVALID/);
  });
});
test('no source file discloses serialized private key material',()=>{
  withSource(dir=>{
    for(const name of fs.readdirSync(dir).filter(x=>x.endsWith('.json'))){
      const content=fs.readFileSync(path.join(dir,name),'utf8');
      assert.doesNotMatch(content,/-----BEGIN PRIVATE KEY-----/);
      assert.doesNotMatch(content,/"privateKey"\s*:/);
    }
  });
});
