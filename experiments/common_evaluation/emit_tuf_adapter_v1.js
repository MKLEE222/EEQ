#!/usr/bin/env node
'use strict';

/*
Emit eeq-adapter-v1 instances for the Bottlerocket production root carrier.

The adapter is built from frozen production root bytes plus the G5 semantic
signature. Native labels are not consulted during adapter construction.
*/
const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const { Metadata, MetadataKind }=require('@tufjs/models');

const DOMAIN='TUF:bottlerocket-root';

function sha256(buf){return crypto.createHash('sha256').update(buf).digest('hex');}
function readRoot(dir,v){
  const bytes=fs.readFileSync(path.join(dir, `${v}.root.json`));
  const raw=JSON.parse(bytes.toString('utf8'));
  const md=Metadata.fromJSON(MetadataKind.Root, raw);
  return {bytes,raw,md,sha256:sha256(bytes)};
}
function validSigners(delegator,candidate){
  const role=delegator.signed.roles.root;
  const out=[];
  for(const kid of role.keyIDs){
    const key=delegator.signed.keys[kid];
    if(!key) continue;
    try{key.verifySignature(candidate); out.push(kid);}catch(_){}
  }
  return out.sort();
}
function eq(a,b){return JSON.stringify([...a].sort())===JSON.stringify([...b].sort());}

function adapterFor(caseObj, prev, cand){
  const sig=caseObj.signature;
  const s=sig.pre_action_state;

  if(cand.sha256!==s.candidate_signed_bytes_sha256)
    throw new Error(`candidate hash mismatch for ${caseObj.semantic_id}`);
  if(!eq(prev.md.signed.roles.root.keyIDs,s.trusted_root_keyids))
    throw new Error(`trusted root key IDs mismatch for ${caseObj.semantic_id}`);
  if(prev.md.signed.roles.root.threshold!==s.trusted_root_threshold)
    throw new Error(`trusted root threshold mismatch for ${caseObj.semantic_id}`);
  if(!eq(cand.md.signed.roles.root.keyIDs,s.candidate_root_keyids))
    throw new Error(`candidate root key IDs mismatch for ${caseObj.semantic_id}`);
  if(cand.md.signed.roles.root.threshold!==s.candidate_root_threshold)
    throw new Error(`candidate root threshold mismatch for ${caseObj.semantic_id}`);

  const previousSigners=validSigners(prev.md,cand.md);
  const selfSigners=validSigners(cand.md,cand.md);
  const previousSatisfied=previousSigners.length>=prev.md.signed.roles.root.threshold;
  const selfSatisfied=selfSigners.length>=cand.md.signed.roles.root.threshold;

  return {
    schema_version:'eeq-adapter-v1',
    validity_boundary:{V0_lawful_information:true},
    C1_support_coverage:{
      claims:[
        'current-trust-authorizes-candidate',
        'candidate-qualifies-as-next-trust-anchor'
      ],
      support_items:[
        {
          id:'candidate-by-previous-root-signatures',
          source_identity:`production-root-${prev.md.signed.version}`,
          provenance:'Bottlerocket production root chain'
        },
        {
          id:'candidate-self-signatures',
          source_identity:`production-root-${cand.md.signed.version}`,
          provenance:'Bottlerocket production root chain'
        }
      ],
      compatibility:[
        {
          claim:'current-trust-authorizes-candidate',
          support:'candidate-by-previous-root-signatures',
          compatible:true
        },
        {
          claim:'candidate-qualifies-as-next-trust-anchor',
          support:'candidate-self-signatures',
          compatible:true
        }
      ]
    },
    C2_qualification_fidelity:{
      qualification_predicates:[
        {
          id:'previous-root-threshold-satisfied',
          support:'candidate-by-previous-root-signatures',
          threshold:prev.md.signed.roles.root.threshold,
          authorized_signers:previousSigners,
          value:previousSatisfied
        },
        {
          id:'candidate-self-threshold-satisfied',
          support:'candidate-self-signatures',
          threshold:cand.md.signed.roles.root.threshold,
          authorized_signers:selfSigners,
          value:selfSatisfied
        }
      ],
      authentication_predicates:[
        {
          id:'candidate-signatures-valid-under-previous-root',
          support:'candidate-by-previous-root-signatures',
          verified_signers:previousSigners
        },
        {
          id:'candidate-signatures-valid-under-candidate-root',
          support:'candidate-self-signatures',
          verified_signers:selfSigners
        }
      ],
      claim_binding:[
        {
          claim:'current-trust-authorizes-candidate',
          support:'candidate-by-previous-root-signatures',
          candidate_root_sha256:cand.sha256,
          candidate_version:cand.md.signed.version
        },
        {
          claim:'candidate-qualifies-as-next-trust-anchor',
          support:'candidate-self-signatures',
          candidate_root_sha256:cand.sha256,
          candidate_version:cand.md.signed.version
        }
      ]
    },
    C3_transition_objective_fidelity:{
      actions:[sig.registered_action],
      successor_relation:{
        from_version:prev.md.signed.version,
        to_version:cand.md.signed.version,
        version_adjacent:cand.md.signed.version===prev.md.signed.version+1
      },
      post_action_observations:{},
      continuation_contract:{
        contract_id:sig.future_contract,
        next_trust_root_sha256:cand.sha256,
        next_trust_keyids:[...cand.md.signed.roles.root.keyIDs].sort(),
        next_trust_threshold:cand.md.signed.roles.root.threshold
      },
      native_action_vocabulary:sig.native_action_vocabulary
    }
  };
}

function main(){
  const ledgerPath=process.argv[2], rootsDir=process.argv[3], outPath=process.argv[4];
  if(!ledgerPath||!rootsDir||!outPath){
    console.error('usage: emit_tuf_adapter_v1.js LEDGER ROOTS_DIR OUT_JSON');
    process.exit(64);
  }
  const ledger=JSON.parse(fs.readFileSync(ledgerPath,'utf8'));
  const cases=ledger.cases.filter(c=>c.signature.semantic_domain===DOMAIN);
  if(cases.length!==7) throw new Error(`expected 7 TUF cases, got ${cases.length}`);

  const roots={};
  const byHash={};
  for(let v=1;v<=8;v++){
    roots[v]=readRoot(rootsDir,v);
    byHash[roots[v].sha256]=v;
  }

  const rows=[];
  for(const c of cases){
    const candidateHash=c.signature.pre_action_state.candidate_signed_bytes_sha256;
    const to=byHash[candidateHash];
    if(!to || to<2) throw new Error(`cannot map candidate root hash for ${c.semantic_id}`);
    const adapter=adapterFor(c,roots[to-1],roots[to]); // built before label is copied
    rows.push({
      semantic_id:c.semantic_id,
      domain:DOMAIN,
      adapter,
      native_action:c.native_action
    });
  }
  rows.sort((a,b)=>a.semantic_id.localeCompare(b.semantic_id));
  fs.writeFileSync(outPath,JSON.stringify({
    schema:'eeq-adapter-instance-set-v1',
    adapter_source:'production root bytes + @tufjs/models@3.0.1 signature verification',
    rows
  },null,2)+'\n');
  console.log(JSON.stringify({rows:rows.length,domain:DOMAIN}));
}
main();
