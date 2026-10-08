#!/usr/bin/env node
'use strict';
// R1b source-derived crypto. No tuf-js, native outcomes, network, or labels.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const SPKI_ED = Buffer.from('302a300506032b6570032100', 'hex');
function check(ok, msg) { if (!ok) throw new Error(msg); }
function hash(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function canon(x) {
  if (x === null) return 'null';
  if (typeof x === 'string') return JSON.stringify(x);
  if (typeof x === 'boolean') return x ? 'true' : 'false';
  if (typeof x === 'number') {
    check(Number.isSafeInteger(x), 'UNSUPPORTED_CANONICAL_NUMBER');
    return String(x);
  }
  if (Array.isArray(x)) return '[' + x.map(canon).join(',') + ']';
  check(x && typeof x === 'object', 'UNSUPPORTED_JSON');
  return '{' + Object.keys(x).sort().map(k =>
    JSON.stringify(k) + ':' + canon(x[k])).join(',') + '}';
}
function inventory(file) {
  const out = new Map();
  for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    const m = /^\|\s*(\d+)\s*\|\s*([0-9a-f]{64})\s*\|\s*(\d+)\s*\|/.exec(line);
    if (!m) continue;
    const n = Number(m[1]);
    check(!out.has(n), 'DUPLICATE_INVENTORY_VERSION');
    out.set(n, {hash: m[2], bytes: Number(m[3])});
  }
  check(out.size === 8 && Array.from({length:8},(_,i)=>i+1).every(n => out.has(n)),
    'SOURCE_INVENTORY_NOT_1_TO_8');
  return out;
}
function readRoot(dir, version, pins) {
  const raw = fs.readFileSync(path.join(dir, version + '.root.json'));
  const pin = pins.get(version);
  check(raw.length === pin.bytes && hash(raw) === pin.hash,
    'SOURCE_PIN_MISMATCH_' + version);
  const obj = JSON.parse(raw.toString('utf8'));
  check(obj && obj.signed && obj.signed._type === 'root' &&
        obj.signed.version === version, 'BAD_ROOT_METADATA_' + version);
  const keys = obj.signed.keys;
  const role = obj.signed.roles && obj.signed.roles.root;
  check(keys && typeof keys === 'object' && role &&
        Array.isArray(role.keyids) && Array.isArray(obj.signatures),
        'MISSING_ROOT_KEYS_ROLE_OR_SIGNATURES_' + version);
  check(new Set(role.keyids).size === role.keyids.length &&
        Number.isInteger(role.threshold) && role.threshold > 0 &&
        role.threshold <= role.keyids.length &&
        role.keyids.every(id => typeof id === 'string' && keys[id]),
        'INVALID_ROOT_ROLE_' + version);
  const signedBytes = Buffer.from(canon(obj.signed), 'utf8');
  return {version, obj, hash: hash(raw), bytes: raw.length,
    signedBytes, signedHash: hash(signedBytes)};
}
function publicKey(key) {
  if (!key || typeof key !== 'object') return {error:'MISSING_KEY'};
  const s = key.scheme;
  const t = key.keytype;
  const v = key.keyval && key.keyval.public;
  if (typeof v !== 'string' || !v) return {error:'MISSING_PUBLIC_KEY'};
  try {
    if (s === 'ed25519' && t === 'ed25519') {
      if (!/^[0-9a-fA-F]{64}$/.test(v)) return {error:'ED25519_ENCODING_UNSUPPORTED'};
      return {scheme:s, key:crypto.createPublicKey({
        key:Buffer.concat([SPKI_ED,Buffer.from(v,'hex')]),
        format:'der',type:'spki'})};
    }
    if (s === 'ecdsa-sha2-nistp256' && t === 'ecdsa') {
      if (!v.includes('BEGIN PUBLIC KEY')) return {error:'EC_ENCODING_UNSUPPORTED'};
      const k = crypto.createPublicKey(v);
      if (k.asymmetricKeyType !== 'ec' ||
          k.asymmetricKeyDetails?.namedCurve !== 'prime256v1')
        return {error:'EC_CURVE_UNSUPPORTED'};
      return {scheme:s,key:k};
    }
    if (s === 'rsassa-pss-sha256' && t === 'rsa') {
      if (!v.includes('BEGIN PUBLIC KEY')) return {error:'RSA_ENCODING_UNSUPPORTED'};
      const k = crypto.createPublicKey(v);
      if (!['rsa','rsa-pss'].includes(k.asymmetricKeyType))
        return {error:'RSA_KEY_UNSUPPORTED'};
      return {scheme:s,key:k};
    }
    return {error:'UNREGISTERED_KEYTYPE_SCHEME'};
  } catch (e) { return {error:'BAD_PUBLIC_KEY_BYTES'}; }
}
function verifySignature(key, signedBytes, hex) {
  const pub = publicKey(key);
  if (pub.error) return {status:'UNKNOWN',reason:pub.error};
  if (typeof hex !== 'string' || !/^[0-9a-fA-F]+$/.test(hex) || hex.length % 2)
    return {status:'INVALID',reason:'BAD_SIGNATURE_HEX'};
  try {
    const sig = Buffer.from(hex,'hex');
    let ok = false;
    if (pub.scheme === 'ed25519')
      ok = crypto.verify(null,signedBytes,pub.key,sig);
    else if (pub.scheme === 'ecdsa-sha2-nistp256')
      ok = crypto.verify('sha256',signedBytes,pub.key,sig);
    else
      ok = crypto.verify('sha256',signedBytes,{
        key:pub.key,padding:crypto.constants.RSA_PKCS1_PSS_PADDING,
        saltLength:crypto.constants.RSA_PSS_SALTLEN_AUTO},sig);
    return {status:ok?'VERIFIED':'INVALID',reason:ok?null:'CRYPTO_SIGNATURE_INVALID'};
  } catch (e) { return {status:'INVALID',reason:'CRYPTO_SIGNATURE_INVALID'}; }
}
function verifyRole(root, candidate) {
  const role = root.obj.signed.roles.root;
  const keys = root.obj.signed.keys;
  const envelope = new Map();
  for (const s of candidate.obj.signatures) {
    check(s && typeof s.keyid === 'string' && typeof s.sig === 'string',
          'BAD_SIGNATURE_ENVELOPE');
    if (!envelope.has(s.keyid)) envelope.set(s.keyid,[]);
    envelope.get(s.keyid).push(s.sig);
  }
  const verified = [], unknown = [], invalid = [];
  for (const keyid of role.keyids) {
    const signatures = envelope.get(keyid) || [];
    if (!signatures.length) continue;
    const verdicts = signatures.map(sig =>
      verifySignature(keys[keyid],candidate.signedBytes,sig));
    if (verdicts.some(v => v.status === 'VERIFIED')) verified.push(keyid);
    else if (verdicts.some(v => v.status === 'UNKNOWN')) unknown.push(keyid);
    else invalid.push(keyid);
  }
  const threshold = role.threshold;
  const status = verified.length >= threshold ? 'SUFFICIENT' :
    verified.length + unknown.length >= threshold ? 'UNKNOWN' : 'INSUFFICIENT';
  return {
    authority_root_version:root.version,threshold,
    verified_unique_keyids:verified.sort(),unknown_unique_keyids:unknown.sort(),
    invalid_unique_keyids:invalid.sort(),status,
    duplicate_envelope_keyids: [...envelope.values()].reduce(
      (acc,sigs)=>acc+Math.max(0,sigs.length-1),0),
  };
}
function edge(old,candidate) {
  const oldProof = verifyRole(old,candidate);
  const newProof = verifyRole(candidate,candidate);
  const adjacent = candidate.version === old.version + 1;
  let effect;
  if (!adjacent) effect='KEEP_TRUST_ROOT';
  else if (oldProof.status==='SUFFICIENT' && newProof.status==='SUFFICIENT')
    effect='ADVANCE_TRUST_ROOT';
  else if (oldProof.status==='UNKNOWN' || newProof.status==='UNKNOWN')
    effect='MODEL_UNSUPPORTED';
  else effect='KEEP_TRUST_ROOT';
  return {
    from_state:'trusted-root-'+old.version,
    action:'submit-root-'+candidate.version,
    candidate_source_sha256:candidate.hash,
    candidate_canonical_signed_sha256:candidate.signedHash,
    version_contiguous:adjacent,
    old_authority:oldProof,new_authority:newProof,
    derived_effect:effect,
    to_state:effect==='MODEL_UNSUPPORTED'?null:
      'trusted-root-'+(effect==='ADVANCE_TRUST_ROOT'?candidate.version:old.version),
    native_oracle_called:false,
  };
}
function build(inventoryFile,rootDir) {
  const pins=inventory(inventoryFile), roots=new Map();
  for(let n=1;n<=8;n++) roots.set(n,readRoot(rootDir,n,pins));
  const states=[],transitions=[],keySchemes=new Set();
  for(let n=1;n<=8;n++){
    const root=roots.get(n),role=root.obj.signed.roles.root;
    states.push({
      state:'trusted-root-'+n, source_sha256:root.hash,
      trusted_role_threshold:role.threshold,
      trusted_role_keyids:[...role.keyids].sort(),
      lawful_source_provenance:'PINNED_BOTTLEROCKET_PRODUCTION_ROOT',
    });
    for(const key of Object.values(root.obj.signed.keys))
      keySchemes.add(String(key.keytype)+'/'+String(key.scheme));
    for(let m=2;m<=8;m++)transitions.push(edge(root,roots.get(m)));
  }
  check(states.length===8 && transitions.length===56,'WRONG_GRID_SIZE');
  const counts={};
  for(const transition of transitions){
    counts[transition.derived_effect]=(counts[transition.derived_effect]||0)+1;
    if(transition.to_state)
      check(states.some(s=>s.state===transition.to_state),'C3_NOT_CLOSED');
  }
  return {
    schema:'eeq-r1b-tuf-source-crypto-transition-v1',
    evidence_class:'PRODUCTION_HISTORY_SOURCE_DERIVED_DEVELOPMENT',
    registered_states:8,registered_actions:7,grid_cells:56,
    action_names:Array.from({length:7},(_,i)=>'submit-root-'+(i+2)),
    states,transitions,
    summary:{
      ...counts,complete_registered_graph:!counts.MODEL_UNSUPPORTED,
      key_schemes:[...keySchemes].sort(),
      native_oracle_calls:0,native_outcomes_read:false,new_g5_cases:0,
    },
    limitations:[
      'Previously known TUF development roots, NOT an unseen native family',
      'Only registered fixed source root proposals, not arbitrary root metadata',
      'Signed root threshold and version logic only; no expiry/full updater semantics',
      'No claim of v2 quotient or native A/B contrast at this stage',
    ],
  };
}
if (require.main===module){
  if(process.argv.length!==5){
    console.error('usage: node tuf_trust_transition_extractor.js INVENTORY ROOT_DIR OUTPUT');
    process.exit(64);
  }
  try{
    const out=build(process.argv[2],process.argv[3]);
    fs.writeFileSync(process.argv[4],JSON.stringify(out,null,2)+'\n');
    console.log(JSON.stringify({
      states:out.registered_states,actions:out.registered_actions,
      grid:out.grid_cells,...out.summary}));
  }catch(e){console.error(e.stack||String(e));process.exit(2);}
}
module.exports={canon,verifySignature,verifyRole,edge,build,hash,publicKey};
