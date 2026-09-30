"""Compile lineage ambiguity from real before/after DDL snapshots.

Identical table structure before and after a name change does not identify
whether rows were preserved.  This component emits two explicit compatible
migration mechanisms and a query witness whenever schema snapshots alone leave
row lineage unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re


@dataclass(frozen=True)
class ColumnDefinition:
    name: str
    definition: str


@dataclass(frozen=True)
class TableSnapshot:
    name: str
    columns: tuple[ColumnDefinition, ...]


@dataclass(frozen=True)
class DDLVersionSnapshot:
    source_id: str
    sha256: str
    tables: tuple[TableSnapshot, ...]


@dataclass(frozen=True)
class LineageCountermodel:
    name: str
    operation: str
    preserved_row_count: int


@dataclass(frozen=True)
class SchemaLineageAmbiguityCertificate:
    old_source_id: str
    new_source_id: str
    old_sha256: str
    new_sha256: str
    removed_table: str
    added_table: str
    structural_signature: tuple[ColumnDefinition, ...]
    candidate_mechanisms: tuple[LineageCountermodel, ...]
    witness_claim: str
    witness_answers: tuple[int, ...]
    row_lineage_identified: bool


_CREATE_TABLE = re.compile(
    r"CREATE\s+TABLE\s+[`\"']?([A-Za-z0-9_]+)[`\"']?\s*\((.*?)\)\s*;",
    re.IGNORECASE | re.DOTALL,
)


def _normalize_definition(value: str) -> str:
    return " ".join(value.strip().rstrip(",").lower().split())


def parse_ddl_snapshot(source_id: str, ddl_text: str) -> DDLVersionSnapshot:
    if not source_id or not ddl_text.strip():
        raise ValueError("empty DDL source")
    tables = []
    for match in _CREATE_TABLE.finditer(ddl_text):
        columns = []
        for raw_line in match.group(2).splitlines():
            line = raw_line.strip()
            if not line or line.startswith(("#", "--")):
                continue
            upper = line.upper()
            if upper.startswith(("PRIMARY KEY", "KEY ", "UNIQUE ", "CONSTRAINT ")):
                continue
            parts = line.rstrip(",").split(None, 1)
            if len(parts) != 2:
                continue
            name = parts[0].strip("`\"'")
            columns.append(ColumnDefinition(name, _normalize_definition(parts[1])))
        tables.append(TableSnapshot(match.group(1), tuple(columns)))
    if not tables:
        raise ValueError("DDL source contains no CREATE TABLE statement")
    if len({table.name for table in tables}) != len(tables):
        raise ValueError("DDL source contains duplicate table definitions")
    return DDLVersionSnapshot(
        source_id,
        sha256(ddl_text.encode("utf-8")).hexdigest(),
        tuple(sorted(tables, key=lambda table: table.name)),
    )


def _structural_signature(table: TableSnapshot) -> tuple[ColumnDefinition, ...]:
    return table.columns


def compile_schema_lineage_ambiguities(
    old: DDLVersionSnapshot,
    new: DDLVersionSnapshot,
) -> tuple[SchemaLineageAmbiguityCertificate, ...]:
    old_by_name = {table.name: table for table in old.tables}
    new_by_name = {table.name: table for table in new.tables}
    removed = [old_by_name[name] for name in sorted(set(old_by_name) - set(new_by_name))]
    added = [new_by_name[name] for name in sorted(set(new_by_name) - set(old_by_name))]
    certificates = []
    for old_table in removed:
        for new_table in added:
            signature = _structural_signature(old_table)
            if signature != _structural_signature(new_table):
                continue
            mechanisms = (
                LineageCountermodel(
                    "preserving-rename-or-copy",
                    f"preserve rows from {old_table.name} into {new_table.name}",
                    1,
                ),
                LineageCountermodel(
                    "destructive-drop-create",
                    f"drop {old_table.name}; create empty {new_table.name}",
                    0,
                ),
            )
            certificates.append(
                SchemaLineageAmbiguityCertificate(
                    old.source_id,
                    new.source_id,
                    old.sha256,
                    new.sha256,
                    old_table.name,
                    new_table.name,
                    signature,
                    mechanisms,
                    f"does a registered pre-migration row survive in {new_table.name}?",
                    tuple(item.preserved_row_count for item in mechanisms),
                    False,
                )
            )
    return tuple(certificates)


def verify_schema_lineage_ambiguity(
    old: DDLVersionSnapshot,
    new: DDLVersionSnapshot,
    certificate: SchemaLineageAmbiguityCertificate,
) -> tuple[bool, str]:
    expected = compile_schema_lineage_ambiguities(old, new)
    if certificate not in expected:
        return False, "schema lineage ambiguity certificate mismatch"
    if len(set(certificate.witness_answers)) < 2:
        return False, "countermodels do not disagree on the witness claim"
    if certificate.row_lineage_identified:
        return False, "ambiguous snapshot was marked identified"
    return True, "schema lineage ambiguity certificate verified"

