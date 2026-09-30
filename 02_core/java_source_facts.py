"""Parse-only JDK bridge. Unknown effects fail closed; source is never executed.

Assumes well-typed input, successful action completion, declared receiver class,
no concurrent/reflection/native mutation, and field-value (not deep heap) claims.
"""
from functools import lru_cache
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

_COMPILED = None


def _tool(name):
    path = shutil.which(name)
    if path is None:
        raise ValueError('Java source admission requires a JDK: missing ' + name)
    return path


def _classes():
    global _COMPILED
    if _COMPILED is None:
        helper = Path(__file__).with_name('LifecycleSourceFacts.java')
        if not helper.is_file():
            raise ValueError('Java AST analyzer is missing from this package')
        temporary = tempfile.TemporaryDirectory(prefix='eeq_ast_')
        try:
            subprocess.run([_tool('javac'), '-encoding', 'UTF-8', '-d', temporary.name,
                            str(helper)], check=True, capture_output=True, timeout=30)
        except (subprocess.SubprocessError, OSError) as exc:
            temporary.cleanup()
            raise ValueError('Cannot compile the bundled Java AST analyzer') from exc
        _COMPILED = temporary
    return _COMPILED.name


@lru_cache(maxsize=32)
def _analyze_json(source: str, class_name: str) -> str:
    if len(source.encode('utf-8')) > 2_000_000:
        raise ValueError('Source exceeds the bounded analyzer input limit')
    with tempfile.TemporaryDirectory(prefix='eeq_source_') as tmp:
        path = Path(tmp) / 'Input.java'
        path.write_text(source, encoding='utf-8')
        try:
            result = subprocess.run([_tool('java'), '-Xmx128m', '-cp', _classes(),
                'LifecycleSourceFacts', str(path), class_name], check=True,
                capture_output=True, text=True, encoding='utf-8', timeout=15)
        except subprocess.CalledProcessError as exc:
            reason = (exc.stderr or 'Java source admission failed').splitlines()[0][:300]
            raise ValueError(reason) from exc
        except (subprocess.TimeoutExpired, OSError) as exc:
            raise ValueError('Java source analyzer could not complete') from exc
    return result.stdout


def analyze_java_source(source: str, class_name: str = '*') -> dict:
    return json.loads(_analyze_json(source, class_name))
