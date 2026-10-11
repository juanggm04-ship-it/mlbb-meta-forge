from pathlib import Path
import sys

ROSTER=Path('roster/index.html')
errors=[]

def need(cond,msg):
    if not cond: errors.append(msg)

need(ROSTER.exists(),'roster/index.html missing')
if ROSTER.exists():
    text=ROSTER.read_text(encoding='utf-8')
    checks=[
        ('id="roster-pair-compare-style"','Pair-compare CSS missing'),
        ('id="roster-pair-compare-script"','Pair-compare runtime missing'),
        ('id="rosterCompareTray"','Pair-compare tray missing'),
        ('id="rosterCompareSlotA"','Hero A slot missing'),
        ('id="rosterCompareSlotB"','Hero B slot missing'),
        ('id="rosterCompareSelected"','Compare-selected CTA missing'),
        ('id="rosterCompareClear"','Clear-selection control missing'),
        ('aria-live="polite"','Accessible pair-selection status missing'),
        ("const selected=[]",'Temporary selection state missing'),
        ("selected.length<2",'Pair selection is not capped at two heroes'),
        ("Ya hay 2 héroes seleccionados. Quita uno antes de elegir otro.",'Third-selection warning missing'),
        ("selected.splice(i,1)",'Selected hero cannot be removed individually'),
        ("selected.length=0",'Clear action does not reset selection'),
        ("go.href='../compare/?a='+encodeURIComponent(selected[0])+'&b='+encodeURIComponent(selected[1])",'Direct two-hero Compare route missing'),
        ("b.dataset.compareSelect",'Selection buttons do not bind to hero identity'),
        ("new MutationObserver(enhanceCards).observe(grid,{childList:true})",'Dynamic cards are not re-enhanced after Roster renders'),
        ('Esta selección es temporal y no modifica tu Watchlist.','Selection-vs-Watchlist disclosure missing'),
    ]
    for token,msg in checks: need(token in text,msg)
    need("setWatch(" not in text[text.find('id="roster-pair-compare-script"'):], 'Pair-compare runtime must not mutate Watchlist state')
    need('data-compare-select' in text,'Pair-selection control marker missing')
    need('aria-disabled="true"' in text,'Compare CTA does not start disabled')

if errors:
    print('ROSTER PAIR COMPARE VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Roster pair-compare validation passed: temporary max-2 selection, accessible tray, direct Hero Compare route, Watchlist untouched.')
