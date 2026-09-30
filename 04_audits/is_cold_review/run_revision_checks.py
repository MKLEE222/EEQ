"""Run only this bounded repair gate; do not imply the whole repository passed."""
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / '02_core'
sys.path.insert(0, str(CORE))
OUT = ROOT / 'is-revision-evidence'
OUT.mkdir(exist_ok=True)
FILES = ['qualification_opportunity_compiler.py', 'schema_history_lineage_ambiguity_v0.py',
         'LifecycleSourceFacts.java', 'java_source_facts.py',
         'lifecycle_qualification_compiler.py', 'schema_migration_adapter.py',
         'java_lifecycle_adapter.py', 'test_prefreeze_adapters.py', 'test_is_source_admission.py']
started = time.monotonic()
with (OUT / 'tests.log').open('w', encoding='utf-8') as log:
    suite = unittest.defaultTestLoader.loadTestsFromNames(
        ['test_prefreeze_adapters', 'test_is_source_admission'])
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
summary = {
    'kind': 'synthetic_source_admission_repair_gate_not_natural_prevalence',
    'commit': os.environ.get('GITHUB_SHA'),
    'python': platform.python_version(),
    'tests_run': result.testsRun, 'failures': len(result.failures),
    'errors': len(result.errors), 'skipped': len(result.skipped),
    'success': result.wasSuccessful() and not result.skipped and result.testsRun == 35,
    'elapsed_seconds': time.monotonic() - started,
    'source_sha256': {name: hashlib.sha256((CORE/name).read_bytes()).hexdigest() for name in FILES},
    'not_claimed': ['whole_repository_pass', 'independent_4500_algorithm_validation',
                    'cross_system_prevalence', 'full_A1_A5_source_correspondence']}
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
print((OUT/'tests.log').read_text())
print(json.dumps(summary,indent=2))
raise SystemExit(0 if summary['success'] else 1)
