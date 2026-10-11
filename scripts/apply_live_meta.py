from pathlib import Path
import json,re
from hero_identity import hero_key, index_by_hero_key
from site_config import load_site_config

LIVE=Path('data/live-meta.json')
INDEX=Path('index.html')
GEN=Path('scripts/generate_heroes.py')
SITE=load_site_config()

def main():
    if not LIVE.exists():
        print('No live-meta.json; keeping bundled snapshot')
        return
    live=json.loads(LIVE.read_text(encoding='utf-8'))
    rows=live.get('heroes',[])
    if len(rows)<100:
        raise RuntimeError('live-meta.json failed validation: fewer than 100 heroes')
    mapping=index_by_hero_key(rows)

    # Patch only public rate stats. Tier remains editorial until provider semantics are explicitly validated.
    html=INDEX.read_text(encoding='utf-8')
    m=re.search(r'const DATA=(\{.*?\});\nconst DRAFTS=',html,re.S)
    if not m:
        raise RuntimeError('Could not locate DATA object in index.html')
    data=json.loads(m.group(1))
    matched=0
    for h in data.get('heroes',[]):
        src=mapping.get(hero_key(h.get('name')))
        if not src:continue
        h['wr']=src.get('wr',h.get('wr'))
        h['ban']=src.get('ban')
        h['pick']=src.get('pick')
        matched+=1
    if matched!=34:
        raise RuntimeError(f'Expected 34 homepage heroes to match live dataset, found {matched}')
    data['updated']=live.get('updated') or data.get('updated')
    data['patch']=live.get('patch') or data.get('patch')
    data['data_provider']=live.get('provider','MLBBDex public API')
    data['source_updated']=live.get('source_updated')
    data['freshness_basis']=live.get('freshness_basis')
    data['fetched_at']=live.get('fetched_at')
    packed=json.dumps(data,ensure_ascii=False,separators=(',',':'))
    html=html[:m.start(1)]+packed+html[m.end(1):]
    INDEX.write_text(html,encoding='utf-8')

    # Keep the legacy hero-page generator portable: its public origin comes from
    # the same site config used by SEO, robots and sitemap finalization.
    src=GEN.read_text(encoding='utf-8')
    src,base_count=re.subn(r"^BASE='[^']*'$",f"BASE={SITE['base_url']!r}",src,count=1,flags=re.M)
    if base_count!=1:
        raise RuntimeError(f'Expected one BASE assignment in hero generator, found {base_count}')

    # Teach the hero-page generator to merge the same live rate stats at build time.
    if '# LIVE_META_OVERRIDE' not in src:
        block=r'''
# LIVE_META_OVERRIDE
import json as _json
from hero_identity import hero_key as _hero_key, index_by_hero_key as _index_by_hero_key

_live_path=Path('data/live-meta.json')
if _live_path.exists():
    _live=_json.loads(_live_path.read_text(encoding='utf-8'))
    _map=_index_by_hero_key(_live.get('heroes',[]))
    _merged=[]
    for _h in HEROES:
        _x=_map.get(_hero_key(_h[0]))
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
    print(f'Applied live rate stats and configured origin to homepage/hero generator; base={SITE["base_url"]}; matched={matched}/34; shared identity keys={len(mapping)}; editorial tiers preserved')

if __name__=='__main__':main()
