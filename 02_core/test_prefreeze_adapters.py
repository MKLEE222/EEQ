from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "02_core"))

from java_lifecycle_adapter import (
    JavaLifecycleEpisode, compile_java_lifecycle_prospectively,
    verify_java_lifecycle_prospective,
)
from schema_migration_adapter import (
    SchemaMigrationEpisode, compile_schema_migration_prospectively,
    verify_schema_migration_prospective,
)


BEFORE = """
public class Carrier {
  private byte[] data;
  private int position;
  private boolean closed;
  public int position() { return position; }
  public int size() { return data; }
  public void close() { closed = true; }
}
"""

AFTER_SEALED = """
public class Carrier {
  private byte[] data;
  private int position;
  private boolean closed;
  public int position() { ensureOpen(); return position; }
  public int size() { return data; }
  public void close() { closed = true; }
}
"""


class AdapterPrefreezeTests(unittest.TestCase):
    def lifecycle(self, after=AFTER_SEALED, field="position"):
        return JavaLifecycleEpisode(
            "synthetic-life", "synthetic/repo", "parent", "action",
            "Carrier", field, "close", BEFORE, after,
        )

    def migration(self, source: str):
        return SchemaMigrationEpisode(
            "synthetic-migration", "synthetic/repo", "parent", "action",
            "legacy", "current", ("id", "owner"), source,
        )

    def test_lifecycle_sealed_route_requires_capsule(self):
        result = compile_java_lifecycle_prospectively(self.lifecycle())
        self.assertEqual("licensed-update", result.status)
        self.assertEqual("snapshot-position-then-close", result.selected_action)
        self.assertFalse(result.post_action_routes)

    def test_lifecycle_surviving_route(self):
        result = compile_java_lifecycle_prospectively(self.lifecycle(field="data"))
        self.assertEqual("licensed-update", result.status)
        self.assertEqual("close", result.selected_action)

    def test_lifecycle_unpreserved_field_withholds(self):
        after = AFTER_SEALED.replace("closed = true", "position = 0; closed = true")
        result = compile_java_lifecycle_prospectively(self.lifecycle(after=after))
        self.assertEqual("withhold", result.status)

    def test_lifecycle_dynamic_dispatch_is_unidentified(self):
        after = AFTER_SEALED.replace("ensureOpen()", "Class.forName(\"Guard\")")
        result = compile_java_lifecycle_prospectively(self.lifecycle(after=after))
        self.assertEqual("unidentified", result.status)

    def test_lifecycle_tamper_rejected(self):
        episode = self.lifecycle()
        result = compile_java_lifecycle_prospectively(episode)
        self.assertFalse(verify_java_lifecycle_prospective(episode, replace(result, selected_action="close"))[0])

    def test_lifecycle_rejects_local_return_variable_as_claim(self):
        source = """
public class Reader {
  private int count;
  public int read() { int b = 1; count++; return b; }
}
"""
        episode = JavaLifecycleEpisode(
            "local-return", "synthetic/repo", "parent", "action",
            "Reader", "b", "read", source, source,
        )
        result = compile_java_lifecycle_prospectively(episode)
        self.assertEqual("unidentified", result.status)

    def test_method_body_does_not_absorb_following_method_writes(self):
        source = """
public class Carrier {
  private int value;
  private boolean closed;
  public int value() { return value; }
  public int inspect() { return value; }
  public void close() { closed = true; }
}
"""
        episode = JavaLifecycleEpisode(
            "body-boundary", "synthetic/repo", "parent", "action",
            "Carrier", "value", "inspect", source, source,
        )
        result = compile_java_lifecycle_prospectively(episode)
        self.assertEqual("unidentified", result.status)

    def test_schema_literal_rename_licenses(self):
        source = "def upgrade():\n    op.rename_table('legacy', 'current')\n"
        result = compile_schema_migration_prospectively(self.migration(source))
        self.assertEqual(("licensed-update", "cutover"), (result.status, result.selected_action))

    def test_schema_identity_transport_licenses(self):
        source = """def upgrade():
    op.execute("INSERT INTO current (id, owner) SELECT id, owner FROM legacy")
    op.drop_table("legacy")
"""
        result = compile_schema_migration_prospectively(self.migration(source))
        self.assertEqual("licensed-update", result.status)
        self.assertTrue(result.cleanup_detected)

    def test_schema_swapped_transport_withholds(self):
        source = """def upgrade():
    op.execute("INSERT INTO current (id, owner) SELECT owner, id FROM legacy")
"""
        result = compile_schema_migration_prospectively(self.migration(source))
        self.assertEqual(("withhold", "hold"), (result.status, result.selected_action))

    def test_schema_dynamic_sql_is_unidentified(self):
        source = "def upgrade():\n    op.execute(build_sql())\n"
        result = compile_schema_migration_prospectively(self.migration(source))
        self.assertEqual("unidentified", result.status)

    def test_schema_unrelated_constraint_is_unidentified(self):
        source = "def upgrade():\n    op.create_index('ix_x', 'other', ['x'])\n"
        result = compile_schema_migration_prospectively(self.migration(source))
        self.assertEqual("unidentified", result.status)

    def test_schema_tamper_rejected(self):
        episode = self.migration("def upgrade():\n    op.rename_table('legacy', 'current')\n")
        result = compile_schema_migration_prospectively(episode)
        self.assertFalse(verify_schema_migration_prospective(episode, replace(result, selected_action="hold"))[0])

    def test_prospective_modules_do_not_reference_adjudication_payloads(self):
        root = Path(__file__).resolve().parent
        forbidden = (
            "developer_test_patch", "post_action_runtime", "relation_mismatch_count",
            "oracle_action", "adjudicated_loss",
        )
        for name in ("java_lifecycle_adapter.py", "schema_migration_adapter.py"):
            text = (root / name).read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
