# EEQ: information-state construction and source-admission repair

This is the author-authorized public workspace for the Information Sciences
cold-review repairs started on 2026-09-30. It supersedes the earlier private
repair branch as the destination for this work; it does not overwrite it.

## Scientific status: HOLD

The research studies how actions change retained evidence's claim qualification
and legal corrective continuations, and which distinctions a decision-support
information state must preserve. This repository is a repair workspace, not an
accepted manuscript or a claim of general source-adapter soundness.

The first migration contains SQL/Alembic admission repairs, a JDK AST-based Java
lifecycle adapter, necessary local dependencies, 35 bounded regression checks,
and least-privilege GitHub Actions CI with retained test evidence.

```sh
python3 04_audits/is_cold_review/run_revision_checks.py
```

Python 3.10+ and a JDK with `java` and `javac` on PATH are required. Tests use the
Python standard library and native SQLite/Java execution; they do not need
private D-drive paths or credentials. This command becomes available once the
code-migration commit is present. The initial README commit alone is not a
complete runnable checkout.

## Evidence boundaries

- Certificate re-computation is a consistency check, not independent semantics.
- Synthetic regression cases are not a natural cohort or prevalence estimate.
- The old 4,500-contract benchmark's exact-view aliases are not independent
  implementations of five algorithms. That scientific blocker remains open.
- Source-correspondence assumptions and supported-language boundaries require
  further audit; passing this repair gate does not close the whole paper.
- Any original paper or frozen ledger later archived here must be explicitly
  marked as pre-repair evidence, not silently updated or presented as validated.

Publication of these repair materials to `MKLEE222/EEQ` was explicitly authorized
by the owner in this conversation. No access permissions, secrets, billing
settings, or unrelated repositories are changed by this migration.
