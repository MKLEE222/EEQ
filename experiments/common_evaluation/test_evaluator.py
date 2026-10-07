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
assert r['B1']['mixed_case_count']==2
assert r['B1']['runs_in_mixed_classes']==2
assert r['B1']['conflict_pairs']==1
assert abs(r['B1']['oracle_optimal_accuracy']-2/3)<1e-12
assert r['B1']['zero_error_recoverable'] is False
assert r['B1']['confusion_matrix']['ACCEPT']['REJECT']==1
assert r['B10']['mixed_classes']==0
assert r['B10']['zero_error_recoverable'] is True
assert r['B10']['oracle_optimal_accuracy']==1.0

# Frozen G4 default tie policy is lexicographic native-label order.
tie_rows=[
 {"native_action":"ZETA","representations":{"R":{"x":0}}},
 {"native_action":"ALPHA","representations":{"R":{"x":0}}},
]
t=evaluate(tie_rows,'ALPHA',None)[0]
assert t['tie_policy']=='lexicographic_native_label'
assert t['tie_classes']==1
assert t['confusion_matrix']['ALPHA']['ALPHA']==1
assert t['confusion_matrix']['ZETA']['ALPHA']==1
assert t['mixed_class_label_histograms'][0]['label_counts']=={'ALPHA':1,'ZETA':1}
print('ok')
