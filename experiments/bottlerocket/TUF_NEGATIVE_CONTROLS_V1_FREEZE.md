# Bottlerocket TUF negative controls v1 — frozen before native execution

Protocol parent: `c15b212ad0c2be3856a03d38802aaffa628aefd1`.

Production source inventory remains
`experiments/bottlerocket/FROZEN_SOURCE_INVENTORY.md`.

These controls are a **CONTROLLED_NATIVE** G6 extension. They do not replace or
inflate the seven production-history transitions and do not alter the already
closed G5 count. The fifth-family holdout remains unopened.

Native library: `tuf-js@3.0.1`.

Initial trust anchor: production-authored Bottlerocket root 1.

## Frozen controls

### NC1 replay_current_root

Feed production root 1 to `TrustedMetadataStore.updateRoot()` while root 1 is
already trusted.

Expected native action: `REJECT`.

Expected native error class: `BadVersionError`.

Mechanism tested: version/continuation replay protection. The candidate is
cryptographically authentic but does not advance the registered root sequence.

### NC2 unsigned_next_root

Take production root 2, preserve its signed payload byte-for-byte at the JSON
data-model level, and replace the top-level `signatures` array with an empty
array.

Expected native action: `REJECT`.

Expected native error class: `UnsignedMetadataError`.

Mechanism tested: qualification/support coverage. A structurally valid next
root without qualifying signatures must not become trusted.

### NC3 tampered_signed_payload

Take production root 2 and add the unrecognized signed-field
`eeq_controlled_tamper: true` while retaining the original signatures.

Expected native action: `REJECT`.

Expected native error class: `UnsignedMetadataError`.

Mechanism tested: claim binding. The original signatures must not authorize a
modified signed payload.

## Failure discipline

The runner must first verify the downloaded production root 1 and root 2
against their frozen SHA256 and byte sizes. A source mismatch is
`SOURCE_UNAVAILABLE/INFRASTRUCTURE`, not a method result.

Any control that is accepted, or rejected with an error class different from
its frozen prediction, fails the control run. No control may be deleted or
rewritten after native execution begins.
