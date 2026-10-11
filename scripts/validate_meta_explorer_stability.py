from pathlib import Path
import sys

PAGE = Path('explore/index.html')
errors = []
def need(cond, msg):
    if not cond:
        errors.append(msg)

need(PAGE.exists(), 'Meta Explorer page missing')
if PAGE.exists():
    text = PAGE.read_text(encoding='utf-8')
    need('content="event-driven-v1"' in text, 'Explorer stability marker missing')
    need("mf:explorer-drawn" in text, 'Explicit redraw event missing')
    need("requestAnimationFrame(draw)" in text, 'Search redraw is not requestAnimationFrame-debounced')
    need("cancelAnimationFrame(explorerSearchFrame)" in text, 'Search redraw cancellation guard missing')
    need("svg.addEventListener('mf:explorer-drawn',syncVisibility)" in text, 'Power tools are not event-driven')
    need("svg.addEventListener('mf:explorer-drawn',upgrade)" in text, 'Keyboard upgrade is not event-driven')
    need('MutationObserver' not in text, 'Meta Explorer still contains a MutationObserver')

if errors:
    print('META EXPLORER STABILITY VALIDATION FAILED')
    for e in errors:
        print('- ' + e)
    sys.exit(1)
print('Meta Explorer stability validation passed: zero MutationObserver usage, explicit redraw event and RAF-debounced search.')
