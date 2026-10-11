from pathlib import Path
import json,re,sys,html as htmlmod

LIVE=Path('data/live-meta.json')
ROSTER=Path('roster/index.html')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

def valid(v): return isinstance(v,(int,float)) and not isinstance(v,bool)
def top(rows,key,n=5):
    return sorted([h for h in rows if h.get('name') and valid(h.get(key))],key=lambda h:(-h[key],h['name']))[:n]

need(LIVE.exists(),'live-meta.json missing')
need(ROSTER.exists(),'roster/index.html missing')
if LIVE.exists() and ROSTER.exists():
    meta=json.loads(LIVE.read_text(encoding='utf-8'))
    heroes=meta.get('heroes',[])
    page=ROSTER.read_text(encoding='utf-8')
    need(meta.get('parser_version')==2,'Live leader validation requires parser v2')
    need(meta.get('rate_unit')=='percentage_points','Live leader validation requires percentage_points')
    need('id="liveLeaders"' in page,'Live leaders section missing')
    need('data-rate-unit="percentage_points"' in page,'Live leaders do not expose the percentage-point contract')
    need('puntos porcentuales' in page,'Live leader percentage-point explanation missing')
    need(str(meta.get('source_updated'))[:10] in page or 'SNAPSHOT LEADERS' in page,'Live leaders measurement context missing')

    for key in ('wr','ban','pick'):
        marker=f'data-leader-key="{key}"'
        start=page.find(marker)
        need(start!=-1,f'Leader board missing for {key}')
        if start==-1: continue
        next_board=page.find('data-leader-key="',start+len(marker))
        end=next_board if next_board!=-1 else page.find('</section>',start)
        block=page[start:end if end!=-1 else len(page)]
        expected=top(heroes,key)
        positions=[]
        for rank,h in enumerate(expected,1):
            name=htmlmod.escape(h['name'])
            value=f'{h[key]:.2f}%'
            token=f'data-leader-rank="{rank}"'
            pos=block.find(token)
            positions.append(pos)
            need(pos!=-1,f'{key} leader rank #{rank} missing')
            if pos!=-1:
                row_end=block.find('</a>',pos)
                row=block[pos:row_end if row_end!=-1 else len(block)]
                need(name in row,f'{key} leader #{rank} name mismatch; expected {h["name"]}')
                need(value in row,f'{key} leader #{rank} value mismatch; expected {value}')
        if positions and all(p!=-1 for p in positions):
            need(positions==sorted(positions),f'{key} leader rows are not in expected rank order')

    picks=[h['pick'] for h in heroes if valid(h.get('pick'))]
    bans=[h['ban'] for h in heroes if valid(h.get('ban'))]
    if picks:
        need(max(picks)<10,f'Pick leader scale regressed; max={max(picks)}')
    if bans:
        need(max(bans)<=100,f'Ban leader scale invalid; max={max(bans)}')

if errors:
    print('LIVE LEADERS VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Live leaders validation passed: WR/ban/pick Top 5 order and displayed values match the corrected snapshot exactly.')
