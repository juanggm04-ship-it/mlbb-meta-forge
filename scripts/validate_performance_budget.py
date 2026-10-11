from pathlib import Path
import sys

ROOT=Path('.')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
def kb(p):
    return p.stat().st_size/1024 if p.exists() else 0

key_limits={
    Path('index.html'):750,
    Path('roster/index.html'):650,
    Path('trends/index.html'):750,
    Path('compare/index.html'):550,
    Path('my-meta/index.html'):650,
    Path('status/index.html'):180,
}
for p,limit in key_limits.items():
    need(p.exists(),f'Missing key page: {p}')
    if p.exists(): need(kb(p)<=limit,f'{p} exceeds {limit} KiB budget: {kb(p):.1f} KiB')

html_pages=[p for p in ROOT.rglob('*.html') if '.git' not in p.parts]
need(len(html_pages)>=170,f'Expected at least 170 generated HTML pages, got {len(html_pages)}')
if html_pages:
    total=sum(p.stat().st_size for p in html_pages)/1024/1024
    need(total<=20,f'Total generated HTML exceeds 20 MiB budget: {total:.2f} MiB')
else:
    total=0

stat_pages=list(Path('stats/heroes').glob('*/index.html')) if Path('stats/heroes').exists() else []
need(len(stat_pages)==133,f'Expected 133 live hero pages, got {len(stat_pages)}')
if stat_pages:
    largest=max(stat_pages,key=lambda p:p.stat().st_size)
    need(kb(largest)<=300,f'Largest live hero page exceeds 300 KiB budget: {largest} = {kb(largest):.1f} KiB')
else:
    largest=None

asset_limits={
    Path('data/live-meta.json'):1024,
    Path('data/meta-score.json'):1024,
    Path('data/meta-score-history.json'):1536,
    Path('data/build-info.json'):64,
    Path('sw.js'):256,
    Path('assets/social-card.png'):500,
}
for p,limit in asset_limits.items():
    need(p.exists(),f'Missing performance-budget asset: {p}')
    if p.exists(): need(kb(p)<=limit,f'{p} exceeds {limit} KiB budget: {kb(p):.1f} KiB')

for p in html_pages:
    text=p.read_text(encoding='utf-8',errors='ignore')
    need('data:image/png;base64,' not in text and 'data:image/jpeg;base64,' not in text,
         f'Inline raster base64 image found in {p}; use a static asset instead')

if errors:
    print('PERFORMANCE BUDGET FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Performance budget passed: '
      + ', '.join(f'{p}={kb(p):.1f}KiB' for p in key_limits if p.exists())
      + f'; html_pages={len(html_pages)}; total_html={total:.2f}MiB; social_card={kb(Path("assets/social-card.png")):.1f}KiB; build_info={kb(Path("data/build-info.json")):.1f}KiB; '
      + (f'largest_stat={largest} ({kb(largest):.1f}KiB)' if largest else 'largest_stat=none'))
