# IS cold-review repair: source-admission v2

Status: engineering repair workspace, NOT a final submission and NOT a complete
proof of source correspondence. Preserve the 2026-09-30 submission and frozen
ledgers. New evidence has new source digests and cannot replace old results.

## Fixed failure classes

SQL aliases are separated from input column identities. Only a full single
unfiltered INSERT/SELECT column projection or literal rename is admitted.
Only an undecorated zero-argument upgrade with straight-line literal op calls is
examined. Downgrade and uninvoked function bodies are not executed actions.
Unknown control flow, calls, shadowed bindings, extra SQL, repeated transports,
source deletion before transport, and target deletion cause unidentified/hold.
Identity and renamed-column positive controls remain in the regression suite.

Java uses the JDK syntax tree, not regex body/write extraction. Private/final
local helper effects propagate transitively. Prefix/postfix and compound writes
are tracked. Unknown/overridable calls, ambiguous overloads, recursion and
shadowed field names cannot produce a preservation certificate. Comments and
strings are not effects. The analyzer parses source only and does not run it.
The independent native replay compiles and executes an authored diagnostic class.

## Explicit boundary (not silently promoted into a theorem)

SQL needs a trusted op binding, declared compatible schema, successful execution,
an empty INSERT destination, no triggers/implicit value-changing casts, and no
concurrent mutation. The adapter does not infer these facts from syntax.

Java analysis assumes well-typed source, successful action completion, declared
receiver/class and trusted JDK operations, without concurrent, reflective or
native mutation. The parser does not typecheck an external project's dependency
graph. Field preservation concerns Java field values/reference identity, not a
claim that an aliased object graph is deeply immutable. May-write means
preservation is NOT established, not that every execution changes the value.
The ensureOpen flag remains syntactic route metadata; arbitrary guard semantics,
implicit callbacks and completeness of all observation routes are NOT proved by
this repair. These require an expanded admission audit before scientific closure.

All verify functions check deterministic certificate consistency. They are NOT
independent semantic validators. SQLite execution and javac/java diagnostics use
separate execution paths. Existing prefreeze tests include structural fixtures;
only explicitly marked native replays establish runtime behavior.

## Experimental identity correction

The 4500-contract runner in the September submission maps full-history-oracle,
wfc-e, factored-wfc, backend-given-wfc and wfc-minus-localization to the SAME
exact MethodView. It is an information-projection sensitivity study, not five
independent implementations. Preserve frozen_v1 and label this limitation in all
manuscript/cover/highlight uses. No local/CI pass here changes that result.

A future construction validation must actually execute source/history -> WFC
construction -> independent backend and compare licensing, value, complete
optimal first-action sets and native validity. Do not inflate this diagnostic
suite into a newly selected natural cohort or a theorem proof.

## Running and migration scope

Requires Python >=3.10 and a JDK with java and javac on PATH; no pip dependencies.
Run: python3 04_audits/is_cold_review/run_revision_checks.py
Artifacts: is-revision-evidence/tests.log and summary.json.
CI deliberately runs this bounded gate, not carrier tests that require excluded
05_runs worktrees. The workflow has read-only repository permissions and does
not merge or write source files. The author's earlier private repository and its
main branch remain unchanged by this public migration.

The two legacy dependency modules are copied byte-for-byte for a self-contained
checkout. Their inclusion is not a new soundness audit of every legacy API.
