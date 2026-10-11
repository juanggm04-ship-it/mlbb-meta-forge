import re
import unicodedata


def hero_key(value):
    """Return a stable cross-source identity key for hero names."""
    text=str(value or '').strip().lower().replace('&','and')
    text=''.join(c for c in unicodedata.normalize('NFD',text) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','',text)


def index_by_hero_key(rows, name_field='name'):
    """Index hero-like dict rows by normalized key and fail on collisions."""
    out={}
    for row in rows or []:
        if not isinstance(row,dict):
            continue
        name=row.get(name_field)
        key=hero_key(name)
        if not key:
            continue
        if key in out:
            prior=out[key].get(name_field)
            raise RuntimeError(f'Hero identity collision for key {key!r}: {prior!r} vs {name!r}')
        out[key]=row
    return out


def semantic_rate_rows(rows):
    """Canonical live-stat view, stable across provider ordering/name punctuation changes."""
    mapping=index_by_hero_key(rows)
    return [
        {
            'key':key,
            'wr':row.get('wr'),
            'ban':row.get('ban'),
            'pick':row.get('pick'),
        }
        for key,row in sorted(mapping.items())
    ]
