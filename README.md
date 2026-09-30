# EEQ: information-state construction and source-admission repair

This is the author-authorized public workspace for the Information Sciences
cold-review repairs started on 2026-09-30. It supersedes the earlier private
repair branch as the destination for this work; it does not overwrite it.

## Scientific status: HOLD

The research studies how actions change retained evidence's claim qualification
and legal corrective continuations, and which distinctions a decision-support
information state must preserve. This repository is a repair workspace, not an
accepted manuscript or a claim of general source-adapter soundness.

The initial migration contains SQL/Alembic admission repairs, a JDK AST-based
Java lifecycle adapter, necessary local dependencies, 35 bounded regression
checks, and least-privilege GitHub Actions CI with retained test evidence.

```sh
python3 04_audits/is_cold_review/run_revision_checks.py
```

Python 3.10+ and a JDK with `java` and `javac` on PATH are required. Tests use the
Python standard library and native SQLite/Java execution; they do not need
private D-drive paths or credentials. CI records the commit, per-file hashes,
test count, errors, failures, and skips in `is-revision-evidence/summary.json`.
A local pass does not assert a cloud pass: consult this repository's Actions run.

## Evidence boundaries

- Certificate re-computation is a consistency check, not independent semantics.
- Synthetic regression cases are not a natural cohort or prevalence estimate.
- The old 4,500-contract benchmark's exact-view aliases are not independent
  implementations of five algorithms. That scientific blocker remains open.
- Source-correspondence assumptions and supported-language boundaries require
  further audit; passing this repair gate does not close the whole paper.
- Original papers and frozen ledgers are not part of this initial code migration.
  Any later archive must be marked as pre-repair evidence, not silently updated.

See `04_audits/is_cold_review/REPAIR_CONTRACT.md` for acceptance assumptions and
`SOURCE_MANIFEST.json` for migration hashes of the runnable files.

Publication to `MKLEE222/EEQ` was explicitly authorized by the owner. No secrets,
billing settings, repository visibility, or unrelated repositories are changed
by this migration. Public availability is not a new licensing declaration.
