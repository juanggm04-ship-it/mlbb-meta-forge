from pathlib import Path
import sys

CORE_TARGETS={
    'roster/index.html':('Roster','../methodology.html'),
    'trends/index.html':('Trends','../methodology.html'),
    'compare/index.html':('Comparar','../methodology.html'),
    'my-meta/index.html':('Mi Meta','../methodology.html'),
    'methodology.html':('Metodología','./methodology.html'),
}
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

for path,(label,method_route) in CORE_TARGETS.items():
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
    need(f'href="{method_route}"' in text,f'Methodology route missing on {path}')

stat_pages=sorted(Path('stats/heroes').glob('*/index.html'))
need(len(stat_pages)==133,f'Expected 133 live hero pages for product nav, found {len(stat_pages)}')
for p in stat_pages:
    text=p.read_text(encoding='utf-8')
    need('id="productShellNav"' in text,f'Product shell nav missing on {p}')
    need('href="../../../roster/" aria-current="page">Roster</a>' in text,f'Roster context not active on {p}')
    need('href="../../../trends/"' in text,f'Trends route missing on {p}')
    need('href="../../../compare/"' in text,f'Compare route missing on {p}')
    need('href="../../../my-meta/"' in text,f'My Meta route missing on {p}')
    need('href="../../../methodology.html"' in text,f'Methodology route missing on {p}')

if errors:
    print('PRODUCT SHELL NAV VALIDATION FAILED')
    for e in errors[:60]: print('- '+e)
    if len(errors)>60: print(f'- ... and {len(errors)-60} more')
    sys.exit(1)
print(f'Product shell navigation validation passed: 5 core surfaces plus {len(stat_pages)} live hero pages share consistent navigation and route context.')
