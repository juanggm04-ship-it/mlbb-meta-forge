from pathlib import Path
import sys

TARGETS={
    'roster/index.html':'Roster',
    'trends/index.html':'Trends',
    'compare/index.html':'Comparar',
    'my-meta/index.html':'Mi Meta',
}
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

for path,label in TARGETS.items():
    p=Path(path)
    need(p.exists(),f'Missing product-nav target: {path}')
    if not p.exists(): continue
    text=p.read_text(encoding='utf-8')
    need('id="productShellNav"' in text,f'Product shell nav missing on {path}')
    need('id="product-shell-nav-style"' in text,f'Product shell nav styles missing on {path}')
    need(f'>{label}</a>' in text,f'Current route label missing on {path}')
    need('aria-current="page"' in text,f'Current route state missing on {path}')
    for token in ['Roster</a>','Trends</a>','Comparar</a>','Mi Meta</a>','Metodología</a>']:
        need(token in text,f'Navigation item {token} missing on {path}')
    need('href="../methodology.html"' in text,f'Methodology route missing on {path}')

if errors:
    print('PRODUCT SHELL NAV VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Product shell navigation validation passed: Roster, Trends, Compare and My Meta expose consistent navigation with active-route state and methodology access.')
