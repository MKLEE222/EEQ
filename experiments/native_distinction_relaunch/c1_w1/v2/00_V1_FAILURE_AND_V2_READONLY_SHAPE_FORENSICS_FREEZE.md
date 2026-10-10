# C1-W1 V1 FAILURE retained; V2 read-only native-source-shape forensics freeze

Date 2026-10-10, new branch `eeq-c1-w1-v2-postnative-shape-audit-20261010`.
Parent V1 prescored candidate branch commit `50764e8559efd5452c3501940279e6c1a8ec1445`.
**This protocol is POST-NATIVE by construction. It is a forensic diagnostic, not an independently pre-scored native gate.**

## First frozen V1 execution and irreversible disposition

W1 V1 first/only actual native trial: GitHub Actions [38029036440](https://github.com/MKLEE222/EEQ/actions/runs/38029036440), execution commit `af8ea13452eaec52bed1a343443eeffad3fb53e3`.
- Both original G4/B10/native Git blob locks passed.
- 48/48 pre-native synthetic and parser tests passed; source-only previous forecast SHA verified **after** native raw save.
- The real Kubernetes WATCH transport captured **3/3** registered source events, **8/8** unfiltered raw collection LIST snapshots, **3/3** genuine API source additions/deletion, and **2/2** WATCH channels with no reported transport error.
- The original independently frozen join-only verifier returned `REFUSE_COLLECTION_ITEM_SHAPE`. Thus V1 Actions conclusion **FAILURE**, NOT `C1_W1...PASS`. This is a real native-vs-synthetic serialization mismatch caught by a strict scientific gate.
- Native raw artifact ID **11661372658**, `eeq-c1-w1-native-two-class-watch-raw-and-scoped-verdict`, outer ZIP SHA256 `9d2dc931d239f4a269da00038d322c5f795001afec8da22d3b311360740af94d` from GitHub artifact upload. It contains the original untouched `C1_W1_RAW_NATIVE_HTTP_WATCH.json` and `C1_W1_NATIVE_HASH_BEFORE_SOURCE_JOIN.txt`, among archived controls.
- Source-only forecast artifact **11660314996**, ZIP SHA256 `202d392b01decf7e42d87429305d2b629ee8029ad91f8daa08afdf75068c1863`; manifest JSON SHA256 `7dddf471c1c0fc53b388c47b32cebbb09caa5f0d8ca377567a9bf23dbc960304`; forecast JSON SHA256 `d97aa16cb8b33532e50767f4d452c58db8ac5f549dd8c1e467b01e3e16bfaffb`.

The old-scored M3 V2 original scorer mismatch on API-defaulted fields remains its own separate historical failure. Do not merge denominators or overwrite that history.

## Restricted V2 forensic question, BEFORE reading raw in this branch

What exact JSON shape difference makes the original verifier fail?
A read-only inspection may report:
- For every source-class LIST and each individual item: collection kind, item `kind` present vs missing, item `apiVersion` present vs missing, object ID (name/UID/RV) present, object spec present.
- For all three WATCH event objects: event type/class/name/UID/RV, item `kind` and `apiVersion` shape relative to the corresponding LIST.
- Any other malformed/missing required fields, duplicate object names/UIDs, bad old-source identity, filtered/incomplete inventory or unknown extra policy/binding.
- The exact original native raw JSON SHA and container artifact ZIP SHA. Verify archived raw against its `NATIVE_HASH_BEFORE_SOURCE_JOIN` file before analysis.
- Emit an audit SHA256 and full denominators; do not simulate or recompute native source observations.

No mutation to original raw data, source forecast, V1 verifier or V1 action is authorized. No new native calls, no kubeconfig/environment, no new G5/P3/R5 evidence.

## Prospective (relative only to V2 code) repair criterion

IF forensic results show the sole structural discrepancy is a *missing* `kind` or `apiVersion` property on a native LIST item despite a verified matching **collection List kind and endpoint**, a future independent V2b **POST-NATIVE** protocol may authorize a narrowly scoped source-local inference of the missing member type. It must:
- Never rewrite original raw native ZIP or claim V1 PASS.
- Never normalize a present **incorrect** kind/version, missing UID/RV/name, changed policy/Binder specs, wrong event source identity, unknown extra sources or WATCH gap.
- Require same immutable four checkpoints/eight raw collection versions, three actual raw WATCH messages, three mutation outcomes and two live native WATCH actor scopes.
- Add anti-masking tests for present wrong `kind` vs missing `kind` and real source authority mismatch.
- Keep all resulting success labelled **RETROSPECTIVE post-native shape calibration**, not independent C1 efficacy/H3 superiority.
IF other semantics or artifact discrepancies are discovered, freeze a separate version before doing anything further; do not choose repairs to force score.

## Scientific stop

Per-kind Kubernetes LIST/WATCH is native API/Reflector prior art, available to fully informed B9. This experiment cannot establish cross-resource atomicity, global admission-source closure, real-time lease or method novelty. Original G4/B10/main unchanged, historical G5=285, G6 global C1 disputed and G8 open.
