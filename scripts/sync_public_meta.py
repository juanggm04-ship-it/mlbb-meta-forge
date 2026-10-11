from pathlib import Path
import json, urllib.request, datetime
from hero_identity import hero_key, index_by_hero_key, semantic_rate_rows

RANKINGS_URL='https://mlbbdex.com/api/v1/rankings'
PATCHES_URL='https://mlbbdex.com/api/v1/patches'
OUT=Path('data/live-meta.json')
PREV=Path('data/previous-meta.json')
HISTORY=Path('data/meta-history.json')
MAX_POINTS=24
IDENTITY_VERSION=1

ALIASES={
    'name':['name','hero_name','hero','title'],
    'wr':['win_rate','winrate','wr'],
    'ban':['ban_rate','banrate','br'],
    'pick':['pick_rate','pickrate','pr'],
    'tier':['tier','rank_tier'],
    'date':['date','updated_at','updated','snapshot_date','recorded_at'],
    'patch':['patch','version','patch_version']
}

def fetch_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'MLBB-Meta-Forge/1.0 (+https://github.com/juanggm04-ship-it/mlbb-meta-forge)'})
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.load(r)

def norm_pct(v):
    if v is None:return None
    if isinstance(v,str):
        s=v.strip().replace('%','').replace(',','.')
        if not s:return None
        v=float(s)
    else:v=float(v)
    if 0 <= v <= 1.0:v*=100
    return round(v,2)

def pick_field(d, aliases):
    if not isinstance(d,dict):return None
    low={str(k).lower():v for k,v in d.items()}
    for a in aliases:
        if a in low:return low[a]
    return None

def name_from_record(rec):
    v=pick_field(rec,ALIASES['name'])
    if isinstance(v,dict):v=pick_field(v,ALIASES['name'])
    return str(v).strip() if v else None

def extract_records(payload):
    if isinstance(payload,dict):
        data=payload.get('data',payload)
        if isinstance(data,list):return data
        if isinstance(data,dict):
            for key in ('rankings','heroes','items','results'):
                if isinstance(data.get(key),list):return data[key]
    if isinstance(payload,list):return payload
    raise RuntimeError('No ranking list found in API response')

def latest_patch(payload):
    data=payload.get('data',payload) if isinstance(payload,dict) else payload
    if isinstance(data,list) and data:
        first=data[0]
        if isinstance(first,dict):
            p=pick_field(first,ALIASES['patch']) or first.get('name')
            return str(p) if p else None
        return str(first)
    return None

def load_history():
    try:
        data=json.loads(HISTORY.read_text(encoding='utf-8')) if HISTORY.exists() else {'snapshots':[]}
        return data if isinstance(data,dict) and isinstance(data.get('snapshots'),list) else {'snapshots':[]}
    except Exception:
        return {'snapshots':[]}

def semantic_view(snapshot):
    if not isinstance(snapshot,dict):return None
    return {
        'patch':snapshot.get('patch'),
        'heroes':semantic_rate_rows(snapshot.get('heroes',[]))
    }

def reconcile_rows(rows,current_map,compact=False):
    out=[]; seen=set()
    for row in rows or []:
        if not isinstance(row,dict) or not row.get('name'):continue
        key=row.get('key') or hero_key(row.get('name'))
        if not key:continue
        if key in seen:raise RuntimeError(f'Duplicate historical hero identity: {key}')
        seen.add(key)
        current=current_map.get(key)
        item={'key':key,'name':current.get('name') if current else row.get('name')}
        if compact:
            item.update({'wr':row.get('wr'),'ban':row.get('ban'),'pick':row.get('pick')})
        else:
            item.update({k:v for k,v in row.items() if k not in ('key','name')})
        out.append(item)
    return sorted(out,key=lambda h:h['key'])

def reconcile_history(hist,current_map):
    migrated=[]
    for snap in hist.get('snapshots',[]):
        if not isinstance(snap,dict):continue
        item={k:v for k,v in snap.items() if k!='heroes'}
        item['heroes']=reconcile_rows(snap.get('heroes',[]),current_map,compact=True)
        migrated.append(item)
    return {'identity_version':IDENTITY_VERSION,'snapshots':migrated[-MAX_POINTS:]}

def write_history(hist):
    HISTORY.write_text(json.dumps(hist,ensure_ascii=False,indent=2),encoding='utf-8')

def append_history(hist,out,current_map):
    snapshots=hist.get('snapshots',[])[:]
    snapshots.append({
        'updated':out.get('updated'),
        'source_updated':out.get('source_updated'),
        'freshness_basis':out.get('freshness_basis'),
        'patch':out.get('patch'),
        'fetched_at':out.get('fetched_at'),
        'heroes':reconcile_rows(out.get('heroes',[]),current_map,compact=True)
    })
    hist={'identity_version':IDENTITY_VERSION,'snapshots':snapshots[-MAX_POINTS:]}
    write_history(hist)
    return hist

def write_previous(old,current_map):
    prev={k:v for k,v in old.items() if k!='heroes'}
    prev['identity_version']=IDENTITY_VERSION
    prev['heroes']=reconcile_rows(old.get('heroes',[]),current_map,compact=False)
    PREV.write_text(json.dumps(prev,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    rankings=fetch_json(RANKINGS_URL)
    patches=fetch_json(PATCHES_URL)
    rows=extract_records(rankings)
    if len(rows)<100:raise RuntimeError(f'Validation failed: only {len(rows)} ranking rows')
    heroes=[]
    for rec in rows:
        if not isinstance(rec,dict):continue
        name=name_from_record(rec)
        if not name:continue
        try:wr=norm_pct(pick_field(rec,ALIASES['wr']))
        except:wr=None
        try:ban=norm_pct(pick_field(rec,ALIASES['ban']))
        except:ban=None
        try:pick=norm_pct(pick_field(rec,ALIASES['pick']))
        except:pick=None
        tier=pick_field(rec,ALIASES['tier']); date=pick_field(rec,ALIASES['date'])
        if wr is None or not 30<=wr<=80:continue
        if ban is not None and not 0<=ban<=100:continue
        if pick is not None and not 0<=pick<=100:continue
        heroes.append({'key':hero_key(name),'name':name,'wr':wr,'ban':ban,'pick':pick,'tier':str(tier) if tier else None,'date':str(date) if date else None})
    if len(heroes)<100:raise RuntimeError(f'Validation failed: only {len(heroes)} valid hero records')
    identity=index_by_hero_key(heroes)
    if len(identity)!=len(heroes):
        raise RuntimeError('Normalized hero identity count differs from validated hero count')

    patch=latest_patch(patches)
    dates=[h['date'] for h in heroes if h.get('date')]
    source_updated=max(dates) if dates else None
    fetched_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    fetched_date=fetched_at[:10]
    updated=source_updated or fetched_date
    freshness_basis='source' if source_updated else 'fetched'
    source=rankings.get('source') if isinstance(rankings,dict) else None
    out={
        'identity_version':IDENTITY_VERSION,
        'updated':updated,
        'source_updated':source_updated,
        'freshness_basis':freshness_basis,
        'patch':patch,
        'fetched_at':fetched_at,
        'provider':'MLBBDex public API',
        'provider_url':'https://mlbbdex.com/api-doc',
        'source':source,
        'total':len(heroes),
        'heroes':sorted(heroes,key=lambda h:h['key'])
    }

    OUT.parent.mkdir(parents=True,exist_ok=True)
    old=None
    if OUT.exists():
        try:old=json.loads(OUT.read_text(encoding='utf-8'))
        except Exception:old=None
    semantic_changed=semantic_view(old)!=semantic_view(out)
    if old and semantic_changed:
        write_previous(old,identity)
    OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')

    history_before=load_history()
    history=reconcile_history(history_before,identity)
    history_migrated=history!=history_before
    if semantic_changed or not history.get('snapshots'):
        history=append_history(history,out,identity)
    elif history_migrated:
        write_history(history)
    points=len(history.get('snapshots',[]))
    print(f'Wrote {len(heroes)} validated heroes; patch={patch}; source_updated={source_updated}; freshness={freshness_basis}; semantic_changed={semantic_changed}; history_migrated={history_migrated}; previous={PREV.exists()}; history_points={points}; identity_keys={len(identity)}')

if __name__=='__main__':main()
