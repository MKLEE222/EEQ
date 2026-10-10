# C1-W1: authority-bounded LIST->WATCH cursor native study — presource freeze

Date: 2026-10-10; branch `eeq-c1-w1-source-cursor-20261010`; parent `33ad1fc790d15f6c705aa7bf0f9d833a2e6de5cd`.
**STATE: PROSPECTIVE DESIGN FREEZE BEFORE C1-W1 CODE, MODEL OR NATIVE RESULTS.**
New scoped controlled-development diagnostic, NOT an amendment of frozen original G4 at `c15b212ad0c2be3856a03d38802aaffa628aefd1`, NOT G5 increment (historical 285), NOT full C1 closure or H3 novelty.

## Different scientific object, not another 8/8 scoreboard

R3-M3 already native-established the third-policy+binding stale-ACCEPT counterexample; V2 original gate FAILED because API defaults were not normalized, and V2B retrospective calibration 8/8 remains **B9 TIE**, not a new score. Stop accumulating more 8/8 decision matches.

C1-W1 measures whether an authorized actor can *actually capture an event stream from a concrete collection LIST cursor*, detect changes in authority membership, and preserve the exact limits of what that observation warrants.

Kubernetes can return a collection `metadata.resourceVersion` in raw unfiltered LIST; starting a WATCH from the same opaque cursor can stream ADDED/MODIFIED/DELETED. A `410 Gone` invalidates the continuous replay claim and requires RE-LIST; BOOKMARK is optional and not scheduled. The `resourceVersion` of POLICY LIST and BINDING LIST cannot be assumed equal or numerically comparable; neither is a signed cross-kind consistent cut. LIST/WATCH is an established Kubernetes feature, not EEQ novelty.

**Epistemic falsification**:
- CLAIM S1: a complete, authenticated *single-resource-class* LIST + watch events from its collection cursor reconstructs a *prefix-relative* scoped membership state, subject to stream validity and complete event consumption.
- CLAIM S2 (must FAIL): this alone proves globally correct Kubernetes admission ACCEPT at arbitrary future wall-clock times, covers all admission mechanisms, or proves no unobserved changes after the last consumed event.
- CLAIM S3 (must FAIL): a caller-supplied `complete:true`, an old object digest, a BOOKMARK from only one class, or numeric comparison of two distinct opaque RV strings suffices for S2.
- CLAIM S4: missing collection authority, RBAC denial, 410, unexpected truncation, unobserved classes or inability to reach the pre-registered evidence checkpoint require explicit `REFUSE_SCOPE_OR_FRESHNESS` for current ACCEPT.
- Negative Deny source witness validity also needs fresh premise qualification; it is NOT automatically preserved across unseen source revocations.

A correctly captured per-kind LIST->WATCH event prefix may support a **HISTORICAL_SCOPED_PREFIX**, not an unconditional *NOW* guarantee. Positive ACCEPT remains CONDITIONAL on the explicitly bounded VAP source contract and independently justified freshness; no global ACCEPT certificates will be claimed.

## Native input identities and exact actor/scope

Reuse immutable R3-M1 source JSON:
`experiments/native_distinction_relaunch/r3_m1/sources/{namespace.json,policy.json,binding-team.json,binding-mode.json}`;
R3-M3 new third sources:
`experiments/native_distinction_relaunch/r3_m3/sources/{policy-third.json,binding-third.json}`.
All source blob IDs will be independently pinned after this freeze, and their raw bytes **MUST NOT BE ALTERED**. No R3-M3 archived native result or previous source prediction may enter W1 source-only model features.

Actor: single ephemeral clean Kind kubeconfig context, cluster-admin for this *controlled experiment*; it must independently and successfully demonstrate LIST and WATCH permissions for BOTH cluster-scoped VAP `validatingadmissionpolicies` and VAP Binding `validatingadmissionpolicybindings` using native `kubectl auth can-i`, plus two actual LIST+WATCH requests. Successful permission probes DO NOT prove future permission, nor mean other source types were enumerated.
Allowed source classes EXACT TWO: unfiltered `/apis/admissionregistration.k8s.io/v1/validatingadmissionpolicies` and `/apis/admissionregistration.k8s.io/v1/validatingadmissionpolicybindings`. No `limit`, `labelSelector`, `fieldSelector`, namespace or continue token. `collection.metadata.resourceVersion` nonempty, `metadata.continue` absent/empty, `kind` and `apiVersion` of raw response checked. No unrestricted global admission completeness from just these two classes.

Pinned runtime from previous actual M3: Kind `v0.31.0` binary sha256 `eb244cbafcc157dff60cf68693c14c9a75c4e6e6fedaf9cd71c58117cb93e3fa`, node `kindest/node:v1.35.0@sha256:452d707d4862f52530247495d180205e029056831160e22870e37e3f6c1ac31f`, kubectl `v1.35.0` download verified against official SHA256, Ubuntu 24.04, Python 3.11. ONE fresh cluster named `eeq-c1-w1`. No prod credentials, no unmanaged external change.

## Preregistered source-only event sequence and complete denominator

Before any native W1 call, independently create *source-only* SHA-sealed event predictions and sealed source manifest, in an artifact without any native truth:
- S0: apply original M1 policy + TEAM and MODE Bindings, then perform TWO raw LIST snapshots and begin TWO independent WATCH channels from **their respective opaque collection RVs**, with `allowWatchBookmarks=true` and fixed `timeoutSeconds=150`. No BOOKMARK required for credit.
- A1: apply new M3 third policy only. Policy-WATCH must observe **ADDED third policy**; no new third Binding. Take TWO new raw LIST snapshots.
- A2: apply M3 third Binding. Binding-WATCH must observe **ADDED third binding**; take TWO raw LIST snapshots. This *revokes the legitimacy* of a cached two-binding ACCEPT evidence boundary for the registered default Pod (the prior M3 proved its decision effect). No new native Pod decision is being scored in W1.
- A3: delete M3 third Binding (third policy remains installed). Binding-WATCH must observe **DELETED third binding**; take TWO raw LIST snapshots.
- No action after failure of a preregistered earlier action; save partial raw evidence and failure category instead of repairing or retrying. No case/execution-order changes.

**Primary registered native observations: 3 source-class WATCH events, 2 native WATCH channels, 4 checkpoints × 2 complete source-class LISTs = 8 raw LIST snapshots, exactly 3 real create/create/delete mutation API requests.** No native Pod decision scoring (0 fresh decision labels). Check each event's type, name, UID and opaque object RV against corresponding native LIST snapshot (DELETED binding's UID compared against prior active LIST). Check original old policy/Binding UIDs and substantive specs unchanged. No event loss or cursor replacement allowed.

Fixed setup waits: 10s after initial three original native policy/bindings; 2s after opening two watches before A1; 6s after each mutation before demanding its single specific event; an additional event retrieval cutoff of 12s **once per expected event**, no method-outcome-driven retries. No numeric comparison of RV; collection cursors passed through exact as opaque strings.
Native raw watch transport may terminate early, fragment JSON text, send unexpected events, or lack permission. Those are explicit `NATIVE_WATCH_CAPTURE_FAILED` or `AUTHORITY_UNAVAILABLE` with original evidence retained, NOT a changed oracle, no fake event or relist substituted.

Watch events must be read from the **real Kubernetes watch HTTP response**, not synthesized from later LIST diff; a LIST diff alone CANNOT substitute for an event.
Kubernetes server may admit additional automatic API defaulted fields; the judge may restrict to stable object identity, UID, RV and source-relevant behavior; do not silently normalize unrelated semantic differences to PASS.
After A3, terminate both watches intentionally *only after* all events have been recorded; this is not evidence of indefinite stream liveness or further collection freshness.

## Frozen synthetic adversaries (not native results)

Pre-register a finite set of **16** structural cases T01–T16 (outcomes fixed before code):
T01 normal unfiltered full-list cursor plus exact WATCH ADDED -> PREFIX_WITNESSED;
T02 correct third Binding ADDED -> OLD_TWO_SOURCE_ACCEPT_INVALIDATED;
T03 correct third Binding DELETED with fresh per-class checkpoint -> CONDITIONAL_SCOPED_REATTESTATION_ONLY;
T04 old unchanged source digests with unobserved new Binding -> REFUSE_FRESHNESS;
T05 WATCH ERROR 410 Gone -> RESYNC_REQUIRED;
T06 WATCH disconnect before proof of required checkpoint -> RESYNC_REQUIRED;
T07 list success but WATCH permission denied -> REFUSE_AUTHORITY;
T08 incomplete list due to nonempty `continue` -> REFUSE_INVENTORY;
T09 LIST restricted by label/field selector -> REFUSE_SCOPE;
T10 caller declares `complete:true` without independent source evidence -> REFUSE_UNATTESTED;
T11 POLICY BOOKMARK alone while BINDING channel unsynced -> REFUSE_CROSS_CLASS;
T12 POLICY and BINDING LIST have different opaque RV strings -> NEITHER numeric compare nor global atomicity claim;
T13 WATCH event without UID/object RV or event of unknown kind -> REFUSE_EVENT_INTEGRITY;
T14 missing/unwatched source class -> REFUSE_GLOBAL_ACCEPT;
T15 old Deny witness if policy/binding may have been revoked -> REFUSE_FRESHNESS;
T16 native relist after gap reestablishes per-class snapshot only -> CONDITIONAL_SCOPED_REATTESTATION_ONLY.
No new original G5 samples or R5 transfer.

## Fair comparator, originality veto and stop rules

Fully informed B9 may use the EXACT SAME Kubernetes LIST/WATCH endpoints, actor RBAC, resourceVersion, native Reflector, caching, source membership/digests, and certificate data structure. It should recover all 3 events; a B9 tie => `NO_INDEPENDENT_VALUE`. Weak stale-collection-hash-only cache is an explicitly UNFAIR diagnostic omission, never strong B9.

Closest prior art: Kubernetes LIST/WATCH+client-go Reflector and RBAC; distributed-systems consistent cuts/knowledge limitations; database provenance, incremental view maintenance, possible-world certain answers, XACML Indeterminate. W1 event capture is infrastructure and feasibility, **not** a new EEQ operator or proof. A 3/3 native event PASS must remain `C1_W1_SCOPED_NATIVE_LIST_WATCH_FEASIBILITY_B9_TIE`, not full C1, global admission safety, quantitative P3 or H3.

If the external inventory authority/scope remains hand-assumed after native W1, the new kernel still cannot claim independent certificate construction. P3 independent human source-to-proof-maintenance comparison remains unopened; no cherry-picking other benefit measures if W1 ties.

Original main, G4/B10, all existing G5=285 and fifth family holdout unchanged. Original G6 disputed and G8 incomplete throughout.

Official references to verify: https://kubernetes.io/docs/reference/using-api/api-concepts/ ; https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/ ; https://kubernetes.io/docs/reference/access-authn-authz/rbac/
