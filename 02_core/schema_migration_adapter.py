"""Prospective relation-transport compiler for literal Alembic and SQL syntax."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from hashlib import sha256
import re


@dataclass(frozen=True)
class SchemaMigrationEpisode:
    episode_id: str
    repository: str
    parent_commit: str
    action_commit: str
    source_table: str
    target_table: str
    registered_columns: tuple[str, ...]
    migration_source: str


@dataclass(frozen=True)
class SchemaMigrationProspective:
    episode_id: str
    evidence_digest: str
    status: str
    selected_action: str
    transport_kind: str
    observed_mapping: tuple[tuple[str, str], ...]
    cleanup_detected: bool
    unsupported_reason: str


# Admission v2 is an explicit bounded language, not arbitrary SQL/Alembic.
# Preconditions: trusted op binding, declared schema, successful execution,
# empty INSERT destination, no triggers/value-changing casts/concurrent writes.
_IDENTIFIER = r'(?:[A-Za-z_][A-Za-z_0-9]*|"[A-Za-z_][A-Za-z_0-9]*"|`[A-Za-z_][A-Za-z_0-9]*`)'
_INSERT_SELECT = re.compile(
    rf"INSERT\s+INTO\s+(?P<target>{_IDENTIFIER})\s*"
    rf"\((?P<tcols>[^()]+)\)\s*SELECT\s+(?P<scols>[^;]+?)\s+FROM\s+"
    rf"(?P<source>{_IDENTIFIER})\s*;?\s*", re.IGNORECASE | re.DOTALL)
_COLUMN = re.compile(
    rf"(?:(?P<table>{_IDENTIFIER})\s*\.\s*)?(?P<column>{_IDENTIFIER})"
    rf"(?:\s+AS\s+{_IDENTIFIER})?", re.IGNORECASE)


def _literal_string(node: ast.AST) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _op_name(call: ast.Call) -> str:
    if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Name):
        if call.func.value.id == 'op':
            return call.func.attr
    return ''


def _digest(episode: SchemaMigrationEpisode) -> str:
    payload = '\0'.join(('schema-admission-v2', episode.episode_id, episode.repository,
        episode.parent_commit, episode.action_commit, episode.source_table,
        episode.target_table, ','.join(episode.registered_columns), episode.migration_source))
    return sha256(payload.encode('utf-8')).hexdigest()


def _identifier(text: str) -> str:
    text = text.strip()
    if not re.fullmatch(_IDENTIFIER, text):
        raise ValueError('unsupported SQL identifier')
    return text.strip('"`')


def _mapping(sql: str, episode: SchemaMigrationEpisode) -> tuple[tuple[str, str], ...]:
    match = _INSERT_SELECT.fullmatch(sql.strip())
    if not match:
        raise ValueError('SQL is not a single unfiltered INSERT/SELECT projection')
    if (_identifier(match['source']), _identifier(match['target'])) != (
            episode.source_table, episode.target_table):
        raise ValueError('SQL relation is outside the registered transport')
    targets = [_identifier(x) for x in match['tcols'].split(',')]
    sources = []
    for expression in match['scols'].split(','):
        column = _COLUMN.fullmatch(expression.strip())
        if not column:
            raise ValueError('SQL expressions are not column identity projections')
        if column['table'] and _identifier(column['table']) != episode.source_table:
            raise ValueError('unregistered source qualifier')
        sources.append(_identifier(column['column']))
    if len(targets) != len(sources) or len(set(targets)) != len(targets):
        raise ValueError('SQL projection arity or duplicate target')
    if set(targets) != set(episode.registered_columns):
        raise ValueError('projection does not cover exactly the registered columns')
    if not set(sources).issubset(episode.registered_columns):
        raise ValueError('projection uses an undeclared source column')
    # AS names outputs; INSERT binds target columns by position.
    return tuple(sorted(zip(targets, sources)))


def _upgrade_calls(source: str) -> list[ast.Call]:
    tree = ast.parse(source)
    upgrade = None
    metadata = {'revision', 'down_revision', 'branch_labels', 'depends_on'}
    for node in tree.body:
        if isinstance(node, ast.Expr) and _literal_string(node.value) is not None:
            continue
        if isinstance(node, ast.ImportFrom):
            if (node.level == 0 and node.module == 'alembic' and len(node.names) == 1
                    and node.names[0].name == 'op' and node.names[0].asname in (None, 'op')):
                continue
            raise ValueError('unsupported module import or op binding')
        if isinstance(node, ast.Import):
            if all(x.name == 'sqlalchemy' and x.asname in (None, 'sa') for x in node.names):
                continue
            raise ValueError('unsupported module import')
        if isinstance(node, ast.Assign):
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                raise ValueError('unsupported module assignment')
            if node.targets[0].id not in metadata:
                raise ValueError('module assignment may change execution bindings')
            ast.literal_eval(node.value)
            continue
        if isinstance(node, ast.FunctionDef):
            if node.name == 'op' or node.decorator_list or node.returns is not None:
                raise ValueError('function binding, decorator or annotation is unsupported')
            args = node.args
            if args.defaults or args.kw_defaults or any(a.annotation is not None for a in
                    args.posonlyargs + args.args + args.kwonlyargs):
                raise ValueError('function defaults/annotations outside module contract')
            if node.name == 'upgrade':
                if upgrade is not None or args.posonlyargs or args.args or args.kwonlyargs or args.vararg or args.kwarg:
                    raise ValueError('expected one zero-argument upgrade')
                upgrade = node
            continue
        raise ValueError('module statement outside admitted execution grammar')
    if upgrade is None:
        raise ValueError('no upgrade entry point')
    calls = []
    for node in upgrade.body:
        if isinstance(node, ast.Pass):
            continue
        if isinstance(node, ast.Expr) and _literal_string(node.value) is not None:
            continue
        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
            raise ValueError('upgrade must be straight-line literal op calls')
        call = node.value
        if not _op_name(call) or call.keywords or any(isinstance(x, ast.Starred) for x in call.args):
            raise ValueError('unknown call, keyword or dynamic argument expansion')
        if any(_literal_string(x) is None for x in call.args):
            raise ValueError('op arguments must be literal strings')
        calls.append(call)
    return calls


def compile_schema_migration_prospectively(episode: SchemaMigrationEpisode) -> SchemaMigrationProspective:
    digest = _digest(episode)
    cleanup = False
    try:
        if (not episode.registered_columns or len(set(episode.registered_columns)) != len(episode.registered_columns)
                or episode.source_table == episode.target_table):
            raise ValueError('invalid registered relation contract')
        for name in (*episode.registered_columns, episode.source_table, episode.target_table):
            if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', name):
                raise ValueError('invalid registered identifier')
        calls = _upgrade_calls(episode.migration_source)
        if not calls:
            raise ValueError('no registered transport in upgrade')
        first = calls[0]
        name = _op_name(first)
        args = tuple(_literal_string(x) for x in first.args)
        if name == 'rename_table' and args == (episode.source_table, episode.target_table):
            if len(calls) != 1:
                raise ValueError('unmodelled operation before/after rename')
            mapping = tuple(sorted((x, x) for x in episode.registered_columns))
            kind = 'literal-rename'
        elif name == 'execute' and len(args) == 1:
            mapping = _mapping(args[0], episode)
            kind = 'literal-insert-select'
            if len(calls) == 2:
                last = calls[1]
                if _op_name(last) != 'drop_table' or tuple(_literal_string(x) for x in last.args) != (episode.source_table,):
                    raise ValueError('unmodelled effect following INSERT/SELECT')
                cleanup = True
            elif len(calls) != 1:
                raise ValueError('multiple transports or extra operations')
        else:
            raise ValueError('no admitted registered transport as first operation')
    except (SyntaxError, ValueError, TypeError, RecursionError) as exc:
        return SchemaMigrationProspective(episode.episode_id, digest, 'unidentified', 'hold',
                                          'unsupported', (), cleanup, str(exc))
    identity = all(target == source for target, source in mapping)
    return SchemaMigrationProspective(episode.episode_id, digest,
        'licensed-update' if identity else 'withhold', 'cutover' if identity else 'hold',
        kind if identity else 'mismatched-literal-transport', mapping, cleanup, '')


def verify_schema_migration_prospective(episode: SchemaMigrationEpisode,
        certificate: SchemaMigrationProspective) -> tuple[bool, str]:
    """Check deterministic certificate consistency, NOT independent semantics."""
    expected = compile_schema_migration_prospectively(episode)
    if expected != certificate:
        return False, 'schema migration prospective certificate mismatch'
    return True, 'schema certificate consistency verified; semantic preconditions remain explicit'
