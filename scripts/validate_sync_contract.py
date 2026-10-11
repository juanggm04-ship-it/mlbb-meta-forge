from pathlib import Path
import importlib.util, sys

WORKFLOW=Path('.github/workflows/sync-meta.yml')
SCRIPT=Path('scripts/sync_public_meta.py')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
need(WORKFLOW.exists(),'sync-meta workflow missing')
need(SCRIPT.exists(),'sync_public_meta.py missing')
workflow=WORKFLOW.read_text(encoding='utf-8') if WORKFLOW.exists() else ''
source=SCRIPT.read_text(encoding='utf-8') if SCRIPT.exists() else ''
need("cron: '30 23 * * *'" in workflow,'Meta sync is not scheduled daily at 23:30 UTC')
need('patch_version_key' in source,'Numeric patch version parser missing')
need('return max(numeric' in source,'Latest patch no longer selects the highest numeric version')
if SCRIPT.exists():
    spec=importlib.util.spec_from_file_location('sync_public_meta',SCRIPT)
    mod=importlib.util.module_from_spec(spec)
    sys.path.insert(0,str(SCRIPT.parent))
    try:
        spec.loader.exec_module(mod)
        cases=[
            ([{'version':'2.9.9'},{'version':'2.10.0'},{'version':'2.2.16'}],'2.10.0'),
            ({'data':[{'name':'Patch 3.0.1'},{'name':'Patch 2.99.9'}]},'Patch 3.0.1'),
            (['1.5.0','1.12.0','1.9.7'],'1.12.0'),
        ]
        for payload,expected in cases:
            got=mod.latest_patch(payload)
            need(got==expected,f'latest_patch({payload}) returned {got!r}, expected {expected!r}')
    except Exception as exc:
        errors.append(f'Could not execute sync contract tests: {exc}')
if errors:
    print('SYNC CONTRACT VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Sync contract validation passed: daily schedule and provider-order-independent numeric patch selection are enforced.')
