from pathlib import Path
import sys

PAGE=Path('compare/index.html')
SRC=Path('scripts/enhance_compare_signals.py')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
need(PAGE.exists(),'compare/index.html missing')
need(SRC.exists(),'Compare signal source missing')
text=PAGE.read_text(encoding='utf-8') if PAGE.exists() else ''
src=SRC.read_text(encoding='utf-8') if SRC.exists() else ''
for token,msg in [
    ('id="compareSignalSummary"','Compare signal summary missing'),
    ('id="compareSignalGrid"','Compare signal grid missing'),
    ('id="compare-signal-script"','Compare signal runtime missing'),
    ("winner(x,y,'wr')",'WR delta signal missing'),
    ("winner(x,y,'pick')",'Pick delta signal missing'),
    ("winner(x,y,'ban')",'Ban delta signal missing'),
    ("winner(x,y,'score')",'Meta Score delta signal missing'),
    ('momentum_observed===true','Momentum history-readiness guard missing'),
    ('Aún no hay historial suficiente para interpretar momentum','Neutral momentum fallback missing'),
    ('No convierten WR, pick, ban o Meta Score en una recomendación automática de pick','No-pick-recommendation disclaimer missing'),
    ("a.addEventListener('change'",'Hero A reactive update missing'),
    ("b.addEventListener('change'",'Hero B reactive update missing'),
]: need(token in text or token in src,msg)
if errors:
    print('COMPARE SIGNAL VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Hero Compare signal validation passed: WR/pick/ban/Meta Score deltas, momentum readiness and neutral non-recommendation framing are present.')
