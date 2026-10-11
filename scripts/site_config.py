from pathlib import Path
from urllib.parse import urlparse
import json, os

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'data'/'site-config.json'


def normalize_base(value):
    value=(value or '').strip()
    if not value:
        raise RuntimeError('Public base URL is empty')
    parsed=urlparse(value)
    if parsed.scheme!='https' or not parsed.netloc or parsed.query or parsed.fragment:
        raise RuntimeError(f'Public base URL must be a clean HTTPS origin/path: {value}')
    return value.rstrip('/')+'/'


def load_site_config():
    if not CONFIG.exists():
        raise RuntimeError('Missing data/site-config.json')
    cfg=json.loads(CONFIG.read_text(encoding='utf-8'))
    if cfg.get('schema_version')!=1:
        raise RuntimeError(f'Unsupported site config schema: {cfg.get("schema_version")}')
    override=os.getenv('MF_PUBLIC_BASE_URL')
    cfg['base_url']=normalize_base(override or cfg.get('base_url'))
    cfg['site_name']=(cfg.get('site_name') or 'MLBB Meta Forge').strip()
    cfg['locale']=(cfg.get('locale') or 'es').strip()
    cfg['noindex_paths']=sorted({str(x).strip('/') for x in cfg.get('noindex_paths',[]) if str(x).strip()})
    legacy=[]
    for value in cfg.get('legacy_base_urls',[]):
        try: base=normalize_base(value)
        except Exception: continue
        if base not in legacy: legacy.append(base)
    cfg['legacy_base_urls']=legacy
    return cfg


def canonical_for(path, base_url=None):
    cfg=load_site_config() if base_url is None else None
    base=cfg['base_url'] if cfg else normalize_base(base_url)
    rel=Path(path).as_posix().lstrip('./')
    if rel=='index.html': return base
    if rel.endswith('/index.html'): return base+rel[:-10]
    return base+rel
