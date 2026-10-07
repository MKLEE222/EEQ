#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { Metadata, MetadataKind } = require('@tufjs/models');

const NA = '__NOT_APPLICABLE__';
const IDS = [...Array(11).keys()].map(i => 'B' + i)
  .concat([...Array(8).keys()].map(i => 'O' + (i + 1)));

function canonical(v) {
  return JSON.stringify(v, Object.keys(v || {}).sort());
}

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function readJSON(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function validRootSigners(delegator, candidate) {
  const role = delegator.signed.roles.root;
  const out = [];
  for (const kid of role.keyIDs) {
    const key = delegator.signed.keys[kid];
    if (!key) continue;
    try {
      key.verifySignature(candidate);
      out.push(kid);
    } catch (_) {
      // Invalid signatures are observations, not fatal to representation extraction.
    }
  }
  return out.sort();
}

function rootView(md, raw, digest) {
  const role = md.signed.roles.root;
  return {
    version: md.signed.version,
    root_threshold: role.threshold,
    root_keyids: [...role.keyIDs].sort(),
    all_keyids: Object.keys(md.signed.keys).sort(),
    signature_keyids: Object.keys(md.signatures).sort(),
    consistent_snapshot: md.signed.consistentSnapshot,
    signed_bytes_sha256: digest,
    expires: md.signed.expires.toISOString(),
  };
}

function diff(a, b) {
  const A = new Set(a), B = new Set(b);
  return [...new Set([...a.filter(x => !B.has(x)), ...b.filter(x => !A.has(x))])].sort();
}

function buildState(prevPath, candPath) {
  const prevBytes = fs.readFileSync(prevPath);
  const candBytes = fs.readFileSync(candPath);
  const prevRaw = JSON.parse(prevBytes.toString('utf8'));
  const candRaw = JSON.parse(candBytes.toString('utf8'));
  const prev = Metadata.fromJSON(MetadataKind.Root, prevRaw);
  const cand = Metadata.fromJSON(MetadataKind.Root, candRaw);
  const prevValid = validRootSigners(prev, cand);
  const selfValid = validRootSigners(cand, cand);
  const p = rootView(prev, prevRaw, sha256(prevBytes));
  const c = rootView(cand, candRaw, sha256(candBytes));
  return {
    previous: p,
    candidate: c,
    qualification: {
      valid_previous_root_signers: prevValid,
      valid_candidate_root_signers: selfValid,
      previous_root_authorized: prevValid.length >= p.root_threshold,
      candidate_self_authorized: selfValid.length >= c.root_threshold,
    },
    continuation: {
      version_adjacent: c.version === p.version + 1,
      next_trust_keyids: c.root_keyids,
      next_trust_threshold: c.root_threshold,
    },
    delta: {
      root_role_keyids_changed: diff(p.root_keyids, c.root_keyids),
      all_keyids_changed: diff(p.all_keyids, c.all_keyids),
      threshold_changed: p.root_threshold !== c.root_threshold,
      signature_count: c.signature_keyids.length,
    },
  };
}

function reps(s) {
  const p = s.previous, c = s.candidate, q = s.qualification, d = s.delta, k = s.continuation;
  const r = {};
  for (const id of IDS) r[id] = NA;

  r.B0 = {
    previous: p, candidate: c, qualification: q, continuation: k, delta: d,
  };
  r.B1 = {
    candidate_version: c.version,
    candidate_root_threshold: c.root_threshold,
    candidate_root_keyids: c.root_keyids,
    candidate_signature_keyids: c.signature_keyids,
    candidate_signed_bytes_sha256: c.signed_bytes_sha256,
  };
  r.B2 = {
    valid_previous_signature_count: q.valid_previous_root_signers.length,
    valid_self_signature_count: q.valid_candidate_root_signers.length,
    previous_root_authorized: q.previous_root_authorized,
    candidate_self_authorized: q.candidate_self_authorized,
  };
  r.B3 = {
    previous_root_threshold: p.root_threshold,
    previous_root_keyids: p.root_keyids,
    candidate_root_threshold: c.root_threshold,
    candidate_root_keyids: c.root_keyids,
  };
  r.B4 = {
    from_version: p.version,
    to_version: c.version,
    previous_sha256: p.signed_bytes_sha256,
    candidate_sha256: c.signed_bytes_sha256,
  };
  r.B5 = {
    previous_root_threshold: p.root_threshold,
    previous_root_keyids: p.root_keyids,
    candidate_root_threshold: c.root_threshold,
    candidate_root_keyids: c.root_keyids,
    from_version: p.version,
    to_version: c.version,
    previous_sha256: p.signed_bytes_sha256,
    candidate_sha256: c.signed_bytes_sha256,
  };
  r.B6 = {
    previous: {
      version: p.version, root_threshold: p.root_threshold, root_keyids: p.root_keyids,
      signed_bytes_sha256: p.signed_bytes_sha256,
    },
    candidate: {
      version: c.version, root_threshold: c.root_threshold, root_keyids: c.root_keyids,
      signature_keyids: c.signature_keyids, signed_bytes_sha256: c.signed_bytes_sha256,
    },
    valid_previous_root_signers: q.valid_previous_root_signers,
    valid_candidate_root_signers: q.valid_candidate_root_signers,
  };
  r.B7 = {
    key_rotation_count: d.root_role_keyids_changed.length,
    all_key_rotation_count: d.all_keyids_changed.length,
    threshold_changed: d.threshold_changed,
    signature_count: d.signature_count,
    version_gap: c.version - p.version,
  };
  r.B8 = {
    candidate_version: c.version,
    candidate_root_threshold: c.root_threshold,
    candidate_root_key_count: c.root_keyids.length,
    candidate_signature_count: c.signature_keyids.length,
    candidate_consistent_snapshot: c.consistent_snapshot,
  };
  r.B9 = {
    previous_root_authorized: q.previous_root_authorized,
    candidate_self_authorized: q.candidate_self_authorized,
    version_adjacent: k.version_adjacent,
  };
  r.B10 = {
    qualified_support: {
      previous_root: {
        threshold: p.root_threshold,
        authorized_signers: q.valid_previous_root_signers,
        satisfied: q.previous_root_authorized,
      },
      candidate_root: {
        threshold: c.root_threshold,
        authorized_signers: q.valid_candidate_root_signers,
        satisfied: q.candidate_self_authorized,
      },
    },
    claim_binding: {
      candidate_root_sha256: c.signed_bytes_sha256,
      candidate_version: c.version,
    },
    continuation_contract: {
      version_adjacent: k.version_adjacent,
      next_trust_keyids: k.next_trust_keyids,
      next_trust_threshold: k.next_trust_threshold,
    },
  };

  r.O1 = {
    previous_root_authorized: q.previous_root_authorized,
    candidate_self_authorized: q.candidate_self_authorized,
    version_adjacent: k.version_adjacent,
    previous_root_keyids: p.root_keyids,
    candidate_root_keyids: c.root_keyids,
  };
  r.O2 = {
    from_version: p.version,
    to_version: c.version,
    previous_root_threshold: p.root_threshold,
    previous_root_keyids: p.root_keyids,
    candidate_root_threshold: c.root_threshold,
    candidate_root_keyids: c.root_keyids,
    candidate_signature_keyids: c.signature_keyids,
  };
  r.O3 = {
    previous_root_authorized: q.previous_root_authorized,
    candidate_self_authorized: q.candidate_self_authorized,
    authorized_previous_signers: q.valid_previous_root_signers,
    authorized_candidate_signers: q.valid_candidate_root_signers,
    version_adjacent: k.version_adjacent,
  };
  r.O4 = {
    candidate_root_threshold: c.root_threshold,
    candidate_root_keyids: c.root_keyids,
    candidate_self_authorized: q.candidate_self_authorized,
    candidate_sha256: c.signed_bytes_sha256,
  };
  r.O5 = {
    previous: p,
    candidate: c,
    qualification: q,
  };
  r.O6 = {
    candidate_version: c.version,
    candidate_root_threshold: c.root_threshold,
    candidate_root_keyids: c.root_keyids,
    candidate_self_authorized: q.candidate_self_authorized,
    candidate_sha256: c.signed_bytes_sha256,
  };
  r.O7 = {
    previous_root_authorized: q.previous_root_authorized,
    valid_previous_root_signers: q.valid_previous_root_signers,
    version_adjacent: k.version_adjacent,
  };
  r.O8 = {
    previous_root_authorized: q.previous_root_authorized,
    valid_previous_root_signers: q.valid_previous_root_signers,
    previous_root_threshold: p.root_threshold,
  };
  return r;
}

function main() {
  const ledgerPath = process.argv[2];
  const rootsDir = process.argv[3];
  const outPath = process.argv[4];
  if (!ledgerPath || !rootsDir || !outPath) {
    console.error('usage: build_tuf_representations.js LEDGER ROOTS_DIR OUT_JSON');
    process.exit(64);
  }

  const ledger = readJSON(ledgerPath);
  const cases = new Map(
    ledger.cases
      .filter(c => c.signature.semantic_domain === 'TUF:bottlerocket-root')
      .map(c => [c.semantic_id, c])
  );
  const executions = ledger.executions.filter(e => e.source_artifact === 'bottlerocket' && e.status === 'SCORED');
  if (executions.length !== 7 || cases.size !== 7) {
    throw new Error(`expected seven scored Bottlerocket transitions, got executions=${executions.length} cases=${cases.size}`);
  }

  const rows = [];
  for (const e of executions.sort((a,b) => a.to_version - b.to_version)) {
    const c = cases.get(e.semantic_id);
    if (!c) throw new Error(`missing case for ${e.semantic_id}`);
    const state = buildState(
      path.join(rootsDir, `${e.from_version}.root.json`),
      path.join(rootsDir, `${e.to_version}.root.json`)
    );
    if (state.previous.version !== e.from_version || state.candidate.version !== e.to_version) {
      throw new Error('root version mismatch');
    }
    if (state.candidate.signed_bytes_sha256 !== c.signature.pre_action_state.candidate_signed_bytes_sha256) {
      throw new Error(`candidate hash mismatch for ${e.execution_id}`);
    }
    // Native action is joined only after representations are fully computed.
    rows.push({
      semantic_id: e.semantic_id,
      domain: 'TUF:bottlerocket-root',
      native_action: c.native_action,
      representations: reps(state),
      not_applicable_reasons: {},
      representation_source: {
        from_version: e.from_version,
        to_version: e.to_version,
        previous_sha256: state.previous.signed_bytes_sha256,
        candidate_sha256: state.candidate.signed_bytes_sha256,
      },
    });
  }

  fs.writeFileSync(outPath, JSON.stringify({
    schema: 'eeq-g4-tuf-representations-v1',
    status: 'development post-native/pre-matrix freeze; no native action used to construct representations',
    b10_status: 'adapter-state pilot; generic EEQ/WFC compiler integration pending',
    all_native_labels_same_warning: true,
    rows,
  }, null, 2) + '\n');
  console.log(JSON.stringify({rows: rows.length, ids: IDS.length, all_native_labels_same_warning: true}));
}

main();
