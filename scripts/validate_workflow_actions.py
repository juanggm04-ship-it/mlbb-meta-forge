from pathlib import Path
import sys

PAGES=Path('.github/workflows/pages.yml')
SYNC=Path('.github/workflows/sync-meta.yml')
mode=(sys.argv[1] if len(sys.argv)>1 else 'all').lower()
if mode not in ('pages','all'):
    raise SystemExit('Usage: validate_workflow_actions.py [pages|all]')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
need(PAGES.exists(),'Pages workflow missing')
need(SYNC.exists(),'Meta sync workflow missing')
pages=PAGES.read_text(encoding='utf-8') if PAGES.exists() else ''
sync=SYNC.read_text(encoding='utf-8') if SYNC.exists() else ''
required_pages={
    'actions/checkout@v7.0.1':'Pages checkout must use verified Node 24 v7.0.1',
    'actions/configure-pages@v6.0.0':'configure-pages must use Node 24 v6.0.0',
    'actions/upload-pages-artifact@v5.0.0':'upload-pages-artifact must use v5.0.0',
    'actions/deploy-pages@v5.0.1':'deploy-pages must use Node 24 v5.0.1',
}
for token,msg in required_pages.items(): need(token in pages,msg)
for old in ['actions/checkout@v4','actions/configure-pages@v5','actions/upload-pages-artifact@v3','actions/deploy-pages@v4']:
    need(old not in pages,f'Legacy Pages action reference still present: {old}')
need("path: '_site'" in pages,'Pages upload must remain scoped to the validated _site artifact')
if mode=='all':
    need('actions/checkout@v7.0.1' in sync,'Meta sync checkout must use verified Node 24 v7.0.1')
    need('actions/checkout@v4' not in sync,'Legacy checkout@v4 still present in meta sync')
if errors:
    print('WORKFLOW ACTION CONTRACT FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'Workflow action contract passed ({mode}): Pages uses checkout v7.0.1, configure-pages v6.0.0, upload-pages-artifact v5.0.0 and deploy-pages v5.0.1; _site upload preserved'+('; meta sync checkout v7.0.1.' if mode=='all' else '.'))
