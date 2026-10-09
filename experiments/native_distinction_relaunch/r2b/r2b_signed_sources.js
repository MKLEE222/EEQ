#!/usr/bin/env node
'use strict';
/* R2-B SOURCE ONLY: deterministic TEST Ed25519 metadata; NO tuf-js calls. */
const fs=require('fs');
const path=require('path');
const crypto=require('crypto');
const {canon,edge,hash}=require('../tuf_trust_transition_extractor_r1b_v3.js');
const PKCS8=Buffer.from('302e020100300506032b657004220420','hex');
const SPKI=Buffer.from('302a300506032b6570032100','hex');
const NAMES=['root1.json','root2_A.json','root2_B.json','root3.json',
             'root3_bad_sig.json','targets_A.json','targets_B.json'];
const ACTIONS=['submit_root3_valid','submit_root3_bad_sig',
               'submit_root2_A_replay'];
const EXP='2035-01-01T00:00:00Z';
function ok(p,msg){if(!p)throw new Error(msg);}
function bytes(s){return Buffer.from(canon(s),'utf8');}
function key(role){
  ok(['root_signer','targets_A','targets_B','snapshot','timestamp'].includes(role),
     'UNDECLARED_TEST_KEY');
  const seed=crypto.createHash('sha256')
    .update('EEQ-R2B-TEST-KEYS-V1|'+role).digest();
  const priv=crypto.createPrivateKey({
    key:Buffer.concat([PKCS8,seed]),format:'der',type:'pkcs8'});
  const der=crypto.createPublicKey(priv).export({format:'der',type:'spki'});
  const pub={keytype:'ed25519',scheme:'ed25519',
    keyval:{public:der.subarray(-32).toString('hex')}};
  return {id:hash(bytes(pub)),pub,privateKey:priv};
}
function makeRoot(version,root,targets,snapshot,timestamp){
  const roleDefs={root,targets,snapshot,timestamp};
  return {
    _type:'root',spec_version:'1.0.0',version,expires:EXP,
    consistent_snapshot:true,
    keys:Object.fromEntries(Object.values(roleDefs).map(k=>[k.id,k.pub])),
    roles:Object.fromEntries(Object.entries(roleDefs).map(([name,k])=>
      [name,{keyids:[k.id],threshold:1}]))
  };
}
function makeTargets(){
  return {_type:'targets',spec_version:'1.0.0',version:1,
    expires:EXP,targets:{}};
}
function signed(signer,s){
  return {signed:s,signatures:[{
    keyid:signer.id,
    sig:crypto.sign(null,bytes(s),signer.privateKey).toString('hex')
  }]};
}
function clone(x){return JSON.parse(JSON.stringify(x));}
function rootObject(raw){
  const obj=JSON.parse(raw.toString('utf8'));
  return {version:obj.signed.version,obj,signedBytes:bytes(obj.signed),
    signedHash:hash(bytes(obj.signed)),hash:hash(raw),length:raw.length};
}
function crossCheck(root,targetEnvelope){
  const role=root.signed.roles.targets;
  const allowed=new Set(role.keyids);
  const verified=new Set();
  for(const s of targetEnvelope.signatures){
    if(!allowed.has(s.keyid))continue;
    const spec=root.signed.keys[s.keyid];
    const raw=Buffer.from(spec.keyval.public,'hex');
    ok(raw.length===32,'INVALID_TARGET_KEY_LENGTH');
    const publicKey=crypto.createPublicKey({
      key:Buffer.concat([SPKI,raw]),format:'der',type:'spki'});
    if(crypto.verify(null,bytes(targetEnvelope.signed),
      publicKey,Buffer.from(s.sig,'hex')))verified.add(s.keyid);
  }
  return {authorized:verified.size>=role.threshold,
    verified_keyids:[...verified].sort(),threshold:role.threshold,
    role_keyids:[...allowed].sort()};
}
function graphFor(rootFiles){
  const trusted={
    H_A:rootObject(rootFiles['root2_A.json']),
    H_B:rootObject(rootFiles['root2_B.json']),
    H_3:rootObject(rootFiles['root3.json'])
  };
  const proposal={
    submit_root3_valid:rootObject(rootFiles['root3.json']),
    submit_root3_bad_sig:rootObject(rootFiles['root3_bad_sig.json']),
    submit_root2_A_replay:rootObject(rootFiles['root2_A.json'])
  };
  const rows=[];
  for(const state of ['H_A','H_B','H_3']){
    for(const action of ACTIONS){
      const p=edge(trusted[state],proposal[action]);
      rows.push({state,action,expected_effect:p.derived_effect,
        expected_next:p.derived_effect==='MODEL_UNSUPPORTED'?null:
          p.derived_effect==='ADVANCE_TRUST_ROOT'?'H_3':state,
        candidate_source_sha256:proposal[action].hash,
        trusted_source_sha256:trusted[state].hash,
        old_verified_keyids:p.old_authority.verified_unique_keyids,
        new_verified_keyids:p.new_authority.verified_unique_keyids,
        source_only:true});
    }
  }
  return rows;
}
function trace(graph,start,r){
  const edges=Object.fromEntries(graph.map(x=>[x.state+'|'+x.action,x]));
  const out=[];
  function walk(state,prefix,effects,remaining){
    const current=ACTIONS.map(a=>edges[state+'|'+a].expected_effect);
    out.push({action_word:[...prefix],effect_path:[...effects],
      available_action_results:current});
    if(remaining===0)return;
    for(const a of ACTIONS){
      const e=edges[state+'|'+a];
      ok(e.expected_next,'UNRESOLVED_GRAPH_EDGE');
      walk(e.expected_next,[...prefix,a],
        [...effects,e.expected_effect],remaining-1);
    }
  }
  walk(start,[],[],r);
  return out;
}
function partitions(graph,maxHorizon){
  const states=['H_A','H_B','H_3'];
  const edges=Object.fromEntries(graph.map(x=>[x.state+'|'+x.action,x]));
  let before=null;
  const result=[];
  for(let r=0;r<=maxHorizon;r++){
    const keys={};
    for(const s of states){
      const obs=ACTIONS.map(a=>edges[s+'|'+a].expected_effect);
      keys[s]=JSON.stringify(r===0?obs:
        [obs,ACTIONS.map(a=>before[edges[s+'|'+a].expected_next])]);
    }
    const names=[...new Set(Object.values(keys))].sort();
    before=Object.fromEntries(states.map(s=>[s,names.indexOf(keys[s])]));
    const groups={};
    for(const s of states)(groups[before[s]]??=[]).push(s);
    result.push(Object.values(groups));
  }
  return result;
}
function generate(dir){
  fs.mkdirSync(dir,{recursive:true});
  const k={};
  for(const role of ['root_signer','targets_A','targets_B','snapshot','timestamp'])
    k[role]=key(role);
  const inputs={
    'root1.json':makeRoot(1,k.root_signer,k.targets_A,k.snapshot,k.timestamp),
    'root2_A.json':makeRoot(2,k.root_signer,k.targets_A,k.snapshot,k.timestamp),
    'root2_B.json':makeRoot(2,k.root_signer,k.targets_B,k.snapshot,k.timestamp),
    'root3.json':makeRoot(3,k.root_signer,k.targets_A,k.snapshot,k.timestamp)
  };
  const source={};
  for(const name of Object.keys(inputs)){
    source[name]=Buffer.from(JSON.stringify(signed(k.root_signer,inputs[name]))+'\n');
  }
  const broken=clone(JSON.parse(source['root3.json'].toString('utf8')));
  const sig=broken.signatures[0].sig;
  broken.signatures[0].sig=(sig[0]==='0'?'1':'0')+sig.slice(1);
  source['root3_bad_sig.json']=Buffer.from(JSON.stringify(broken)+'\n');
  source['targets_A.json']=Buffer.from(JSON.stringify(signed(k.targets_A,makeTargets()))+'\n');
  source['targets_B.json']=Buffer.from(JSON.stringify(signed(k.targets_B,makeTargets()))+'\n');
  ok(Object.keys(source).length===7 && NAMES.every(name=>source[name]),
    'FIXTURE_SOURCE_SET_INCOMPLETE');
  for(const name of NAMES)fs.writeFileSync(path.join(dir,name),source[name]);

  const root1=rootObject(source['root1.json']);
  const init=[
    edge(root1,rootObject(source['root2_A.json'])),
    edge(root1,rootObject(source['root2_B.json']))
  ];
  ok(init.every(x=>x.derived_effect==='ADVANCE_TRUST_ROOT'),
     'SOURCE_ONLY_SETUP_REJECTED');
  const cross={};
  for(const state of ['A','B']){
    cross[state]={};
    const r=JSON.parse(source['root2_'+state+'.json'].toString('utf8'));
    for(const t of ['A','B']){
      const target=JSON.parse(source['targets_'+t+'.json'].toString('utf8'));
      cross[state][t]=crossCheck(r,target);
    }
  }
  ok(cross.A.A.authorized&&!cross.A.B.authorized&&
     !cross.B.A.authorized&&cross.B.B.authorized,
     'NO_NONCOSMETIC_AUTHORIZATION_DIFFERENCE');

  const graph=graphFor(source);
  ok(graph.length===9 && graph.every(x=>x.expected_next!==null),
     'INCOMPLETE_REGISTERED_SOURCE_GRAPH');
  const a=trace(graph,'H_A',2),b=trace(graph,'H_B',2);
  ok(a.length===13&&b.length===13,'TRACE_ENUMERATION_INCOMPLETE');
  const files=Object.fromEntries(NAMES.map(name=>[
    name,{sha256:hash(source[name]),bytes:source[name].length}]));
  return {
    schema:'eeq-r2b-controlled-source-predictions-v1',
    evidence_class:'CONTROLLED_SIGNED_TEST_SOURCES',
    source_files:files,
    key_ids:Object.fromEntries(Object.entries(k).map(([role,v])=>[role,v.id])),
    no_private_key_artifacts:true,native_oracle_called:false,
    prior_native_outcomes_used:false,
    states:['H_A','H_B','H_3'],
    actions:ACTIONS,horizon:2,
    root1_source_only_setup_effects:init.map(x=>x.derived_effect),
    real_targets_qualification_cross_check:cross,
    true_authority_difference:
      inputs['root2_A.json'].roles.targets.keyids[0] !==
      inputs['root2_B.json'].roles.targets.keyids[0],
    frozen_contract:'ROOT_UPDATE_ONLY',
    registered_graph:graph,
    refinement_classes:partitions(graph,2),
    source_trace_A:a,source_trace_B:b,
    source_only_root_update_traces_equal:JSON.stringify(a)===JSON.stringify(b),
    baseline_b9_expected_same_root_role_projection:true,
    r2_b_native_verified:false,r4_independent_advantage:false,
    status:'SOURCE_ONLY_FEASIBILITY_NOT_NATIVE_RESULT'
  };
}
if(require.main===module){
  if(process.argv.length!==3){console.error('usage: node r2b_signed_sources.js DEST');process.exit(64);}
  try {
    const p=generate(process.argv[2]);
    fs.writeFileSync(path.join(process.argv[2],'SOURCE_ONLY_PREDICTIONS.json'),
      JSON.stringify(p,null,2)+'\n');
    console.log(JSON.stringify({
      source_count:Object.keys(p.source_files).length,grid:p.registered_graph.length,
      pair_targets_auth_cross:[
        p.real_targets_qualification_cross_check.A.A.authorized,
        p.real_targets_qualification_cross_check.A.B.authorized,
        p.real_targets_qualification_cross_check.B.A.authorized,
        p.real_targets_qualification_cross_check.B.B.authorized],
      trace_count_per_history:p.source_trace_A.length,
      root_update_traces_equal:p.source_only_root_update_traces_equal,
      quotient_classes:p.refinement_classes.map(x=>x.length),
      native_oracle_called:false
    }));
  }catch(e){console.error(e.stack||String(e));process.exit(2);}
}
module.exports={generate,publicTestKey:key,makeRoot,makeTargets,graphFor,trace,
  partitions,crossCheck};
