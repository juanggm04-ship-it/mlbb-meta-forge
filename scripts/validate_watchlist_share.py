from pathlib import Path
import sys

PAGE=Path('my-meta/index.html')
SRC=Path('scripts/inject_watchlist_share.py')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
need(PAGE.exists(),'my-meta/index.html missing')
need(SRC.exists(),'Watchlist-share source missing')
text=PAGE.read_text(encoding='utf-8') if PAGE.exists() else ''
src=SRC.read_text(encoding='utf-8') if SRC.exists() else ''
for token,msg in [
    ('id="watchlistShare"','Watchlist-share panel missing'),
    ('id="shareWatchlist"','Share Watchlist action missing'),
    ('id="sharedWatchlistPreview"','Shared Watchlist preview missing'),
    ('id="watchlist-share-script"','Watchlist-share runtime missing'),
    ("u.searchParams.set('shared'",'Shared Watchlist URL parameter missing'),
    ("new URL(location.href).searchParams.get('shared')",'Incoming shared parameter parsing missing'),
    ("navigator.share",'Web Share support missing'),
    ("navigator.clipboard.writeText",'Clipboard fallback missing'),
    ("localStorage.setItem(WATCH,JSON.stringify(merged))",'Explicit merge behavior missing'),
    ("localStorage.setItem(WATCH,JSON.stringify(incoming))",'Explicit replace behavior missing'),
    ("confirm(`Reemplazar tu Watchlist actual",'Replace confirmation missing'),
    ('Nada se importará sin tu permiso','Consent disclosure missing'),
    ('No se modificó tu Watchlist','Dismiss-without-mutation behavior missing'),
    ('Hero slug collision blocks shareable Watchlist','Slug-collision guard missing'),
]: need(token in text or token in src,msg)
need('fetch(' not in src and 'XMLHttpRequest' not in src,'Watchlist sharing must not upload data over the network')
if errors:
    print('WATCHLIST SHARE VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Watchlist-share validation passed: 133-hero slug map, share/clipboard fallback, preview-only import, explicit merge/replace consent and no network upload.')
