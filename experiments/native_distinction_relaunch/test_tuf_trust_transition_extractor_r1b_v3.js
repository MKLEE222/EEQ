#!/usr/bin/env node
'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const {canon,verifySignature,verifyRole,edge,publicKey}=require('./tuf_trust_transition_extractor_r1b_v3.js');

function pair(){
  const p=crypto.generateKeyPairSync('ed25519');
  const spki=p.publicKey.export({format:'der',type:'spki'});
  const publicHex=spki.subarray(spki.length-32).toString('hex');
  return {privateKey:p.privateKey,
    key:{keytype:'ed25519',scheme:'ed25519',keyval:{public:publicHex}}};
}
function signedRoot(version,keys,ids,threshold){
  return {_type:'root',version,expires:'2030-01-01T00:00:00Z',
    keys,roles:{root:{keyids:ids,threshold}},spec_version:'1.0.0',
    consistent_snapshot:true};
}
function wrap(version,signed,signatures){
  const bytes=Buffer.from(canon(signed),'utf8');
  return {version,obj:{signed,signatures},signedBytes:bytes,
    signedHash:crypto.createHash('sha256').update(bytes).digest('hex'),hash:'unit-'+version};
}
function good(){
  const old=pair(),fresh=pair();
  const previous=wrap(1,signedRoot(1,{old:old.key},['old'],1),[]);
  const next=signedRoot(2,{fresh:fresh.key},['fresh'],1);
  const signedBytes=Buffer.from(canon(next),'utf8');
  const candidate=wrap(2,next,[
    {keyid:'old',sig:crypto.sign(null,signedBytes,old.privateKey).toString('hex')},
    {keyid:'fresh',sig:crypto.sign(null,signedBytes,fresh.privateKey).toString('hex')},
  ]);
  return {old,fresh,previous,candidate};
}

test('canonical JSON ignores object insertion order and preserves types',()=>{
  assert.equal(canon({b:1,a:'x'}),'{\"a\":\"x\",\"b\":1}');
  assert.equal(canon({a:[false,null,'x'],b:3}),'{\"a\":[false,null,\"x\"],\"b\":3}');
  assert.throws(()=>canon({a:0.1}),/UNSUPPORTED_CANONICAL_NUMBER/);
});
test('verified old and new distinct signatures authorize adjacent move',()=>{
  const {previous,candidate}=good();
  const outcome=edge(previous,candidate);
  assert.equal(outcome.derived_effect,'ADVANCE_TRUST_ROOT');
  assert.equal(outcome.to_state,'trusted-root-2');
  assert.equal(outcome.old_authority.verified_unique_keyids.length,1);
  assert.equal(outcome.new_authority.verified_unique_keyids.length,1);
});
test('current root signature alone is insufficient for old threshold',()=>{
  const x=good();
  x.candidate.obj.signatures=x.candidate.obj.signatures.filter(s=>s.keyid==='fresh');
  assert.equal(edge(x.previous,x.candidate).derived_effect,'KEEP_TRUST_ROOT');
});
test('old root signature alone is insufficient for new threshold',()=>{
  const x=good();
  x.candidate.obj.signatures=x.candidate.obj.signatures.filter(s=>s.keyid==='old');
  assert.equal(edge(x.previous,x.candidate).derived_effect,'KEEP_TRUST_ROOT');
});
test('non-adjacent valid signatures cannot advance trusted root',()=>{
  const x=good();
  x.candidate.version=4;
  x.candidate.obj.signed.version=4;
  x.candidate.signedBytes=Buffer.from(canon(x.candidate.obj.signed),'utf8');
  x.candidate.obj.signatures=[
    {keyid:'old',sig:crypto.sign(null,x.candidate.signedBytes,x.old.privateKey).toString('hex')},
    {keyid:'fresh',sig:crypto.sign(null,x.candidate.signedBytes,x.fresh.privateKey).toString('hex')},
  ];
  assert.equal(edge(x.previous,x.candidate).derived_effect,'KEEP_TRUST_ROOT');
});
test('changing signed metadata invalidates cryptographic threshold',()=>{
  const x=good();
  x.candidate.obj.signed.expires='2040-01-01T00:00:00Z';
  x.candidate.signedBytes=Buffer.from(canon(x.candidate.obj.signed),'utf8');
  assert.equal(edge(x.previous,x.candidate).derived_effect,'KEEP_TRUST_ROOT');
});
test('duplicated signer keyid counts once, never multiplies threshold',()=>{
  const x=good();
  const another=pair();
  x.previous.obj.signed.keys.old2=another.key;
  x.previous.obj.signed.roles.root.keyids=['old','old2'];
  x.previous.obj.signed.roles.root.threshold=2;
  x.candidate.obj.signatures.push({...x.candidate.obj.signatures[0]});
  const role=verifyRole(x.previous,x.candidate);
  assert.equal(role.status,'INSUFFICIENT');
  assert.equal(role.verified_unique_keyids.length,1);
  assert.equal(role.duplicate_envelope_keyids,1);
  assert.equal(edge(x.previous,x.candidate).derived_effect,'KEEP_TRUST_ROOT');
});
test('unknown material cryptographic scheme fails closed, not false',()=>{
  const x=good();
  x.previous.obj.signed.keys.old.scheme='mystery-curve';
  const outcome=edge(x.previous,x.candidate);
  assert.equal(outcome.old_authority.status,'UNKNOWN');
  assert.equal(outcome.derived_effect,'MODEL_UNSUPPORTED');
  assert.equal(outcome.to_state,null);
});
test('malformed signature hexadecimal is INVALID rather than accepted',()=>{
  const x=good();
  x.candidate.obj.signatures[0].sig='zz';
  const verdict=verifySignature(x.old.key,x.candidate.signedBytes,'zz');
  assert.equal(verdict.status,'INVALID');
  assert.equal(edge(x.previous,x.candidate).derived_effect,'KEEP_TRUST_ROOT');
});
test('a source with missing key material must never supply qualification',()=>{
  const x=good();
  x.previous.obj.signed.keys.old.keyval={};
  assert.equal(publicKey(x.previous.obj.signed.keys.old).error,'MISSING_PUBLIC_KEY');
  assert.equal(edge(x.previous,x.candidate).derived_effect,'MODEL_UNSUPPORTED');
});
test('independent key identities do not become equivalent on string similarity',()=>{
  const x=good();
  x.candidate.obj.signatures[0].keyid='fresh';
  const outcome=edge(x.previous,x.candidate);
  assert.equal(outcome.old_authority.verified_unique_keyids.length,0);
  assert.equal(outcome.derived_effect,'KEEP_TRUST_ROOT');
});
test('unsupported canonical signed number cannot be normalized silently',()=>{
  const x=good();
  x.candidate.obj.signed.version=2.25;
  assert.throws(()=>canon(x.candidate.obj.signed),/UNSUPPORTED_CANONICAL_NUMBER/);
});

test('OLPC canonical strings preserve PEM newlines rather than JSON escaping',()=>{
  const value={key:"BEGIN PUBLIC KEY\nline A\nEND PUBLIC KEY"};
  const out=canon(value);
  assert.equal(out, '{"key":"BEGIN PUBLIC KEY\nline A\nEND PUBLIC KEY"}');
  assert.notEqual(out, JSON.stringify(value));
});
test('RSA-PSS old/new dual signatures over PEM-containing signed JSON verify',()=>{
  const old=crypto.generateKeyPairSync('rsa',{modulusLength:2048});
  const fresh=crypto.generateKeyPairSync('rsa',{modulusLength:2048});
  const keyOf=p=>({keytype:'rsa',scheme:'rsassa-pss-sha256',
    keyval:{public:p.publicKey.export({format:'pem',type:'spki'})}});
  const prior=wrap(1,signedRoot(1,{old:keyOf(old)},['old'],1),[]);
  const newSigned=signedRoot(2,{fresh:keyOf(fresh)},['fresh'],1);
  const signed=Buffer.from(canon(newSigned),'utf8');
  assert.equal(signed.includes(Buffer.from('\n')),true);
  const sign=p=>crypto.sign('sha256',signed,{
    key:p.privateKey,padding:crypto.constants.RSA_PKCS1_PSS_PADDING,
    saltLength:crypto.constants.RSA_PSS_SALTLEN_DIGEST}).toString('hex');
  const proposed=wrap(2,newSigned,[
    {keyid:'old',sig:sign(old)},{keyid:'fresh',sig:sign(fresh)}
  ]);
  assert.equal(edge(prior,proposed).derived_effect,'ADVANCE_TRUST_ROOT');
  const altered=wrap(2,{...newSigned,expires:'2041-01-01T00:00:00Z'},
    proposed.obj.signatures);
  assert.equal(edge(prior,altered).derived_effect,'KEEP_TRUST_ROOT');
});
