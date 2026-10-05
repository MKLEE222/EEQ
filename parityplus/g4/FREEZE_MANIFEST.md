# G4 freeze manifest

Semantic protocol blob:
- parityplus/g4/UNIFIED_PROTOCOL_FREEZE_v1.md
- git blob: 3eeaeeb828d2fcf7ec4487da06489fee3146c920

Adapter schema blob:
- parityplus/g4/adapter_schema_v1.json
- git blob: 5b25e074f26f1c0b02ec4aa65c32ff9bccf51631

Baseline/omission taxonomy blob:
- parityplus/g4/baseline_taxonomy_v1.json
- git blob: 29ff507d5abace5b4153f814d7fad226d8c0cc13

All three blobs existed before this manifest commit. Any semantic replacement of these blobs after the freeze is a protocol amendment and must receive a new protocol version plus PROTOCOL_BREAK ledger entry.

GitHub was inspected before this freeze and is a development family. The final family-level holdout must be a fifth, previously unopened semantic family.
