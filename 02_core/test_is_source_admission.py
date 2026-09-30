"""Synthetic repair regressions, not a new prospective/natural cohort."""
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile
import unittest
from schema_migration_adapter import SchemaMigrationEpisode, compile_schema_migration_prospectively
from java_lifecycle_adapter import JavaLifecycleEpisode, compile_java_lifecycle_prospectively


def schema(source):
    return SchemaMigrationEpisode('diagnostic', 'synthetic', 'before', 'after',
                                  'legacy', 'current', ('id', 'owner'), source)


def sql_source(sql):
    return 'def upgrade():\n    op.execute(' + repr(sql) + ')\n    op.drop_table("legacy")\n'


def java_source(close_body='closed = true;', helper='', getter='return position;'):
    return ('public class Carrier {\n private int position = 7;\n private boolean closed;\n'
            ' public int position() { ' + getter + ' }\n public void close() { ' + close_body + ' }\n' + helper + '\n}\n')


def java_cert(after, before=None):
    return compile_java_lifecycle_prospectively(JavaLifecycleEpisode(
        'diagnostic', 'synthetic', 'before', 'after', 'Carrier', 'position',
        'close', before or java_source(), after))


class SchemaAdmissionTests(unittest.TestCase):
    @staticmethod
    def execute(sql):
        with sqlite3.connect(':memory:') as db:
            db.executescript('CREATE TABLE legacy(id INTEGER, owner INTEGER);'
                             'CREATE TABLE current(id INTEGER, owner INTEGER);'
                             'INSERT INTO legacy VALUES (1,10),(2,20);')
            db.executescript(sql)
            return db.execute('SELECT id, owner FROM current ORDER BY id').fetchall()

    def test_identity_positive_control_and_native_relation(self):
        sql = 'INSERT INTO current (id, owner) SELECT id, owner FROM legacy'
        self.assertEqual(compile_schema_migration_prospectively(schema(sql_source(sql))).status, 'licensed-update')
        self.assertEqual(self.execute(sql), [(1, 10), (2, 20)])

    def test_alias_arithmetic_does_not_certify_identity(self):
        sql = 'INSERT INTO current (id, owner) SELECT id, owner + 100 AS owner FROM legacy'
        self.assertNotEqual(self.execute(sql), [(1, 10), (2, 20)])
        self.assertEqual(compile_schema_migration_prospectively(schema(sql_source(sql))).status, 'unidentified')

    def test_alias_swap_tracks_input_not_output_alias(self):
        sql = 'INSERT INTO current (id, owner) SELECT owner AS id, id AS owner FROM legacy'
        cert = compile_schema_migration_prospectively(schema(sql_source(sql)))
        self.assertEqual(cert.status, 'withhold')
        self.assertEqual(cert.observed_mapping, (('id', 'owner'), ('owner', 'id')))
        self.assertNotEqual(self.execute(sql), [(1, 10), (2, 20)])

    def test_identity_alias_is_supported(self):
        sql = 'INSERT INTO current (id, owner) SELECT legacy.id AS id, legacy.owner AS owner FROM legacy'
        self.assertEqual(compile_schema_migration_prospectively(schema(sql_source(sql))).status, 'licensed-update')

    def test_sql_suffix_and_multiple_statements_are_not_silently_dropped(self):
        for suffix in [' WHERE id=1', '; DELETE FROM current', ' UNION SELECT id,owner FROM legacy',
                       ' LIMIT 1', ' JOIN other ON legacy.id=other.id']:
            with self.subTest(suffix=suffix):
                sql = 'INSERT INTO current (id, owner) SELECT id, owner FROM legacy' + suffix
                self.assertEqual(compile_schema_migration_prospectively(schema(sql_source(sql))).status, 'unidentified')

    def test_dead_branch_is_not_an_executed_rename(self):
        src = 'def upgrade():\n    if False:\n        op.rename_table("legacy", "current")\n'
        self.assertEqual(compile_schema_migration_prospectively(schema(src)).status, 'unidentified')

    def test_uninvoked_helper_and_downgrade_are_not_upgrade(self):
        for other in ['helper', 'downgrade']:
            src = 'def upgrade():\n    pass\ndef ' + other + '():\n    op.rename_table("legacy","current")\n'
            self.assertEqual(compile_schema_migration_prospectively(schema(src)).status, 'unidentified')

    def test_unknown_calls_shadowing_and_decorators_fail_closed(self):
        for src in ['def upgrade():\n    helper()\n    op.rename_table("legacy","current")',
                    'def upgrade():\n    op = Fake()\n    op.rename_table("legacy","current")',
                    '@skip\ndef upgrade():\n    op.rename_table("legacy","current")',
                    'op = 0\ndef upgrade():\n    op.rename_table("legacy","current")']:
            with self.subTest(source=src):
                self.assertEqual(compile_schema_migration_prospectively(schema(src)).status, 'unidentified')

    def test_operation_order_and_target_destruction_fail_closed(self):
        for src in ['def upgrade():\n    op.drop_table("legacy")\n    op.rename_table("legacy","current")',
                    'def upgrade():\n    op.rename_table("legacy","current")\n    op.drop_table("current")']:
            self.assertEqual(compile_schema_migration_prospectively(schema(src)).status, 'unidentified')

    def test_literal_rename_and_inert_module_metadata_are_supported(self):
        src = '"""migration"""\nrevision="a"\nfrom alembic import op\nimport sqlalchemy as sa\n' \
              'def upgrade():\n    op.rename_table("legacy","current")\n' \
              'def downgrade():\n    op.rename_table("current","legacy")\n'
        self.assertEqual(compile_schema_migration_prospectively(schema(src)).status, 'licensed-update')


class JavaAdmissionTests(unittest.TestCase):
    def test_preserving_action_positive_control(self):
        cert = java_cert(java_source())
        self.assertEqual(cert.status, 'licensed-update')
        self.assertTrue(cert.value_preserved)

    def test_private_helper_effect_is_propagated(self):
        cert = java_cert(java_source('erasePosition(); closed=true;', ' private void erasePosition() { position=0; }'))
        self.assertNotEqual(cert.status, 'unidentified')
        self.assertFalse(cert.value_preserved)

    def test_multihop_and_this_receiver_effect_is_propagated(self):
        cert = java_cert(java_source('this.erase(); closed=true;',
              ' private void erase() { clear(); }\n private void clear() { this.position=0; }'))
        self.assertNotEqual(cert.status, 'unidentified')
        self.assertFalse(cert.value_preserved)

    def test_unresolved_call_cannot_assert_preservation(self):
        cert = java_cert(java_source('unknown(); closed=true;'))
        self.assertEqual(cert.status, 'unidentified')
        self.assertFalse(cert.value_preserved)

    def test_recursive_call_is_unidentified_not_safe(self):
        self.assertEqual(java_cert(java_source('again(); closed=true;', ' private void again() { again(); }')).status, 'unidentified')

    def test_all_assignment_forms_are_effects(self):
        for assignment in ['++position;', '--position;', 'position *= 2;', 'position /= 2;', 'this.position = 0;', 'position <<= 1;']:
            with self.subTest(assignment=assignment):
                cert = java_cert(java_source(assignment + 'closed=true;'))
                self.assertNotEqual(cert.status, 'unidentified')
                self.assertFalse(cert.value_preserved)

    def test_comment_text_is_not_an_effect(self):
        self.assertTrue(java_cert(java_source('/* position = 0; */ closed=true;')).value_preserved)

    def test_later_shadowing_cannot_hide_an_earlier_field_write(self):
        self.assertEqual(java_cert(java_source('position=0; { int position=1; } closed=true;')).status, 'unidentified')

    def test_dynamic_helper_cannot_assert_preservation(self):
        self.assertEqual(java_cert(java_source('helper(); closed=true;', ' public void helper() {}')).status, 'unidentified')

    def test_same_arity_overload_is_not_resolved_by_name_alone(self):
        cert = java_cert(java_source('erase(1); closed=true;',
            ' private void erase(int x) { position=0; } private void erase(String x) {}'))
        self.assertEqual(cert.status, 'unidentified')

    def test_native_java_replays_helper_counterexample(self):
        self.assertIsNotNone(shutil.which('javac'), 'JDK required; missing native replay is not a pass')
        source = java_source('erasePosition(); closed=true;', ' private void erasePosition() { position=0; }')
        source = source.rsplit('}', 1)[0] + (
            ' public static void main(String[] args) { Carrier c=new Carrier(); '
            'System.out.print(c.position()+",");c.close();System.out.println(c.position()); }\n}')
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); (p/'Carrier.java').write_text(source)
            subprocess.run(['javac', str(p/'Carrier.java')], check=True, capture_output=True, timeout=30)
            result = subprocess.run(['java','-cp',tmp,'Carrier'],check=True,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.stdout.strip(), '7,0')
        self.assertFalse(java_cert(source).value_preserved)


if __name__ == '__main__':
    unittest.main()
