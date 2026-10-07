#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { TrustedMetadataStore } = require('tuf-js/dist/store');

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function readRoot(dir, version) {
  const p = path.join(dir, `${version}.root.json`);
  const bytes = fs.readFileSync(p);
  return { path: p, bytes, json: JSON.parse(bytes.toString('utf8')) };
}

function canon(v) {
  if (Array.isArray(v)) return '[' + v.map(canon).join(',') + ']';
  if (v && typeof v === 'object') {
    return '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + canon(v[k])).join(',') + '}';
  }
  return JSON.stringify(v);
}

function runUpdate(store, candidate) {
  const t0 = process.hrtime.bigint();
  let nativeAction = 'REJECT';
  let errorClass = null;
  let errorMessage = null;
  try {
    store.updateRoot(candidate);
    nativeAction = 'ACCEPT';
  } catch (err) {
    errorClass = err && err.constructor ? err.constructor.name : typeof err;
    errorMessage = err && err.message ? err.message : String(err);
  }
  const t1 = process.hrtime.bigint();
  return {
    native_action: nativeAction,
    decision_ns: Number(t1 - t0),
    error_class: errorClass,
    error_message: errorMessage,
  };
}

function main() {
  const rootDir = process.argv[2];
  const outPath = process.argv[3];
  if (!rootDir || !outPath) {
    console.error('usage: run_tuf_invariant_controls.js ROOT_DIR OUT_JSON');
    process.exit(64);
  }

  const r1 = readRoot(rootDir, 1);
  const r2 = readRoot(rootDir, 2);
  const r3 = readRoot(rootDir, 3);

  // NC1: same parsed metadata, compact reserialization changes bytes only.
  const nc1Bytes = Buffer.from(JSON.stringify(r2.json), 'utf8');
  if (sha256(nc1Bytes) === sha256(r2.bytes)) {
    throw new Error('NC1 perturbation did not change bytes');
  }
  if (canon(JSON.parse(nc1Bytes.toString('utf8'))) !== canon(r2.json)) {
    throw new Error('NC1 changed parsed JSON value');
  }
  const nc1Store = new TrustedMetadataStore(r1.bytes);
  const nc1Native = runUpdate(nc1Store, nc1Bytes);

  // NC2: preserve signed payload exactly; permute only top-level signature order.
  if (!Array.isArray(r3.json.signatures) || r3.json.signatures.length < 2) {
    throw new Error('NC2 requires at least two root-3 signatures');
  }
  const nc2Json = JSON.parse(JSON.stringify(r3.json));
  nc2Json.signatures = [...nc2Json.signatures].reverse();
  if (canon(nc2Json.signed) !== canon(r3.json.signed)) {
    throw new Error('NC2 changed signed payload');
  }
  const nc2Bytes = Buffer.from(JSON.stringify(nc2Json), 'utf8');
  if (sha256(nc2Bytes) === sha256(r3.bytes)) {
    throw new Error('NC2 perturbation did not change bytes');
  }
  const nc2Store = new TrustedMetadataStore(r1.bytes);
  const setup = runUpdate(nc2Store, r2.bytes);
  if (setup.native_action !== 'ACCEPT') {
    throw new Error(`NC2 setup root 1->2 failed: ${setup.error_class}: ${setup.error_message}`);
  }
  const nc2Native = runUpdate(nc2Store, nc2Bytes);

  const controls = [
    {
      id: 'tuf-nc-json-reserialization',
      perturbation: 'compact JSON reserialization of production root 2',
      history: 'production root 1 -> perturbed root 2',
      expected_native_action: 'ACCEPT',
      original_sha256: sha256(r2.bytes),
      perturbed_sha256: sha256(nc1Bytes),
      bytes_changed: true,
      decision_relation_preserved: true,
      ...nc1Native,
    },
    {
      id: 'tuf-nc-signature-order',
      perturbation: 'reverse top-level signatures array of production root 3',
      history: 'production root 1 -> production root 2 -> perturbed root 3',
      expected_native_action: 'ACCEPT',
      original_sha256: sha256(r3.bytes),
      perturbed_sha256: sha256(nc2Bytes),
      bytes_changed: true,
      signed_payload_preserved: true,
      signature_count: r3.json.signatures.length,
      decision_relation_preserved: true,
      ...nc2Native,
    },
  ];

  const mismatches = controls.filter(x => x.native_action !== x.expected_native_action);
  const payload = {
    schema: 'eeq-tuf-section7-invariant-controls-v1',
    native_library: 'tuf-js@3.0.1',
    oracle_operation: 'TrustedMetadataStore.updateRoot',
    evidence_class: 'CONTROLLED_NATIVE',
    controls,
    summary: {
      controls: controls.length,
      matched: controls.length - mismatches.length,
      mismatches: mismatches.length,
      accepted: controls.filter(x => x.native_action === 'ACCEPT').length,
      rejected: controls.filter(x => x.native_action === 'REJECT').length,
    },
    g5_count_effect: 0,
    fifth_family_holdout: 'UNOPENED',
  };

  fs.writeFileSync(outPath, JSON.stringify(payload, null, 2) + '\n');
  console.log(JSON.stringify(payload.summary));

  if (mismatches.length) process.exit(2);
}

main();
