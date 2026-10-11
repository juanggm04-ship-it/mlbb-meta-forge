from pathlib import Path
import sys
PAGE=Path('explore/index.html')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
need(PAGE.exists(),'Meta Explorer page missing')
if PAGE.exists():
    text=PAGE.read_text(encoding='utf-8')
    for token,msg in [
        ('id="explorerPowerTools"','Explorer power-tools bar missing'),
        ('data-explorer-scope="all"','All scope missing'),
        ('data-explorer-scope="watch"','Watchlist scope missing'),
        ('data-explorer-scope="editorial"','Editorial scope missing'),
        ('data-explorer-scope="top20"','Top20 scope missing'),
        ('id="explorerVisibleCount"','Visible counter missing'),
        ('id="explorerPairTray"','A/B tray missing'),
        ('id="explorerPairA"','Pair slot A missing'),
        ('id="explorerPairB"','Pair slot B missing'),
        ('id="explorerAddSelected"','Add-selection control missing'),
        ('id="explorerClearPair"','Pair clear control missing'),
        ('id="explorerComparePair"','Pair compare link missing'),
        ('id="explorer-power-runtime"','Explorer power runtime missing'),
        ("WATCH_KEY='mf_watchlist_v1'",'Explorer does not reuse shared Watchlist key'),
        ("scope==='watch'",'Watchlist filtering missing'),
        ("scope==='editorial'",'Editorial filtering missing'),
        ("scope==='top20'",'Top20 filtering missing'),
        ('row.rank<=20','Top20 must use canonical Meta Score rank'),
        ('pair.length>=2','Pair hard limit of 2 missing'),
        ('pair.includes(current)','Pair duplicate guard missing'),
        ('../compare/?a=${encodeURIComponent(pair[0])}&b=${encodeURIComponent(pair[1])}','Direct A/B Compare route missing'),
        ('MutationObserver','Explorer redraw synchronization missing'),
        ("window.addEventListener('storage'",'Cross-tab Watchlist sync missing'),
    ]: need(token in text,msg)
    need('localStorage.setItem' not in text.split('id="explorer-power-runtime"',1)[1],'Explorer power tools must not mutate Watchlist localStorage')
if errors:
    print('META EXPLORER POWER TOOLS VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Meta Explorer power tools validation passed: all/watch/editorial/top20 scopes, canonical Top20, shared read-only Watchlist, max-2 pair selection and direct Hero Compare route.')
