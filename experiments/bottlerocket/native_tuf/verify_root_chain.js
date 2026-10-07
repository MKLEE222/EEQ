#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// tuf-js@3.0.1 does not export TrustedMetadataStore from its public index,
// but its pinned package ships the implementation used by Updater.loadRoot().
// Using this exact store keeps root-transition verification inside the native
// tuf-js client semantics rather than reimplementing TUF in this experiment.
const { TrustedMetadataStore } = require('tuf-js/dist/store');

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function readRoot(rootDir, version) {
  const p = path.join(rootDir, `${version}.root.json`);
  const data = fs.readFileSync(p);
  const parsed = JSON.parse(data.toString('utf8'));
  return { path: p, data, parsed, sha256: sha256(data) };
}

function rootRoleSummary(parsed) {
  const signed = parsed.signed || {};
  const roles = signed.roles || {};
  const rootRole = roles.root || {};
  return {
    version: signed.version,
    expires: signed.expires,
    root_threshold: rootRole.threshold,
    root_keyids: Array.isArray(rootRole.keyids) ? [...rootRole.keyids].sort() : [],
    all_keyids: Object.keys(signed.keys || {}).sort(),
    consistent_snapshot: signed.consistent_snapshot,
  };
}

function symmetricDifference(a, b) {
  const A = new Set(a);
  const B = new Set(b);
  return [...new Set([...a.filter(x => !B.has(x)), ...b.filter(x => !A.has(x))])].sort();
}

function main() {
  const rootDir = process.argv[2];
  const outPath = process.argv[3];
  if (!rootDir || !outPath) {
    console.error('usage: verify_root_chain.js ROOT_DIR OUT_JSON');
    process.exit(64);
  }

  const first = readRoot(rootDir, 1);
  const store = new TrustedMetadataStore(first.data);
  if (store.root.signed.version !== 1) {
    throw new Error(`initial trusted root version is ${store.root.signed.version}, expected 1`);
  }

  const rows = [];
  let previous = first;

  for (let version = 2; version <= 8; version++) {
    const current = readRoot(rootDir, version);
    const before = rootRoleSummary(previous.parsed);
    const candidate = rootRoleSummary(current.parsed);
    const startedNs = process.hrtime.bigint();
    let nativeAction = 'REJECT';
    let errorClass = null;
    let errorMessage = null;

    try {
      const accepted = store.updateRoot(current.data);
      if (accepted.signed.version !== version) {
        throw new Error(`trusted version after update is ${accepted.signed.version}, expected ${version}`);
      }
      nativeAction = 'ACCEPT';
    } catch (err) {
      errorClass = err && err.constructor ? err.constructor.name : typeof err;
      errorMessage = err && err.message ? err.message : String(err);
    }

    const endedNs = process.hrtime.bigint();
    rows.push({
      case_id: `bottlerocket-root-${version - 1}-to-${version}`,
      family: 'TUF',
      environment: 'bottlerocket-aws-k8s-1.35-x86_64',
      evidence_class: 'PRODUCTION_HISTORY',
      action: 'ROOT_UPDATE',
      from_version: version - 1,
      to_version: version,
      future_contract: 'TUF_ROOT_CHAIN_CONTINUATION',
      native_action_vocabulary: ['ACCEPT', 'REJECT'],
      native_action: nativeAction,
      oracle: 'tuf-js@3.0.1 TrustedMetadataStore.updateRoot',
      source_sha256: {
        from_root: previous.sha256,
        to_root: current.sha256,
      },
      pre_action_state: {
        trusted_root_version: before.version,
        trusted_root_threshold: before.root_threshold,
        trusted_root_keyids: before.root_keyids,
      },
      candidate_state: {
        root_version: candidate.version,
        root_threshold: candidate.root_threshold,
        root_keyids: candidate.root_keyids,
        expires: candidate.expires,
        consistent_snapshot: candidate.consistent_snapshot,
      },
      continuation_delta: {
        changed_root_role_keyids: symmetricDifference(before.root_keyids, candidate.root_keyids),
        changed_all_keyids: symmetricDifference(before.all_keyids, candidate.all_keyids),
        threshold_changed: before.root_threshold !== candidate.root_threshold,
      },
      decision_ns: Number(endedNs - startedNs),
      error_class: errorClass,
      error_message: errorMessage,
    });

    if (nativeAction !== 'ACCEPT') {
      fs.writeFileSync(outPath, JSON.stringify({
        schema: 'eeq-bottlerocket-native-root-chain-v1',
        native_library: 'tuf-js@3.0.1',
        initial_anchor: {
          version: 1,
          sha256: first.sha256,
          self_verified_by_constructor: true,
        },
        rows,
        summary: {
          transitions: rows.length,
          accepted: rows.filter(r => r.native_action === 'ACCEPT').length,
          rejected: rows.filter(r => r.native_action === 'REJECT').length,
          complete: false,
        },
      }, null, 2) + '\n');
      throw new Error(`native root transition ${version - 1}->${version} rejected: ${errorClass}: ${errorMessage}`);
    }

    previous = current;
  }

  if (store.root.signed.version !== 8) {
    throw new Error(`final trusted root is ${store.root.signed.version}, expected 8`);
  }

  const payload = {
    schema: 'eeq-bottlerocket-native-root-chain-v1',
    protocol_note: 'Seven adjacent production-authored root transitions. HTTP 403 for root 9 is a source boundary, not a rejected transition.',
    native_library: 'tuf-js@3.0.1',
    oracle_operation: 'TrustedMetadataStore.updateRoot',
    initial_anchor: {
      version: 1,
      sha256: first.sha256,
      self_verified_by_constructor: true,
    },
    rows,
    summary: {
      transitions: rows.length,
      accepted: rows.filter(r => r.native_action === 'ACCEPT').length,
      rejected: rows.filter(r => r.native_action === 'REJECT').length,
      final_trusted_root_version: store.root.signed.version,
      complete: true,
    },
  };

  fs.writeFileSync(outPath, JSON.stringify(payload, null, 2) + '\n');
  console.log(JSON.stringify(payload.summary));
}

main();
