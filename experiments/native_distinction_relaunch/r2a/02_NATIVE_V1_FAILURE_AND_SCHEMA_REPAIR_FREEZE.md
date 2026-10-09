# R2-A Native Attempt v1 — FAILED NATIVE INPUT SCHEMA, retained

Date: 2026-10-09.
Classification: **NATIVE_FIXTURE_SCHEMA_INVALID / NO R2-A SCIENTIFIC SCORE**.

Prescoring contract/source-only frozen unchanged. The first native attempt was:
- GitHub Actions 37900621767, commit 4ccb2ffa5fa07753a1f98f87dcd4e978c09f3359;
- failed workflow, artifact 11602247238,
  SHA256 5fee6caafb7f7f27eab8c1d06d45775cbfb79579f9a993388d1176d698575063.

Observed raw evidence, not an imputed policy outcome:
- Kind v1.35.0 cluster WORLD_GATE started successfully;
- initial registered native binding selector was {"eeq.r2a/armed":"never"} and resourceVersion 488;
- actual PATCH of binding to {"eeq.r2a/armed":"gate"} returned success,
  subsequent native GET showed resourceVersion 499 and selector gate;
- current Pod dry-run requests were NOT valid Kubernetes objects:
  generated metadata.name values contained the world token world_gate,
  including an underscore. Native API returned RFC1123 name validation errors.
  These are NATIVE_ORACLE_AMBIGUOUS / OTHER_NATIVE_ERROR, never ACCEPT/REJECT;
- independent activation probe also had invalid names and remained
  OTHER_NATIVE_ERROR for 60 attempts, causing
  POLICY_MUTATION_ACTIVATION_NOT_VERIFIED;
- only WORLD_GATE was attempted before failed workflow step terminated;
  WORLD_STANDBY was NOT executed, and no source-vs-native 8-cell score exists.

The successful binding patch shows a mutable native source operation, but
does NOT prove preregistered future divergence. No native A match counted.

## ONE justified native-driver v2 repair (pre-repeat)

Modify ONLY generated Pod metadata.name world token:
  world.lower()  ->  world.lower().replace('_','-')
and assert the resulting name satisfies RFC1123 DNS-subdomain syntax.
No change to Pod namespace, serviceAccountName, spec, frozen CEL policy,
binding/source bytes, patch, action vocabulary, horizon, registered case
count, or source-only prediction bytes.

Freeze this diagnostic BEFORE rerunning native. Old v1 driver blob, first
failure artifact, source-only prediction artifact, and original prescore
manifest remain immutable.

After the change, commit a separate v2 prescore code/blob manifest and
workflow rejecting any change to registered source/predictions/unchanged
scorer. No adaptation based on native ACCEPT/REJECT outcomes is permitted.

Any next native mismatch or infrastructure failure is retained, never
silently treated as method PASS.
