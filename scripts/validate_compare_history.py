from pathlib import Path
import sys

PAGE=Path('compare/index.html')
SRC=Path('scripts/inject_compare_history.py')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
need(PAGE.exists(),'Hero Compare page missing')
need(SRC.exists(),'Compare-history source missing')
text=PAGE.read_text(encoding='utf-8') if PAGE.exists() else ''
src=SRC.read_text(encoding='utf-8') if SRC.exists() else ''
for token,msg in [
    ('id="compareRecent"','Recent compare panel missing'),
    ('id="compareRecentList"','Recent compare list missing'),
    ('id="compareRecentClear"','Recent compare clear action missing'),
    ('id="compare-recent-script"','Recent compare runtime missing'),
    ("KEY='mf_compare_recent_v1'",'Recent compare localStorage key missing'),
    ('MAX=6','Recent compare history is not capped at six'),
    (".sort((m,n)=>m.localeCompare(n)).join(':::')",'Unordered pair key missing'),
    ("rows.filter(r=>r&&r.key!==key)",'Recent compare deduplication missing'),
    ("rows.unshift({a:x,b:y,key,ts:Date.now()})",'Recent compare orientation/timestamp record missing'),
    ("u.searchParams.set('a',r.a)",'Recent compare A route missing'),
    ("u.searchParams.set('b',r.b)",'Recent compare B route missing'),
    ("localStorage.removeItem(KEY)",'Clear-history behavior missing'),
    ('Se guarda solo en este navegador','Local-only disclosure missing'),
]: need(token in text or token in src,msg)
need('fetch(' not in src and 'XMLHttpRequest' not in src,'Recent compare history must not send network requests')
if errors:
    print('COMPARE HISTORY VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Hero Compare recent-history validation passed: max 6, unordered-pair dedupe, shareable pair links and local-only storage.')
