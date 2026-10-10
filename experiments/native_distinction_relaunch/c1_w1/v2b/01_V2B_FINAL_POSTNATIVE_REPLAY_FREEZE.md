# C1-W1 V2B final POST-NATIVE replay freeze (2026-10-10)

STATUS: **POST-NATIVE retrospective replay preregistration**, before V2B retrospective join; NOT a prospective native experimental freeze. The initial W1 native run 38029036440 was a **FAILURE** due to REFUSE_COLLECTION_ITEM_SHAPE. That historical failure must remain unchanged, even if this replay succeeds.

## Original sources and immutable chronology

- Parent W1 V1 original presource freeze commit 16dae1e9db0f7e254077a7658594e055da0fb185 and prescore manifest commit 0378753912b2b311afd453773259f3668d22f776 (blob b3134f5d537b1178af46f3ef21e36b21bdd30275).
- Original 48/48 pre-native test run 38028957072. Native first/only execution run 38029036440, code commit af8ea13452eaec52bed1a343443eeffad3fb53e3, original result FAILURE.
- Native original raw artifact ID 11661372658, ZIP SHA256 9d2dc931d239f4a269da00038d322c5f795001afec8da22d3b311360740af94d. The archived RAW JSON SHA256 is inside C1_W1_NATIVE_HASH_BEFORE_SOURCE_JOIN.txt. Verify that checksum on the original before ANY copy.
- Earlier SEALED source-only forecast artifact ID 11660314996, outer ZIP SHA256 202d392b01decf7e42d87429305d2b629ee8029ad91f8daa08afdf75068c1863. SOURCE_MANIFEST.json SHA256 7dddf471c1c0fc53b388c47b32cebbb09caa5f0d8ca377567a9bf23dbc960304; SOURCE_EVENTS_ONLY.json SHA256 d97aa16cb8b33532e50767f4d452c58db8ac5f549dd8c1e467b01e3e16bfaffb.
- Read-only, independently preregistered postnative forensic run 38029310544 SUCCESS, artifact 11662055398, ZIP SHA256 06c692afd8dbe674afd34cd77fe2d121948d1a6c3cff4b3063546351027d4cc2. It counted 16 LIST items across 8 collections each *missing* both kind and apiVersion but no missing required UID/RV/spec and no wrong collection identities.
- Surgical postnative V2b normalization freeze created BEFORE code at commit 95bacb356406c1239ba3e95b6ccaea5867f7efdf (file blob 2df4ed414f4ad17350ff26ae0eea20a195011a3d). Authorizes only COPY augmentation of exactly 32 previously ABSENT TypeMeta attributes for exactly 16 LIST items, from their verified enclosing List kind/API version. Raw original is NEVER changed.
- 22/22 entirely synthetic normalization refusal tests passed at run 38029429155 commit 08446cdaf316249f7ddd93ee26ece6f1468e3e2b, before any V2b replay of old native archive.

## Locked exact Git blob SHA values

Paths under experiments/native_distinction_relaunch/c1_w1:
- v2b/00_V2B_POSTNATIVE_TYPemETA_COPY_FREEZE.md: 2df4ed414f4ad17350ff26ae0eea20a195011a3d
- v2b/c1_w1_v2b_copy_absent_typemeta.py: 8b3d485943c2b90c3452cf1f4ce237485ec98039
- v2b/test_c1_w1_v2b_copy_absent_typemeta.py: e259155ea772003d89b8017744963b1f98509a5d
- original c1_w1_scoped_evidence_verifier.py: 5013a1a42a92d837cf54e4ca5d0c765d2277a0f4
- original c1_w1_join_only_scorer.py: b721e378de5406b66eaf7c9ef8f8cd30e77f7425
- original 01_C1_W1_FINAL_NATIVE_PRESCORE_MANIFEST.md: b3134f5d537b1178af46f3ef21e36b21bdd30275
- Old main/G4/B10 unchanged: main b5434ab1ad317e5121c88b632806880f903774db, G4 original commit c15b212ad0c2be3856a03d38802aaffa628aefd1, G4 blob 3eeaeeb828d2fcf7ec4487da06489fee3146c920, old B10 blob 9a6bff7a2b8db73b86b6952c706852c92b1a4b1d.

## Retrospective score and abort rule

No native Kubernetes calls, no Pod decisions, no new G5 examples. Original native whole archive ZIP and raw SHA must match. Run 22 negative tests BEFORE opening historical archive. Normalize only to new COPY, never original. Verify exactly 16 items / 32 inferred previously absent TypeMeta fields and no edits to native WATCH events, LIST resourceVersions, original object identities, policy/Binding semantics or actions. Reuse original V1 verifier and join-only scorer WITHOUT modification on that copy, and compare with sealed source-only forecast ONLY AFTER original raw saved.

Registered fixed counts: 3 original native WATCH events, 8 raw LIST snapshots, 2 actual WATCH streams, 3 source mutations, 0 Pod scores, 0 G5 increment. Any scorer failure means V2B failure (no widening posthoc). Original V1 gate remains FAILURE under all outcomes. If all pass, V2B disposition only: C1_W1_V2B_RETROSPECTIVE_SCOPED_PREFIX_FEASIBILITY_B9_TIE.

No global Kubernetes C1, atomic cross-kind state, open-ended NOW freshness, live native 410 denial proof, general cross-family EEQ compiler, P3 labor benefit or H3 independent B9 superiority. Standard client-go Reflector, XACML, provenance and certain-answer prior art remain. Historical G5=285, G6 global C1 disputed, G8 incomplete and fifth holdout unopened.
