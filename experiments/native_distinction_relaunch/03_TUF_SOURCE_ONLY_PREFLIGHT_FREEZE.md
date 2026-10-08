# R1a — Bottlerocket Root Source-Only Feasibility Preflight

Date: 2026-10-08
Status: PRE-SOURCE-EXECUTION FREEZE; no TUF native calls allowed.

## Authority and scope

This is a **read-only metadata extraction diagnostic** for the proposed
EEQ native distinction program. It is NOT native scoring, nor G4-v1 method
scoring, nor R1 transition-extractor certification.

Pinned source:
- experiments/bottlerocket/FROZEN_SOURCE_INVENTORY.md
- Bottlerocket aws-k8s-1.35/x86_64 source roots 1.root.json to 8.root.json
- exact eight SHA256s and raw byte counts from that existing inventory;
- raw base URL:
  https://updates.bottlerocket.aws/2020-07-07/aws-k8s-1.35/x86_64/

Reference root-update obligations (TUF specification 1.0.36, not an assertion
about the exact native-library implementation):
https://theupdateframework.github.io/specification/v1.0.36/
- before accepting root N+1, the old root-N authority threshold and new
  root-(N+1) authority threshold must both be satisfied by valid signatures;
- every distinct KEYID contributes at most one verified signature;
- adjacent root version continuity is relevant.

**This preflight DOES NOT cryptographically verify any signature.**
It only counts *syntactically present* signature KEYIDs overlapping the old
and new root role keyid inventories. Such counts are not native trust labels
and are not sufficient evidence of verified qualifications.

## Registered measurements before source fetch

For each of eight root source blobs:
- raw SHA256 and byte length, signed metadata version;
- root role threshold and unique declared root keyids;
- declared key IDs in signed.keys and signature envelope keyids;
- structural support for the declared root role key references;
- signature keyid uniqueness / duplicates as a diagnostic, not validity.

For each ordered adjacent pair (N,N+1):
- old/new root role keyid intersections, removals and additions;
- old/new root role thresholds and syntactic signature-keyid overlaps;
- number of declared root role key set changes;
- candidate transition = "root N update with root N+1 metadata";
- explicit "cryptographic verification NOT performed", and no
  native ACCEPT/REJECT decision field.

Reject source hash mismatch; retain failure rather than substituting files.
Do not fetch version 9 or any alternate root variant after observing results.

## Interpretive / kill boundary

If the root authority role and key inventories are identical throughout,
this production chain does not by itself instantiate a meaningful key
authority-rotation contrast. R1 would need a *separately frozen controlled*
signing fixture or another native system; do NOT invent native difference.

If authority changes exist, that is only an R1 hypothesis lead. It does not
establish which transitions are accepted by tuf-js, that an action graph is
total, that an A/B pair exists, or that EEQ surpasses B9.

A full source-to-state extractor still must meet 01_NATIVE_EXTRACTOR_
PROOF_OBLIGATIONS.md and gain independent native validation.

Expected evidence class: PRODUCTION_HISTORY source metadata only.
G5 count effect = 0; new native method-scored rows = 0.
