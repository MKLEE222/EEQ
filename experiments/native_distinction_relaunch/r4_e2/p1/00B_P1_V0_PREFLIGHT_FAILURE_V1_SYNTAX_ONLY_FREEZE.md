# E2-P1 V0 Python preflight syntax failure — V1 narrow correction freeze

Date 2026-10-10. P1 first CI run 38033018972 was **FAILURE BEFORE OLD E2 ARTIFACT DOWNLOAD AND BEFORE ANY P1 ATTACK EVALUATION**.
The original frozen 2 attack scenarios, exact old source/strong B9 evidence, expected effects, and evaluation rules remain unchanged. Source and native scored denominators both ZERO at the failed stage.

The cause is a Python syntax error in P1 attack code at lines 65-66: multiline `if` expression was split without parentheses/line continuation. It was caught at Python test import. It is an implementation infrastructure/test blocker, not evidence that the attack succeeded or failed.

This explicitly versioned V1 amendment, frozen BEFORE modifying the script, authorizes exactly one syntax-only change:
from two unparenthesized lines:
  if "third_policy" in leaf.get("source_refs",[]) and
     leaf.get("obligation")=="K8S_REGISTERED_CEL_NOT_EQUAL_SUBSET":
to equivalent single parenthesized expression.
No change to the registered original TUF/K8s leaf selected, B9 control, source bytes, model semantics, outputs or success threshold.

The original failure remains in Actions. After the syntax-only correction re-run ALL ten pre-archive fake-fixture tests before immutable E2 source-only ZIP is fetched. If another issue appears, do not silently shift the attack hypothesis; preserve it with a new versioned correction. No Kubernetes/TUF native calls, no G5/old G6/old G8 change.
