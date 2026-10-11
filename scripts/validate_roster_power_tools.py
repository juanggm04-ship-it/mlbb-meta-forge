from pathlib import Path
import sys

ROSTER=Path('roster/index.html')
SRC=Path('scripts/enhance_roster_power_tools.py')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
need(ROSTER.exists(),'roster/index.html missing')
need(SRC.exists(),'Roster power-tools source missing')
text=ROSTER.read_text(encoding='utf-8') if ROSTER.exists() else ''
src=SRC.read_text(encoding='utf-8') if SRC.exists() else ''
for token,msg in [
    ('id="rosterPowerTools"','Roster power-tools panel missing'),
    ('id="rosterCopyView"','Copy-view action missing'),
    ('id="rosterExportCsv"','CSV export action missing'),
    ('id="rosterResetView"','Reset-view action missing'),
    ('id="rosterPowerStatus"','Accessible power-tools status missing'),
    ('id="roster-power-tools-script"','Roster power-tools runtime missing'),
    ('id="roster-power-tools-style"','Roster power-tools CSS missing'),
    ('URLSearchParams','Shareable URL parsing missing'),
    ("searchParams.set('q'",'Shareable search param missing'),
    ("searchParams.set('sort'",'Shareable sort param missing'),
    ("searchParams.set('filter'",'Shareable filter param missing'),
    ('history.replaceState','URL synchronization missing'),
    ("new Set(['score','wr','ban','pick','name'])",'Valid sort allowlist missing'),
    ("new Set(['all','watch','editorial','top20'])",'Valid filter allowlist missing'),
    ("localStorage.getItem('mf_watchlist_v1')",'Watch filter does not read shared Watchlist'),
    ("f==='top20'&&Number(h.rank)<=20",'CSV Top 20 scope is not canonical Meta rank'),
    ("['MetaRank','Hero','MetaScore','WR_pp','Ban_pp','Pick_pp','Coverage']",'CSV header contract missing'),
    ("new Blob([csvText()]",'CSV Blob export missing'),
    ("'\\ufeff'",'CSV UTF-8 BOM missing'),
    ("/^[=+\\-@]/",'Spreadsheet formula-injection protection missing'),
    ('“Siguiendo” siempre usa la Watchlist local','Watch-filter sharing disclosure missing'),
    ("['q','sort','filter'].forEach",'Reset does not clear all shareable params'),
]: need(token in text or token in src,msg)
start=text.find('id="roster-power-tools-script"')
if start>=0:
    runtime=text[start:]
    need("localStorage.setItem('mf_watchlist_v1'" not in runtime,'Power tools must not mutate Watchlist storage')
if errors:
    print('ROSTER POWER TOOLS VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Roster power-tools validation passed: q/sort/filter URL state, local Watchlist semantics, safe current-view CSV export and reset behavior.')
