# R2-A v2 pre-native harness import failure — retained

On 2026-10-09 GitHub Actions 37901283134 FAILED **before any native
cluster installation**. Original GitHub Actions run and artifact
11602577575 are retained, with outer ZIP SHA256
a2642193edc52e5d93361882f85dec77c23f2335c5eafbbdee7749ab1ec65d2e.

The independent nine-case native comparison scorer passed. The NEW
native-Pod-name regression test did not import because Python unittest
was invoked from repository root but the test imports sibling modules
r2a_native_episode and r2a_native_episode_v2 without extending sys.path.
This is a TEST HARNESS module search path issue, not a native prediction,
scientific finding, or content mismatch. No Kubernetes kind/native
attempt ran under this v2 commit.

Pre-native remedy: in a separately named v2b workflow, prefix the
native-Pod-name-only unittest invocation with
  PYTHONPATH=experiments/native_distinction_relaunch/r2a
so the existing immutable test and native source blobs are unchanged.

All SOURCE only predictions, registered native case grid, Pod name
repair, evaluator, native error attribution and Kubernetes node/image pins
remain EXACTLY as previously frozen. The earlier v1 invalid Pod name
native attempt is also retained.

If v2b fails native, retain native evidence and do not change expected
source-only predictions or baseline fairness after inspecting it.
