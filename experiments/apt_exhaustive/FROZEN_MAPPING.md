# APT 3.0.3 exhaustive finite carrier — frozen semantic mapping

Freeze status: predictions are committed before any exhaustive native execution.

Registered decision contract:
- qualification: current InRelease signer must satisfy the configured Signed-By binding;
- protected continuation fields: Origin, Label, Codename;
- continuation authorization: either global --allow-releaseinfo-change or field-specific allowances;
- Suite and Version are retained in the native artifacts but are predicted zero-effect controls for this registered default decision contract.

Frozen decoder:
1. if signer qualification is false -> REJECT_AUTH;
2. else if any changed protected field is not globally or field-specifically allowed -> BLOCK_CONFIRM;
3. else -> ACCEPT.

Finite core state space:
- qualification: 2;
- protected-change vector: 2^3 = 8;
- continuation contract: 8 field-specific subsets with global=false, plus one global=true state = 9;
- core semantic states = 2 * 8 * 9 = 144.

Negative-control expansion:
- Suite changed / unchanged: 2;
- Version changed / unchanged: 2;
- total native configurations = 144 * 4 = 576.

Counting discipline:
- all 576 native executions remain in the configuration ledger;
- Suite/Version multiplicity does not create new core semantic templates;
- version/client repeats never inflate the semantic-template denominator.

Native output labels are oracle-only and are not inputs to the frozen decoder.
