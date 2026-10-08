#!/usr/bin/env node
'use strict';

// G8 native-reference robustness only: NO EEQ method score is produced.
// The source inventory and scenario forecasts were frozen before this run.

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { TrustedMetadataStore } = require('tuf-js/dist/store');

function sha256(bytes) {
  return crypto.createHash('sha256').update(bytes).digest('hex');
}
function readRoot(dir, n) {
  return fs.readFileSync(path.join(dir, String(n) + '.root.json'));
}
function canon(x) {
  if (Array.isArray(x)) return '[' + x.map(canon).join(',') + ']';
  if (x !== null && typeof x === 'object') {
    return '{' + Object.keys(x).sort().map(k => JSON.stringify(k) + ':' + canon(x[k])).join(',') + '}';
  }
  return JSON.stringify(x);
}
function update(store, candidate) {
  const t0 = process.hrtime.bigint();
  let action = 'ACCEPT';
  let errorClass = null;
  let errorMessage = null;
  try {
    store.updateRoot(candidate);
  } catch (e) {
    action = 'REJECT';
    errorClass = e && e.constructor ? e.constructor.name : typeof e;
    errorMessage = e && e.message ? e.message : String(e);
  }
  return {
    native_action: action,
    decision_ns: Number(process.hrtime.bigint() - t0),
    error_class: errorClass,
    error_message: errorMessage
  };
}
function setup(bytes1, bytes2, bytes3) {
  const store = new TrustedMetadataStore(bytes1);
  const a = update(store, bytes2);
  const b = update(store, bytes3);
  if (a.native_action !== 'ACCEPT' || b.native_action !== 'ACCEPT') {
    throw new Error('FROZEN_PRODUCTION_CHAIN_SETUP_FAILURE: ' +
      JSON.stringify({from1to2:a, from2to3:b}));
  }
  return store;
}
function main() {
  const dir = process.argv[2];
  const output = process.argv[3];
  if (!dir || !output) {
    process.stderr.write('usage: run_tuf_g8_robustness.js ROOT_DIR OUTPUT\n');
    process.exit(64);
  }
  const b1 = readRoot(dir, 1);
  const b2 = readRoot(dir, 2);
  const b3 = readRoot(dir, 3);
  const b4 = readRoot(dir, 4);
  const original = JSON.parse(b4.toString('utf8'));
  const cases = [];

  // R3: top-level unsigned observation, unchanged signed data/signatures.
  const outer = JSON.parse(JSON.stringify(original));
  if (Object.prototype.hasOwnProperty.call(outer,'eeq_noncritical_observation')) {
    throw new Error('R3 source already contains frozen probe key');
  }
  outer.eeq_noncritical_observation = 'controlled-20261008';
  if (canon(outer.signed) !== canon(original.signed) ||
      canon(outer.signatures) !== canon(original.signatures)) {
    throw new Error('R3 unexpectedly altered signed data/signatures');
  }
  const bR3 = Buffer.from(JSON.stringify(outer),'utf8');
  if (sha256(bR3) === sha256(b4)) throw new Error('R3 unchanged bytes');
  cases.push({
    id:'R3',
    category:3,
    change:'outer auxiliary observation',
    g8_prediction:'PRESERVE_DECISION',
    expected_native_action:'ACCEPT',
    native_scored:true,
    original_sha256:sha256(b4),
    candidate_sha256:sha256(bR3),
    signed_payload_preserved:true,
    ...update(setup(b1,b2,b3),bR3)
  });

  // R4: empty signed.keys has no independently certified schema admission.
  // PREDECLARED UNSCORED irrespective of observed exception class.
  const missingKeys = JSON.parse(JSON.stringify(original));
  missingKeys.signed.keys = {};
  const bR4 = Buffer.from(JSON.stringify(missingKeys),'utf8');
  if (sha256(bR4) === sha256(b4)) throw new Error('R4 unchanged bytes');
  cases.push({
    id:'R4',
    category:4,
    change:'signed.keys replaced by empty object',
    g8_prediction:'INSUFFICIENT_EVIDENCE_REFUSE',
    expected_native_action:null,
    native_scored:false,
    unscored_reason:'INDEPENDENT_NATIVE_SCHEMA_ADMISSIBILITY_NOT_ESTABLISHED_BEFORE_SCORING',
    original_sha256:sha256(b4),
    candidate_sha256:sha256(bR4),
    ...update(setup(b1,b2,b3),bR4)
  });

  // R5: root-4 signed version is changed to 5 but signatures remain from 4.
  // Both sequence and cryptographic constraints can produce the rejection.
  const corrupt = JSON.parse(JSON.stringify(original));
  if (corrupt.signed.version !== 4) {
    throw new Error('R5 expected frozen signed root version 4');
  }
  corrupt.signed.version = 5;
  if (canon(corrupt.signatures) !== canon(original.signatures)) {
    throw new Error('R5 unexpectedly changed signatures');
  }
  const bR5 = Buffer.from(JSON.stringify(corrupt),'utf8');
  if (sha256(bR5) === sha256(b4)) throw new Error('R5 unchanged bytes');
  cases.push({
    id:'R5',
    category:5,
    change:'root4 signed.version 4 to 5 without resigning',
    g8_prediction:'INSUFFICIENT_EVIDENCE_REFUSE',
    expected_native_action:'REJECT',
    native_scored:true,
    original_sha256:sha256(b4),
    candidate_sha256:sha256(bR5),
    ...update(setup(b1,b2,b3),bR5)
  });

  // R10: replay production root2 into a trusted store already at root3.
  cases.push({
    id:'R10',
    category:10,
    change:'trusted root3 gets prior production root2',
    g8_prediction:'INSUFFICIENT_EVIDENCE_REFUSE',
    expected_native_action:'REJECT',
    native_scored:true,
    original_sha256:sha256(b2),
    candidate_sha256:sha256(b2),
    bytes_equal_by_design:true,
    ...update(setup(b1,b2,b3),b2)
  });

  // R6 is an unavailable source, not an invalid TUF candidate.
  cases.push({
    id:'R6',
    category:6,
    change:'no candidate bytes available',
    g8_prediction:'INSUFFICIENT_EVIDENCE_REFUSE',
    expected_native_action:null,
    native_scored:false,
    observation_status:'SOURCE_UNAVAILABLE',
    native_operation_invoked:false,
    native_action:null,
    decision_ns:null,
    error_class:null,
    error_message:null
  });

  const scored = cases.filter(x => x.native_scored);
  const matched = scored.filter(x => x.native_action === x.expected_native_action);
  const bad = scored.filter(x => x.native_action !== x.expected_native_action);
  const result = {
    schema:'eeq-tuf-g8-controlled-native-robustness-v1',
    evidence_class:'CONTROLLED_NATIVE',
    library:'tuf-js@3.0.1',
    operation:'TrustedMetadataStore.updateRoot',
    frozen_history:'Bottlerocket roots 1->2->3, candidate rooted at 4',
    scenario_predictions_frozen_before_native:true,
    method_scoring_performed:false,
    source_roots_sha256:{
      '1':sha256(b1),'2':sha256(b2),'3':sha256(b3),'4':sha256(b4)
    },
    cases,
    summary:{
      scenarios:cases.length,
      native_scored:scored.length,
      native_matched:matched.length,
      native_mismatches:bad.length,
      native_unscored:cases.length-scored.length,
      unavailable:cases.filter(x => x.observation_status === 'SOURCE_UNAVAILABLE').length,
    },
    g5_count_effect:0,
    holdout_sources_consumed:false
  };
  fs.writeFileSync(output, JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result.summary));
  // Native mismatches are scientific data, not infrastructure failures.
}
main();
