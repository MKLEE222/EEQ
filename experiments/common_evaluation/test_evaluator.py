#!/usr/bin/env python3
from evaluate_representations import evaluate
rows=[
 {"native_action":"ACCEPT","representations":{"B1":{"x":0},"B10":{"z":0}}},
 {"native_action":"REJECT","representations":{"B1":{"x":0},"B10":{"z":1}}},
 {"native_action":"ACCEPT","representations":{"B1":{"x":1},"B10":{"z":2}}},
]
r={x['baseline']:x for x in evaluate(rows,'ACCEPT',['REJECT','ACCEPT'])}
assert r['B1']['classes']==2
assert r['B1']['mixed_classes']==1
assert r['B1']['runs_in_mixed_classes']==2
assert r['B1']['conflict_pairs']==1
assert abs(r['B1']['oracle_optimal_accuracy']-2/3)<1e-12
assert r['B10']['mixed_classes']==0
assert r['B10']['oracle_optimal_accuracy']==1.0
print('ok')
