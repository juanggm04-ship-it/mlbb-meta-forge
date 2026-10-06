from pathlib import Path
import json,re,unicodedata

LIVE=Path('data/live-meta.json')
INDEX=Path('index.html')
GEN=Path('scripts/generate_heroes.py')

def norm(s):
    s=str(s or '').lower().replace('&','and')
    s=''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','',s)

def main():
    if not LIVE.exists():
        print('No live-meta.json; keeping bundled snapshot')
        return
    live=json.loads(LIVE.read_text(encoding='utf-8'))
    rows=live.get('heroes',[])
    if len(rows)<100:
        raise RuntimeError('live-meta.json failed validation: fewer than 100 heroes')
    mapping={norm(h.get('name')):h for h in rows if h.get('name')}

    # Patch only public rate stats. Tier remains editorial until provider semantics are explicitly validated.
    html=INDEX.read_text(encoding='utf-8')
    m=re.search(r'const DATA=(\{.*?\});\nconst DRAFTS=',html,re.S)
    if not m:
        raise RuntimeError('Could not locate DATA object in index.html')
    data=json.loads(m.group(1))
    matched=0
    for h in data.get('heroes',[]):
        src=mapping.get(norm(h.get('name')))
        if not src:continue
        h['wr']=src.get('wr',h.get('wr'))
        h['ban']=src.get('ban')
        h['pick']=src.get('pick')
        matched+=1
    if matched<25:
        raise RuntimeError(f'Only {matched} homepage heroes matched live dataset')
    data['updated']=live.get('updated') or data.get('updated')
    data['patch']=live.get('patch') or data.get('patch')
    data['data_provider']=live.get('provider','MLBBDex public API')
    data['source_updated']=live.get('source_updated')
    data['freshness_basis']=live.get('freshness_basis')
    data['fetched_at']=live.get('fetched_at')
    packed=json.dumps(data,ensure_ascii=False,separators=(',',':'))
    html=html[:m.start(1)]+packed+html[m.end(1):]
    INDEX.write_text(html,encoding='utf-8')

    # Teach the hero-page generator to merge the same live rate stats at build time.
    src=GEN.read_text(encoding='utf-8')
    if '# LIVE_META_OVERRIDE' not in src:
        block=r'''
# LIVE_META_OVERRIDE
import json as _json

def _live_norm(s):
    s=str(s or '').lower().replace('&','and')
    s=''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','',s)

_live_path=Path('data/live-meta.json')
if _live_path.exists():
    _live=_json.loads(_live_path.read_text(encoding='utf-8'))
    _map={_live_norm(x.get('name')):x for x in _live.get('heroes',[]) if x.get('name')}
    _merged=[]
    for _h in HEROES:
        _x=_map.get(_live_norm(_h[0]))
        if _x:
            _merged.append((_h[0],_h[1],_h[2],_x.get('wr',_h[3]),_x.get('ban'),_h[5],_h[6]))
        else:
            _merged.append(_h)
    HEROES=_merged
    UPDATED=_live.get('updated') or UPDATED
    PATCH=_live.get('patch') or PATCH
'''
        src=src.replace('\nBY_NAME={h[0]:h for h in HEROES}',block+'\nBY_NAME={h[0]:h for h in HEROES}',1)
        GEN.write_text(src,encoding='utf-8')
    print(f'Applied live rate stats to homepage and hero generator; matched={matched}; editorial tiers preserved')

if __name__=='__main__':main()
